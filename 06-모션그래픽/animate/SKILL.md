---
name: animate
description: UI에 자연스러운 애니메이션·마이크로 인터랙션을 붙이는 스킬. 사용자가 "애니메이션 넣어줘", "호버 효과", "부드럽게 움직이게", "마이크로 인터랙션", "페이지 전환", "스크롤 등장", "Framer Motion", "GSAP", "이징", "튕기는 효과", "/animate"를 언급하거나, 이미 만들어진 정적 컴포넌트에 모션을 추가·수정·진단해 달라고 할 때 발동한다. 레이아웃 배치는 layout-design-coach, 스타일 토큰은 uxui-design-system이 담당하고, 이 스킬은 '움직임'만 전담한다.
---

# Animate

정적 UI에 모션을 붙인다. 규칙: **모션은 상태 변화를 설명할 때만 존재한다.** 장식용 움직임은 넣지 않는다.

## 기술 선택 (위에서부터 멈추는 곳에서 멈춘다)

1. **CSS `transition`** — hover, focus, 색/투명도/transform 변화. 90%가 여기서 끝난다.
2. **CSS `@keyframes` + `animation`** — 반복(스피너·펄스), 진입 1회 재생.
3. **`IntersectionObserver` + CSS 클래스** — 스크롤 등장. 라이브러리 불필요.
4. **View Transitions API** — 페이지/뷰 전환 (`document.startViewTransition`). 지원 안 되면 자동 무시됨.
5. **Framer Motion** — 이미 설치된 경우, 또는 레이아웃 애니메이션(`layoutId`)·제스처·spring이 실제로 필요할 때만.
6. **GSAP** — 타임라인 오케스트레이션, 스크롤 스크러빙 같은 정말 복잡한 경우.

새 의존성은 5번부터. 3번까지는 코드 몇 줄로 끝난다.

## 기본값 (요청이 없으면 이 값)

| 상황 | duration | easing |
|---|---|---|
| hover / focus / 색 변화 | 150ms | `ease-out` |
| 요소 진입 (fade+rise) | 250ms | `cubic-bezier(.16,1,.3,1)` |
| 요소 퇴장 | 150ms | `ease-in` |
| 모달·시트 열기 | 300ms | `cubic-bezier(.16,1,.3,1)` |
| 탭/누름 피드백 | 100ms | `ease-out` |
| spring 필요 시 | — | `stiffness 300, damping 25` |

- **진입은 느리게, 퇴장은 빠르게.** 퇴장은 진입의 절반.
- 움직이는 거리: 4~16px. 그 이상은 산만해진다.
- `transform`과 `opacity`만 애니메이트. `width`/`height`/`top`/`left`는 레이아웃 리플로우를 일으킨다 (크기 변화는 `scale`로).
- 리스트 stagger: 항목당 30~50ms, 총 300ms 넘기지 않기.

## 필수 (생략 금지)

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: .01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: .01ms !important;
    scroll-behavior: auto !important;
  }
}
```

Framer Motion이면 `useReducedMotion()`으로 분기한다. 모션 감소 설정에서도 **상태 변화 자체는 보여야 한다** — 움직임만 없애고 최종 상태는 즉시 적용.

## 작업 순서

1. 대상 컴포넌트 코드를 읽는다. 어떤 **상태 전이**가 있는지 목록화 (idle→hover, closed→open, loading→loaded).
2. 각 전이에 위 표의 기본값을 매핑한다. 전이가 없는 곳엔 모션을 넣지 않는다.
3. 기술 사다리 1번부터 적용. 기존 프로젝트에 이미 있는 애니메이션 유틸/토큰이 있으면 그걸 재사용.
4. `prefers-reduced-motion` 처리를 같은 커밋에 넣는다.
5. 브라우저 도구(preview_start → computer/read_page)로 실제 hover·클릭을 실행해 확인. "될 겁니다"로 끝내지 않는다.

## 체크리스트

- [ ] `transform`/`opacity`만 사용했는가 (레이아웃 속성 애니메이트 없음)
- [ ] `prefers-reduced-motion` 대응 있는가
- [ ] 퇴장이 진입보다 빠른가
- [ ] 300ms 넘는 전이가 있다면 그 이유를 댈 수 있는가
- [ ] 포커스 링·접근성 상태가 애니메이션에 가려지지 않는가
- [ ] 무한 반복 애니메이션이 로딩 표시 외의 용도로 쓰이지 않았는가

## 안티패턴

- 페이지 전체 fade-in (첫 인상만 느려짐)
- 스크롤할 때마다 재생되는 등장 애니메이션 — 1회만
- `ease-in-out` 남발 — 대부분은 `ease-out`이 맞다
- bounce/elastic을 UI 전반에 — 삭제·확인 같은 확정적 동작에만 절제해서
