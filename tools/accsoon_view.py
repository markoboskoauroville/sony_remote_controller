#!/usr/bin/env python3
"""
The bench for Step A1 (PLAN.md §3): the camera's HDMI picture from an Accsoon CineView Nano, on the Mac.

The Nano is its own 5 GHz access point; the transmitter is 10.0.0.1. This port of accsoon-decode (MIT,
reference/accsoon/accsoon-decode/accsoon-decoder-mac) keeps the stream alive with the 19-byte "ACCSOON" trigger
over TCP 8001, gathers the UDP 8000 fragments into frames and writes them as Annex-B H.264 to stdout:

    python3 tools/accsoon_view.py | ffplay -loglevel warning -fflags nobuffer -flags low_delay -f h264 -

    --stats    no video out, one line a second: frames, fps, Mb/s, the first frame's size (Step A1's numbers)

Frame layout (accsoon_udp_stream.cpp): every fragment has a 14-byte header (message id at 8, uint16 LE;
fragment count at 10; fragment index at 11); the first fragment adds a 23-byte message header, after which the
H.264 starts with its start code (the first frame wanted is an SPS, NAL type 0x67).
"""

import socket
import struct
import sys
import threading
import time

NANO = "10.0.0.1"
TCP_PORT, UDP_PORT = 8001, 8000
TRIGGER = bytes([0x41, 0x43, 0x43, 0x53, 0x4F, 0x4F, 0x4E, 0x01, 0x00, 0x01,
                 0x00, 0x0A, 0x00, 0x02, 0x00, 0x00, 0x00, 0x01, 0x00])
FRAG_HEADER, MSG_HEADER = 14, 23

stop = threading.Event()


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, file=sys.stderr, flush=True)


def keep_alive():
    """The Nano sends only while it is asked: trigger, wait for its 20-byte reply, 1 ms, again."""
    while not stop.is_set():
        try:
            s = socket.create_connection((NANO, TCP_PORT), timeout=3)
            s.settimeout(0.4)
            log("TCP 8001 connected")
            while not stop.is_set():
                s.sendall(TRIGGER)
                try:
                    s.recv(20)
                except socket.timeout:
                    pass
                time.sleep(0.001)
        except OSError as e:
            log("TCP 8001:", e, "- again in 1 s")
            time.sleep(1)


def receive(stats: bool):
    u = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    u.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1 << 20)
    u.bind(("0.0.0.0", UDP_PORT))
    u.settimeout(1)
    messages = {}
    started = False
    last_id = None
    frames = nbytes = 0
    t0 = time.time()
    out = sys.stdout.buffer
    while not stop.is_set():
        try:
            data = u.recv(8192)
        except socket.timeout:
            log("no UDP for 1 s")
            continue
        if len(data) < FRAG_HEADER:
            continue
        msg_id = struct.unpack_from("<H", data, 8)[0]
        count, index = data[10], data[11]
        m = messages.setdefault(msg_id, {"count": count, "frags": {}})
        m["frags"][index] = data[FRAG_HEADER:]
        if len(m["frags"]) != m["count"]:
            continue
        del messages[msg_id]
        if last_id is not None and 0 < (last_id - msg_id) & 0xFFFF < 30:
            continue                                   # an older frame finished late
        first = m["frags"][0]
        if not started:
            if len(first) <= MSG_HEADER + 4 or first[MSG_HEADER + 4] != 0x67:
                continue                               # wait for the SPS
            started = True
            w, h = struct.unpack_from("<HH", first, 0) if len(first) >= 4 else (0, 0)
            log(f"first frame (SPS); message header {first[:MSG_HEADER].hex()}")
        last_id = msg_id
        frame = first[MSG_HEADER:] + b"".join(m["frags"][i] for i in range(1, m["count"]))
        frames += 1
        nbytes += len(frame)
        if not stats:
            out.write(frame)
            out.flush()
        if time.time() - t0 >= 1:
            dt = time.time() - t0
            log(f"{frames / dt:.1f} fps, {nbytes * 8 / dt / 1e6:.1f} Mb/s")
            frames = nbytes = 0
            t0 = time.time()
        for old in [k for k in messages if 30 < (msg_id - k) & 0xFFFF < 0x8000]:
            del messages[old]


def main():
    stats = "--stats" in sys.argv
    threading.Thread(target=keep_alive, daemon=True).start()
    try:
        receive(stats)
    except (KeyboardInterrupt, BrokenPipeError):
        stop.set()


if __name__ == "__main__":
    main()
