# The page: mantrasonyremote.pages.dev

The app drawn before it is built (Marko, 22.10.2026: "first a web page, no app code yet"). Static files in
`public/`. Candle language for the page (MANTRA_MANIFEST language-candle.md); the app's screens inside it are drawn
in the CAMERA language (green on, grey off, dark unavailable, red live) and their keys work, so the switching can be felt.

Deploy (since 1.11.2026, MANTRA_MANIFEST download-always-latest.md): **by the Build workflow only**, on every push to
the default branch, right after the release: `tools/publish_page.sh` puts the released APK at
`download/SonyRemote.apk` (the button's address, never with a version), writes the version, date and size into the
`app-version` / `app-date` / `app-size` spans, and runs wrangler. A redeploy without a build: Actions → "Deploy to
Cloudflare Pages" → Run workflow. Never deploy `site/public` by hand from the Mac: git holds no APK, so a hand deploy
would take the download off the page. Old links (`download/mantra-sony-remote-vN.apk`) 301 to the fixed one (`_redirects`).

Pictures: `img/hero.jpg` (and the camera scenes) come from Nano Banana in Gemini, in Marko's Chrome. Until they
exist the page shows "photograph in the making" and warm gradients stand in for the camera pictures.
