import runpy
runpy.run_path('scripts/finalize_french.py',run_name='__main__')
import json,re,hashlib
from pathlib import Path
root=Path('docs/data'); count=variants=0
for path in sorted(root.glob('lex-[GH]*.json')):
    source=json.loads(path.read_text()); target=json.loads((root/path.name.replace('lex-','lex-fr-')).read_text())
    assert set(source)==set(target),path
    for key,entries in source.items():
        count+=1;assert len(entries)==len(target[key]),key
        for e,f in zip(entries,target[key]):
            variants+=1;assert f['variant']==e['variant'],key
            assert f['source_sha256']==hashlib.sha256(json.dumps(e,ensure_ascii=False,sort_keys=True).encode()).hexdigest(),key
            for field in ['gloss','definition']:
                assert not e[field].strip() or f[field+'_fr'].strip(),key
                for token in re.findall(r'[\u0370-\u03ff\u1f00-\u1fff\u0590-\u05ff]+|\b[GH]\d+\b',e[field]):assert token in f[field+'_fr'],(key,token)
print(f'PASS: {count} Strong keys, {variants} variants, source hashes and original-language tokens preserved.')
