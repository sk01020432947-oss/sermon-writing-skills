# 09 한 도형 UI 모프 (One-shape UI Morph)
원본: YouTube 영상 속 "드리블 수준 UI 모션" 시연 결과 · 재현

## 한 문장 버전
원문(영어 스타일):
> Make a Dribbble-level UI motion piece: one single element that never cuts — a "Connect" button that a cursor clicks, then it morphs into a loader, a success check, a dynamic-island music player, a volume slider, a segmented control, a toggle, a command palette and a toast, and finally collapses back into the button. Springy, something happens on every beat at 120 BPM.

한국어:
> 컷 없이 요소 하나가 계속 모양을 바꾸는 드리블급 UI 모션을 만들어줘. 커서가 "Connect" 버튼을 누르면 로더 → 체크 → 다이내믹 아일랜드 음악 플레이어 → 볼륨 슬라이더 → 탭 → 토글 → 커맨드 팔레트 → 토스트로 변했다가 다시 버튼으로 돌아온다. 스프링 느낌, 120BPM 박자마다 뭔가 일어나게.

## 구조 버전
<inputs>
문구: Connect / Afterimage · Nightshift · 1:12 · -1:56 / Day Week Month / Sh → Share track, Shuffle, Show lyrics / Link copied
비율 1080x1080 · 16초 · 무음
</inputs>
<direction>
바깥 검정, 가운데 크림 카드 #EDEAE4(940px, 모서리 48px). 요소는 단 하나(#el)이고 폭·높이·모서리·배경색·그림자만 바뀐다. 상태 바뀔 때마다 0.1초 블러(5px) 펄스 + back.out(1.5) 스프링(작은 오버슛). 내부 내용은 0.9→1 스케일로 튀어 들어옴.
색: 흰 #FFF, 먹 #111/#0E0E0F, 성공 #2DB55D, 주황 #F2552C, 파랑 #3B6BFF, 토글 꺼짐 #CFCBC4. 글꼴 Pretendard 600~700.
커서(macOS 화살표)가 모든 변화를 일으킨다: 실제 클릭(커서 0.82 축소 + 요소 0.94 눌림), 실제 드래그.
금지: 장면 컷, 요소 교체(새 박스 등장), 박자 밖의 변화, 선형 이징.
</direction>
<structure>
| 초 | 상태 | 움직임 |
|---|---|---|
| 0–1.25 | 흰 알약 버튼 Connect | 커서 진입, 1.0 클릭·눌림 |
| 1.25–2.5 | 검정 원 로더 | 스피너 2회전 |
| 2.5–3.5 | 초록 원 | 체크 획이 그려지고 한 번 통통 |
| 3.5–5.5 | 다이내믹 아일랜드 플레이어 560×150 | 앨범아트·제목·이퀄라이저·일시정지, 진행바 1:12에서 흐름 |
| 5.0–6.5 | 스크럽 | 커서가 노브를 잡고 75%까지 드래그, 시간 숫자 갱신 |
| 6.75–8.0 | 흰 볼륨 슬라이더 | 커서를 놓지 않은 채 이어서 좌→우 드래그 |
| 8.0–9.5 | 세그먼트 탭 | Week(8.5), Month(9.0) 클릭, 검정 표시자가 늘었다 줄며 미끄러짐 |
| 9.5–10.5 | 토글 | 10.0 클릭, 노브가 늘어나며 이동, 회색→주황 |
| 10.5–12.25 | 커맨드 팔레트 580×320 | "S","h" 타이핑, 결과 3줄 스태거, Share track 클릭(↵ 강조) |
| 12.25–13.5 | 토스트 Link copied ✓ | 아래에서 튀어오름 |
| 13.5–16 | 버튼으로 복귀 | 커서가 버튼 위로 돌아와 호버(1.03), 홀드 |
</structure>
<build>
HTML 한 파일, GSAP 타임라인 seek, 30fps 렌더, 결정론. morph(t, 박스속성, 내용레이어) 헬퍼 하나로 모든 상태 전환, 커서는 mv()/click() 헬퍼. 진행바·볼륨은 프록시 값 onUpdate.
</build>

## 바꿔 쓰기 포인트 (소재만 교체할 자리)
- 상태 순서·박자: `morph(시각, {width,height,borderRadius,backgroundColor}, '#L번호')` 호출 목록
- 곡명·아티스트·길이(`TOTAL`), 탭 라벨, 팔레트 검색어·결과, 토스트 문구
- 강조색 #F2552C 일괄 교체

## 원본 대조·보강 기록
원본: V2 4:15–4:45 결과 화면(크림 카드 위 단일 요소 모프)과 1:53–4:15 프롬프트 설명(탭 표시자 두 모서리 다른 스프링, 볼륨 최대치 넘김 늘어남, 스스로 그려지는 차트+툴팁).

이번에 바꾼 것
- 요소 전체를 `#zoom` 래퍼로 1.15배(원본 대비 약 15% 작던 크기 보정). 커서도 같은 래퍼 안이라 좌표 그대로.
- 원본 순서로 재배열: 버튼 → 로더 → 체크 → **Connected 알약(새로 추가)** → 플레이어 → 볼륨 → 토글 → 탭 → **차트 카드(새로 추가)** → 팔레트 → 토스트 → 버튼. 길이 16→17초.
- 탭 표시자: 왼쪽·오른쪽 모서리를 프록시 `{l,r}`로 분리, 앞 모서리 back.out(2.2) 0.38초, 뒤 모서리 80ms 늦게 back.out(1.1) 0.6초 → 액체처럼 늘었다 따라붙음. Day→Week→Month→Week 세 번.
- 볼륨: 최대치 도달 뒤 커서가 90px 더 끌면 트랙·요소가 40px 고무줄처럼 늘어나고 노브가 눌려 납작해짐, 놓으면 elastic.out으로 복귀.
- 차트: Week 탭이 600×400 카드로 펼쳐지고 14h 25m 카운트업, Catmull-Rom 곡선이 1초간 그려진 뒤 커서가 목요일 점에 머물면 점선·점·툴팁 "Thu · 3h 05m"이 튀어나옴.

남은 차이
- 원본은 탭이 카드 상단으로 그대로 이어지는 연속 변형이지만 여기서는 블러 펄스 교차(레이어 교체)로 처리.
- 원본 결과물 뒤에 붙은 다른 쇼릴(주황 MAKE 타이포·3D 오브젝트)은 범위 밖이라 넣지 않음.
