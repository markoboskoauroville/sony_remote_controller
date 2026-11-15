# Takeover: Mantra Sony Remote

**Where it is (22.10.2026).** Android app (Kotlin, Android Views), package `com.mantraproductions.sonyremote`, branch
`ccr-7270d80e-knr8l8` (the default). Step 0 built in the cloud (11 unit tests, assembleDebug), not yet on a phone.
Moved to the Mac session ("DaVinci Resolve Router and Monitor") on 22.10.2026 at Marko's word.

**Now: visualisation before code, done (22.10.2026 evening).** https://mantrasonyremote.pages.dev (`site/`): the CAM
rail, the 2×2 multiview, the 2-camera switcher, the network, the tiers, the road; five Nano Banana photographs (hero,
CAM1 wide, CAM2 hands, CAM3 singer, kit); the kit with 8 Amazon.de affiliate links (markomantresh-21; site registered
in PartnerNet by Marko). Card 14 "KAMERA" on markobosko.pages.dev (concept). Sony's Camera Remote Command 2.02.00 is in
reference/sony-official, on the Mac only (see *Local only* below). Marko: *"Looks fantastic."*

**Next:** Step 0 on the Pixel 7 emulator (check its GitHub build first), then Marko's phone; then Step 1, the A7 V.

**Local only, not in git (14.11.2026).** The repository is public (it builds on GitHub), so two things stay on Marko's Mac:
- `reference/` (whole folder, gitignored) at /Users/markobosko/Developer/SONY_REMOTE_CONTROLLER/reference. It holds
  Sony's Camera Remote Command 2.02.00 (`reference/sony-official/`, Sony's personal-use licence: it may not be published),
  copies of third-party projects without a licence (and one with Sony's PTP 3 PDF), and code from a private repo of ours.
  Nothing in it is built. A cloud session does not have it; ask the Mac session.
- the test-builds signing key: /Users/markobosko/Developer/SONY_REMOTE_CONTROLLER/signing/test-builds.p12 and its password and alias in
  signing/signing.properties (both gitignored). The workflow gets them from the repository secrets SIGNING_KEYSTORE_B64,
  SIGNING_STORE_PASSWORD and SIGNING_KEY_ALIAS.

**Read first:** PLAN.md (§2e for several cameras), momentaryupdates.md (his words), reference/README.md (Mac only; the code we
build on and its licences), LESSONS.md.

**Waiting for Marko:** "start the app" for Step 0.

## TC JAM (v2–v27, 29.10.2026): the first part that works on real cameras

Launcher "TC Jam" (TcJamActivity), opens by itself when a Sony camera is plugged in. Files: TcJamActivity.kt (screen,
generator, USB PTP jam, clap, status displays, help), BleRemote.kt (Bluetooth remote commander 8000FF00: REC on all,
FF02 recording reports, SYNC CAMERA REC BUTTONS = follow), ScreenReader.kt (Camera2 + ML Kit on-device OCR, sensor crop
for pinch zoom and pan, reads the time code nearest the draggable box), Ltc.kt (SMPTE LTC 25 fps out).
- Generator = phone clock + an offset (prefs "offset") taken from a camera's screen; PHONE CLOCK → PHONE TC GENERATOR resets it.
- USB jam: Sony handshake 0x9201 1/2, 0x9202 (0x012C PTP 3 / 0x00C8 PTP 2), 0x9201 3; 0x9209 lists settings; 0x9205 sets
  0xD0D6 Run=2 Free Run, 0xD0D7 Make=1 Preset, 0xD0D3 = h<<24|m<<16|s<<8|f **binary**; the camera reads back the old value
  for ~0.5 s. α7 V on USB PORT 1, USB Cnct Mode: Remote Shoot/Trn. The a6600 (PTP 2) has no time code over USB.
- Opening the app from its icon never jams; a plug-in, the USB key or `--es tc HH:MM:SS:FF` does. Test doors: `--es tc`,
  `--ez read true` (opens the reader).
- Clap: 1, 2, 3 kHz 300 ms each 500 ms apart, then the chord; torch one frame (40 ms) with each; white slate at the chord.
- Beta on mantrasonyremote.pages.dev at **download/SonyRemote.apk**, an address with no version (since 1.11.2026,
  MANTRA_MANIFEST download-always-latest.md). arm64 only (21 MB, under Pages' 25 MB). No APK in git any more.
Not verified: LTC with a decoder; the a7 V's own REC button report; the clap timing against picture.

## Inside Mantra Manual Camera (31.10.2026)

The whole TC Jam (TcJamActivity, BleRemote, Ltc, ScreenReader, AspectFrame) is copied into Mantra Manual Camera v187
(MANTRA_NDI `app/src/main/java/com/mantraproductions/ndi/sony/`), opened from its Settings → SONY, with one shared
Bluetooth remote (SonyLink) that the camera's top line (SONY STBY / ● SONY REC k/n) and its REC hold (START SONY) also
use. The camera's copy has an upright fix this app does not have yet: the camera displays stack under the flag and the
six keys form two rows of three (upright, side by side they were squeezed and cut words). **Next here:** port that fix.
The site lists every Sony Alpha body on Amazon.de (#alphas, 34 permanent dp/ listings, checked by title 31.10.2026).

## The download follows every release by itself (1.11.2026)

- **Build** (.github/workflows/build.yml), on every push: tests, assembleDebug, release `vN` (prerelease, the two newest
  kept), then, on the default branch only, *Put the release on the page*: downloads that release's APK,
  `tools/publish_page.sh` puts it at site/public/download/SonyRemote.apk, writes appVersion, the date and the size into
  the `app-version` / `app-date` / `app-size` spans of index.html, deploys with wrangler (repo secrets
  CLOUDFLARE_API_TOKEN / CLOUDFLARE_ACCOUNT_ID), and checks the live file byte for byte against the release.
- A push to a test branch still makes a release (as before) but never touches the public page.
- **Deploy to Cloudflare Pages** (deploy-pages.yml) is now a hand redeploy only (Run workflow): the committed page with the
  release of the current appVersion. It no longer runs on push (git holds no APK; two deploys would race).
- Old links `download/mantra-sony-remote-vN.apk` 301 to the fixed one (site/public/_redirects).
- CI was red since 28.10.2026: setup-gradle's wrapper check refused the third-party wrapper jar in
  reference/legacy-api/timelapse-sony. The build checks out only .github, app, signing, site, tools (sparse), so the
  check stays on and passes. First green Build: run 41277446446, 1.11.2026.
- A new version: raise appVersion, push to the default branch. Nothing else; never deploy site/public by hand.

## 14.11.2026: TC Jam no longer jumps on the camera (v29), and the branch is main

Marko: "when I plug camera, what is coming up automatically is my time code adjusting application. Please don't make this
application jump and take my camera." Cause: TcJamActivity had an intent-filter for `USB_DEVICE_ATTACHED` with meta-data
`@xml/sony_usb`, so Android opened TC Jam on every Sony plug-in and TC Jam took the USB device, while Mantra Manual Camera
should use the Sony as a UVC camera. Fix (v29): the filter, the meta-data and `res/xml/sony_usb.xml` are removed; nothing in
the app opens the Sony's USB interface unless Marko opens TC Jam himself (it then asks USB permission as before). Bluetooth
remote unchanged. No receiver or service claims USB in the background (only the in-activity permission receiver).
Branch: `main` created from ccr-7270d80e-knr8l8 and made the GitHub default; build.yml runs on push to main and marks the
release Latest. (The two old branches were deleted later that day, see below.) No updater (checkAtStart) yet.

## 14.11.2026 (evening): the repository is public, one fresh root commit, v29 built
Marko: "Everything. What is building goes public? Go public." Private builds were stopped by billing, so the repo was made
public after the three checks of MANTRA_MANIFEST building-repos-public.md (patterns, exact values against the local key store,
a fresh clone): clean. Before that:
- `reference/` (Sony's Camera Remote Command under a personal-use licence, unlicensed third-party copies, Sony's PTP 3 PDF,
  code from the private CINEVIEW_VIEWER) left git and is gitignored; it stays on the Mac (see *Local only* at the top).
- `signing/test-builds.p12` left git; the key, its password and alias are the repository secrets SIGNING_KEYSTORE_B64,
  SIGNING_STORE_PASSWORD, SIGNING_KEY_ALIAS. build.yml writes the key from the secret; app/build.gradle.kts reads the two
  values from the environment, or from signing/signing.properties on the Mac. The same key, so v29 installs over v28.
- tools/__pycache__ untracked. History rewritten to ONE root commit (author: the GitHub no-reply address), main force-pushed,
  the branches ccr-7270d80e-knr8l8 and claude/compassionate-volta-sqmlza deleted, tags v28/v1 moved to the new root.
  The old history is kept only as a local git bundle, never pushed.
- First run failed (`java.util` shadowed by Gradle's `java` extension: import java.util.Properties fixed it); then green:
  https://github.com/markoboskoauroville/sony_remote_controller/actions/runs/43637922124, v29 released and marked Latest,
  the page updated by the workflow.

## 15.11.2026: the Mac side is its own repository
Sony Remote (Mantra) for the Mac (record the α7 V on its card from the Mac over Wi-Fi, PTP-IP through the camera's SSH
Access Authentication, door 127.0.0.1:8881) lives in markoboskoauroville/SONY_REMOTE_MAC (~/Developer/SONY_REMOTE_MAC).
It is written from the same Camera Remote Command documents in reference/sony-official, which stay here, local only.
