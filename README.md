# Habitat durable : cours et exercices interactifs

Construction reprise du dépôt « Chaîne fonctionnelle » (lui-même repris du dépôt « Résistance des matériaux », RDM) :
une page autonome (un seul fichier HTML, aucune dépendance externe, utilisable hors ligne), publiée par GitHub Pages
depuis `index.html`. L'accueil présente les rubriques **Les cours**, **Les exercices** et **Études de cas** (plus
**Les ressources** dès qu'une page annexe, un formulaire par exemple, y est rangée) :

| Adresse | Contenu |
|---|---|
| `index.html` | accueil, en cartes illustrées à mots-clés ; une rubrique encore vide serait annoncée par une carte « En cours d'édition » |
| `?ex=cours-habitat-durable` | Cours 1 — Habitat durable : concevoir et équiper une maison performante (Niveau 1) : maison bioclimatique au fil des saisons, déperditions, pont thermique, vitrages, ventilation simple et double flux animée, puits canadien, cycle de la pompe à chaleur, programmation ; simulateurs (compacité, paroi R, U, D, surface vitrée, COP, bois, champ photovoltaïque), cinq jeux, quiz de 12 questions |
| `?ex=lecture-plan` | Exercice 1.1 — Lecture de plan : initiation (Niveau 1) : le dossier de plans d'un pavillon (perspective, façades, plans, coupe), 6 parties, 25 questions, 57 cases, 1 h, dont un schéma à compléter avec des étiquettes |
| `?ex=isoler-paroi` | Exercice 1.2 — Isoler une paroi (Niveau 1) : le mur du même pavillon, couche par couche (isolants, coupe à compléter avec la courbe de température, R, U, D, puissance perdue, mur sans isolant, choix d'une épaisseur), 4 parties, 19 questions, 35 cases, 45 min |
| `?ex=qcm-re2020` | QCM 1.3 — La maison RE2020 (Niveau 1) : révision de tout le cours 1, 6 parties, 46 questions dont 13 sur ses figures, 45 min |
| `?ex=iti-ite` | Exercice 2.1 — ITI ou ITE : choisir son isolation (Niveau 2) : les deux procédés au droit d'un plancher (schéma à compléter), déperditions avec ponts thermiques, énergie perdue à Strasbourg, Nantes et Nice (DJU), déphasage d'été (formule simple), inertie et occupation (résidence principale ou de week-end), rénovation ou neuf ; 6 parties, 24 questions, 54 cases, 1 h 20 |
| `?ex=etude-pavillon` | Étude 1 — Le pavillon face à la RE2020 (Niveau 2) : orientation, compacité, vitrages, pompe à chaleur ou granulés, photovoltaïque sur le toit, bilan ; 6 parties, 29 questions, 56 cases, 1 h 30 ; données et hypothèses dans son DT5 |

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
- **Un document** (dossier de présentation DP, dossier technique DT) : une entrée dans `DOCS`, citée par l'exercice
  par sa clé, ou par `(étiquette, clé)` pour l'afficher sous une autre étiquette (un document partagé, ou des DT
  numérotés à partir de DT1 dans chaque exercice).
- **Une image** : `illustration(nom, …)` et les images des QCM n'écrivent une figure qu'une fois dans la page, même
  si plusieurs contenus l'affichent.
- **Une page annexe** : une entrée dans `LIENS`.

```python
EXO_DEFS = [
    {"key": "vitrage", "prefix": "e", "tag": "Exercice 1.4", "level": "Niveau 1",
     "title": "Choisir un vitrage", "sub": "…", "docs": [], "mots": ["Vitrage", "Coefficient Uw", "Fenêtre"],
     "consignes": CONSIGNES_MODES + CONSIGNES_SAISIE + CONSIGNES_BAREME,
     "hero": ("accueil", "texte alternatif", "légende"), "vign": "accueil", "valt": "texte alternatif",
     "parts": [{"title": "Déperdition d'une fenêtre", "minutes": 15, "intro": ["<p>…</p>"], "blocks": [
         Q("Calculer la déperdition d'une fenêtre de 2 m² (Uw = 1,5 W/(m²·K)).", "Valeur et unité.",
           NUM(3, "W/K"), "3 W/K", "<p>D = Uw × S = 1,5 × 2 = 3 W/K.</p>")]}]},
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
node --test tests/correction.test.js                          # gabarit inchangé, configuration, réponses de référence, étiquettes, schémas, écritures acceptées
node --test tests/qcm.test.js                                 # QCM : bonnes réponses acceptées, toutes les autres refusées
NODE_PATH=$(npm root -g) node --test tests/navigateur.test.js # accueil, cours (jeux, quiz, figures, simulateurs), exercice en entraînement et en examen, documents
```

Les tests lisent la page générée : chaque cours et chaque exercice ajoutés sont parcourus d'eux-mêmes (un sujet
entièrement juste donne 20/20, une copie d'examen vide 0/20, sans erreur JavaScript). Tant qu'aucun n'est décrit,
ces parcours sont signalés « SKIP ».

## Organisation

| Chemin | Rôle |
|---|---|
| `src/gabarit-exercice-interactif.html` | gabarit de référence (charte, moteurs de correction et d'application), repris du dépôt « Chaîne fonctionnelle » |
| `src/generer.py` | contenu (exercices 1.1, 1.2 et 2.1, QCM 1.3, étude 1, leurs documents), accueil, aiguillage et assemblage |
| `src/cours_habitat.py` | cours 1 : texte du Word, figures SVG, comportement et style (préfixe `hd-`) |
| `src/plans.py` | schémas à compléter, redessinés en SVG avec leurs cases : la baie (exercice 1.1), le mur en coupe (exercice 1.2), ITI et ITE au droit d'un plancher (exercice 2.1) |
| `src/qcm.py` | QCM : questions à propositions, mises aux normes du gabarit |
| `src/images/accueil.svg` | dessin de l'accueil (maison et leviers d'un habitat durable) |
| `src/images/originaux/` | figures d'origine : cours Word (`ch-*`, photos `ch-ph-*`), dossier de plans du pavillon (`lp-*`) |
| `src/images/` | figures intégrées en data URI (PNG quantifiés, photos, SVG), images des cartes de l'accueil |
| `outils/preparer-images.sh` | quantification des figures, images des cartes de l'accueil (480 × 270) |
| `tests/` | tests Node et Playwright ; `tests/reponses.js` : bonne réponse de chaque case |
| `.github/workflows/static.yml` | publication GitHub Pages (déclenchée sur la branche `main`) |
