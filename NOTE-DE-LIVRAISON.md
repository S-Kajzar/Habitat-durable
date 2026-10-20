# Note de livraison — Habitat durable : cours et exercices interactifs

## Construction reprise du dépôt « Chaîne fonctionnelle »

**Source** : le dépôt « Chaîne fonctionnelle » (générateur, gabarit, accueil, pastilles, aiguillage, éléments communs
des cours, étiquettes à glisser, schémas à compléter, QCM, tests, publication), lui-même repris du dépôt RDM.

**Dépôt non modifié** : « Chaîne fonctionnelle », consulté seulement. Son gabarit est copié tel quel dans
`src/gabarit-exercice-interactif.html` (fichier identique, vérifié octet par octet ; empreinte SHA-256
`d39968af…3db91a`, contrôlée par `tests/correction.test.js`). Le fichier de publication GitHub Pages et le
`.gitignore` sont copiés à l'identique.

**État livré** : l'accueil (`index.html`) présente le **Cours 1** (Habitat durable, Niveau 1), trois exercices
(**Exercice 1.1** Lecture de plan : initiation, **Exercice 1.2** Isoler une paroi, **QCM 1.3** La maison RE2020, de
Niveau 1 ; **Exercice 2.1** ITI ou ITE : choisir son isolation, de Niveau 2) et l'**Étude 1** (Le pavillon face à la
RE2020, Niveau 2). Une rubrique vide serait annoncée par une
carte « En cours d'édition », remplacée d'elle-même dès qu'un contenu y est décrit dans `src/generer.py`. La rubrique
**Les ressources** (formulaire, fiches…) n'apparaît que lorsqu'une page annexe y est rangée. Les numéros suivent la
logique RDM : le premier chiffre d'un exercice donne son niveau. Les deux exercices et l'étude suivent le même
pavillon, celui de l'exercice 1.1 : on lit ses plans, on isole son mur, puis on le juge avec tout le cours.

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
`plans.py` de ce dépôt dessine les schémas de ses propres exercices), le QCM 2.1 et sa page source, les cours 1 à 3 (`portail-anime.html`, `cours_information.py`), le formulaire de la chaîne de
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
  `qcm.partie`), propositions affichées a, b, c…
- **Images partagées** : une figure citée par plusieurs contenus (une figure du cours reprise dans un QCM, un document
  ou l'accueil d'un exercice) n'est écrite qu'une fois dans la page ; un petit script la pose dans les balises
  `<img data-img>` du contenu ouvert.
- **Documents renommables** : un exercice cite un document par sa clé, ou par (étiquette, clé) pour l'afficher sous
  une autre étiquette. L'exercice 1.2 numérote ainsi ses propres DT1 et DT2 et montre le plan du rez-de-chaussée sous
  l'étiquette DT3 ; l'étude reprend les DP1 et DT1 à DT4 de l'exercice 1.1 et y ajoute son DT5.
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

## Exercice 1.2 — Isoler une paroi (Niveau 1, `?ex=isoler-paroi`)

La partie 2 du cours (conductivité λ, résistance R, coefficient U, déperdition D) appliquée au mur de la partie
habitation du pavillon. 4 parties (10, 10, 15 et 10 min), 19 questions, 35 cases.

- **Les matériaux** : isolant ou non (règle λ &lt; 0,065 W/(m·K), d'où la brique Monomur, bien moins conductrice que
  le parpaing, classée « non isolant ») ; classement de quatre matériaux ; rapport des conductivités du parpaing et du
  polystyrène (≈ 30).
- **Le mur en coupe** : un schéma à compléter redessiné en SVG (`plans.paroi()`, préfixe `ip-`) : pièce chauffée,
  plaque de plâtre, polystyrène, parpaing creux et ses alvéoles, enduit, air extérieur, avec la courbe de température
  calculée couche par couche (19 °C → −5 °C) ; procédé (ITI), pont thermique, couche où la température chute,
  épaisseur totale.
- **Les calculs** : R de chaque couche, R totale (3,39 m²·K/W), U (0,30 W/(m²·K)), D pour 25 m² (7,4 W/K), puissance
  perdue à 24 K d'écart (177 W).
- **Comparer et choisir** : le même mur sans isolant (R = 0,26, D = 96 W/K, 13 fois plus de pertes), l'épaisseur de
  polystyrène pour R = 4 (12,8 cm, d'où 14 cm dans le commerce), et celle de parpaing pour la même résistance (3,80 m).
- **Documents** : DT1 fiches matériaux (conductivités, épaisseurs vendues, formules), DT2 composition du mur (avec la
  figure 3 du cours), DT3 le plan du rez-de-chaussée de l'exercice 1.1.

**Hypothèses, à vérifier** : le dossier ne détaille pas le mur. Sa composition est choisie pour retrouver la cote du
plan : plaque de plâtre 1 cm + polystyrène expansé 10 cm + parpaing creux 20 cm + enduit 1 cm = 32 cm. Le complexe
de doublage (plâtre + polystyrène) mesure donc 11 cm, et non les 12 cm de la question de l'exercice 1.1 (32 − 20), qui
compte l'enduit avec lui : la différence ne gêne aucun calcul. Conductivités : celles du cours et celles du
simulateur de la paroi (plâtre 0,25, polystyrène 0,032, enduit 1) ; résistances superficielles non comptées, comme
dans le cours ; pan de mur de 25 m² ; épaisseurs vendues : 4 à 16 cm.

## QCM 1.3 — La maison RE2020 (Niveau 1, `?ex=qcm-re2020`)

Une révision de tout le cours : 46 questions (dont 5 à plusieurs réponses) en six parties qui suivent les siennes
(architecture bioclimatique, déperditions et isolation, renouvellement de l'air, chaleur d'origine renouvelable,
consommation, production), 45 min, un point par question. 13 questions s'appuient sur les figures du cours (isolation
extérieure, porte soufflante, VMC simple et double flux, puits canadien, système solaire combiné, chauffe-eau
thermodynamique, combustibles, programmateur, domotique, photovoltaïque, site isolé, réseau), écrites une seule fois
dans la page. Chaque question a son explication, tirée du cours ; les distracteurs reprennent les erreurs courantes
(épaisseur en centimètres dans R = e / λ, moyenne au lieu de somme des résistances, COP divisé au lieu de multiplié).

## Étude 1 — Le pavillon face à la RE2020 (Niveau 2, `?ex=etude-pavillon`)

Le pavillon de l'exercice 1.1 jugé avec les notions du cours : 6 parties (15, 15, 20, 15, 20 et 5 min), 29 questions,
56 cases, 1 h 30.

- **Le plan est-il bioclimatique ?** Orientation des baies et de la façade nord ; conformité aux principes (séjour et
  cuisine au sud, façade nord fermée, garage tampon : conformes ; chambres 1, 2 et 4 à l'ouest : contraire, le cours
  plaçant les chambres à l'est) ; une protection solaire à ajouter (brise-soleil, casquette, pergola…).
- **La compacité** : la forme à étage (pavé de 9 × 6 m, l'emprise de l'étage, sur deux niveaux) contre la même maison
  de plain-pied (12 × 9 m), même volume de 270 m³ : C = 0,96 contre 1,19 m²/m³, 63 m² de parois en moins. Mêmes
  conventions que le simulateur du cours (niveau de 2,5 m, toutes les parois déperditives).
- **Les vitrages** : la surface de chaque orientation, le total (16,95 m², soit 15,7 % des 108 m² : un peu sous les
  16 à 18 %), la répartition (50 % à l'ouest, 30 % au sud : l'ouest trop vitré, le sud pas assez), la déperdition des
  baies en double vitrage standard et en VIR, la puissance économisée (≈ 610 W par grand froid).
- **Le chauffage** : pompe à chaleur de COP 3 (1 800 kWh d'électricité, 3 600 kWh puisés dans l'air), chaudière à
  granulés (1 188 kg), chaudière fioul (540 L) ; générateurs admis ou abandonnés par la RE2020.
- **Produire de l'électricité** : le faîtage de la partie à étage est orienté nord-sud (le pignon est sur la façade
  sud), ses versants regardent l'est et l'ouest : il n'y a pas de versant sud. L'étude pose donc les modules sur le
  versant ouest : dénivelé (0,99 m), rampant par Pythagore (3,16 m), surface (28,4 m²), 16 modules de 1 m² avec une
  bande libre de 0,50 m, 1,6 kWc, 144 V par chaîne de 8 modules, 1 600 kWh par an, soit 89 % de l'électricité de la
  pompe à chaleur.
- **Bilan** : atouts et points à améliorer.

Le relevé des menuiseries, retiré de l'exercice 1.1, n'est pas redemandé : le DT5 donne les baies, leurs dimensions,
leur surface et leur orientation, et l'élève n'additionne que ce qui sert au calcul.

**Hypothèses, à vérifier**, toutes écrites dans le DT5 : surface habitable d'environ **108 m²** (estimée d'après les
plans, rez-de-chaussée et étage) ; hauteur de la fenêtre de la douche **75 cm** (non cotée : 40/75) ; besoin annuel de
chauffage **5 400 kWh** (50 kWh par m² habitable) ; production photovoltaïque **1 000 kWh par kWc** et par an sur le
versant ouest ; modules de 1,00 × 1,00 m, 100 Wc et 36 cellules, comme dans le cours. Si ces valeurs changent, les
réponses se recalculent dans `src/generer.py` et `tests/reponses.js`.

## Exercice 2.1 — ITI ou ITE : choisir son isolation (Niveau 2, `?ex=iti-ite`)

Dans quels cas isoler par l'intérieur ou par l'extérieur ? 6 parties (10, 15, 15, 20, 10 et 10 min), 24 questions,
54 cases, 1 h 20. L'exercice prolonge l'exercice 1.2 (même mur en parpaing, mêmes conductivités).

- **Deux procédés** : un schéma à compléter (`plans.iti_ite()`, préfixe `ii-`), deux coupes verticales du même mur
  au droit du plancher de l'étage. En ITI, le plancher traverse l'isolant et une large flèche de chaleur passe par la
  liaison (pont thermique) ; en ITE, l'isolant passe devant le plancher et la flèche, fine, s'arrête sur lui.
- **Calcul thermique** : R du mur (4,01 m²·K/W), la même en ITI et en ITE (une somme ne dépend pas de l'ordre), U
  (0,25), puis D = U × S + ψ × L avec les ponts thermiques : 57,3 W/K en ITI contre 38,1 W/K en ITE ; en ITI, 39 % des
  pertes des murs passent par les liaisons.
- **Trois climats** : Strasbourg (H1), Nantes (H2), Nice (H3) ; énergie annuelle E = D × DJU × 24 / 1 000 (4 104 kWh
  en ITI à Strasbourg) ; économie de l'ITE : 1 368, 1 003 et 638 kWh par an, soit 33 % partout ; priorité de chaque
  région (l'hiver, un climat doux, l'été).
- **Déphasage** (formule simple φ = 1,38 × e × √(ρ × c / (3 600 × λ)), déphasages des couches additionnés) : fibre de
  bois 16 cm 10,7 h (calcul guidé en trois étapes), polystyrène 12 cm 2,3 h, parpaing 20 cm 4,8 h ; murs : 15,5 h en
  fibre de bois, 7,1 h en polystyrène, en ITI comme en ITE (le calcul simple ne voit pas l'ordre des couches) ; heure
  d'arrivée du pic de 15 h (vers 22 h ou vers 6 h 30).
- **Inertie et occupation** : place de la masse (dans ou hors du volume chauffé), inertie forte ou faible, relance
  après une absence ; procédé à conseiller pour une résidence principale, une maison de week-end, une maison à Nice,
  un studio de vacances.
- **Rénovation ou neuf** : atouts de chaque procédé, surface habitable perdue par un doublage de 14 cm (9,52 m²),
  quatre cas (pierre de taille, pavillon des années 1970 à ravaler, copropriété, maison neuve).
- **Documents** : DT1 les trois murs comparés, la maison, ψ et les formules (avec les figures 3 et 4 du cours) ; DT2
  les matériaux (λ, ρ, c) et le déphasage ; DT3 les climats, l'occupation et la rénovation.

**Hypothèses, à vérifier** (toutes écrites dans les DT) :
- **Ponts thermiques** : ψ = 0,7 W/(m·K) en ITI sans rupteur, 0,1 W/(m·K) en ITE ; valeurs indicatives, le cours ne
  chiffre pas les ponts thermiques.
- **Matériaux** : polystyrène ρ = 15 kg/m³, c = 1 450 J/(kg·K) ; fibre de bois λ = 0,040 W/(m·K), ρ = 160 kg/m³,
  c = 2 100 J/(kg·K) ; parpaing creux ρ = 1 050 kg/m³ (un bloc de 20 × 20 × 50 cm d'environ 21 kg), c = 1 000 J/(kg·K),
  avec le λ = 0,95 du cours.
- **Déphasage** : formule simple d'une couche homogène, déphasages des couches additionnés ; le DT2 précise que c'est
  un ordre de grandeur. Recommandation retenue : au moins 8 h, idéalement 10 à 12 h.
- **Climats** : DJU arrondis (base 18 °C) de 3 000 à Strasbourg, 2 200 à Nantes et 1 400 à Nice ; zones H1, H2 et H3 ;
  pas de température extérieure de base, pour ne pas dépendre d'une table départementale.
- **Maison** : 140 m² de murs, 32 m de liaison avec le plancher de l'étage ; maison à rénover : 2 niveaux de 34 m de
  murs extérieurs, doublage de 14 cm.

## Vérifications effectuées

- `node --test tests/correction.test.js` : 11 tests — gabarit inchangé (empreinte), style et moteur de correction de
  la page identiques à ceux du gabarit ; configuration des cinq exercices ; réponse de référence juste pour chaque
  case (202 cases hors QCM) ; saisie vide refusée ; valeur sans unité à un demi-point ; étiquettes (la bonne est
  proposée, toutes les autres de la liste refusées) ; schémas corrigés ; plus de 230 écritures acceptées et
  confusions refusées, réparties entre les exercices 1.1, 1.2, 2.1 et l'étude (unités, e en centimètres dans
  R = e / λ, écart de 14 K au lieu de 24 K, 15 marches, 1,19 t de granulés, déphasage sans la racine…).
- `node --test tests/qcm.test.js` : 3 tests — pour les 46 questions du QCM 1.3, chaque bonne proposition est acceptée,
  chaque autre refusée, une réponse multiple incomplète ou avec un intrus refusée, une explication présente.
- `tests/navigateur.test.js` (Playwright, Chromium) : 19 parcours, tous réussis — accueil (cartes de même taille à 3
  à 5 mots-clés, toutes illustrées, téléphone, aucune mention de diplôme ou d'épreuve), adresse inconnue ; cours 1
  (cinq jeux justes, quiz 12/12 et trois étoiles, images partagées affichées, impression, téléphone) ; ses figures et
  simulateurs ; puis, pour chacun des cinq exercices : entraînement (20,0/20, étiquettes posées sur les schémas comme
  le ferait l'élève), examen (rien ne filtre avant la remise, y compris à l'impression ; copie vide 0,0/20), documents,
  images partagées affichées et téléphone.
- Aucune erreur JavaScript dans aucun parcours. Poids : `index.html` 3,0 Mio, dont 2,4 Mio d'images (les figures
  communes au cours, au QCM et aux documents ne sont écrites qu'une fois).
- L'essai de bout en bout du gabarit vide (copie jetable, non livrée) reste valable pour le seul mécanisme que ce
  dépôt n'utilise pas encore (les ressources).
