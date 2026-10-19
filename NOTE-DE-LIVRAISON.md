# Note de livraison — Habitat durable : cours et exercices interactifs

## Construction reprise du dépôt « Chaîne fonctionnelle »

**Source** : le dépôt « Chaîne fonctionnelle » (générateur, gabarit, accueil, pastilles, aiguillage, éléments communs
des cours, étiquettes à glisser, schémas à compléter, QCM, tests, publication), lui-même repris du dépôt RDM.

**Dépôt non modifié** : « Chaîne fonctionnelle », consulté seulement. Son gabarit est copié tel quel dans
`src/gabarit-exercice-interactif.html` (fichier identique, vérifié octet par octet ; empreinte SHA-256
`d39968af…3db91a`, contrôlée par `tests/correction.test.js`). Le fichier de publication GitHub Pages et le
`.gitignore` sont copiés à l'identique.

**État livré** : la leçon n'a encore ni cours, ni exercice, ni étude de cas. L'accueil (`index.html`) présente ses
trois rubriques, **Les cours**, **Les exercices** et **Études de cas**, chacune annoncée par une carte « En cours
d'édition » (image hachurée, étiquette, titre, mots-clés), remplacée d'elle-même par les cartes des contenus décrits
dans `src/generer.py`. La rubrique **Les ressources** (formulaire, fiches…) n'apparaît que lorsqu'une page annexe y
est rangée. Les numéros suivent la logique RDM : le premier chiffre d'un exercice donne son niveau.

**Accueil** : en-tête « Habitat durable » et présentation de la leçon ; illustration **dessinée pour le site**
(`src/images/accueil.svg`, aucune image n'étant fournie) : une maison aux murs isolés par l'extérieur, des panneaux
photovoltaïques sur le pan au soleil, un arbre qui l'ombrage, une cuve de récupération de l'eau de pluie. **À
vérifier** : la phrase de présentation et les mots-clés des cartes « En cours d'édition » sont provisoires, à
ajuster au contenu réel de la leçon.

**Moteur applicatif** : comme dans le dépôt d'origine, seules les entrées réservées au sujet sont remplacées, chaque
remplacement étant vérifié : `CONSEIL_MIN` (lue dans `window.__CONSEIL_MIN__`), `DECOR` et `DR_NAMES` (vides : aucun
tracé), le texte de la fenêtre « Imprimer les DR », et le libellé « Diagramme validé » des questions à plusieurs
cases, devenu « Réponses validées ». Le correctif d'impression des tracés relevé dans le dépôt RDM est repris.

## Ce qui est repris, retiré, généralisé

**Repris tels quels** (blocs recopiés du générateur d'origine) : outils d'images et d'écriture, correcteur à
mots-clés, rendu des parties et des questions, schémas à compléter et leur bandeau d'étiquettes, documents (rail,
panneau), page d'accueil d'un exercice, choix du mode, cartes de l'accueil, en-tête, sommaire et sections des cours,
jeux de classement, quiz noté, cartes à retourner, styles des simulateurs, aiguillage, styles de contenu, script des
étiquettes, assemblage de la page.

**Retirés** (propres à la chaîne fonctionnelle) : l'exercice 1.1 et ses schémas (`plans.py`, `rav4.py`), le QCM 2.1
et sa page source, les cours 1 à 3 (`portail-anime.html`, `cours_information.py`), le formulaire de la chaîne de
puissance (`formulaire.html`), les images, `outils/captures.js`.

**Généralisés**, pour accueillir les contenus à venir :
- **Images** : `image(nom)` prend un JPEG, un PNG ou un dessin SVG de `src/images` (vignettes, illustrations).
- **Correcteurs** : en plus des mots-clés (`KW`), `NUM` (valeur à 1 % près par défaut, unité : une valeur juste sans
  son unité vaut un demi-point ; les écritures de l'unité sont déduites de son libellé, « m²·K/W » → « m2k/w ») et
  `OUI_NON`.
- **Questions** : `Q` (une case à écrire, que le dépôt d'origine gardait sans l'utiliser) ; `GRP` reçoit directement
  sa liste d'étiquettes, son titre et ses repères sur le schéma ; **sans étiquettes, ses cases sont à écrire**.
  Le gabarit note une question à plusieurs cases sans demi-point : une valeur avec unité s'y refuse (le générateur
  s'arrête et le dit) ; elle se demande dans une question à une case.
- **QCM** : `src/qcm.py` ne lit plus une page fournie ; les questions se décrivent en Python (`qcm.QCM`,
  `qcm.partie`), propositions affichées a, b, c…, images partagées écrites une fois.
- **Cours** : chaque entrée de `COURS` porte sa fonction de rendu, son script, sa fonction d'initialisation et son
  style ; l'aiguillage les assemble.
- **Consignes** : paragraphes à assembler selon l'exercice (modes, réponses à écrire, étiquettes, documents, barème).
- **Contrôles** à la génération : adresses `?ex=` et préfixes uniques, clés des cours en `cours-…`, documents cités
  existants, cases d'un schéma présentes sur la figure.
- **Outil d'images** : `outils/preparer-images.sh` garde la quantification et les fonctions des cartes de l'accueil,
  sans les découpes propres aux anciens contenus.

## Vérifications effectuées

- `node --test tests/correction.test.js tests/qcm.test.js` : gabarit inchangé (empreinte), style et moteur de
  correction de la page identiques à ceux du gabarit ; les tests propres aux contenus (configuration, réponses de
  référence, saisie vide, unités, étiquettes, schémas, QCM) sont signalés « SKIP » tant qu'aucun contenu n'est décrit.
- `tests/navigateur.test.js` (Playwright, Chromium) : accueil (titre, illustration chargée, trois rubriques annoncées
  « En cours d'édition », cartes de même taille à 3 à 5 mots-clés, téléphone sans défilement horizontal, aucune
  mention de diplôme ou d'épreuve), adresse inconnue ; aucune erreur JavaScript.
- **Essai de bout en bout** sur une copie jetable du dépôt (non livrée) : un exercice (questions à écrire, valeur et
  unité, oui ou non, étiquettes sous l'énoncé et sur un schéma, document DP1), un QCM (réponse unique, réponses
  multiples, image), une étude de cas, un cours (jeu, quiz) et une ressource. Les 22 tests passent : chaque contenu
  est parcouru en entraînement (20/20) et en examen (copie vide 0/20, rien ne filtre avant la remise, y compris à
  l'impression), documents, téléphone ; une réponse de référence volontairement fausse fait bien échouer les tests.
