# usage: python3 check_units.py SRC.json OUT.json  -> validates keys and tag sequences
import json,re,sys,io
src=json.load(io.open(sys.argv[1],encoding='utf-8'));out=json.load(io.open(sys.argv[2],encoding='utf-8'))
tags=lambda h:re.findall(r'<[^>]+>',h)
missing=[u['k'] for u in src if u['k'] not in out]
bad=[u['k'] for u in src if u['k'] in out and tags(u['h'])!=tags(out[u['k']])]
empty=[k for k,v in out.items() if not v.strip()]
same=[u['k'] for u in src if out.get(u['k'])==u['h'] and len(u['k'])>12]
print('src',len(src),'out',len(out),'missing',len(missing),'tag-mismatch',len(bad),'empty',len(empty),'untranslated',len(same))
for k in (missing+bad+empty+same)[:10]: print('  ',k[:80])
sys.exit(0 if not(missing or bad or empty) else 1)
