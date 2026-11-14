# Lessons

1. **The a6600 cannot be remote-controlled through a router or hotspot** (22.10.2026). Its Wi-Fi remote is only its
   own Direct AP (or USB). Sony's Imaging Edge access-point list leaves it out and its menu has no "PC Remote Cnct
   Method". So in a multi-camera setup it comes in through its Accsoon picture and Bluetooth keys.
2. **A CineView Nano is always its own AP at 10.0.0.1, 5 GHz only**; no client mode found. A phone holds one Nano at a
   time (two in theory with STA+STA concurrency). A Nano can feed up to four phones.
3. **Multiview colours are an industry rule**: program right and red, preview left and green, idle grey, the name at
   the bottom on a dark box (OBS Multiview.cpp, ATEM, vMix).
4. **Headless Chrome will not make a window narrower than about 485 px**: to check a page at 390 px, render it in a
   390 px iframe (22.10.2026).
5. **`[hidden]` loses to a `display:` rule**: add `[hidden]{display:none!important}` when a hidden element also has a
   display set (the multiview showed both layouts at once).
6. **Sony's own README: the a6600 is PTP 2 over USB only** (Camera Remote Command 2.02.00, 22.10.2026). No IP, no
   PTP 3. The A7 V is PTP 3 over USB and IP. The package's licence is personal use: the repository stays private.
7. **The CineView Nano does not speak accsoon-decode's protocol** (28.10.2026, Marko's Nano, Accsoon_00EA, 5 GHz ch 36,
   password 12345678): TCP 8001 refuses; open are 21 (vsFTPd 3.0.3), 23 (a login), 28101 and 28102 (silent until spoken
   to). The real handshake is in Accsoon SEE (com.accsoon.uvctransmission); read it from the app, never guess the login.
8. **The Mac has one Wi-Fi**: to join a Nano it first takes its internet from the Pixel's USB tethering and puts the
   "Pixel 7" service first in `networksetup -ordernetworkservices`, or this session is cut off. Put the order back after.
9. **The Nano's real protocol is Accsoon's "RTMS" (rtms_4_0 / wit07, namespace accsoon_2025_02_25)**, read from Accsoon SEE
   (com.accsoon.uvctransmission) on 28.10.2026: control on TCP **28101** with a frame head **9528** (0x2538), the picture
   by UDP from the Nano's port **28000** to the client's **28001**, keep-alive timeout 6000 ms, up to 4 stations; the
   client connects by uid, the Nano answers with a profile (JSON) naming video and audio streams. It lives in native
   code (librtms_4_0_client.so, libwit07_rtms_client.so), so the Mac receiver needs that code read (disassembled), not
   guessed. Until then the picture reaches the Mac through the Pixel: Accsoon SEE on the Pixel, mirrored by scrcpy.

## 29.10.2026, TC Jam
- *.apk in .gitignore silently kept the beta off the page: the link served index.html with an APK content type. Check
  the first bytes of a download (PK) after every deploy.
- The α7 V's Time Code Preset is plain binary, not BCD (a BCD 0x10 became 16:00 on its screen).
- A Bluetooth scan filtered on Sony's manufacturer bytes 03 00 found nothing; an open scan found both cameras at once.
- Two cameras in one shot: read the time code nearest a box the user drags, never the first one found.
- Labels must say direction: "PHONE TC GENERATOR → CAMERA (USB)", not "JAM". The word REC is red everywhere.

## 1.11.2026, download links by themselves
- The Build workflow had failed on every push since 28.10.2026 and nobody looked: `gradle/actions/setup-gradle@v4`
  validates every gradle-wrapper.jar in the checkout, including third-party code under reference/. Its v4 has no
  allow-list input (`allow-checksums` is "unexpected"); a sparse checkout of only what the build uses fixed it.
- Once a workflow fills the page's download, git must not hold the APK and no other workflow may deploy the page on
  push: a page-only deploy would publish the folder without the APK, and two deploys of one push race.
- Cloudflare Pages sends no content-length for a 21 MB APK (chunked): compare a live download with the release
  byte for byte (cmp in CI, free there), not by headers, and not on the Mac's SIM.
- Pages `_redirects` splat in the middle of a name works: `/download/mantra-sony-remote-v* /download/SonyRemote.apk 301`.

## 14.11.2026
- A USB_DEVICE_ATTACHED intent-filter on a launcher activity makes the app jump up and claim the device every time it is
  plugged in. If another app should own the device (Manual Camera uses the Sony as UVC), keep the filter out: the app lists
  and asks permission only when the user opens it.
- Marko's repos have one branch, `main`; this repo started on a ccr- branch and was moved to main on 14.11.2026.
