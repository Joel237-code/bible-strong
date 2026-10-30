# Base de données — Étude biblique Strong

État au 30 octobre 2026. Import réalisé ; application non construite dans ce lot.

## Résultats contrôlés
- 66 livres, 1 189 chapitres, 31 170 lignes de versets dans l’export source (ce compte dépend de sa versification).
- 417 671 segments balisés, dont 8 419 sans texte français et 5 006 associés à plusieurs Strong.
- 14 035 identifiants Strong distincts utilisés dans le texte.
- 10 847 clés grecques étendues dans TBESG et 8 674 clés hébraïques dans Open Scriptures.
- Aucune référence dupliquée, aucune erreur XML, aucun Strong utilisé sans clé de lexique correspondante.
- Cinq références sans Strong : Neh.7.68, Luke.17.36, Acts.8.37, Acts.15.34, Acts.24.7.
- Vérification structurelle seulement : ne prouve ni l’exactitude de chaque association, ni l’exhaustivité linguistique.

## Fichiers
`processed/bible.json` : texte et segments, identifiants normalisés sans zéros initiaux.
`processed/concordance.json` : liste de versets par numéro Strong (pas le nombre de répétitions du mot).
`processed/lexicon-greek.json` : entrées anglaises TBESG ; les distinctions étendues restent groupées sous leur clé, sans fusion arbitraire.
`processed/lexicon-hebrew.json` : entrées anglaises Strong Open Scriptures.
`processed/lexicon-fr-sample.json` : 9 résumés français pilotes, non exhaustifs, assistés par IA, sans révision indépendante.
`processed/audit.json` : mesures et empreintes des sources.

## Vérification sur Galates 6:6
Le segment « part » est lié à G2841. « fasse » n’est pas balisé séparément par le fournisseur ; aucune modification de cet alignement n’a été faite.
G2841 apparaît dans 8 versets : Romains 12:13 ; 15:27 ; Galates 6:6 ; Philippiens 4:15 ; 1 Timothée 5:22 ; Hébreux 2:14 ; 1 Pierre 4:13 ; 2 Jean 1:11.

## Sources, licences et corrections du choix initial
1. Segond 1910 : domaine public. Export avec versification d’origine provenant de https://concordance.bible/Sg1910/download/ .
Attribution obligatoire : Numéros Strong affectés en 2026 par “Concordances et Traductions de la Bible” (concordance.bible).
Le fournisseur signale une fiabilisation en cours, des correspondances multiples et des variantes de texte. Les mots non traduits sont conservés comme segments vides.
2. Grec : STEP Bible, https://www.STEPBible.org ; dépôt https://github.com/STEPBible/STEPBible-Data . TBESG sous CC BY 4.0 : https://creativecommons.org/licenses/by/4.0/ . Conserver le crédit et signaler les adaptations. L’en-tête original est conservé dans raw/TBESG.txt. Le README courant autorise les miroirs tenus à jour et liés à l’original ; l’en-tête recommande de renvoyer vers la source centrale.
3. Hébreu : James Strong, édition numérique Open Scriptures (2010), corrections/translittérations David Troidl, source numérique David Instone-Brewer. https://github.com/openscriptures/strongs . Fichier marqué CC-BY-SA ; la page générale https://openscriptures.org/about/ précise CC BY-SA 3.0 : https://creativecommons.org/licenses/by-sa/3.0/ . Les adaptations de ce lexique restent sous cette licence. La conversion JSON préserve tous les champs du fichier original.
4. IMPORTANT : les définitions de TBESH ne sont PAS incluses. L’en-tête propre à TBESH demande une autorisation d’Online Bible malgré la présentation générale CC BY du dépôt. La proposition initiale d’utiliser ces définitions a donc été corrigée.

## Modifications effectuées
Conversion TSV/XML en JSON ; normalisation H0430 → H430 ; index de références ; conversion du dictionnaire JS en JSON ; 9 résumés français pilotes. Le texte français biblique n’a pas été retraduit. Les descriptions anglaises restent identifiées comme telles. Les identifiants de variantes grecques sont conservés.

## Reproduction
Python 3, bibliothèque standard : `python import_sources.py` puis `python build_data.py` puis `python prepare_package.py`.
Les sources en ligne peuvent changer. Les empreintes permettent de distinguer les versions ; cet import ne fige pas un commit Git amont.

## Travail restant
Traduction et révision du lexique complet ; contrôle linguistique par échantillons puis corrections ; présentation des variantes et mots non balisés ; construction de l’interface et de la PWA. Ne pas annoncer que le lexique français complet est terminé.
