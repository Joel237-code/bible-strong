"""Normalize Argos SentencePiece output and correct checked sample entries."""
import json,re
from pathlib import Path
root=Path('docs/data'); unchanged=0
for path in root.glob('lex-fr-*.json'):
    data=json.loads(path.read_text())
    for key,variants in data.items():
        for entry in variants:
            for field in ('gloss_fr','definition_fr'):
                entry[field]=entry[field].replace('▁',' ').replace('_',' ')
            # KJV is a named source, not the Louis Segond Bible (LS).
            if key.startswith('H'):
                lines=entry['definition_fr'].split('\n')
                if len(lines)>1:
                    last=lines[-1]
                    if ':' in last:lines[-1]='Équivalents KJV (traduits) : '+last.split(':',1)[1].strip()
                    entry['definition_fr']='\n'.join(lines)
            unchanged+=entry['definition_fr'].count('[Passage conservé en anglais :')
    if 'G2841' in data:
        e=data['G2841'][0];e['gloss_fr']='participer ; partager'
        e['definition_fr']='κοινωνέω, -ῶ\n[Dans la Septante : 2Ch.20:35, Job.34:8, Ecc.9:4 (חָבַר), Pro.1:11, Wis.6:23, Sir.13:1, et ailleurs.]\nAvoir part à quelque chose ; partager quelque chose avec quelqu’un ; prendre part. Avec le génitif de la chose (comme habituellement en grec classique ; voir aussi Pr, passage cité, avec) : Heb.2:14. Avec le datif de la chose : Rom.12:13 15:27, 1Ti.5:22, 1Pe.4:13, 2Jn.11. Avec le datif de la personne, devant εἰς : Php.4:15 ; avec ἐν : Gal.6:6 (comparer συν-κοινωνέω).†\n(AS)'
        e['post_edit']='French wording adjusted with AI; no independent scholarly review'
    if 'H430' in data:
        e=data['H430'][0];e['gloss_fr']='dieux au sens ordinaire ; employé notamment pour le Dieu suprême'
        e['definition_fr']='Pluriel de H433 (אֱלוֹהַּ).\n« Dieux » au sens ordinaire ; employé spécialement, sous cette forme plurielle et en particulier avec l’article, pour désigner le Dieu suprême. Parfois appliqué par déférence à des magistrats ; parfois employé comme superlatif.\nÉquivalents KJV (traduits) : anges ; [idiome] extrêmement ; Dieu, dieux, déesse ; [idiome] très grands ; juges ; [idiome] puissants.'
        e['post_edit']='French wording adjusted with AI; no independent scholarly review'
    source=json.loads((root/path.name.replace('lex-fr-','lex-')).read_text())
    for key,variants in data.items():
        for original,entry in zip(source[key],variants):
            for field in ('gloss','definition'):
                text=entry[field+'_fr']
                protected=re.findall(r'[\u0370-\u03ff\u1f00-\u1fff\u0590-\u05ff]+|\b[GH]\d+\b|\b[123]?[A-Z][a-z]{1,7}\.\d+(?::\d+)?',original[field])
                suspect=any(token not in text for token in protected) or re.search(r'règlement|commission européenne|aisselles|génitaux|stratégie de Lisbonne|États-Unis d.Amérique',text,re.I)
                if suspect:
                    entry[field+'_fr']='[Passage conservé en anglais après contrôle automatique :]\n'+original[field]
                    entry['quality_fallback']=True
    path.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n')
print(f'Normalized French typography; {unchanged} definition passages explicitly retained in English.')
