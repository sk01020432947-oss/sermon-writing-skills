---
name: orange-gradient-deck
description: 원고를 주면 오렌지 그라데이션 기업 프레젠테이션 PPTX를 생성. 그라데이션 풀블리드 배경+동심원 링 모티프, 흰 라운드 카드, 원형 사진, 도넛 게이지, 그라데이션 바 차트, 팀 서클 행, THANKS 클로징이 특징. 사용자가 "오렌지 그라데이션 PPT", "회사소개서 오렌지", "orange gradient deck", "/orange-gradient-deck"을 요청할 때 발동. HTML 덱이 아닌 진짜 .pptx 산출.
---

# orange-gradient-deck

원고(텍스트)를 받아 오렌지 그라데이션 기업 스타일의 **PPTX**를 생성한다.
레퍼런스: Company Creative Presentation 템플릿 룩.

## 디자인 토큰 (build.py에 내장 — 수정 금지)

- 그라데이션: 딥 오렌지 `#E04A17` → 라이트 `#F59E42` (배경 55°, 카드 30°, 바 90°)
- 잉크 `#33302E` / 그레이 `#8A8682` / 카드 보더 `#E8E4E0`
- 동심원 링 데코 자동 배치. 원형 사진은 Pillow 원형 마스크(PNG 알파)로 처리
- 도넛 게이지는 freeform 폴리곤(파이 도형 미사용). 사진 컬러 유지, 없으면 플레이스홀더
- 최상위 `brand`(예: "FASTPPT.NET")가 헤더·커버·땡큐에 자동 표기

## 워크플로

1. **원고 파싱** → 기업 서사: cover → contents → split(배경) → project → teamrow → stats → bars → cards3 → gradsection → thanks. 그라데이션 풀블리드(cover/contents/gradsection/thanks)와 화이트 슬라이드를 교차해 리듬을 만든다.
2. **spec JSON 작성** — 스크래치패드에 저장. `output` 기본값 `~/Documents/<제목>-orange.pptx`.
3. **빌드**: `python ~/.claude/skills/orange-gradient-deck/scripts/build.py spec.json`
4. **검증(가능하면)**: PowerPoint COM으로 PNG 내보내기 → 육안 확인 → 재빌드.
5. SendUserFile로 전달 + 파일 링크.

## spec JSON 스키마

```json
{
  "output": "...", "brand": "FASTPPT.NET",
  "slides": [
    {"layout": "cover", "title": "COMPANY", "sub": "Creative Presentation template"},
    {"layout": "contents", "title": "Contents", "items": ["About US", "Future strategies"]},
    {"layout": "split", "title": "Background", "body": "본문", "tag": "칩 텍스트(선택)", "image": "path"},
    {"layout": "project", "kicker": "Creative", "title": "Project", "body": "좌측 본문",
     "card_head": "Creative design", "card_body": "그라데이션 카드 본문", "image": "path(원형)"},
    {"layout": "teamrow", "title": "Service team", "body": "설명(선택)",
     "items": [{"name": "Justin", "role": "CEO", "body": "설명", "image": "path"}]},
    {"layout": "stats", "card_head": "Season 1", "card_body": "카드 본문", "image": "path(원형)",
     "items": [{"pct": 65, "head": "Performance", "body": "설명"}]},
    {"layout": "bars", "title": "Performance",
     "bars": [{"value": 30, "label": "1월"}, {"value": 55, "label": "2월"}],
     "items": [{"head": "Season 1", "body": "우측 설명"}]},
    {"layout": "cards3", "title": "Powerful design", "body": "우측 설명(선택)",
     "items": [{"icon": "🎨", "head": "Creative", "body": "설명", "image": "path"}]},
    {"layout": "gradsection", "title": "Connecting with our people", "kicker": "Business growth",
     "body": "본문", "image": "path"},
    {"layout": "thanks", "title": "THANKS", "sub": "Creative Presentation template",
     "meta": [["Phone", "+00 123 456"], ["E-mail", "a@b.com"], ["Web", "www.x.com"]]}
  ]
}
```

## 분량 가드 (넘침 방지 — 반드시 지킬 것)

- cover/thanks.title ≤10자(영문 60pt). contents.items ≤6(각 ≤22자)
- split/gradsection.body ≤450자. project.body ≤300자, card_body ≤180자
- teamrow.items ≤4(name ≤12자, body ≤80자). stats.items ≤2(body ≤130자), pct 0~100
- bars.bars 5~14개(value 양수, label ≤4자), items ≤2(body ≤150자)
- cards3.items 정확히 3개, body 각 ≤80자. thanks.meta ≤3쌍
- 원고가 길면 split/gradsection을 여러 장으로.

## 레이아웃 선택 가이드

- 표지 → `cover` / 목차 → `contents` / 회사 배경·연혁 소개 → `split`
- 프로젝트·제품 소개 → `project`(그라데이션 카드+원형 사진) / 팀 → `teamrow`
- 핵심 지표(%) → `stats`(도넛) / 추이·실적 → `bars` / 3개 항목 비교 → `cards3`
- 비전·문화 강조(풀블리드) → `gradsection` / 마무리 → `thanks`
