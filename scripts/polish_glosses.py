"""Nettoie les gloses françaises (espaces, longueur) et applique des gloses révisées pour les mots les plus fréquents.
Idempotent : peut être relancé sans effet supplémentaire. La glose d'origine est conservée dans `gloss_fr_auto`."""
import json,re,unicodedata
from pathlib import Path
root=Path('docs/data')
# (lemme attendu, glose française). Le lemme sert de garde-fou contre une erreur de numéro.
OVERRIDES={
'G3588':('ὁ','le ; la ; les (article)'),
'G2532':('καί','et ; aussi ; même'),
'G846':('αὐτός','lui ; elle ; même (pronom)'),
'G1161':('δέ','mais ; or ; et'),
'G1510':('εἰμί','être ; exister'),
'G1722':('ἐν','en ; dans ; parmi'),
'G1519':('εἰς','vers ; dans ; pour'),
'G3756':('οὐ','ne… pas ; non'),
'G3004':('λέγω','dire ; parler'),
'G3739':('ὅς','qui ; lequel (pronom relatif)'),
'G2316':('θεός','Dieu ; dieu'),
'G3754':('ὅτι','que ; parce que'),
'G3956':('πᾶς','tout ; chaque'),
'G1063':('γάρ','car ; en effet'),
'G2424':('Ἰησοῦς','Jésus'),
'G3361':('μή','ne… pas (négation)'),
'G2036':('εἶπον','dire'),
'G3056':('λόγος','parole ; mot ; discours'),
'G5207':('υἱός','fils'),
'G4102':('πίστις','foi ; confiance ; fidélité'),
'G5485':('χάρις','grâce ; faveur ; reconnaissance'),
'G26':('ἀγάπη','amour'),
'G2962':('κύριος','Seigneur ; maître'),
'G5547':('Χριστός','Christ ; Messie'),
'G4151':('πνεῦμα','Esprit ; esprit ; souffle'),
'G3962':('πατήρ','père'),
'G444':('ἄνθρωπος','homme ; être humain'),
'G932':('βασιλεία','royaume ; règne'),
'G266':('ἁμαρτία','péché'),
'G225':('ἀλήθεια','vérité'),
'G2222':('ζωή','vie'),
'G4561':('σάρξ','chair ; corps'),
'G1343':('δικαιοσύνη','justice ; droiture'),
'G746':('ἀρχή','commencement ; principe ; pouvoir'),
'H3068':('יְהֹוָה','Yahvé ; l’Éternel'),
'H5921':('עַל','sur ; au-dessus de ; contre'),
'H834':('אֲשֶׁר','qui ; que (pronom relatif)'),
'H559':('אָמַר','dire'),
'H3605':('כֹּל','tout ; l’ensemble'),
'H413':('אֶל','vers ; à'),
'H3808':('לֹא','ne… pas'),
'H3588':('כִּי','que ; car ; parce que'),
'H1121':('בֵּן','fils'),
'H1961':('הָיָה','être ; devenir'),
'H935':('בּוֹא','venir ; entrer'),
'H6213':('עָשָׂה','faire'),
'H430':('אֱלֹהִים','Dieu ; dieux (Élohim)'),
'H3478':('יִשְׂרָאֵל','Israël'),
'H776':('אֶרֶץ','terre ; pays'),
'H3117':('יוֹם','jour'),
'H4428':('מֶלֶךְ','roi'),
'H6440':('פָּנִים','visage ; devant'),
'H376':('אִישׁ','homme ; mari'),
'H5414':('נָתַן','donner ; mettre'),
'H1004':('בַּיִת','maison'),
'H1931':('הוּא','il ; lui-même'),
'H5971':('עַם','peuple'),
'H853':('אֵת','(marque de l’objet direct)'),
'H3027':('יָד','main'),
'H1697':('דָּבָר','parole ; chose ; affaire'),
'H7200':('רָאָה','voir'),
'H5704':('עַד','jusqu’à ; jusque'),
'H4480':('מִן','de ; hors de'),
'H8085':('שָׁמַע','entendre ; écouter'),
'H2088':('זֶה','ce ; celui-ci'),
'H1':('אָב','père'),
'H1696':('דָּבַר','parler'),
'H859':('אַתָּה','toi ; tu'),
'H3318':('יָצָא','sortir'),
'H3427':('יָשַׁב','s’asseoir ; habiter'),
'H7725':('שׁוּב','revenir ; retourner'),
'H3212':('יָלַךְ','aller ; marcher'),
'H5892':('עִיר','ville'),
'H518':('אִם','si ; ou'),
'H5973':('עִם','avec'),
'H1732':('דָּוִד','David'),
'H3947':('לָקַח','prendre'),
}
MAX=60
def clean(g):
    if g.startswith('[Passage conservé'): return g
    g=g.replace('▁',' ').strip().strip('{}').strip()
    g=re.sub(r'\s+',' ',g)
    if len(g)<=MAX: return g.rstrip(' ;,')
    segs=[s.strip() for s in g.split(';') if s.strip()]
    out=''
    for s in segs:
        t=(out+' ; '+s) if out else s
        if len(t)<=MAX: out=t
        else: break
    if not out:
        s=segs[0]; cut=s[:MAX-1]
        i=max(cut.rfind(', '),cut.rfind(' '))
        out=(cut[:i] if i>20 else cut).rstrip(' ,;(')+'…'
    return out.rstrip(' ;,')
changed=ov=0
for path in sorted(root.glob('lex-fr-*.json')):
    data=json.loads(path.read_text(encoding='utf-8')); src=json.loads((root/path.name.replace('lex-fr-','lex-')).read_text(encoding='utf-8'))
    dirty=False
    for key,entries in data.items():
        for i,e in enumerate(entries):
            old=e['gloss_fr']
            if e.get('gloss_edit')=='manual': continue
            new=clean(old)
            if key in OVERRIDES and i==0:
                lemma,gloss=OVERRIDES[key]
                got=src[key][0].get('lemma','')
                N=lambda x:re.sub(r'[\u0300-\u036f\u0591-\u05c7]','',unicodedata.normalize('NFD',x))
                assert N(lemma) in N(got), (key,lemma,got)
                new=gloss; ov+=1
                e['gloss_edit']='manual'
            if new!=old:
                e.setdefault('gloss_fr_auto',old); e['gloss_fr']=new
                e.setdefault('gloss_edit','auto'); changed+=1; dirty=True
            elif e.get('gloss_edit')=='manual': dirty=True
    if dirty or any(k in OVERRIDES for k in data):
        path.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
print(f'{changed} gloses nettoyées, {ov} gloses révisées à la main.')
