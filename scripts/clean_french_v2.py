"""Clean French glosses, add concise summaries, and apply checked key entries."""
import json, re
from pathlib import Path

ROOT = Path('docs/data')

EDITORIAL = {
 'G3056': ('parole ; discours ; raison', 'Parole exprimant une pensée, discours ou message ; selon le contexte, raison ou compte rendu. Dans Jean 1, le terme désigne la Parole, le Logos.'),
 'G2316': ('Dieu ; dieu ; divinité', 'Désigne Dieu ou, selon le contexte, un dieu ou une divinité. Le mot seul ne signifie pas « mon Dieu » : cette expression suppose un possessif.'),
 'H3068': ('YHWH ; Yahvé ; l’Éternel', 'Nom propre du Dieu d’Israël, écrit avec les quatre consonnes YHWH. « Yahvé » est une restitution usuelle ; la Segond le rend généralement par « l’Éternel ». « Jéhovah » est une forme traditionnelle plus tardive.'),
 'H3069': ('YHWH ; Yahvé', 'Même nom divin YHWH, avec une vocalisation particulière liée à la lecture traditionnelle « Elohim ». Ce numéro ne désigne pas une autre divinité.'),
 'H430': ('Dieu ; dieux', 'Forme plurielle hébraïque employée notamment pour le Dieu d’Israël, avec un accord souvent singulier, ou pour des dieux. Le contexte et la syntaxe déterminent le sens.'),
 'G3588': ('le ; la ; les', 'Article défini grec. Il peut aussi introduire une expression correspondant à « celui qui » ou « ceux qui ».'),
 'G2532': ('et ; aussi ; même', 'Relie des mots ou des propositions. Peut aussi marquer l’addition ou l’insistance selon le contexte.'),
 'G846': ('il ; elle ; lui ; même', 'Pronom dont le sens dépend de sa place : il, elle, lui, elle-même, ou « le même ».'),
 'G1161': ('mais ; et ; or', 'Particule de liaison marquant souvent une transition ou une opposition légère.'),
 'G1510': ('être', 'Verbe « être » : exprime l’existence, l’identité ou un état.'),
 'G1722': ('dans ; en ; parmi', 'Préposition suivie du datif : indique notamment un lieu, une situation, un moyen ou un domaine.'),
 'G1519': ('vers ; dans ; pour', 'Préposition indiquant souvent une direction, une destination ou un but.'),
 'G3756': ('ne… pas ; non', 'Négation grecque employée pour nier une affirmation.'),
 'G3361': ('ne… pas ; non', 'Négation employée notamment avec les ordres, les souhaits et diverses constructions non affirmatives.'),
 'G3739': ('qui ; que ; lequel', 'Pronom relatif reliant une proposition à ce qui précède.'),
 'G3956': ('tout ; chaque', 'Exprime la totalité ou considère chaque élément d’un ensemble.'),
 'G1063': ('car ; en effet', 'Introduit généralement une explication ou une justification.'),
 'G2036': ('dire ; parler', 'Rapporte des paroles ou une déclaration.'),
 'G1909': ('sur ; à ; contre', 'Préposition aux sens variés selon le cas grammatical : position, direction, relation ou opposition.'),
 'G26': ('amour', 'Amour, bienveillance ou attachement. Le contexte en précise l’objet et la portée.'),
 'G4102': ('foi ; confiance ; fidélité', 'Peut exprimer la confiance, la foi ou la fidélité selon le passage.'),
 'G5485': ('grâce ; faveur', 'Faveur ou bienveillance accordée ; peut aussi exprimer la reconnaissance.'),
 'G4151': ('souffle ; esprit', 'Souffle ou esprit. Selon le contexte : esprit humain, être spirituel ou Esprit de Dieu.'),
 'H5921': ('sur ; au-dessus de ; contre', 'Préposition exprimant notamment la position, la relation ou l’opposition.'),
 'H559': ('dire', 'Dire ou exprimer quelque chose.'),
 'H3605': ('tout ; chaque ; totalité', 'Exprime la totalité ou chaque élément d’un ensemble.'),
 'H1121': ('fils ; descendant', 'Fils ou descendant ; peut aussi exprimer l’appartenance à un peuple ou à une catégorie.'),
 'H1961': ('être ; devenir ; arriver', 'Exprime l’existence, le devenir ou la survenue d’un événement.'),
 'H776': ('terre ; pays', 'Terre, pays ou territoire ; peut désigner le monde ou une région déterminée.'),
 'H1697': ('parole ; chose ; affaire', 'Parole ou propos ; peut aussi désigner une chose, un événement ou une affaire.'),
 'H1': ('père ; ancêtre', 'Père au sens familial, ancêtre ou figure d’origine.'),
 'H7307': ('vent ; souffle ; esprit', 'Vent, souffle ou esprit ; le contexte distingue la réalité naturelle, humaine ou divine.'),
 'H5315': ('être vivant ; vie ; âme', 'Être vivant, personne, vie ou désir selon le contexte ; ne désigne pas toujours une âme séparée du corps.'),
 'H7225': ('commencement ; prémices', 'Ce qui vient en premier dans le temps, l’ordre ou le rang ; notamment les prémices.'),
}
EDITORIAL_DEFINITIONS = {
 'H3068': 'YHWH (יהוה), nom propre du Dieu d’Israël. Le dictionnaire anglais de Strong emploie la forme traditionnelle « Jehovah » et rattache ce nom à H1961 (הָיָה), « être », avec l’explication « celui qui existe » ou « l’Éternel ». Cette étymologie appartient au dictionnaire source et ne tranche pas à elle seule la question historique de la formation du nom.\nDans la KJV : Jehovah, LORD. Comparer H3050 (יָהּ) et H3069 (יְהֹוִה).',
 'H3069': 'Variante écrite de YHWH (יהוה), nom propre du Dieu d’Israël, avec une vocalisation particulière liée à la lecture traditionnelle Elohim (אֱלֹהִים, H430), par analogie avec Adonaï (אֲדֹנָי, H136). Comparer H3068 (יְהֹוָה), H136 (אֲדֹנָי) et H430 (אֱלֹהִים).'
}

def normalize(text):
 return re.sub(r'\s+', ' ', text.replace('▁',' ').replace('_',' ')).strip()

def short_gloss(text):
 text=normalize(text)
 if len(text)<=60:return text
 candidate=re.sub(r'\([^()]*\)', '', text)
 candidate=re.sub(r'^(properly|proprement|literally|littéralement|by implication|par implication)\s*[,;:]?\s*','',candidate,flags=re.I)
 candidate=normalize(re.split(r'[;:]|,(?=\s)',candidate)[0]).rstrip(' .')
 if len(candidate)>60:candidate=candidate[:59].rsplit(' ',1)[0].rstrip(' ,;:')+'…'
 return candidate or text[:59].rstrip()+'…'

stats={'variants':0,'leading_spaces_removed':0,'long_glosses_condensed':0,'editorial_entries':0,'summaries_added':0}
for path in sorted(ROOT.glob('lex-fr-*.json')):
 data=json.loads(path.read_text())
 for key,entries in data.items():
  for entry in entries:
   stats['variants']+=1
   raw=entry['gloss_fr']; expanded=normalize(raw)
   stats['leading_spaces_removed']+=raw!=raw.lstrip()
   stats['long_glosses_condensed']+=len(expanded)>60
   entry['gloss_expanded_fr']=expanded
   entry['gloss_fr']=short_gloss(expanded)
   entry['summary_fr']=expanded if len(expanded)<=240 else expanded[:239].rsplit(' ',1)[0].rstrip(' ,;:')+'…'
   entry['summary_method']='extrait automatique de la glose française ; non révisé'
   if key in EDITORIAL and len(entries)==1:
    entry['gloss_fr'],entry['summary_fr']=EDITORIAL[key]
    entry['summary_method']='résumé éditorial assisté par IA, vérifié avec la source anglaise ; non révisé scientifiquement'
    entry['editorial_revision']='2026-11-09';stats['editorial_entries']+=1
   if key in EDITORIAL_DEFINITIONS and len(entries)==1:
    entry['definition_fr']=EDITORIAL_DEFINITIONS[key]
   assert entry['gloss_fr']==entry['gloss_fr'].strip() and 0<len(entry['gloss_fr'])<=60,(key,entry['gloss_fr'])
   stats['summaries_added']+=1
 path.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n')
(ROOT/'french-revision-report.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(stats,ensure_ascii=False))

