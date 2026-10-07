#!/usr/bin/env python3
"""
sermon-history-culture-geo-context 응답 자동 검증 게이트.

LLM이 출력 *직전* 자기 응답을 이 스크립트에 통과시킨다.
references/* 4종에 정의된 검증 데이터(era-timeline·primary-sources·scholarly-debates)와
대조하여, 다음 5종 위험을 정량적으로 검출한다:

  1. 시대 좌표 위반 (검증 외 연대·통치자 단정)
  2. 외부 사료 인용 형식 위반 + 표준 외 절수 단정
  3. 학자명 + 정확 논문 단정 인용
  4. 시대착오 키워드 (팔레스타인 BC, 유대교 BC 2c 이전, 랍비 1c 이전 등)
  5. 학계 논쟁 22개 사안 단독 단정 (양 진영 병기 누락)

전 항목 PASS 시 응답 전송 허용. 한 항목이라도 WARN/FAIL 시 응답 수정 후 재검증.

사용:
  python3 verify_response.py < draft.txt
  python3 verify_response.py --file draft.txt
  python3 verify_response.py --text "응답 본문"

종료 코드:
  0 = PASS
  1 = WARN (1개 이상 약점, 사람 검토 필요)
  2 = FAIL (확실한 오류, 수정 필수)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from typing import List


# ---------------------------------------------------------------------------
# 검증 데이터 (references/era-timeline-verified.md 의 *완전 검증 목록*에서 동기화)
# ---------------------------------------------------------------------------

VERIFIED_INSCRIPTIONS = {
    # 명문/문서 → (학계 합의 연대 표기, 소장처)
    "메르넵타 비문": ("BC 1207경", "카이로 이집트 박물관"),
    "메르넵타": ("BC 1207경", "카이로 이집트 박물관"),
    "Merneptah Stele": ("BC 1207경", "카이로 이집트 박물관"),
    "시삭 부조": ("BC 925경", "카르나크 신전"),
    "Shoshenq": ("BC 925경", "카르나크 신전"),
    "모압 석비": ("BC 840경", "루브르 박물관"),
    "메샤 비문": ("BC 840경", "루브르 박물관"),
    "Mesha Stele": ("BC 840경", "루브르 박물관"),
    "텔단 비문": ("BC 9세기", "이스라엘 박물관"),
    "Tel Dan Stele": ("BC 9세기", "이스라엘 박물관"),
    "쿠르크 모놀리스": ("BC 853", "영국 박물관"),
    "Kurkh Monolith": ("BC 853", "영국 박물관"),
    "검은 오벨리스크": ("BC 825경", "영국 박물관"),
    "Black Obelisk": ("BC 825경", "영국 박물관"),
    "산헤립 프리즘": ("BC 691", "영국 박물관"),
    "Taylor Prism": ("BC 691", "영국 박물관"),
    "Sennacherib Prism": ("BC 691", "영국 박물관"),
    "라기스 부조": ("BC 700경", "영국 박물관"),
    "Lachish Reliefs": ("BC 700경", "영국 박물관"),
    "바벨론 연대기": ("BC 6세기", "영국 박물관"),
    "Babylonian Chronicles": ("BC 6세기", "영국 박물관"),
    "여호야긴 점토판": ("BC 590년대", "페르가몬 박물관"),
    "Jehoiachin Tablets": ("BC 590년대", "페르가몬 박물관"),
    "고레스 실린더": ("BC 539경", "영국 박물관"),
    "Cyrus Cylinder": ("BC 539경", "영국 박물관"),
    "엘레판틴 파피루스": ("BC 5세기", "베를린·카이로 박물관"),
    "Elephantine Papyri": ("BC 5세기", "베를린·카이로 박물관"),
    "사해사본": ("BC 3세기-AD 1세기", "이스라엘 박물관 사해사본 사당"),
    "Dead Sea Scrolls": ("BC 3세기-AD 1세기", "이스라엘 박물관 사해사본 사당"),
    "빌라도 비석": ("AD 26-36", "이스라엘 박물관"),
    "Pilate Stone": ("AD 26-36", "이스라엘 박물관"),
    "가야바 납골당": ("AD 1세기", "이스라엘 박물관"),
    "Caiaphas Ossuary": ("AD 1세기", "이스라엘 박물관"),
}

# 학계가 검증한 *최고 확실* 외부 사료 절수 (단정 인용 가능 목록)
SAFE_CITATIONS = {
    # 정확 절수 → 내용 한 줄 메모
    "Ant. 18.63-64": "테스티모니움 플라비아눔 (예수)",
    "Antiquities 18.63-64": "테스티모니움 플라비아눔",
    "유대 고대사 18.63-64": "테스티모니움 플라비아눔",
    "Ant. 18.116-119": "세례 요한 처형",
    "Antiquities 18.116-119": "세례 요한 처형",
    "유대 고대사 18.116-119": "세례 요한 처형",
    "Ant. 20.200": "야고보 처형",
    "Antiquities 20.200": "야고보 처형",
    "B.J. 6.249-266": "AD 70 성전 파괴",
    "War 6.249-266": "AD 70 성전 파괴",
    "유대 전쟁기 6.249-266": "AD 70 성전 파괴",
    "B.J. 7.252-406": "마사다",
    "War 7.252-406": "마사다",
    "Annales 15.44": "네로 박해·예수 빌라도 처형",
    "Annals 15.44": "네로 박해·예수 빌라도 처형",
    "연대기 15.44": "네로 박해·예수 빌라도 처형",
    "Claudius 25.4": "클라우디우스 유대인 추방",
    "Ep. 10.96": "기독교인 심문",
    "Epistulae 10.96": "기독교인 심문",
    "Legat. 38": "필로의 빌라도 묘사",
    "1마카비 4:52-59": "성전 정화 하누카",
    "1 Macc 4:52-59": "성전 정화 하누카",
    "2마카비 10:1-8": "성전 정화 하누카",
    # R1·R2에서 안전 확인된 부가 절수
    "Ant. 13.171-173": "요세푸스 3대 종파 묘사",
    "Antiquities 13.171-173": "요세푸스 3대 종파 묘사",
    "Ant. 17.190-191": "헤롯 사망 월식",
    "Ant. 17.167": "헤롯 사망 월식",
    "Ant. 18.11-22": "요세푸스 종파 분류 (4철학 포함)",
    "Ant. 18.15": "바리새파 영향력",
    "Ant. 18.35": "가야바 등장",
    "Ant. 18.55-62": "빌라도 성소 깃발 사건",
    "Ant. 18.85-89": "빌라도 사마리아 학살",
    "Ant. 12.138-144": "안티오쿠스 헌장",
    "B.J. 2.293-308": "AD 66 플로루스 약탈",
    "B.J. 2.499-555": "케스티우스 갈루스 패배",
    "B.J. 3.350-408": "요세푸스 요타파타 항복",
    "B.J. 6.68-92": "안토니아 함락",
    "B.J. 3.35-40": "갈릴리 지리 묘사",
    "Ag. Ap. 1.106-127": "메난드로스의 두로 왕 명단",
    "Against Apion 1.106-127": "메난드로스의 두로 왕 명단",
}

# 학계 논쟁 22개 사안 → 응답에서 다룰 때 양 진영 병기 의무 트리거 키워드
DEBATE_TRIGGERS = {
    "출애굽 연대": ["BC 1446", "BC 1260", "투트모세", "람세스 2세", "초기 연대설", "후기 연대설"],
    "가나안 정복 모델": ["군사 정복", "평화", "이주", "농민 봉기", "점진적 출현", "Finkelstein"],
    "다윗 솔로몬 왕국 규모": ["고년대학", "저년대학", "Mazar", "Finkelstein", "솔로몬 왕국 규모"],
    "다니엘서 저작": ["다니엘서 저작", "BC 6세기 다니엘", "BC 2세기 다니엘", "마카비기 저작"],
    "이사야서 저자": ["제2 이사야", "이사야 단일 저자", "이사야 두 저자", "Deutero-Isaiah"],
    "모세오경 JEDP": ["JEDP", "문서가설", "Wellhausen", "야훼 문서", "엘로힘 문서", "제사장 문서"],
    "예수 십자가 처형 연도": ["AD 30 십자가", "AD 33 십자가", "예수 처형 연도", "처형 AD 30", "처형 AD 33"],
    "사도행전 역사성": ["사도행전 역사성", "Bruce", "Hemer", "Haenchen", "Käsemann"],
    "산상수훈 vs 평지 설교": ["산상수훈 vs 평지", "평지 설교", "마태 편집 통합"],
    "출애굽 노예 인구": ["60만", "장정 60만", "엘레프", "출애굽 인구"],
    "셉투아진트 형성": ["72인 학자", "아리스테아스", "셉투아진트 형성", "LXX 형성"],
    "1세기 회당 정형": ["회당 예배 정형", "낭독 강해 정형", "1세기 회당 예배"],
    "바리새파 영향력": ["바리새파 영향력", "유대교 = 바리새파", "Ant. 18.15"],
    "사두개파 바리새파 에세네파 분류": ["3분류", "4분류", "제4철학", "요세푸스 종파"],
    "본디오 빌라도 성격": ["빌라도 잔혹", "빌라도 우유부단", "빌라도 성격"],
    "가야바 납골당 동일시": ["가야바 동일시", "Joseph who was called Caiaphas"],
    "팔레스타인 명칭": ["팔레스타인"],
    "헤롯 사망 연도": ["BC 4 헤롯 사망", "BC 1 헤롯 사망", "Steinmann"],
    "마사다 자살 vs 학살": ["마사다 자살", "마사다 학살", "Yadin 발굴"],
    "솔로몬 성전 위치": ["솔로몬 성전 위치", "바위 돔 위치"],
}

# 양 진영 병기 신호 (응답에 1개 이상 있어야 양설 병기로 인정)
BALANCE_MARKERS = [
    "학계 논쟁",
    "양 진영",
    "vs",
    "또는",
    "전통적",
    "비평학계",
    "전통 견해",
    "전통적 견해",
    "주류",
    "소수",
    "양설",
    "한편",
    "반면",
    "병기",
    "두 견해",
]

# 시대착오 패턴 (정규식)
ANACHRONISM_PATTERNS = [
    # (패턴, 설명, 등급)
    (r"(?<!후대 )(?<!후대\s)팔레스타인", "‘팔레스타인’ 명칭은 AD 135년 하드리아누스 명명. BC 시대·1세기 본문에 사용 시 시대 단서 필요", "WARN"),
    (r"(BC\s*\d|구약\s*시대|모세|족장|사사|왕국|포로기).{0,40}유대교", "‘유대교’는 BC 2세기 마카비기 이후 형성된 종교 범주. 그 이전 시대에 적용 시 시대 단서 필요", "WARN"),
    (r"(BC|구약).{0,30}랍비", "‘랍비’는 AD 1세기 후반-2세기부터 공식 호칭. 이전 시대에 적용 시 시대착오", "WARN"),
    (r"(BC\s*\d|구약|포로|페르시아|헬라|마카비).{0,30}기독교", "‘기독교/교회’ 명칭은 부활 사건 이후. 그 이전 시대에 적용 시 시대착오", "WARN"),
    (r"(BC|구약|왕국|족장).{0,30}비잔틴", "‘비잔틴’은 AD 4세기 이후 명칭", "WARN"),
    (r"미쉬나.{0,30}1세기.*?(이다|였다|는 것이다)(?!.*후대|.*AD 200)", "미쉬나(AD 200)를 1세기로 단정 — 시대 단서 필수", "WARN"),
    (r"탈무드.{0,30}1세기.*?(이다|였다|는 것이다)(?!.*후대|.*AD 200|.*AD 500)", "탈무드(AD 500-600)를 1세기로 단정 — 시대 단서 필수", "WARN"),
]

# 절대 금지 표현 (anti-hallucination-checklist 절대 금지 표현 목록)
FORBIDDEN_PHRASES = [
    ("당시는 분명", "본문에 없는 추측 — ‘동시대 자료를 종합하면 ~ 가능성’로 변경"),
    ("성경이 말하는 그대로 역사가 증명", "변호적 표현 — ‘본문과 X 고고학 증거가 일치한다’로 변경"),
    ("대부분의 학자들이 동의한다", "구체성 부족 — 학자명 1-2명 또는 ‘학계 합의/주류 학설’ 명시"),
    ("Ant. Rom.", "디오 카시우스의 작품 명칭은 Historia Romana. ‘Ant. Rom.’은 디오니시우스 폰 할리카르나소스의 작품"),
    ("Antiquitates Romanae", "이 작품은 디오니시우스 폰 할리카르나소스의 것. 디오 카시우스와 혼동 금지"),
]

# 작품 혼동 페어 (둘이 함께 나오면 점검 신호)
CONFUSION_PAIRS = [
    (["디오 카시우스", "Ant. Rom"], "디오 카시우스의 작품은 Historia Romana. Ant. Rom.은 디오니시우스 폰 할리카르나소스"),
    (["폴리비우스", "사도교부"], "폴리비우스(BC 200-118 역사가) vs 폴리카르포스(AD 사도교부) 혼동 점검"),
    (["대 플리니우스", "Epistulae"], "Epistulae는 소(2세) 플리니우스의 작품. 대 플리니우스는 Naturalis Historia"),
    (["소 플리니우스", "Naturalis Historia"], "Naturalis Historia는 대 플리니우스의 작품. 소 플리니우스는 Epistulae"),
]

# 신뢰도 등급 표기 (응답에 *결정적 주장* 있을 때 1개 이상 등장 권장)
CONFIDENCE_MARKERS = [
    "확정",
    "학계 합의",
    "주류 학설",
    "일반적으로",
    "학자 다수",
    "학계는",
    "논쟁 중",
    "양분",
    "추정",
    "일부 학자",
    "단정하기 어렵",
    "PROBABLE",
    "[CONFIRMED]",
    "전통적으로",
    "비평학계는",
]

# 외부 사료 인용 정규식 — 응답에서 일종의 절수 인용을 자동 추출
CITATION_REGEXES = [
    # 요세푸스 Ant. / Antiquities / 유대 고대사
    re.compile(r"(?:Ant\.|Antiquities|유대 고대사)\s*([0-9]+\.[0-9]+(?:[-–][0-9]+)?)"),
    # 요세푸스 B.J. / War / 유대 전쟁기
    re.compile(r"(?:B\.\s*J\.|War|유대 전쟁기)\s*([0-9]+\.[0-9]+(?:[-–][0-9]+)?)"),
    # 타키투스 Annales / Annals / 연대기
    re.compile(r"(?:Annales|Annals|연대기)\s*([0-9]+\.[0-9]+(?:[-–][0-9]+)?)"),
    # 미쉬나 m. *Tractate* X.Y
    re.compile(r"m\.\s*([A-Z][A-Za-z]+(?:\s*[A-Z][A-Za-z]+)*)\s*([0-9]+[.:][0-9]+)"),
    # 수에토니우스 Claudius/Nero 등
    re.compile(r"(?:Claudius|Nero|Augustus|Tiberius|Caligula|Vespasian|Titus|Domitian|Trajan)\s*([0-9]+\.[0-9]+)"),
    # 필로 Legat. / Flacc.
    re.compile(r"(?:Legat\.|Flacc\.|Legatio|In Flaccum|Mos\.|Spec\.\s*Leg\.|Prob\.)\s*([0-9]+(?:[-–][0-9]+)?)"),
    # 플리니우스 Ep. / Epistulae
    re.compile(r"(?:Ep\.|Epistulae)\s*([0-9]+\.[0-9]+(?:[-–][0-9]+)?)"),
    # 마카비 1마카비/2마카비
    re.compile(r"([12]마카비|1\s*Macc|2\s*Macc)\s*([0-9]+[.:][0-9]+(?:[-–][0-9]+)?)"),
]


# ---------------------------------------------------------------------------
# 결과 자료구조
# ---------------------------------------------------------------------------

@dataclass
class Finding:
    gate: str  # 1~5 + Forbidden + Confusion + Confidence
    severity: str  # PASS / WARN / FAIL
    message: str
    snippet: str = ""


@dataclass
class Report:
    findings: List[Finding] = field(default_factory=list)

    def add(self, gate: str, severity: str, message: str, snippet: str = "") -> None:
        self.findings.append(Finding(gate, severity, message, snippet))

    @property
    def fail_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == "FAIL")

    @property
    def warn_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == "WARN")

    def overall(self) -> str:
        if self.fail_count > 0:
            return "FAIL"
        if self.warn_count > 0:
            return "WARN"
        return "PASS"

    def to_text(self) -> str:
        lines = []
        lines.append(f"=== sermon-history-culture-geo-context 응답 검증 결과 ===")
        lines.append(f"전체: {self.overall()}  (FAIL={self.fail_count}, WARN={self.warn_count})")
        lines.append("")
        if not self.findings:
            lines.append("발견 없음. 응답 안전.")
            return "\n".join(lines)
        for i, f in enumerate(self.findings, 1):
            lines.append(f"[{i}] {f.gate} | {f.severity}")
            lines.append(f"    {f.message}")
            if f.snippet:
                lines.append(f"    스니펫: {f.snippet[:160]}")
            lines.append("")
        return "\n".join(lines)

    def to_json(self) -> str:
        return json.dumps(
            {
                "overall": self.overall(),
                "fail_count": self.fail_count,
                "warn_count": self.warn_count,
                "findings": [f.__dict__ for f in self.findings],
            },
            ensure_ascii=False,
            indent=2,
        )


# ---------------------------------------------------------------------------
# 게이트 구현
# ---------------------------------------------------------------------------

def gate1_era_timeline(text: str, report: Report) -> None:
    """Gate 1: 시대 좌표 — 검증된 명문 사용 시 연대·소장처 일치 점검."""
    for name, (era, museum) in VERIFIED_INSCRIPTIONS.items():
        # 한글·영문 공백 변형까지 허용
        if re.search(re.escape(name), text, flags=re.IGNORECASE):
            # 응답이 이 명문의 *완전 다른 연대*를 명시했는지 점검
            # — 검증 연대(예: BC 840경)에 대응하는 *세기 키워드* 누락 시 WARN
            era_key = re.findall(r"(BC\s*\d+|AD\s*\d+|\d+세기)", era)
            if era_key:
                found_any = any(re.search(re.escape(k), text) for k in era_key)
                if not found_any:
                    # 응답에서 명문 언급은 했으나 검증 연대를 명시하지 않음 → 일반화 권장
                    report.add(
                        gate="Gate1-시대좌표",
                        severity="WARN",
                        message=f"‘{name}’ 언급 시 학계 합의 연대({era})를 함께 명시 권장. era-timeline-verified.md 완전 검증 목록 일치.",
                        snippet=name,
                    )


def gate2_citation_form(text: str, report: Report) -> None:
    """Gate 2: 외부 사료 인용 형식 + 최고 확실 목록 외 단정 절수 검출."""
    citations = []
    for rx in CITATION_REGEXES:
        for m in rx.finditer(text):
            citations.append(m.group(0))
    # 안전 목록과 대조
    for cit in citations:
        # 안전 목록의 *부분 문자열*이라도 일치하면 OK
        safe = any(safe_key in cit for safe_key in SAFE_CITATIONS.keys())
        # 보조: 안전 목록의 정확한 절수가 cit에 포함된 경우
        if not safe:
            for safe_key in SAFE_CITATIONS.keys():
                # 절수만 같으면 OK (예: "Ant. 18.116-119"와 "Antiquities 18.116-119")
                # 안전 목록의 마지막 토큰(절수)을 추출하여 비교
                tail = safe_key.split()[-1]
                if tail and tail in cit:
                    safe = True
                    break
        if not safe:
            report.add(
                gate="Gate2-사료형식",
                severity="WARN",
                message=f"외부 사료 절수 ‘{cit}’가 *최고 확실 목록* 밖. Niese/Whiston 번호 차이 + LLM 한계로 일반화 표현 권장 (‘요세푸스 ~ 권의 ~ 기록에 따르면’).",
                snippet=cit,
            )


def gate3_anachronism(text: str, report: Report) -> None:
    """Gate 4(시대착오) — 후대 개념의 이전 시대 투사 점검."""
    for pattern, message, severity in ANACHRONISM_PATTERNS:
        m = re.search(pattern, text)
        if m:
            # 후대 단서가 함께 있는지 확인
            ctx_start = max(0, m.start() - 60)
            ctx_end = min(len(text), m.end() + 60)
            ctx = text[ctx_start:ctx_end]
            if any(hint in ctx for hint in ["후대", "AD 135", "AD 200", "AD 500", "후기", "이후", "소급"]):
                continue
            report.add(
                gate="Gate4-시대착오",
                severity=severity,
                message=message,
                snippet=ctx,
            )


def gate4_debates_balance(text: str, report: Report) -> None:
    """Gate 5(학계 논쟁) — 22개 사안 중 하나라도 다루면 양 진영 병기 의무."""
    balance_found = any(marker in text for marker in BALANCE_MARKERS)
    for topic, triggers in DEBATE_TRIGGERS.items():
        if any(trigger in text for trigger in triggers):
            if not balance_found:
                report.add(
                    gate="Gate5-학계논쟁",
                    severity="FAIL",
                    message=f"학계 논쟁 사안 ‘{topic}’ 다룸. 양 진영 병기 마커(‘학계 논쟁’, ‘vs’, ‘또는’, ‘비평학계’, ‘전통 견해’ 등) *없음* → scholarly-debates-balanced.md 의무 위반.",
                    snippet=", ".join(t for t in triggers if t in text)[:120],
                )


def gate_forbidden(text: str, report: Report) -> None:
    """절대 금지 표현 검출."""
    for phrase, fix in FORBIDDEN_PHRASES:
        if phrase in text:
            report.add(
                gate="금지표현",
                severity="FAIL",
                message=f"금지 표현 ‘{phrase}’ 검출. {fix}",
                snippet=phrase,
            )


def gate_confusion(text: str, report: Report) -> None:
    """자주 혼동되는 작품·인물 쌍 점검."""
    for terms, fix in CONFUSION_PAIRS:
        if all(t in text for t in terms):
            report.add(
                gate="혼동쌍",
                severity="FAIL",
                message=f"혼동 가능 쌍 검출: {' + '.join(terms)}. {fix}",
                snippet=" / ".join(terms),
            )


def gate_confidence_markers(text: str, report: Report) -> None:
    """신뢰도 등급 표기 점검 — 결정적 주장이 있는데 한정자가 없으면 WARN."""
    # 결정적 단정 신호
    decisive = re.findall(r"(?:[^\s]+)(?:이다|였다|이었다|이며|였으며)(?:[.\s]|$)", text)
    if len(decisive) >= 5:
        has_marker = any(m in text for m in CONFIDENCE_MARKERS)
        if not has_marker:
            report.add(
                gate="신뢰도등급",
                severity="WARN",
                message="응답에 다수 단정 표현이 있으나 신뢰도 한정자(‘학계 합의’, ‘일반적으로’, ‘추정’, ‘논쟁 중’ 등)가 *전무*. anti-hallucination-checklist.md 의무 위반 위험.",
                snippet=str(len(decisive)) + "건 단정",
            )


def gate_scholar_paper(text: str, report: Report) -> None:
    """학자명 + 정확 논문/연도 단정 인용 점검 — 일반화 표현 권장."""
    # 학자명 + 연도 4자리 + 인용 표지 형태 검출
    pattern = re.compile(
        r"([A-Z][a-z]+(?:\s*(?:and|et al\.|와|·)\s*[A-Z][a-z]+)*)\s*(?:\(|『|《)?\s*((?:19|20)\d{2})"
    )
    for m in pattern.finditer(text):
        scholar = m.group(1)
        year = m.group(2)
        # ‘추정’·‘견해’·‘일반화’ 단서가 ±60자 내에 있으면 OK
        ctx_start = max(0, m.start() - 60)
        ctx_end = min(len(text), m.end() + 60)
        ctx = text[ctx_start:ctx_end]
        if any(h in ctx for h in ["추정", "견해", "주장", "라고 본다", "라고 봄", "을 비롯한 학자들", "등 학자"]):
            continue
        report.add(
            gate="학자논문단정",
            severity="WARN",
            message=f"‘{scholar} {year}’ — 학자명+연도 단정 인용. anti-hallucination-checklist 보강 C 위반. ‘{scholar}를 비롯한 학자들의 추정에 따르면’ 식 일반화 권장.",
            snippet=f"{scholar} {year}",
        )


# ---------------------------------------------------------------------------
# 메인
# ---------------------------------------------------------------------------

def run_verification(text: str) -> Report:
    report = Report()
    gate1_era_timeline(text, report)
    gate2_citation_form(text, report)
    gate3_anachronism(text, report)
    gate4_debates_balance(text, report)
    gate_forbidden(text, report)
    gate_confusion(text, report)
    gate_confidence_markers(text, report)
    gate_scholar_paper(text, report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="sermon-history-culture-geo-context 응답 검증 게이트")
    parser.add_argument("--file", help="검증할 응답 텍스트 파일 경로")
    parser.add_argument("--text", help="검증할 응답 텍스트 (인라인)")
    parser.add_argument("--json", action="store_true", help="JSON 출력")
    args = parser.parse_args()

    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            text = f.read()
    elif args.text:
        text = args.text
    else:
        text = sys.stdin.read()

    if not text.strip():
        print("입력 없음.", file=sys.stderr)
        return 2

    report = run_verification(text)

    if args.json:
        print(report.to_json())
    else:
        print(report.to_text())

    if report.fail_count > 0:
        return 2
    if report.warn_count > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
