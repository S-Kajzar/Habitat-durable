// Réponses justes de référence (une par case), partagées par les tests Node et navigateur.
// Une entrée par exercice (sa clé ?ex=…), puis une réponse par case : <préfixe><partie>_<question> pour une question
// à une case, <préfixe><partie>_<question>_<case> pour une question à plusieurs cases. Une case à étiquettes reçoit
// l'étiquette exacte que l'élève y glisse ; une valeur numérique s'écrit avec son unité (« 0,25 m²·K/W »).
// Les QCM n'y figurent pas : leurs bonnes propositions sont lues dans la configuration du moteur.
module.exports = {
  // Exercice 1.1 — Lecture de plan : initiation (?ex=lecture-plan)
  "lecture-plan": {
    // Partie 1 — le dossier de plans
    a1_1_1: "Perspective (DP1)", a1_1_2: "Façades (DT1)", a1_1_3: "Plan du rez-de-chaussée (DT2)",
    a1_1_4: "Plan de l'étage (DT3)", a1_1_5: "Coupe transversale (DT4)",
    a1_2_1: "Ouest", a1_2_2: "Sud",
    a1_3_1: "Tuiles romanes", a1_3_2: "Deux versants", a1_3_3: "Appentis (un seul versant)",
    a1_3_4: "Porche sous arcade", a1_3_5: "Volets pleins en bois", a1_3_6: "Double vitrage 4/16/4 à l'argon",
    // Partie 2 — les cotes des plans
    a2_1_1: "5", a2_1_2: "50", a2_2_1: "418", a2_2_2: "4,18", a2_3_1: "32", a2_3_2: "320",
    a2_4_1: "20", a2_4_2: "200", a2_5: "12 cm", a2_6_1: "160", a2_6_2: "1,60", a2_7: "305 cm",
    // Partie 3 — les pièces
    a3_1_1: "3,50", a3_1_2: "1,50", a3_1_3: "4,58", a3_1_4: "3,03", a3_1_5: "5,00", a3_1_6: "3,10",
    a3_2: "13,88 m²",
    a3_3_1: "Pièce principale", a3_3_2: "Pièce principale", a3_3_3: "Pièce de service", a3_3_4: "Pièce de service",
    a3_3_5: "Pièce de service", a3_3_6: "Circulation",
    // Partie 4 — la coupe : hauteurs et niveaux
    a4_1_1: "Hauteur sous plafond", a4_1_2: "Retombée de linteau", a4_1_3: "Hauteur de la baie", a4_1_4: "Allège",
    a4_1_5: "Trumeau", a4_1_6: "Cote de niveau",
    a4_2_1: "2,45", a4_2_2: "2450", a4_3: "90 cm", a4_4_1: "0,30", a4_4_2: "300", a4_5: "−0,60", a4_6: "33",
    // Partie 5 — l'escalier
    a5_1: "14", a5_2: "2,60 m", a5_3: "185,7 mm",
    // Partie 6 — le pavillon est-il bioclimatique ?
    a6_1: "Nord", a6_2: "Le garage", a6_3: "Sud",
  },
  // Exercice 1.2 — Isoler une paroi (?ex=isoler-paroi)
  "isoler-paroi": {
    // Partie 1 — les matériaux du mur
    b1_1_1: "Non isolant", b1_1_2: "Isolant", b1_1_3: "Non isolant", b1_1_4: "Isolant", b1_1_5: "Non isolant",
    b1_1_6: "Isolant",
    b1_2_1: "Polystyrène expansé", b1_2_2: "Laine de bois", b1_2_3: "Ossature bois", b1_2_4: "Parpaing creux",
    b1_3: "30",
    // Partie 2 — le mur en coupe
    b2_1_1: "Intérieur : pièce chauffée", b2_1_2: "Plaque de plâtre", b2_1_3: "Polystyrène expansé",
    b2_1_4: "Parpaing creux", b2_1_5: "Enduit", b2_1_6: "Extérieur : air froid",
    b2_2_1: "Isolation par l'intérieur (ITI)", b2_3: "Oui", b2_4: "Le polystyrène expansé", b2_5: "32 cm",
    // Partie 3 — résistance, coefficient U et déperdition
    b3_1_1: "0,04", b3_1_2: "3,13", b3_1_3: "0,21", b3_1_4: "0,01",
    b3_2: "3,39 m²·K/W", b3_3: "0,30 W/(m²·K)", b3_4: "7,4 W/K", b3_5: "177 W",
    // Partie 4 — comparer et choisir
    b4_1: "0,26 m²·K/W", b4_2: "96 W/K", b4_3: "13", b4_4: "12,8 cm", b4_5: "14 cm", b4_6: "3,80 m",
  },
};
