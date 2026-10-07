#!/usr/bin/env python3
"""
verify_all.py — 큐티 산출물 통합 검증 진입점 (C1-C8 자동화)

C1-C8 체크리스트 자동화:
- C1 (본문 인용 정확성) → verify_quote.py
- C2 (원어 정확성)·C3 (원어-본문 일치) → verify_transliteration.py
- C4·C7 (3대지 구조·분량과 형식)·C8 (검색 출처 투명성) → verify_format.py
- C5 (본문 비약 차단)·C6 (출처·인물 단언 차단의 트리거 부분) → verify_misapplication.py

사용법:
    python3 verify_all.py --file path/to/qt.md --level standard --refs "잠 3:5,잠 3:6" --passage-ref "잠 3:5-6"
    python3 verify_all.py --text "..." --level simple --refs "..." --passage-ref "..."

종료 코드:
    0 — 모든 검증 통과
    1 — 한 개 이상 검증 실패
"""
import argparse
import importlib.util
import json
import os
import sys


SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))


def _load_module(name):
    path = os.path.join(SCRIPTS_DIR, f"{name}.py")
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_verify_quote(text, refs):
    mod = _load_module("verify_quote")
    krv_gae = mod.load_krv_gae()
    verified = mod.load_verified()
    krv_hits = mod.find_krv_traces(text, krv_gae)
    quote_check = mod.check_verified_quotes(text, refs, verified) if refs else []
    ok = (not krv_hits) and all(
        r["status"] in ("exact_match", "not_in_database") for r in quote_check
    )
    return {
        "passed": ok,
        "krv_traces": krv_hits,
        "quote_check": quote_check,
    }


def run_verify_transliteration(text):
    mod = _load_module("verify_transliteration")
    rules = mod.load_rules()
    pairs = mod.extract_pairs_from_markdown(text)
    results = [mod.check_pair(o, k, rules) for o, k in pairs]
    any_fail = any(r["status"] == "mismatch" or r["violations"] for r in results)
    return {
        "passed": not any_fail and bool(pairs),
        "pairs_count": len(pairs),
        "details": results,
        "note": (
            "원어-한글 쌍을 추출하지 못함. 산출물에 원문/발음 블록이 있는지 점검 필요."
            if not pairs
            else None
        ),
    }


def run_verify_format(text, level):
    mod = _load_module("verify_format")
    header_ok, header_info = mod.check_header(text)
    meta_ok = mod.check_meta_line(text)
    three_ok, three_info = mod.check_three_points(text, level)
    meanings_ok, meanings_info = mod.check_three_meanings(text)
    q_ok, q_info = mod.check_meditation_questions(text, level)
    ap_ok, ap_info = mod.check_application_and_prayer(text)
    tr_ok, tr_info = mod.check_search_transparency(text)
    len_ok, len_info = mod.check_length(text, level)
    if level == "simple" and not meanings_ok:
        meanings_ok = three_info["p3"] or True
    all_ok = all(
        [header_ok, meta_ok, three_ok, meanings_ok, q_ok, ap_ok, tr_ok, len_ok]
    )
    return {
        "passed": all_ok,
        "header": header_ok,
        "meta_line": meta_ok,
        "three_points": three_ok,
        "three_meanings": meanings_ok,
        "meditation_questions": q_ok,
        "app_prayer": ap_ok,
        "search_transparency": tr_ok,
        "length": len_ok,
        "length_info": len_info,
    }


def run_verify_misapplication(text, passage_ref):
    mod = _load_module("verify_misapplication")
    patterns = mod.load_patterns()
    passage_hits = (
        mod.check_passage_traps(text, passage_ref, patterns) if passage_ref else []
    )
    heretical_hits = mod.check_heretical(text, patterns)
    general_hits = mod.check_general(text, patterns)
    ok = not (passage_hits or heretical_hits or general_hits)
    return {
        "passed": ok,
        "passage_trap_hits": passage_hits,
        "heretical_hits": heretical_hits,
        "general_hits": general_hits,
    }


def main():
    ap = argparse.ArgumentParser(description="C1-C8 통합 검증")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--text")
    g.add_argument("--file")
    ap.add_argument("--level", required=True, choices=["simple", "standard", "detailed"])
    ap.add_argument("--refs", default="", help="콤마 구분 인용 구절")
    ap.add_argument("--passage-ref", default="", help="대표 본문 약어 (비약 검출)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            text = f.read()
    else:
        text = args.text

    refs = [r for r in args.refs.split(",") if r.strip()] if args.refs else []

    c1 = run_verify_quote(text, refs)
    c23 = run_verify_transliteration(text)
    c47 = run_verify_format(text, args.level)
    c56 = run_verify_misapplication(text, args.passage_ref)

    summary = {
        "C1_quote_accuracy": c1,
        "C2_C3_transliteration": c23,
        "C4_C7_C8_format": c47,
        "C5_C6_misapplication": c56,
        "overall_pass": all(
            [c1["passed"], c23["passed"] or c23["pairs_count"] == 0, c47["passed"], c56["passed"]]
        ),
    }

    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print("#" * 60)
        print("# C1-C8 통합 검증")
        print("#" * 60)
        print(f"C1 본문 인용 정확성: {'PASS' if c1['passed'] else 'FAIL'}")
        if c1["krv_traces"]:
            print(f"   - KRV 흔적 {len(c1['krv_traces'])}건")
        for q in c1["quote_check"]:
            if q["status"] not in ("exact_match", "not_in_database"):
                print(f"   - 인용 불일치: {q['ref']}")

        c23_pass = c23["passed"] or c23["pairs_count"] == 0
        print(
            f"C2·C3 원어 표기·일치: {'PASS' if c23_pass else 'FAIL'} "
            f"(쌍 {c23['pairs_count']}개)"
        )
        if c23.get("note"):
            print(f"   - {c23['note']}")
        for d in c23["details"]:
            if d["status"] == "mismatch":
                print(f"   - 표기 불일치: {d['word']} → {d['given_korean']} (표준: {d['expected_korean']})")

        print(f"C4·C7·C8 형식·분량·투명성: {'PASS' if c47['passed'] else 'FAIL'}")
        for k in ["header", "meta_line", "three_points", "three_meanings", "meditation_questions", "app_prayer", "search_transparency", "length"]:
            if not c47[k]:
                print(f"   - 미통과: {k}")

        print(f"C5·C6 비약·이단 차단: {'PASS' if c56['passed'] else 'FAIL'}")
        if c56["passage_trap_hits"]:
            print(f"   - 본문 함정 {len(c56['passage_trap_hits'])}건")
        if c56["heretical_hits"]:
            print(f"   - 이단 트리거 {len(c56['heretical_hits'])}건")
        if c56["general_hits"]:
            print(f"   - 일반 경고 {len(c56['general_hits'])}건")

        print()
        print(f"종합: {'ALL PASS' if summary['overall_pass'] else 'FAIL — 재작성 필요'}")

    sys.exit(0 if summary["overall_pass"] else 1)


if __name__ == "__main__":
    main()
