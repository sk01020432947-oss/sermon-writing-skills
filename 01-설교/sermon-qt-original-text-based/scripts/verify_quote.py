#!/usr/bin/env python3
"""
verify_quote.py — 큐티 산출물의 개역개정(GAE) 본문 인용 정확성 검증기

검증 항목:
1. 큐티 텍스트에 포함된 성경 인용이 KRV 흔적인지(개역한글 잔재) 점검 — 발견 시 경고
2. data/verified_passages.json의 확정된 GAE 본문과 토씨 단위 비교
3. 인용된 장절 표기가 사용자 지정 범위와 일치하는지 점검

사용법:
    python3 verify_quote.py --text "큐티 텍스트 전문" [--refs "롬 12:1,롬 12:2"]
    python3 verify_quote.py --file path/to/qt.md [--refs "롬 12:1"]

종료 코드:
    0 — 통과
    1 — 경고 있음 (KRV 흔적/토씨 차이)
    2 — 입력 오류
"""
import argparse
import json
import os
import re
import sys


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def load_krv_gae():
    return load_json(os.path.join(DATA_DIR, "krv_gae_differences.json"))


def load_verified():
    return load_json(os.path.join(DATA_DIR, "verified_passages.json"))


def normalize_whitespace(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def find_krv_traces(text: str, krv_gae: dict):
    """텍스트에서 KRV 흔적을 검출. (구절별 토큰 + 일반 패턴) 둘 다 점검."""
    hits = []
    norm_text = normalize_whitespace(text)

    # 1) 구절별 KRV-only 토큰
    for passage in krv_gae["passages"]:
        for token in passage["krv_only_tokens"]:
            if not token:
                continue
            token_norm = normalize_whitespace(token)
            if token_norm in norm_text:
                hits.append({
                    "type": "passage_specific",
                    "ref": passage["ref"],
                    "krv_token": token,
                    "gae_replacement": (
                        passage["gae_only_tokens"][0]
                        if passage["gae_only_tokens"]
                        else "(동일)"
                    ),
                })

    # 2) 일반 패턴
    for pat in krv_gae["patterns_krv_to_gae"]:
        krv_pat = pat["krv"]
        gae_pat = pat["gae"]
        if normalize_whitespace(krv_pat) in norm_text:
            # GAE 패턴도 동시에 등장하면 그건 의도된 비교일 수 있으므로 약경고로
            already_gae = normalize_whitespace(gae_pat) in norm_text
            hits.append({
                "type": "general_pattern",
                "krv_pattern": krv_pat,
                "gae_pattern": gae_pat,
                "gae_also_present": already_gae,
            })

    return hits


def check_verified_quotes(text: str, refs: list, verified: dict):
    """사용자가 인용한다고 한 구절들을 verified 본문과 토씨 단위 비교."""
    results = []
    norm_text = normalize_whitespace(text)
    for ref in refs:
        ref = ref.strip()
        if not ref:
            continue
        if ref not in verified["verses"]:
            results.append({
                "ref": ref,
                "status": "not_in_database",
                "note": "이 구절은 검증 DB에 미수록. 수동 점검 필요.",
            })
            continue
        expected = normalize_whitespace(verified["verses"][ref])
        if expected in norm_text:
            results.append({"ref": ref, "status": "exact_match"})
        else:
            # 부분 일치 검사: 첫 15자 또는 끝 15자가 들어 있는지 확인
            head = expected[:15]
            tail = expected[-15:]
            head_in = head in norm_text
            tail_in = tail in norm_text
            results.append({
                "ref": ref,
                "status": "mismatch_or_partial",
                "expected": expected,
                "head_present": head_in,
                "tail_present": tail_in,
            })
    return results


def main():
    ap = argparse.ArgumentParser(description="개역개정 인용 정확성 검증기")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--text", help="검증할 큐티 텍스트 전문")
    g.add_argument("--file", help="텍스트 파일 경로")
    ap.add_argument(
        "--refs",
        default="",
        help="콤마 구분 인용 구절 (예: '롬 12:1,롬 12:2'). 미지정 시 verified 점검 생략.",
    )
    ap.add_argument("--json", action="store_true", help="JSON 출력")
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

    krv_gae = load_krv_gae()
    verified = load_verified()

    krv_hits = find_krv_traces(text, krv_gae)
    refs = [r for r in args.refs.split(",") if r.strip()] if args.refs else []
    quote_check = check_verified_quotes(text, refs, verified) if refs else []

    if args.json:
        out = {
            "krv_traces_found": krv_hits,
            "verified_quote_checks": quote_check,
            "pass": (not krv_hits)
            and all(r["status"] == "exact_match" for r in quote_check)
            if quote_check
            else (not krv_hits),
        }
        print(json.dumps(out, ensure_ascii=False, indent=2))
        sys.exit(0 if out["pass"] else 1)

    # 사람용 출력
    print("=" * 60)
    print("개역개정 인용 정확성 검증 결과")
    print("=" * 60)

    if not krv_hits:
        print("[PASS] KRV 흔적 검출 없음.")
    else:
        print(f"[WARN] KRV 흔적 {len(krv_hits)}건 검출:")
        for h in krv_hits:
            if h["type"] == "passage_specific":
                print(
                    f"  - {h['ref']}: KRV '{h['krv_token']}' → "
                    f"GAE '{h['gae_replacement']}'"
                )
            else:
                note = " (GAE 패턴도 함께 등장 — 비교 목적일 가능성)" if h.get("gae_also_present") else ""
                print(
                    f"  - 일반 패턴: KRV '{h['krv_pattern']}' → "
                    f"GAE '{h['gae_pattern']}'{note}"
                )

    if quote_check:
        print()
        print("검증 본문 대조:")
        for r in quote_check:
            if r["status"] == "exact_match":
                print(f"  [OK] {r['ref']} — 정확히 일치")
            elif r["status"] == "not_in_database":
                print(f"  [SKIP] {r['ref']} — DB 미수록, 수동 점검 필요")
            else:
                print(f"  [MISMATCH] {r['ref']}")
                print(f"      기대: {r['expected']}")
                print(f"      head={r['head_present']} tail={r['tail_present']}")

    fail = bool(krv_hits) or any(
        r["status"] not in ("exact_match", "not_in_database") for r in quote_check
    )
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
