# 10 애플식 런칭 필름 (Apple-style Launch Film)
원본: YouTube 영상 속 "애플 스타일 런칭 영상" 시연 결과(가상 브랜드 Slowlife.) · 재현

## 한 문장 버전
원문(영어 스타일):
> Make an Apple-style launch film for "Slowlife.", a framed-print shop: a blinking cursor types the wordmark, a circle-cropped coffee photo, a landscape that expands with a scrub bar, the same image on an iPhone lock screen, the product page "Morning mist €129", the framed print on a wall with drifting leaf shadows, and the wordmark again. Only crisp morphs, masks and push transitions — no crossfades, blur-ins, glows, particles or 3D flips.

한국어:
> 액자 프린트 가게 "Slowlife."의 애플식 런칭 영상을 만들어줘. 깜빡이는 커서가 워드마크를 타이핑 → 원형으로 잘린 커피 사진 → 풍경이 화면 가득 펼쳐지고 스크럽바로 보정 비교 → 같은 사진이 아이폰 잠금화면 → 상품 페이지 "Morning mist €129" → 벽에 걸린 액자와 흔들리는 잎 그림자 → 다시 워드마크. 전환은 마스크·모프·푸시만, 크로스페이드·블러인·글로우·파티클·3D 플립 금지.

## 구조 버전
<inputs>
문구: Slowlife. / Sunday 27 September · 6:47 / FRAMED PRINT · Morning mist · €129 · Frame · Size 30×40 50×70 70×100 · Add to cart → ✓ Added — on its way
소재: 사진 대신 SVG로 그린 커피 탑뷰(나무 테이블·잔·라테아트), 항구와 산 풍경(구름·산 2겹·마을·배·바다)
비율 1080x1080 · 16초 · 무음
</inputs>
<direction>
바깥 검정, 큰 둥근 카드 #F1EFEA(940px, 모서리 56px) 안에서만 일어난다. 글꼴 Pretendard 800, 자간 -0.05em(SF 느낌). 이징은 expo.inOut / power4.out만.
전환 문법: ① 창(window) 크기·모서리 모프로 내용 드러내기 ② 마스크 안 글자 올리기 ③ 화면 밀어내기(push). 커서는 상품 페이지에서만 클릭.
금지: 크로스페이드, 블러인, 밝기 현상(developing), 3D 플립, 파티클, 글로우.
</direction>
<structure>
| 초 | 화면 | 움직임 |
|---|---|---|
| 0–1 | 빈 카드 | 세로 커서 깜빡 |
| 1–2.4 | 워드마크 | 글자 하나씩 타입셋(마스크 상승), 커서가 따라감 → 접힘 |
| 2.4–4 | 커피 | 워드마크 위로 밀려나가고 원형 창이 열림 → 둥근 사각 타일로 모프 |
| 4–6.7 | 풍경 | 커피 왼쪽으로 푸시, 풍경 타일 오른쪽에서 들어와 카드 전체로 확장, 스크럽바 올라와 커서가 드래그하며 보정본 분할 비교 |
| 6.9–8.6 | 아이폰 | 풍경 창이 폰 화면으로 모프, 베젤·다이내믹 아일랜드, 날짜·6:47 마스크 상승 |
| 8.6–11.6 | 브라우저 상품 페이지 | 폰 밀려나고 페이지 푸시 인, 커서: 검정 프레임 → 50×70(액자 커짐) → Add to cart(문구 위로 교체) |
| 11.6–14.1 | 벽 | 위로 푸시, 검정 액자, 육각형 마스크로 그림 리빌(육각형 꼭짓점이 매트 안에 완전히 들어오게 — 프레임에 잘리면 안 됨), 흐린 잎 그림자 흔들림 |
| 14.1–16 | 엔딩 | 벽 위로 빠지고 워드마크 글자별 상승, 홀드 |
</structure>
<build>
HTML 한 파일, GSAP 타임라인 seek, 30fps 렌더, 결정론(마을·배·나뭇결·잎은 Motion.rand 시드). 풍경은 `<symbol id="land">` 하나를 `<use>`로 풍경·보정본·폰·상품·액자에 재사용(use에 width/height 940 명시).
</build>

## 바꿔 쓰기 포인트 (소재만 교체할 자리)
- 브랜드 워드마크 `word()`의 'Slowlife.', 잠금화면 날짜·시각, 상품명·가격·옵션
- `#cup`, `#land` 심볼을 다른 소재 그림으로 교체(창 모프 구조는 그대로)
- 카드 색 #F1EFEA, 벽 색 #E6E1D8, 액자 색 2종

## 원본 대조·보강 기록
남은 차이
- 원본에 있는 커피 뒤 사진 무드보드(3×3) 비트와 원형 렌즈 안 색보정 비트는 없음(여기선 스크럽 분할로 대체).
- 원본 풍경은 실사 사진 — SVG 일러스트로 근사.
이번에 바꾼 것
- 풍경 원근감 보강: 먼 능선 2겹(밝고 푸르고 대비 낮게)·중경 산의 햇빛면/그늘면·근경 어두운 언덕, 층 사이 안개(haze) 띠, 해 쪽 따뜻한 빛, 수면의 흐린 산 반사와 윤슬 그라데이션.
- 옅은 필름 그레인(feTurbulence, seed 고정, overlay 9%).
- 풍경이 카드를 채우는 동안 구름>먼 능선>중경>근경 순으로 다른 속도의 시차 이동.
- 금지 목록(크로스페이드·블러인·3D 플립·입자·글로·1초 넘는 정지) 준수 확인.
