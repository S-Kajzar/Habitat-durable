# Habitat durable : cours et exercices interactifs

Construction reprise du dépôt « Chaîne fonctionnelle » (lui-même repris du dépôt « Résistance des matériaux », RDM) :
une page autonome (un seul fichier HTML, aucune dépendance externe, utilisable hors ligne), publiée par GitHub Pages
depuis `index.html`. L'accueil présente les rubriques **Les cours**, **Les exercices** et **Études de cas** (plus
**Les ressources** dès qu'une page annexe, un formulaire par exemple, y est rangée) :

| Adresse | Contenu |
|---|---|
| `index.html` | accueil, en cartes illustrées à mots-clés ; chaque rubrique encore vide est annoncée par une carte « En cours d'édition » |
| `?ex=cours-…` | un cours (à venir) |
| `?ex=…` | un exercice ou une étude de cas (à venir), en mode entraînement ou en mode examen, avec sa note pondérée par la durée de ses parties |

Décisions et différences avec le dépôt d'origine : [`NOTE-DE-LIVRAISON.md`](NOTE-DE-LIVRAISON.md). Les exemples
complets (exercice à étiquettes posées sur des schémas, QCM, cours interactifs animés) sont dans le dépôt
« Chaîne fonctionnelle ».

## Ajouter du contenu

Tout se décrit dans `src/generer.py` ; la carte apparaît d'elle-même sur l'accueil et remplace l'annonce
« En cours d'édition » de sa rubrique.

- **Un exercice** : ses parties (titre, durée conseillée, introduction, blocs), puis une entrée dans `EXO_DEFS`
  (modèle en commentaire). Blocs : `Q` (une case à écrire : mots-clés `KW`, valeur et unité `NUM`, `OUI_NON`), `GRP`
  (plusieurs cases validées ensemble, à écrire ou à remplir d'étiquettes ; `zones` les pose sur le schéma de la
  partie), `QBAR` (documents à consulter), `HTML`. Les réponses justes de chaque case vont dans `tests/reponses.js`.
- **Un QCM** : `qcm.partie(…)` et `qcm.QCM(…)` (voir `src/qcm.py`), `"qcm": True` dans `EXO_DEFS`.
- **Une étude de cas** : comme un exercice, avec `"etude": True`.
- **Un cours** : une entrée dans `COURS`, dont la clé commence par `cours-`, avec sa fonction de rendu ; éléments
  communs fournis : en-tête, sommaire, sections, cartes à retourner, jeux de classement, quiz noté, simulateurs.
- **Un document** (dossier de présentation DP, dossier technique DT) : une entrée dans `DOCS`, citée par l'exercice.
- **Une page annexe** : une entrée dans `LIENS`.

```python
EXO_DEFS = [
    {"key": "isolation-paroi", "prefix": "a", "tag": "Exercice 1.1", "level": "Niveau 1",
     "title": "Isoler une paroi", "sub": "…", "docs": [], "mots": ["Isolation", "Résistance thermique", "Paroi"],
     "consignes": CONSIGNES_MODES + CONSIGNES_SAISIE + CONSIGNES_BAREME,
     "hero": ("accueil", "texte alternatif", "légende"), "vign": "accueil", "valt": "texte alternatif",
     "parts": [{"title": "Résistance thermique", "minutes": 15, "intro": ["<p>…</p>"], "blocks": [
         Q("Calculer la résistance thermique R d'un isolant de 20 cm (λ = 0,04 W/(m·K)).", "Valeur et unité.",
           NUM(5, "m²·K/W"), "5 m²·K/W", "<p>R = e / λ = 0,20 / 0,04 = 5 m²·K/W.</p>")]}]},
]
```

Numérotation (logique RDM) : le premier chiffre d'un exercice donne son niveau (1.1, 1.2… au niveau 1 ; 2.1… au
niveau 2) ; pastilles verte (Niveau 1) et bleue (Niveau 2).

## Régénérer la page

La page est produite par un script, à partir du gabarit (`src/gabarit-exercice-interactif.html`, copie conforme de
celui des dépôts RDM et « Chaîne fonctionnelle », recopié sans modification de son style ni de ses moteurs) et du
contenu décrit dans `src/generer.py`.

```sh
bash outils/preparer-images.sh   # seulement si les images de src/images/originaux changent (ImageMagick 6)
python3 src/generer.py           # écrit index.html
```

## Tester

```sh
node --test tests/correction.test.js                          # gabarit inchangé, configuration, réponses de référence, étiquettes, schémas
node --test tests/qcm.test.js                                 # QCM : bonnes réponses acceptées, toutes les autres refusées
NODE_PATH=$(npm root -g) node --test tests/navigateur.test.js # accueil, chaque cours, chaque exercice en entraînement et en examen, documents
```

Les tests lisent la page générée : chaque cours et chaque exercice ajoutés sont parcourus d'eux-mêmes (un sujet
entièrement juste donne 20/20, une copie d'examen vide 0/20, sans erreur JavaScript). Tant qu'aucun n'est décrit,
ces parcours sont signalés « SKIP ».

## Organisation

| Chemin | Rôle |
|---|---|
| `src/gabarit-exercice-interactif.html` | gabarit de référence (charte, moteurs de correction et d'application), repris du dépôt « Chaîne fonctionnelle » |
| `src/generer.py` | contenu (exercices, documents, cours), accueil, aiguillage et assemblage |
| `src/qcm.py` | QCM : questions à propositions, mises aux normes du gabarit |
| `src/images/accueil.svg` | dessin de l'accueil (maison et leviers d'un habitat durable) |
| `src/images/originaux/` | figures d'origine des contenus |
| `src/images/` | figures intégrées en data URI (PNG quantifiés, photos, SVG), images des cartes de l'accueil |
| `outils/preparer-images.sh` | quantification des figures, images des cartes de l'accueil (480 × 270) |
| `tests/` | tests Node et Playwright ; `tests/reponses.js` : bonne réponse de chaque case |
| `.github/workflows/static.yml` | publication GitHub Pages (déclenchée sur la branche `main`) |
