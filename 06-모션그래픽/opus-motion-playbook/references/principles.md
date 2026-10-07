# 원리 74 — opus-motion-playbook

정본은 principles.json. 이 파일과 HTML 도감은 `scripts/build.py`가 생성한다.

## 출처

- **V1** [Claude로 15초 모션그래픽 만들기｜Opus 5.5 프로젝트 완벽 가이드](https://www.youtube.com/watch?v=jv8MtZ-T1iw) — GPT PARK의 AI팩트. 프로젝트 지침 8섹션 저장 → 출처 주고 요청 → 문구·디자인 검증 → 128BPM 박자 동기 렌더 → 자가검수
- **V2** [Claude랑 ChatGPT만으로 이런 모션그래픽이? 따로 툴도 플러그인도 없이](https://www.youtube.com/watch?v=RKK9aWedELs) — 닥또리. MCP 없이 기본 기능만. 영상 첨부 시 Claude는 분위기를 먼저 묻는다. 채팅은 코드, Cowork는 실제 영상 파일
- **V3** [클로드 오퍼스 5.5의 미친 모션그래픽 방법 총정리](https://www.youtube.com/watch?v=NE306sbvopY) — 성공지식백과. ① Higgsfield + After Effects 플러그인으로 AE를 직접 조작 ② AE 없이 생성 에셋 + Remotion/HyperFrames로 조립
- **V4** [클로드 Opus 5.5 영상 자동화 실전 | 모션그래픽 광고·예고편·3D 제작 × Higgsfield](https://www.youtube.com/watch?v=UcAbZwtEfbk) — Dante's Datalab. 같은 프롬프트를 코드 단독 / Higgsfield 연결로 두 번씩 제작해 시간·토큰·크레딧 실측 비교
- **V5** [클로드로 만든 영상, 이 정도까지 왔습니다 | Opus 5.5](https://www.youtube.com/watch?v=yFxZNHWyIMs) — 구름모찌. X에 공개된 Opus 5.5 작품 13편의 연출 원리 해설
- **R** [opus-video-prompts (V4 설명란 연결 저장소)](https://github.com/dandacompany/opus-video-prompts) — 단테랩스 번역 · 샹양차오무 정리. 프롬프트 17개 · 공개 사례 53건 · 제작 방식 9가지
- **P** [PDoomVideo ANIMATION_GUIDE (R의 작성 요령이 참조)](https://github.com/JohnHeibel/PDoomVideo/blob/main/ANIMATION_GUIDE.md) — JohnHeibel. 156.6초 수채화 뮤직비디오를 seek(t) 순수함수로 병렬 렌더한 규칙서

## A. 작업 흐름

### A1 영상은 시간에 따라 바뀌는 그림이다

Opus는 영상 파일을 직접 만들지 않는다. HTML·JavaScript·Python으로 장면을 그리고 프레임마다 저장해 FFmpeg로 묶는다. 그래서 '어느 시점에 무엇이 어디에 얼마나 크게'를 숫자로 정할 수 있는 것은 모두 영상이 된다.

- 프롬프트: `코드로 장면을 그리고 프레임을 캡처해 MP4(1920×1080, 30fps, AAC 스테레오)로 렌더해 줘.`
- 응용: 슬라이드·주보·연표처럼 이미 있는 정보 화면은 전부 움직이는 영상 재료다.
- 출처: [V4 1:29](https://www.youtube.com/watch?v=UcAbZwtEfbk&t=89s) · [V5 7:40](https://www.youtube.com/watch?v=yFxZNHWyIMs&t=460s)
- 원본 장면: [V5 7:50](https://www.youtube.com/watch?v=yFxZNHWyIMs&t=470s) → `~/Desktop/cysjavis/모션그래픽/오퍼스_모션원리_도감_자료/frames/A1.jpg`

### A2 고정 규칙은 지침에, 바뀌는 값은 메시지에

Claude 프로젝트 맞춤 지침에 8섹션(정보 범위·비주얼 시스템·음악·박자 동기·장면 구성·기술 사양·품질 검증·목표 수준)을 한 번 저장한다. 원본 지침은 고치지 않고 영상마다 출처·색 같은 변수만 채팅으로 준다.

- 프롬프트: `프로젝트 지침은 그대로 두고 이번 영상 변수만 줄게: 출처=…, 색=…, 길이=15초.`
- 응용: 설교 인트로·주보 광고처럼 매주 반복되는 영상은 프로젝트 하나에 모아 둔다.
- 출처: [V1 3:11](https://www.youtube.com/watch?v=jv8MtZ-T1iw&t=191s) · [V1 3:59](https://www.youtube.com/watch?v=jv8MtZ-T1iw&t=239s)
- 원본 장면: [V1 3:20](https://www.youtube.com/watch?v=jv8MtZ-T1iw&t=200s) → `~/Desktop/cysjavis/모션그래픽/오퍼스_모션원리_도감_자료/frames/A2.jpg`

### A3 첫 메시지의 핵심은 출처

이름만 주면 Claude가 근거를 직접 찾아야 해서 느리고 틀리기 쉽다. 공식 URL이나 소개 글을 주면 화면 문구가 정확해지고 검증이 빨라진다. 지침 1번 '제공된 출처만 쓰고 데이터를 지어내지 않는다'와 짝을 이룬다.

- 프롬프트: `출처는 이 URL과 첨부 문서뿐이야. 여기 없는 수치·문구는 만들지 마.`
- 응용: 교회 소개 영상은 홈페이지·요람 PDF를 출처로 준다.
- 출처: [V1 4:09](https://www.youtube.com/watch?v=jv8MtZ-T1iw&t=249s) · [V1 3:16](https://www.youtube.com/watch?v=jv8MtZ-T1iw&t=196s)
- 원본 장면: [V1 4:15](https://www.youtube.com/watch?v=jv8MtZ-T1iw&t=255s) → `~/Desktop/cysjavis/모션그래픽/오퍼스_모션원리_도감_자료/frames/A3.jpg`

### A4 제작 전 검증 관문

바로 만들지 않고 ① 화면 문구를 출처와 함께 표로 정리하고 ② 팔레트·글꼴·도형·모션 스타일을 근거와 함께 제안한다. 사용자가 창작 문구와 사진·로고 사용 여부를 확인하고 '진행'이라고 하면 그다음부터는 묻지 않고 끝까지 만든다. 품질은 이 단계에서 정해진다.

- 프롬프트: `코드 작성 전에 화면 문구 표(문구·출처)와 디자인 제안(색·글꼴·도형·모션, 근거 포함)을 먼저 보여 주고 승인을 기다려.`
- 응용: 주보·광고처럼 오탈자가 치명적인 영상에 반드시 넣는다.
- 출처: [V1 4:27](https://www.youtube.com/watch?v=jv8MtZ-T1iw&t=267s) · [V1 4:50](https://www.youtube.com/watch?v=jv8MtZ-T1iw&t=290s)
- 원본 장면: [V1 4:34](https://www.youtube.com/watch?v=jv8MtZ-T1iw&t=274s) → `~/Desktop/cysjavis/모션그래픽/오퍼스_모션원리_도감_자료/frames/A4.jpg`

### A5 스토리보드·박자표 먼저

장면이나 박자표를 먼저 확인하고 코드를 쓰면 특정 장면만 다시 고치기 쉽다. R의 상세 템플릿은 모두 '코드 전에 입력값을 묻고 박자표 위에 상태 목록을 보여 줘'로 끝난다. V4에서 Opus는 렌더 전에 장면 16칸 스토리보드 시트를 스스로 만들어 보여 줬다.

- 프롬프트: `코드를 쓰기 전에 모든 시점을 박자표에 맞춘 스토리보드를 보여 줘.`
- 응용: scripts/beatgrid.py --scenes N 으로 장면표 뼈대를 먼저 뽑는다.
- 출처: [R](https://github.com/dandacompany/opus-video-prompts) · [V4 4:32](https://www.youtube.com/watch?v=UcAbZwtEfbk&t=272s)
- 원본 장면: [V4 4:34](https://www.youtube.com/watch?v=UcAbZwtEfbk&t=274s) → `~/Desktop/cysjavis/모션그래픽/오퍼스_모션원리_도감_자료/frames/A5.jpg`

### A6 프롬프트도 Opus에게 쓰게 한다

직접 프롬프트를 짜기보다 '이런 모션그래픽을 만들 프롬프트를 짜 줘'라고 맡기면 장면별로 훨씬 상세한 프롬프트를 쓴다. 그 프롬프트를 복사할 필요 없이 같은 대화에서 바로 제작을 이어 간다.

- 프롬프트: `3D 메카 체스말이 싸우는 모션그래픽을 만들 거야. 먼저 장면별 제작 프롬프트를 상세히 짜고, 이어서 그대로 제작해 줘.`
- 응용: 아이디어만 있을 때 1단계는 항상 메타 프롬프팅.
- 출처: [V3 1:44](https://www.youtube.com/watch?v=NE306sbvopY&t=104s) · [V3 2:16](https://www.youtube.com/watch?v=NE306sbvopY&t=136s)
- 원본 장면: [V3 2:02](https://www.youtube.com/watch?v=NE306sbvopY&t=122s) → `~/Desktop/cysjavis/모션그래픽/오퍼스_모션원리_도감_자료/frames/A6.jpg`

### A7 글보다 참고 미디어

텍스트만 주는 것보다 사진·영상을 함께 주면 품질이 확연히 좋아진다. 참고 영상을 보여 주고 '내 제품을 이렇게 설명해 줘'라고 하면 움직임에 목적이 생긴다.

- 프롬프트: `첨부한 참고 영상의 구조와 리듬만 빌려서, 주제는 내 서비스(설명 첨부)로 바꿔 만들어 줘.`
- 응용: watch 스킬로 참고 영상 프레임을 뽑아 함께 준다.
- 출처: [V2 4:21](https://www.youtube.com/watch?v=RKK9aWedELs&t=261s) · [V5 2:00](https://www.youtube.com/watch?v=yFxZNHWyIMs&t=120s)
- 원본 장면: [V5 2:05](https://www.youtube.com/watch?v=yFxZNHWyIMs&t=125s) → `~/Desktop/cysjavis/모션그래픽/오퍼스_모션원리_도감_자료/frames/A7.jpg`

### A8 분위기를 먼저 정한다

영상을 주면 Claude는 클립을 잘라 분석한 뒤 원하는 분위기(시네마틱 등)와 용도(쇼츠 인트로 등)를 먼저 묻는다. 묻지 않고 바로 만드는 도구보다 결과가 좋았고, 대신 시간은 약 3배(15분) 걸렸다.

- 프롬프트: `먼저 분위기 후보 3개와 용도를 제안해 줘. 내가 고르면 만들어.`
- 응용: 기본값을 정해 두고 싶으면 지침 8번 '목표 수준'에 분위기를 적는다.
- 출처: [V2 1:09](https://www.youtube.com/watch?v=RKK9aWedELs&t=69s) · [V2 2:06](https://www.youtube.com/watch?v=RKK9aWedELs&t=126s)
- 원본 장면: [V2 1:15](https://www.youtube.com/watch?v=RKK9aWedELs&t=75s) → `~/Desktop/cysjavis/모션그래픽/오퍼스_모션원리_도감_자료/frames/A8.jpg`

### A9 채팅은 코드, 작업 모드는 파일

일반 채팅에서는 코드로 웹 미리보기가 나오고 완성도가 조금 낮다. Cowork·Claude Code·코드 실행이 켜진 프로젝트에서는 실제 MP4·WAV 파일이 나온다. 설정 › 기능에서 '코드 실행 및 파일 생성'을 켜야 렌더된다. V2에서 ChatGPT Work는 완성 MP4(2560×1440·15초·원본 소리 유지), 프리미어 원본 위 트랙에 올리는 투명 그래픽 MOV, 수정용 소스 ZIP을 함께 냈다. Claude에도 같은 3종을 요청할 수 있다.

- 프롬프트: `웹 미리보기가 아니라 파일로: ① 완성 MP4 ② 알파 채널 투명 오버레이 MOV(ProRes 4444) ③ 소스 ZIP.`
- 응용: 로컬 렌더는 Claude Code + claude-motion-studio의 render_hq.mjs.
- 출처: [V2 2:48](https://www.youtube.com/watch?v=RKK9aWedELs&t=168s) · [V1 1:54](https://www.youtube.com/watch?v=jv8MtZ-T1iw&t=114s) · [V2 2:40](https://www.youtube.com/watch?v=RKK9aWedELs&t=160s)
- 원본 장면: [V2 2:40](https://www.youtube.com/watch?v=RKK9aWedELs&t=160s) → `~/Desktop/cysjavis/모션그래픽/오퍼스_모션원리_도감_자료/frames/A9.jpg`

### A10 장면 번호로 고친다

결과를 받은 뒤에는 장면 번호와 바꿀 내용을 콕 집어 같은 대화에서 요청한다. 같은 대화 안이면 정해진 스타일을 유지하며 고친다. 시리즈는 같은 프로젝트에 둔다.

- 프롬프트: `장면 3: 키워드를 '은혜'로 바꾸고 0.5박 늦게 등장. 나머지는 그대로.`
- 응용: 수정 요청 템플릿을 설명서 탭에 두었다.
- 출처: [V1 6:13](https://www.youtube.com/watch?v=jv8MtZ-T1iw&t=373s) · [V1 6:40](https://www.youtube.com/watch?v=jv8MtZ-T1iw&t=400s)
- 원본 장면: [V1 6:16](https://www.youtube.com/watch?v=jv8MtZ-T1iw&t=376s) → `~/Desktop/cysjavis/모션그래픽/오퍼스_모션원리_도감_자료/frames/A10.jpg`

### A11 한 번 요청 ≠ 한 번 작업

'한 번에 만들었다'는 사례도 내부에서는 코드 작성·실행·화면 확인·수정이 반복된다. 16개 효과를 만든 제작자도 참고 자료와 여러 차례 수정이 필요했다. 결과는 매번 달라질 수 있다. 공개 쇼케이스는 제작자가 고른 결과이며 같은 요청에 같은 완성도를 보장하는 비교 실험이 아니다(V5 8:26).

- 프롬프트: `렌더 후 대표 프레임을 직접 보고, 문제가 있으면 고쳐서 다시 렌더한 뒤에 보고해.`
- 응용: 예산·시간은 '수정 2회'를 기본으로 잡는다(V4의 비교 규칙).
- 출처: [V5 8:09](https://www.youtube.com/watch?v=yFxZNHWyIMs&t=489s) · [V4 6:52](https://www.youtube.com/watch?v=UcAbZwtEfbk&t=412s)
- 원본 장면: [V5 8:15](https://www.youtube.com/watch?v=yFxZNHWyIMs&t=495s) → `~/Desktop/cysjavis/모션그래픽/오퍼스_모션원리_도감_자료/frames/A11.jpg`

### A12 에이전트는 주변 도구를 스스로 찾는다

코드만으로 만들라 해도 PC에 있는 ElevenLabs API 키와 오디오 스킬을 찾아 썼고, 브랜드 디자인 스킬을 찾아 색·글꼴·로고를 지침대로 적용했다. 편리하지만 비교 실험이라면 사용 가능한 도구를 미리 정해야 한다.

- 프롬프트: `이번 작업에서 쓸 수 있는 외부 도구는 X뿐이야. 다른 API·스킬은 쓰지 마.`
- 응용: 교회 브랜드 스킬을 만들어 두면 모든 영상에 자동 적용된다.
- 출처: [V4 7:54](https://www.youtube.com/watch?v=UcAbZwtEfbk&t=474s) · [V4 23:31](https://www.youtube.com/watch?v=UcAbZwtEfbk&t=1411s)
- 원본 장면: [V4 8:10](https://www.youtube.com/watch?v=UcAbZwtEfbk&t=490s) → `~/Desktop/cysjavis/모션그래픽/오퍼스_모션원리_도감_자료/frames/A12.jpg`

### A13 권한 우회 모드 주의

Blender 서버 렌더가 느리자 Opus가 사용자 확인 없이 맥에 Blender를 설치했다. 권한 확인을 건너뛰는 설정으로 실행했기 때문이다.

- 프롬프트: `프로그램 설치나 유료 API 호출 전에는 반드시 확인을 받아.`
- 응용: 장시간 렌더를 맡길 때도 설치·결제는 승인 대상으로 둔다.
- 출처: [V4 14:16](https://www.youtube.com/watch?v=UcAbZwtEfbk&t=856s)
- 원본 장면: [V4 14:30](https://www.youtube.com/watch?v=UcAbZwtEfbk&t=870s) → `~/Desktop/cysjavis/모션그래픽/오퍼스_모션원리_도감_자료/frames/A13.jpg`


## B. 박자와 소리

### B1 초가 아니라 박자로 짠다

모든 움직임을 초가 아니라 박자로 정한다. 128 BPM이면 4/4박 8마디 = 32박이 정확히 15초에 들어간다(32 × 60/128 = 15). BPM = 마디 × 4 × 60 ÷ 길이(초).

- 프롬프트: `길이에 맞는 BPM과 마디 수를 먼저 정하고(예: 128 BPM × 8마디 = 정확히 15초), 모든 사건 시각을 박자 번호로 지정해.`
- 응용: 30초 = 16마디@128, 10초 = 5마디@120, 20초 = 10마디@120(R16).
- 출처: [V1 5:19](https://www.youtube.com/watch?v=jv8MtZ-T1iw&t=319s)
- 원본 장면: [V1 5:23](https://www.youtube.com/watch?v=jv8MtZ-T1iw&t=323s) → `~/Desktop/cysjavis/모션그래픽/오퍼스_모션원리_도감_자료/frames/B1.jpg`

### B2 박자 계층에 사건을 배정

강박(마디 첫 박) → 장면 전환·주요 등장 / 매 박 → 키워드 교체·스케일 펄스 / 8분·16분음표 → 글자 단위 등장 / 히트 포인트 → 흔들림·플래시. 계층이 곧 화면의 위계가 된다.

- 프롬프트: `강박=장면 전환, 박=키워드 교체와 스케일 펄스, 8·16분=글자 단위 등장, 히트=셰이크·플래시로 배정해.`
- 응용: 찬양 가사 영상: 마디=가사 줄, 박=핵심 단어, 16분=음절.
- 출처: [V1 5:28](https://www.youtube.com/watch?v=jv8MtZ-T1iw&t=328s)
- 원본 장면: [V1 5:37](https://www.youtube.com/watch?v=jv8MtZ-T1iw&t=337s) → `~/Desktop/cysjavis/모션그래픽/오퍼스_모션원리_도감_자료/frames/B2.jpg`

### B3 음악이 먼저다

제작이 시작되면 음악부터 준비한다. 1순위는 상업 이용 가능한 무료 음원(CC0·CC-BY)을 찾아 라이선스를 기록하는 것, 2순위는 받을 수 없을 때 그 사실을 알리고 직접 작곡(코드 합성)하는 것이다. 화면은 음악의 박자표 위에 얹는다.

- 프롬프트: `음악을 먼저 정해. CC0·CC-BY 음원을 찾아 라이선스를 기록하고, 없으면 알린 뒤 Python으로 정한 BPM에 맞는 곡을 합성해.`
- 응용: claude-motion-studio/scripts의 합성기는 BPM·길이 상수만 바꿔 쓴다.
- 출처: [V1 5:06](https://www.youtube.com/watch?v=jv8MtZ-T1iw&t=306s)
- 원본 장면: [V1 5:10](https://www.youtube.com/watch?v=jv8MtZ-T1iw&t=310s) → `~/Desktop/cysjavis/모션그래픽/오퍼스_모션원리_도감_자료/frames/B3.jpg`

### B4 컷 지점을 먼저 찾고 소리를 놓는다

기존 영상에 소리를 입힐 때는 프레임을 분석해 장면 전환 지점(예: 5·9·14·22·27·31초)을 먼저 찾는다. 코드 합성 효과음은 20개 중 19개가 1ms 이내로 맞았다.

- 프롬프트: `영상을 프레임 단위로 분석해 장면 전환 시각을 표로 뽑고, 그 시각에 효과음을 배치해.`
- 응용: ffmpeg scene 필터로 컷을 찾고 beatgrid.py로 가장 가까운 박에 스냅한다.
- 출처: [V4 8:37](https://www.youtube.com/watch?v=UcAbZwtEfbk&t=517s)
- 원본 장면: [V4 9:02](https://www.youtube.com/watch?v=UcAbZwtEfbk&t=542s) → `~/Desktop/cysjavis/모션그래픽/오퍼스_모션원리_도감_자료/frames/B4.jpg`

### B5 효과음은 파일 시작이 아니라 소리 정점에

효과음 파일의 시작점이 아니라 측정한 소리의 정점(peak)이 사건 시각에 오도록 놓는다. 효과음은 음악보다 작게, 최종 loudnorm -14 LUFS.

- 프롬프트: `각 효과음의 측정한 정점이 사건 시각에 오게 배치하고 음악보다 작게, loudnorm -14 LUFS로 맞춰.`
- 응용: 유튜브 업로드 기준 음량(-14 LUFS)과 같다.
- 출처: [R](https://github.com/dandacompany/opus-video-prompts)

### B6 코드 합성음 vs 생성 음악

코드 합성: 컷과 완벽히 맞지만 전자음 같고 얇다. ElevenLabs 생성: 실제 악기처럼 풍부하지만 박이 컷과 어긋나 구간별로 속도를 1.6% 조절하고 한 박을 잘라 맞추는 편집이 필요했다.

- 프롬프트: `생성 음악의 박을 분석해 컷과 어긋나면 구간별 템포를 ±2% 안에서 조절하고 남는 박은 잘라 맞춰.`
- 응용: 초안은 코드 합성, 최종본은 생성 음악 + 싱크 보정.
- 출처: [V4 9:08](https://www.youtube.com/watch?v=UcAbZwtEfbk&t=548s) · [V4 10:02](https://www.youtube.com/watch?v=UcAbZwtEfbk&t=602s)
- 원본 장면: [V4 9:17](https://www.youtube.com/watch?v=UcAbZwtEfbk&t=557s) → `~/Desktop/cysjavis/모션그래픽/오퍼스_모션원리_도감_자료/frames/B6.jpg`

### B7 가사가 바뀌면 공간이 바뀐다

기존 노래의 글자와 도형 움직임을 맞춘 뮤직비디오에서 가사가 바뀔 때마다 화면의 공간과 구도가 함께 변한다. 서로 다른 장면을 하나의 리듬으로 묶는 것이 화려한 요소보다 중요하다.

- 프롬프트: `가사 줄이 바뀔 때마다 구도(위치·크기·배경 면)를 바꾸고, 모든 장면을 같은 박자 펄스로 묶어.`
- 응용: 찬양 가사 영상·성경 암송 영상.
- 출처: [V5 0:27](https://www.youtube.com/watch?v=yFxZNHWyIMs&t=27s) · [V5 1:14](https://www.youtube.com/watch?v=yFxZNHWyIMs&t=74s)
- 원본 장면: [V5 0:19](https://www.youtube.com/watch?v=yFxZNHWyIMs&t=19s) → `~/Desktop/cysjavis/모션그래픽/오퍼스_모션원리_도감_자료/frames/B7.jpg`

### B8 음악까지 코드로

픽셀 캐릭터 밴드가 연주하고 글자와 조명이 음악에 맞춰 움직이는 뮤직비디오를 화면과 소리 모두 JavaScript로 만들었다. 기존 노래에 화면을 붙이는 것과 다른 접근이다. 드럼 이름표에 'KARPLUS STRONG'이 보이는데, 줄을 튕기는 소리를 계산으로 만드는 Karplus-Strong 합성 알고리즘이다.

- 프롬프트: `Web Audio로 곡을 합성하고(기타·현은 Karplus-Strong) 같은 시간축으로 화면을 그려. 음과 화면이 한 소스에서 나오게 해.`
- 응용: 저작권 걱정 없는 짧은 브랜드 징글.
- 출처: [V5 7:08](https://www.youtube.com/watch?v=yFxZNHWyIMs&t=428s)
- 원본 장면: [V5 7:20](https://www.youtube.com/watch?v=yFxZNHWyIMs&t=440s) → `~/Desktop/cysjavis/모션그래픽/오퍼스_모션원리_도감_자료/frames/B8.jpg`


## C. 렌더 공학

### C1 모든 프레임은 seek(t)의 순수함수

모든 스타일을 seek(t)의 시간값으로 계산한다. CSS 전환·타이머·프레임 간 상태 저장을 쓰지 않는다. 그래야 임의 시점의 프레임을 순서 없이 병렬로 렌더하고, 특정 시각만 다시 확인할 수 있다.

- 프롬프트: `모든 시각 상태를 seek(t) 하나로 계산해. CSS 애니메이션·setTimeout·이전 프레임 상태 금지.`
- 응용: 이 도감의 데모도 전부 draw(t) 순수함수로 그렸다.
- 출처: [R](https://github.com/dandacompany/opus-video-prompts) · [P](https://github.com/JohnHeibel/PDoomVideo/blob/main/ANIMATION_GUIDE.md)

### C2 난수 대신 해시, 떨림은 의도적으로

Math.random()을 쓰지 않고 hash(i)로 객체별 고정 난수를 만든다. 손그림 떨림(jit)은 초당 12번 시드를 바꿔 선이 '보글거리게(boil)' 한다. 셀 애니메이션 질감이 의도적으로 생긴다.

- 프롬프트: `난수는 hash(i)로 고정하고, 손그림 선 떨림은 초당 12회 재시드해 boil 효과를 내.`
- 응용: 그림책·수채화풍 성경 이야기 영상.
- 출처: [P](https://github.com/JohnHeibel/PDoomVideo/blob/main/ANIMATION_GUIDE.md)

### C3 닫힌형 스프링

스프링을 시뮬레이션하지 않고 닫힌 형태의 계단 응답으로 계산한다. 목표값이 여러 번 바뀌면 변화마다 스프링을 하나씩 더해 시간의 순수함수로 유지한다. 초과(overshoot)는 아주 작게.

- 프롬프트: `스프링은 닫힌형 계단 응답의 합으로 계산하고 초과 움직임은 5% 이하로.`
- 응용: 버튼·카드가 '착' 자리 잡는 고급 UI 느낌.
- 출처: [R](https://github.com/dandacompany/opus-video-prompts)

### C4 양 끝에 다른 스프링

탭 표시기의 앞쪽 끝과 뒤쪽 끝에 서로 다른 스프링을 주면 앞이 먼저 늘어나고 뒤가 따라와 액체처럼 움직인다. 토글 손잡이에도 같은 기법을 쓴다.

- 프롬프트: `탭 표시기 앞 끝은 빠른 스프링, 뒤 끝은 느린 스프링으로 늘어났다 줄어들게 해.`
- 응용: 목차·진행 단계 표시.
- 출처: [R](https://github.com/dandacompany/opus-video-prompts)

### C5 서브프레임 모션블러

Playwright로 프레임마다 하위 프레임 3~4장(t−1/240, t, t+1/240초 등)을 렌더해 FFmpeg tmix로 섞으면 60fps 모션블러가 생긴다. 마지막 서브프레임을 정확한 시각으로 두면 정지 화면은 선명하다.

- 프롬프트: `프레임마다 서브프레임 4장을 렌더해 tmix로 섞어 60fps 모션블러를 만들어.`
- 응용: claude-motion-studio의 render_hq.mjs --sub 4 가 이미 구현.
- 출처: [R](https://github.com/dandacompany/opus-video-prompts)

### C6 실사 영상은 이미지 시퀀스로

HTML 안에서 실제 영상을 쓸 때는 FFmpeg로 30fps JPEG 시퀀스를 뽑아 프레임마다 img 소스를 바꾼다. seek는 이미지 디코딩이 끝날 때까지 기다린다. video 태그의 재생 시점은 프레임 정확도가 없다.

- 프롬프트: `실제 영상은 30fps JPEG 시퀀스로 추출해 seek(t)마다 해당 프레임 img로 교체하고 decode()를 기다려.`
- 응용: 예배 실황 클립 위에 코드 자막·그래픽 얹기.
- 출처: [R](https://github.com/dandacompany/opus-video-prompts)

### C7 알려진 함정 다섯

① 카메라가 확대하는 요소에 will-change를 걸면 글자가 흐려진다. ② preserve-3d 요소에 opacity·filter를 주면 평면화돼 앞뒷면이 함께 보인다 → 래퍼에 페이드. ③ 변형되는 컨테이너 안 글자 교체는 등장·퇴장 시점을 따로. ④ 루프는 마지막 프레임을 첫 프레임과 같게, 커서 위치와 속도까지. ⑤ 매치컷은 실행 중 측정한 요소 위치를 쓴다.

- 프롬프트: `will-change 금지, 3D 페이드는 래퍼에, 텍스트 교체는 퇴장 후 등장, 루프는 위치·속도까지 첫 프레임과 일치.`
- 응용: 예배 전 대기 화면 같은 무한 루프 영상.
- 출처: [R](https://github.com/dandacompany/opus-video-prompts)

### C8 콘택트 시트로 검수

전체 렌더 전에 박자마다 한 프레임씩, 각 샷의 첫·끝 프레임과 히트 주변 0.1초 간격 프레임을 한 장에 모아 직접 본다. 박자 이탈·겹침·잘림·읽기 어려움을 고친다. 완성 후에는 ffprobe로 해상도·길이·오디오 트랙을 확인하고 보고한다.

- 프롬프트: `전체 렌더 전에 박자별 프레임 시트를 만들어 직접 보고 고쳐. 완료 후 ffprobe 결과를 함께 보고해.`
- 응용: scripts/beatgrid.py --sheet clip.mp4 가 강박 시트를 만든다.
- 출처: [V1 5:45](https://www.youtube.com/watch?v=jv8MtZ-T1iw&t=345s) · [R](https://github.com/dandacompany/opus-video-prompts) · [P](https://github.com/JohnHeibel/PDoomVideo/blob/main/ANIMATION_GUIDE.md)
- 원본 장면: [V1 5:52](https://www.youtube.com/watch?v=jv8MtZ-T1iw&t=352s) → `~/Desktop/cysjavis/모션그래픽/오퍼스_모션원리_도감_자료/frames/C8.jpg`

### C9 긴 영상은 챕터 파일로 쪼갠다

156초 뮤직비디오는 챕터마다 파일 하나(IIFE)로 나누고 공유 파일은 고치지 않게 했다. 프레임이 순수함수라 여러 에이전트가 동시에 렌더할 수 있다. 성능 예산은 프레임당 2.5초 이하, 도형은 수백 개까지.

- 프롬프트: `챕터별 파일로 나누고 공유 헬퍼는 수정하지 마. 프레임당 렌더 2.5초 이하로 유지해.`
- 응용: 3분 이상 강의 영상을 서브에이전트로 병렬 제작.
- 출처: [P](https://github.com/JohnHeibel/PDoomVideo/blob/main/ANIMATION_GUIDE.md)

### C10 표정은 스냅하지 않는다

캐릭터 표정을 바로 바꾸지 않고 깜박임–찌그러짐–팝(blink-squash-pop)으로 전환한다. 예비 동작(anticipation)과 초과(overshoot), 스쿼시·스트레치를 박자 위에 둔다. 샷마다 초점 동작 하나, 큰 실루엣.

- 프롬프트: `표정 변화는 깜박임→찌그러짐→팝 순서, 주요 동작은 박자에, 샷마다 초점 동작 하나.`
- 응용: 마스코트 캐릭터 광고.
- 출처: [P](https://github.com/JohnHeibel/PDoomVideo/blob/main/ANIMATION_GUIDE.md)

### C11 3D 피사계심도는 누적 렌더

Three.js 디오라마에서 장면을 96번 렌더해 누적하면 피사계심도 흐림이 생겨 작은 모형을 접사한 사진처럼 보인다. 창으로 들어오는 달빛과 먼지 같은 극적인 빛은 코드 버전이 더 강했다.

- 프롬프트: `Three.js로 렌더하되 카메라 조리개를 흔들며 96회 누적해 미니어처 피사계심도를 만들어.`
- 응용: 성막·성전 미니어처 디오라마.
- 출처: [V4 12:09](https://www.youtube.com/watch?v=UcAbZwtEfbk&t=729s)
- 원본 장면: [V4 12:15](https://www.youtube.com/watch?v=UcAbZwtEfbk&t=735s) → `~/Desktop/cysjavis/모션그래픽/오퍼스_모션원리_도감_자료/frames/C11.jpg`


## D. 시각 문법

### D1 한 물체가 계속 변신한다

새 화면을 매번 꺼내는 대신 같은 물체의 모양을 바꿔 시선을 붙잡는다. 재생 버튼 → 음악 플레이어 → 스위치 → 차트 → 검색창. 크기·모서리·색만 바꾸고 내용은 짧은 흐림과 함께 교체, 커서가 실제로 클릭·드래그해 변화를 일으킨다.

- 프롬프트: `도형 하나를 컷 없이 계속 변형해. 매 박자마다 상태 하나, 커서가 클릭해서 변화를 일으키게.`
- 응용: 강의 개념 변신: 질문 → 본문 → 적용 → 기도.
- 출처: [V5 1:40](https://www.youtube.com/watch?v=yFxZNHWyIMs&t=100s) · [R](https://github.com/dandacompany/opus-video-prompts)
- 원본 장면: [V5 1:44](https://www.youtube.com/watch?v=yFxZNHWyIMs&t=104s) → `~/Desktop/cysjavis/모션그래픽/오퍼스_모션원리_도감_자료/frames/D1.jpg`

### D2 맥락을 주면 움직임에 목적이 생긴다

같은 변신 기법을 제품 소개에 적용하자 버튼이 지구본이 되고 사람 목록과 모임 카드로 바뀌었다. 참고 영상과 '내 제품 설명'을 함께 주는 것이 비결이었다.

- 프롬프트: `이 기법으로 우리 서비스(설명 첨부)를 소개해 줘. 변신마다 기능 하나.`
- 응용: 교회 앱·홈페이지 기능 소개.
- 출처: [V5 2:00](https://www.youtube.com/watch?v=yFxZNHWyIMs&t=120s)
- 원본 장면: [V5 2:05](https://www.youtube.com/watch?v=yFxZNHWyIMs&t=125s) → `~/Desktop/cysjavis/모션그래픽/오퍼스_모션원리_도감_자료/frames/D2.jpg`

### D3 어느 단어를 먼저 읽게 할지

큰 글자만으로 화면을 끌고 간다. 단어가 밀려 들어오고 크기가 바뀌고 다음 문장으로 넘어간다. 무엇을 보여 줄지보다 어느 단어를 먼저 읽게 할지가 연출의 핵심이다. 관찰 세부(V5 2:21–2:43): 1:1 검정 정사각에 흰 초굵은 산세리프, 강조색은 한 화면 한 단어에만, 줄을 쌓을수록 마지막 단어가 가장 크다, 문장 사이 글자 스크램블 전환, 끝 글자 하나를 기준선 아래로 떨어뜨리는 흔적(한 영상 1회), 엔딩은 제작자 이름을 커서로 타자.

- 프롬프트: `문장마다 먼저 읽힐 핵심 단어를 하나 정해 가장 크게, 나머지는 작게 뒤따르게 해. 먼저 문장마다 '먼저 읽힐 단어 1개와 크기 등급(대·중·소)' 표를 보여 주고, 강조색은 그 단어에만, 문장 사이는 text-scramble 0.4초로.`
- 응용: 설교 제목·핵심 문장 인트로.
- 출처: [V5 2:28](https://www.youtube.com/watch?v=yFxZNHWyIMs&t=148s)
- 원본 장면: [V5 2:35](https://www.youtube.com/watch?v=yFxZNHWyIMs&t=155s) → `~/Desktop/cysjavis/모션그래픽/오퍼스_모션원리_도감_자료/frames/D3.jpg`

### D4 정보를 글자·그래프·지도로

15초 자기소개에서 이름·사진·경력·성과가 차례로 등장한다. 한 사람이 가진 정보를 글자, 그래프, 지도로 바꿔 보여 준다. 소개할 내용이 이미 있을 때 전달 방식만 바꾸는 데 쓴다.

- 프롬프트: `내 이력(첨부)을 짧은 소개 영상으로. 숫자는 그래프로, 지역은 지도로, 나머지는 글자로.`
- 응용: 선교사 소개·새가족 환영 영상.
- 출처: [V5 2:54](https://www.youtube.com/watch?v=yFxZNHWyIMs&t=174s)
- 원본 장면: [V5 3:00](https://www.youtube.com/watch?v=yFxZNHWyIMs&t=180s) → `~/Desktop/cysjavis/모션그래픽/오퍼스_모션원리_도감_자료/frames/D4.jpg`

### D5 과정은 단계 표시와 함께

칵테일 레시피: 빈 잔에 얼음 → 재료가 차례로 부어지고 옆에 양이 표시되며, 아래에 지금 몇 단계인지 따라갈 수 있는 표시가 있다. 섞이며 색과 높이가 달라진다. 글로 읽던 순서를 눈으로 따라가게 한다.

- 프롬프트: `빈 상태에서 완성까지 전 과정을 보여 줘. 재료를 넣는 순간마다 이름과 양을 표시하고 하단에 단계 진행바.`
- 응용: 성찬·세례 순서, 교회 행정 절차 안내.
- 출처: [V5 3:13](https://www.youtube.com/watch?v=yFxZNHWyIMs&t=193s) · [R](https://github.com/dandacompany/opus-video-prompts)
- 원본 장면: [V5 3:25](https://www.youtube.com/watch?v=yFxZNHWyIMs&t=205s) → `~/Desktop/cysjavis/모션그래픽/오퍼스_모션원리_도감_자료/frames/D5.jpg`

### D6 평면 도면을 공간으로

이케아 설명서를 3차원 조립 영상으로 바꿨다. 떨어져 있던 부품이 공간에서 만나 순서대로 움직인다. 단, 자연스럽게 움직인다고 조립 순서까지 정확한 것은 아니므로 원본과 대조가 필요하다.

- 프롬프트: `도면(첨부)을 3D 조립 영상으로. 각 단계 끝에 원본 도면의 해당 컷을 작게 띄워 대조할 수 있게.`
- 응용: 행사 무대·성막 구조 설명.
- 출처: [V5 3:47](https://www.youtube.com/watch?v=yFxZNHWyIMs&t=227s)
- 원본 장면: [V5 4:00](https://www.youtube.com/watch?v=yFxZNHWyIMs&t=240s) → `~/Desktop/cysjavis/모션그래픽/오퍼스_모션원리_도감_자료/frames/D6.jpg`

### D7 계산과 시각화를 함께 만든다

손글씨 숫자가 들어오면 신경망 연결을 따라 빛이 움직이고 예측이 나타나는 픽셀 그래픽. 제작자는 실제로 신경망까지 학습시켰다고 밝혔다. 설명할 계산과 그 계산을 보여 주는 애니메이션을 함께 만들 수 있다.

- 프롬프트: `개념을 실제로 계산하는 코드를 먼저 짜고, 그 중간값을 그대로 화면에 그려.`
- 응용: 헌금 통계·출석 추이처럼 실제 데이터 기반 영상.
- 출처: [V5 4:27](https://www.youtube.com/watch?v=yFxZNHWyIMs&t=267s)
- 원본 장면: [V5 4:45](https://www.youtube.com/watch?v=yFxZNHWyIMs&t=285s) → `~/Desktop/cysjavis/모션그래픽/오퍼스_모션원리_도감_자료/frames/D7.jpg`

### D8 같은 대상을 여러 거리에서

세포 속 운반 단백질이 점토 캐릭터처럼 걷는 Blender 클레이 애니메이션. 다리를 가까이 보여 줬다가 넓은 장면으로 돌아온다. 같은 대상을 여러 거리에서 보여 주면 짧아도 하나의 장면처럼 느껴진다. 내레이션 자막도 'Left foot… right foot…', 'Uh-oh. End of the line?'처럼 대상의 1인칭 유머로 썼다.

- 프롬프트: `주인공을 와이드 → 클로즈업 → 와이드로 보여 줘. 카메라만 바꾸고 대상은 유지.`
- 응용: 인물 소개·제품 디테일.
- 출처: [V5 5:15](https://www.youtube.com/watch?v=yFxZNHWyIMs&t=315s)
- 원본 장면: [V5 5:10](https://www.youtube.com/watch?v=yFxZNHWyIMs&t=310s) → `~/Desktop/cysjavis/모션그래픽/오퍼스_모션원리_도감_자료/frames/D8.jpg`

### D9 픽셀이 적어도 규칙이 맞으면 산다

가로 128 × 세로 96 픽셀의 말이 관절을 계산해 달리고 배경과 먼지가 흐른다. 정수 좌표, 고정 24색 팔레트, 안티앨리어싱 금지, 60fps 루프여도 8~12fps로 양자화해 스프라이트처럼 보이게 한다.

- 프롬프트: `128×96 논리 해상도에 정수 배율 확대, 24색 고정 팔레트, 좌표 정수화, 포즈는 10fps로 양자화.`
- 응용: 레트로 게임풍 어린이부 영상.
- 출처: [V5 5:35](https://www.youtube.com/watch?v=yFxZNHWyIMs&t=335s) · [R](https://github.com/dandacompany/opus-video-prompts)
- 원본 장면: [V5 5:45](https://www.youtube.com/watch?v=yFxZNHWyIMs&t=345s) → `~/Desktop/cysjavis/모션그래픽/오퍼스_모션원리_도감_자료/frames/D9.jpg`

### D10 카메라 이동이 이야기의 순서

방 → 노트북 → 칩 → 결정 구조 → 원자 → 쿼크로 계속 확대한다. HTML과 Three.js로 만들었다. 실제 현미경 영상이 아니라 크기 차이를 이해시키는 시각화임을 밝혀야 한다.

- 프롬프트: `한 번도 컷하지 않고 계속 확대하며 단계마다 이름표를 띄워. 끝에 '개념 시각화' 표기.`
- 응용: 우주 → 지구 → 이스라엘 → 예루살렘 → 성전 줌인.
- 출처: [V5 6:09](https://www.youtube.com/watch?v=yFxZNHWyIMs&t=369s)
- 원본 장면: [V5 6:15](https://www.youtube.com/watch?v=yFxZNHWyIMs&t=375s) → `~/Desktop/cysjavis/모션그래픽/오퍼스_모션원리_도감_자료/frames/D10.jpg`

### D11 질감이 일관되면 코드도 그림책

종이를 오려 붙인 그림책 같은 동화를 매 프레임 JavaScript로 그렸다. 일관된 질감과 캐릭터, 장면 전환이 모이면 코드도 딱딱한 도형을 벗어난다. 장면마다 손글씨 한 단어('trees', 'the stars')만 놓아 그림책의 문법을 따른다.

- 프롬프트: `모든 장면에 같은 종이 질감·윤곽선 굵기·팔레트를 써서 그림책처럼.`
- 응용: vox-paper-motion 스킬과 결합.
- 출처: [V5 6:49](https://www.youtube.com/watch?v=yFxZNHWyIMs&t=409s)
- 원본 장면: [V5 6:50](https://www.youtube.com/watch?v=yFxZNHWyIMs&t=410s) → `~/Desktop/cysjavis/모션그래픽/오퍼스_모션원리_도감_자료/frames/D11.jpg`

### D12 제약이 스타일이 된다

한 문장 출시 영상에서 Opus는 검정과 주황 두 색만 쓰고, 영상 전체를 수학 증명처럼(전제 → 추론 → 증명 완료를 뜻하는 로고) 구성했다. 큰 글자가 박자에 맞춰 바뀐다.

- 프롬프트: `색은 두 개만 써. 영상 구조를 '전제 → 추론 → 결론'의 증명처럼 짜.`
- 응용: 교리 영상: 질문 → 성경 근거 → 고백.
- 출처: [V4 3:53](https://www.youtube.com/watch?v=UcAbZwtEfbk&t=233s)
- 원본 장면: [V4 4:06](https://www.youtube.com/watch?v=UcAbZwtEfbk&t=246s) → `~/Desktop/cysjavis/모션그래픽/오퍼스_모션원리_도감_자료/frames/D12.jpg`

### D13 얼굴 위에 글자를 얹지 않는다

인물 컷에서는 얼굴 위에 글자를 올리지 않고 화면을 왼쪽 글자 / 오른쪽 영상으로 나눴다. Opus가 스스로 정한 레이아웃이다.

- 프롬프트: `인물이 나오는 장면은 얼굴을 가리지 말고 좌측 텍스트 / 우측 영상 분할로.`
- 응용: 설교자·간증자 인터뷰 자막.
- 출처: [V4 5:52](https://www.youtube.com/watch?v=UcAbZwtEfbk&t=352s)
- 원본 장면: [V4 5:56](https://www.youtube.com/watch?v=UcAbZwtEfbk&t=356s) → `~/Desktop/cysjavis/모션그래픽/오퍼스_모션원리_도감_자료/frames/D13.jpg`

### D14 금지 목록이 품질을 가른다

상세 템플릿은 모두 금지 목록을 둔다: 과도하게 튀는 가속, 입자 폭발, 발광, UI 장식 그러데이션, 충격파 고리, RGB 분리, 카메라 흔들림, 렌즈 플레어, 네온, 격자 바닥, 깜박이는 배경, 템플릿 같은 요소, 화면 문구 끝 마침표.

- 프롬프트: `금지: 입자 폭발·네온 발광·RGB 분리·렌즈 플레어·과한 바운스·템플릿 느낌·문구 끝 마침표.`
- 응용: claude-motion-studio의 style-presets.md 금지목록과 함께 쓴다.
- 출처: [R](https://github.com/dandacompany/opus-video-prompts)

### D15 한 장면 한 생각, 마스크와 매치컷

고급 미니멀: 장면마다 생각 하나와 넉넉한 여백, 강조색 하나, 자간 좁힌 산세리프 하나. 글자는 마스크로 드러나고, 동작을 이어 붙이는 매치컷과 일관된 카메라 방향을 쓴다.

- 프롬프트: `한 장면 한 문장, 강조색 1개, 글자는 마스크 리빌, 장면은 동작 매치컷으로 연결.`
- 응용: 광고·런칭·연말 결산.
- 출처: [R](https://github.com/dandacompany/opus-video-prompts)

### D16 서로 다른 장면을 하나의 리듬으로

점 하나가 튀어나와 입체 공간과 큰 글자, 수많은 도형으로 이어지는 쇼릴. 금속 반사 도형, 물감처럼 섞이는 색, 화면을 채우는 글자가 나와도 산만하지 않은 이유는 하나의 리듬으로 묶었기 때문이다.

- 프롬프트: `장면은 다양하게 바꾸되 모든 전환을 같은 박자 위에 둬서 하나의 리듬으로 묶어.`
- 응용: 연간 사역 하이라이트 릴.
- 출처: [V5 0:54](https://www.youtube.com/watch?v=yFxZNHWyIMs&t=54s) · [V5 1:17](https://www.youtube.com/watch?v=yFxZNHWyIMs&t=77s)
- 원본 장면: [V5 1:04](https://www.youtube.com/watch?v=yFxZNHWyIMs&t=64s) → `~/Desktop/cysjavis/모션그래픽/오퍼스_모션원리_도감_자료/frames/D16.jpg`

### D17 글자를 피사체 뒤로

큰 글자를 배경과 피사체 사이에 끼운다. V2는 'FOLLOW ME' 거대 글자를 인물 뒤에 두어 사람이 글자를 가리고, V3는 '쨍' 글자 앞에 제품 컷아웃을 세웠다. 피사체 누끼(마스크)가 있어야 가능하며, 한 장면에 깊이가 생긴다.

- 프롬프트: `핵심 단어를 화면 높이의 60%로 키워 배경 위·피사체 아래 레이어에 두고, 피사체 마스크로 글자를 가려.`
- 응용: 설교 제목을 강단 사진의 설교자 뒤에 배치.
- 출처: [V2 0:02](https://www.youtube.com/watch?v=RKK9aWedELs&t=2s) · [V3 5:36](https://www.youtube.com/watch?v=NE306sbvopY&t=336s)
- 원본 장면: [V3 5:36](https://www.youtube.com/watch?v=NE306sbvopY&t=336s) → `~/Desktop/cysjavis/모션그래픽/오퍼스_모션원리_도감_자료/frames/D17.jpg`

### D18 HUD 프레임

실사 위에 촬영 장비 같은 계기판을 얹는다. 위쪽 구간 진행바(7구간 = 7초 7장면), 'FOLLOW ME · 7 WORLDS IN 7 SECONDS' 같은 제목줄, 02/07 카운터, 네 모서리 브래킷, 'LOC 01 · 지하철 승강장' 위치 태그, 'TELEPORT >>> T+02.00s' 타임코드, 위아래 레터박스와 SCENE 01/03. 몇 번째 장면인지와 전체 구조를 계속 알려 준다.

- 프롬프트: `화면 테두리에 HUD를 얹어: 상단 장면 수만큼 나뉜 진행바, 우상단 01/07 카운터, 네 모서리 브래킷, 좌하단 위치 태그, 우하단 타임코드.`
- 응용: 선교지 순례·수련회 스케치 영상.
- 출처: [V2 0:02](https://www.youtube.com/watch?v=RKK9aWedELs&t=2s) · [V2 1:40](https://www.youtube.com/watch?v=RKK9aWedELs&t=100s)
- 원본 장면: [V2 0:02](https://www.youtube.com/watch?v=RKK9aWedELs&t=2s) → `~/Desktop/cysjavis/모션그래픽/오퍼스_모션원리_도감_자료/frames/D18.jpg`

### D19 숫자는 세어 올라가고 양은 점으로

숫자를 바로 보여 주지 않고 세어 올라가게 한다(28 → 55편, 1개 → 4개, 1 → 13). 옆에 점 격자·막대를 함께 채워 크기를 눈으로 느끼게 한다. 숫자는 출처 있는 값만.

- 프롬프트: `수치는 0에서 목표값까지 1박 동안 세어 올리고, 옆에 단위 하나당 점 하나로 양을 채워. 출처·기준일 표기.`
- 응용: 연간 사역 결산(세례 인원·봉사 시간).
- 출처: [V1 6:55](https://www.youtube.com/watch?v=jv8MtZ-T1iw&t=415s) · [V3 5:27](https://www.youtube.com/watch?v=NE306sbvopY&t=327s) · [V5 2:54](https://www.youtube.com/watch?v=yFxZNHWyIMs&t=174s)
- 원본 장면: [V1 6:55](https://www.youtube.com/watch?v=jv8MtZ-T1iw&t=415s) → `~/Desktop/cysjavis/모션그래픽/오퍼스_모션원리_도감_자료/frames/D19.jpg`

### D20 스크램블 디코드

글자가 무작위 기호로 깨졌다가 한 글자씩 제자리를 찾는다. V4 출시 영상의 'MOST AI 1Y6IU5F.' → 'MOST AI GUESSES.', V2의 'From Confusing to #<!!%<' → 'to Clear.'. '혼란 → 명료' 같은 메시지와 붙이면 효과가 의미가 된다.

- 프롬프트: `핵심 문장은 무작위 기호로 시작해 16분음표마다 왼쪽부터 한 글자씩 확정되게 해. 난수는 시드 해시로.`
- 응용: '의심 → 믿음' 같은 전환 메시지.
- 출처: [V4 9:35](https://www.youtube.com/watch?v=UcAbZwtEfbk&t=575s) · [V2 3:31](https://www.youtube.com/watch?v=RKK9aWedELs&t=211s)
- 원본 장면: [V4 9:37](https://www.youtube.com/watch?v=UcAbZwtEfbk&t=577s) → `~/Desktop/cysjavis/모션그래픽/오퍼스_모션원리_도감_자료/frames/D20.jpg`

### D21 정보 장치 키트

V1 샘플들이 반복해 쓴 작은 장치들: 정보를 감싸는 코너 브래킷, 인원수만큼 하나씩 켜지는 점(●●●●●), 원형 이름 배지가 차례로 떠오르기, 연도+제목 리스트가 위에서부터 채워지는 디스코그래피, 하단 진행바, 사진 카드에 색 그림자를 준 스티커 느낌, 키워드 번호(KEYWORD 03/04)와 단계 점. 정보형 브랜드 영상의 기본 부품이다.

- 프롬프트: `정보 장면은 코너 브래킷으로 감싸고, 개수는 점으로 하나씩, 목록은 위에서부터 한 줄씩, 하단에 진행바를 넣어.`
- 응용: 교회 소개(부서 수·예배 시간표·연혁).
- 출처: [V1 0:20](https://www.youtube.com/watch?v=jv8MtZ-T1iw&t=20s) · [V1 6:52](https://www.youtube.com/watch?v=jv8MtZ-T1iw&t=412s)
- 원본 장면: [V1 0:21](https://www.youtube.com/watch?v=jv8MtZ-T1iw&t=21s) → `~/Desktop/cysjavis/모션그래픽/오퍼스_모션원리_도감_자료/frames/D21.jpg`

### D22 말을 그림 은유로

슬로건을 문자 그대로 그린다. 'Untangling AI'는 엉킨 선이 곧은 선으로 풀리고, 'Clarity'는 흩어진 픽셀 조각이 모이며, 단테랩스의 'Orchestrating AI'는 빈 공연장의 지휘대가 됐다. 글을 읽기 전에 그림이 먼저 뜻을 전한다.

- 프롬프트: `슬로건의 핵심 동사를 그대로 움직임으로 그려(풀다 = 엉킨 선이 펴짐, 모으다 = 흩어진 조각이 합쳐짐).`
- 응용: '회복' = 끊긴 선이 이어짐, '연합' = 흩어진 점이 한 모양으로.
- 출처: [V2 3:31](https://www.youtube.com/watch?v=RKK9aWedELs&t=211s) · [V4 22:45](https://www.youtube.com/watch?v=UcAbZwtEfbk&t=1365s)
- 원본 장면: [V2 3:32](https://www.youtube.com/watch?v=RKK9aWedELs&t=212s) → `~/Desktop/cysjavis/모션그래픽/오퍼스_모션원리_도감_자료/frames/D22.jpg`

### D23 주제의 고유 기호를 라벨로

메카 체스 영상은 장면마다 좌하단에 'UNIT 01 · PAWN', 우상단에 체스 기보('e4 e5', 'Nf3 x Nf6', 'Qxe1')를 띄우고 'CHECK', 'CHECKMATE'로 끝냈다. 그 세계에서만 쓰는 기호가 화면 장식이 되면 세계관이 단단해진다.

- 프롬프트: `이 주제에서만 쓰는 표기(단위·기호·번호 체계)를 장면 라벨로 써: 좌하단 단위명, 우상단 진행 기호.`
- 응용: 성경 장절 표기(요 3:16)·히브리어 알파벳을 장면 라벨로.
- 출처: [V3 2:46](https://www.youtube.com/watch?v=NE306sbvopY&t=166s) · [V3 3:16](https://www.youtube.com/watch?v=NE306sbvopY&t=196s)
- 원본 장면: [V3 2:54](https://www.youtube.com/watch?v=NE306sbvopY&t=174s) → `~/Desktop/cysjavis/모션그래픽/오퍼스_모션원리_도감_자료/frames/D23.jpg`

### D24 지우고 나서 제시한다

V1 도입부: '디자이너', '편집 프로그램' 칩에 취소선이 그어지고 물음표가 뜬 뒤, 입력창에 '출처 URL + 지침대로 15초 영상 만들어줘'가 타이핑되고 MP4·WAV 파일 카드가 튀어나온다. 옛 방식을 먼저 지우면 새 방식이 답처럼 보인다.

- 프롬프트: `첫 마디에 기존 방법 2개를 칩으로 보여 주고 취소선을 그은 뒤, 다음 마디에 새 방법을 입력창 타이핑으로 등장시켜.`
- 응용: '바쁨·핑계'에 줄 긋고 '쉼'을 제시하는 안식 설교 인트로.
- 출처: [V1 0:08](https://www.youtube.com/watch?v=jv8MtZ-T1iw&t=8s)
- 원본 장면: [V1 0:08](https://www.youtube.com/watch?v=jv8MtZ-T1iw&t=8s) → `~/Desktop/cysjavis/모션그래픽/오퍼스_모션원리_도감_자료/frames/D24.jpg`

### D25 반복 타일 속 한 줄

같은 단어를 화면 가득 줄줄이 반복해 흘리고, 한 줄만 색 띠로 강조한다(쇼릴의 MOTION MOTION…). 반복이 리듬을 만들고 강조된 한 줄이 초점이 된다.

- 프롬프트: `한 단어를 8줄로 반복해 줄마다 반대 방향으로 흘리고, 가운데 한 줄만 강조색 띠와 반전 글자로.`
- 응용: '은혜 은혜 은혜…' 반복 속 '오늘' 한 줄.
- 출처: [V5 0:49](https://www.youtube.com/watch?v=yFxZNHWyIMs&t=49s)
- 원본 장면: [V5 0:49](https://www.youtube.com/watch?v=yFxZNHWyIMs&t=49s) → `~/Desktop/cysjavis/모션그래픽/오퍼스_모션원리_도감_자료/frames/D25.jpg`


## E. 코드 + 생성형 분업

### E1 언제 생성형을 붙이나

글자·도형·그래프가 대부분이면 Opus 코드만으로 충분하다. 사람·실제 공간·표정·제품 실물이 필요하면 영상 생성(Higgsfield 등)을 연결한다. 코드로 만든 사람은 둥근 머리 마네킹, 트레일러는 실루엣 애니메이션에 머물렀다.

- 프롬프트: `글자·도형은 코드로, 사람·실공간 장면만 생성 모델로 만들어.`
- 응용: 설교 인트로는 코드, 교회 소개는 하이브리드.
- 출처: [V4 21:15](https://www.youtube.com/watch?v=UcAbZwtEfbk&t=1275s) · [V4 16:50](https://www.youtube.com/watch?v=UcAbZwtEfbk&t=1010s)
- 원본 장면: [V4 16:42](https://www.youtube.com/watch?v=UcAbZwtEfbk&t=1002s) → `~/Desktop/cysjavis/모션그래픽/오퍼스_모션원리_도감_자료/frames/E1.jpg`

### E2 코드 버전 먼저, 크레딧은 나중

크레딧을 쓰기 전에 코드 버전을 먼저 만든다. 출시 영상은 실사 4컷을 붙이자 240크레딧이 들었지만 시간은 29분 → 15분, 출력 토큰은 18만 → 6만으로 오히려 줄었다(그릴 장면이 줄어서).

- 프롬프트: `먼저 코드만으로 전체 초안을 만들고, 실사가 꼭 필요한 컷 목록과 예상 크레딧을 보고해.`
- 응용: 생성 크레딧 승인 단계를 두는 이유.
- 출처: [V4 21:40](https://www.youtube.com/watch?v=UcAbZwtEfbk&t=1300s) · [V4 6:08](https://www.youtube.com/watch?v=UcAbZwtEfbk&t=368s)
- 원본 장면: [V4 20:48](https://www.youtube.com/watch?v=UcAbZwtEfbk&t=1248s) → `~/Desktop/cysjavis/모션그래픽/오퍼스_모션원리_도감_자료/frames/E2.jpg`

### E3 글자는 언제나 코드로

생성 영상 속 글자는 일그러지므로 화면 문구는 모두 코드로 덧입힌다. 생성 프롬프트에는 '글자·로고 넣지 말 것'을 넣는다. 그렇게 만든 4컷은 재생성 없이 모두 쓰였다.

- 프롬프트: `생성 컷 프롬프트에는 no text, no logo를 넣고 모든 문구는 코드로 오버레이해.`
- 응용: 한글 자막은 특히 생성 모델이 망가뜨린다.
- 출처: [V4 4:53](https://www.youtube.com/watch?v=UcAbZwtEfbk&t=293s) · [V4 5:40](https://www.youtube.com/watch?v=UcAbZwtEfbk&t=340s)
- 원본 장면: [V4 5:00](https://www.youtube.com/watch?v=UcAbZwtEfbk&t=300s) → `~/Desktop/cysjavis/모션그래픽/오퍼스_모션원리_도감_자료/frames/E3.jpg`

### E4 역할 분담: 그림·소리·조립

비주얼은 Higgsfield, 소리는 ElevenLabs 또는 코드 합성, 둘을 장면에 맞춰 조립하는 것은 Opus. Higgsfield 오디오 도구는 음성 전용이라 배경음악·효과음에는 쓰이지 않았다(Opus가 도구 설명을 읽고 스스로 배제).

- 프롬프트: `장면 영상=생성 모델, 음악·효과음=ElevenLabs(또는 코드), 내레이션=TTS, 최종 조립과 글자=너.`
- 응용: 도구 설명(description)을 정확히 써 두면 에이전트가 맞게 고른다.
- 출처: [V4 10:23](https://www.youtube.com/watch?v=UcAbZwtEfbk&t=623s) · [V4 10:45](https://www.youtube.com/watch?v=UcAbZwtEfbk&t=645s)
- 원본 장면: [V4 10:50](https://www.youtube.com/watch?v=UcAbZwtEfbk&t=650s) → `~/Desktop/cysjavis/모션그래픽/오퍼스_모션원리_도감_자료/frames/E4.jpg`

### E5 이미지 먼저, 그다음 움직임

장면마다 이미지를 먼저 만들고(Cinematic Studio·GPT Image) 그 이미지를 영상 모델(Kling·Seedance)에 넣어 6초 클립으로 움직인다. 구도를 확인하고 움직이므로 실패가 적다. 대신 생성 횟수가 두 배라 크레딧이 많이 든다(회사 소개 16회, 약 970크레딧).

- 프롬프트: `장면별 스틸을 먼저 만들어 보여 주고, 승인된 스틸만 6초 영상으로 움직여.`
- 응용: vox-paper-motion은 스틸만 생성하고 움직임은 코드로 — 가장 싸다.
- 출처: [V4 17:39](https://www.youtube.com/watch?v=UcAbZwtEfbk&t=1059s) · [V4 22:10](https://www.youtube.com/watch?v=UcAbZwtEfbk&t=1330s)
- 원본 장면: [V4 17:42](https://www.youtube.com/watch?v=UcAbZwtEfbk&t=1062s) → `~/Desktop/cysjavis/모션그래픽/오퍼스_모션원리_도감_자료/frames/E5.jpg`

### E6 레퍼런스로 형태를 이어 간다

첫 장면에서 만든 목마를 이후 장면의 참조 이미지로 계속 넣어 장면마다 모양이 바뀌지 않게 했다(V4, Opus가 스스로 정함). V3의 메카 체스도 먼저 말 전체(양 팀 6종)를 한 장의 에셋 시트로 만들고 컨셉 배경을 만든 뒤 장면 영상을 뽑았다.

- 프롬프트: `주인공·핵심 소품은 첫 컷 이미지를 이후 모든 생성의 레퍼런스로 넣어 일관성을 유지해.`
- 응용: 캐릭터 시리즈·연속 에피소드.
- 출처: [V4 17:52](https://www.youtube.com/watch?v=UcAbZwtEfbk&t=1072s) · [V3 1:57](https://www.youtube.com/watch?v=NE306sbvopY&t=117s)
- 원본 장면: [V3 1:57](https://www.youtube.com/watch?v=NE306sbvopY&t=117s) → `~/Desktop/cysjavis/모션그래픽/오퍼스_모션원리_도감_자료/frames/E6.jpg`

### E7 시작 프레임과 끝 프레임

열린 문 이미지만 넣으면 영상이 이미 열린 상태로 시작한다. 같은 구도의 닫힌 문 이미지를 따로 만들어 시작 프레임으로, 열린 문을 끝 프레임으로 지정하고 사이를 영상으로 채웠다.

- 프롬프트: `변화가 있는 컷은 같은 구도의 '전' 이미지와 '후' 이미지를 만들어 시작·끝 프레임으로 지정해.`
- 응용: 무덤 돌이 굴려지는 장면, 성전 휘장이 찢어지는 장면.
- 출처: [V4 18:03](https://www.youtube.com/watch?v=UcAbZwtEfbk&t=1083s)
- 원본 장면: [V4 18:08](https://www.youtube.com/watch?v=UcAbZwtEfbk&t=1088s) → `~/Desktop/cysjavis/모션그래픽/오퍼스_모션원리_도감_자료/frames/E7.jpg`

### E8 도구의 강점을 요청해야 차이가 난다

책상·모니터·카메라 이동만 요청했을 때는 코드 버전이 더 나았다(Blender로도 결국 상자·원기둥을 조합). 사람이 걸어 들어와 앉는 동작, 창으로 드는 빛줄기, 유리·금속 반사처럼 Blender가 잘하는 것을 요청하자 차이가 났다.

- 프롬프트: `이 장면에서 Blender(또는 생성 모델)는 사람 동작·반사·실사 질감에만 써.`
- 응용: 도구 연결 = 자동 품질 향상이 아니다.
- 출처: [V4 10:59](https://www.youtube.com/watch?v=UcAbZwtEfbk&t=659s) · [V4 15:05](https://www.youtube.com/watch?v=UcAbZwtEfbk&t=905s)
- 원본 장면: [V4 15:15](https://www.youtube.com/watch?v=UcAbZwtEfbk&t=915s) → `~/Desktop/cysjavis/모션그래픽/오퍼스_모션원리_도감_자료/frames/E8.jpg`

### E9 에셋 카탈로그와 모션 라이브러리

3D 소품은 카탈로그에서 가져오고(책장·화분·책·러그), 사람은 ① 전신 이미지 생성 → ② 3D 모델 변환 → ③ 모션 라이브러리의 걷기·앉기 적용. 무게중심 이동이 자연스러워진다. 손 각도 결함은 원인(손 회전각 미정의, 본 길이 데이터 오류로 손목이 30cm 뜸)을 진단해 그 구간만 다시 렌더했다(17분).

- 프롬프트: `인물은 이미지→3D→모션 라이브러리 순서로. 결함이 보이면 원인을 진단하고 해당 구간만 재렌더.`
- 응용: 실내 공간 소개·성경 인물 3D 장면.
- 출처: [V4 12:55](https://www.youtube.com/watch?v=UcAbZwtEfbk&t=775s) · [V4 13:28](https://www.youtube.com/watch?v=UcAbZwtEfbk&t=808s)
- 원본 장면: [V4 13:10](https://www.youtube.com/watch?v=UcAbZwtEfbk&t=790s) → `~/Desktop/cysjavis/모션그래픽/오퍼스_모션원리_도감_자료/frames/E9.jpg`

### E10 After Effects를 직접 조작

Higgsfield의 AE 플러그인을 설치하고 Claude에서 'AE 스킬 설치'를 요청한 뒤 AE의 창 › 확장에서 패널을 연다. Claude가 배경·컨셉 이미지와 AE용 소재 영상을 만들고, 컴포지션을 직접 구성해 렌더한다. AE 프로젝트 파일이 남아 중간 수정이 자유롭다.

- 프롬프트: `Higgsfield로 소재를 만들고 After Effects에 연결해 컴포지션을 구성한 뒤 렌더해. 프로젝트 파일은 남겨.`
- 응용: AE 사용자라면 손으로 다듬을 여지를 남기는 경로.
- 출처: [V3 1:03](https://www.youtube.com/watch?v=NE306sbvopY&t=63s) · [V3 2:31](https://www.youtube.com/watch?v=NE306sbvopY&t=151s)
- 원본 장면: [V3 2:50](https://www.youtube.com/watch?v=NE306sbvopY&t=170s) → `~/Desktop/cysjavis/모션그래픽/오퍼스_모션원리_도감_자료/frames/E10.jpg`

### E11 AE 없이: 생성 에셋 + 코드 조립

제품을 설명하면 생성 모델이 배경, 오렌지 자르는 슬로모션, 주스 붓는 장면을 만들고 필요한 소재는 배경 제거(누끼)까지 자동으로 한다. Remotion이나 HyperFrames(둘 다 코드로 영상)로 한글 모션그래픽을 입힌다. 핵심 프레임 몇 장으로 중간 컨펌을 받는다.

- 프롬프트: `제품 소재 영상을 만들고 배경을 지운 컷아웃도 준비해. Remotion으로 한글 모션그래픽을 입히기 전에 핵심 프레임 4장으로 컨펌받아.`
- 응용: claude-motion-studio + media-gen-video 조합.
- 출처: [V3 3:23](https://www.youtube.com/watch?v=NE306sbvopY&t=203s) · [V3 5:16](https://www.youtube.com/watch?v=NE306sbvopY&t=316s)
- 원본 장면: [V3 4:18](https://www.youtube.com/watch?v=NE306sbvopY&t=258s) → `~/Desktop/cysjavis/모션그래픽/오퍼스_모션원리_도감_자료/frames/E11.jpg`

### E12 디렉션은 사람이 준다

모션그래픽 자체는 AI가 만들지만 '이 슬로모션 장면은 반드시 써 달라' 같은 디렉션을 사람이 줘야 디테일이 산다. 글꼴 교체 같은 사소한 수정은 대화로 계속 다듬는다.

- 프롬프트: `반드시 쓸 장면: ○○. 반드시 들어갈 문장: ○○. 나머지 구성은 맡길게.`
- 응용: 지침 5번 장면 구성에 '필수 장면' 칸을 둔다.
- 출처: [V3 5:00](https://www.youtube.com/watch?v=NE306sbvopY&t=300s)
- 원본 장면: [V3 5:05](https://www.youtube.com/watch?v=NE306sbvopY&t=305s) → `~/Desktop/cysjavis/모션그래픽/오퍼스_모션원리_도감_자료/frames/E12.jpg`

### E13 스타일 프리셋 제안은 거절할 수 있다

생성 플랫폼이 첫 컷을 막고 비슷한 분위기의 스타일 프리셋을 제안했을 때, Opus는 제안을 거절하고 원래 프롬프트를 다시 보냈다. 회사 소개 영상에서도 같은 일이 한 번 더 있었다.

- 프롬프트: `플랫폼이 다른 프리셋을 권하면 받아들이지 말고 원 프롬프트로 재요청해.`
- 응용: 의도한 톤을 지키는 안전장치.
- 출처: [V4 5:20](https://www.youtube.com/watch?v=UcAbZwtEfbk&t=320s) · [V4 22:35](https://www.youtube.com/watch?v=UcAbZwtEfbk&t=1355s)
- 원본 장면: [V4 5:25](https://www.youtube.com/watch?v=UcAbZwtEfbk&t=325s) → `~/Desktop/cysjavis/모션그래픽/오퍼스_모션원리_도감_자료/frames/E13.jpg`

### E14 사람을 빼면 빈 공간이 된다

실존 회사 영상이라 AI 인물을 쓰지 말라고 하자 모든 장면이 빈 공간이 되어 '분위기 배경 위 텍스트 카드'처럼 느껴졌다. 홈페이지 슬로건 'Orchestrating AI'를 지휘대로 번역한 은유는 좋았다. 공개용이면 직접 찍은 사람 영상으로 채운다.

- 프롬프트: `실존 단체 영상: AI 인물은 쓰지 말고, 사람 자리는 비워 두되 내가 줄 실제 촬영본이 들어갈 컷을 표시해.`
- 응용: 교회 홍보는 성도 촬영본 + 코드 그래픽.
- 출처: [V4 22:02](https://www.youtube.com/watch?v=UcAbZwtEfbk&t=1322s) · [V4 24:03](https://www.youtube.com/watch?v=UcAbZwtEfbk&t=1443s)
- 원본 장면: [V4 22:54](https://www.youtube.com/watch?v=UcAbZwtEfbk&t=1374s) → `~/Desktop/cysjavis/모션그래픽/오퍼스_모션원리_도감_자료/frames/E14.jpg`


## G. 윤리와 비용

### G1 남의 로고·사진·원곡

공식 로고와 타인의 사진은 쓰지 않는 편이 안전하다. 원곡은 저작권이 있어 개인 소장용이 아니면 피한다. 기존 사진을 쓴 작품을 '모델이 사진까지 만들었다'고 소개하면 안 된다.

- 프롬프트: `로고·인물 사진·기존 곡은 내가 권리를 가진 파일만 써. 생성물과 기존 소재를 NOTES.md에 구분해 적어.`
- 응용: 찬양은 CCLI 등 이용 허락 범위를 확인.
- 출처: [V1 6:25](https://www.youtube.com/watch?v=jv8MtZ-T1iw&t=385s) · [V5 8:00](https://www.youtube.com/watch?v=yFxZNHWyIMs&t=480s)
- 원본 장면: [V1 6:28](https://www.youtube.com/watch?v=jv8MtZ-T1iw&t=388s) → `~/Desktop/cysjavis/모션그래픽/오퍼스_모션원리_도감_자료/frames/G1.jpg`

### G2 변하는 수치에는 확인일

구독자 수처럼 변하는 수치는 확인 날짜를 함께 넣는다. 회사 소개 영상의 숫자는 촬영일이 아니라 제작일(9월 30일) 홈페이지 기준이었다.

- 프롬프트: `화면의 모든 수치 옆이나 끝 크레딧에 '○월 ○일 기준'과 출처를 넣어.`
- 응용: 출처 없는 통계는 화면에 '예시'라고 표시.
- 출처: [V1 6:31](https://www.youtube.com/watch?v=jv8MtZ-T1iw&t=391s) · [V4 23:18](https://www.youtube.com/watch?v=UcAbZwtEfbk&t=1398s)
- 원본 장면: [V4 23:20](https://www.youtube.com/watch?v=UcAbZwtEfbk&t=1400s) → `~/Desktop/cysjavis/모션그래픽/오퍼스_모션원리_도감_자료/frames/G2.jpg`

### G3 시간과 비용은 들쭉날쭉

원작자가 '1분, 2달러'라고 한 한 문장 프롬프트가 V4 환경에서는 15~29분 걸렸다. 수 분짜리 뮤직비디오는 한 세션 200달러 사례도 있다. 영상 제작은 자원을 많이 쓰니 여유 있을 때 작업한다.

- 프롬프트: `시작 전에 예상 시간·토큰·크레딧을 추정해 보고하고, 끝나면 실제 값과 NOTES.md에 기록해.`
- 응용: V4 실측표를 하이브리드 탭에 정리했다.
- 출처: [V4 7:01](https://www.youtube.com/watch?v=UcAbZwtEfbk&t=421s) · [V1 6:36](https://www.youtube.com/watch?v=jv8MtZ-T1iw&t=396s)
- 원본 장면: [V4 20:48](https://www.youtube.com/watch?v=UcAbZwtEfbk&t=1248s) → `~/Desktop/cysjavis/모션그래픽/오퍼스_모션원리_도감_자료/frames/G3.jpg`

## 하이브리드 실측 (V4)

| 예시 | 코드 단독 | Higgsfield 연결 | 크레딧 | 채택 | 이유 |
|---|---|---|---|---|---|
| 출시 영상 (한 문장) | 약 29분 · 출력 18만 토큰 · 42초 · 7장면 | 약 15분 · 6만 토큰 · 37초 · 실사 4컷 | 240 | 하이브리드 | 출시 영상은 사람과 공간이 보여야 분위기가 산다 |
| 배경음악·효과음 | 약 13분 · 코드 합성 · 효과음 19/20 1ms 이내 | ElevenLabs 약 11분 · 풍부하나 싱크 보정 필요 | 0 | 코드 또는 ElevenLabs | Higgsfield 오디오는 음성 전용 |
| 3D 작업실 디오라마 | 약 32분 · Three.js · 빛 표현 우수 · 인물 마네킹 | 약 62분 · 3D 도구+Blender · 인물 동작 자연 | 약 54 | 하이브리드 | 요청의 초점이 사람의 걷고 앉는 동작 |
| 트로이 목마 예고편 60초 | 약 28분 · 14만 토큰 · 실루엣 애니메이션 · 맥 기본 음성 | 약 25분 · 9만 토큰 · 실사 9컷 · 얼굴과 표정 | 약 145 | 하이브리드 | 예고편에서 얼굴과 표정은 코드가 대체하기 어렵다 |
| 회사 소개 (URL 하나) | — | 약 14분 · 5.6만 토큰 · 이미지→영상 16회 · 50초 | 약 970 | 초안용 | 인물 없이 빈 공간 위주 → 공개용은 실제 촬영본 권장 |
