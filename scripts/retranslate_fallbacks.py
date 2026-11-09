"""Retranslate definitions explicitly retained in English using OPUS-MT EN-FR."""
import json,re
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

ROOT=Path('docs/data'); MODEL='Helsinki-NLP/opus-mt-tc-big-en-fr'
tokenizer=AutoTokenizer.from_pretrained(MODEL);model=AutoModelForSeq2SeqLM.from_pretrained(MODEL)
PROTECTED=re.compile(r'([\u0370-\u03ff\u1f00-\u1fff\u0590-\u05ff\u0300-\u036f]+|\b[GH]\d+\b|\b[123]?[A-Z][a-z]{1,7}\.\d+(?::\d+)?)')

def translate(text):
 parts=[];sentences=[]
 for line in text.splitlines(keepends=True):
  for i,part in enumerate(PROTECTED.split(line)):
   if not part:continue
   if i%2 or not re.search('[A-Za-z]{2}',part):parts.append(('keep',part));continue
   words=part.split();chunks=[];current=[]
   for word in words:
    if current and len(tokenizer(' '.join(current+[word])).input_ids)>160:chunks.append(' '.join(current));current=[]
    current.append(word)
   if current:chunks.append(' '.join(current))
   for n,chunk in enumerate(chunks):
    if n:parts.append(('keep',' '))
    parts.append(('tr',len(sentences)));sentences.append(chunk)
 if sentences:
  out=[]
  for start in range(0,len(sentences),16):
   batch=sentences[start:start+16];enc=tokenizer(batch,return_tensors='pt',padding=True,truncation=False)
   ids=model.generate(**enc,num_beams=4,max_new_tokens=280,no_repeat_ngram_size=3)
   out.extend(tokenizer.batch_decode(ids,skip_special_tokens=True))
 else:out=[]
 return ''.join(value if kind=='keep' else out[value].strip() for kind,value in parts).strip()

count=0
for path in sorted(ROOT.glob('lex-fr-*.json')):
 data=json.loads(path.read_text());source=json.loads((ROOT/path.name.replace('lex-fr-','lex-')).read_text());changed=False
 for key,entries in data.items():
  for i,entry in enumerate(entries):
   if 'Passage conservé' in entry['definition_fr']:
    entry['definition_fr']=translate(source[key][i]['definition'])
    entry['translation_engine']='Helsinki-NLP opus-mt-tc-big-en-fr; non révisé';entry.pop('quality_fallback',None)
    count+=1;changed=True
 if changed:path.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n')
 print(path.name,count,flush=True)
print('Retraductions:',count)
