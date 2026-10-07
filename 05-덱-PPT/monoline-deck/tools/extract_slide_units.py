import re,io,json,html,sys,os
def norm(h): return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>','',h))).strip()
for p in sys.argv[1:]:
    s=io.open(p,encoding='utf-8').read()
    secs=re.findall(r'<section class="slide[^"]*"[^>]*>(.*?)</section>',s,re.S)
    units=[];seen=set()
    def add(h):
        k=norm(h)
        if k and k not in seen: seen.add(k);units.append({'k':k,'h':h})
    for sec in secs:
        for m in re.finditer(r'<h1 class="in">(.*?)</h1>',sec): add(m.group(1))
        for m in re.finditer(r'<div class="notes[^"]*">(.*?)</div>',sec): add(m.group(1))
        for m in re.finditer(r'<div class="node[^"]*"><div>(.*?)</div>(?:<small>(.*?)</small>)?',sec):
            add(m.group(1)); 
            if m.group(2): add(m.group(2))
        for m in re.finditer(r'<div class="pill[^"]*"><b>(.*?)</b>(?:<span>(.*?)</span>)?',sec):
            add(m.group(1));
            if m.group(2): add(m.group(2))
        for m in re.finditer(r'<div class="nl">(.*?)</div>',sec): add(m.group(1))
    base=os.path.basename(p).split('_monoline')[0]
    out=os.path.join(os.path.dirname(p),'_slides_%s.json'%base)
    json.dump(units,io.open(out,'w',encoding='utf-8'),ensure_ascii=False,indent=1)
    print(base,len(secs),'slides',len(units),'units',sum(len(u['h']) for u in units),'chars')
