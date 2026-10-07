#!/usr/bin/env python3
"""
verify_citation_format.py — 코란/탈무드/Vulgata 인용 형식 검증

본 도구는 본문 string을 입력받아 다음을 검사한다:
1. 코란 인용이 [수라]:[절] 또는 코란 X:Y 형식인가?
2. 탈무드 인용이 b./y./m. + 마쎄켓 + 페이지 형식인가?
3. Vulgata 인용에 판본(Clementine/Nova Vulgata/Stuttgart) 명시인가?
4. 한국어 코란 인용에 번역자 명시 또는 "필자 사역"인가?
5. 시편 인용이 MT/LXX 두 번호 병기인가? (Vulgata나 LXX layer에서)
6. 페이지·다프 번호가 비현실적이지 않은가?

Usage:
  python3 verify_citation_format.py <파일경로>
  echo "본문 내용" | python3 verify_citation_format.py -
"""

from __future__ import annotations
import re
import sys


# 탈무드 마쎄켓 표준 명칭 (전체 63 + 흔한 영어 표기)
TALMUD_TRACTATES = {
    "Berakhot", "Peah", "Demai", "Kilayim", "Sheviit", "Terumot",
    "Maaserot", "Maaser Sheni", "Challah", "Orlah", "Bikkurim",
    "Shabbat", "Eruvin", "Pesachim", "Shekalim", "Yoma", "Sukkah",
    "Beitzah", "Rosh Hashanah", "Taanit", "Megillah", "Moed Katan", "Chagigah",
    "Yevamot", "Ketubot", "Nedarim", "Nazir", "Sotah", "Gittin", "Kiddushin",
    "Bava Kamma", "Bava Metzia", "Bava Batra", "Sanhedrin", "Makkot",
    "Shevuot", "Eduyot", "Avodah Zarah", "Avot", "Pirkei Avot", "Horayot",
    "Zevachim", "Menachot", "Chullin", "Bekhorot", "Arakhin", "Temurah",
    "Keritot", "Meilah", "Tamid", "Middot", "Kinnim",
    "Niddah",
    # 그 외 토호롯
    "Kelim", "Oholot", "Negaim", "Parah", "Tohorot", "Mikvaot",
    "Machshirin", "Zavim", "Tevul Yom", "Yadayim", "Uktzin",
}


# 코란 한국어 번역자
QURAN_TRANSLATORS = {
    "김용선", "최영길", "조희선", "공일주", "필자 사역", "필자사역",
    "Sahih International", "Saheeh International", "Yusuf Ali",
    "Pickthall", "Marmaduke Pickthall", "Asad", "Muhammad Asad",
    "Arberry", "Hilali", "Khan",
}


def check_quran(text: str) -> list[str]:
    issues = []

    # 코란 인용 패턴: 수라/코란 NN:NN
    quran_refs = re.findall(r"(?:수라|코란|Surah|Quran|꾸란)\s*[알-힣A-Za-z\-]*\s*(\d+)[:：](\d+(?:[-–]\d+)?)", text)
    for sura, ayah in quran_refs:
        sura_num = int(sura)
        if not (1 <= sura_num <= 114):
            issues.append(f"코란 수라 번호 비현실적: {sura} (1-114 범위 초과)")
        # 절 번호 상한 (각 수라의 절 수)
        sura_max_ayahs = {
            1: 7, 2: 286, 3: 200, 4: 176, 5: 120, 6: 165, 7: 206, 8: 75, 9: 129,
            10: 109, 11: 123, 12: 111, 13: 43, 14: 52, 15: 99, 16: 128, 17: 111,
            18: 110, 19: 98, 20: 135, 37: 182, 112: 4,
        }
        if sura_num in sura_max_ayahs:
            first_ayah = int(re.match(r"(\d+)", ayah).group(1))
            if first_ayah > sura_max_ayahs[sura_num]:
                issues.append(f"코란 수라 {sura_num} 절 번호 비현실적: {ayah} (수라 최대 {sura_max_ayahs[sura_num]})")

    # 코란 한국어 인용 시 번역자 명시 점검
    # "코란"이 등장하는 단락에서 따옴표 본문이 있다면 번역자 명시 권장
    # 간단 휴리스틱: 코란 인용 직후 따옴표가 있는데 번역자 명시 없으면 경고
    quran_blocks = re.findall(r"(코란\s*\d+[:：]\d+[\s\S]{0,400})", text)
    for block in quran_blocks:
        if '"' in block or '"' in block or '"' in block:
            has_translator = any(t in block for t in QURAN_TRANSLATORS)
            if not has_translator:
                issues.append(
                    f"코란 한국어 인용 시 번역자 명시 누락 가능 (필자 사역/김용선/최영길/Sahih International 등): "
                    f"{block[:80].replace(chr(10), ' ')}..."
                )

    return issues


def check_talmud(text: str) -> list[str]:
    issues = []

    # 탈무드 인용 패턴: b./y./m. + 마쎄켓 + 페이지
    # 예: b. Sanhedrin 38a, m. Pirkei Avot 5:3
    talmud_pattern = re.compile(
        r"(b\.|y\.|m\.|t\.)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(\d+[ab]?(?::\d+)?)"
    )
    for match in talmud_pattern.finditer(text):
        prefix, tractate, page = match.group(1), match.group(2), match.group(3)
        if tractate not in TALMUD_TRACTATES:
            # Pirkei Avot, Bava Kamma 등 두 단어 마쎄켓
            issues.append(f"탈무드 마쎄켓 명칭 검증 필요: '{tractate}' (b. y. m. 표준 목록과 대조)")
        # 페이지 번호 상한 검사: b. 마쎄켓 다프 1~500 정도 (실제 마쎄켓별로 다름)
        page_num_match = re.match(r"(\d+)", page)
        if page_num_match:
            page_num = int(page_num_match.group(1))
            if page_num > 200:  # 가장 긴 b. Bava Batra가 ~176
                issues.append(f"탈무드 다프 번호 비현실적: {prefix} {tractate} {page} (>200)")
            # 미쉬나는 m. + chapter:mishnah 형식이 더 일반적
            if prefix == "m." and ":" not in page and not page.endswith(("a", "b")):
                # OK — 단일 장 표기. 절 표기 없음.
                pass

    # b. Berakhot 17a 오기 점검 (라반 요하난 벤 자카이 임종)
    if re.search(r"b\.\s+Berakhot\s+17a", text):
        # 임종 또는 라반 요하난 벤 자카이 컨텍스트에 등장하면 오류
        if "임종" in text or "요하난 벤 자카이" in text or "Yochanan ben Zakkai" in text:
            issues.append("CRITICAL: b. Berakhot 17a는 임종 본문 아님. b. Berakhot 28b가 정확.")

    return issues


def check_vulgata(text: str) -> list[str]:
    issues = []

    # Vulgata 등장 시 판본 명시 권장
    if re.search(r"Vulgata|Vg\.|Vulg\.", text) and not re.search(
        r"Clementine|Nova Vulgata|Stuttgart|Weber-Gryson|Vulgata Clementina|1592|1979", text
    ):
        issues.append(
            "Vulgata 인용 시 판본 명시 누락 (Clementine/Nova Vulgata/Stuttgart 중 하나)"
        )

    # caritas vs cardinal virtue 점검
    # caritas가 "추기경적/cardinal 덕"과 같은 문장 또는 인접 컨텍스트에 묶일 때 오류
    has_caritas = "caritas" in text.lower()
    has_cardinal_term = bool(re.search(r"추기경적\s*덕|cardinal\s*virtue", text, re.IGNORECASE))
    if has_caritas and has_cardinal_term:
        wrong_pattern = re.search(
            r"caritas[^.\n]{0,200}(?:추기경적\s*덕|cardinal\s*virtue)|"
            r"(?:추기경적\s*덕|cardinal\s*virtue)[^.\n]{0,200}caritas",
            text,
            re.IGNORECASE,
        )
        if wrong_pattern:
            # 단, "caritas는 추기경적 덕이 *아니다*"처럼 명백히 부정하는 컨텍스트는 OK
            negation_pattern = re.search(
                r"caritas[^.\n]{0,200}(?:추기경적\s*덕|cardinal\s*virtue)[^.\n]{0,50}(?:아니|아님|not|≠)|"
                r"(?:추기경적\s*덕|cardinal\s*virtue).{0,50}(?:과는?\s*다름|과\s*다름|아니다|아님|not|≠)[^.\n]{0,200}caritas",
                text,
                re.IGNORECASE,
            )
            if not negation_pattern:
                issues.append(
                    "CRITICAL: caritas는 *신학적 덕*(theological virtue)이지 *추기경적 덕*(cardinal virtue)이 아님. "
                    "Cardinal virtue는 prudentia·iustitia·fortitudo·temperantia."
                )

    return issues


def check_psalm_numbering(text: str) -> list[str]:
    issues = []

    # 시편 인용 패턴: 시 NN:NN 또는 시편 NN:NN 또는 Ps NN:NN
    # Vulgata/LXX 컨텍스트에서 시편 인용 시 두 번호 병기 권장
    if re.search(r"Vulgata|LXX|70인역|Septuagint", text):
        psalm_in_vulg_lxx = re.findall(
            r"(?:Ps\.?\s|시편\s|시\s)(\d+)[:：](\d+)", text
        )
        for ch, vs in psalm_in_vulg_lxx:
            ch_num = int(ch)
            # 다른 번호 (MT or LXX/Vg) 병기 여부 확인 — 단순 휴리스틱
            # 두 번호 차이 1 사이가 같은 단락에 있으면 OK
            other_num = ch_num - 1 if ch_num > 1 else ch_num + 1
            # 단순화: 시편 인용 시 "MT" 또는 "Vg" 또는 "LXX" 라벨이 함께 있는지
            window_pattern = (
                r"(시편?\s*\d+[:：]\d+\s*\([^)]*\b(MT|LXX|Vg|Vulgata|히)\b[^)]*\))"
                r"|(\([^)]*(MT|LXX|Vg)\s*\d+[:：]\d+[^)]*\))"
            )
            if not re.search(window_pattern, text):
                if ch_num <= 150:
                    issues.append(
                        f"시편 {ch}:{vs} 인용 — LXX/Vulgata 컨텍스트에서 MT 번호 병기 권장 "
                        f"(예: '시 {ch_num}편 (Vg {ch_num-1}편)')"
                    )

    return issues


def check_text(text: str) -> dict:
    issues = {
        "quran": check_quran(text),
        "talmud": check_talmud(text),
        "vulgata": check_vulgata(text),
        "psalm_numbering": check_psalm_numbering(text),
    }
    total = sum(len(v) for v in issues.values())
    return {"issues": issues, "total": total}


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    if sys.argv[1] == "-":
        text = sys.stdin.read()
    else:
        with open(sys.argv[1], encoding="utf-8") as f:
            text = f.read()

    result = check_text(text)
    print()
    print(f"=== 인용 형식 검증 결과 (총 {result['total']}개 이슈) ===")
    print()
    for category, issues in result["issues"].items():
        print(f"[{category.upper()}]")
        if not issues:
            print("  ✓ 통과 (이슈 없음)")
        else:
            for i, issue in enumerate(issues, 1):
                print(f"  {i}. {issue}")
        print()
    sys.exit(0 if result["total"] == 0 else 1)


def _self_test():
    """검증 도구 자체 테스트."""
    failures = []

    # 1. 정상 케이스
    ok_text = """
    출처: 코란 19:30 (수라 마르얌). 김용선역 "그는 말하기를 '나는 알라의 종이다'".
    탈무드: b. Sanhedrin 89b. 미쉬나: m. Pirkei Avot 5:3.
    Vulgata Clementina, Iohannem 1:1: "In principio erat Verbum".
    시 23편 (Vg 22편 / Hebr. 23편): "Dominus pascit me".
    """
    result = check_text(ok_text)
    if result["total"] > 0:
        failures.append(
            f"  FAIL: 정상 케이스가 통과해야 하나 {result['total']}개 이슈 발견: {result['issues']}"
        )

    # 2. 코란 수라 번호 초과
    bad_quran = "출처: 코란 200:1 (존재하지 않는 수라)"
    result = check_text(bad_quran)
    if not any("코란 수라 번호 비현실적" in i for i in result["issues"]["quran"]):
        failures.append("  FAIL: 코란 수라 200 비현실 미감지")

    # 3. 탈무드 잘못된 본문 (b. Berakhot 17a 임종)
    bad_talmud = "라반 요하난 벤 자카이의 임종 기도 (b. Berakhot 17a)"
    result = check_text(bad_talmud)
    if not any("CRITICAL" in i for i in result["issues"]["talmud"]):
        failures.append("  FAIL: b. Berakhot 17a 임종 오기 미감지")

    # 4. Vulgata 판본 미명시
    bad_vulgata = "Vulgata에서는 'In principio erat Verbum'으로 옮긴다."
    result = check_text(bad_vulgata)
    if not any("판본 명시 누락" in i for i in result["issues"]["vulgata"]):
        failures.append("  FAIL: Vulgata 판본 미명시 미감지")

    # 5. caritas vs cardinal virtue 혼동
    bad_caritas = "caritas는 4가지 추기경적 덕 중 하나이다."
    result = check_text(bad_caritas)
    if not any("CRITICAL" in i for i in result["issues"]["vulgata"]):
        failures.append("  FAIL: caritas/cardinal virtue 혼동 미감지")

    if failures:
        print("자체 테스트 실패:")
        for f in failures:
            print(f)
        return False
    print("자체 테스트 통과 (5건)")
    return True


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        sys.exit(0 if _self_test() else 1)
    main()
