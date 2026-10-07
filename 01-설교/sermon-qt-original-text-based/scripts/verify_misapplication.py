#!/usr/bin/env python3
"""
verify_misapplication.py — 큐티 산출물의 본문 비약·이단적 풀이 패턴 검출

검증 항목:
1. 사용자가 다루는 본문이 한국 교회 빈번 비약 본문(빌 4:13·렘 29:11 등)일 때 그
   본문 특유의 함정 키워드가 산출물에 들어가 있는지 점검
2. 이단적 풀이 트리거 (양태론·종속론·신천지·통일교·영지주의·번영신학·새시대운동·점성술)
3. 일반 경고 문구 ("이 본문을 외우면 반드시 부와 건강…" 등)

사용법:
    python3 verify_misapplication.py --text "큐티 텍스트" --ref "빌 4:13"
    python3 verify_misapplication.py --file path/to/qt.md --ref "잠 3:5-6"

종료 코드:
    0 — 통과
    1 — 경고 있음
    2 — 입력 오류
"""
import argparse
import json
import os
import re
import sys


DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def load_patterns():
    with open(os.path.join(DATA_DIR, "misapplication_patterns.json"), "r", encoding="utf-8") as f:
        return json.load(f)


def normalize_ref(ref: str) -> str:
    """본문 약어 정규화. 공백·하이픈 통일."""
    s = ref.strip().replace("–", "-").replace("—", "-")
    s = re.sub(r"\s+", " ", s)
    return s


def check_passage_traps(text: str, ref: str, patterns: dict):
    """이 본문이 빈번 비약 본문이면 그 함정 키워드 점검."""
    hits = []
    ref_n = normalize_ref(ref)
    for entry in patterns["passage_specific_traps"]:
        entry_ref_n = normalize_ref(entry["ref"])
        # 정확 일치 또는 prefix 일치 (예: "빌 4:13" 입력 시 entry "빌 4:13" 매치)
        if entry_ref_n in ref_n or ref_n in entry_ref_n:
            for trap in entry["traps"]:
                if trap in text:
                    hits.append({
                        "ref": entry["ref"],
                        "trap_phrase": trap,
                        "orthodox": entry["orthodox"],
                    })
    return hits


def check_heretical(text: str, patterns: dict):
    """이단적 풀이 트리거 검출."""
    hits = []
    for h in patterns["heretical_patterns"]:
        for phrase in h["trigger_phrases"]:
            if phrase in text:
                hits.append({
                    "label": h["label"],
                    "phrase": phrase,
                    "orthodox": h["orthodox"],
                })
    return hits


def check_general(text: str, patterns: dict):
    """일반 경고 문구 검출."""
    hits = []
    for phrase in patterns["general_warning_phrases"]:
        if phrase in text:
            hits.append(phrase)
    return hits


def main():
    ap = argparse.ArgumentParser(description="본문 비약·이단 풀이 검출")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--text", help="검증할 큐티 텍스트")
    g.add_argument("--file", help="텍스트 파일 경로")
    ap.add_argument("--ref", default="", help="본문 약어 (예: '빌 4:13')")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                text = f.read()
        except OSError as e:
            print(f"파일 읽기 오류: {e}", file=sys.stderr)
            sys.exit(2)
    else:
        text = args.text

    patterns = load_patterns()

    passage_hits = check_passage_traps(text, args.ref, patterns) if args.ref else []
    heretical_hits = check_heretical(text, patterns)
    general_hits = check_general(text, patterns)

    if args.json:
        out = {
            "passage_trap_hits": passage_hits,
            "heretical_hits": heretical_hits,
            "general_warning_hits": general_hits,
            "pass": not (passage_hits or heretical_hits or general_hits),
        }
        print(json.dumps(out, ensure_ascii=False, indent=2))
        sys.exit(0 if out["pass"] else 1)

    print("=" * 60)
    print("본문 비약·이단 풀이 검출 결과")
    print("=" * 60)
    any_hit = False

    if passage_hits:
        any_hit = True
        print(f"\n[WARN] 본문 함정 키워드 {len(passage_hits)}건:")
        for h in passage_hits:
            print(f"  - [{h['ref']}] 함정 문구: '{h['trap_phrase']}'")
            print(f"    정통 해석: {h['orthodox']}")

    if heretical_hits:
        any_hit = True
        print(f"\n[ALERT] 이단적 풀이 트리거 {len(heretical_hits)}건:")
        for h in heretical_hits:
            print(f"  - [{h['label']}] '{h['phrase']}'")
            print(f"    정통: {h['orthodox']}")

    if general_hits:
        any_hit = True
        print(f"\n[WARN] 일반 경고 문구 {len(general_hits)}건:")
        for p in general_hits:
            print(f"  - '{p}'")

    if not any_hit:
        print("[PASS] 비약·이단 풀이 패턴 검출 없음.")

    sys.exit(1 if any_hit else 0)


if __name__ == "__main__":
    main()
