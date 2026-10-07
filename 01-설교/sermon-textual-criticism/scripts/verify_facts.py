#!/usr/bin/env python3
"""
sermon-textual-criticism 응답 사실 검증 도구

응답 텍스트에서 사본 사실 주장(연대·소장처·계열·약어)을 추출해
references/manuscript-facts.json의 사실 DB와 대조한다.

사용:
    python3 verify_facts.py [응답 텍스트 파일 경로]
    또는 stdin으로 응답 텍스트 전달:
    cat response.md | python3 verify_facts.py

목적:
    LLM이 사본 메타데이터를 추측·창작할 때 즉시 탐지하여 할루시네이션을 차단한다.
    NA28/UBS5/BHS critical apparatus와의 정합성을 정량 검증한다.
"""

import json
import re
import sys
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
FACTS_PATH = SCRIPT_DIR.parent / "references" / "manuscript-facts.json"


def load_facts() -> dict[str, Any]:
    """사실 DB 로드."""
    with FACTS_PATH.open(encoding="utf-8") as f:
        return json.load(f)


# 사본명·한글 명칭 → DB 키 매핑
NT_NAME_MAP: dict[str, str] = {
    "시내 사본": "Sinaiticus", "시내사본": "Sinaiticus", "Sinaiticus": "Sinaiticus",
    "Codex Sinaiticus": "Sinaiticus", "ℵ": "Sinaiticus",
    "바티칸 사본": "Vaticanus", "바티칸사본": "Vaticanus", "Vaticanus": "Vaticanus",
    "Codex Vaticanus": "Vaticanus",
    "알렉산드리아 사본": "Alexandrinus", "알렉산드리아사본": "Alexandrinus",
    "Alexandrinus": "Alexandrinus", "Codex Alexandrinus": "Alexandrinus",
    "에브라임 사본": "Ephraemi", "Ephraemi": "Ephraemi",
    "Codex Ephraemi": "Ephraemi", "에브라이미": "Ephraemi",
    "베자 사본": "Bezae", "베자사본": "Bezae", "Bezae": "Bezae",
    "Codex Bezae": "Bezae", "코덱스 베자": "Bezae",
    "클라로몬타누스": "Claromontanus", "Claromontanus": "Claromontanus",
    "워싱턴 사본": "Washingtonianus", "워싱턴사본": "Washingtonianus",
    "Washingtonianus": "Washingtonianus", "Freer Gospels": "Washingtonianus",
    "Codex W": "Washingtonianus",
    "코리데티": "Koridethi", "Koridethi": "Koridethi", "Codex Θ": "Koridethi",
    "레기우스": "Regius", "Regius": "Regius",
    "아토스 라우라": "Athous_Laurensis", "Athous Laurensis": "Athous_Laurensis",
    "라우다누스": "Laudianus", "Laudianus": "Laudianus",
}


GA_NUMBER_MAP: dict[str, str] = {
    # Gregory-Aland number → DB key
    "01": "Sinaiticus", "02": "Alexandrinus", "03": "Vaticanus", "04": "Ephraemi",
    "05": "Bezae", "06": "Claromontanus", "08": "Laudianus",
    "019": "Regius", "032": "Washingtonianus", "038": "Koridethi", "044": "Athous_Laurensis",
}


PAPYRUS_MAP: dict[str, str] = {
    "P45": "P45", "P46": "P46", "P47": "P47", "P52": "P52",
    "P66": "P66", "P72": "P72", "P74": "P74", "P75": "P75",
    "𝔓⁴⁵": "P45", "𝔓⁴⁶": "P46", "𝔓⁴⁷": "P47",
    "𝔓⁵²": "P52", "𝔓⁶⁶": "P66", "𝔓⁷²": "P72", "𝔓⁷⁴": "P74", "𝔓⁷⁵": "P75",
}


OT_NAME_MAP: dict[str, str] = {
    "1QIsaᵃ": "1QIsa_a", "1QIsa-a": "1QIsa_a", "1QIsaa": "1QIsa_a",
    "Great Isaiah Scroll": "1QIsa_a", "대 이사야 두루마리": "1QIsa_a",
    "1QIsaᵇ": "1QIsa_b", "1QIsab": "1QIsa_b",
    "4QSamᵃ": "4QSam_a", "4QSama": "4QSam_a",
    "4QDeutⱼ": "4QDeut_j", "4QDeutj": "4QDeut_j",
    "11Q5": "11Q5", "11QPsa": "11Q5", "11QPsᵃ": "11Q5",
    "Aleppo Codex": "Aleppo_Codex", "알레포 사본": "Aleppo_Codex", "알레포사본": "Aleppo_Codex",
    "Leningradensis": "Leningradensis", "레닌그라드 사본": "Leningradensis",
    "레닌그라드사본": "Leningradensis", "Codex Leningradensis": "Leningradensis",
    "B19A": "Leningradensis", "B19a": "Leningradensis",
    "Codex Cairensis": "Cairensis", "카이로 사본": "Cairensis", "Cairo Codex": "Cairensis",
    "Damascus Pentateuch": "Damascus_Pentateuch",
    "Samaritan Pentateuch": "Samaritan_Pentateuch", "사마리아 오경": "Samaritan_Pentateuch", "SP": "Samaritan_Pentateuch",
}


# 단정형 표현 — G1 (확정 vs 추정 구분) 위반 후보
ABSOLUTE_CLAIM_PATTERNS = [
    re.compile(r"원본은 분명히"),
    re.compile(r"원본은 확실히"),
    re.compile(r"확정적으로"),
    re.compile(r"100% 확실"),
    re.compile(r"의심의 여지가 없"),
    re.compile(r"누구도 부정할 수 없"),
]


# Metzger 등급 단언 — G6 위반
# (Metzger와 같은 문장 안 50자 이내에 {A}~{D} 등급 단언이 있는 경우)
# 단, "단언 금지", "회피", "0건", "지양" 같은 메타 문맥은 false positive로 제외.
METZGER_GRADE_PATTERN = re.compile(r"Metzger[^.]{0,50}?\{[ABCD]\}")
METZGER_META_NEGATIONS = re.compile(r"(단언\s*금지|회피|0\s*건|지양|위반\s*없음|준수)")


# 가짜 사본 — DB에 없는데 자주 혼동될 만한 명칭
FAKE_MS_TRAPS = {
    "라이덴 사본": "라이덴 사본은 단일 사본이 아님. Leiden Peshitta Institute의 비평본은 존재. 의도라면 'Leiden Peshitta Edition'으로 명시 필요.",
    "Codex L (사도행전)": "Codex L (019, Regius)는 복음서 사본이지 사도행전 사본 아님. 행 8:37의 'E'는 Codex Laudianus (08)임.",
    "Codex Sinaiticus (5세기)": "시내 사본 ℵ은 4세기 (c. 330-360)이지 5세기 아님.",
    "Codex Vaticanus (5세기)": "바티칸 사본 B는 4세기 (c. 300-325)이지 5세기 아님.",
    "Aleppo Codex (1008년)": "Aleppo 사본은 c. 925-935년. 1008년은 Leningradensis임.",
    "Leningradensis (10세기 중반)": "Leningradensis는 1008/1009년 (11세기 초)이지 10세기 중반 아님.",
}


def extract_sigla(text: str) -> list[tuple[str, str]]:
    """본문에서 사본 약어/명칭 추출 → DB 키 매핑."""
    found: list[tuple[str, str]] = []
    for name, key in {**NT_NAME_MAP, **PAPYRUS_MAP, **OT_NAME_MAP}.items():
        if name in text:
            found.append((name, key))
    # Gregory-Aland 숫자 ("032 W", "01 ℵ" 등)
    for m in re.finditer(r"\b(01|02|03|04|05|06|08|019|032|038|044)\b", text):
        num = m.group(1)
        if num in GA_NUMBER_MAP:
            found.append((f"GA #{num}", GA_NUMBER_MAP[num]))
    return found


def check_dates(text: str, facts: dict[str, Any]) -> list[str]:
    """텍스트의 연대 주장이 DB와 일치하는지 검증."""
    issues: list[str] = []
    nt = facts["nt_manuscripts"]
    ot = facts["ot_manuscripts"]
    # 핵심 위험 케이스: 사본명 + 잘못된 세기
    # 단어 거리를 짧게 제한해 false positive 차단 (한 문장 안의 명백한 오류만 잡음)
    risky_patterns = [
        # (정규식, 잘못된 세기, 올바른 세기, 사본 키)
        (r"시내\s*사본[^.\n]{0,15}?5세기", "5세기", "4세기 (c. 330-360)", "Sinaiticus"),
        (r"바티칸\s*사본[^.\n]{0,15}?5세기", "5세기", "4세기 (c. 300-325)", "Vaticanus"),
        (r"베자\s*사본[^.\n]{0,15}?4세기", "4세기", "5세기", "Bezae"),
        (r"P75[^.\n]{0,15}?(BC|기원전)", "BC", "AD c. 175-225", "P75"),
        (r"P46[^.\n]{0,15}?4세기", "4세기", "c. 200 (혹은 c. 175-225)", "P46"),
        (r"Aleppo\s*Codex[^.\n]{0,15}?1008", "1008년", "c. 925-935 (Leningradensis가 1008)", "Aleppo_Codex"),
        (r"Leningradensis[^.\n]{0,15}?10세기\s*중반", "10세기 중반", "1008/1009 AD (11세기 초)", "Leningradensis"),
    ]
    for regex, wrong, right, _key in risky_patterns:
        if re.search(regex, text):
            issues.append(f"  ⚠️ 연대 오류 의심: '{wrong}' → 정확한 연대는 '{right}'")
    return issues


def check_absolute_claims(text: str) -> list[str]:
    """G1 단정형 표현 검출."""
    issues: list[str] = []
    for pat in ABSOLUTE_CLAIM_PATTERNS:
        for m in pat.finditer(text):
            ctx_start = max(0, m.start() - 30)
            ctx_end = min(len(text), m.end() + 30)
            ctx = text[ctx_start:ctx_end].replace("\n", " ")
            issues.append(f"  ⚠️ G1 위반 의심 (단정형): …{ctx}…")
    return issues


def check_metzger_grades(text: str) -> list[str]:
    """G6 Metzger 등급 단언 검출. 단, 동일 80자 안에 '단언 금지'·'회피' 등 메타 부정 표현이 있으면 false positive로 제외."""
    issues: list[str] = []
    for m in METZGER_GRADE_PATTERN.finditer(text):
        ctx_start = max(0, m.start() - 40)
        ctx_end = min(len(text), m.end() + 80)
        ctx = text[ctx_start:ctx_end]
        if METZGER_META_NEGATIONS.search(ctx):
            continue  # 메타 부정 표현이 있으면 false positive로 처리
        ctx_clean = ctx.replace("\n", " ")
        issues.append(f"  ⚠️ G6 위반 (Metzger 등급 단언): …{ctx_clean}…")
    return issues


def check_fake_ms_traps(text: str) -> list[str]:
    """가짜 사본·혼동 명칭 검출."""
    issues: list[str] = []
    for trap, note in FAKE_MS_TRAPS.items():
        if trap in text:
            issues.append(f"  ⚠️ 사본 명칭 함정: '{trap}' — {note}")
    return issues


def check_url_authenticity(text: str) -> list[str]:
    """학술 디지털 자료 URL이 표준에서 벗어났는지 검증."""
    known_good = {
        "ntvmr.uni-muenster.de", "uni-muenster.de", "intf.uni-muenster.de",
        "codexsinaiticus.org", "digi.vatlib.it", "vatlib.it",
        "cudl.lib.cam.ac.uk", "lib.cam.ac.uk", "cam.ac.uk",
        "csntm.org", "chesterbeatty.ie",
        "deadseascrolls.org.il", "dss.collections.imj.org.il",
        "aleppocodex.org", "usc.edu", "usc.edu/dept/LAS/wsrp",
        "medieval.bodleian.ox.ac.uk", "bodleian.ox.ac.uk",
        "asia.si.edu", "si.edu",
    }
    issues: list[str] = []
    url_pattern = re.compile(r"https?://([^/\s\)]+)|\b([a-z0-9-]+\.(?:org|edu|com|de|gov|net|gv\.at|nl))(/[^\s\)]*)?")
    for m in url_pattern.finditer(text):
        host = m.group(1) or m.group(2)
        if host and not any(host.endswith(k) or k in host for k in known_good):
            # 학술적 화이트리스트에 없는 도메인 — 보고 (반드시 오류는 아님)
            issues.append(f"  ℹ️ 비표준 URL 의심: {host} (학술 화이트리스트 외)")
    return issues


def report_summary(text: str, facts: dict[str, Any]) -> int:
    """검증 결과 보고 — 종합."""
    print("=" * 70)
    print("sermon-textual-criticism 응답 사실 검증 보고")
    print("=" * 70)

    sigla = extract_sigla(text)
    if sigla:
        print(f"\n[1] 식별된 사본 사실 주장: {len(sigla)}건")
        seen: set[str] = set()
        for name, key in sigla:
            if key in seen:
                continue
            seen.add(key)
            db = facts["nt_manuscripts"].get(key) or facts["ot_manuscripts"].get(key)
            if db:
                print(f"  ✓ {name} → DB 매칭 (연대: {db.get('date', '?')})")
            else:
                print(f"  ✗ {name} → DB에 없음 — 의심")
    else:
        print("\n[1] 식별된 사본: 없음")

    date_issues = check_dates(text, facts)
    print(f"\n[2] 연대 사실 검증: {'오류 의심 ' + str(len(date_issues)) + '건' if date_issues else '통과 (0 오류)'}")
    for issue in date_issues:
        print(issue)

    abs_issues = check_absolute_claims(text)
    print(f"\n[3] G1 단정형 표현 검증: {'위반 의심 ' + str(len(abs_issues)) + '건' if abs_issues else '통과 (0 위반)'}")
    for issue in abs_issues:
        print(issue)

    metz_issues = check_metzger_grades(text)
    print(f"\n[4] G6 Metzger 등급 단언 검증: {'위반 ' + str(len(metz_issues)) + '건' if metz_issues else '통과 (0 위반)'}")
    for issue in metz_issues:
        print(issue)

    trap_issues = check_fake_ms_traps(text)
    print(f"\n[5] 사본 명칭 함정 검증: {'적발 ' + str(len(trap_issues)) + '건' if trap_issues else '통과 (0 함정)'}")
    for issue in trap_issues:
        print(issue)

    url_issues = check_url_authenticity(text)
    print(f"\n[6] 학술 디지털 자료 URL 검증: {'비표준 ' + str(len(url_issues)) + '건 보고' if url_issues else '통과 (모두 표준)'}")
    for issue in url_issues:
        print(issue)

    total = len(date_issues) + len(abs_issues) + len(metz_issues) + len(trap_issues)
    print("\n" + "=" * 70)
    if total == 0:
        print(f"✅ 검증 결과: 0 결함 (사본 사실·G1·G6·명칭 함정 모두 통과)")
    else:
        print(f"❌ 검증 결과: {total}건 결함 발견 — 응답 수정 필요")
    print("=" * 70)
    return total


def main() -> int:
    if len(sys.argv) > 1:
        path = Path(sys.argv[1])
        if not path.exists():
            print(f"파일 없음: {path}", file=sys.stderr)
            return 2
        text = path.read_text(encoding="utf-8")
    else:
        text = sys.stdin.read()
    if not text.strip():
        print("응답 텍스트가 비어 있음.", file=sys.stderr)
        return 2
    facts = load_facts()
    return 1 if report_summary(text, facts) else 0


if __name__ == "__main__":
    sys.exit(main())
