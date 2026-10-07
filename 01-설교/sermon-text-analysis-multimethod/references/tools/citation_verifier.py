#!/usr/bin/env python3
"""
sermon-text-analysis-multimethod citation verifier
===================================================

목적: 본 스킬이 응답을 생성한 후, 응답 안의 학자·작품·연도·출판사·헬라어/히브리어
단어·본문 인용·숫자 상징 주장을 카탈로그와 대조하여 할루시네이션을 차단한다.

LLM 단독 답변에서 발생할 수 있는 환각은 본 스크립트로 검증한다:
  1. verify_author(name, work?, year?, publisher?)
  2. verify_lexicon(word, transliteration?, claimed_meaning?)
  3. verify_passage(book_kor, chapter, verse_range?)
  4. detect_false_etymology(text)
  5. self_check_response(response_text)  -- 전체 응답을 받아 자동 점검

사용:
  $ python3 citation_verifier.py self-check < response.md
  $ python3 citation_verifier.py author "Joel Marcus" "Mark 1-8" 2000
  $ python3 citation_verifier.py lexicon "ἀγάπη"
  $ python3 citation_verifier.py passage "롬" 12 "1-2"

종료 코드:
  0: 모든 검증 통과
  1: 경고 있음 (응답 보정 권장)
  2: 치명적 오류 (응답 재생성 권장)
"""

from __future__ import annotations
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any, Optional


def _nfc(s: str) -> str:
    """Canonical composition — 헬라어 결합 액센트 정규화."""
    return unicodedata.normalize("NFC", s)

DATA_DIR = Path(__file__).parent.parent / "data"


def _load(name: str) -> dict[str, Any]:
    path = DATA_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"카탈로그 데이터 누락: {path}")
    with open(path, encoding="utf-8") as fp:
        return json.load(fp)


def _safe_load(name: str) -> dict[str, Any]:
    try:
        return _load(name)
    except FileNotFoundError as e:
        print(f"[FATAL] {e}", file=sys.stderr)
        sys.exit(2)


AUTHORS = _safe_load("verified_authors.json")
LEXICON = _safe_load("verified_lexicon.json")
BOOKS = _safe_load("bible_books.json")
ETYMOLOGY = _safe_load("false_etymology_signals.json")


# ---------------------------------------------------------------------------
# 1) Author verification
# ---------------------------------------------------------------------------

def verify_author(
    name: str,
    work: Optional[str] = None,
    year: Optional[int | str] = None,
    publisher: Optional[str] = None,
) -> dict[str, Any]:
    """학자 인용 검증.

    name: 학자명 (성, 또는 'Marcus, Joel' 형식)
    work: 작품명 (선택)
    year: 출판 연도 (선택)
    publisher: 출판사 (선택)
    """
    result = {
        "name": name,
        "status": "UNKNOWN",
        "found_entry": None,
        "warnings": [],
        "details": {},
    }

    verified = AUTHORS.get("verified_authors", {})

    # 키 매칭: 정확 일치 또는 성 부분 일치
    candidate_key = None
    for key in verified:
        if key.lower() == name.lower():
            candidate_key = key
            break
        # 성 추출 (콤마 앞 또는 첫 단어)
        if "," in key:
            last_name = key.split(",")[0].strip().lower()
        else:
            last_name = key.split()[0].lower()
        if last_name in name.lower() or name.lower() in last_name:
            candidate_key = key
            break

    if candidate_key is None:
        result["status"] = "NOT_FOUND"
        result["warnings"].append(
            f"학자 '{name}' 카탈로그에 없음. 인용 회피 또는 직접 확인 권장."
        )
        return result

    entry = verified[candidate_key]
    result["found_entry"] = candidate_key
    result["details"] = entry
    result["status"] = "VERIFIED_AUTHOR"

    # 경고 보존
    if "WARNING" in entry:
        result["warnings"].append(f"⚠ {entry['WARNING']}")

    # 작품 검증
    if work:
        works = entry.get("works", [])
        work_match = None
        for w in works:
            if work.lower() in w.lower() or w.lower().startswith(work.lower()[:15]):
                work_match = w
                break
        if work_match is None:
            result["status"] = "AUTHOR_OK_WORK_UNVERIFIED"
            result["warnings"].append(
                f"작품 '{work}'은 {candidate_key} 검증 작품 목록에 없음. "
                f"검증된 작품: {works[:3]}..."
            )
        else:
            result["details"]["matched_work"] = work_match

    # 연도 검증 (작품 문자열 안에 연도가 들어있는지)
    if year and work:
        year_str = str(year)
        works_with_year = [w for w in entry.get("works", []) if year_str in w]
        if not works_with_year:
            result["warnings"].append(
                f"연도 {year}이 {candidate_key} {work} 카탈로그 정보와 일치하지 않음. 직접 확인."
            )

    # 출판사 검증
    if publisher and work:
        works_str = " ".join(entry.get("works", []))
        if publisher.lower() not in works_str.lower():
            result["warnings"].append(
                f"출판사 '{publisher}'이 카탈로그 {candidate_key} 정보와 일치하지 않음."
            )

    return result


# ---------------------------------------------------------------------------
# 2) Lexicon verification
# ---------------------------------------------------------------------------

def verify_lexicon(
    word: str,
    transliteration: Optional[str] = None,
    claimed_meaning: Optional[str] = None,
) -> dict[str, Any]:
    """원어 단어 검증.

    word: 헬라어/히브리어 단어 (또는 음역)
    transliteration: 음역 (선택)
    claimed_meaning: 사용자가 주장하려는 의미 (선택)
    """
    result = {
        "word": word,
        "status": "UNKNOWN",
        "found_entry": None,
        "warnings": [],
        "details": {},
    }

    word_nfc = _nfc(word)

    # 헬라어·히브리어 모두 검색
    for category in ("greek_NT", "hebrew_OT"):
        catalog = LEXICON.get(category, {})
        for key, entry in catalog.items():
            key_nfc = _nfc(key)
            if (
                key_nfc == word_nfc
                or entry.get("transliteration", "").lower() == word.lower()
                or entry.get("korean_phonetic", "") == word
            ):
                result["found_entry"] = key
                result["details"] = entry
                result["status"] = f"VERIFIED_{category.upper()}"
                if "WARNING" in entry:
                    result["warnings"].append(f"⚠ {entry['WARNING']}")
                if claimed_meaning:
                    basic = entry.get("basic_meaning", "").lower()
                    bdag = entry.get("BDAG_summary", entry.get("BDB_HALOT_summary", "")).lower()
                    if not (
                        any(w in basic for w in claimed_meaning.lower().split())
                        or any(w in bdag for w in claimed_meaning.lower().split())
                    ):
                        result["warnings"].append(
                            f"주장 의미 '{claimed_meaning}'이 카탈로그 기본 의미 '{entry.get('basic_meaning')}'와 결이 다를 수 있음. BDAG/HALOT 직접 확인 권장."
                        )
                return result

    result["status"] = "NOT_FOUND"
    result["warnings"].append(
        f"단어 '{word}' 카탈로그에 없음. BDAG/BDB/HALOT 직접 인용 또는 '표준 사전 확인 권장' 명시."
    )
    return result


# ---------------------------------------------------------------------------
# 3) Passage verification
# ---------------------------------------------------------------------------

def verify_passage(
    book_kor: str,
    chapter: int | str,
    verse_range: Optional[str] = None,
) -> dict[str, Any]:
    """본문 인용 검증.

    book_kor: 한국어 책 약자 또는 전체명 (예: '롬', '로마서')
    chapter: 장 번호
    verse_range: 절 또는 절 범위 (예: '1-2', '15')
    """
    result = {
        "passage": f"{book_kor} {chapter}{':' + verse_range if verse_range else ''}",
        "status": "UNKNOWN",
        "found_book": None,
        "warnings": [],
    }

    # 책 찾기 — 우선순위: (1) abbrev_kor 정확 일치, (2) full_name 정확 일치,
    # (3) abbrev_eng 정확 일치, (4) full_name startswith 일치
    book_entry = None
    book_canonical = None

    def _scan(predicate):
        for testament in ("OT_39", "NT_27"):
            canon = BOOKS.get(testament, {})
            for full_name, entry in canon.items():
                if predicate(full_name, entry):
                    return full_name, entry
        return None, None

    # priority 1: abbrev_kor 정확 일치 (예: '요' → 요한복음)
    book_canonical, book_entry = _scan(
        lambda fn, e: e.get("abbrev_kor") == book_kor
    )
    # priority 2: full_name 정확 일치
    if book_entry is None:
        book_canonical, book_entry = _scan(lambda fn, e: fn == book_kor)
    # priority 3: abbrev_eng 정확 일치
    if book_entry is None:
        book_canonical, book_entry = _scan(
            lambda fn, e: e.get("abbrev_eng") == book_kor
        )
    # priority 4: full_name startswith (마지막 수단)
    if book_entry is None:
        book_canonical, book_entry = _scan(lambda fn, e: fn.startswith(book_kor))

    if book_entry is None:
        # 알려진 오인 책명 확인
        misnomers = BOOKS.get("_known_misnomers", {})
        if book_kor in misnomers:
            result["status"] = "INVALID_BOOK"
            result["warnings"].append(
                f"'{book_kor}' = {misnomers[book_kor]}"
            )
        else:
            result["status"] = "BOOK_NOT_FOUND"
            result["warnings"].append(
                f"책 '{book_kor}' 정경 66권에 없음. 책명 오타 가능성."
            )
        return result

    result["found_book"] = book_canonical
    result["details"] = book_entry

    # 장 검증
    try:
        ch = int(chapter)
    except (TypeError, ValueError):
        result["status"] = "INVALID_CHAPTER"
        result["warnings"].append(f"장 번호 '{chapter}' 정수 아님.")
        return result

    max_ch = book_entry.get("chapters", 0)
    if ch < 1 or ch > max_ch:
        result["status"] = "CHAPTER_OUT_OF_RANGE"
        result["warnings"].append(
            f"{book_canonical}({book_kor})는 총 {max_ch}장. {ch}장은 범위 초과."
        )
        return result

    result["status"] = "VERIFIED_PASSAGE"

    if verse_range:
        # 형식 검증만 (정확한 절 수 검증은 본 카탈로그 범위 밖)
        if not re.match(r"^\d+(-\d+)?(,\s*\d+(-\d+)?)*$", str(verse_range)):
            result["warnings"].append(
                f"절 범위 형식 '{verse_range}' 표준 형식 아님 (예: '1-10' 또는 '1, 5, 7')."
            )

    return result


# ---------------------------------------------------------------------------
# 4) False etymology detection
# ---------------------------------------------------------------------------

def detect_false_etymology(text: str) -> dict[str, Any]:
    """응답 텍스트에서 가짜 어원·과장 단어 의미 패턴을 식별."""
    result = {
        "input_length": len(text),
        "matches": [],
        "warnings": [],
    }

    # 블록 목록 검사 — 거짓 양성 방지:
    # 응답이 *교정 방향*을 진술하면 매칭 제외 (예: "BDAG 표준", "직접 확인 권장", "카탈로그",
    # "곡해", "회피", "본문에 없음", "단정 회피", "WARNING", "학계 표준")
    correction_safe_signals = [
        "BDAG 표준", "HALOT", "직접 확인", "곡해", "WARNING", "단정 회피",
        "학계 표준", "카탈로그", "본문에 없", "회피", "교정",
        "Exegetical Fallacies", "Illegitimate Totality Transfer",
    ]

    def _looks_like_correction(window: str) -> bool:
        return any(s in window for s in correction_safe_signals)

    def _check_block(claims: dict, hebrew: bool = False) -> None:
        for fallacy_id, info in claims.items():
            false_claim = info.get("false_claim", "")
            keywords = re.findall(r"[가-힣]{2,}|[a-zA-Zα-ωΑ-Ω]{4,}", false_claim)
            if len(keywords) < 3:
                continue
            hits = sum(1 for kw in keywords if kw in text)
            # 거의 모든 키워드가 등장해야 진정한 매칭으로 인정 (이전 1/3 → 2/3 상향)
            threshold = max(3, (len(keywords) * 2) // 3)
            if hits < threshold:
                continue
            # 응답 본문 안에 교정 신호가 다수면 false positive 가능성 — 제외
            if _looks_like_correction(text):
                continue
            result["matches"].append({
                "fallacy_id": fallacy_id,
                "hits": hits,
                "keywords_total": len(keywords),
                "category": info.get("category"),
                "correction": info.get("correction"),
            })

    _check_block(ETYMOLOGY.get("blocked_etymology_claims", {}))
    _check_block(ETYMOLOGY.get("blocked_hebrew_claims", {}), hebrew=True)

    # 숫자 상징 신호 검사 — 교정 신호 다수면 거짓 양성으로 간주 제외
    if not _looks_like_correction(text):
        number_warnings = ETYMOLOGY.get("number_symbolism_warnings", {}).get(
            "blocked_numerologies", []
        )
        for n in number_warnings:
            keywords = [k for k in re.split(r"[ =·\-]+", n) if len(k) >= 2]
            if len(keywords) < 3:
                continue
            hits = sum(1 for kw in keywords if kw in text)
            # 1/2 → 2/3 임계 상향
            if hits >= max(3, (len(keywords) * 2) // 3):
                result["warnings"].append(
                    f"의심 숫자 상징 패턴 감지: '{n}' — 본문이 그 숫자에 신학적 의미를 부여하지 않으면 의미를 만들지 말 것."
                )

    return result


# ---------------------------------------------------------------------------
# 5) Self-check on full response
# ---------------------------------------------------------------------------

PASSAGE_REGEX = re.compile(
    r"(?P<book>[가-힣]{1,5})\s*(?P<chapter>\d{1,3})\s*(?:[:\.](?P<verses>\d{1,3}(?:-\d{1,3})?)|장|편)"
)


def _is_known_book(name: str) -> bool:
    """name이 정경 66권의 책명 또는 약자에 정확히 매칭되는지."""
    for testament in ("OT_39", "NT_27"):
        canon = BOOKS.get(testament, {})
        for full_name, entry in canon.items():
            if (
                name == full_name
                or name == entry.get("abbrev_kor")
                or name == entry.get("abbrev_eng")
            ):
                return True
    return False

# 헬라어 (basic + extended + combining diacritics) + 히브리어 (consonants + vowel points)
GREEK_HEBREW_REGEX = re.compile(
    r"["
    r"Ͱ-Ͽ"        # Greek and Coptic basic
    r"ἀ-῿"        # Greek Extended
    r"̀-ͯ"        # Combining diacritical marks
    r"֐-׿"        # Hebrew (with vowel points)
    r"יִ-ﭏ"        # Hebrew presentation forms
    r"]{2,}"
)


def self_check_response(text: str) -> dict[str, Any]:
    """응답 텍스트를 받아 모든 검증 수행."""
    summary = {
        "total_warnings": 0,
        "passage_checks": [],
        "lexicon_checks": [],
        "etymology_check": {},
        "verdict": "OK",
    }

    # 1) 본문 인용 검증
    # 책명이 known book에 정확 매칭되는 경우만 검증 (오탐 회피)
    # 책명을 길이 내림차순으로 정렬하여 긴 책명 우선 매칭
    seen_passages = set()
    known_kor_full = set()
    known_kor_abbr = set()
    for testament in ("OT_39", "NT_27"):
        for full_name, entry in BOOKS.get(testament, {}).items():
            known_kor_full.add(full_name)
            ak = entry.get("abbrev_kor")
            if ak:
                known_kor_abbr.add(ak)

    # 긴 풀네임을 먼저 시도하는 정규식 매칭 — 텍스트에서 긴 책명+장:절 패턴 우선 추출
    for m in PASSAGE_REGEX.finditer(text):
        book = m.group("book")
        chapter = m.group("chapter")
        # 0장은 거짓 양성 — 건너뜀
        if chapter == "0":
            continue
        # 위경/외경 prefix 인식: 책명 직전에 '4', '5', '6', '7' 등 정경 prefix 범위 밖
        # (정경은 1·2·3 까지만) 숫자가 있으면 위경으로 간주, 검증 건너뜀.
        # 예: "4 에스라 13" → "4" prefix는 위경 *4 Ezra/2 Esdras* 표기.
        start = m.start("book")
        if start >= 2:
            preceding = text[max(0, start - 4):start]
            apoc_match = re.search(r"([4-9])\s+$", preceding)
            if apoc_match:
                continue
        # 알려진 책이 아니면 거짓 양성 — 건너뜀
        # 단, 풀네임 (예: '고린도전서')이 잘려 '린도전서'로 잡힌 경우 복구 시도
        if not _is_known_book(book):
            # 텍스트 위치에서 추가 한 글자(앞)를 확인하여 풀네임 복구
            if start > 0:
                extended = text[start - 1] + book
                if _is_known_book(extended):
                    book = extended
                else:
                    continue
            else:
                continue
        sig = (book, chapter)
        if sig in seen_passages:
            continue
        seen_passages.add(sig)
        r = verify_passage(book, chapter, m.group("verses"))
        summary["passage_checks"].append(r)
        if r["warnings"]:
            summary["total_warnings"] += len(r["warnings"])

    # 2) 헬라어·히브리어 단어 검증
    # 카탈로그 외 단어는 informational (BDAG/HALOT 직접 확인 권장 자동 안내).
    # WARNING 가진 verified 단어만 응답 보정 요청.
    summary["lexicon_not_in_catalog"] = []
    seen_words = set()
    for m in GREEK_HEBREW_REGEX.finditer(text):
        word = m.group(0)
        if word in seen_words:
            continue
        seen_words.add(word)
        r = verify_lexicon(word)
        if r["status"] == "NOT_FOUND":
            summary["lexicon_not_in_catalog"].append(word)
            continue
        summary["lexicon_checks"].append(r)
        # 검증된 단어 중 WARNING 가진 항목만 응답 보정 필요
        if r["warnings"]:
            summary["total_warnings"] += len(r["warnings"])

    # 3) 가짜 어원·숫자 상징 검증
    etym = detect_false_etymology(text)
    summary["etymology_check"] = etym
    summary["total_warnings"] += len(etym.get("matches", [])) + len(etym.get("warnings", []))

    # 판정
    if summary["total_warnings"] == 0:
        summary["verdict"] = "OK"
    elif any(
        c.get("status") in ("BOOK_NOT_FOUND", "INVALID_BOOK", "CHAPTER_OUT_OF_RANGE")
        for c in summary["passage_checks"]
    ):
        summary["verdict"] = "CRITICAL_ERRORS"
    elif summary["total_warnings"] >= 5:
        summary["verdict"] = "MANY_WARNINGS_REVIEW_REQUIRED"
    else:
        summary["verdict"] = "MINOR_WARNINGS"

    return summary


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _print(obj: Any) -> None:
    print(json.dumps(obj, ensure_ascii=False, indent=2))


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2

    cmd = argv[1]

    if cmd == "author":
        if len(argv) < 3:
            print("Usage: author NAME [WORK] [YEAR] [PUBLISHER]", file=sys.stderr)
            return 2
        r = verify_author(
            argv[2],
            argv[3] if len(argv) > 3 else None,
            argv[4] if len(argv) > 4 else None,
            argv[5] if len(argv) > 5 else None,
        )
        _print(r)
        return 0 if not r["warnings"] else 1

    if cmd == "lexicon":
        if len(argv) < 3:
            print("Usage: lexicon WORD [CLAIMED_MEANING]", file=sys.stderr)
            return 2
        r = verify_lexicon(argv[2], None, argv[3] if len(argv) > 3 else None)
        _print(r)
        return 0 if not r["warnings"] else 1

    if cmd == "passage":
        if len(argv) < 4:
            print("Usage: passage BOOK CHAPTER [VERSES]", file=sys.stderr)
            return 2
        r = verify_passage(argv[2], argv[3], argv[4] if len(argv) > 4 else None)
        _print(r)
        return 0 if not r["warnings"] else 1

    if cmd == "etymology":
        text = sys.stdin.read() if argv[2] == "-" else argv[2]
        r = detect_false_etymology(text)
        _print(r)
        return 0 if not (r.get("matches") or r.get("warnings")) else 1

    if cmd == "self-check":
        text = sys.stdin.read()
        r = self_check_response(text)
        _print({
            "verdict": r["verdict"],
            "total_warnings": r["total_warnings"],
            "passages_checked_ok": sum(1 for p in r["passage_checks"] if p["status"] == "VERIFIED_PASSAGE"),
            "passages_with_warnings": [p for p in r["passage_checks"] if p["warnings"]],
            "lexicon_verified_with_WARNING": [l for l in r["lexicon_checks"] if l["warnings"]],
            "lexicon_not_in_catalog_count": len(r.get("lexicon_not_in_catalog", [])),
            "lexicon_not_in_catalog_sample": r.get("lexicon_not_in_catalog", [])[:8],
            "etymology_matches": r["etymology_check"].get("matches", []),
            "etymology_number_warnings": r["etymology_check"].get("warnings", []),
        })
        if r["verdict"] == "OK":
            return 0
        if r["verdict"] in ("CRITICAL_ERRORS",):
            return 2
        return 1

    print(f"Unknown command: {cmd}", file=sys.stderr)
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
