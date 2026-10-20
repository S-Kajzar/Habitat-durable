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
  // Étude de cas 1 — Le pavillon face à la RE2020 (?ex=etude-pavillon)
  "etude-pavillon": {
    // Partie 1 — le plan est-il bioclimatique ?
    d1_1_1: "Sud", d1_1_2: "Est", d1_1_3: "Ouest", d1_1_4: "Ouest", d1_1_5: "Nord",
    d1_2_1: "Conforme aux principes", d1_2_2: "Conforme aux principes", d1_2_3: "Conforme aux principes",
    d1_2_4: "Contraire aux principes", d1_2_5: "Conforme aux principes",
    d1_3: "Un brise-soleil",
    // Partie 2 — la compacité
    d2_1_1: "270", d2_1_2: "258", d2_1_3: "0,96", d2_2_1: "270", d2_2_2: "321", d2_2_3: "1,19",
    d2_3: "La forme à étage", d2_4: "63 m²",
    // Partie 3 — les vitrages
    d3_1_1: "5,16", d3_1_2: "8,46", d3_1_3: "3,33", d3_1_4: "0", d3_2: "16,95 m²", d3_3: "15,7", d3_4: "Non",
    d3_5_1: "30", d3_5_2: "50", d3_5_3: "20", d3_5_4: "0", d3_6_1: "Ouest", d3_6_2: "Sud",
    d3_7_1: "50,9", d3_7_2: "25,4", d3_8: "610 W",
    // Partie 4 — le chauffage
    d4_1: "1 800 kWh", d4_2: "3 600 kWh", d4_3: "1 188 kg", d4_4: "540 L",
    d4_5_1: "Admise par la RE2020", d4_5_2: "Admise par la RE2020", d4_5_3: "Abandonnée par la RE2020",
    d4_5_4: "Abandonnée par la RE2020",
    // Partie 5 — produire de l'électricité
    d5_1: "0,99 m", d5_2: "3,16 m", d5_3: "28,4 m²", d5_4: "16", d5_5: "1 600 Wc", d5_6: "144 V", d5_7: "1 600 kWh",
    d5_8: "89",
    // Partie 6 — bilan
    d6_1_1: "Atout", d6_1_2: "Point à améliorer", d6_1_3: "Atout", d6_1_4: "Atout", d6_1_5: "Point à améliorer",
  },
};
