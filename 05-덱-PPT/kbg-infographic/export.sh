#!/bin/bash
# 사용: export.sh <포스터.html>  → 같은 폴더에 .png(1400px 폭, 2배 해상도)와 .pdf를 만든다.
set -e
in="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
base="${in%.html}"
chrome="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
# 포스터 실제 높이를 재서 잘림 없이 찍는다
h=$("$chrome" --headless=new --disable-gpu --virtual-time-budget=6000 --window-size=1400,1000 \
  --dump-dom "file://$in" 2>/dev/null | grep -o 'data-h="[0-9]*"' | grep -o '[0-9]*')
h=${KBG_H:-${h:-2400}}
"$chrome" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=2 \
  --virtual-time-budget=6000 --window-size=1400,"$h" --screenshot="$base.png" "file://$in" 2>/dev/null
"$chrome" --headless=new --disable-gpu --virtual-time-budget=6000 --no-pdf-header-footer \
  --print-to-pdf="$base.pdf" "file://$in" 2>/dev/null
echo "$base.png"; echo "$base.pdf"
