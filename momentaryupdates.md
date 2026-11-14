# Momentary updates: every request, word for word, before any code

## 22.10.2026 — handed over from the cloud session to the Mac session (DaVinci Resolve Router and Monitor)

Marko to the cloud session "Sony Alpha Android remote controller", twice: *"You need to go to DaVinci Resolve Router and Monitor and work from there."*
The request, as the cloud session relayed it (its summary of Marko's words):

1. MULTI-CAMERA: he often shoots with 3+ Sonys, each with an Accsoon attached. The app must hold several connections at once, with very easy switching between cameras. Reuse the Mantra Manual Camera LENS SWITCHER (L1–L5 keys on the rail): same logic and UI, but the keys pick a camera (CAM 1, 2, 3…) instead of a lens.
2. COMPATIBILITY: must work with the Alpha a6600 and the newest bodies such as the A7 V. He also has an older Sony (ask which model) and wants to see how much works over Wi-Fi. Research: the a6600 predates Sony's "Camera Remote Command" over Wi-Fi (Imaging Edge Mobile, old Camera Remote API / Smart Remote, USB PC Remote).
3. MULTIVIEW (research + development): split the screen into 4, three quarters for three cameras and one for the final output (Program). Study OBS Studio's and vMix's Multiview and copy the layout so it is clear what is live and what is preview. With 2 cameras it also works as a 2-camera switcher.
4. Constraints for the plan: one Wi-Fi radio on the phone, while every CineView Nano and every camera's Direct Wi-Fi is its own AP, so several cameras means one shared network (camera Remote Shoot over an access point, his router or the phone hotspot; Plan Step 9 becomes central). Check whether the CineView Nano can join a network as a client, or how Accsoon's multi-transmitter setups work. Android can hold several BLE connections (Bluetooth keys on several cameras).
5. FIRST A WEB PAGE, NO APP CODE YET: visualisation first, then the code. Lifestyle images, connection diagrams, the multiview layout, the camera-switcher rail, the principles; the UI developed visually without code. Name: mantrasonyremote.pages.dev (one word, no dashes), Cloudflare Pages. Images through Gemini in his Chrome on a free session (or Kie AI). Read MANTRA_MANIFEST first. Then update PLAN.md on the branch to match: multi-camera, the camera rail, compatibility tiers, multiview, the network topology.

**Status:** picked up on the Mac 22.10.2026. The older Sony, Marko: *"Alpaha 660"*, read as the a6600 (ILCE-6600): the a6600 is the older body, the A7 V the new one.

## 22.10.2026 — reference material (to the cloud session)

Marko: *"copy and download stuff. Sony SDK. Any source code you can find. So everything is handy there"*
**Status:** done by the cloud session in 16c3cb5 (`reference/`, 16 projects, index in reference/README.md). Sony's official Camera Remote Command and SDK wait for Marko to apply and accept the license (reference/sony-official/README.md).

## 22.10.2026, evening — pictures, Sony's licence, affiliate links

- *"Chrome is open. Please start working"*
- *"You need to use multiple accounts in the Chrome. Google has Gemini, has multiple accounts. Everything is in a manifest. Read manifest. Why you are lazy."* / *"Manifolds also say to use multiple accounts at the same time to generate multiple images at the same time to speed up the process."* / *"You don't need to switch to Pro ... just don't touch Gemini model. Just go and create image."*
- *"Sony's license I don't understand what to do. Where to go? How to do this?"* / *"Only pages open. Please fill up everything you know about me and I do the rest.Sony"* / *"Camera remote is in downloads. Please push it to GitHub."*
- *"In a web page, please add affiliated links like in my other pages which are selling something. We're going to sell this application in the future for my ads soon transmitter."* (*"acsoon transmiter"*) / *"website is added to partners on Amazon Germany. Please now make affiliate links. For all products which make sense."*
- *"Please continue generating images and update my website. I'm going to eat something."*

**Status:** done. Five Nano Banana pictures (u/0 and u/3), Sony's package in reference/ (d9a70bf), the kit with 8 affiliate links (Nano, Beryl AX, Anker hub, coiled micro HDMI, SmallRig holder, A7 IV, a6700), live on mantrasonyremote.pages.dev (caaf43b).

## 24.10.2026 — a donation bowl for the development

- *"please add a donation box at the bottom of this page this time. The donation is for development, not yet developed, to help develop the app"*
- *"Donation box equals donation bowl."*

**Status:** done 24.10.2026: the bowl (#donate) at the bottom of mantrasonyremote.pages.dev, above the footer, worded for the development of the app; both steps checked locally and live.

## 28.10.2026 — start coding

- *"please start coding Sony remote"*

**Status:** started: Step 0 on the Pixel 7 emulator, then Step 1 (PTP/IP connect to the A7 V) against a fake camera.
- *"sony camera is also available. Let me know when I'm going to switch it on. We have the Alpha 75, and you let me know which menu items I need to enable, so there will be a flow of this camera screen to this computer"* (Alpha 75 = the A7 V)

## 28.10.2026 — the Accsoon picture on the Mac

- *"I have connected the camera with USB-C, but I also have connected Atsun Nano through HDMI. Please read Atsun Nano Wi-Fi and get the picture from my camera on this computer through the Wi-Fi Atsun Nano."* (Atsun = Accsoon)
- *"Show me an image from Nano on one display on my computer."*

**Status 08:20:** the Mac joined Accsoon_00EA (password 12345678, factory) with its internet through the Pixel's USB tethering; the Nano answers on TCP 21 (vsFTPd), 23 (a login), 28101, 28102, **not** 8001: accsoon-decode's protocol is not the Nano's. Now: the Pixel on the Nano runs Accsoon SEE (com.accsoon.uvctransmission), mirrored to the Mac by scrcpy; the Mac back on mantra. The SEE APK is kept for reading the Nano's real protocol (Step A1).

## 28.10.2026

"please let me know what the best free application is for remote shooting with my Sony camera. What is it? 7.5? Now the camera is in remote shooting mode. Let me see its picture and its parameters on the screen, please"

"now there is a whole set of applications from Sony to work with this camera. It means you can find all its settings. Please read its settings. You can now go into DaVinci Resolve and color grade my footage, which is on the timeline. You need to first normalize exposure in every shot, and then color grade it to be like some popular music video film stock. What they do, I don't know. Most of Rihanna or these popular artists make a picture look filmic and high-end. That's all you do color grading in DaVinci Resolve and then export all individual clips in the folder of footages. For Svenir, you can make a folder and put them inside, because he is editing on a 20-year-old PC. It must be MP4, H.264, not 5, and the data rate must be set so it's full HD. We also resize the image. Data rate: make it 20 megabits per second"

"You need to find repository mantra color profile and please set PP Picture Profile 1 to exactly that one in this camera and picture profile two to this filmic one. The best we were looking for the profile which is maximum Dynamic range for this camera."

"also, by the way, please I'm downloading DaVinci Resolve Studio 21.1.2. Please, in a voice, read me what's new in this edition"

"sorry, I have closed the remote thing. We are also developing a remote control for the app, and then you can use this app to find all the settings inside the camera. Please use the app Mantra remote control. Don't use anything from Sony."

"our remote control app should be able to read and change color profiles from the app itself"

"no need to dig through menus. When I, for example, use some other camera, I can just push my color profiles into it without any delays"

"please, when you read anything from this chat or anything using this local voice engine, you need to give me Blob to control this voice. Blob has a simple user interface: one arrow, a round arrow going backwards. It means repeat, repeat from the top. It has pause, and it has X to stop talking, and that's it. It's similar to this Blob from Speechify, which I'm using, and you can see the screenshot on the desktop from it right now. That's it"

"please change my shortcut to enter the prompt immediately from Option Enter to Command Enter, please, in iTerm"

"please burn in this workflow inside the DaVinci Resolve workflows. It is called \"Balancing, Grading, and Exporting Automatic.\" Next time, I don't need to use the UAI tool. I just press a button and everything is happening automatically"

"I have a tool in a star menu called \"DaVinci Resolve Actions.\" Inside, put this action and make a tab for Actions. Please redesign the user interface for this application with tabs and group different styles of working. This is Actions"

## 29.10.2026 (a GitHub deploy workflow)

> Yes, any repository which doesn't have a deploy workflow should be added, yes.

**Status:** done 29.10.2026: .github/workflows/deploy-pages.yml publishes site/public to mantrasonyremote.pages.dev on every push to ccr-7270d80e-knr8l8.

## 29.10.2026, 12:55 — the timecode generator in the phone (Marko, word for word)

"Yes, we're going to build it. Now I connected my camera via USB to my Pixel 7 phone. First, build the app, which is going to just sync, or better to say, can you build a timecode generator inside the phone? Then I connect with USB first, 6600, and then my Alpha 75. Then when they recognize it's connected, they jam the time code automatically."

(Before it, 12:50: "Do you think you can build the action for DaVinci Resolve to synchronize this kind of footage with music beats? ... align it by the music, not by sound." → yes, "Sync by music" in DAVINCI_RESOLVE_ACTIONS, after this.)
Finding 12:46: the a6600 has time code (its screen showed 12:46:58:01 beside the α7 V's 12:46:58:05, both Free Run by hand).
**Status 13:01 (v4):** TC JAM screen in the app (launcher "TC Jam", opens by itself when a Sony camera is plugged in). Deck-style
display (one line, sized to the width, amber over unlit 88s, TCG / FREE RUN / 25P NDF / SRC PHONE CLOCK). MEASURED on the a6600
over USB: Sony handshake OK, PTP 2, 83 settings, **no Time Code Preset (0xD0D3), Run or Make**: the a6600 cannot be jammed by
the phone through Sony's protocol. Next: the α7 V (PTP 3 lists 0xD0D3/0xD0D6/0xD0D7).
Marko 12:58: "Please design a nice screen for time code, like they have it in Betacam scopes. Sound is distorting." 

**Status 13:30:** REC BOTH CAMERAS over Bluetooth WORKS (Marko: "It works. Both cameras were recording when I pressed the button"). a6600 and α7 V bonded with the Pixel (camera: Bluetooth Rmt Ctrl On + Pairing), FF01 01 0F/01 0E. Learned: the first 30 s scan with a 03 00 manufacturer filter found nothing; an open scan (company 0x012D or name ILCE) found both at once.

**Status 13:35:** the α7 V JAMMED over USB PORT 1 (USB Cnct Mode: Remote Shoot/Trn.): PTP 3, 449 settings, Time Code Preset accepted, value **plain binary** hour<<24|min<<16|sec<<8|frame (a BCD 0x10 became 16:00, measured on its screen). The camera reports the old value for ~0.5 s after a set. Marko asked for 10:00:00:00: sent 0x0a000000, read back 10:00:00:00. A chosen time code: adb am start ... --es tc HH:MM:SS:FF.

## 29.10.2026, 13:40–13:50 (Marko)

"You need to jam the phone to my screen of my 6600, and then when it is jammed, I can walk to another camera and just jam it ... list the models in this app under Help." / "build into this app also a digital clapboard ... after two seconds ... three beeps" / "I will open the camera from this app in full screen, and under the camera will be the running time code ... change of color ... so I know they are synced." / "When camera is recording triggered through Bluetooth, is it possible to have confirmation ... when it stops recording, I can see that".

**Status (v9):** the generator = phone clock + an offset jammed from a camera screen (ML Kit on-device OCR, interval lock over 12+ readings); full-screen reader, CAMERA and PHONE time codes, amber → green when locked, keeps checking (IN SYNC ±frames / DRIFTED); USB jams use the generator; HELP lists PTP 3 (USB time code) and PTP 2-only models (Sony README 2.02.00); CLAP: 2 s after REC, three beeps 1 s apart (the third 2 kHz) and a white slate with the time code; Bluetooth REC confirmations logged per camera (FF02 0xD5). Not yet seen working: the reader, the clap, the confirmations.

## 29.10.2026, 13:40–13:50 (Marko)

"You need to jam the phone to my screen of my 6600 ... list the models in this app under Help." / "a digital clapboard ... after two seconds ... three beeps" / "the camera ... in full screen, and under the camera ... the running time code ... change of color ... so I know they are synced." / "is it possible to have confirmation ... when it stops recording, I can see that".

**Status (v9):** generator = phone clock + an offset jammed from a camera screen (ML Kit OCR, interval lock over 12+ readings); full-screen reader, CAMERA and PHONE time codes, green when locked and in sync; USB jams use the generator; HELP lists PTP 3 and PTP 2-only models; CLAP 2 s after REC: three beeps, white slate at the third. **MEASURED: the a6600 reports REC pressed on its body over Bluetooth (FF02 0xD5), start and stop.** Not yet seen: the reader, the clap.

## 29.10.2026, 13:58 (Marko)

"Please fix the bugs, update the app, and offer this app on my Sony remote page ... released as a beta version for testers ... V1, V2, V3. We are going by whole numbers."

**Status:** v14 beta on mantrasonyremote.pages.dev (site/public/download/mantra-sony-remote-v14.apk, arm64 only, 21 MB, under Cloudflare Pages 25 MB), beta section + hero button, download counter (data-dl-app mantra-sony-remote).

**Status 14:15 (v18):** full-screen time code (⛶ or a tap on the display) for the cameras to film; AUDIO TC (LTC) OUT: SMPTE LTC 25 fps, biphase mark, 48 kHz, latency from AudioTrack timestamps (not yet checked with an LTC decoder); reader: one finger inside the box moves it, outside pans the picture (sensor crop), two fingers zoom. Marko: "if you send over the speaker ... the longitudinal time code ... can the cameras recording and editing software recognize this ... Maybe we can build this app for the Star Menu."

## 1.11.2026: the page order (banner, introduction, lifestyle, technical, donation)

> "the page is perfect. Let's do it all pages" (Marko, 1.11.2026, about mantramiditools.pages.dev)

1. Every public app page in the order of MANTRA_MANIFEST modules/app-page-order.md: the banner (the app at work, name and one line on it), a short introduction with the download button and the version line, the lifestyle picture, the technical part, the donation bowl.

**Status:** done 1.11.2026 (site/public/index.html): banner = img/hero.jpg (the sound healing evening, the filmmaker's phone showing three cameras) with the icon and the name on it, the introduction with the v28 beta download, the technical part (TC Jam, the idea, the rail, multiview, network, cameras, kit, road), the bowl. The lifestyle picture is still needed (a placeholder comment marks its place), to be made in Gemini.
**Status, 1.11.2026 (later):** the lifestyle picture is in (made in Gemini, lifestyle.jpg); the page order is complete.

## 1.11.2026: no Mantra at the beginning of the name
> "please, you do renaming, and then let me write on the screen in big letters. You can close the session now" (1.11.2026)

**Status:** done: the page, the deploy scripts and the bio card say "<Name> (Mantra)".

## 1.11.2026: download links that follow every new version by themselves
> "yes, fix download links so every website gets each new version by itself" (Marko, 1.11.2026)

**Status:** done 1.11.2026: both buttons link download/SonyRemote.apk; the Build workflow, in the run that releases vN on the default branch, puts that release's APK there, writes vN, the date and the size into the page and deploys (run 41277729940: live file identical to release v28, 22368499 bytes, the page shows v28). Old download/mantra-sony-remote-vN.apk links 301 to it.

## 1.11.2026: My studio setup, a link above the bowl

> "Just above the Tibetan bowl for donation, you can just make one link, and then it will open the page with all lifestyle images and images of these products which I'm using in my development studio ... For this link, you can say "My studio setup." ... It is opening a new page, which is going to call studio setup mantra.pages.dev" (Marko, 1.11.2026)

1. One centred link "My studio setup" right above the donation bowl, opening https://studiosetupmantra.pages.dev in a new tab, with the line "The gear these apps are made with · affiliate links on Amazon.de".

**Status:** published 1.11.2026: studiosetupmantra.pages.dev registered in PartnerNet and live with the tag; Marko: "Please publish it."

## 14.11.2026: the camera must not be taken by TC Jam

"Camera is plugged. There is an issue When I plug camera, what is coming up automatically is my time code adjusting application. Please don't make this application jump and take my camera. It should be just run automatically without jumping on my camera." (Marko, 14.11.2026)
