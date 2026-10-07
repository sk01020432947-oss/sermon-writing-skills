# 터미널 비트 타이포 (Terminal Beat Typo · NO_KEYFRAMES)
원본: "NO_KEYFRAMES" 94 BPM 가사 영상 (ref-frames/03-terminal-beat-typo.jpg) · 재현(v1.mp4 4:45–5:19 전 구간 38.5초, 음악은 자체 합성)

## 한 문장 버전
94 BPM 곡에 맞춰 "started with a black screen… no keyframes, only code" 가사를 터미널·코드 에디터 느낌의 키네틱 타이포로 38.5초 만들어 줘. 검은 배경 #0E0F11, 미색 글자 #ECEBE4, 라임 #C8F031 한 색만 강조, 장면은 박자마다 컷, 마지막은 반전 카드 "NO KEYFRAMES".

## 구조 버전
<inputs>
- 가사: render() / RENDER / started with a BLACK SCREEN / and a BLINKING line / typed a little logic(); now the letters come alive / LETTERS / i don't drag a KEYFRAME / i don't BEND A CURVE / EVERY PIXEL on the screen is moving off a / watch it SPIN / SPLIT / ZOOM / CLOSE / SNAP BACK / UP STACK STACK STACK / FLIP it / then it GOES / SIXTY FRAMES / a second and i wrote EVERY ONE / hit RENDER / BOOM / ONE TAKE / and it's DONE. / NO KEYFRAMES / NO TIMELINE / ONLY code / LANDS RIGHT ON TIME / FRAME ×4 / NO KEYFRAMES / // 0 keyframes. 1 file. 60 fps.
- 1280x720, 38.5초(60박), 94 BPM(1박 = 0.6383초, 1마디 = 2.553초)
- 음악: music.wav(킥 1·3박, 스네어 2·4박, 하이햇 8분, 8분 베이스 Am–F–C–G, 장면 컷마다 짧은 신스 스탭, 최종 카드에 크래시+긴 화음)
</inputs>
<direction>
- 분위기: 개발자 터미널 + 뮤직비디오. 조용한 모노 타자 ↔ 화면을 꽉 채우는 굵은 대문자의 대비
- 색: 배경 #0E0F11, 글자 #ECEBE4, 강조 라임 #C8F031(커서 블록·취소선·하이라이트 박스·채워지는 칸), 보조 회색 #5D5F63
- 글꼴: 모노 IBM Plex Mono(타자·HUD), 큰 단어 Gmarket Sans TTF Bold 대문자
- 고정 HUD: 위 왼쪽 "■ NO_KEYFRAMES.JS", 위 오른쪽 "94 BPM  BAR 02.1 ●●○○"(마디·박 실시간), 아래 왼쪽 장면별 명령어 "> type("started with")", 아래 오른쪽 "F 0142  00:04:12" 프레임 카운터
- 커서는 라임 블록, 반 박마다 깜빡임
- 움직임 동사: 친다(타자) · 떨어진다 · 긋는다 · 찍힌다(도트) · 쪼개진다 · 튕긴다 · 미끄러진다 · 채운다 · 터진다 · 넘긴다(필름)
- 금지: 글리치처럼 보이는 반쪽 겹침·잔상, 그라디언트·그림자 장식, 라임 외 색, 박자 밖 컷, 페이드 전환(모두 하드 컷)
</direction>
<structure>
| 박 | 화면 | 움직임 |
|---|---|---|
| 0 | 줄번호 거터 + "$ render()" | 모노 타자, 라임 커서 |
| 2 | RENDER (R·E 라임) | 글자가 하나씩 떨어져 튕김 |
| 4 | "started with a" + BLACK / SCREEN | BLACK 글자가 기울어져 흩어 들어온 뒤 5박에 거의 검게 꺼지고, SCREEN이 올라오며 라임 선이 위를 긋는다 |
| 6 | "and a" + BLINKING + 라임 블록 커서 | 6.5박부터 반 박마다 단어 전체가 켜졌다 꺼짐 |
| 8 | 라임 가로선 + "line" | 선이 왼→오로 그어지고 끝에 라벨 |
| 9 | 에디터 "typed a little logic(); / now the / come alive" | 모노 타자 |
| 11 | LETTERS (L·T·S 라임) | 기울어진 채 떨어져 튕김 |
| 13 | "i don't drag a" + KEYFRAME | 라임 마름모 키프레임이 트랙에서 튕겨 이동, 14.2박 라임 취소선 |
| 15 | "i don't" + 그래프 BEND A CURVE | 핸들을 끌어 직선이 S자 이징 곡선으로 휘고, 글자가 곡선(textPath)을 타고 미끄러짐 |
| 17 | EVERY → EVERY / PIXEL 도트 매트릭스 + "on the screen is moving off a" | 꽉 찬 EVERY가 올라온 뒤 17.45박 라임 세로 스캔선이 왼→오로 지나가며 글자를 도트로 바꾸고, 18.3박 픽셀이 회전하며 오른쪽으로 흩어짐(구름이 남은 채 컷) |
| 19 | "watch it" + SPIN | 어두운 유령 단어 위로 단어가 −90° 회전해 세로로 섬, 잔상 2장이 40·90ms 늦게 따라 돌아 번짐 |
| 21 | SPLIT | 반 박 외곽선 유령 → 꽉 찬 단어 → 22박 라임 칼날 선 → 위 반쪽 왼쪽·아래 반쪽 오른쪽 60px, 홀드 |
| 23 | ZOOM | 유령 위 단어가 첫 O 중심으로 14배 확대되어 O 고리가 화면을 채움 |
| 24 | CLOSE | 화면 밖으로 잘린 초대형 단어, 1.12→1 |
| 25 | SNAP / BACK | SNAP 1.9배에서 착, 26박 BACK이 오른쪽에서 튕겨 들어옴 |
| 27 | UP(라임) + STACK ×4 | 8분음표마다 STACK이 위에서 떨어져 쌓임, 28박 더미가 왼쪽으로 비키고 FLIP이 X축으로 뒤집혀 섬 + "it" |
| 29 | "then it" GOES | 유령 위로 기울어진 채 미끄러져 들어옴 |
| 30 | 00→60 카운터 + SIXTY FRAMES · fps | 숫자와 60칸 눈금이 함께 차고 60에서 라임, 31박 FRAMES |
| 32 | "a second and i wrote" + 60칸 격자(칸마다 라임 점) | 칸이 라임으로 채워지고 33.25박 EVERY ONE(검은 외곽선) |
| 34 | "hit" + RENDER 버튼 | 35박 눌리며 라임으로 차고 진행 막대·frame 0000→2143 |
| 36 | BOOM (1박) | 라임 테두리 상자가 1.3→1로 조여 들고 단어가 펑 + 흔들림, 8–24px 픽셀 사각형 90개(시드) 사방으로 |
| 37 | ONE / TAKE + "1" 카드 | 줄마다 미끄러져 들어오고, 카드엔 외곽선 1이 먼저 있다가 38박 라임 1이 위에서 떨어져 튕김 |
| 40 | "and it's" DONE + 라임 마침표 사각형 + "// render complete" | 아래에서 올라옴 |
| 42 | NO [KEYFRAMES] + 편집기 타임라인(키프레임 점) | 라임 박스 펼침, 42.8박 키프레임 점이 차례로 사라지고 43.5박 KEYFRAMES 박스가 꺼져 NO만 남음 |
| 44 | NO TIMELINE + "$ rm -rf ./timeline" | 타자 후 "removed 4 tracks, 46 keyframes" |
| 46 | ONLY / code█ | 흐린 코드 위에 code 타자 + 큰 블록 커서 |
| 48 | LANDS / RIGHT ON TIME + 시간 눈금자 | LANDS가 떨어져 착지, 라임 밑줄, 라임 마커가 박에 맞춰 도착, RIGHT → ON TIME(TIME 라임) + offset 0.000 s |
| 50 | 필름 스트립 FRAME ×4 | 반 박마다 탁 넘김: 꽉 찬 → 외곽선 → 반전 → 라임 바탕 |
| 52 | NO / KEYFRAMES(S 라임) | 두 줄이 올라옴 |
| 53 | 반전 카드(미색 바탕) NO / KEYFRAMES | 반 박 간격으로 올라오고 54.5박 검은 취소선, 크래시 + 긴 화음 |
| 56–60 | "// 0 keyframes. 1 file. 60 fps." / "// written in code" | 타자 후 끝까지 홀드 |
</structure>
<build>
HTML 한 파일, 하네스(stage.css/stage.js), GSAP 타임라인. 시계 프록시 하나(`clock.t` 0→38.5, ease none)의 onUpdate에서 장면 표시·HUD·타자·커서 깜빡임을 시간 함수로 계산 → seek 결정론. 컷 시각은 `at(박)` = 박 × 60/94. 타자 요소는 `data-b`(시작 박)·`data-cps`. 음악은 python3 표준 라이브러리로 38.5초 합성(킥 1·3박, 스네어 2·4박, 8분 하이햇, 8분 베이스 Am–F–C–G, 마디마다 패드, 모든 컷에 짧은 스퀘어 스탭, 53박 크래시+긴 화음, 56박부터 드럼 멈춤). 30fps 렌더 후 `ffmpeg -i clip.mp4 -i music.wav -c:v copy -c:a aac -shortest clip_audio.mp4`.
</build>

## 바꿔 쓰기 포인트 (소재만 교체할 자리)
- `SC` 배열: [시작 박, 아래 명령어] — 가사 줄과 컷 위치를 여기서만 바꾼다(섹션 순서와 1:1, 하네스의 `.blk` 클래스명은 피한다)
- 각 `<section>`의 큰 단어와 `data-ty`(타자 문구), `data-b`(시작 박), `data-cps`(초당 글자수)
- BPM 변경 시 `B = 60/BPM`과 synth 스크립트의 B 함께 수정
- 라임 #C8F031 → 다른 형광 한 색. 최종 반전 카드 문구가 곡의 훅

## 원본 대조·보강 기록
대조: v1.mp4 4:45–5:19를 2fps·6fps로 뽑아 clip.mp4와 나란히 봄(2026-10-04).

남은 차이
- 원본 큰 글자는 아주 넓은 익스텐디드 그로테스크다. 설치 글꼴에 없어 Gmarket Sans Bold를 가로 1.12배·외곽선 0.016em으로 넓고 두껍게 흉내 냈다(폭이 아직 원본보다 좁음).
- 원본은 장면이 1–1.5박으로 더 빠듯해 전체가 약 33초다. 이 샘플은 2박 격자를 유지해 38.5초다(음악·가사 박자 구조를 지키려고 의도적으로 유지).
- 원본 RENDER는 타자된 "render()" 자리에서 큰 글자로 바뀌는 매치 컷이고 LETTERS는 에디터 아래에 같이 뜬다. 여기는 하드 컷 후 낙하다.
- 원본 NO KEYFRAMES는 KEY 글자가 라임으로 스크램블되며 타자된다. 여기는 라임 상자가 펼쳐진다.

이번에 바꾼 것
- 큰 단어 전체를 넓고 두껍게(`.W`에 `scale:1.12 1`, 획 0.016em), 넘치는 장면(BLINKING·LETTERS·BACK·BOOM·NO KEYFRAMES 상자·최종 KEYFRAMES)은 크기·위치를 다시 맞춤
- 모노 타자 글자를 원본 비율에 맞춰 1.3–1.4배 키움(30→42px, 에디터 36→48px, 줄 강조·거터 간격도 같이)
- EVERY PIXEL: 꽉 찬 EVERY → 라임 스캔선이 도트로 바꾸는 매치 전환, x좌표 기반 스태거, 흩어짐을 짧고 남게 바꿔 18.8박의 빈 화면 제거
- SPIN: 40·90ms 지연 잔상 2장으로 원본의 회전 번짐(후속 동작) 재현
- STACK: 위에서 300px 관통 낙하 → 70px 짧은 착지(power4.out)로 겹침 감소
- BOOM 1박으로 줄이고 원본의 라임 테두리 상자 추가, ONE TAKE를 37박으로 당기고 외곽선 "1" 고스트 → 라임 1 낙하
- DONE: 라임 마침표 사각형이 41박에 위에서 떨어져 튕겨 자리 잡음(원본)
- 아웃트로 둘째 줄을 57.4박으로 당겨 마지막 홀드 1.2초 확보
- 음악: `scripts/synth_music_94bpm_38s.py`의 CUTS 38→37, 36박 BOOM 크래시 추가 후 music.wav 재합성·clip_audio.mp4 재먹싱
