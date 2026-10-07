import sys,io,re,os,json
p=sys.argv[1]; d=os.path.dirname(p); bn=os.path.basename(p); base=bn.split('_monoline')[0] if '_monoline' in bn else bn[:-5]
s=io.open(p,encoding='utf-8').read()

# ---- strip v1/v2 blocks (idempotent) ----
s=re.sub(r'\n/\* ---- editor(?: v2)? ---- \*/.*?(?=</style>)','\n',s,flags=re.S)
s=re.sub(r'<div id="edbar" hidden>.*?</div>\n(?:<div id="edMarq"></div>\n(?:<button id="edShow"[^\n]*\n)?<div id="narr".*?</div></div></div>\n<div id="edhelp".*?</div></div></div>\n)?','',s,flags=re.S)
s=re.sub(r'<script type="application/json" id="(?:narrData|trData)">.*?</script>\n','',s,flags=re.S)
s=re.sub(r'<script>\n/\* ---- editor(?: v2)?: E 키로 토글 ---- \*/.*?</script>\n','',s,flags=re.S)
NS=len(re.findall(r'<section class="slide',s))
HAS_KO='ko-panel' in s
KH='<div id="khint">'+('N = 한국어 패널 · ' if HAS_KO else '')+'S = 해설 · E = 편집 · ? = 사용법</div>'
if '<div id="khint">' in s: s=re.sub(r'<div id="khint">[^<]*</div>',KH,s)
else:
    assert s.count('<div id="nav">')==1; s=s.replace('<div id="nav">',KH+'\n<div id="nav">')
if '#khint{' not in s: s=s.replace('</style>\n</head>','#khint{position:fixed;left:22px;bottom:18px;color:#fff;font-size:14px;font-weight:600;z-index:99;opacity:.8}\n@media print{#khint{display:none}}\n</style>\n</head>')

# ---- narration data ----
narr={}
for code in ['ko','en','zh','ne','my','vi']:
    f=os.path.join(d,'_notes_%s%s.json'%(base,'' if code=='ko' else '.'+code))
    if os.path.exists(f):
        a=json.load(io.open(f,encoding='utf-8'))
        if isinstance(a,list) and len(a)==NS: narr[code]=a
        else: print('skip',f)
NARR='<script type="application/json" id="narrData">'+json.dumps(narr,ensure_ascii=False).replace('</','<\\/')+'</script>\n'
print('langs:',list(narr))
tr={}
for code in ['zh','vi','my']:
    f=os.path.join(d,'_slides_%s.%s.json'%(base,code))
    if os.path.exists(f):
        try:
            a=json.load(io.open(f,encoding='utf-8'))
            if isinstance(a,dict) and len(a)>50: tr[code]=a
            else: print('skip',f)
        except Exception as e: print('bad',f,e)
TRD='<script type="application/json" id="trData">'+json.dumps(tr,ensure_ascii=False).replace('</','<\\/')+'</script>\n'
print('slide langs:',list(tr))

CSS='''
/* ---- editor v2 ---- */
#edbar{position:fixed;left:0;right:0;top:0;z-index:99;display:flex;gap:4px;align-items:center;flex-wrap:nowrap;overflow-x:auto;height:34px;
  background:#111;color:#fff;padding:0 10px;font-size:11.5px;font-weight:600;font-family:inherit;box-shadow:0 2px 8px rgba(0,0,0,.4)}
#edbar .brand{font-weight:900;letter-spacing:.06em;margin-right:4px;font-size:11px;flex-shrink:0}
#edbar button,#edbar select{font:inherit;font-size:11.5px;font-weight:600;padding:0 7px;height:24px;line-height:1;border:1px solid #666;border-radius:5px;background:#1e1e1e;color:#fff;cursor:pointer;white-space:nowrap;flex-shrink:0}
#edbar button:hover{background:#333}
#edbar button.on{background:#3b5bff;border-color:#3b5bff}
#edbar button:disabled{opacity:.35;cursor:default}
#edbar select.lang{background:#2a2a2a;border-color:#888}
#edbar .sep{width:1px;height:18px;background:#444;margin:0 2px;flex-shrink:0}
#edbar input[type=color]{width:26px;height:24px;border:1px solid #666;border-radius:5px;padding:0;background:#1e1e1e;cursor:pointer;flex-shrink:0}
#edbar .hint{margin-left:auto;font-weight:400;font-size:11px;color:#bbb;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;min-width:0;padding-left:8px}
#edShow{position:fixed;left:8px;top:6px;z-index:99;font:inherit;font-size:11.5px;font-weight:700;padding:3px 9px;border:1px solid #666;border-radius:6px;background:#111;color:#fff;cursor:pointer;opacity:.85}
#edMarq{position:fixed;border:1.5px dashed #3b5bff;background:rgba(59,91,255,.12);pointer-events:none;z-index:98;display:none}
body.editing .ed-sel{outline:3px dashed #e33;outline-offset:6px}
body.editing.mode-move .ed-sel{cursor:move}
body.editing.mode-text .slide *{cursor:text}
body.editing [contenteditable]{outline:3px solid #36f}
body:not(.editing) .ed-hidden{display:none!important}
body.editing .ed-hidden{opacity:.2!important}
.active .fx-none{animation-name:none}
.active .fx-fade{animation-name:fadeUp;animation-duration:.5s;animation-fill-mode:both}
.active .fx-zoom{animation-name:fxZoom;animation-duration:.6s;animation-fill-mode:both}
.active .fx-left{animation-name:fxLeft;animation-duration:.6s;animation-fill-mode:both}
.active .fx-right{animation-name:fxRight;animation-duration:.6s;animation-fill-mode:both}
.active .fx-pop{animation-name:fxPop;animation-duration:.7s;animation-fill-mode:both}
.active .fx-blur{animation-name:fxBlur;animation-duration:.8s;animation-fill-mode:both}
@keyframes fxZoom{from{opacity:0;transform:scale(.6)}to{opacity:1;transform:none}}
@keyframes fxLeft{from{opacity:0;transform:translateX(-120px)}to{opacity:1;transform:none}}
@keyframes fxRight{from{opacity:0;transform:translateX(120px)}to{opacity:1;transform:none}}
@keyframes fxPop{0%{opacity:0;transform:scale(.3)}60%{opacity:1;transform:scale(1.12)}100%{transform:none}}
@keyframes fxBlur{from{opacity:0;filter:blur(14px)}to{opacity:1;filter:none}}
.ov{position:fixed;inset:0;z-index:100;background:rgba(0,0,0,.72);display:flex;align-items:center;justify-content:center;padding:4vh 4vw}
.ov[hidden]{display:none}
.ov .box{background:#fff;color:#111;width:min(1100px,100%);max-height:92vh;display:flex;flex-direction:column;border-radius:14px;overflow:hidden;
  font-family:"Pretendard Variable",Pretendard,-apple-system,"Noto Sans KR","Noto Sans","Noto Sans Devanagari","Noto Sans Myanmar",sans-serif}
.ov .hd{display:flex;align-items:center;gap:12px;padding:14px 22px;border-bottom:2px solid #111;font-weight:800;font-size:18px}
.ov .hd select{font:inherit;font-size:14px;font-weight:600;padding:4px 8px;border:2px solid #111;border-radius:6px;background:#fff}
.ov .hd .pos{font-weight:400;font-size:14px;color:#666}
.ov .hd .nv{font:inherit;font-size:14px;padding:2px 10px;border:2px solid #111;border-radius:6px;background:#fff;cursor:pointer}
.ov .hd .x{margin-left:auto;font-size:22px;background:none;border:0;cursor:pointer;font-family:inherit;color:#111}
.ov .bd{overflow:auto;padding:18px 26px;font-size:16px;line-height:1.75}
.nb{padding:16px 18px;border-radius:10px;margin-bottom:10px;white-space:pre-wrap;border:2px solid transparent}
.nb.cur{border-color:#3b5bff;background:#f3f5ff}
.nb b{display:block;font-weight:800;margin-bottom:6px}
#edhelp h3{font-size:15px;font-weight:800;margin:20px 0 8px;padding-bottom:4px;border-bottom:2px solid #111}
#edhelp h3:first-child{margin-top:0}
#edhelp table{border-collapse:collapse;width:100%;font-size:14.5px}
#edhelp td{padding:6px 8px;vertical-align:top;border-bottom:1px solid #eee}
#edhelp td:first-child{white-space:nowrap;font-weight:700;width:200px}
#edhelp kbd{font:inherit;font-size:12.5px;font-weight:700;border:1px solid #bbb;border-bottom-width:2px;border-radius:4px;padding:0 6px;background:#f7f7f7}
@media print{#edbar,#edShow,#edMarq,.ov{display:none!important}}
'''

HELP='''<h3>1. 발표(기본 조작)</h3><table>
<tr><td><kbd>→</kbd> <kbd>Space</kbd> / <kbd>←</kbd></td><td>다음 / 이전 슬라이드. 화면 오른쪽 절반 클릭 = 다음, 왼쪽 절반 클릭 = 이전. 터치 화면은 좌우 스와이프.</td></tr>
<tr><td><kbd>Home</kbd> / <kbd>End</kbd></td><td>첫 / 마지막 슬라이드</td></tr>
<tr><td>주소 끝 <kbd>#번호</kbd></td><td>특정 슬라이드로 바로 열기 (예: <code>…toggleN.html#12</code>). 주소 끝에 <code>?ko</code>를 붙이면 한국어 패널이 켜진 채 시작.</td></tr>
<tr><td><kbd>N</kbd></td><td>오른쪽 한국어 패널 켜기 / 끄기 (영·한 토글 덱에서만)</td></tr>
<tr><td><kbd>S</kbd></td><td>강의 해설 화면 켜기 / 끄기 (아래 4번)</td></tr>
<tr><td><kbd>E</kbd></td><td>편집 모드 켜기 / 끄기</td></tr>
<tr><td><kbd>?</kbd></td><td>이 사용법 화면</td></tr>
<tr><td><kbd>Esc</kbd></td><td>열린 화면 닫기 · 선택 해제 · 텍스트 입력 완료</td></tr>
<tr><td>인쇄 / PDF</td><td>브라우저 인쇄(<kbd>Ctrl</kbd>+<kbd>P</kbd>)에서 슬라이드 한 장이 한 쪽으로 출력됩니다. 숨긴 요소는 인쇄에도 빠집니다.</td></tr>
</table>
<h3>2. 편집 모드 — 두 가지 모드</h3><table>
<tr><td>텍스트 편집</td><td>요소를 클릭하면 그 자리에 커서가 생깁니다. 바로 타이핑하고, <kbd>Enter</kbd>로 줄바꿈, <kbd>Ctrl</kbd>+<kbd>B</kbd>/<kbd>I</kbd>/<kbd>U</kbd>로 굵게·기울임·밑줄. 바깥을 클릭하거나 <kbd>Esc</kbd>로 완료. 번역 보기 중에는 사용할 수 없으니 <b>원문 EN</b>으로 돌아가서 편집하세요.</td></tr>
<tr><td>요소 이동 · 숨기기</td><td>클릭 선택 · <kbd>Shift</kbd>+클릭 추가 선택 · 빈 곳을 드래그하면 범위 안의 요소를 한꺼번에 선택. 선택한 요소를 드래그하거나 <kbd>방향키</kbd>(4px, <kbd>Shift</kbd>+방향키 20px)로 이동. 이동 모드에서 요소를 더블클릭하면 바로 텍스트 편집.</td></tr>
</table>
<h3>3. 편집 툴바</h3><table>
<tr><td>글자 작게 / 크게</td><td><kbd>Ctrl</kbd>+<kbd>[</kbd> / <kbd>Ctrl</kbd>+<kbd>]</kbd> — 선택한 요소(안의 글자 포함)를 10%씩</td></tr>
<tr><td>색상</td><td>선택한 요소의 글자색·선색·상자 테두리색을 바꿉니다</td></tr>
<tr><td>모션</td><td>선택한 요소의 등장 효과(없음 · 페이드업 · 줌인 · 왼쪽/오른쪽에서 · 팝 · 블러). 고르면 바로 미리보기.</td></tr>
<tr><td>정렬</td><td>선택한 텍스트 요소의 왼쪽 · 가운데 · 오른쪽 정렬</td></tr>
<tr><td>슬라이드 언어</td><td>툴바 오른쪽의 <b>원문 EN · 中文 · Tiếng Việt · မြန်မာ</b>에서 고르면 제목·상자·하단 문장 등 슬라이드 본문이 그 언어로 바뀝니다(오른쪽 한국어 패널은 그대로). 선택은 기억되며 편집 모드를 꺼도 유지됩니다. 저장되는 HTML은 항상 원문 기준이고, 번역 보기 중에 한 이동·크기·색·숨김 편집은 그대로 저장됩니다.</td></tr>
<tr><td>선택 요소 숨기기</td><td><kbd>Del</kbd> 또는 <kbd>H</kbd>. 편집 중에는 반투명으로 보이고, 발표에서는 사라집니다. 다시 누르면 복구.</td></tr>
<tr><td>숨긴 요소 모두 보이기</td><td>현재 슬라이드에서 숨긴 요소를 전부 복구</td></tr>
<tr><td>선택 요소 초기화</td><td>이동·크기·색·모션·숨김을 원래대로 (고친 글은 유지)</td></tr>
<tr><td>실행 취소 / 다시 실행</td><td><kbd>Ctrl</kbd>+<kbd>Z</kbd> / <kbd>Ctrl</kbd>+<kbd>Y</kbd> (최근 100단계). 텍스트 입력 중의 <kbd>Ctrl</kbd>+<kbd>Z</kbd>는 글자 단위로 되돌립니다.</td></tr>
<tr><td>HTML 저장</td><td><kbd>Ctrl</kbd>+<kbd>S</kbd> — 편집이 반영된 HTML 파일을 내려받습니다. 원본 파일 위에 덮어쓰면 어느 브라우저에서나 그대로 보입니다.</td></tr>
<tr><td>감추기</td><td>툴바를 숨기고 화면 전체로 슬라이드를 봅니다(편집 모드는 유지). 왼쪽 위 <b>☰ 메뉴</b>를 누르면 다시 나타나고, <kbd>E</kbd>로 편집 모드를 끄면 함께 사라집니다.</td></tr>
<tr><td>자동 저장</td><td>편집 내용은 이 브라우저에 자동 저장되어 새로고침해도 유지됩니다(같은 파일 · 같은 브라우저에서만). 모두 지우고 원본으로 돌아가려면 아래 버튼.</td></tr>
</table>
<p style="margin-top:10px"><button id="edWipe" style="font:inherit;font-weight:700;padding:6px 14px;border:2px solid #e33;color:#e33;background:#fff;border-radius:8px;cursor:pointer">편집 전체 초기화 (원본 복원)</button></p>
<h3>4. 강의 해설 화면 (<kbd>S</kbd>)</h3><table>
<tr><td>열기 / 닫기</td><td><kbd>S</kbd> 또는 <kbd>Esc</kbd>. 발표 중 언제든 열 수 있습니다.</td></tr>
<tr><td>언어</td><td>오른쪽 위에서 한국어 · English · 中文 · नेपाली · မြန်မာ · Tiếng Việt 선택. 선택은 기억됩니다.</td></tr>
<tr><td>따라가기</td><td>현재 슬라이드의 해설만 표시됩니다. <kbd>←</kbd> <kbd>→</kbd> 또는 화면의 ◀ ▶로 슬라이드를 넘기면 해설도 함께 바뀝니다.</td></tr>
</table>'''

BAR='''<div id="edbar" hidden>
  <span class="brand">EDIT</span>
  <button id="mText">텍스트 편집</button><button id="mMove" class="on">이동 · 숨기기</button>
  <span class="sep"></span>
  <button data-act="small">작게 Ctrl+[</button><button data-act="big">크게 Ctrl+]</button>
  <input type="color" id="edColor" value="#111111" title="글자·선 색상">
  <select id="edFx" title="등장 모션"><option value="">모션</option><option value="fx-none">없음</option><option value="fx-fade">페이드업</option><option value="fx-zoom">줌인</option><option value="fx-left">왼쪽에서</option><option value="fx-right">오른쪽에서</option><option value="fx-pop">팝</option><option value="fx-blur">블러</option></select>
  <select id="edAlign" title="정렬"><option value="">정렬</option><option value="left">왼쪽</option><option value="center">가운데</option><option value="right">오른쪽</option></select>
  <span class="sep"></span>
  <button data-act="hide">숨기기 Del</button><button data-act="unhide">모두 보이기</button><button data-act="reset">초기화</button>
  <span class="sep"></span>
  <button data-act="undo">취소 Ctrl+Z</button><button data-act="redo">다시 Ctrl+Y</button><button data-act="save">저장 Ctrl+S</button>
  <span class="sep"></span>
  <select id="edLang" class="lang" title="슬라이드 언어"><option value="en">원문 EN</option><option value="zh">中文</option><option value="vi">Tiếng Việt</option><option value="my">မြန်မာ</option></select>
  <button data-act="help">사용법 ?</button><button data-act="hidebar" title="툴바 감추기 (E 키로 편집 종료)">감추기</button>
  <span class="hint" id="edHint"></span>
</div>
<div id="edMarq"></div>
<button id="edShow" hidden title="툴바 보이기">☰ 메뉴</button>
<div id="narr" class="ov" hidden><div class="box"><div class="hd">강의 해설 <select id="narrLang"></select><button class="nv" data-nv="-1" title="이전 슬라이드">◀</button><span class="pos" id="narrPos"></span><button class="nv" data-nv="1" title="다음 슬라이드">▶</button><button class="x" data-close aria-label="닫기">✕</button></div><div class="bd" id="narrBody"></div></div></div>
<div id="edhelp" class="ov" hidden><div class="box"><div class="hd">사용법<button class="x" data-close aria-label="닫기">✕</button></div><div class="bd">'''+HELP+'''</div></div></div>
'''

JS='''<script>
/* ---- editor v2: E 키로 토글 ---- */
const ED={on:false,mode:'move',sel:[],undo:[],redo:[],cs:0};
const SEL='h1,.ko-title,.notes,.ko-notes,.node,.pill,.arrow,.vs,.nest,.art,.kp-title,.ko-panel p';
const KEY='deckedit:'+location.pathname;
const UNIT='h1,.notes,.node>div,.node>small,.pill>b,.pill>span,.nest>.nl';const ORIG=new WeakMap();let LANG='en';
const $=id=>document.getElementById(id);
const edbar=$('edbar'),edColor=$('edColor'),edFx=$('edFx'),edAlign=$('edAlign'),marq=$('edMarq'),narr=$('narr'),help=$('edhelp');
const HINT={move:'클릭 선택 · ⇧클릭 추가 · 빈 곳 드래그 범위 · 드래그/방향키 이동 · 더블클릭 텍스트',
  text:'요소 클릭 후 바로 입력 · Ctrl+B/I/U · 바깥 클릭 또는 Esc로 완료'};
function clean(s){const c=s.cloneNode(true);c.querySelectorAll('.ed-sel').forEach(x=>x.classList.remove('ed-sel'));
  c.querySelectorAll('[contenteditable]').forEach(x=>x.removeAttribute('contenteditable'));
  const a=s.querySelectorAll(UNIT),b=c.querySelectorAll(UNIT);a.forEach((el,i)=>{if(LANG!=='en'&&ORIG.has(el))b[i].innerHTML=ORIG.get(el)});
  c.querySelectorAll('[data-tk]').forEach(x=>x.removeAttribute('data-tk'));return c.innerHTML}
function snap(){ED.undo.push({i:cur,html:clean(slides[cur])});if(ED.undo.length>100)ED.undo.shift();ED.redo.length=0}
function save(){try{localStorage.setItem(KEY,JSON.stringify(slides.map(clean)))}catch(e){}}
function select(list){ED.sel.forEach(x=>x.classList.remove('ed-sel'));ED.sel=list;list.forEach(x=>x.classList.add('ed-sel'))}
function commitText(){document.querySelectorAll('[contenteditable]').forEach(el=>{if(document.activeElement===el)el.blur();else el.dispatchEvent(new Event('blur'))})}
function setMode(m){ED.mode=m;document.body.classList.toggle('mode-text',m==='text');document.body.classList.toggle('mode-move',m==='move');
  $('mText').classList.toggle('on',m==='text');$('mMove').classList.toggle('on',m==='move');$('edHint').textContent=HINT[m];
  if(m==='text')select([]);else commitText()}
function toggle(){ED.on=!ED.on;document.body.classList.toggle('editing',ED.on);edbar.hidden=!ED.on;$('edShow').hidden=true;
  if(ED.on)setMode(ED.mode);else{commitText();select([]);document.body.classList.remove('mode-text','mode-move')}}
function setPos(el,x,y){el.dataset.tx=x;el.dataset.ty=y;el.style.translate=x+'px '+y+'px'}
function move(el,dx,dy){setPos(el,(+el.dataset.tx||0)+dx,(+el.dataset.ty||0)+dy)}
function scaleFont(k){if(!ED.sel.length)return;snap();ED.sel.forEach(el=>[el,...el.querySelectorAll('*')].forEach(x=>{
  x.style.fontSize=(parseFloat(getComputedStyle(x).fontSize)*k).toFixed(1)+'px'}));save()}
function hideSel(){if(!ED.sel.length)return;snap();ED.sel.forEach(el=>el.classList.toggle('ed-hidden'));save()}
function unhideAll(){snap();slides[cur].querySelectorAll('.ed-hidden').forEach(el=>el.classList.remove('ed-hidden'));save()}
function resetSel(){if(!ED.sel.length)return;snap();ED.sel.forEach(el=>{[el,...el.querySelectorAll('*')].forEach(x=>x.removeAttribute('style'));
  delete el.dataset.tx;delete el.dataset.ty;el.className=el.className.replace(/\\b(fx-\\S+|ed-hidden)/g,'').replace(/\\s+/g,' ').trim()});save()}
function apply(u){select([]);slides[u.i].innerHTML=u.html;applyLang(slides[u.i]);show(u.i);save()}
function undo(){commitText();const u=ED.undo.pop();if(!u)return;ED.redo.push({i:u.i,html:clean(slides[u.i])});apply(u)}
function redo(){commitText();const u=ED.redo.pop();if(!u)return;ED.undo.push({i:u.i,html:clean(slides[u.i])});apply(u)}
function editText(el){if(el.isContentEditable||LANG!=='en')return;commitText();select([el]);const before=clean(slides[cur]),i=cur;
  el.contentEditable='true';el.focus();
  el.addEventListener('blur',()=>{el.removeAttribute('contenteditable');
    if(clean(slides[i])!==before){ED.undo.push({i,html:before});ED.redo.length=0;save()}},{once:true})}
function exportHtml(){
  commitText();
  const root=document.documentElement.cloneNode(true);
  root.querySelector('body').classList.remove('editing','mode-text','mode-move');
  root.querySelectorAll('.slide').forEach((s,i)=>s.innerHTML=clean(slides[i]));
  root.querySelector('#edbar').hidden=true;root.querySelector('#edShow').hidden=true;root.querySelectorAll('.ov').forEach(o=>o.hidden=true);
  const a=document.createElement('a');
  a.href=URL.createObjectURL(new Blob(['<!DOCTYPE html>\\n'+root.outerHTML],{type:'text/html'}));
  a.download=decodeURIComponent(location.pathname.split('/').pop())||'deck.html';a.click();
}
try{const st=JSON.parse(localStorage.getItem(KEY));if(st&&st.length===slides.length)slides.forEach((s,i)=>s.innerHTML=st[i])}catch(e){}

/* slide translation (toolbar select) */
const TR=(()=>{try{return JSON.parse($('trData').textContent)}catch(e){return {}}})();
const edLang=$('edLang');const normT=s=>s.replace(/\\s+/g,' ').trim();
[...edLang.options].forEach(o=>{if(o.value!=='en'&&!TR[o.value])o.text+=' (준비 중)'});
function applyLang(root){root.querySelectorAll(UNIT).forEach(el=>{
  if(LANG==='en'||!ORIG.has(el)){ORIG.set(el,el.innerHTML);el.dataset.tk=normT(el.textContent)}
  const t=edLang.value!=='en'&&TR[edLang.value]&&TR[edLang.value][el.dataset.tk];
  const h=t||ORIG.get(el);if(el.innerHTML!==h)el.innerHTML=h})}
function setLang(v){edLang.value=v;commitText();if(ED.on&&ED.mode==='text'&&v!=='en')setMode('move');
  applyLang(stage);LANG=v;$('mText').disabled=v!=='en';try{localStorage.setItem('deckSlideLang:'+location.pathname,v)}catch(e){}}
edLang.onchange=()=>setLang(edLang.value);
try{const v=localStorage.getItem('deckSlideLang:'+location.pathname);if(v&&v!=='en'&&TR[v])setLang(v)}catch(e){}

/* pointer: select / drag / marquee / text */
let drag=null;
stage.addEventListener('pointerdown',e=>{
  if(!ED.on||e.button!==0||e.target.isContentEditable)return;
  const el=e.target.closest(SEL),inSlide=!!el&&slides[cur].contains(el);
  if(ED.mode==='text'){if(inSlide&&!el.matches('.art'))editText(el);else commitText();return}
  e.preventDefault();
  if(!inSlide){if(!e.shiftKey)select([]);drag={marq:true,x:e.clientX,y:e.clientY,add:[...ED.sel]};return}
  if(e.shiftKey)select(ED.sel.includes(el)?ED.sel.filter(x=>x!==el):[...ED.sel,el]);else if(!ED.sel.includes(el))select([el]);
  drag={x:e.clientX,y:e.clientY,moved:false,base:ED.sel.map(el=>[+el.dataset.tx||0,+el.dataset.ty||0])};
});
addEventListener('pointermove',e=>{
  if(!drag)return;
  if(drag.marq){
    const x=Math.min(e.clientX,drag.x),y=Math.min(e.clientY,drag.y),w=Math.abs(e.clientX-drag.x),h=Math.abs(e.clientY-drag.y);
    if(w+h<4)return;Object.assign(marq.style,{display:'block',left:x+'px',top:y+'px',width:w+'px',height:h+'px'});
    const hit=[...slides[cur].querySelectorAll(SEL)].filter(el=>{const b=el.getBoundingClientRect();
      return b.width>0&&b.right>x&&b.left<x+w&&b.bottom>y&&b.top<y+h});
    select([...new Set([...drag.add,...hit.filter(el=>!hit.some(o=>o!==el&&o.contains(el)))])]);return}
  const s=+getComputedStyle(stage).getPropertyValue('--scale')||1;
  const dx=(e.clientX-drag.x)/s,dy=(e.clientY-drag.y)/s;
  if(!drag.moved){if(Math.hypot(dx,dy)<3)return;drag.moved=true;snap()}
  ED.sel.forEach((el,i)=>setPos(el,drag.base[i][0]+dx,drag.base[i][1]+dy));
});
addEventListener('pointerup',()=>{if(!drag)return;if(drag.marq)marq.style.display='none';else if(drag.moved)save();drag=null});
stage.addEventListener('dblclick',e=>{if(!ED.on||ED.mode!=='move')return;const el=e.target.closest(SEL);
  if(el&&slides[cur].contains(el)&&!el.matches('.art'))editText(el)});

/* toolbar */
const ACT={small:()=>scaleFont(1/1.1),big:()=>scaleFont(1.1),hide:hideSel,unhide:unhideAll,reset:resetSel,undo,redo,save:exportHtml,help:()=>{help.hidden=false},hidebar:()=>{edbar.hidden=true;$('edShow').hidden=false}};
$('edShow').onclick=()=>{edbar.hidden=false;$('edShow').hidden=true};
edbar.addEventListener('click',e=>{const b=e.target.closest('button');if(!b)return;
  if(b.id==='mText')setMode('text');else if(b.id==='mMove')setMode('move');else if(ACT[b.dataset.act])ACT[b.dataset.act]();b.blur()});
edColor.addEventListener('input',e=>{if(!ED.sel.length)return;if(!ED.cs){snap();ED.cs=1}
  ED.sel.forEach(el=>{el.style.color=e.target.value;el.style.setProperty('--ink',e.target.value)})});
edColor.addEventListener('change',()=>{ED.cs=0;save()});
edFx.addEventListener('change',e=>{const v=e.target.value;e.target.value='';if(!v||!ED.sel.length)return;snap();
  ED.sel.forEach(el=>{el.className=el.className.replace(/\\bfx-\\S+/g,'').replace(/\\s+/g,' ').trim();el.classList.add(v);
    el.style.animation='none';el.offsetHeight;el.style.animation=''});save()});
edAlign.addEventListener('change',e=>{const v=e.target.value;e.target.value='';if(!v||!ED.sel.length)return;snap();
  ED.sel.forEach(el=>el.style.textAlign=v);save()});
$('edWipe').onclick=()=>{if(confirm('이 브라우저에 저장된 편집 내용을 모두 지우고 원본으로 되돌립니다. 계속할까요?')){try{localStorage.removeItem(KEY)}catch(e){}location.reload()}};

/* narration overlay (S) */
const NARR=(()=>{try{return JSON.parse($('narrData').textContent)}catch(e){return {}}})();
const LANGS=[['ko','한국어'],['en','English'],['zh','中文'],['ne','नेपाली'],['my','မြန်မာ'],['vi','Tiếng Việt']];
const narrLang=$('narrLang');
LANGS.forEach(([c,n])=>narrLang.add(new Option(n+(NARR[c]?'':' (준비 중)'),c)));
try{narrLang.value=localStorage.getItem('deckNarrLang')||'ko'}catch(e){}
if(!narrLang.value)narrLang.value='ko';
narrLang.onchange=()=>{try{localStorage.setItem('deckNarrLang',narrLang.value)}catch(e){}renderNarr()};
const esc=s=>s.replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
function renderNarr(){const arr=NARR[narrLang.value],bd=$('narrBody');$('narrPos').textContent=(cur+1)+' / '+slides.length;
  if(!arr){bd.innerHTML='<p>이 언어의 해설은 아직 준비되지 않았습니다.</p>';return}
  const s=arr[cur]||'',k=s.indexOf('\\n'),h=k<0?s:s.slice(0,k),b=k<0?'':s.slice(k+1).replace(/^\\n+/,'');
  bd.innerHTML='<div class="nb cur"><b>'+esc(h)+'</b>'+esc(b)+'</div>';bd.scrollTop=0}
function narrSync(){renderNarr()}
function toggleNarr(){narr.hidden=!narr.hidden;if(!narr.hidden)renderNarr()}
document.querySelectorAll('#narr .nv').forEach(b=>b.onclick=()=>show(cur+(+b.dataset.nv)));
document.querySelectorAll('[data-close]').forEach(b=>b.onclick=()=>{b.closest('.ov').hidden=true});
document.querySelectorAll('.ov').forEach(o=>o.addEventListener('click',e=>{if(e.target===o)o.hidden=true}));
const _showV1=show;show=function(n){_showV1(n);if(!narr.hidden)narrSync()};

/* keys */
addEventListener('keydown',e=>{
  const mod=e.ctrlKey||e.metaKey,t=e.target.isContentEditable,tag=e.target.tagName;
  if(tag==='SELECT'||tag==='INPUT')return;
  if(!t&&!mod){
    if(e.key==='e'||e.key==='E'||e.key==='ㄷ'){toggle();return}
    if(e.key==='s'||e.key==='S'||e.key==='ㄴ'){toggleNarr();return}
    if(e.key==='?'){help.hidden=!help.hidden;return}
    if(e.key==='Escape'&&(!narr.hidden||!help.hidden)){narr.hidden=help.hidden=true;return}
  }
  if(!ED.on)return;
  if(t&&mod&&/^[zyZY]$/.test(e.key))return;
  if(mod&&(e.key==='z'||e.key==='Z')){e.preventDefault();e.shiftKey?redo():undo();return}
  if(mod&&(e.key==='y'||e.key==='Y')){e.preventDefault();redo();return}
  if(mod&&(e.key==='s'||e.key==='S')){e.preventDefault();exportHtml();return}
  if(mod&&(e.key===']'||e.key==='[')){e.preventDefault();scaleFont(e.key===']'?1.1:1/1.1);return}
  if(t){if(e.key==='Escape')e.target.blur();return}
  if(e.key==='Escape'){select([]);return}
  if(!ED.sel.length)return;
  if(e.key==='h'||e.key==='H'||e.key==='ㅗ'||e.key==='Delete'||e.key==='Backspace'){e.preventDefault();hideSel();return}
  const st=e.shiftKey?20:4,mv={ArrowLeft:[-st,0],ArrowRight:[st,0],ArrowUp:[0,-st],ArrowDown:[0,st]}[e.key];
  if(mv){e.preventDefault();snap();ED.sel.forEach(el=>move(el,mv[0],mv[1]));save()}
});
</script>
'''

def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(a[:50],s.count(a)); s=s.replace(a,b)

rep('</style>\n</head>', CSS+'</style>\n</head>')
rep(KH+'\n', KH+'\n'+BAR)
# guards on original handlers (fresh template or already patched)
G1="if(e.target.isContentEditable||(ED.on&&ED.sel.length))return;"
if G1 not in s:
    a="addEventListener('keydown',e=>{\n  if(e.key==='ArrowRight'"; assert s.count(a)==1,('nav keydown anchor',s.count(a))
    s=s.replace(a,"addEventListener('keydown',e=>{\n  "+G1+"\n  if(e.key==='ArrowRight'")
if "closest('#nav,.ov')" not in s:
    a="if(e.target.closest('#nav'))return;"; a2="if(ED.on||e.target.closest('#nav'))return;"
    if a2 in s: s=s.replace(a2,"if(ED.on||e.target.closest('#nav,.ov'))return;")
    else: assert s.count(a)==1,('click anchor',s.count(a)); s=s.replace(a,"if(ED.on||e.target.closest('#nav,.ov'))return;")
if "closest('.ov')?null" not in s:
    a="addEventListener('touchstart',e=>tx=e.touches[0].clientX);"; assert s.count(a)==1,('touch anchor',s.count(a))
    s=s.replace(a,"addEventListener('touchstart',e=>tx=e.target.closest('.ov')?null:e.touches[0].clientX);")
a="addEventListener('keydown',e=>{if(e.key==='n'"
if a in s: s=s.replace(a,"addEventListener('keydown',e=>{if(e.target.isContentEditable||e.ctrlKey||e.metaKey)return;if(e.key==='n'")
rep('</script>\n</body>', '</script>\n'+NARR+TRD+JS+'</body>')
io.open(p,'w',encoding='utf-8').write(s)
print('ok',os.path.basename(p),len(s))
