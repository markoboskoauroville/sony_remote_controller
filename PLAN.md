# Sony Remote Controller: research and plan

Goal: **one Android app with two modes.** You switch between them; they never
run at the same time.

| Mode | Picture comes from | Camera control |
|---|---|---|
| **Sony Direct** | the A7 V itself, over its Wi-Fi (PTP/IP live view) | yes: photo, REC, exposure, focus point |
| **Accsoon** | the Accsoon CineView Nano transmitter on the camera's HDMI (H.264 over its Wi-Fi) | **basic controls over Bluetooth** (REC, shutter, AF-On, C1, focus/zoom jog), so you don't have to switch modes for everyday shooting |

The goal is the same in both modes: one person standing in front of an
A7 V (ILCE-7M5) sees on the phone what the camera sees, and runs the shoot
alone.

Status: **plan only. No code yet.** Each feature below is built, tested on the
real equipment and approved before the next one starts.

**How we work: like jazz.** Every step is an *experiment*. We build one small
thing, try it on the real camera, and then decide together: **keep**, **change**
or **drop**. The order below is a starting chart, not a score; we rearrange it
whenever a test tells us to. Each decision is written in the experiment log at
the end of this file.

---

## 1. What exists on GitHub (checked 22.10.2026)

### Most forked / most popular Sony camera projects

| Repo | Forks / stars | Platform | Works with A7 V? |
|---|---|---|---|
| [ma1co/Sony-PMCA-RE](https://github.com/ma1co/Sony-PMCA-RE) | 322 / 2950 | Python | **No.** Installs apps on older cameras (PlayMemories era). Not a remote. |
| [ma1co/OpenMemories-Tweak](https://github.com/ma1co/OpenMemories-Tweak) | 126 / 1425 | Java | **No.** Same older cameras. |
| [Bloodevil/sony_camera_api](https://github.com/Bloodevil/sony_camera_api) | 65 / 288 | Python | **No.** Uses the old "Camera Remote API" (JSON-RPC), which Sony dropped. The A7 IV and newer don't have it. |
| [ThibaudM/timelapse-sony](https://github.com/ThibaudM/timelapse-sony) | 34 / 141 | Android | **No.** Same old API. |
| [frank26080115/alpha-fairy](https://github.com/frank26080115/alpha-fairy) | 21 / 220 | ESP32 | Partly. PTP/IP Wi-Fi remote; a hardware gadget, not a phone app. |
| [Staacks/alpharemote](https://github.com/Staacks/alpharemote) | 15 / 150 | Android (Kotlin) | Bluetooth shutter only. **No live view.** |

**Conclusion:** the most popular projects target the old API that the A7 V no
longer has. We can't fork any of them.

### Modern projects that match the A7 V (PTP/IP + Sony vendor extensions)

These are new and have few stars, but they speak the protocol the A7 V uses.

| Repo | License | What we can take |
|---|---|---|
| [mvpzac/Imagedge](https://github.com/mvpzac/Imagedge) | **Apache-2.0** | **The best starting point.** A Kotlin + Jetpack Compose Android app. It has a pure-Kotlin PTP/IP stack with Sony extensions (`:ptp`), a live-view client (`:liveview`), ISO/aperture/shutter/WB/exp-comp control, QR Wi-Fi joining, keep-alive and reconnect. Tested on a ZV-E10. The app itself is built around photo transfer and LUTs, so we reuse its modules, not the whole app. |
| [argallo/sony-camera-android](https://github.com/argallo/sony-camera-android) | MIT | A Kotlin USB-cable PTP library: live view, AF, capture, auto-reconnect. Useful as a **wired fallback** later. Tested on an α6600. |
| [sarnau/sony-camera-protocol](https://github.com/sarnau/sony-camera-protocol) | none (reference only) | The best protocol document. It is **hardware-verified on an A7R V**, the same generation as the A7 V: Wi-Fi handoff, PTP/IP session, shutter, AF, movie REC, 446 properties, and live view at 25.7 fps. No license, so we read it and don't copy code from it. |
| [jakkuh/sony-alpha-python](https://github.com/jakkuh/sony-alpha-python) | none | Shows the SSH-authenticated PTP over LAN (home-network mode). Includes Sony's "Camera Control PTP 3 Reference" PDF. |
| [Streetblock/remote-camera-control-rs](https://github.com/Streetblock/remote-camera-control-rs), [Knallli/alpha2go](https://github.com/Knallli/alpha2go) | – | Rust and Go cross-checks of the same protocol. |

### Official Sony options

- **Camera Remote Command** is Sony's published PTP-level protocol. The
  ILCE-7M5 is supported (v2.01.00), including PTP-IP. This is the spec we
  implement against.
- **Camera Remote SDK** is a C++ SDK. The ILCE-7M5 is supported since 2.01.00
  (Feb 2026). It ships prebuilt for Windows, macOS and Linux, and **Android is
  not an official target**. Pure Kotlin is simpler than cross-compiling it.
- **Sony Creators' App** already does remote shooting with live view on the
  A7 V. It is our usability benchmark, not code we can use.

### Decision

Build our own small Android app (Kotlin, Android Views like mantra-ndi). Reuse Imagedge's
`:ptp` and `:liveview` modules under Apache-2.0, with attribution in `NOTICE`.
Use sarnau's A7R V notes and Sony's Camera Remote Command docs to fill the
A7 V-specific details.

---

## 2. How the connection works on the A7 V

```
Phone ──Wi-Fi──► camera (TCP 15740, PTP/IP: command + event channels)
                  OpenSession → SDIO_Connect 1,2 → GetVendorCodeVersion
                  → GetExtDeviceInfo → SDIO_Connect 3 → ready
Phone ──HTTP──►  camera :60152/liveviewstream  (URL read from prop 0xD278)
                  endless stream of [16-byte header + JPEG + focus-frame info]
Controls:        SDIO_ControlDevice 0x9207  (S1 half-press 0xD2C1, S2 0xD2C2,
                 MovieRec 0xD2C8, AFAreaPosition 0xD2DC, …)
Settings:        SDIO_SetExtDevicePropValue 0x9205 (ISO 0xD21E, shutter 0xD20D,
                 F-number 0x5007, exp. comp 0x5010, …)
```

The three Wi-Fi setups you asked for, in build order:

1. **Phone joins the camera's own Wi-Fi** (`DIRECT-xxxx:ILCE-7M5`, camera at
   `192.168.122.1`). This is the simplest and best documented, so we build it
   first.
2. **Camera joins the phone's hotspot.** Same protocol; we only have to find
   the camera's IP.
3. **Both on the house Wi-Fi.** This may need the camera's "Access
   Authentication" (SSH-tunneled PTP; see jakkuh). It is the riskiest, so it
   comes last.

---

## 2b. How the Accsoon mode works (from our CINEVIEW_VIEWER)

Our own `CINEVIEW_VIEWER` repo is a **Mac** viewer (Swift) for the CineView
Nano. Its protocol comes from lithiumee/accsoon-decode (MIT) and
yoons100/Accsoon-Bridge (tested on a Master 4K). Its HANDOVER says it **has not
been compiled or run against the Nano yet.**

```
Phone ──Wi-Fi──► CineView AP, transmitter at 10.0.0.1
TCP 8001   send the 19-byte "ACCSOON" trigger about every 1 ms (keeps the stream alive)
UDP 8000   phone binds 8000; fragments [14-byte header: msg id, count, index]
           first fragment adds a 23-byte header (width, height, bitrate, fps)
           payload = Annex-B H.264 (HEVC on the 4K models)
```

On Android this becomes a Kotlin port of `CineViewCore` (Protocol,
Reassembler, NAL, with the 22 tests ported too). `MediaCodec` replaces
`AVSampleBufferDisplayLayer` and draws to a `SurfaceView`.

## 2c. How the switching works

The phone has one Wi-Fi radio, so it joins **either** the A7 V's network
**or** the CineView's network. Switching mode means: stop the current source,
release its network, join the other network, and start the other source.

```
            ┌──────────── app ────────────┐
  [Sony Direct]  ⇄  mode switch  ⇄  [Accsoon]
      │                                 │
 SonyDirectSource                  AccsoonSource
 (PTP/IP + MJPEG live view,        (TCP trigger + UDP H.264
  full controls over Wi-Fi)          + basic controls over BLE)
      └──── both implement VideoSource ────┘
            → one shared full-screen viewer + overlay
```

- `VideoSource` is a small interface: `connect()`, `disconnect()`, a picture
  output, a `status` flow, and `capabilities` (which controls it offers).
- The viewer screen is shared. Each mode lights only the keys it can honour;
  the others stay **dark** (the Mantra rule below), so your hand always finds
  each key in the same place.
- **Bluetooth runs beside either Wi-Fi.** In Accsoon mode the phone's Wi-Fi is
  on the CineView, but Bluetooth is a separate radio, so the A7 V's BLE remote
  service (`8000FF00`, the one Sony's RMT-P1BT remote uses; sarnau §1.10)
  still reaches the camera. It offers:

  | Over BLE (Accsoon mode) | Over Wi-Fi only (Sony Direct) |
  |---|---|
  | REC start/stop, shutter half/full, AF-On, **C1** (assign any camera function to it), focus near/far jog, power-zoom jog, and status: focusing, shutter, recording | ISO, shutter speed, aperture, exp. comp, WB, tap-to-focus point, readback of all settings |

  Watch out: sarnau found the camera's *Bluetooth Rmt Ctrl* setting and
  *smartphone pairing* can't both be on. We test what that means on the A7 V.
- The app remembers each mode's Wi-Fi network (SSID/password, or the scanned
  QR code), so a switch is a single tap.

---

## 2d. The look: borrowed from Mantra Manual Camera and Mantra Monitor

Our `mantra-ndi` repo (the NDI camera app and its sister Mantra Monitor) already
has the interface we want. We copy its pieces where they fit and adapt them
where they don't. They're **ready to try, not decided**; each one is an
experiment.

| From mantra-ndi | What it is there | How we'd use it here |
|---|---|---|
| Palette (`colors.xml`: ink, surface, slate, sand, amber, quiet, fault) | fixed across every Mantra app; colour is the only state signal | the same, so it looks like one family |
| `RailButton.kt` (shared) | drawn keys: **grey = off, green = on, dark = this device can't** | the same keys; a key dark in Accsoon mode (e.g. ISO) stays in place |
| **Two rails** beside a 16:9 `AspectFrame` | the keys live in the black margins of a 20:9 phone, never on the picture | the same: Sony and Accsoon pictures are 16:9 (3:2 for Sony stills) |
| `ControlZones.kt` | mixer faders across the picture (ISO, shutter, focus, WB), relative drag, an A / M switch each | Sony Direct: ISO, shutter speed, aperture, exp. comp, WB, snapped to the steps the camera allows |
| `RecordButtonView.kt` | white circle, red while rolling | REC in both modes (PTP in Sony Direct, BLE in Accsoon) |
| `FULL` key | clean feed, double tap brings the keys back | the same |
| Monitor: **double tap in the middle → sources** | lists every NDI source; tap one to watch it, remembered next time | **the mode switch**: double tap → *Sony Direct · A7 V* / *Accsoon · CineView Nano* |
| Monitor: status line + `MarksOverlay.kt` | one line of what's connected and why nothing shows | the same, plus the A7 V's focus frames drawn from its live-view data |
| `PreviewEffects.kt` | focus peaking, false colour, zebra, LUT on the GPU, monitor only | on both pictures; especially useful for checking an S-Log3 picture |
| `CameraCommand.kt` (shared) | one flat command vocabulary (iso, shutter, focus x/y, record, key…) | the same idea: one `CameraCommand`, and each mode turns it into PTP or BLE, or says the key is dark |
| Telemetry line, timecode, REC timer | top/bottom readouts | camera battery, card time left, REC timer |

---

## 2e. Several cameras (Marko, 22.10.2026)

Marko often shoots with **three or more Sonys, an Accsoon CineView Nano on each**. The app holds several
cameras at once and switches between them with one key. Visualised first at
**https://mantrasonyremote.pages.dev** (source `site/public/`); no app code for this yet.
Research of 22.10.2026 below; **H** = vendor docs or source, **M** = secondary or inferred, **L** = thin.

### The camera rail
The Mantra Manual Camera lens keys (L1–L5 on the left rail, `CameraCatalogue` + `RailButton`) become
**CAM1–CAM5**, same place, same logic. Each is a two-line key: the word, and the body in a whisper
(`CAM2` / `a6600`). Colour is the state, as in the CAMERA language:

| Colour | Means |
|---|---|
| green | the camera you are on (its picture fills the box, the right rail steers it) |
| grey | connected, waiting |
| dark | no camera on this key; the key stays in place |
| red dot | this camera is on program (tally), the same dot as on its multiview tile |

Each camera remembers its own source (Sony direct or Accsoon); the double tap still opens SOURCES for the
camera you are on. Keys the current camera's source cannot honour go dark (ISO, SHTR, IRIS in Accsoon).

### Compatibility tiers

| Tier | Bodies | Wi-Fi | Bluetooth (`8000FF00` remote) |
|---|---|---|---|
| **Network** | A7 V (ILCE-7M5), A7 IV (ILCE-7M4); later A7C II, a6700, FX3 | Remote Shoot over an access point (the camera joins the phone hotspot or a router as for a PC, Access Authen. or pairing), PTP/IP 15740, live view HTTP :60152; also Wi-Fi Direct. A7 V also USB-LAN/tethering (H) | REC, shutter, AF, focus/zoom jog; one BLE remote per body (H) |
| **Direct** | a6600 (ILCE-6600); likely a6400, a6100 | **only its own Wi-Fi Direct AP** (DIRECT-xxxx, 192.168.122.1) or USB PC Remote. Not in Sony's Imaging Edge access-point list, no "PC Remote Cnct Method" item (H). Protocol on its AP: legacy Camera Remote API (JSON-RPC/SSDP) or PTP/IP — alpha-fairy probes both; **measure on Marko's a6600** (M/L). USB PTP tested by argallo (H) | Bluetooth Rmt Ctrl with RMT-P1BT (H); excludes phone location linking |
| **Picture** | any HDMI camera | the clean picture through its Accsoon, one Nano per phone | Sony bodies as above |

**Sony's README (2.02.00, read 22.10.2026) settles it:** the A7 V speaks PTP 3 over USB and IP; the A7 IV PTP 3 (and
the deprecated PTP 2) over USB and IP; **the a6600 speaks only PTP 2, and only over USB** (no IP). So the a6600's
official road is the USB cable; over Wi-Fi only its own Direct AP with the legacy API, or Bluetooth.
Use PTP 3 wherever a body has it (PTP 2 is deprecated for bodies that have both, may end by 2027).

### The network topology
- **The phone has one Wi-Fi radio.** Every CineView Nano is its own AP at 10.0.0.1 (5 GHz only, ~60 ms,
  up to **4 phones per Nano**); no client (STA) mode found (M). Several Nanos on one phone: not normally;
  in theory 2 with Android 12+ STA+STA local-only concurrency
  (`isStaConcurrencyForLocalOnlyConnectionsSupported()`), each socket bound to its own `Network` (L for the Pixel 7).
- **Several cameras = one shared network**: the phone's hotspot or a travel router (fixed DHCP leases,
  clean 5 GHz, phone free). Network-tier bodies join it; discovery by SSDP (the "DigitalImaging" service),
  because apps cannot read the ARP table on Android 10+; manual IP as the fallback. Plan Step 9 becomes central.
- **The a6600 cannot join the shared network.** Its picture comes from its Nano (if the phone can hold the
  hotspot and the Nano together: STA+AP concurrency, `isStaApConcurrencySupported()`, to be measured) or by
  USB; its keys come over Bluetooth.
- **USB-C hub with Ethernet**: Android supports USB Ethernet, and USB host gives PTP to the a6600. Hub power
  and several devices on one hub to be tested (M).
- **Bluetooth**: Android's usual cap is 7 BLE links, 3–4 Sony remotes is comfortable (M). Each body takes one
  BLE remote at a time.

### Multiview
Every tool agrees: preview left/upper, **program right**, **red = on air, green = next, grey = idle**, the
name bottom-centre on a dark translucent box (OBS `Multiview.cpp`: program `0xFFD00000`, preview
`0xFF00D000`, others `0xFF999999`, 6 px border, H; vMix colours only the title bar, M; ATEM Mini: PVW left,
PGM right, inputs below, red/green tally borders, M).
- **3 cameras + program (2×2)**: four 16:9 tiles in the 16:9 box (2400×1080 phone: 1920×1080 block, the
  rails beside it). **PGM top right**, CAM1 top left, CAM2 bottom left, CAM3 bottom right. Tap a tile or a
  CAM key = preview (green); **CUT** or **AUTO** (time in its whisper) takes it to program (red). The tally
  dot repeats on the CAM key.
- **2-camera switcher**: PVW left (green), PGM right (red), CUT and AUTO on the right rail.
- **Alternative to try**: one big PGM plus three small cameras stacked beside it (OBS "Vertical").
- **Experiment**: preview-then-CUT (director) vs one tap straight to program (solo).
- The tiles' pictures: network-tier cameras send their PTP/IP live view (~25 fps JPEG, 640/1024); the one
  Nano the phone holds sends H.264.

### New steps (after S1, one at a time)
- **M1: Two network cameras.** Both join the phone hotspot (or a travel router), two CAM keys, switching.
- **M2: The a6600.** Its own Wi-Fi Direct: which protocol answers (PTP/IP or JSON-RPC), what works; USB; BLE keys.
- **M3: Three cameras + multiview.** The 2×2, preview/program, tally on tiles and keys.
- **M4: The switcher.** CUT and AUTO; the 2-camera layout.
- **M5: Hotspot + Nano together** (STA+AP), and STA+STA for a second Nano, measured on the Pixel 7.

---

## 3. Feature-by-feature plan

Rule: **one feature at a time.** Each step ends with a test on your real
equipment and your OK before the next step starts. Nothing from later steps is
built early.

Every step includes:
- **Unit tests** (JVM, no hardware): packet encoding and decoding against byte
  captures, and parsers.
- **A fake-device test**: small simulators, one for the Sony PTP/IP + HTTP side
  and one for the Accsoon TCP + UDP side, so the logic is checked in CI without
  hardware.
- **A real-equipment check**: a short checklist you run with a debug APK.

### Step 0: Project skeleton with the mode switch
- Android project (Kotlin, Android Views like mantra-ndi so `RailButton` and
  `ControlZones` drop in unchanged, minSdk 29), a single `:app` module for now.
  The `:ptp` / `:liveview` modules (from Imagedge, with `NOTICE`) arrive in
  Step 1 and `:accsoon` in Step A1. GitHub Actions builds the debug APK.
- The Mantra look from §2d: palette, `RailButton`, the two rails around a 16:9
  box, and a **double tap in the middle** that opens the source list
  (*Sony Direct* / *Accsoon*). Both sources show an empty picture box for now,
  every camera key is dark, and FULL (the clean picture) already works.
- **Test:** CI is green, the APK installs, the double tap opens the list,
  picking a source changes the status line, and the choice is remembered after
  a restart.
- **Decide:** do the rails feel right for this app, or do we try a different
  layout?

### Sony Direct: picture

**Step 1: Connect (phone → camera Wi-Fi)**
- You turn on remote shooting on the camera, then the app joins `DIRECT-…`
  (via `WifiNetworkSpecifier` or QR scan) and runs the PTP/IP handshake.
- It shows the model, firmware and vendor code version, and writes a
  shareable log of every property and control your A7 V supports.
- **Real test:** the connection succeeds 5 times in a row; switching the camera
  off shows "Disconnected" within 10 s; the keep-alive holds for 30 minutes.

**Step 2: Live view**
- Read `LiveViewUrl` and stream the frames full-screen, with an fps counter
  and a choice of 640 or 1024 quality.
- **Real test:** ≥20 fps for 10 minutes, delay under ~300 ms (film a stopwatch
  next to the phone), no memory growth, and auto-recovery after Wi-Fi drops.

### Accsoon: picture

**Step A1: Accsoon connect and stream**
- Port `CineViewCore` to Kotlin with its tests. Join the CineView Wi-Fi, run
  the TCP trigger loop and the UDP receiver, and show resolution, fps and
  codec as text, without decoding yet.
- **Real test on the Nano:** frames arrive and the numbers match the camera's
  HDMI output. If nothing arrives, follow CINEVIEW_VIEWER HANDOVER points 2–3
  (traffic capture, then compare the first bytes) and record the result there.
  This is the **first real Nano test ever**, so it also checks the Mac viewer's
  protocol.

**Step A2: Accsoon picture on screen**
- Decode the H.264 with `MediaCodec` onto the shared viewer.
- **Real test:** 10 minutes with no tearing or freezes; delay compared
  side-by-side with Sony Direct mode.

**Step A3: Accsoon + Bluetooth remote (basic controls without switching)**
- Pair the phone with the camera as a Bluetooth remote. While the Accsoon
  picture is on screen, the REC, shutter, AF-On and C1 keys and the focus/zoom
  jog work over BLE, and REC turns red from the camera's own status.
- **Real test:** with the camera across the room, start and stop 5 clips and
  take 5 photos while watching the Accsoon picture, without switching mode.
- **Experiment to decide:** what C1 should be on the camera (e.g. Eye AF or
  focus-area reset), and whether the jog speed is usable for pulling focus.

### Switching

**Step S1: Switch between the two modes**
- One tap: stop the current source, change Wi-Fi, start the other. The app
  remembers both networks.
- **Real test:** 10 switches in a row each way. Each one shows a picture
  within ~10 s, and nothing stays connected in the background.

### Sony Direct: control (only in Sony Direct mode)

**Step 3: Take a photo**
- S1 → wait for focus → S2 → release, with sarnau's delays. Success is
  confirmed by `SDIE_CapturedEvent`, not just "OK".
- **Real test:** 20 photos, 20 files; the app shows an error, not false
  success, when the card is missing.

**Step 4: Video REC start/stop**
- A REC button, a recording indicator and a timer, all read back from the
  camera.
- **Real test:** 1-minute and 10-minute clips; the button stays correct when
  REC is pressed on the camera itself.

**Step 5: Exposure control**
- ISO, shutter, aperture, exposure compensation (and WB). The app only offers
  values the camera allows, and changes on the camera's dials show up in the
  app.
- **Real test:** every change shows in the live view; dial changes appear in
  the app within 1 s.

**Step 6: Focus point**
- Tap the live view to set `AFAreaPosition`, and draw the camera's focus frame.
- **Real test:** tap left/right/center while standing in front of the camera;
  the frame follows and the face stays sharp.

**Step 7: Solo-operator comfort (both modes)**
- Mirror toggle, big buttons, keep the screen on, shutter self-timer, and
  landscape and portrait layouts.
- **Real test:** you record a clip alone, start to finish, in each mode.

### Sony Direct: other networks

**Step 8: Camera on the phone hotspot.** Find the camera's IP or enter it by
hand. **Test:** Steps 1–6 pass again in this mode.

**Step 9: Camera and phone on the house Wi-Fi.** "Remote Shoot" on an access
point, plus Access Authentication / SSH if the A7 V requires it. **Test:**
Steps 1–6 pass again in this mode.

### Later
- BLE wake-up and automatic Wi-Fi handoff for Sony Direct, a USB-cable mode
  (argallo), and photo download.

---

## 4. Risks we know about
- The A7 V firmware may differ from the A7R V; Step 1's log answers this.
- The Accsoon protocol has never been tested on a Nano (CINEVIEW_VIEWER was
  never run); Step A1 answers this.
- Android may send traffic to mobile data when the camera or CineView Wi-Fi
  has no internet. Each source binds its sockets to its own network.
- Switching Wi-Fi on Android 10+ needs the user to confirm the network once
  per network. After that it should be one tap; Step S1 measures this.
- House-Wi-Fi mode may need SSH authentication (Step 9).
- I can't test on the real equipment myself. Each real check needs you to run
  the debug APK and send back the in-app log.

---

## 5. Experiment log

One line per experiment: what we tried, what the real test showed, and the
decision (keep / change / drop).

| Date | Step | Tried | Result on real equipment | Decision |
|---|---|---|---|---|
| 22.10.2026 | 0 | the stage: Mantra rails, double-tap SOURCES, FULL | built, 11 unit tests pass; not yet on the phone | waiting for Marko |
| 22.10.2026 | page | multi-camera visualised on mantrasonyremote.pages.dev: CAM rail, 2×2 multiview, 2-camera switcher, topology, tiers | drawn, not yet seen by Marko | waiting for Marko |
