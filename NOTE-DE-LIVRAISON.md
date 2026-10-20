# Note de livraison — Habitat durable : cours et exercices interactifs

## Construction reprise du dépôt « Chaîne fonctionnelle »

**Source** : le dépôt « Chaîne fonctionnelle » (générateur, gabarit, accueil, pastilles, aiguillage, éléments communs
des cours, étiquettes à glisser, schémas à compléter, QCM, tests, publication), lui-même repris du dépôt RDM.

**Dépôt non modifié** : « Chaîne fonctionnelle », consulté seulement. Son gabarit est copié tel quel dans
`src/gabarit-exercice-interactif.html` (fichier identique, vérifié octet par octet ; empreinte SHA-256
`d39968af…3db91a`, contrôlée par `tests/correction.test.js`). Le fichier de publication GitHub Pages et le
`.gitignore` sont copiés à l'identique.

**État livré** : l'accueil (`index.html`) présente le **Cours 1** (Habitat durable, Niveau 1) et l'**Exercice 1.1**
(Lecture de plan : initiation, Niveau 1) ; la rubrique **Études de cas** reste annoncée par une carte « En cours
d'édition » (image hachurée, étiquette, titre, mots-clés), remplacée d'elle-même dès qu'une étude est décrite dans
`src/generer.py`. La rubrique **Les ressources** (formulaire, fiches…) n'apparaît que lorsqu'une page annexe y est
rangée. Les numéros suivent la logique RDM : le premier chiffre d'un exercice donne son niveau.

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

**Retirés** (propres à la chaîne fonctionnelle) : son exercice 1.1 et ses schémas (`plans.py`, `rav4.py` ; le
`plans.py` de ce dépôt dessine le schéma de son propre exercice), le QCM 2.1 et sa page source, les cours 1 à 3 (`portail-anime.html`, `cours_information.py`), le formulaire de la chaîne de
puissance (`formulaire.html`), les images, `outils/captures.js`.

**Généralisés**, pour accueillir les contenus à venir :
- **Images** : `image(nom)` prend un JPEG, un PNG ou un dessin SVG de `src/images` (vignettes, illustrations).
- **Correcteurs** : en plus des mots-clés (`KW`), `NUM` (valeur à 1 % près par défaut, unité : une valeur juste sans
  son unité vaut un demi-point ; les écritures de l'unité sont déduites de son libellé, « m²·K/W » → « m2k/w ») et
  `OUI_NON` ; `NUM` accepte aussi la même grandeur dans d'autres unités (305 cm, 3,05 m ou 3 050 mm).
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
  sans les découpes propres aux anciens contenus ; il réduit les grandes figures à 1100 px de large, passe les photos
  (`*-ph-*`) en JPEG et ignore les originaux des figures redessinées.

## Cours 1 — Habitat durable : concevoir et équiper une maison performante (Niveau 1, `?ex=cours-habitat-durable`)

**Source** : le cours Word « Séquence 4 — Habitat durable : exigences de la RE2020 » (environ 3 h). Le cours est rendu
« vivant » sur le modèle des cours du dépôt « Chaîne fonctionnelle » : tout son texte est conservé, ses six parties
deviennent des sections avec sommaire, complétées d'une synthèse et d'un quiz (`src/cours_habitat.py`, préfixe
`hd-`).

- **En-tête** : problématique, objectifs et prérequis. Ne sont pas repris, comme dans le dépôt d'origine : les champs
  « Nom / Prénom / Groupe », le tableau des compétences (le cours ne vise pas une seule filière), les documents
  ressources (manuel, fiches, activité) et les modalités ; les renvois « (Séquence 1, 2, 3) » des prérequis ; les deux
  notes de rédaction du Word sur des photos non reprises (onduleur, éoliennes).
- **Figures redessinées en SVG et rendues interactives** (les originaux restent dans `src/images/originaux`) :
  figure 1, la maison bioclimatique en coupe, au fil des saisons (le soleil d'hiver entre jusqu'au fond du séjour,
  celui d'été est arrêté par l'avancée du toit ; les trois principes de la figure, touchés, s'éclairent sur la
  maison) ; figure 2, les déperditions, une flèche par poste, de largeur proportionnelle, qui s'explique quand on la
  touche ; la paroi multicouche (R<sub>1</sub> à R<sub>4</sub>) devient un simulateur ; figures 5 et 6, les vitrages
  (température de la face intérieure, U<sub>w</sub>, S<sub>w</sub>, déperdition d'une fenêtre) ; figure 11, le cycle de
  la pompe à chaleur, étape par étape ou en boucle, fluide animé ; figure 14, la chaîne du chauffage central ;
  figure 15, la programmation hebdomadaire, cliquable heure par heure.
- **Ajouts** : pont thermique, isolation intérieure ou extérieure ; ventilation simple et double flux sur un plan de
  maison, air animé de l'entrée d'air aux bouches d'extraction ; puits canadien (température de l'air le long du
  tube) ; simulateurs de compacité (plain-pied ou étage), d'épaisseur pour une résistance visée, de surface vitrée,
  de COP, d'équivalences du bois, de champ photovoltaïque (série, parallèle) ; cinq jeux (orientation des pièces,
  maillons du chauffage central, éclairage, filaire ou sans fil, synthèse) et un quiz de 12 questions.
- **Gardées en images** : photos des matériaux et de l'éclairage, isolation intérieure et extérieure (figures 3, 4),
  porte soufflante, VMC (figures 7, 8), puits canadien (figure 9), système solaire combiné (figure 10), chauffe-eau
  thermodynamique, bois (figures 12, 13), programmateur (figure 16), domotique (figure 17), photovoltaïque et éolien
  (figures 18 à 22).
- **Hypothèses des simulateurs**, écrites à côté de chacun : conductivités du cours (terre crue : 0,8 W/(m·K), au
  milieu de 0,6 à 1) et valeurs usuelles indicatives pour la plaque de plâtre (0,25), les laines de verre (0,035) et
  de bois (0,038), le polystyrène (0,032), l'enduit (1,0) ; hauteur du soleil à midi vers 46° de latitude nord (21°,
  44°, 67°) ; températures de la VMC double flux (insufflation ≈ 15 °C, rejet ≈ 5 °C) ; puits canadien : l'air garde
  environ 30 % de son écart avec le sol ; programmation : environ 7 % de chauffage en moins par degré ; module
  photovoltaïque : I = P / U, et un choix 200 Wc par m² (module récent) à côté des 100 Wc du cours.

Corrections et décisions :
- **Unités** écrites W/(m·K), m²·K/W, W/(m²·K) et m³/(h·m²) (le Word écrit « W/m.K », « m2.K/W »…).
- **Figure 2** : arrondies, les parts des déperditions totalisent 105 % ; la page le signale (« ordres de
  grandeur »). Sa vignette « pont thermique » inverse « Intérieur » et « Extérieur » (la chaleur y va du côté marqué
  Extérieur vers le côté marqué Intérieur, alors que la dalle est à l'intérieur) : elle n'est pas reprise, le pont
  thermique est redessiné, et sa phrase de définition est gardée.
- **Figures 5 et 6** : le « double vitrage standard » de la figure 5 est le « double vitrage » de la figure 6
  (U<sub>w</sub> = 3) ; son S<sub>w</sub> n'est pas chiffré, ni le survitrage, qui n'est pas repris.
- **Photovoltaïque** : « 1 m² produit 100 Wc » est gardé (valeur du cours) ; le simulateur propose aussi 200 Wc, ordre
  de grandeur d'un module récent.
- Les explications des flèches de la figure 2 et des étapes du jeu de synthèse sont ajoutées ; les textes de la
  figure 11 (étapes 1 à 4) sont repris mot pour mot.

## Exercice 1.1 — Lecture de plan : initiation (Niveau 1, `?ex=lecture-plan`)

**Source** : l'activité « Lecture de plan — Activité 1 » : un sujet de 17 questions et un dossier technique de cinq
pages (perspective et remarques architecturales, façades A et B, plan du rez-de-chaussée et vue axonométrique, plan de
l'étage, coupe transversale). Les pages du dossier sont reprises telles quelles (images extraites du PDF, de 548 à
593 px de large : le panneau des documents permet de les agrandir) ; la perspective et les remarques architecturales
sont réécrites en texte (DP1).

- **Retiré** : la question 13, l'inventaire des menuiseries extérieures (désignation, LNB, HNB, orientation).
- **Orienté vers l'architecture** : nature des vues et document où lire chaque information (Q1.1) ; caractères
  architecturaux du pavillon tirés des remarques (DP1) et des façades (Q1.3) ; classement des pièces principales et
  de service, en lien avec la ventilation du cours (Q3.3) ; schéma à compléter du vocabulaire de la baie (figure 1 de
  l'exercice, `src/plans.py` : hauteur sous plafond, retombée de linteau, hauteur de baie, allège, trumeau, cote de
  niveau) ; pente du toit ; une partie « Le pavillon est-il bioclimatique ? », en lien avec la partie 1 du cours.
- **Repris** : orientation des façades, épaisseurs (cloisons, murs, complexe isolant), largeur de la cuisine,
  trumeaux, hauteur sous plafond, allège, retombée de linteau, cote de niveau du garage, escalier (nombre de marches,
  hauteur à franchir, hauteur de marche), en cm puis en mm ou en m comme dans le sujet.
- **Question 12** : son titre (« menuiseries extérieures ») ne correspondait pas à son tableau (dimensions des pièces) ;
  elle devient le relevé des dimensions de trois pièces cotées sans ambiguïté (hall, chambre 4, garage), suivi du
  calcul de la surface de la chambre 4. Les pièces en L (salon séjour) n'étaient déjà pas à remplir.
- **Document DP2** rédigé : les vues d'un dossier, l'orientation, les cotes (centimètres, chaînes de cotes,
  largeur / hauteur des baies, cotes de niveau en mètres), le vocabulaire (définitions, sans le dessin coté) et
  l'escalier.
- Le sujet mentionne « Nom / Prénom / Date » et l'enseignant : remplacés par le champ « Nom et prénom » du gabarit.
- **Barème** : 6 parties pondérées par leur durée (10, 15, 10, 15, 5 et 5 min), une case = un point ; les valeurs avec
  unité acceptent les autres unités (305 cm, 3,05 m ou 3 050 mm) ; une valeur juste sans unité vaut un demi-point.

Corrections et décisions :
- **Corrigé** : le fichier du sujet contient, en texte invisible à l'impression, une partie des réponses (5 cm,
  418 cm, 32 cm, 20 cm, 32 − 20 = 12 cm, 0,90 + 1,25 + 0,30 = 2,45 m, 90 cm, 305 cm) ; elles concordent avec les plans et
  ont servi de corrigé. **À noter** : un élève qui reçoit ce PDF peut les retrouver par copier-coller.
- **Orientation** : la flèche du Nord du plan du rez-de-chaussée pointe vers la droite. Façade A = **ouest**,
  façade B = **sud** ; la vue axonométrique (« Façade Sud », « Façade Est ») et les orientations déjà portées dans le
  tableau de la question 13 (hall à l'est, séjour à l'ouest) le confirment.
- **Escalier** : la volée droite compte 11 nez de marche (le dernier est le bord du palier d'arrivée) et le départ
  3 marches balancées, soit **14 marches** ; hauteur à franchir 2,45 + 0,15 = 2,60 m ; hauteur de marche 2 600 ÷ 14 =
  **185,7 mm**. **À vérifier** : le plan scanné est peu net ; si le décompte de l'activité d'origine est de 15 marches,
  la hauteur de marche vaut 173,3 mm (deux nombres à changer dans `src/generer.py`, deux réponses dans
  `tests/reponses.js`).
- **Complexe isolant** : 32 − 20 = 12 cm, le mur de l'habitation étant celui du garage doublé d'un complexe isolant.

## Vérifications effectuées

- `node --test tests/correction.test.js` : 8 tests — gabarit inchangé (empreinte), style et moteur de correction de la
  page identiques à ceux du gabarit ; configuration de l'exercice 1.1 (6 parties, 57 cases, 1 h) ; réponse de
  référence juste pour chaque case ; saisie vide refusée ; valeur sans unité à un demi-point ; étiquettes (la bonne
  est proposée, toutes les autres de la liste refusées) ; schéma corrigé ; une cinquantaine d'écritures acceptées et
  de confusions refusées (unités, signe de la cote de niveau, 15 marches, 173,3 mm, 13,9 m²…).
- `node --test tests/qcm.test.js` : signalé « SKIP » (aucun QCM).
- `tests/navigateur.test.js` (Playwright, Chromium) : 7 parcours, tous réussis — accueil (cartes de même taille à 3 à
  5 mots-clés, étude annoncée « En cours d'édition », téléphone, aucune mention de diplôme ou d'épreuve), adresse
  inconnue ; cours 1 (cinq jeux justes, quiz 12/12 et trois étoiles, impression, téléphone) ; ses figures et
  simulateurs (saison et soleil, principes, déperditions, compacité, paroi avec et sans isolant, pont thermique,
  vitrages, surface vitrée, VMC, puits canadien, cycle et COP de la pompe à chaleur, bois, programmation, champ
  photovoltaïque) ; exercice 1.1 en entraînement (20,0/20, étiquettes posées sur le schéma comme le ferait l'élève),
  en examen (rien ne filtre avant la remise, y compris à l'impression ; copie vide 0,0/20), documents et téléphone.
- Aucune erreur JavaScript dans aucun parcours. Poids : `index.html` 2,8 Mio, dont 2,4 Mio d'images.
- L'essai de bout en bout du gabarit vide (copie jetable, non livrée : exercice de démonstration, QCM, étude, cours,
  ressource ; 22 tests réussis) reste valable pour les mécanismes que ce dépôt n'utilise pas encore (QCM, ressources).
