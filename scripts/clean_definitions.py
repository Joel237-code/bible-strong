"""Nettoie la mise en forme des définitions françaises : « _ » résiduels, lettres collées à l'hébreu, références collées au mot suivant. Idempotent."""
import json,re
from pathlib import Path
HEB=r'[\u0590-\u05ff]'
def fix(t):
    t=t.replace('▁',' ')
    t=re.sub(r'__+','\n',t).replace('_',' ')
    t=re.sub(r'([A-Za-zÀ-ÿ.,;:)\]])(?=%s)'%HEB,r'\1 ',t)      # lettre latine -> hébreu
    t=re.sub(r'(%s)(?=[A-Za-zÀ-ÿ(\[])'%HEB,r'\1 ',t)            # hébreu -> lettre latine
    t=re.sub(r'(\d:\d+)(?=[a-zà-ÿ]{3,})',r'\1 ',t)               # Act.19:37seulement
    t=re.sub(r'[ \t]{2,}',' ',t); t=re.sub(r' *\n *','\n',t)
    return t.strip()
n=0
for p in sorted(Path('docs/data').glob('lex-fr-*.json')):
    d=json.loads(p.read_text(encoding='utf-8')); ch=False
    for es in d.values():
        for e in es:
            new=fix(e['definition_fr'])
            if new!=e['definition_fr']: e['definition_fr']=new; n+=1; ch=True
    if ch: p.write_text(json.dumps(d,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
print(n,'définitions nettoyées')
