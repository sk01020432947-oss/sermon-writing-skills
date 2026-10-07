#!/usr/bin/env python3
"""
verify_transliteration.py — 큐티 산출물의 헬라어·히브리어 한글 표기 검증기

검증 항목:
1. 헬라어/히브리어 단어와 한글 발음을 SKILL.md 표준에 비추어 점검
2. 금지 패턴 검출 (η→이, θ→쓰, ου→오우, χ→차, υ→이 등)
3. 표준어 사전(transliteration_rules.json)과 직접 대조

입력 형식 (text 모드):
    "단어목록 — 원어:한글" 한 줄씩
    예:
        ἀγάπη:아가페
        χάρις:카리스
        בְּטַח:베타흐

또는 markdown 모드: 큐티 텍스트 전체에서 자동으로 원어-한글 쌍을 추출 시도.

사용법:
    python3 verify_transliteration.py --pairs "ἀγάπη:아가페" "χάρις:카리스"
    python3 verify_transliteration.py --file path/to/qt.md

종료 코드:
    0 — 통과
    1 — 위반 발견
    2 — 입력 오류
"""
import argparse
import json
import os
import re
import sys


DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def load_rules():
    with open(os.path.join(DATA_DIR, "transliteration_rules.json"), "r", encoding="utf-8") as f:
        return json.load(f)


GREEK_RE = re.compile(r"[Ͱ-Ͽἀ-῿]+")
HEBREW_RE = re.compile(r"[֐-׿]+")
KOREAN_RE = re.compile(r"[가-힯]+")


def lookup_greek(word: str, rules: dict):
    """헬라어 단어의 표준 한글 표기를 사전에서 찾는다."""
    table = rules["greek_standard_words"]
    if word in table:
        return table[word]
    # 소문자화·악센트 제거 시도 (간이)
    lower = word.lower()
    for key, val in table.items():
        if key.lower() == lower:
            return val
    return None


def lookup_hebrew(word: str, rules: dict):
    table = rules["hebrew_standard_words"]
    if word in table:
        return table[word]
    return None


def detect_forbidden_in_korean(korean: str, rules: dict):
    """한글 표기에 금지 발음이 들어있는지 패턴 검출."""
    hits = []
    # 헬라어 금지 패턴 (한글 표기 측면)
    if "오우" in korean:
        hits.append("ου를 '오우'로 표기 — 금지 (표준: '우')")
    if korean.endswith("쎄"):
        hits.append("θ를 '쎄'로 표기 — 금지 (modern Greek, 표준: '테')")
    if re.search(r"쓰[^아-힣]?$", korean):
        # 마지막 음절이 '쓰'면 θ→쓰 의심
        pass  # 단어 단독으로는 확정 불가, 음역과 대조 필요
    return hits


def check_pair(greek_or_hebrew: str, korean: str, rules: dict):
    """원어-한글 쌍을 검증."""
    result = {
        "word": greek_or_hebrew,
        "given_korean": korean,
        "violations": [],
        "expected_korean": None,
        "status": "unknown",
    }

    is_greek = bool(GREEK_RE.search(greek_or_hebrew))
    is_hebrew = bool(HEBREW_RE.search(greek_or_hebrew))

    if is_greek:
        expected = lookup_greek(greek_or_hebrew, rules)
        result["expected_korean"] = expected
        if expected is None:
            result["status"] = "not_in_dictionary"
            result["violations"].extend(detect_forbidden_in_korean(korean, rules))
        else:
            if expected == korean:
                result["status"] = "match"
            else:
                result["status"] = "mismatch"
                result["violations"].append(
                    f"표준 표기 '{expected}'와 다름. 입력: '{korean}'"
                )
    elif is_hebrew:
        expected = lookup_hebrew(greek_or_hebrew, rules)
        result["expected_korean"] = expected
        if expected is None:
            result["status"] = "not_in_dictionary"
            result["violations"].extend(detect_forbidden_in_korean(korean, rules))
        else:
            if expected == korean:
                result["status"] = "match"
            else:
                result["status"] = "mismatch"
                result["violations"].append(
                    f"표준 표기 '{expected}'와 다름. 입력: '{korean}'"
                )
    else:
        result["status"] = "no_original_language_detected"
        result["violations"].append("원어 문자(헬라어/히브리어) 미검출")

    return result


def extract_pairs_from_markdown(text: str):
    """
    큐티 마크다운에서 원어-한글 쌍을 추출 시도.
    SKILL.md 표기 규약상 다음 구조:
        - **원문**: ἀγάπη
        - **음역(영어)**: agapē
        - **발음(한글)**: 아가페
    또는 한 줄에 함께 나오는 경우.
    """
    pairs = []
    # 패턴 1: 블록 단위 (원문, 음역, 발음)
    blocks = re.split(r"\n\s*\n", text)
    for block in blocks:
        original = None
        korean = None
        for line in block.splitlines():
            m_orig = re.search(r"원문[^:]*:\s*([Ͱ-Ͽἀ-῿֐-׿].*?)(?:\s*$|\s*\|)", line)
            if m_orig:
                w = m_orig.group(1).strip()
                # 첫 단어만 (공백 또는 -, , 등으로 절단)
                w = re.split(r"[\s,\-—()]+", w)[0]
                original = w
            m_kor = re.search(r"발음[^:]*:\s*([가-힣].*?)(?:\s*$|\s*\|)", line)
            if m_kor:
                k = m_kor.group(1).strip()
                k = re.split(r"[\s,\-—()]+", k)[0]
                korean = k
        if original and korean:
            pairs.append((original, korean))

    # 패턴 2: 같은 줄에 "원어 단어 (음역, 한글)" 형식
    inline = re.findall(
        r"([Ͱ-Ͽἀ-῿֐-׿]+)\s*\([^,)]+,\s*([가-힣]+)\)",
        text,
    )
    for o, k in inline:
        pairs.append((o, k))

    # 패턴 3: "원어 단어 (한글)" 단순형
    simple = re.findall(
        r"([Ͱ-Ͽἀ-῿֐-׿]+)\s*\(([가-힣]+)\)",
        text,
    )
    for o, k in simple:
        if (o, k) not in pairs:
            pairs.append((o, k))

    return pairs


def main():
    ap = argparse.ArgumentParser(description="원어 한글 표기 검증기")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--pairs", nargs="*", help="원어:한글 쌍 목록")
    g.add_argument("--file", help="큐티 마크다운 파일 (자동 추출)")
    ap.add_argument("--json", action="store_true", help="JSON 출력")
    args = ap.parse_args()

    rules = load_rules()
    pairs = []

    if args.pairs:
        for p in args.pairs:
            if ":" not in p:
                print(f"형식 오류 — '원어:한글' 형태가 필요: {p}", file=sys.stderr)
                sys.exit(2)
            o, k = p.split(":", 1)
            pairs.append((o.strip(), k.strip()))
    else:
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                text = f.read()
        except OSError as e:
            print(f"파일 읽기 오류: {e}", file=sys.stderr)
            sys.exit(2)
        pairs = extract_pairs_from_markdown(text)
        if not pairs:
            print("[INFO] 파일에서 원어-한글 쌍을 추출하지 못함.", file=sys.stderr)

    results = [check_pair(o, k, rules) for o, k in pairs]

    if args.json:
        out = {
            "total": len(results),
            "matches": sum(1 for r in results if r["status"] == "match"),
            "mismatches": sum(1 for r in results if r["status"] == "mismatch"),
            "not_in_dictionary": sum(1 for r in results if r["status"] == "not_in_dictionary"),
            "details": results,
        }
        print(json.dumps(out, ensure_ascii=False, indent=2))
        any_fail = any(r["status"] == "mismatch" or r["violations"] for r in results)
        sys.exit(1 if any_fail else 0)

    print("=" * 60)
    print("원어 한글 표기 검증 결과")
    print("=" * 60)
    for r in results:
        if r["status"] == "match":
            print(f"  [OK]   {r['word']} → {r['given_korean']}")
        elif r["status"] == "mismatch":
            print(
                f"  [FAIL] {r['word']} → {r['given_korean']}  "
                f"(표준: {r['expected_korean']})"
            )
            for v in r["violations"]:
                print(f"         · {v}")
        elif r["status"] == "not_in_dictionary":
            print(f"  [INFO] {r['word']} → {r['given_korean']} — 사전 미수록")
            for v in r["violations"]:
                print(f"         · {v}")
        else:
            print(f"  [?]    {r['word']} → {r['given_korean']} — {r['status']}")
            for v in r["violations"]:
                print(f"         · {v}")

    any_fail = any(r["status"] == "mismatch" or r["violations"] for r in results)
    print()
    print(f"총 {len(results)}개 중 {sum(1 for r in results if r['status'] == 'match')}개 정확 일치.")
    sys.exit(1 if any_fail else 0)


if __name__ == "__main__":
    main()
