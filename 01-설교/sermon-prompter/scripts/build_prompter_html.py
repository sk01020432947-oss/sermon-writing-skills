#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
설교 프롬프터(텔레프롬프터) HTML 빌더
─────────────────────────────────────────────
설교를 구조화한 JSON을 받아 assets/template.html에 주입하여
일정한 속도로 위로 자동 스크롤되는 프롬프터 HTML 파일을 생성한다.
글꼴 선택 · 글자 크기 · 배경(밝게/어둡게) · 스크롤 속도 조절 버튼이 탑재된다.

사용:
  python build_prompter_html.py --input sermon.json --out "설교프롬프터.html"

JSON 스키마:
{
  "title":         "설교 제목",                       (필수)
  "subtitle":      "주일설교 · 2026.06.07 · ○○○ 목사",       (선택, 상단 라벨)
  "scripture_ref": "마태복음 5:1-12 (개역개정)",       (필수, 본문 표기)
  "scripture_text":"본문 봉독 텍스트(개역개정)",        (선택, 있으면 본문 카드 생성)
  "sections": [                                       (필수, H1 = 읽기 단위)
    { "heading": "서론",      "text": "단락 본문..." },
    { "heading": "1. 첫째 대지","text": "..." },
    ...
  ]
}

본문 작성 규칙(text 필드):
  - 빈 줄로 문단 구분
  - **강조**  → <strong> (이탤릭 없음)
  - 「」『』  → 그대로 표기
  - 줄 맨 앞 >  → 인용(blockquote)
  - 줄 맨 앞 // → 설교자 메모(.no-tts, 낭독에서 제외)
이미 완성된 HTML을 직접 넣으려면 "text" 대신 "html" 필드를 사용한다.
"""

import argparse
import datetime
import html
import json
import re
import sys
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent.parent / "assets" / "template.html"


def inline(s: str) -> str:
    """HTML 이스케이프 후 **굵게** 처리."""
    s = html.escape(s, quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    return s


def split_commas(sentence: str):
    """한 문장을 최상위 쉼표(, ，) 뒤에서 나눈다.
    따옴표·괄호 안의 쉼표, 숫자 안 쉼표(1,000)는 끊지 않는다."""
    openers, closers = "(（[「『“", ")）]」』”"
    out, buf, depth, in_quote = [], "", 0, False
    n = len(sentence)
    i = 0
    while i < n:
        ch = sentence[i]
        if ch in openers:
            depth += 1; buf += ch
        elif ch in closers:
            depth = max(0, depth - 1); buf += ch
        elif ch == '"':
            in_quote = not in_quote; buf += ch
        elif (ch in ",，" and depth == 0 and not in_quote
              and (i + 1 >= n or sentence[i + 1] in " \u3000")):
            buf += ch
            out.append(buf.strip()); buf = ""
            j = i + 1
            while j < n and sentence[j] in " \u3000":
                j += 1
            i = j - 1
        else:
            buf += ch
        i += 1
    if buf.strip():
        out.append(buf.strip())
    return out


def _split_sentence(line: str):
    """한 줄을 종결부호(. ! ? 。 …) 뒤 공백에서 문장 단위로 나눈다. 따옴표·괄호 안은 보존."""
    return [p.strip() for p in re.split(r"(?<=[.!?。…])\s+", line) if p.strip()]


def split_sentences(block_text: str):
    """한 문단을 문장 단위로, 다시 쉼표 단위로 분리한다(강단 낭독용 줄나눔)."""
    out = []
    for line in block_text.splitlines():
        line = line.strip()
        if not line:
            continue
        for part in _split_sentence(line):   # 1차: 문장
            out.extend(split_commas(part))   # 2차: 쉼표
    return out


def split_quote(quote_lines):
    """인용(성경 구절)을 문장 단위로 나눈다. 작성자가 나눈 줄은 유지하되,
    한 줄 안에 여러 문장이 있으면 문장마다 줄을 바꾼다. 쉼표는 끊지 않는다."""
    out = []
    for raw in quote_lines:
        line = raw.lstrip()
        if line.startswith(">"):
            line = line[1:]
        line = line.strip()
        if not line:
            continue
        out.extend(_split_sentence(line))
    return out


def md_to_html(text: str) -> str:
    """간이 마크다운 → HTML (문단/인용/메모/굵게).

    본문 문단은 문장마다 줄을 바꾸고(<br>), 문단과 문단 사이는
    한 줄(빈 줄)을 띄운다. 인용·메모는 작성자가 나눈 줄을 그대로 보존한다.
    """
    text = text.replace("\r\n", "\n").strip()
    out = []
    for blk in re.split(r"\n\s*\n", text):
        lines = [ln for ln in blk.splitlines() if ln.strip()]
        if not lines:
            continue
        # 설교자 메모(낭독 제외)
        if all(ln.lstrip().startswith("//") for ln in lines):
            inner = " ".join(ln.lstrip()[2:].strip() for ln in lines)
            out.append(f'<div class="no-tts">✎ {inline(inner)}</div>')
        # 인용 — 문장마다 줄바꿈(작성자 줄 유지, 쉼표는 끊지 않음)
        elif all(ln.lstrip().startswith(">") for ln in lines):
            inner = "<br>".join(inline(s) for s in split_quote(lines))
            out.append(f"<blockquote>{inner}</blockquote>")
        # 일반 문단 — 문장 단위로 줄바꿈
        else:
            sents = split_sentences(blk)
            out.append("<p>" + "<br>".join(inline(s) for s in sents) + "</p>")
    return "\n      ".join(out)


def build_sections(sections) -> str:
    cards = []
    for i, sec in enumerate(sections):
        heading = html.escape(str(sec.get("heading", "")).strip(), quote=False)
        body = sec.get("html") or md_to_html(sec.get("text", ""))
        cards.append(
            f'<section class="sermon-block" id="blk-{i}" data-index="{i}">\n'
            f'    <h1 class="block-title">\n'
            f'      <span class="block-title-text">{heading}</span>\n'
            f'      <button class="btn-read" data-target="{i}">▶ 읽기</button>\n'
            f"    </h1>\n"
            f'    <div class="block-body">\n      {body}\n    </div>\n'
            f"  </section>"
        )
    return "\n\n  ".join(cards)


def build_scripture(text: str) -> str:
    if not text or not text.strip():
        return ""
    paras = "\n    ".join(
        f"<p>{inline(ln.strip())}</p>"
        for ln in re.split(r"\n+", text.strip())
        if ln.strip()
    )
    return (
        '<div class="scripture-card">\n'
        '    <div class="sc-label">📖 본문 봉독</div>\n'
        f"    {paras}\n"
        "  </div>"
    )


def main():
    ap = argparse.ArgumentParser(description="설교 프롬프터 HTML 빌더")
    ap.add_argument("--input", required=True, help="설교 구조 JSON 경로")
    ap.add_argument("--out", required=True, help="출력 HTML 경로")
    ap.add_argument("--template", default=str(TEMPLATE), help="템플릿 경로(기본: assets/template.html)")
    args = ap.parse_args()

    data = json.loads(Path(args.input).read_text(encoding="utf-8"))

    title = str(data.get("title", "설교")).strip()
    subtitle = str(data.get("subtitle", "")).strip()
    ref = str(data.get("scripture_ref", "")).strip()
    sections = data.get("sections", [])
    if not sections:
        sys.exit("오류: sections 가 비어 있습니다.")

    tpl = Path(args.template).read_text(encoding="utf-8")
    repl = {
        "{{PAGE_TITLE}}": html.escape(title, quote=False),
        "{{DOC_TITLE}}": html.escape(title, quote=False),
        "{{DOC_SUBTITLE}}": html.escape(subtitle, quote=False) or "SERMON",
        "{{SCRIPTURE_REF}}": html.escape(ref, quote=False),
        "{{SCRIPTURE_BLOCK}}": build_scripture(data.get("scripture_text", "")),
        "{{SERMON_SECTIONS}}": build_sections(sections),
        "{{GEN_DATE}}": datetime.date.today().isoformat(),
    }
    for k, v in repl.items():
        tpl = tpl.replace(k, v)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(tpl, encoding="utf-8")
    print(f"✅ 생성 완료: {out}  (단락 {len(sections)}개)")


if __name__ == "__main__":
    main()
