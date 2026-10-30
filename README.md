# Logos — Bible Strong

Annexe d’étude biblique : Louis Segond 1910, mots Strong cliquables, lexiques grec/hébreu anglais, recherche et concordance. PWA avec téléchargement hors connexion (~50 Mo). Sans compte utilisateur, notes ou favoris.

## Publication

Dans **Settings → Pages → Build and deployment → Source**, sélectionner **GitHub Actions**. Le workflow **Publier Bible Strong** publie automatiquement les modifications de `main`. Si nécessaire : **Actions → Publier Bible Strong → Run workflow**.

Adresse attendue après publication réussie : https://joel237-code.github.io/bible-strong/

## Fichiers et indépendance

Le dossier `docs/` contient toute l’application et ses données. Une importation initiale copie la version existante depuis son hébergement précédent, avec contrôle SHA-256 de chaque fichier. Ces fichiers sont ensuite enregistrés dans ce dépôt ; les publications suivantes et l’application ne dépendent plus de cet hébergement. Le script ne remplace jamais un fichier déjà importé, afin de préserver les modifications.

Les chemins de l’application sont relatifs et compatibles avec `/bible-strong/`. Installer la PWA depuis la nouvelle adresse et retélécharger les données sur chaque appareil : le stockage de l’ancien domaine ne se transfère pas.

## Développement

Modifier les fichiers sous `docs/`. Pour tester localement : `python3 -m http.server 8000 --directory docs`. Lors de modifications de l’application, mettre à jour la version du cache dans `sw.js` et prévoir la mise à jour des données hors ligne.

## Sources et limites

Les attributions et licences des données sont détaillées dans `docs/SOURCES.md`. Le texte Segond 1910 relève du domaine public ; les correspondances Strong exigent l’attribution à Concordance.bible. Le lexique grec STEPBible est sous CC BY 4.0 ; le lexique hébreu Open Scriptures et ses adaptations sous CC BY-SA 3.0. Ne pas appliquer une licence globale incompatible aux données.

Le français du lexique est incomplet : neuf résumés pilotes assistés par IA, non révisés, sans traduction intégrale. Les contrôles de données sont structurels et ne constituent pas une validation linguistique exhaustive.
