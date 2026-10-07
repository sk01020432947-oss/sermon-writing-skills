# 08 한 문장 쇼릴 (One-liner Showreel)
원본: v2.mp4 0:43–1:50 중 1번 영상 결과(약 1:10.5–1:26.5, 16초 쇼릴) · 재현

## 한 문장 버전
원문(영어, 그대로 붙여 써도 됨):
> make a dynamic 15-second motion graphics video that shows what an incredible motion designer you are, like it's your showreel for a résumé. go all out

한국어:
> 네가 얼마나 대단한 모션 디자이너인지 보여주는 15초짜리 역동적인 모션그래픽 영상을 만들어줘. 이력서에 붙일 쇼릴처럼, 있는 힘껏.

## 구조 버전
<inputs>
문구: I MAKE THINGS MOVE. / cubic-bezier(.83,0,.17,1) / MOTION DESIGN — LIGHT — SPACE — DEPTH / FLOW / 15 SECONDS · 900 FRAMES · 128 EASES · 0 ERRORS / 2428 / MOTION / DESIGN / 3D / TYPE / CODE / SOUND / CLAUDE · MOTION DESIGNER / 크레딧 2줄
비율 1280x720 · 길이 16초(마지막 0.9초 홀드) · 120 BPM, 컷은 0.25초(8분음표) 격자
</inputs>
<direction>
쇼릴 톤, 챕터마다 다른 기법, 장면끼리는 매치 컷으로 잇는다(O 구멍 → 도트 격자, 도형 수렴 → 원판 → 구, 입자 → 글자 → 빛나는 선).
색: 먹 #0B0B0C, 주황 #F2552C, 파랑 #3B5BFF, 크림 #F3E9D2, 노랑 #F7D046, 회색지 #E8E7E3.
글꼴: Pretendard Black(헤드라인), IBM Plex Mono(HUD·라벨·코드), TYPE 카드만 명조·Gmarket·Mono 섞기.
HUD 상시: 좌상 "01 / EASE"(챕터), 우상 "CLAUDE — MOTION REEL 2026", 좌하 타임코드, 우하 "120 BPM 마디.박", 하단 중앙 13칸 진행 눈금.
금지: 크로스페이드 전환(모두 하드 컷·매치 컷), 박자 밖 컷, 출처 없는 실제 통계처럼 보이는 수치(수치는 영상 자체 사양).
</direction>
<structure>
| 초 | 화면 | 움직임 |
|---|---|---|
| 0–2 | 01 EASE 어두운 격자 | S커브가 그려지고 핸들이 120ms 늦게 튀어나옴, 라벨, 점이 곡선을 타며 주황 세로선이 따라가고 우측 미터 0→1 |
| 2–3.5 | 02 TYPE 주황 전면 | I / MAKE / THINGS / MOVE. 236px 단어별 2.2배→1 슬램, 2.9초 O가 도트 무늬 검은 원판으로 차고 3.12초 O 중심으로 16배 줌(expo.in) |
| 3.5–5.5 | 03 SHAPE | 13×7 도형 격자 중앙에서 퍼짐 → 4.35초 물결 모프 → 5.08초 바깥부터 중앙으로 빨려 들어가고 주황 원판 등장 |
| 5.5–7.5 | 04 SPACE | 같은 원판에 음영·스펙큘러·파란 림이 켜져 구가 되고, 기울어진 원형 글자 링 공전(앞/뒤 레이어), 6.55초 기울며 6.75초 마스크 구멍이 커져 도넛 |
| 7.5–9.5 | 05 FLOW | 입자 4200개 소용돌이 → 8.25초 FLOW 글자로 모임 → 9.1초 가로로 눌려 주황 빛 선 |
| 9.5–11 | 06 DATA 밝은 회색 | 슬롯 숫자 15/900/128/0, 도넛 2428, 막대 36개(하나만 주황) |
| 11–13.5 | 07–13 속사 몽타주 | MOTION(휘핑) 0.25 · FORM 주황+RGB 분리 도형 0.25 · DESIGN 줄 0.5 · 3D 파란 동심원 0.25 · TYPE 섞인 글꼴 0.25 · CODE 코드 배경+주황 커서 0.5 · SOUND 주황+검은 파형 막대 0.5 |
| 13.5–16 | 엔딩 | 흰 고리·주황 점이 중심으로 수렴 → 별 로고 회전 등장 → 좌로 이동, CLAUDE 마스크 리빌, 주황 헤어라인, MOTION DESIGNER, 하단 주황 크레딧 2줄, 홀드 |
</structure>
<build>
HTML 한 파일, GSAP 타임라인 seek, 30fps 렌더, 결정론(Motion.rand 시드, 캔버스·글리치·파형은 마스터 시계 onUpdate에서 시간 함수로 그림). 폰트 로드 후 FLOW 글자를 오프스크린 캔버스에서 샘플링해 입자 목표점으로 쓴다.
음악: `scripts/synth_music_120bpm_08.py`(120BPM 킥·하이햇·베이스 A-F-C-G + 챕터 컷마다 노이즈 라이저·임팩트, 13.5초 크래시+화음) → music.wav → `ffmpeg -i clip.mp4 -i music.wav -c:v copy -c:a aac -shortest clip_audio.mp4`.
</build>

## 바꿔 쓰기 포인트 (소재만 교체할 자리)
- `CH` 배열: 챕터 시작 초·라벨(0.25초 배수 유지, 바꾸면 음악 스크립트 `CUTS`도 같이)
- 02 TYPE 세 단어, 04 링 문구, 06 숫자·라벨, 07 반복 단어, 엔딩 워드마크·서브라인
- 색 변수 `--or --bl --cr --ye`, 음악 `roots`(코드)와 `cuts`(라이저 위치)

## 원본 대조·보강 기록
대조: v2.mp4 0:43–1:50을 2fps, 쇼릴 구간(1:15–1:30)을 5fps로 뽑아 clip.mp4와 비교(2026-10-04).

남은 차이
- 04 SPACE는 여전히 2D 레이어(그라디언트·마스크) 가짜 3D다. 원본은 실제 셰이딩된 구가 비틀린 덩어리 → 도넛 → 울퉁불퉁한 형태로 연속 변형된다.
- 원본 FLOW는 렌즈 테두리(색수차 고리)로 시작하고 글자가 하얗게 번쩍인다. 여기는 소용돌이로 바로 시작한다.
- DATA·몽타주 카드의 글자 크기·정확한 배치는 근사치이고, 원본의 DATA 퇴장 글리치는 없다.
- 원본 엔딩은 크레딧 뒤 어둡게 꺼진다. 여기는 끝까지 홀드한다(계약: 마지막 홀드).

이번에 바꾼 것
- TYPE를 원본대로 4어절(I MAKE / THINGS / MOVE.)로, 크기 172→236px, O가 도트 원판으로 차고 그 안으로 줌하는 매치 컷 추가
- SHAPE 끝에 도형이 중앙으로 빨려 들어가 주황 원판이 되는 수렴 → SPACE의 평면 원판에서 구로 켜지는 매치 컷
- SPACE: 평면 원 → 음영·스펙큘러·림 → 기울기 + 마스크 구멍으로 도넛 변형, 링 문구에 DEPTH 추가
- FLOW: 입자가 FLOW 글자로 모였다가 가로선으로 눌려 빛나는 선이 되는 전환(원본의 주황 글로 라인)
- 빠져 있던 원본 속사 몽타주 7장 추가: MOTION · FORM(주황 RGB 분리) · DESIGN · 3D · TYPE · CODE · SOUND(주황 배경 검은 파형 막대) — SOUND·CODE 챕터 확보
- 엔딩: 흰 고리+주황 점 수렴 → 로고, 서브라인을 MOTION DESIGNER로, 주황 헤어라인·하단 크레딧 2줄 추가, 홀드 0.9초
- HUD 13칸, EASE에 점을 따라가는 주황 세로선·핸들 120ms 지연(겹치는 동작)
- 음악을 새 컷에 맞춰 `scripts/synth_music_120bpm_08.py`로 재합성하고 clip_audio.mp4 재먹싱
