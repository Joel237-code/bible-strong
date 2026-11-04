"""Translate EN lexicons to FR with Argos EN-FR 1.9 / CTranslate2, preserving variants.
No external translation API: inference runs on the GitHub runner. Originals stay unchanged.
"""
import argparse, hashlib, json, re, time, urllib.request, zipfile
from pathlib import Path

def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, separators=(',', ':'))+'\n', encoding='utf-8')

def main():
    import ctranslate2, sentencepiece
    parser=argparse.ArgumentParser();parser.add_argument('--shard',type=int,required=True);parser.add_argument('--shards',type=int,default=8)
    args=parser.parse_args(); root=Path('docs/data'); out=Path('translated');out.mkdir(exist_ok=True)
    archive=Path('/tmp/argos-en-fr.argosmodel')
    urllib.request.urlretrieve('https://data.argosopentech.com/argospm/v1/translate-en_fr-1_9.argosmodel',archive)
    model_sha=hashlib.sha256(archive.read_bytes()).hexdigest()
    with zipfile.ZipFile(archive) as z:z.extractall('/tmp/argos-en-fr')
    sp_path=next(Path('/tmp/argos-en-fr').rglob('sentencepiece.model')); pkg=sp_path.parent
    sp=sentencepiece.SentencePieceProcessor(model_file=str(sp_path))
    translator=ctranslate2.Translator(str(pkg/'model'), device='cpu', compute_type='int8', inter_threads=2, intra_threads=2)
    metadata=json.loads((pkg/'metadata.json').read_text());prefix=metadata.get('target_prefix','')
    # Keep Greek/Hebrew expressions, Strong IDs and Scripture references literally intact.
    protected=re.compile(r'([\u0370-\u03ff\u1f00-\u1fff\u0590-\u05ff]+(?:[\s\u0300-\u036f]*[\u0370-\u03ff\u1f00-\u1fff\u0590-\u05ff]+)*|\b[GH]\d+[A-Za-z]*\b|\b[123]?[A-Z][a-z]{1,7}\.\d+(?:[:.]\d+)?(?:[-;,]\s*\d+(?:[:.]\d+)?)*)')
    texts={}; plans={}
    def parts(text):
        if text in plans:return plans[text]
        result=[]
        for para in text.splitlines(keepends=True):
            for i,fragment in enumerate(protected.split(para)):
                if not fragment:continue
                if i%2 or not re.search('[A-Za-z]{2}',fragment):result.append(('keep',fragment));continue
                leading=fragment[:len(fragment)-len(fragment.lstrip())];trailing=fragment[len(fragment.rstrip()):]
                if leading:result.append(('keep',leading))
                core=fragment.strip()
                # Hard token bound avoids silent truncation of long dictionary entries.
                tokens=sp.encode(core,out_type=str)
                if len(tokens)<=180:segments=[core]
                else:
                    segments=[];current=[]
                    for word in core.split():
                        if current and len(sp.encode(' '.join(current+[word])))>180:segments.append(' '.join(current));current=[]
                        current.append(word)
                    if current:segments.append(' '.join(current))
                for n,segment in enumerate(segments):
                    if n:result.append(('keep',' '))
                    texts.setdefault(segment,sp.encode(segment,out_type=str));result.append(('translate',segment))
                if trailing:result.append(('keep',trailing))
        plans[text]=result;return result
    paths=sorted(root.glob('lex-[GH]*.json'));selected=[p for i,p in enumerate(paths) if i%args.shards==args.shard]
    sources={p.name:json.loads(p.read_text()) for p in selected}
    for source in sources.values():
        for entries in source.values():
            for e in entries:
                parts(e.get('gloss',''));parts(e.get('definition',''))
    translated={};items=list(texts.items());start=time.time()
    print(f'Shard {args.shard}: {len(selected)} files, {len(items)} unique segments',flush=True)
    for offset in range(0,len(items),64):
        batch=items[offset:offset+64]
        results=translator.translate_batch([x[1] for x in batch],target_prefix=[[prefix]]*len(batch) if prefix else None,beam_size=2,max_batch_size=2048,batch_type='tokens',max_input_length=0,max_decoding_length=768,replace_unknowns=True)
        for (text,_),res in zip(batch,results):
            value=sp.decode(res.hypotheses[0]).strip()
            if prefix and value.startswith(prefix):value=value[len(prefix):].strip()
            if not value and text:raise ValueError('Empty translation: '+text)
            if len(res.hypotheses[0])>=768:raise ValueError('Output reached decoding limit')
            translated[text]=value
        if offset%640==0:print(f'{offset+len(batch)}/{len(items)} segments; {time.time()-start:.0f}s',flush=True)
    def render(text):return ''.join(value if kind=='keep' else translated[value] for kind,value in parts(text))
    count=0
    for filename,source in sources.items():
        result={}
        for key,entries in source.items():
            result[key]=[{'variant':e.get('variant',key),'gloss_fr':render(e.get('gloss','')),'definition_fr':render(e.get('definition','')),'source_sha256':hashlib.sha256(json.dumps(e,ensure_ascii=False,sort_keys=True).encode()).hexdigest()} for e in entries];count+=len(entries)
        dump(out/filename.replace('lex-','lex-fr-'),result)
    dump(out/f'metadata-{args.shard}.json',{'engine':'Argos Translate EN-FR 1.9 / CTranslate2 int8','model_sha256':model_sha,'variants':count,'files':len(selected),'status':'machine-translated, not independently reviewed'})
    for key in ['G2841','G3056','G26','H430','H1','H7225']:
        for source in sources.values():
            if key in source:print('SAMPLE',key,json.dumps([{'en':e['gloss'],'fr':render(e['gloss']),'definition_fr':render(e['definition'])} for e in source[key]],ensure_ascii=False),flush=True)
    print(f'Completed {count} variants in {time.time()-start:.0f}s',flush=True)
if __name__=='__main__':main()
