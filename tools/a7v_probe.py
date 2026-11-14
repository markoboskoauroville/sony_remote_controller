#!/usr/bin/env python3
"""
The bench for Step 1 and Step 2 (PLAN.md §3), run on the Mac before the same steps go into the app.

The A7 V joins the same Wi-Fi as the Mac (Remote Shoot over an access point). This finds it, runs the
PTP/IP handshake (§2), writes what the camera says it supports to a log, reads the live view address
(0xD278) and shows the camera's screen at http://127.0.0.1:8841/ in the browser.

    python3 tools/a7v_probe.py              find the camera on the network by itself
    python3 tools/a7v_probe.py 192.168.1.42 or name it
    python3 tools/a7v_probe.py --pp1 [ip]    first set PP1 as docs/a7v-pp1-slog3-guide (S-Log3, S-Gamut3.Cine,
                                             ISO 800) and read the values back from the camera

The GUID is kept in ~/.config/mantra-sony-remote/guid, so the camera pairs with this bench once and
recognises it after that (Sony bodies keep one pairing; alpha-fairy's warning).
"""

import http.server
import ipaddress
import os
import socket
import socketserver
import struct
import subprocess
import sys
import threading
import time
import urllib.request
import uuid
from concurrent.futures import ThreadPoolExecutor

PORT = 15740
VIEW_PORT = 8841
LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs")

# PTP/IP packet types (SONY-CAMERA-PROTOCOL.md §3.1)
INIT_CMD_REQ, INIT_CMD_ACK, INIT_EVT_REQ, INIT_EVT_ACK, INIT_FAIL = 1, 2, 3, 4, 5
OP_REQ, OP_RESP, EVENT, START_DATA, DATA, END_DATA = 6, 7, 8, 9, 10, 12
PROBE_REQ, PROBE_RESP = 13, 14

OK = 0x2001
LIVE_VIEW_URL = 0xD278
LIVE_VIEW_HANDLE = 0xFFFFC002


def say(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def guid() -> bytes:
    path = os.path.expanduser("~/.config/mantra-sony-remote/guid")
    if os.path.exists(path):
        return bytes.fromhex(open(path).read().strip())
    os.makedirs(os.path.dirname(path), exist_ok=True)
    g = uuid.uuid4().bytes
    open(path, "w").write(g.hex())
    return g


# ---------------------------------------------------------------- finding the camera

def local_net():
    ip = subprocess.run(["ipconfig", "getifaddr", "en0"], capture_output=True, text=True).stdout.strip()
    return ip, ipaddress.ip_network(ip + "/24", strict=False)


def ssdp() -> list:
    """Sony answers M-SEARCH for its DigitalImaging service (PLAN.md §2e: no ARP table on Android)."""
    msg = ("M-SEARCH * HTTP/1.1\r\nHOST: 239.255.255.250:1900\r\nMAN: \"ssdp:discover\"\r\nMX: 2\r\n"
           "ST: urn:schemas-sony-com:service:DigitalImaging:1\r\n\r\n").encode()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(3)
    s.sendto(msg, ("239.255.255.250", 1900))
    found = []
    try:
        while True:
            data, (ip, _) = s.recvfrom(4096)
            if ip not in found:
                found.append(ip)
                say("SSDP answer from", ip, data.split(b"\r\n")[0].decode(errors="replace"))
    except socket.timeout:
        pass
    return found


def sweep() -> list:
    me, net = local_net()

    def open_(ip):
        try:
            with socket.create_connection((str(ip), PORT), timeout=0.6):
                return str(ip)
        except OSError:
            return None

    with ThreadPoolExecutor(64) as pool:
        return [ip for ip in pool.map(open_, (h for h in net.hosts() if str(h) != me)) if ip]


# ---------------------------------------------------------------- PTP/IP

class Ptp:
    def __init__(self, ip):
        self.ip = ip
        self.tx = 0
        self.lock = threading.Lock()

    @staticmethod
    def _recv_exact(sock, n):
        buf = b""
        while len(buf) < n:
            chunk = sock.recv(n - len(buf))
            if not chunk:
                raise ConnectionError("the camera closed the connection")
            buf += chunk
        return buf

    def _packet(self, sock):
        length, kind = struct.unpack("<II", self._recv_exact(sock, 8))
        return kind, self._recv_exact(sock, length - 8)

    def connect(self):
        self.cmd = socket.create_connection((self.ip, PORT), timeout=60)
        name = "Mantra Sony Remote".encode("utf-16le") + b"\0\0"
        body = guid() + name + struct.pack("<I", 0x00010000)
        self.cmd.sendall(struct.pack("<II", 8 + len(body), INIT_CMD_REQ) + body)
        say("InitCommandRequest sent; if the camera asks to pair, press OK on the camera")
        kind, body = self._packet(self.cmd)
        if kind == INIT_FAIL:
            reason = struct.unpack("<I", body[:4])[0] if len(body) >= 4 else 0
            raise ConnectionError(f"the camera refused the bench (InitFail 0x{reason:X}): pairing or Access Authen.")
        if kind != INIT_CMD_ACK:
            raise ConnectionError(f"unexpected packet {kind}")
        conn_id = struct.unpack("<I", body[:4])[0]
        cam_name = body[20:].decode("utf-16le", errors="replace").split("\0")[0]
        say("camera answers:", cam_name, f"(connection {conn_id})")

        self.evt = socket.create_connection((self.ip, PORT), timeout=10)
        self.evt.sendall(struct.pack("<III", 12, INIT_EVT_REQ, conn_id))
        kind, _ = self._packet(self.evt)
        if kind != INIT_EVT_ACK:
            raise ConnectionError(f"event channel: unexpected packet {kind}")
        threading.Thread(target=self._events, daemon=True).start()
        self.cmd.settimeout(15)
        return cam_name

    def _events(self):
        # The camera probes the event channel; an unanswered probe ends the session.
        try:
            while True:
                kind, body = self._packet(self.evt)
                if kind == PROBE_REQ:
                    self.evt.sendall(struct.pack("<II", 8, PROBE_RESP))
        except Exception:
            pass

    def op(self, code, *params, data_out: bytes = None):
        """One operation. Returns (response code, data from the camera)."""
        with self.lock:
            self.tx += 1
            tx = self.tx
            phase = 2 if data_out is not None else 1
            body = struct.pack("<IHI", phase, code, tx) + b"".join(struct.pack("<I", p) for p in params)
            self.cmd.sendall(struct.pack("<II", 8 + len(body), OP_REQ) + body)
            if data_out is not None:
                self.cmd.sendall(struct.pack("<IIIQ", 20, START_DATA, tx, len(data_out)))
                self.cmd.sendall(struct.pack("<III", 12 + len(data_out), END_DATA, tx) + data_out)
            data = b""
            while True:
                kind, body = self._packet(self.cmd)
                if kind in (DATA, END_DATA):
                    data += body[4:]
                elif kind == OP_RESP:
                    return struct.unpack("<H", body[:2])[0], data
                elif kind == PROBE_REQ:
                    self.cmd.sendall(struct.pack("<II", 8, PROBE_RESP))


def ptp_string(b, i):
    n = b[i]
    s = b[i + 1:i + 1 + 2 * n].decode("utf-16le", errors="replace").rstrip("\0")
    return s, i + 1 + 2 * n


def find_string_prop(blob, code):
    """The current value of a STR (0xFFFF) property in SDIO_GetAllExtDevicePropInfo's answer."""
    needle = struct.pack("<HH", code, 0xFFFF)
    i = blob.find(needle)
    if i < 0:
        return None
    i += 4 + 2                    # code, type, GetSet, IsEnabled
    _, i = ptp_string(blob, i)    # factory default
    value, _ = ptp_string(blob, i)
    return value


def handshake(p: Ptp):
    rc, _ = p.op(0x1002, 1)                                  # OpenSession
    say(f"OpenSession 0x{rc:04X}")
    for step in (1, 2):
        rc, _ = p.op(0x9201, step, 0, 0)                     # SDIO_Connect 1, 2
        say(f"SDIO_Connect({step}) 0x{rc:04X}")
    rc, data = p.op(0x9216)                                  # SDIO_GetVendorCodeVersion
    version = struct.unpack("<H", data[:2])[0] if len(data) >= 2 else 0
    say(f"vendor code version {version} (0x{rc:04X})")
    rc, info = p.op(0x9202, 0x012C)                          # SDIO_GetExtDeviceInfo
    say(f"SDIO_GetExtDeviceInfo 0x{rc:04X}, {len(info)} bytes")
    rc, _ = p.op(0x9201, 3, 0, 0)                            # SDIO_Connect 3
    say(f"SDIO_Connect(3) 0x{rc:04X}")
    return version, info


def codes(info):
    """SDIO_GetExtDeviceInfo: uint16 version, then two uint32-counted arrays of uint16 codes."""
    try:
        i = 2
        n = struct.unpack("<I", info[i:i + 4])[0]; i += 4
        props = struct.unpack(f"<{n}H", info[i:i + 2 * n]); i += 2 * n
        m = struct.unpack("<I", info[i:i + 4])[0]; i += 4
        controls = struct.unpack(f"<{m}H", info[i:i + 2 * m])
        return props, controls
    except struct.error:
        return (), ()


# ---------------------------------------------------------------- settings (Camera Control PTP 3)

# property: (datatype size in bytes, value) — PTP 3 Reference: 0xD23F UINT8, 0xD0E1/0xD0E9 UINT16, 0xD21E UINT32
PP1 = [
    (0xD23F, 1, 0x01, "Picture Profile", "PP1"),
    (0xD0E1, 2, 0x0303, "PP Gamma", "S-Log3"),
    (0xD0E9, 2, 0x0008, "PP Color Mode", "S-Gamut3.Cine"),
    (0xD21E, 4, 800, "ISO", "800"),
]


def find_number_prop(blob, code, size):
    """Current value of a numeric property in SDIO_GetAllExtDevicePropInfo: code, type, GetSet, IsEnabled, default, current."""
    types = {1: (0x0001, 0x0002), 2: (0x0003, 0x0004), 4: (0x0005, 0x0006)}[size]
    for t in types:
        i = blob.find(struct.pack("<HH", code, t))
        if i >= 0:
            j = i + 6 + size
            fmt = {1: "<B", 2: "<H", 4: "<I"}[size]
            return struct.unpack(fmt, blob[j:j + size])[0], blob[i + 5]
    return None, None


def set_pp1(p: Ptp, version: int):
    for code, size, value, name, word in PP1:
        data = value.to_bytes(size, "little")
        params = (code, 1) if version >= 310 else (code,)
        rc, _ = p.op(0x9205, *params, data_out=data)             # SDIO_SetExtDevicePropValue
        say(f"set {name} = {word}: 0x{rc:04X}")
        time.sleep(0.3)
    rc, blob = p.op(0x9209, 0, 1)
    for code, size, value, name, word in PP1:
        now, enabled = find_number_prop(blob, code, size)
        ok = "OK" if now == value else "NOT SET"
        say(f"camera says {name}: {now if now is None else hex(now)} (wanted {word}) {ok}, enabled={enabled}")


# ---------------------------------------------------------------- live view

latest = {"jpeg": None, "n": 0, "t0": time.time()}


def frames_from_http(url):
    """HTTP :60152 stream: 16-byte header (four uint32), then reserved + JPEG + focal frame info (§3.10)."""
    r = urllib.request.urlopen(url, timeout=10)
    while True:
        head = r.read(16)
        if len(head) < 16:
            raise ConnectionError("live view stream ended")
        off_img, img_size, off_ff, ff_size = struct.unpack("<IIII", head)
        reserved = min(off_ff or off_img, off_img) - 16
        body = r.read(max(reserved, 0) + img_size + ff_size)
        start = off_img - 16
        yield body[start:start + img_size]


def frames_from_ptp(p: Ptp):
    """GetObject on the live view handle: the same layout in one data phase (the A7R V refused it)."""
    while True:
        rc, data = p.op(0x1009, LIVE_VIEW_HANDLE)
        if rc != OK:
            raise ConnectionError(f"GetObject(live view) 0x{rc:04X}")
        off_img, img_size = struct.unpack("<II", data[:8])
        yield data[off_img:off_img + img_size]


def pump(frames):
    for jpeg in frames:
        if jpeg[:2] == b"\xff\xd8":
            latest["jpeg"] = jpeg
            latest["n"] += 1
            if latest["n"] % 100 == 0:
                fps = latest["n"] / (time.time() - latest["t0"])
                say(f"{latest['n']} frames, {fps:.1f} fps, {len(jpeg) // 1024} KB")


class View(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        if self.path == "/frame.jpg":
            j = latest["jpeg"] or b""
            self.send_response(200); self.send_header("Content-Type", "image/jpeg"); self.end_headers()
            self.wfile.write(j)
            return
        if self.path == "/stream":
            self.send_response(200)
            self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=f")
            self.end_headers()
            last = 0
            try:
                while True:
                    if latest["n"] != last and latest["jpeg"]:
                        last = latest["n"]
                        j = latest["jpeg"]
                        self.wfile.write(b"--f\r\nContent-Type: image/jpeg\r\nContent-Length: %d\r\n\r\n" % len(j) + j + b"\r\n")
                    time.sleep(0.01)
            except OSError:
                return
        page = (b"<!doctype html><title>A7 V</title><body style='margin:0;background:#000;display:grid;"
                b"place-items:center;height:100vh'><img src='/stream' style='max-width:100%;max-height:100vh'>")
        self.send_response(200); self.send_header("Content-Type", "text/html"); self.end_headers()
        self.wfile.write(page)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    ip = args[0] if args else None
    if not ip:
        me, net = local_net()
        say(f"looking for the camera on {net} (this Mac is {me})")
        found = ssdp() or sweep()
        if not found:
            say("no camera found: is it on the same Wi-Fi with Remote Shoot on? (port 15740 nowhere open)")
            sys.exit(1)
        ip = found[0]
    say("camera at", ip)

    p = Ptp(ip)
    name = p.connect()
    version, info = handshake(p)
    props, controls = codes(info)

    if "--pp1" in sys.argv:
        set_pp1(p, version)

    rc, blob = p.op(0x9209, 0, 1)                            # SDIO_GetAllExtDevicePropInfo
    url = find_string_prop(blob, LIVE_VIEW_URL) if rc == OK else None
    say(f"all properties 0x{rc:04X}, {len(blob)} bytes; live view URL: {url}")

    os.makedirs(LOG, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    with open(os.path.join(LOG, f"a7v-{stamp}.txt"), "w") as f:
        f.write(f"camera {name} at {ip}\nvendor code version {version}\nlive view URL {url}\n")
        f.write(f"{len(props)} properties: " + " ".join(f"{c:04X}" for c in props) + "\n")
        f.write(f"{len(controls)} controls: " + " ".join(f"{c:04X}" for c in controls) + "\n")
    open(os.path.join(LOG, f"a7v-{stamp}-props.bin"), "wb").write(blob)
    say(f"{len(props)} properties, {len(controls)} controls, written to logs/a7v-{stamp}.txt")

    socketserver.ThreadingTCPServer.allow_reuse_address = True
    server = socketserver.ThreadingTCPServer(("127.0.0.1", VIEW_PORT), View)
    server.daemon_threads = True
    threading.Thread(target=server.serve_forever, daemon=True).start()
    say(f"the camera's screen: http://127.0.0.1:{VIEW_PORT}/")

    try:
        if url:
            pump(frames_from_http(url))
        else:
            pump(frames_from_ptp(p))
    except Exception as e:
        say("HTTP live view stopped:", e, "- trying PTP GetObject")
        pump(frames_from_ptp(p))


if __name__ == "__main__":
    main()
