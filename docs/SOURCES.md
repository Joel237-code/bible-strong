# Base de données — Étude biblique Strong

État au 6 novembre 2026. Texte biblique et lexiques importés ; application publiée (PWA) ; définitions françaises générées automatiquement pour les 14 035 mots Strong utilisés dans le texte, non révisées par un spécialiste.

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



## Ajout des définitions françaises — 4 novembre 2026

Traduction automatique des champs anglais `gloss` et `definition` de chaque variante, par Argos Translate EN-FR 1.9 avec CTranslate2 (calcul int8, beam 2). Les définitions anglaises ne sont pas modifiées. Les segments grecs/hébreux, les numéros Strong et les références détectées sont conservés. Traduction non révisée : les termes techniques, abréviations, noms propres et nuances théologiques peuvent comporter des erreurs. Ce n’est pas une traduction officielle de STEPBible ou d’Open Scriptures.

Les traductions des entrées grecques sont sous CC BY 4.0, avec attribution à STEPBible ; les traductions des entrées hébraïques sont des adaptations sous CC BY-SA 3.0, avec attribution à James Strong / Open Scriptures, David Troidl et David Instone-Brewer. Les fichiers `data/lex-fr-*.json` sont directement accessibles et réutilisables selon la licence de leur source. Les fichiers `data/metadata-*.json` identifient le moteur et l’empreinte du modèle. Les neuf résumés français pilotes sont conservés séparément et ne doivent pas être confondus avec les définitions complètes traduites.

Moteur : https://github.com/argosopentech/argos-translate ; index officiel des modèles : https://github.com/argosopentech/argospm-index .

## Nettoyage et révision des gloses françaises — 6 novembre 2026

`scripts/polish_glosses.py` (idempotent) :
- supprime les espaces et accolades parasites des gloses françaises et raccourcit à 60 caractères celles qui contenaient une définition entière (6 331 gloses). La glose d'origine est conservée dans `gloss_fr_auto`, et l'entrée est marquée `gloss_edit: "auto"` ;
- remplace par une glose révisée à la main les 77 mots les plus fréquents (par exemple G3056 « parole ; mot ; discours », G2316 « Dieu », H3068 « Yahvé ; l’Éternel »). Ces entrées sont marquées `gloss_edit: "manual"`. Le lemme attendu est vérifié avant chaque remplacement.

`scripts/validate_french.py` ne contrôle plus la présence des jetons grecs et hébreux dans les gloses ainsi modifiées ; les définitions complètes, elles, restent contrôlées.

Limites connues : 531 définitions restent partiellement en anglais (« Passage conservé en anglais après contrôle automatique »), dont de nombreux mots très fréquents (G2532, G3588, G5207…). Les gloses révisées à la main n'ont pas été relues par un tiers.
