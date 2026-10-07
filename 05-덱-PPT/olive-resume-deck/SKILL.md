---
name: olive-resume-deck
description: 원고를 주면 크림 배경+올리브 그린 액센트+잉크 블랙의 레트로 레주메/포트폴리오 PPTX를 생성. 초대형 헤비 대문자 타이틀, 필(알약) 태그 칩, 검정 서클 넘버·퍼센트, 다크 테이블 패널, 컬러 사진 콜라주, 하단 크레딧 푸터+우측 세로 텍스트가 특징. 사용자가 "올리브 레주메 덱", "레트로 이력서 PPT", "hasu 스타일", "olive resume", "/olive-resume-deck"을 요청할 때 발동. HTML 덱이 아닌 진짜 .pptx 산출.
---

# olive-resume-deck

원고(텍스트)를 받아 크림/올리브/잉크 레트로 레주메 스타일의 **PPTX**를 생성한다.
레퍼런스: HASU Resume 템플릿 룩.

## 디자인 토큰 (build.py에 내장 — 수정 금지)

- 크림 `#EFE8DB` / 잉크 `#161616` / 올리브 `#A9A257` / 다크 패널 `#1C1C1C` / 그레이 `#6E6A60`
- 타이틀: Pretendard Black 대문자, 자간 음수. 사진: 컬러 유지 중앙 크롭, 없으면 플레이스홀더
- 모든 슬라이드 공통 크롬: 하단 헤어라인+주소(좌)+`DESIGN BY 작성자`(중)+쪽번호(우), 우측 세로 텍스트(`side`)
- 필 칩: 3개 중 1개꼴로 올리브 채움, 나머지 아웃라인 (자동)

## 워크플로

1. **원고 파싱** → 레주메 서사: cover → toc → about → columns(경력) → card(직무 상세) → circles(학력) → darktable(어학·스킬표) → stats(기술 %) → sidelist(봉사) → collage(취미) → contact.
2. **spec JSON 작성** — 스크래치패드에 저장. `output` 기본값 `~/Documents/<제목>-olive.pptx`.
3. **빌드**: `python ~/.claude/skills/olive-resume-deck/scripts/build.py spec.json`
4. **검증(가능하면)**: PowerPoint COM으로 PNG 내보내기 → 육안 확인 → 재빌드.
5. SendUserFile로 전달 + 파일 링크.

## spec JSON 스키마

최상위: `address`(푸터 좌측), `author`(DESIGN BY), `side`(우측 세로 텍스트, 예: 이메일·웹사이트).

```json
{
  "output": "...", "address": "123, street name city", "author": "Linda Brown", "side": "user@email.com — www.site.com",
  "slides": [
    {"layout": "cover", "title": "HASU", "mark": "®", "accent": "RESUME", "sub": "Presentation Template",
     "body": "소개(선택)", "image": "path"},
    {"layout": "toc", "title": "CONTENTS LIST",
     "items": [{"head": "Experience", "body": "한 줄 설명(선택)"}], "image": "path"},
    {"layout": "about", "title": "ABOUT\nME", "body": "소개 문단", "tags": ["Growth", "Insight"], "image": "path"},
    {"layout": "columns", "title": "EXPERIENCE", "body": "설명(선택)", "image": "path",
     "items": [{"head": "JAN - FEB", "body": "설명", "tag": "2021 Q1"}]},
    {"layout": "card", "title": "JOB POSITION", "head": "COMPANY NAME HERE", "period": "2023-2024",
     "sub": "Job / Position Title Here", "body": "본문", "bullets": ["항목1", "항목2"], "image": "path"},
    {"layout": "circles", "title": "EDUCATION", "body": "하단 설명(선택)", "image": "path",
     "items": [{"label": "ONE", "head": "JAN - FEB", "body": "설명", "tag": "2021 Q1"}]},
    {"layout": "darktable", "title": "COMMUNICATION\nSKILLS", "panel_head": "Communication Skills", "image": "path",
     "groups": [{"head": "Mother Tongue(s)", "rows": [["Korean", "100%"]]},
                {"head": "Other Language(s)", "rows": [["English", "80%"]]}]},
    {"layout": "stats", "title": "TECHNICAL\nSKILLS", "body": "설명(선택)", "image": "path",
     "items": [{"value": "10%", "head": "Insert Title", "body": "설명"}]},
    {"layout": "sidelist", "title": "VOLUNTEER\nWORK", "body": "본문", "tags": ["Design", "Mentoring"],
     "items": [{"head": "One. Work Name", "body": "설명", "image": "path"}]},
    {"layout": "collage", "title": "HOBBIES", "body": "본문", "tags": ["Baking", "Travel"],
     "images": ["p1", "p2", "p3", "p4", "p5"]},
    {"layout": "contact", "title": "GET\nIN TOUCH", "image": "path", "tags": ["Design", "Branding"],
     "meta": [["Address", "주소"], ["Phone", "번호"], ["Website", "주소"]]}
  ]
}
```

## 분량 가드 (넘침 방지 — 반드시 지킬 것)

- cover.title ≤6자(영문, 120pt — 길면 잘림), accent ≤8자. 한글 타이틀이면 build 전 title_size 조정 대신 글자수를 지켜라
- toc.items ≤7(head ≤14자). about/sidelist/collage.body ≤300자, tags 각 ≤10자
- columns/circles.items ≤4, body 각 ≤160자, tag ≤8자. card.bullets ≤6(각 ≤26자), body ≤400자
- darktable.groups 정확히 2개, rows 각 ≤6행. stats.items ≤4, value는 "10%"형, body ≤110자
- sidelist.items ≤3(body ≤110자). collage.images ≤5. contact.meta ≤3쌍
- 원고가 길면 card/columns를 여러 장으로.

## 레이아웃 선택 가이드

- 표지 → `cover`(다크 상단) / 목차 → `toc` / 자기소개 → `about`
- 시기별 나열 → `columns` / 회사·직무 하나 깊게 → `card`(올리브 카드) / 학력 → `circles`(서클 넘버)
- 표 형태 스킬(어학 등) → `darktable` / 퍼센트 역량 → `stats` / 활동+사진 리스트 → `sidelist`
- 사진 다수 → `collage` / 연락처 → `contact`
