"""Batch retranslate English fallbacks with OPUS-MT through CTranslate2."""
import json,re
from pathlib import Path
import ctranslate2
from transformers import AutoTokenizer

ROOT=Path('docs/data');MODEL='Helsinki-NLP/opus-mt-tc-big-en-fr';CT=Path('/tmp/opus-en-fr-ct2')
tokenizer=AutoTokenizer.from_pretrained(MODEL)
if not (CT/'model.bin').exists():
 ctranslate2.converters.TransformersConverter(MODEL).convert(str(CT),quantization='int8',force=True)
translator=ctranslate2.Translator(str(CT),device='cpu',compute_type='int8',intra_threads=6)
PROTECTED=re.compile(r'([\u0370-\u03ff\u1f00-\u1fff\u0590-\u05ff\u0300-\u036f]+|\b[GH]\d+\b|\b[123]?[A-Z][a-z]{1,7}\.\d+(?::\d+)?)')
BAD=re.compile(r'Passage conservé|commission européenne|consommation de drogues|stratégie de Lisbonne|Non, non, non',re.I)
plans={};segments={}

def plan(text):
 if text in plans:return plans[text]
 result=[]
 for line in text.splitlines(keepends=True):
  for i,part in enumerate(PROTECTED.split(line)):
   if not part:continue
   if i%2 or not re.search('[A-Za-z]{2}',part):result.append(('keep',part));continue
   words=part.split();chunks=[];current=[]
   for word in words:
    if current and len(tokenizer.encode(' '.join(current+[word])))>150:chunks.append(' '.join(current));current=[]
    current.append(word)
   if current:chunks.append(' '.join(current))
   for n,chunk in enumerate(chunks):
    if n:result.append(('keep',' '))
    result.append(('tr',chunk));segments.setdefault(chunk,tokenizer.convert_ids_to_tokens(tokenizer.encode(chunk)))
 plans[text]=result;return result

targets=[]
for path in sorted(ROOT.glob('lex-fr-*.json')):
 data=json.loads(path.read_text());source=json.loads((ROOT/path.name.replace('lex-fr-','lex-')).read_text())
 for key,entries in data.items():
  for i,entry in enumerate(entries):
   if BAD.search(entry['definition_fr']):
    original=source[key][i]['definition'];plan(original);targets.append((path,key,i,original))
items=list(segments.items());translated={}
print(f'{len(targets)} définitions, {len(items)} segments uniques',flush=True)
for start in range(0,len(items),48):
 batch=items[start:start+48]
 results=translator.translate_batch([tokens for _,tokens in batch],beam_size=3,max_decoding_length=320,no_repeat_ngram_size=3,max_batch_size=2048,batch_type='tokens')
 for (text,_),res in zip(batch,results):
  value=tokenizer.decode(tokenizer.convert_tokens_to_ids(res.hypotheses[0]),skip_special_tokens=True).strip()
  if not value:raise ValueError('empty translation: '+text)
  translated[text]=value
 if start%480==0:print(f'{start+len(batch)}/{len(items)}',flush=True)

def render(text):return ''.join(value if kind=='keep' else translated[value] for kind,value in plan(text)).strip()
by_path={}
for path,key,i,original in targets:by_path.setdefault(path,[]).append((key,i,original))
for path,rows in by_path.items():
 data=json.loads(path.read_text())
 for key,i,original in rows:
  entry=data[key][i];entry['definition_fr']=render(original);entry['translation_engine']='Helsinki-NLP opus-mt-tc-big-en-fr / CTranslate2 int8 ; non révisé';entry.pop('quality_fallback',None)
 path.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n')
print('Retraductions:',len(targets))
