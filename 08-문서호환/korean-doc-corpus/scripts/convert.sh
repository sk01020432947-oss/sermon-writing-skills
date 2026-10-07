#!/bin/zsh
# Finder 빠른 동작·바탕화면 앱 공용: 인자로 받은 폴더/파일을 MD로 변환하고 알림을 띄운다.
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
S="${0:A:h}/batch_to_md.py"
note() { osascript -e 'on run a' -e 'display notification (item 1 of a) with title (item 2 of a)' -e 'end run' "$1" "$2"; }
for p in "$@"; do
  p="${p%/}"
  n=$(basename "$p")
  [ -d "$p" ] && note "변환 중…" "문서 → MD: $n"
  r=$(python3 "$S" "$p" 2>&1 | tail -1)
  note "$r" "문서 → MD: $n"
  if [ -d "$p" ] && [ -d "${p}_md" ]; then open "${p}_md"; fi
done
exit 0
