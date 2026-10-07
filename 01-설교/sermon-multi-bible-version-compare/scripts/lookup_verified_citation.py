#!/usr/bin/env python3
"""
lookup_verified_citation.py — 검증된 코란/탈무드/Vulgata 인용 사실 lookup.

본 도구는 인용 토픽을 입력받아 references/ 파일에 등재된
검증된 사실만 반환한다. 등재되지 않은 토픽은 "자신 없음" 응답.

Usage:
  python3 lookup_verified_citation.py quran "예수 십자가 부정"
  python3 lookup_verified_citation.py talmud "아케다"
  python3 lookup_verified_citation.py vulgata "요한 1:1"
"""

from __future__ import annotations
import sys


# 코란 검증 사실 (quran-verified-citations.md 동기화)
QURAN_FACTS = {
    "예수 십자가 부정": {
        "sura": "수라 4:157-159",
        "topic": "예수의 십자가 죽음 부정",
        "summary": "이슬람은 예수의 십자가 죽음을 부정. 그와 비슷한 모양만 보였을 뿐이라는 본문.",
        "korean_translators": ["김용선역", "최영길역", "Sahih International에서 한역"],
        "warning": "정통 기독교의 십자가 죽음 교리(사도신경·니케아 신경)와 정면 충돌.",
    },
    "예수 자기 증언": {
        "sura": "수라 19:30-34",
        "topic": "마리아 품의 어린 예수가 자신을 알라의 종으로 소개",
        "summary": "예수는 알라의 종(*아브드 알라*)이며 선지자라고 자기 증언.",
        "korean_translators": ["김용선역", "최영길역"],
        "warning": "신성·삼위일체 부정과 일치하는 본문.",
    },
    "삼위일체 부정": {
        "sura": "수라 5:116",
        "topic": "알라가 예수께 '나와 마리아를 신으로 모시라 했느냐' 묻는 장면",
        "summary": "이슬람이 이해한 *삼위일체*는 알라·예수·마리아 모심. 정통 기독교 삼위일체(성부·성자·성령)와 다름.",
        "korean_translators": ["김용선역", "최영길역"],
        "warning": "이슬람의 삼위일체 이해 자체가 오해에 기반하므로 비교 시 이 사실 명시.",
    },
    "예수 말씀 영": {
        "sura": "수라 4:171",
        "topic": "예수는 마리아에게 던져진 알라의 말씀(*칼리마투후*)·영(*루훈 민후*)",
        "summary": "이슬람은 '말씀'·'영'을 피조물 또는 능력으로 이해. 기독교의 영원한 위격(로고스·성령)과 다름.",
        "korean_translators": ["김용선역", "최영길역"],
        "warning": "용어는 비슷하나 신학적 내용 정반대.",
    },
    "동정녀 수태": {
        "sura": "수라 3:47, 수라 19:20-21",
        "topic": "마리아의 동정녀 수태",
        "summary": "이슬람도 동정녀 수태 인정. 차이는 수태된 분의 신성 여부.",
        "korean_translators": ["김용선역", "최영길역"],
        "warning": "동정녀 수태는 인정하나 그분의 신성은 부정.",
    },
    "아브라함 결박": {
        "sura": "수라 37:99-113",
        "topic": "아브라함과 아들의 결박 사건",
        "summary": "코란 본문 자체는 아들 이름 미명시. 다수 무슬림 학자는 이스마엘로 해석하나 초기 일부 주석가는 이삭. 본문 vs 해석 구별 필수.",
        "korean_translators": ["김용선역", "최영길역"],
        "warning": "기독교/유대교는 명백히 이삭 (창 22:2 '네 사랑하는 독자 이삭').",
    },
    "아담 타락": {
        "sura": "수라 2:30-34, 7:11-25, 20:115-127",
        "topic": "아담·하와의 타락",
        "summary": "코란은 원죄 교리 없음. 타락 후 알라가 즉시 용서 (수라 2:37). 사탄(이블리스)의 거부·추방 강조.",
        "korean_translators": ["김용선역", "최영길역"],
        "warning": "기독교 원죄 교리(롬 5:12)와 정면 충돌.",
    },
    "다윗 시편": {
        "sura": "수라 4:163, 17:55",
        "topic": "다윗과 자부르(시편)",
        "summary": "이슬람은 다윗을 예언자로 보고 시편을 알라의 계시로 인정하나, 현재 본문이 변조되었다는 *타흐리프* 입장.",
        "korean_translators": ["김용선역", "최영길역"],
        "warning": "현 시편 본문 권위를 부정.",
    },
    "모세 토라": {
        "sura": "수라 5:44",
        "topic": "모세에게 토라가 계시됨",
        "summary": "이슬람은 토라를 알라의 계시로 인정하나 변조되었다는 *타흐리프* 주장.",
        "korean_translators": ["김용선역", "최영길역"],
        "warning": "현 토라 본문 권위를 부정.",
    },
    "알라의 일치": {
        "sura": "수라 112 (수라 알-이클라스)",
        "topic": "단일신론",
        "summary": "'알라는 한 분이시다. 알라는 영원하시다. 낳지도 낳음을 받지도 않으셨다. 그분과 동등한 자가 없다.'",
        "korean_translators": ["김용선역", "최영길역"],
        "warning": "정통 기독교 삼위일체와 가장 첨예하게 대립. '낳음을 받지도 않으셨다'는 *성자*의 영원적 출생 교리(신경) 부정.",
    },
}


# 탈무드 검증 사실 (talmud-verified-citations.md 동기화)
TALMUD_FACTS = {
    "아케다 사탄": {
        "ref": "b. Sanhedrin 89b",
        "topic": "아케다(이삭 결박) — 사탄의 고발",
        "summary": "사탄이 여호와께 욥과 같이 아브라함을 고발하여 시험의 동인이 되었다는 랍비 전승.",
        "warning": "기독교 해석(언약·메시아 예표)과 강조점 다름.",
    },
    "아브라함 10 시험": {
        "ref": "m. Pirkei Avot 5:3",
        "topic": "아브라함의 10가지 시험",
        "summary": "아브라함이 받은 10대 시험 중 아케다가 최대(또는 최후)였다는 미쉬나 전승.",
        "warning": "10가지 목록은 후대 주석가들이 보완.",
    },
    "벤 자카이 임종": {
        "ref": "b. Berakhot 28b",
        "topic": "라반 요하난 벤 자카이 임종 기도",
        "summary": "임종을 앞둔 라반의 기도와 제자들의 반응. 70년 멍에 진 율법 학자의 임종.",
        "warning": "흔한 오기: b. Berakhot 17a로 잘못 표기. 28b가 정확.",
    },
    "메타트론": {
        "ref": "b. Sanhedrin 38b, b. Chagigah 15a",
        "topic": "메타트론과 '두 권능' 논쟁",
        "summary": "Aher(엘리샤 벤 아부야)가 메타트론을 보고 '두 권능 in heaven'이라 외친 일화. 정통 일신론과 어그러져 보이는 카발라적 전통.",
        "warning": "기독교의 성부-성자 두 위격 교리와 다름. 단, 비교종교학적으로 흥미.",
    },
    "두 메시아": {
        "ref": "b. Sukkah 52a",
        "topic": "메시아 벤 요셉·메시아 벤 다윗",
        "summary": "고난받는 메시아 벤 요셉(전사·죽음)과 왕적 메시아 벤 다윗 두 전통.",
        "warning": "기독교의 한 메시아 두 직분(고난+영광) 해석과 비교.",
    },
    "예수 탈무드": {
        "ref": "b. Sanhedrin 43a, 67a, 107b",
        "topic": "탈무드의 '예슈' 또는 'Ben Stada/Pandera' 언급",
        "summary": "Vilna판은 검열본. Steinsaltz판·Soncino영역판 등 비검열본에서 '예슈가 마법을 행하고 이스라엘을 잘못 인도했다'는 언급.",
        "warning": "검열본/비검열본 차이 명시 필수. 매우 제한된 언급.",
    },
    "황금률 힐렐": {
        "ref": "b. Shabbat 31a",
        "topic": "힐렐의 황금률 (부정형)",
        "summary": "'네가 싫어하는 것을 네 이웃에게 행하지 말라. 이것이 전부이며 나머지는 주석이다.'",
        "warning": "예수의 황금률(마 7:12, 눅 6:31, 긍정형)과 비교. 힐렐은 BC 1세기 인물.",
    },
    "한 영혼 한 세계": {
        "ref": "m. Sanhedrin 4:5",
        "topic": "한 영혼을 구하는 자는 한 세계를 구한다",
        "summary": "'한 영혼을 멸하는 자는 한 세계를 멸하는 것과 같고, 한 영혼을 구하는 자는 한 세계를 구하는 것과 같다.'",
        "warning": "사본에 따라 '이스라엘에서 한 영혼' / '한 영혼' 차이. 후자가 더 보편적 형식.",
    },
    "안식일 39 금지노동": {
        "ref": "m. Shabbat 7:2",
        "topic": "안식일 39가지 금지 노동",
        "summary": "안식일 *멜라카*(노동) 39가지 카테고리. 후대 할라카의 기본.",
        "warning": "예수의 '안식일은 사람을 위해' 가르침과 비교 풍부.",
    },
    "토라 전승": {
        "ref": "m. Pirkei Avot 1:1",
        "topic": "토라 전승 사슬",
        "summary": "'모세는 시내산에서 토라를 받아 여호수아에게 전했고, 여호수아는 장로들에게, 장로들은 예언자들에게, 예언자들은 큰 회당의 사람들에게.'",
        "warning": "구전 토라(Mishnah)의 권위 정당화 본문.",
    },
}


# Vulgata 검증 사실 (vulgata-facts.md 동기화)
VULGATA_FACTS = {
    "요 1:1": {
        "clementine": "In principio erat Verbum, et Verbum erat apud Deum, et Deus erat Verbum.",
        "nova_vulgata": "In principio erat Verbum, et Verbum erat apud Deum, et Deus erat Verbum.",
        "diff": "동일. 차이 거의 없음.",
        "korean": "태초에 말씀이 계셨고, 말씀이 하나님과 함께 계셨고, 말씀은 하나님이셨다.",
        "note": "헬라어 원문 *καὶ θεὸς ἦν ὁ λόγος*에서 술어 *θεὸς*는 정관사 부재 — Colwell's Rule 적용 (Wallace, *Greek Grammar Beyond the Basics*). 정관사 부재는 *질적* 강조이지 *비한정적* 의미가 아님.",
        "source": "Clementine Vulgate 1592 (Ioan 1:1); Nova Vulgata 1979 (Evangelium Secundum Ioannem 1:1)",
        "scholarly_reference": "Stuttgart Vulgate (Weber-Gryson 5th ed., 2007) p.1655; Nova Vulgata vatican.va/archive/bible/nova_vulgata/documents/nova-vulgata_nt_evang-ioannem_lt.html#1"
    },
    "요 3:16": {
        "clementine": "Sic enim Deus dilexit mundum, ut Filium suum unigenitum daret, ut omnis qui credit in eum, non pereat, sed habeat vitam æternam.",
        "nova_vulgata": "Sic enim dilexit Deus mundum, ut Filium suum unigenitum daret, ut omnis, qui credit in eum, non pereat, sed habeat vitam aeternam.",
        "diff": "어순 미세 차이 (*Sic enim Deus dilexit* vs *Sic enim dilexit Deus*), *æ*/*ae* 철자.",
        "korean": "하나님께서 세상을 이렇게 사랑하사 그 외아들을 주셨으니, 이는 그를 믿는 모든 자가 멸망하지 않고 영생을 얻게 하려 하심이다.",
        "source": "Clementine Vulgate 1592 (Ioan 3:16); Nova Vulgata 1979 (Evangelium Secundum Ioannem 3:16)",
        "scholarly_reference": "Stuttgart Vulgate (Weber-Gryson 5th ed., 2007) p.1658; Metzger, A Textual Commentary on the Greek New Testament (UBS5, 2014) p.175"
    },
    "시 23:1": {
        "clementine": "Dominus regit me, et nihil mihi deerit. (Ps 22:1 Vg Gallicanum)",
        "nova_vulgata": "Dominus pascit me, et nihil mihi deerit. (Ps 22:1 Nova Vulgata)",
        "diff": "*regit*(다스리시다) vs *pascit*(목축하시다·먹이시다). Nova Vulgata는 Jerome의 Iuxta Hebraicos를 채택해 히브리어 *ro'i*(목자)에 충실. Clementine은 Psalterium Gallicanum(LXX 기반 라틴 전승) 보존.",
        "korean": "주께서 나를 다스리시니(Clementine) / 주께서 나를 먹이시니(Nova Vulgata) — 부족함이 없으리라.",
        "numbering_note": "Vulgata 시편 번호: 22편 = 한국어 23편 (LXX 번호 사용).",
        "source": "Clementine Vulgate 1592 Psalterium Gallicanum (Ps 22:1); Nova Vulgata 1979 (Psalmus 22:1; iuxta Hebraeos)",
        "scholarly_reference": "Stuttgart Vulgate (Weber-Gryson 5th ed.) p.797 (Psalterium Gallicanum); Rahlfs-Hanhart LXX (2006) Ps 22:1; BHS (5th ed., 1997) Ps 23:1"
    },
    "마 6:13": {
        "clementine": "Et ne nos inducas in tentationem, sed libera nos a malo. Amen.",
        "nova_vulgata": "Et ne inducas nos in tentationem, sed libera nos a Malo.",
        "diff": "Amen 유무, *malo*/*Malo* 대문자 (사탄 인격화), 어순. '나라와 권세와 영광...'은 Vulgata 어디에도 없음 (Byzantine TR에만).",
        "korean": "우리를 시험에 빠지지 말게 하시고, 다만 악(또는 악한 자)에서 구하소서.",
        "source": "Clementine Vulgate 1592 (Matt 6:13); Nova Vulgata 1979 (Evangelium Secundum Matthaeum 6:13)",
        "scholarly_reference": "Stuttgart Vulgate p.1535; NA28 (2012) p.13 — 결구 '나라와 권세와 영광' Byzantine TR/Didache 8:2 등 후대 사본 전승"
    },
    "요일 5:7-8": {
        "clementine": "Quoniam tres sunt, qui testimonium dant in coelo: Pater, Verbum, et Spiritus Sanctus...",
        "nova_vulgata": "Comma Johanneum 제거됨 (각주만).",
        "diff": "Comma Johanneum. Clementine만 포함, Nova Vulgata·Stuttgart는 제거. NA28도 본문에서 제외.",
        "korean": "Clementine: '하늘에 증언하시는 분이 셋이 계시니 아버지, 말씀, 성령이시며...'",
        "warning": "4-5세기 헬라어 사본에 없음. Erasmus 3판(1522)에 라틴 사본 통해 추가.",
        "source": "Clementine Vulgate 1592 (1 Ioan 5:7-8 Comma Johanneum); Nova Vulgata 1979 — 본문 제거, 각주만",
        "scholarly_reference": "NA28 (2012) p.713 critical apparatus; Metzger, Textual Commentary (2014) pp.647-649; Erasmus, Novum Instrumentum 3rd ed. (1522) — Comma Johanneum 추가 출처"
    },
    "요 14:6": {
        "clementine": "Dicit ei Iesus: Ego sum via, et veritas, et vita. Nemo venit ad Patrem, nisi per me.",
        "nova_vulgata": "Dicit ei Iesus: 'Ego sum via et veritas et vita; nemo venit ad Patrem nisi per me.'",
        "diff": "쉼표 유무·인용부호 처리 차이만. 본문 자체 동일.",
        "korean": "예수께서 그에게 말씀하시기를 '나는 길이요 진리요 생명이니, 나로 말미암지 않고는 아버지께로 올 자가 없다.'",
        "source": "Clementine Vulgate 1592 (Ioan 14:6); Nova Vulgata 1979",
        "scholarly_reference": "Stuttgart Vulgate p.1675; Nova Vulgata Evangelium Ioannis 14:6"
    },
    "출 20:13": {
        "clementine": "Non occides.",
        "nova_vulgata": "Non occides.",
        "diff": "동일. 단, 히브리어 *lo tirṣaḥ*(לֹא תִּרְצָח)는 정확히는 *murder*(불법 살인)이며, 라틴 *occidere*는 *murder/kill* 양쪽 가능. 영어 KJV 'Thou shalt not kill'은 라틴 따른 폭넓은 번역, NIV·ESV 'You shall not murder'는 히브리어 정밀.",
        "korean": "살인하지 말라.",
        "numbering_note": "유대교는 출 20:13을 세 번째 그룹의 첫 계명으로 봄. 가톨릭·루터교는 안식일 분리 후 다른 번호. 개혁교회·정교회는 또 다른 번호 체계.",
        "source": "Clementine Vulgate 1592 (Ex 20:13); Nova Vulgata 1979 (Exodus 20:13)",
        "scholarly_reference": "Stuttgart Vulgate p.99; BHS p.122; Mishnah Makkot 1:1 (10계명 번호 체계)"
    },
    "마 5:3": {
        "clementine": "Beati pauperes spiritu: quoniam ipsorum est regnum cælorum.",
        "nova_vulgata": "Beati pauperes spiritu, quoniam ipsorum est regnum caelorum.",
        "diff": "구두점·æ/ae 철자만. 본문 동일.",
        "korean": "심령이 가난한 자는 복이 있나니, 천국이 그들의 것임이라.",
        "note": "*pauperes spiritu* — '영(*spiritus*)에서의 가난'. 헬라어 *πτωχοὶ τῷ πνεύματι*. 눅 6:20 평행본 *Beati pauperes*는 *영*이 빠진 단순 '가난한 자'. 마-눅 차이가 신학적 강조점 분기.",
        "source": "Clementine Vulgate 1592 (Matt 5:3); Nova Vulgata 1979",
        "scholarly_reference": "Stuttgart Vulgate p.1532; NA28 p.10; Davies-Allison, ICC Matthew Vol.1 (1988) pp.435-444 — pauperes spiritu 학계 해석사"
    },
    "고전 13:13": {
        "clementine": "Nunc autem manent fides, spes, caritas, tria haec: maior autem horum est caritas.",
        "nova_vulgata": "Nunc autem manet fides, spes, caritas, tria haec; maior autem ex his est caritas.",
        "diff": "*manent*(복수) vs *manet*(단수) — '셋'을 통합으로 보는지 분리로 보는지. *horum* vs *ex his*.",
        "korean": "이제 믿음·소망·사랑, 이 세 가지는 항상 있을 것인데, 그 중에 제일은 사랑이다.",
        "note": "**핵심**: *caritas*는 *신학적 덕*(virtutes theologicae) — fides·spes·caritas — 중 하나이며, *추기경적 덕*(virtutes cardinales) — prudentia·iustitia·fortitudo·temperantia — 과 *다름*. 두 분류를 혼동 금지.",
        "source": "Clementine Vulgate 1592 (1 Cor 13:13); Nova Vulgata 1979 (Epistula I ad Corinthios 13:13)",
        "scholarly_reference": "Stuttgart Vulgate p.1789; NA28 p.532; Fee, NICNT 1 Corinthians (1987) p.649 — fides/spes/caritas theological virtue 분류"
    },
    "창 3:15": {
        "clementine": "Inimicitias ponam inter te et mulierem, et semen tuum et semen illius: ipsa conteret caput tuum, et tu insidiaberis calcaneo ejus.",
        "nova_vulgata": "Inimicitias ponam inter te et mulierem et inter semen tuum et semen illius; ipsum conteret caput tuum, et tu conteres calcaneum eius.",
        "diff": "**핵심 차이**: Clementine *ipsa conteret* (그녀 — 여자) vs Nova Vulgata *ipsum conteret* (그것 — 후손). MT 히브리어는 *hu* (그/그것, 남성 단수)로 '후손'을 가리킴. LXX는 *autos*(남성). Vulgata 원본(제롬)은 *ipse*(그), 후대 사본 전승에서 *ipsa*(그녀)로 변형 → Clementine. Nova Vulgata는 *ipsum*(그것, 후손 = semen)으로 복원.",
        "korean": "내가 너와 여자 사이에, 너의 후손과 여자의 후손 사이에 적의를 두리니, [그/그녀/그것]이 네 머리를 부수고, 너는 그의 발꿈치를 [상하게/노릴 것]이다.",
        "note": "**마리아론 논쟁의 핵심 본문**: Clementine *ipsa*는 가톨릭 전통의 마리아=두 번째 하와 해석 근거가 됨. 그러나 본문비평·MT·LXX·Nova Vulgata 모두 *후손*(남성/중성)을 지칭. 개신교는 *ipse/ipsum* 채택. 천주교 2005 한국어판도 '그녀'가 아닌 '그'로 옮김. *원시복음*(protoevangelium)으로서 메시아 예언으로 읽는 데에는 양 진영 공통.",
        "warning": "Clementine *ipsa*는 후대 사본 변형. 제롬 원본은 *ipse*. 인용 시 어느 판인지 명시.",
        "source": "Clementine Vulgate 1592 (Gen 3:15); Nova Vulgata 1979 (Liber Genesis 3:15) — ipsa/ipsum 본문비평 핵심",
        "scholarly_reference": "Stuttgart Vulgate p.7; BHS p.5; Wenham, WBC Genesis 1-15 (1987) pp.79-81 — ipsa/ipse 본문비평; Tov, Textual Criticism of the Hebrew Bible (3rd ed., 2012) §7.1.2"
    },
    "행 2:38": {
        "clementine": "Petrus vero ad illos: Pœnitentiam, inquit, agite, et baptizetur unusquisque vestrum in nomine Jesu Christi in remissionem peccatorum vestrorum: et accipietis donum Spiritus Sancti.",
        "nova_vulgata": "Petrus vero ad illos: 'Paenitentiam agite, et baptizetur unusquisque vestrum in nomine Iesu Christi in remissionem peccatorum vestrorum, et accipietis donum Sancti Spiritus.'",
        "diff": "구두점·œ/ae 철자, *Spiritus Sancti* vs *Sancti Spiritus* 어순. 본문 의미 동일.",
        "korean": "베드로께서 그들에게 말씀하기를 '회개하라, 그리고 너희 죄 사함을 위해 너희 각자가 예수 그리스도의 이름으로 세례를 받으라. 그리하면 너희가 성령의 선물을 받으리라.'",
        "note": "*Pœnitentiam agite* — *회개를 행하라* (행위 강조). 종교개혁 시기 루터의 99개 논제 1번 비판 — '회개'(헬 *metanoeite*)는 단발 행위가 아닌 평생의 마음 돌이킴. 라틴어 *poenitentiam agite*는 헬라어 *μετανοεῖτε*를 좁게 옮긴 면이 있다는 평가.",
        "source": "Clementine Vulgate 1592 (Act 2:38); Nova Vulgata 1979",
        "scholarly_reference": "Stuttgart Vulgate p.1700; NA28 p.385; Luther, 95 Theses Thesis 1 (1517) — poenitentiam agite/metanoeite 논쟁"
    },
    "시 8:4": {
        "clementine": "Quid est homo, quod memor es ejus? aut filius hominis, quoniam visitas eum? (Vg Ps 8:5)",
        "nova_vulgata": "Quid est homo, quod memor es eius, aut filius hominis, quoniam visitas eum?",
        "diff": "구두점·œ/ae 철자만. 본문 동일.",
        "korean": "사람이 무엇이기에 주께서 그를 기억하시며, 인자가 무엇이기에 주께서 그를 돌보십니까?",
        "note": "**번호 매핑**: 한국어/MT 시 8:4 ↔ Vg/LXX Ps 8:5 (+1 절 차이). 시 8편 표제어를 LXX/Vg가 1절로 계수. 한국어/MT는 표제어를 비번호 처리.",
        "source": "Clementine Vulgate 1592 Psalterium Gallicanum (Ps 8:5; LXX 절번호); MT 시 8:4",
        "scholarly_reference": "Stuttgart Vulgate p.778 (Ps 8:5 LXX 번호); BHS p.1093 (Ps 8:5 BHS 번호 — 표제 1절); Rahlfs LXX Ps 8:5"
    },
    "시 8:5": {
        "clementine": "Minuisti eum paulo minus ab angelis: gloria et honore coronasti eum, (Vg Ps 8:6)",
        "nova_vulgata": "Minuisti eum paulo minus ab angelis, gloria et honore coronasti eum.",
        "diff": "구두점만. 본문 동일.",
        "korean": "그를 하나님보다 조금 못하게 하시고 영화와 존귀로 관을 씌우셨나이다.",
        "note": "**중요 매핑**: 한국어/MT 시 8:5 ↔ Vg/LXX Ps 8:6. 히 2:6-8에서 *LXX 형식*으로 인용 — '천사보다 조금 못하게'. 히브리어 *elohim*(하나님)을 LXX가 *angelous*(천사들)로 옮긴 것이 핵심. 신약은 LXX 채택.",
        "warning": "한국어 '하나님보다' vs 신약 인용 '천사보다'는 *번역 어휘 선택*의 결과이지 본문 충돌이 아님. 히브리어 *elohim* 다의어 처리.",
        "source": "Clementine Vulgate 1592 Psalterium Gallicanum (Ps 8:6; LXX 절번호); MT 시 8:5; 히 2:6-8 인용",
        "scholarly_reference": "Stuttgart Vulgate p.778 (Ps 8:6); BHS p.1093 (Ps 8:6 — 표제 1절); 히 2:6-8 LXX 인용"
    },
    "마 16:18": {
        "clementine": "Et ego dico tibi, quia tu es Petrus, et super hanc petram ædificabo Ecclesiam meam, et portæ inferi non prævalebunt adversus eam.",
        "nova_vulgata": "Et ego dico tibi: Tu es Petrus, et super hanc petram aedificabo Ecclesiam meam; et portae inferi non praevalebunt adversum eam.",
        "diff": "구두점·æ/ae 철자만. 본문 동일.",
        "korean": "내가 또한 너에게 이르노니 너는 베드로(Petrus)라, 내가 이 반석(petram) 위에 내 교회를 세우리니, 음부의 권세가 이를 이기지 못하리라.",
        "note": "**핵심 단어 유희**: 헬라어 *Πέτρος*(베드로 — 남성, '돌') vs *πέτρα*(반석 — 여성, '바위'). 라틴어도 *Petrus*(남) vs *petram*(여)로 같은 유희. 가톨릭은 베드로 자신을 반석으로 해석, 개신교 다수는 베드로의 신앙고백을 반석으로 해석. 아람어 *케파* 단일 어휘 가능성도 학설.",
        "warning": "교황 수위권 vs 사도적 계승 논쟁의 핵심 본문. 인용 시 해석 전통 명시.",
        "source": "Clementine Vulgate 1592 (Matt 16:18); Nova Vulgata 1979",
        "scholarly_reference": "Stuttgart Vulgate p.1551; NA28 p.49; Davies-Allison ICC Matthew Vol.2 (1991) pp.602-615 — Petrus/petra 해석사"
    },
    "사 53:5": {
        "clementine": "Ipse autem vulneratus est propter iniquitates nostras, attritus est propter scelera nostra: disciplina pacis nostræ super eum, et livore ejus sanati sumus.",
        "nova_vulgata": "Ipse autem vulneratus est propter iniquitates nostras, attritus est propter scelera nostra; disciplina pacis nostrae super eum, et livore eius sanati sumus.",
        "diff": "구두점·æ/ae 철자만. 본문 동일.",
        "korean": "그가 찔림은 우리의 허물 때문이요, 그가 상함은 우리의 죄악 때문이라. 그가 징계를 받음으로 우리는 평화를 누리고, 그가 채찍에 맞음으로 우리는 나음을 얻었도다.",
        "note": "**고난의 종 본문**. 신약 다수 인용 (벧전 2:24, 마 8:17 등). 유대교는 이사야 53장의 종을 *이스라엘 민족*으로 해석 (Rashi, 11세기). 기독교는 메시아 예수로 해석 (LXX 시점부터). 두 해석은 사 53장의 *언약 공동체와 메시아*에 대한 신학적 갈림.",
        "warning": "랍비 전통은 53장 종을 이스라엘 민족으로, 기독교는 메시아로 해석. 인용 시 해석 전통 명시.",
        "source": "Clementine Vulgate 1592 (Isaiae 53:5); Nova Vulgata 1979 (Isaias 53:5)",
        "scholarly_reference": "Stuttgart Vulgate p.1166; BHS p.762; Rahlfs LXX Is 53:5; Hengel, Atonement (1981) pp.49-65 — Suffering Servant 신약 인용"
    },
    "출 3:14": {
        "clementine": "Dixit Deus ad Moysen: Ego sum qui sum. Ait: Sic dices filiis Israël: Qui est misit me ad vos.",
        "nova_vulgata": "Dixit Deus ad Moysen: 'Ego sum qui sum.' Ait: 'Sic dices filiis Israel: Qui est misit me ad vos.'",
        "diff": "구두점·인용부호 처리만. 본문 동일.",
        "korean": "하나님께서 모세에게 말씀하시기를 '나는 스스로 있는 자이니라.' 또 말씀하시기를 '너는 이스라엘 자손에게 이렇게 이르라. 〈〈스스로 있는 자〉〉께서 나를 너희에게 보내셨다 하라.'",
        "note": "**핵심**: 히브리어 *ehyeh asher ehyeh*(אֶהְיֶה אֲשֶׁר אֶהְיֶה) — '나는 있는 자다' 또는 '나는 있을 자다'. 미완료시제. LXX *Ἐγώ εἰμι ὁ ὤν*(나는 *존재하는 자*다, 분사). 라틴 *Ego sum qui sum*(나는 나인 자다). 신약 요한복음의 *ego eimi*(나는 ~이다) 발언이 이 본문을 인유.",
        "warning": "신약 *ego eimi*가 신성 자기 증언 함의를 띠는 이유는 출 3:14 LXX 표현이 신학적 기반. 인용 시 LXX/Vulgate 어형도 함께 제시.",
        "source": "Clementine Vulgate 1592 (Exod 3:14); Nova Vulgata 1979 (Exodus 3:14)",
        "scholarly_reference": "Stuttgart Vulgate p.69; BHS p.88; Childs, OTL Exodus (1974) pp.61-89 — ehyeh asher ehyeh 해석사"
    },
    "마 1:23": {
        "clementine": "Ecce virgo in utero habebit, et pariet filium: et vocabunt nomen ejus Emmanuel, quod est interpretatum Nobiscum Deus.",
        "nova_vulgata": "Ecce, virgo in utero habebit et pariet filium, et vocabunt nomen eius Emmanuel, quod est interpretatum Nobiscum Deus.",
        "diff": "구두점·œ/ae 철자만. 본문 동일.",
        "korean": "보라, 처녀가 잉태하여 아들을 낳을 것이요, 그의 이름을 *임마누엘*이라 부르리라. 임마누엘을 번역하면 *하나님이 우리와 함께 계시다*라는 뜻이다.",
        "note": "**핵심**: 마태가 사 7:14를 LXX 형식으로 인용. LXX는 히브리어 *almah*(젊은 여자)를 *parthenos*(처녀)로 의역. 마태는 이 LXX 의역을 채택해 *처녀 출산* 메시아 예언으로 확립.",
        "warning": "사 7:14 히브리어 자체는 *almah*(처녀일 수도 있는 젊은 여자). LXX 의역 + 마태 인용을 통해 *처녀 출산* 교리 확립. 본문비평적 정직 필요.",
        "source": "Clementine Vulgate 1592 (Matt 1:23 인용 Isaiae 7:14 LXX); Nova Vulgata 1979",
        "scholarly_reference": "Stuttgart Vulgate p.1525; NA28 p.3; Brown, The Birth of the Messiah (1993) pp.143-153 — almah/parthenos 인용 사슬"
    },
    "요 6:53": {
        "clementine": "Dixit ergo eis Jesus: Amen, amen dico vobis: nisi manducaveritis carnem Filii hominis, et biberitis ejus sanguinem, non habebitis vitam in vobis.",
        "nova_vulgata": "Dixit ergo eis Iesus: 'Amen, amen dico vobis: Nisi manducaveritis carnem Filii hominis et biberitis eius sanguinem, non habetis vitam in vobismetipsis.'",
        "diff": "*non habebitis*(미래) vs *non habetis*(현재) — Clementine 미래, Nova Vulgata 현재. *vobis*/*vobismetipsis* 강조형 차이.",
        "korean": "이에 예수께서 그들에게 말씀하시기를 '진실로 진실로 너희에게 이르노니, 인자의 살을 먹지 아니하고 인자의 피를 마시지 아니하면, 너희 속에 생명이 없으리라.'",
        "note": "**성찬 신학의 핵심 본문**. 가톨릭은 화체설(transubstantiation), 루터교는 성령적 임재 또는 공재설(consubstantiation), 개혁교회는 영적 임재(스피리투얼리스) 또는 상징(zwinglian) 해석. 본문 자체는 *manducare*(육체적 먹음)을 사용.",
        "warning": "성례 신학 핵심 논쟁 본문. 인용 시 해석 전통 명시.",
        "source": "Clementine Vulgate 1592 (Ioan 6:53); Nova Vulgata 1979 (Ioannes 6:53)",
        "scholarly_reference": "Stuttgart Vulgate p.1663; NA28 p.296; Brown, AB John I-XII (1966) pp.281-294 — 성찬 신학 해석사"
    },
    "룻 1:16": {
        "clementine": "Quæ respondit: Ne adverseris mihi ut relinquam te et abeam: quocumque enim perrexeris, pergam, et ubi morata fueris, et ego pariter morabor. Populus tuus populus meus, et Deus tuus Deus meus.",
        "nova_vulgata": "Quae respondit: 'Ne adverseris mihi, ut relinquam te et abeam; quocumque perrexeris, pergam, et ubi morata fueris, et ego pariter morabor. Populus tuus populus meus, et Deus tuus Deus meus.'",
        "diff": "구두점·æ/ae 철자, *enim* 유무. 본문 의미 동일.",
        "korean": "그(룻)가 대답하기를 '당신을 떠나 돌아가라고 강권하지 마소서. 당신이 가시는 곳에 나도 가고, 당신이 머무시는 곳에 나도 머물겠나이다. 당신의 백성이 나의 백성이 되고, 당신의 하나님이 나의 하나님이 되시리이다.'",
        "note": "**중요 컨텍스트**: 시어머니-며느리 관계 약속. *결혼 서약이 아님*. 결혼 서약으로 인용하는 것은 오용 — common-misreadings.md §K.4 참조.",
        "warning": "결혼식에서 자주 인용되나 원래 컨텍스트는 시어머니-며느리. 인용 시 컨텍스트 명시.",
        "source": "Clementine Vulgate 1592 (Ruth 1:16); Nova Vulgata 1979 (Liber Ruth 1:16)",
        "scholarly_reference": "Stuttgart Vulgate p.358; BHS p.1320; Hubbard, NICOT Ruth (1988) pp.117-119 — 컨텍스트 분석"
    },
    "막 16:9": {
        "clementine": "Surgens autem mane prima sabbati, apparuit primo Mariæ Magdalenæ, de qua ejecerat septem dæmonia. (마 16:9-20 긴 결말 포함)",
        "nova_vulgata": "Surgens autem mane, prima sabbati, apparuit primo Mariae Magdalenae, de qua eiecerat septem daemonia. (대괄호로 표시 또는 각주)",
        "diff": "Clementine은 본문에 포함. Nova Vulgata·Stuttgart Vulgate는 본문에 포함하되 학술적 의심 표시. NA28도 이중 괄호로 의심 표시.",
        "korean": "예수께서 안식일 다음 첫날 새벽에 부활하사 막달라 마리아에게 먼저 보이셨으니, 마리아는 일곱 귀신이 떠났던 자라.",
        "note": "**막 16:9-20 긴 결말**: 시내·바티칸 사본(4세기)에 없음. 단, 다수 후대 사본(A·C·D·W·Θ·Byzantine)에 있음. 라틴 전통은 일관되게 포함. 신약 사본학에서 가장 논쟁적인 본문 중 하나.",
        "warning": "본문비평 논쟁의 핵심. 인용 시 사본 전통 명시. 뱀을 잡거나 독을 마시는 등의 본문(16:18)은 신학적 적용에 신중 요청.",
        "source": "Clementine Vulgate 1592 (Marc 16:9 — 긴 결말 포함); Nova Vulgata 1979 (Evangelium Secundum Marcum 16:9 — 본문 포함하되 학술적 의심 표시)",
        "scholarly_reference": "Stuttgart Vulgate p.1607; NA28 p.187 (이중 괄호 표시); Metzger, Textual Commentary (2014) pp.102-106 — Longer Ending of Mark"
    },
    "욥 19:25": {
        "clementine": "Scio enim quod redemptor meus vivit, et in novissimo die de terra surrecturus sum:",
        "nova_vulgata": "Scio enim quod redemptor meus vivit, et in novissimo de terra surrecturus sit,",
        "diff": "Clementine *surrecturus sum*(나는 일어날 것이다) vs Nova Vulgata *surrecturus sit*(그가 일어날 것이다). 주어가 *나* vs *구속자* 차이. *die* 유무.",
        "korean": "내가 알기로는 나의 구속자가 살아 계시니, 마지막 날에 그가(또는 내가) 땅 위에 서실(설) 것이라.",
        "note": "**핵심**: 히브리어 *go'el*(구속자)을 Vulgata가 *redemptor*로, LXX가 *ho mellōn ekluein me*로 옮김. Clementine은 '내가 일어난다' — 욥의 부활 인식. Nova Vulgata는 '그가 일어난다' — 구속자의 출현 강조. 핸델 메시아 *I know that my redeemer liveth*가 KJV(Clementine 계열) 기반.",
        "source": "Clementine Vulgate 1592 (Iob 19:25); Nova Vulgata 1979 (vatican.va/archive/bible/nova_vulgata/documents/nova-vulgata_vt_iob_lt.html#19)",
        "scholarly_reference": "Stuttgart Vulgate p.756; BHS p.1257; Rahlfs LXX Iob 19:25; Clines, WBC Job 1-20 (1989) pp.452-465 — go el 해석사"
    },
    "전 12:13": {
        "clementine": "Finem loquendi pariter omnes audiamus. Deum time, et mandata ejus observa: hoc est enim omnis homo.",
        "nova_vulgata": "Finis loquendi, omnibus auditis: Deum time et mandata eius observa; hoc est enim omnis homo.",
        "diff": "*Finem loquendi pariter omnes audiamus*(모두가 듣자 — 권면) vs *Finis loquendi omnibus auditis*(모든 것을 들었으니 — 결론). Clementine은 능동, Nova Vulgata는 수동(absolute).",
        "korean": "일의 결국을 다 들었으니 하나님을 경외하고 그의 명령들을 지킬지어다. 이것이 모든 사람의 본분이라.",
        "note": "**전도서 결론**. 히브리어 *zeh kol-ha'adam*(이것이 모든 사람) — 라틴어 *hoc est enim omnis homo* 직역. *omnis homo*가 '모든 사람의 본분' 또는 '모든 사람'으로 해석.",
        "source": "Clementine Vulgate 1592 (Eccl 12:13); Nova Vulgata 1979 (Ecclesiastes 12:13)",
        "scholarly_reference": "Stuttgart Vulgate p.989; BHS p.1349; Rahlfs LXX Eccl 12:13; Crenshaw, OTL Ecclesiastes (1987) pp.190-194"
    },
    "미 6:8": {
        "clementine": "Indicabo tibi, o homo, quid sit bonum, et quid Dominus requirat a te: utique facere judicium, et diligere misericordiam, et sollicitum ambulare cum Deo tuo.",
        "nova_vulgata": "Indicatum est tibi, o homo, quid sit bonum, et quid Dominus quaerat a te: utique facere iudicium et diligere caritatem et sollicitum ambulare cum Deo tuo.",
        "diff": "*Indicabo*(미래 1인칭, 내가 말하리라) vs *Indicatum est*(완료 수동, 보여졌다). *requirat*/*quaerat* 동사 차이. *misericordiam*(자비) vs *caritatem*(사랑) — 히브리어 *hesed*에 대한 다른 라틴어 어휘 선택.",
        "korean": "사람아 주께서 선한 것이 무엇임을 네게 보이셨나니 여호와께서 네게 구하시는 것은 오직 정의를 행하며 인자를 사랑하며 겸손히 네 하나님과 함께 행하는 것이 아니냐.",
        "note": "**핵심 어휘**: 히브리어 *hesed*(언약적 사랑·인자)를 Clementine은 *misericordia*(자비), Nova Vulgata는 *caritas*(사랑)로 옮김. 본문 자체에서 두 라틴 어휘 선택의 신학적 차이가 드러남.",
        "source": "Clementine Vulgate 1592 (Mich 6:8); Nova Vulgata 1979 (Michaeas 6:8)",
        "scholarly_reference": "Stuttgart Vulgate p.1392; BHS p.1041; Rahlfs LXX Mic 6:8; Andersen-Freedman, AB Micah (2000) pp.520-531 — hesed/misericordia/caritas 분석"
    },
    "갈 2:20": {
        "clementine": "Vivo autem, jam non ego: vivit vero in me Christus. Quod autem nunc vivo in carne: in fide vivo Filii Dei, qui dilexit me, et tradidit semetipsum pro me.",
        "nova_vulgata": "Vivo autem, iam non ego, sed vivit in me Christus; quod autem nunc vivo in carne, in fide vivo Filii Dei, qui dilexit me et tradidit seipsum pro me.",
        "diff": "구두점·*sed* 유무·*semetipsum*/*seipsum* 강조형 차이만. 본문 의미 동일.",
        "korean": "내가 그리스도와 함께 십자가에 못 박혔나니, 그런즉 이제는 내가 사는 것이 아니요 오직 내 안에 그리스도께서 사시는 것이라. 이제 내가 육체 가운데 사는 것은 나를 사랑하사 나를 위하여 자기 자신을 버리신 하나님의 아들을 믿는 믿음 안에서 사는 것이라.",
        "note": "**바울 신학의 핵심 자기 증언**. *fide Filii Dei*(하나님의 아들을 믿는 믿음) — 주관적 소유격 vs 목적적 소유격 논쟁(*pistis Christou*). N.T. Wright·Richard Hays는 *그리스도의 신실하심*으로 읽음. 전통 개혁주의는 *그리스도를 향한 우리의 믿음*으로 읽음.",
        "source": "Clementine Vulgate 1592 (Gal 2:20); Nova Vulgata 1979 (Ad Galatas 2:20)",
        "scholarly_reference": "Stuttgart Vulgate p.1804; NA28 p.585; Hays, The Faith of Jesus Christ (2nd ed., 2002) — pistis Christou 논쟁"
    },
    "약 2:17": {
        "clementine": "Sic et fides, si non habeat opera, mortua est in semetipsa.",
        "nova_vulgata": "Sic et fides, si non habeat opera, mortua est in semetipsa.",
        "diff": "동일.",
        "korean": "이와 같이 행함이 없는 믿음은 그 자체가 죽은 것이라.",
        "note": "**종교개혁 핵심 논쟁 본문**. 루터가 야고보서를 '지푸라기 서신'(Strohepistel)이라 부른 이유. 다만 칼빈은 야고보의 '믿음'을 *vivid 살아있는 믿음*과 *unfruitful 열매 없는 믿음*의 구분으로 조화시킴. 트리엔트 공의회는 본 본문을 *justification by faith and works*의 근거로 사용.",
        "source": "Clementine Vulgate 1592 (Jac 2:17); Nova Vulgata 1979 (Iacobi 2:17)",
        "scholarly_reference": "Stuttgart Vulgate p.1855; NA28 p.668; Trent Council 1547 Session 6 ch.16 (Denzinger §1532) — opera 신학 정의"
    },
    "행 17:28": {
        "clementine": "in ipso enim vivimus, et movemur, et sumus: sicut et quidam vestrorum poëtarum dixerunt: Ipsius enim et genus sumus.",
        "nova_vulgata": "In ipso enim vivimus et movemur et sumus, sicut et quidam vestrorum poetarum dixerunt: 'Ipsius enim et genus sumus.'",
        "diff": "구두점·œ/ae 철자만.",
        "korean": "우리가 그를 힘입어 살며 기동하며 존재하느니라. 너희의 어떤 시인들도 말한 바와 같이 '우리가 또한 그의 자녀라' 하니",
        "note": "**바울의 헬라 시인 인용**. *Ipsius enim et genus sumus*는 헬라 시인 *Aratus*(Phaenomena 5) 또는 *Cleanthes*(Hymn to Zeus)의 시구. 바울이 *pagan poetry*를 *기독교 진리*로 재맥락화. *General Revelation*(일반 계시) 신학의 성경적 근거.",
        "source": "Clementine Vulgate 1592 (Act 17:28); Nova Vulgata 1979 (Actus Apostolorum 17:28)",
        "scholarly_reference": "Stuttgart Vulgate p.1734; NA28 p.421; Aratus Phaenomena 5 (Hellenistic Library) — 시인 인용 출처"
    },
    "골 1:15": {
        "clementine": "qui est imago Dei invisibilis, primogenitus omnis creaturæ:",
        "nova_vulgata": "qui est imago Dei invisibilis, primogenitus omnis creaturae,",
        "diff": "구두점·æ/ae 철자만. 본문 동일.",
        "korean": "그는 보이지 아니하시는 하나님의 형상이시요 모든 피조물보다 먼저 나신 이시니",
        "note": "**아리우스 논쟁 핵심 본문**. *primogenitus omnis creaturae*(피조물의 처음 나신 자) — 헬라어 *πρωτότοκος πάσης κτίσεως*. 아리우스는 '피조물 중 첫째 = 피조물'로 해석. 정통은 *πρωτότοκος*(processit non factum, 신경)의 *주권·우선성*으로 해석. *Filium Dei unigenitum*(요 1:14 신경 어휘)와 함께 니케아 신경의 *generated, not made* 형성.",
        "warning": "아리우스주의·여호와의 증인이 흔히 인용하는 본문. 골 1:16-17의 컨텍스트(*그로 말미암아 만물이 창조되었으니*)로 정통 해석 확립.",
        "source": "Clementine Vulgate 1592 (Col 1:15); Nova Vulgata 1979 (Ad Colossenses 1:15)",
        "scholarly_reference": "Stuttgart Vulgate p.1834; NA28 p.620; Nicene Creed 325 (Tanner, Decrees 1990 Vol.1 p.5) — primogenitus 정통 해석"
    },
    "히 11:1": {
        "clementine": "Est autem fides sperandarum substantia rerum, argumentum non apparentium.",
        "nova_vulgata": "Est autem fides sperandorum substantia, rerum argumentum non apparentium.",
        "diff": "*sperandarum substantia rerum*(소망하는 것들의 실체) vs *sperandorum substantia, rerum argumentum*(소망의 실체, 일들의 증거) — 구두점·성수 형태 차이로 의미 분기. 전자는 'res sperandarum'(소망하는 것들)을 형용, 후자는 *sperandorum*(소망의 것)과 *rerum*(일들)을 분리.",
        "korean": "믿음은 바라는 것들의 실상이요 보이지 않는 것들의 증거니",
        "note": "**히브리어 단어 *emunah* vs 헬라어 *pistis* vs 라틴어 *fides***. *substantia*(실체)·*hypostasis*(헬라어)의 라틴 번역. 보에티우스·아퀴나스의 *substantia/substantiae* 형이상학 어휘 기초.",
        "source": "Clementine Vulgate 1592 (Hebr 11:1); Nova Vulgata 1979 (Ad Hebraeos 11:1)",
        "scholarly_reference": "Stuttgart Vulgate p.1879; NA28 p.700; Aquinas, Summa Theologica II-II q.4 — substantia/fides 형이상학"
    },
    "슥 12:10": {
        "clementine": "Et effundam super domum David et super habitatores Jerusalem spiritum gratiæ et precum: et aspicient ad me, quem confixerunt: et plangent eum planctu quasi super unigenitum, et dolebunt super eum, ut doleri solet in morte primogeniti.",
        "nova_vulgata": "Et effundam super domum David et super habitatores Ierusalem spiritum gratiae et precum; et aspicient ad me, quem confixerunt, et plangent eum planctu quasi super unigenitum et dolebunt super eum, ut doleri solet super primogenitum.",
        "diff": "구두점·œ/ae 철자, *in morte*(죽음에) vs *super*(위에서) 마지막 구의 미세 차이.",
        "korean": "내가 다윗의 집과 예루살렘 주민에게 은총과 간구의 영을 부어 주리니, 그들이 그 찌른 자(나) 곧 나를 바라보고, 그를 위하여 애통하기를 독자를 위하여 애통하듯 하며, 그를 위하여 슬퍼하기를 장자를 위하여 슬퍼하듯 하리로다.",
        "note": "**요 19:37 인용**: 십자가 옆구리 찌름의 예언적 본문. *aspicient ad me, quem confixerunt*(그들이 찌른 자 곧 나를 바라보리라) — 히브리어 *we-hibbitu elay et asher-daqaru*. 본문비평적으로 *elay*(나에게)가 일부 사본에서 *elaw*(그에게)로 변형. 마소라 전통은 *elay* 보존.",
        "source": "Clementine Vulgate 1592 (Zach 12:10); Nova Vulgata 1979 (Zaccharias 12:10)",
        "scholarly_reference": "Stuttgart Vulgate p.1421; BHS p.1080; Rahlfs LXX Zach 12:10; Meyers-Meyers, AB Zechariah 9-14 (1993) pp.330-345"
    },
    "살전 4:17": {
        "clementine": "deinde nos, qui vivimus, qui relinquimur, simul rapiemur cum illis in nubibus obviam Christo in aëra, et sic semper cum Domino erimus.",
        "nova_vulgata": "deinde nos, qui vivimus, qui relinquimur, simul rapiemur cum illis in nubibus obviam Domino in aera, et sic semper cum Domino erimus.",
        "diff": "*obviam Christo*(그리스도를 만나러) vs *obviam Domino*(주를 만나러). *aëra*/*aera* 철자.",
        "korean": "그 후에 우리 살아 남아 있는 자들도 그들과 함께 구름 속으로 끌어 올려 공중에서 주를 영접하게 하시리니, 그리하여 우리가 항상 주와 함께 있으리라.",
        "note": "**휴거 신학 본문**. *rapiemur*(우리가 채여 올려질 것이다) — 헬라어 *ἁρπαγησόμεθα*. 라틴어 *rapio*에서 *Rapture* 영어 어휘 유래. 다만 본 본문이 *그리스도의 재림 시 부활과 동시 사건*인지 *별도 휴거 사건*인지는 dispensationalism 논쟁의 핵심. 정통 종말론 다수는 *동시*로 해석.",
        "warning": "Tim LaHaye의 *Left Behind* 시리즈 휴거 신학과 정통 종말론(아미레니얼·포스트미레니얼) 차이. 인용 시 신학적 입장 명시.",
        "source": "Clementine Vulgate 1592 (1 Thess 4:17); Nova Vulgata 1979 (Epistula I ad Thessalonicenses 4:17)",
        "scholarly_reference": "Stuttgart Vulgate p.1822; NA28 p.629; Wanamaker, NIGTC 1-2 Thessalonians (1990) pp.173-176 — rapiemur 종말론 학파"
    },
}


def lookup_quran(topic: str) -> dict | None:
    for key, value in QURAN_FACTS.items():
        if topic in key or key in topic or any(t in topic for t in [value.get("sura", ""), value.get("topic", "")]):
            return value
    return None


def lookup_talmud(topic: str) -> dict | None:
    for key, value in TALMUD_FACTS.items():
        if topic in key or key in topic or any(t in topic for t in [value.get("ref", ""), value.get("topic", "")]):
            return value
    return None


def lookup_vulgata(ref: str) -> dict | None:
    # 직접 본문 참조 lookup
    if ref in VULGATA_FACTS:
        return VULGATA_FACTS[ref]
    # 부분 매칭
    for key, value in VULGATA_FACTS.items():
        if ref in key or key in ref:
            return value
    return None


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    source = sys.argv[1].lower()
    query = " ".join(sys.argv[2:])

    if source == "quran":
        result = lookup_quran(query)
    elif source == "talmud":
        result = lookup_talmud(query)
    elif source == "vulgata":
        result = lookup_vulgata(query)
    else:
        print(f"미지원 소스: {source} (quran/talmud/vulgata)")
        sys.exit(1)

    print()
    if result is None:
        print(f"질의 '{query}' 미등재. 자신 있는 출처 확보 전 *인용 금지*.")
        print("references/ 파일을 직접 확인하여 등재 여부 점검하거나,")
        print("Sefaria(탈무드)·Quran.com(코란)·Vatican.va(Vulgata)에서 1차 검증.")
        sys.exit(1)
    else:
        for k, v in result.items():
            print(f"{k}: {v}")
    print()


def _self_test():
    """검증 도구 자체 테스트."""
    failures = []

    # 1. 코란 lookup 정상
    result = lookup_quran("예수 십자가 부정")
    if result is None or "157-159" not in result.get("sura", ""):
        failures.append(f"  FAIL: 코란 십자가 부정 lookup 실패: {result}")

    # 2. 탈무드 lookup 정상
    result = lookup_talmud("아케다 사탄")
    if result is None or "89b" not in result.get("ref", ""):
        failures.append(f"  FAIL: 탈무드 아케다 lookup 실패: {result}")

    # 3. 벤 자카이 임종 — 28b이지 17a 아님
    result = lookup_talmud("벤 자카이 임종")
    if result is None or "28b" not in result.get("ref", ""):
        failures.append(f"  FAIL: 벤 자카이 임종 lookup 실패: {result}")

    # 4. Vulgata 요 1:1
    result = lookup_vulgata("요 1:1")
    if result is None or "Verbum" not in result.get("clementine", ""):
        failures.append(f"  FAIL: Vulgata 요 1:1 lookup 실패: {result}")

    # 5. 미등재 토픽
    result = lookup_quran("존재하지 않는 토픽 xyz")
    if result is not None:
        failures.append(f"  FAIL: 미등재 토픽이 매칭됨: {result}")

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
