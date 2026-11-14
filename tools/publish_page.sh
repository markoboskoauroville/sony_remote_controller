#!/usr/bin/env bash
# The page gets the released APK by itself (MANTRA_MANIFEST modules/download-always-latest.md, 1.11.2026).
# Usage: tools/publish_page.sh <released.apk> <version> [<release date d.m.yyyy>]
# Puts the APK at site/public/download/SonyRemote.apk (an address with no version, written once in index.html),
# writes the version, date and size into the page, and deploys site/public to mantrasonyremote.pages.dev.
# Run by the Build workflow right after the release; CLOUDFLARE_API_TOKEN and CLOUDFLARE_ACCOUNT_ID in the environment.
set -euo pipefail
APK="$1"; V="$2"; D="${3:-$(date -u +%-d.%-m.%Y)}"
cd "$(dirname "$0")/.."
PAGE=site/public/index.html
OUT=site/public/download/SonyRemote.apk

case "$V" in ''|*[!0-9]*) echo "version is not a whole number: $V"; exit 1;; esac
[ "$(head -c 2 "$APK")" = "PK" ] || { echo "not an APK: $APK"; exit 1; }
BYTES=$(stat -c%s "$APK" 2>/dev/null || stat -f%z "$APK")
[ "$BYTES" -lt 26214400 ] || { echo "APK is $BYTES bytes, over Cloudflare Pages' 25 MB per file"; exit 1; }
MB=$(( (BYTES + 524288) / 1048576 ))

mkdir -p site/public/download
rm -f site/public/download/*.apk
cp "$APK" "$OUT"

# The page names the version in spans the run fills; the address of the button never changes.
sed -i.bak -E \
  -e "s#(<span class=\"app-version\">)[0-9]+(</span>)#\1${V}\2#g" \
  -e "s#(<span class=\"app-date\">)[0-9.]+(</span>)#\1${D}\2#g" \
  -e "s#(<span class=\"app-size\">)[0-9]+(</span>)#\1${MB}\2#g" "$PAGE"
rm -f "$PAGE.bak"
grep -q "href=\"download/SonyRemote.apk\"" "$PAGE" || { echo "the button does not link download/SonyRemote.apk"; exit 1; }
echo "page: v$V, $D, $MB MB; $OUT = $BYTES bytes"

npx --yes wrangler@4 pages deploy site/public --project-name mantrasonyremote --branch main --commit-dirty=true
