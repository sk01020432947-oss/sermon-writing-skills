# 프롬프트 체계 — Vox 종이 콜라주

영상(원카AI)이 보여 준 "목적 한 줄 + 고정 제작법" 구조를 이 스킬용으로 **새로 쓴** 지침이다(원문 복제 아님).
Claude에게 그대로 붙이거나, 블록 몇 개만 골라 붙인다(P8: 모션·변주만 떼어 써도 된다).

## 1. 목적 한 줄 (매번 바뀌는 부분)

```
<주제>에 관한 Vox 스타일 인트로를 <길이>초로 만들어줘. 이미지는 <로컬 Qwen | Higgsfield MCP Nano Banana 2>로
요소만 만들고, 영상은 vox-paper-motion(vox_compose / vox_sequence)으로 조립해. 아래 제작법을 따르고,
생성 전에 장면 계획과 비용(또는 시간) 견적을 먼저 보여 줘.
```

## 2. 고정 제작법 (한국어)

**목표** — 손으로 오려 붙여 사진 찍은 인쇄물 같은 다큐 제목·간지 체계. 깨끗한 디지털 모션그래픽이 아니다. 사람·물건·건물·동물·문서·지도 어떤 주제에도 맞아야 하고, 사람이 없는 장면에 사람을 가정하지 않는다.

**팔레트** — 네 값만: 먹색, 따뜻한 종이색, 중간 회색, 주홍 하나. 순백은 쓰지 않는다. 주홍은 주인공에게만. 나머지는 먹·종이·회색이라 눈이 글보다 주인공에 먼저 간다.

**주인공** — 장면마다 주인공은 하나, 강조색을 가질 수 있는 것도 그것 하나. 강조는 셋 중 하나만(장면마다 seed가 고름): ① 듀오톤(그림자 먹, 밝은 곳 주홍) ② 주인공 바로 뒤 평평한 주홍 판 ③ 주인공을 정의하는 한 부분만 주홍(케이블카 객실, 책 표지, 겉옷). 조연은 크거나 가까워도 강조색 금지. 두 곳이 색을 원하면 주인공이 둘이니 다시 구성.

**소재 준비** — 받은 이미지는 모두 로컬 배경 제거 스크립트를 거친다(일괄 처리 가능). 조연은 배경 없이 흑백으로, 주인공도 흑백으로 만든 뒤 강조를 얹는다. 흑백 뒤 밝게 읽히는 소재는 종이 바탕에 묻히므로 중간 회색 판을 댄다. 소재 생성 시 흰색·크림색 옷/물건을 피한다.

**변주** — chaos(0~1) 하나가 위치·회전·크기·자르기·가장자리·활자 흔들림·배경 흩뿌림·질감 오프셋과 투명도를 함께 움직인다. 0은 반듯, 1은 겨우 버팀. seed와 짝을 지어 기본은 빌드마다 새 seed. 같은 seed와 chaos는 반드시 같은 프레임 — 좋은 우연을 다시 뽑을 수 있게.

**글자** — 굵은 세리프 제목을 주인공 위에 두되 윗가장자리와 맞물리게(사람이면 머리, 건물이면 지붕선). 아래 얇은 설명 줄로 굵기 대비, 한 덩어리로 움직인다. 글자는 먹/종이색, 제목 단어가 곧 주인공일 때만 강조색. chaos만큼 어절 기준선·회전을 흔들되 읽기 줄은 깨지지 않게.

**배경** — 주인공 뒤로 찢은 신문 조각을 낮은 대비로, seed 배치. 분위기일 뿐 읽히지 않게. 지도·평면 장면에서는 뺀다.

**모션** — 배경·주인공·전경 조각 평면 사이로 2.5D 카메라가 지나가며 실제 패럴랙스. 죽은 정지 없이 느리게 계속 흐르다가 박자에서만 결정적으로 밀거나 뺀다. 푸시인은 주인공에 착지. 등장은 지수 감속 + 작은 오버슈트 후 정착, 여러 요소는 시간차, 주인공이 마지막. 흐림은 둘로 나눈다: 깊이용 초점 흐림, 속도용 방향 블러 — 서로 대신 쓰지 않는다.

**질감·마감** — 그림자·중간톤에만 고해상 망점(밝은 곳은 깨끗하게, 강조 영역 제외), 약한 복사기 열화, 가장자리 색수차 아주 약하게, 부드러운 초점 비네트. 빛샘은 전환에만.

**확장(이 스킬)** — 2프레임 홀드로 스톱모션 손맛. 가로·세로 동시 출력, 세로는 아래 20%·오른쪽 버튼 자리 비우고 동기 캡션. 연도는 "경", 경로는 "예시", 성경 장절은 사용 번역본 대조.

## 3. Fixed system (English, for image/video models or English-speaking agents)

Goal: an analog title-and-interstitial system for documentary explainers — printed matter cut by hand, arranged, and photographed; not slick digital motion. Works for any subject; never assume a person when none is present.
Palette: four values only — ink black, warm off-white paper, mid grey, one red-orange accent. No pure white. The accent belongs to the single hero of each frame.
Hero: one per composition, the only element allowed to carry the accent, via exactly one method chosen per build by the seed — duotone, flat accent card behind the hero, or selective recolor of the one defining part. Supporting elements stay ink/paper/grey.
Subject prep: every supplied image goes through a scriptable local background-removal step; supporting layers come out cut-out and black-and-white; the hero is cut-out and black-and-white before its accent; light-reading subjects get a mid-grey card.
Variation: one chaos control 0–1 drives position, rotation, scale, crop, edge, type jitter, background scatter and texture offset/opacity; paired with a seed; same seed + chaos must reproduce the identical frame.
Typography: bold editorial serif title interlocking with the hero's top edge, thin descriptor line beneath, animated as one unit; type in ink or paper; per-word baseline/rotation offsets scaled by chaos, never breaking the reading line.
Background: low-contrast torn newspaper fragments placed by the seed, illegible on purpose.
Motion: 2.5D camera through layered planes with real parallax; slow continuous drift with no dead holds; decisive push-in or pull-back on beats, landing on the hero; ease-out expo entrances with a small overshoot; staggered entrances, hero last; focal defocus for depth and directional blur for velocity, kept separate.
Finish: halftone gated to shadows and midtones (hero accent kept clean), light xerox degradation, restrained edge chromatic aberration, soft vignette, occasional light leak on transitions only.

## 4. 소재 이미지 프롬프트 (생성 모델용)

공통 꼬리
```
flat colored paper cutout collage, torn paper edges, visible paper fiber texture, Vox documentary style, no text
```
판화·신문 양식으로 갈 때
```
vintage black and white engraving illustration, cross-hatched ink lines, old book print, no text
```
주인공·물건 (배경 제거용)
```
<대상>, full body, <방향> view, <양식 꼬리>, saturated colors (no white or cream clothing), isolated on a plain pure white background, no shadow, no text
```
배경 (1장 고정)
```
<장소> wide view, no people, layered depth (far hills, middle, foreground), <양식 꼬리>
```
프레임 순환 (첫 장을 참고 이미지로)
```
same character as the reference image, identical style and colors, only the pose changes: <동작 단계 1/5 … 5/5>, isolated on a plain pure white background
```
세로판 배경은 처음부터 세로로(720×1280) — 가로 그림을 세로로 늘리면 3배 넘게 확대돼 흐려진다.

## 5. 음악 프롬프트 (Suno 등)

생성 음악은 10~20초를 정확히 못 맞춘다 → **구간 순서만 유도해 길게 뽑고, 큐 두 개에 맞춰 자른다**.

스타일 칸 (예: 다큐 인트로, 가사 없음)
```
Instrumental cinematic documentary intro, <BPM> BPM, warm analog textures, soft piano and plucked strings,
light percussion, paper and tape foley accents, starts immediately, short swell into one clear impact hit,
gentle ringing tail, restrained, no vocals
```
가사 칸 (구간 지시)
```
[Instrumental]
[Intro - 1 bar, light pulse, plucked strings]
[Break - 1 bar, drop out, tape slow-down, low drone]
[Build - 1 bar, rising swell, ticking percussion]
[Drop - one clear impact on the downbeat, bright bell]
[Outro - ringing tail, fade out, end]
```
설정: Custom · Instrumental 켬 · 제외 스타일 `vocals, choir, lo-fi` · 한 번에 2곡 → 골라 쓰기.
큐 맞추기: 영상의 강박 시각(예: 제목 착지 5.3초)과 곡의 임팩트 시각을 재서 `music.offset = 곡임팩트초 − 영상강박초`.
예배·교회용은 저작권 문제 없는 생성곡/보유 음원만. 생성 서비스의 상업 이용 조건은 요금제마다 다르니 확인.
