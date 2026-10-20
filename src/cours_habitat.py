"""Cours 1 — Habitat durable : concevoir et équiper une maison performante (Niveau 1), d'après le cours Word
« Séquence 4 — Habitat durable : exigences de la RE2020 ».

Tout le texte du Word est repris, partie par partie (architecture bioclimatique, déperditions thermiques,
renouvellement de l'air, énergies renouvelables, consommation, production d'énergie). Les photos et les
illustrations détaillées restent des images (src/images/ch-*) ; les figures de principe sont redessinées en SVG et
rendues interactives : maison bioclimatique au fil des saisons (figure 1), déperditions cliquables (figure 2), pont
thermique selon l'isolation, vitrages (figures 5 et 6), ventilation simple et double flux animée, puits canadien,
cycle de la pompe à chaleur (figure 11), programmation hebdomadaire (figure 15). S'y ajoutent des simulateurs :
compacité, épaisseur d'un matériau pour une résistance visée, paroi multicouche (R, U, D), surface vitrée,
coefficient de performance, équivalences du bois, champ photovoltaïque ; cinq jeux et un quiz.

render(h) reçoit les fonctions communes du générateur (en-tête, sections, jeux, quiz, images) : pas d'import
circulaire. Classes et identifiants propres au cours : préfixe « hd- ».
"""
import html
import math

PROBLEMATIQUE = ("Quelles solutions techniques permettent de réduire les besoins énergétiques d'une maison neuve, de "
                 "renouveler son air intérieur et de couvrir ses besoins à partir d'énergies renouvelables, "
                 "conformément à la RE2020 ?")
OBJECTIFS = [
    "Identifier les principes d'une architecture bioclimatique.",
    "Caractériser une paroi : conductivité, résistance, coefficient de transfert, déperdition ; calculer la "
    "compacité d'un bâtiment.",
    "Décrire les solutions de renouvellement d'air (VMC simple et double flux, puits canadien).",
    "Identifier les équipements de production de chaleur et d'électricité d'origine renouvelable.",
    "Repérer les moyens de limiter la consommation énergétique (programmation, éclairage, domotique).",
]
PREREQUIS = ["Énergie et puissance : unités, conversions.", "Chaîne de puissance.", "Chaîne d'information."]

# ------------------------------------------------------------ jeux et quiz
ORIENTATIONS = [("sud", "Sud"), ("nord", "Nord"), ("est", "Est")]
JEU_PIECES = [("Salon séjour", "sud"), ("Garage", "nord"), ("Chambre", "est"), ("Cellier", "nord"),
              ("Salle à manger", "sud"), ("Couloir", "nord")]
MAILLONS = [("enr", "Énergie"), ("gen", "Générateur"), ("tra", "Transport"), ("emi", "Émetteur")]
JEU_CHAUFFAGE = [("Bois (granulés)", "enr"), ("Chaudière", "gen"), ("Tuyaux souples en PER", "tra"),
                 ("Radiateur", "emi"), ("Soleil", "enr"), ("Ballon tampon", "gen"), ("Chauffage au sol", "emi"),
                 ("Tuyaux rigides en cuivre", "tra"), ("Air (pompe à chaleur)", "enr")]
ECLAIRAGES = [("pl", "Puits de lumière"), ("dp", "Détection de présence"), ("dc", "Détection crépusculaire"),
              ("led", "LED"), ("et", "Étiquette énergétique")]
JEU_ECLAIRAGE = [("Une salle de bains sans fenêtre, sombre en plein jour", "pl"),
                 ("Un couloir où l'on ne fait que passer", "dp"),
                 ("L'éclairage de l'allée du jardin, à la tombée de la nuit", "dc"),
                 ("Remplacer une vieille ampoule qui chauffe beaucoup", "led"),
                 ("Choisir un réfrigérateur peu énergivore", "et")]
LIAISONS = [("fil", "Filaire"), ("sf", "Sans fil")]
JEU_LIAISONS = [("Bus KNX", "fil"), ("Zigbee", "sf"), ("Ethernet domestique", "fil"), ("Wi-Fi", "sf"),
                ("Z-Wave", "sf"), ("Legrand MyHome", "fil"), ("Infrarouge", "sf")]
FAMILLES = [("bio", "Bioclimatique"), ("dep", "Déperditions"), ("air", "Air"), ("enr", "Chaleur renouvelable"),
            ("con", "Consommation"), ("pro", "Production")]
JEU_SYNTHESE = [("Séjour largement vitré au sud", "bio"), ("Avancée de toit au-dessus des baies sud", "bio"),
                ("Isolation par l'extérieur", "dep"), ("Triple vitrage", "dep"), ("Test d'étanchéité à l'air", "dep"),
                ("VMC double flux", "air"), ("Puits canadien", "air"), ("Pompe à chaleur", "enr"),
                ("Chaudière à granulés", "enr"), ("Programmateur de chauffage", "con"),
                ("Détecteur de présence", "con"), ("Panneaux photovoltaïques", "pro"), ("Petite éolienne", "pro")]

QUIZ = [
    ("Depuis le 1<sup>er</sup> janvier 2022, une maison neuve doit respecter :",
     ["la RT2012", "la RE2020", "aucune réglementation thermique"], 1,
     "La réglementation environnementale RE2020 s'applique aux maisons neuves depuis le 1<sup>er</sup> janvier 2022."),
    ("Dans une maison bioclimatique, les pièces de vie sont exposées :", ["au nord", "au sud", "à l'ouest"], 1,
     "Au sud, elles profitent de la lumière et des apports solaires ; le nord accueille les espaces tampons."),
    ("La compacité d'un bâtiment est la meilleure quand le facteur C = S<sub>p</sub> / V est :",
     ["le plus faible", "le plus élevé", "égal à 1"], 0,
     "Moins de parois déperditives pour un même volume chauffé : C faible, compacité meilleure."),
    ("Lequel de ces matériaux est le plus isolant ?",
     ["Parpaing (λ = 0,95 W/(m·K))", "Ossature bois (λ = 0,12 W/(m·K))", "Terre crue (λ = 0,6 à 1 W/(m·K))"], 1,
     "Plus λ est faible, plus le matériau est isolant."),
    ("Un isolant de 10 cm a une conductivité λ = 0,04 W/(m·K). Sa résistance thermique R vaut :",
     ["0,4 m²·K/W", "2,5 m²·K/W", "4 m²·K/W"], 1, "R = e / λ = 0,10 / 0,04 = 2,5 m²·K/W (e en mètres)."),
    ("Une paroi a une résistance R = 4 m²·K/W. Son coefficient U vaut :",
     ["4 W/(m²·K)", "0,25 W/(m²·K)", "0,4 W/(m²·K)"], 1, "U = 1 / R = 1 / 4 = 0,25 W/(m²·K)."),
    ("L'isolation par l'extérieur permet surtout :",
     ["de supprimer les ponts thermiques", "de réduire l'épaisseur des murs", "de se passer de ventilation"], 0,
     "L'isolant enveloppe le mur et les tranches des planchers : l'isolation n'est plus interrompue."),
    ("La VMC double flux :",
     ["extrait l'air vicié sans jamais faire entrer d'air neuf",
      "réchauffe l'air neuf dans un échangeur avant de l'insuffler",
      "souffle l'air vicié dans les chambres"], 1,
     "L'air extrait des pièces de service cède sa chaleur à l'air neuf dans l'échangeur."),
    ("Une pompe à chaleur de COP 3 consomme 1 kWh d'électricité. Elle fournit :",
     ["0,33 kWh de chaleur", "1 kWh de chaleur", "3 kWh de chaleur"], 2,
     "COP = W<sub>thermique</sub> / W<sub>électrique</sub>, donc W<sub>thermique</sub> = 3 × 1 = 3 kWh."),
    ("Quelle température de confort conseille-t-on en présence des occupants ?", ["16 °C", "19 °C", "22 °C"], 1,
     "19 °C en présence des occupants, 16 °C en leur absence (température réduite)."),
    ("Un module photovoltaïque de 36 cellules en série fournit une tension d'environ :", ["0,5 V", "18 V", "36 V"], 1,
     "36 × 0,5 V = 18 V : la mise en série additionne les tensions."),
    ("Une maison à énergie positive (Bepos) :",
     ["consomme plus d'énergie qu'elle n'en produit", "produit plus d'énergie qu'elle n'en consomme",
      "ne consomme aucune énergie"], 1, "Elle produit plus d'énergie qu'elle n'en consomme, grâce au soleil et au vent."),
]


# ------------------------------------------------------------ outils
def e(s):
    return html.escape(s, quote=True)


def img(h, name, alt, caption, maxw, cls="fig hd-fig"):
    """Image de src/images (JPEG, PNG ou SVG), avec sa légende ; image partagée : un exercice (QCM…) peut l'afficher
    aussi sans que la page en contienne deux copies."""
    w, hh = h.image_partagee(name)
    return (f'<figure class="{cls}" style="max-width:{maxw}px"><img data-img="{name}" alt="{e(alt)}" width="{w}" '
            f'height="{hh}">' + (f"<figcaption>{caption}</figcaption>" if caption else "") + "</figure>")


def fleche(x1, y1, x2, y2, w, tete=None):
    """Points d'une flèche pleine de (x1, y1) à (x2, y2), de largeur w."""
    lg = math.hypot(x2 - x1, y2 - y1)
    ux, uy = (x2 - x1) / lg, (y2 - y1) / lg
    nx, ny = -uy, ux
    t = tete or w * 1.25 + 6
    bx, by = x2 - ux * t, y2 - uy * t
    pts = [(x1 + nx * w / 2, y1 + ny * w / 2), (bx + nx * w / 2, by + ny * w / 2), (bx + nx * w, by + ny * w),
           (x2, y2), (bx - nx * w, by - ny * w), (bx - nx * w / 2, by - ny * w / 2), (x1 - nx * w / 2, y1 - ny * w / 2)]
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)


HACHURES = ('<pattern id="{id}" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
            '<rect width="7" height="7" fill="#FFF3C4"/><line x1="0" y1="0" x2="0" y2="7" stroke="#D9A21B" '
            'stroke-width="2.4"/></pattern>')
MARQUEUR = ('<marker id="{id}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" '
            'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{c}"/></marker>')


# ------------------------------------------------------------ figure 1 : maison bioclimatique au fil des saisons
def svg_bio():
    vent = "".join(f'<path d="{d}" class="hd-bio-vent" marker-end="url(#hd-mk-vent)"/>' for d in (
        "M6,196 C70,186 150,168 232,160 S350,112 420,100", "M6,226 C90,214 170,196 250,186",
        "M6,170 C80,160 170,140 260,128"))
    sapins = "".join(f'<polygon points="{x},{y} {x - 17},{y + 76} {x + 17},{y + 76}" fill="#2F6B3A"/>'
                     f'<rect x="{x - 3}" y="{y + 76}" width="6" height="10" fill="#6B4A2B"/>'
                     for x, y in ((70, 178), (128, 190), (182, 206)))
    return f"""<svg class="hd-svg" id="hd-bio-svg" viewBox="0 0 900 360" role="img" aria-labelledby="hd-bio-tt">
<title id="hd-bio-tt">Maison bioclimatique en coupe : au nord des arbres et un talus la protègent du vent ; au sud, un
grand vitrage abrité par l'avancée du toit laisse entrer le soleil d'hiver.</title>
<defs>{HACHURES.format(id="hd-hach-bio")}{MARQUEUR.format(id="hd-mk-vent", c="#1F5FA8")}</defs>
<rect width="900" height="320" fill="#EAF2FB"/><rect y="320" width="900" height="40" fill="#E6DCC6"/>
<line x1="0" y1="320" x2="900" y2="320" stroke="#46525C" stroke-width="2"/>
<path d="M0,320 L0,262 Q140,248 300,320 Z" fill="#CFE3C4"/>{sapins}
<g id="hd-bio-g2" class="hd-bio-g">{vent}<text x="8" y="122" class="hd-t hd-t-b" fill="#1F5FA8">Vents dominants</text>
  <rect x="344" y="204" width="88" height="102" fill="#ECEEEA"/>
  <rect x="330" y="232" width="14" height="22" fill="#BFD9F2" stroke="#1F5FA8"/>
  <text x="388" y="236" class="hd-t hd-t-s" text-anchor="middle">Cellier,</text>
  <text x="388" y="252" class="hd-t hd-t-s" text-anchor="middle">garage :</text>
  <text x="388" y="268" class="hd-t hd-t-s" text-anchor="middle">espaces</text>
  <text x="388" y="284" class="hd-t hd-t-s" text-anchor="middle">tampons</text></g>
<rect x="438" y="204" width="168" height="102" fill="#FFFFFF"/>
<rect x="432" y="204" width="6" height="102" fill="#9AA3AB"/>
<text x="522" y="236" class="hd-t hd-t-b" text-anchor="middle">Séjour</text>
<text x="522" y="254" class="hd-t hd-t-s" text-anchor="middle">pièce de vie</text>
<polygon id="hd-bio-beam" points="" fill="rgba(242,183,5,.42)"/>
<g id="hd-bio-g1" class="hd-bio-g">
  <rect x="330" y="204" width="14" height="28" fill="url(#hd-hach-bio)"/><rect x="330" y="254" width="14" height="52" fill="url(#hd-hach-bio)"/>
  <rect x="330" y="190" width="290" height="14" fill="url(#hd-hach-bio)"/>
  <rect x="330" y="306" width="290" height="14" fill="url(#hd-hach-bio)"/>
  <rect x="606" y="204" width="14" height="10" fill="url(#hd-hach-bio)"/><rect x="606" y="300" width="14" height="6" fill="url(#hd-hach-bio)"/>
  <text x="520" y="182" class="hd-t hd-t-s" text-anchor="middle">isolation continue</text></g>
<g id="hd-bio-g3" class="hd-bio-g"><rect x="606" y="214" width="14" height="86" fill="#BFD9F2" stroke="#1F5FA8" stroke-width="1.5"/>
  <line x1="620" y1="199" x2="690" y2="199" class="hd-bio-bs"/></g>
<polygon points="316,196 452,114 694,190 690,199 452,125 330,203" fill="#8C4A2F"/>
<g id="hd-bio-rays"></g>
<g id="hd-bio-sun"><circle r="20" fill="#F2B705"/><g stroke="#F2B705" stroke-width="3" stroke-linecap="round">
  <line x1="0" y1="-26" x2="0" y2="-34"/><line x1="0" y1="26" x2="0" y2="34"/><line x1="-26" y1="0" x2="-34" y2="0"/>
  <line x1="26" y1="0" x2="34" y2="0"/><line x1="18" y1="18" x2="24" y2="24"/><line x1="-18" y1="-18" x2="-24" y2="-24"/>
  <line x1="18" y1="-18" x2="24" y2="-24"/><line x1="-18" y1="18" x2="-24" y2="24"/></g></g>
<text x="890" y="22" class="hd-t hd-t-b" text-anchor="end" id="hd-bio-ang"></text>
<text x="14" y="345" class="hd-t hd-t-b">← Nord</text><text x="886" y="345" class="hd-t hd-t-b" text-anchor="end">Sud →</text>
</svg>"""


NOTES_BIO = [
    (1, "<b>Isolation maximale</b> des parois extérieures (toiture, murs, dalles, fenêtres…)."),
    (2, "La <b>façade nord</b> est protégée des vents dominants. Elle possède <b>peu d'ouvertures</b> et donne sur des "
        "espaces tampons."),
    (3, "<b>Orientation au sud</b> des pièces de vie équipées de parois vitrées importantes afin de récupérer au maximum "
        "l'éclairement naturel et les apports solaires. Des <b>brise-soleil</b> permettent d'éviter les surchauffes en "
        "été."),
]


# ------------------------------------------------------------ figure 2 : répartition des déperditions
DEPERDITIONS = [  # clé, libellé, part, flèche (x1, y1, x2, y2), position du texte, ancrage, explication
    ("toit", "Toiture", 30, (262, 128, 168, 64), (160, 52), "end",
     "L'air chaud monte et s'accumule sous le toit : c'est la première paroi à isoler (combles, rampants)."),
    ("air", "Air renouvelé", 20, (390, 92, 390, 22), (404, 30), "start",
     "L'air vicié extrait par la ventilation, et l'air qui fuit par les défauts d'étanchéité, emportent leur chaleur "
     "(voir les parties 2.5 et 3)."),
    ("murs", "Murs et ponts thermiques", 30, (436, 236, 530, 236), (538, 226), "start",
     "Les murs ont une grande surface ; à leurs jonctions avec les planchers et les refends, l'isolation "
     "s'interrompt : ce sont les <b>ponts thermiques</b>. Un pont thermique correspond à une zone de déperditions "
     "thermiques par conduction à travers un défaut d'isolation."),
    ("fen", "Fenêtres", 15, (236, 230, 140, 230), (134, 226), "end",
     "Même performant, un vitrage isole moins qu'un mur : il faut bien le choisir (2.4) et bien l'orienter."),
    ("plancher", "Plancher bas", 10, (330, 306, 330, 348), (346, 346), "start",
     "Le plancher, sur vide sanitaire ou sur terre-plein, perd de la chaleur vers le sol."),
]


def svg_deperditions():
    fl = "".join(
        f'<g class="hd-dep-a" data-k="{k}" tabindex="0" role="button" aria-label="{e(lib)} : {pct} %" '
        f'data-info="{e(info)}" data-t="{e(lib)} : {pct} %"><polygon points="{fleche(*xy, 6 + pct * 0.55)}"/>'
        f'<text x="{tx}" y="{ty}" text-anchor="{anc}" class="hd-t hd-t-b">'
        + (f'Murs et ponts<tspan x="{tx}" dy="17">thermiques : ' if k == "murs" else f"{lib} : ")
        + f'<tspan class="hd-dep-pc">{pct} %</tspan>' + ("</tspan>" if k == "murs" else "") + "</text></g>"
        for k, lib, pct, xy, (tx, ty), anc, info in DEPERDITIONS)
    return f"""<svg class="hd-svg hd-svg-m" id="hd-dep-svg" viewBox="0 0 680 370" role="group" aria-label="Répartition des déperditions thermiques d'une maison : touche une flèche">
<rect width="680" height="306" fill="#F4F8FC"/><rect y="306" width="680" height="64" fill="#E6DCC6"/>
<g id="hd-dep-p-toit" class="hd-dep-p"><polygon points="200,176 330,96 460,176" fill="#4F7F3A" stroke="#2F4F22" stroke-width="2"/></g>
<g id="hd-dep-p-air" class="hd-dep-p"><rect x="380" y="100" width="22" height="44" fill="#B26A00" stroke="#6B4A2B" stroke-width="2"/></g>
<g id="hd-dep-p-murs" class="hd-dep-p"><rect x="222" y="176" width="216" height="130" fill="#F3EEDF" stroke="#7A6F5A" stroke-width="2"/></g>
<g id="hd-dep-p-fen" class="hd-dep-p"><rect x="240" y="200" width="56" height="52" fill="#BFD9F2" stroke="#1F5FA8" stroke-width="2"/>
  <line x1="268" y1="200" x2="268" y2="252" stroke="#1F5FA8"/></g>
<rect x="352" y="232" width="40" height="74" fill="#4F7F3A" stroke="#2F4F22" stroke-width="2"/>
<g id="hd-dep-p-plancher" class="hd-dep-p"><rect x="222" y="300" width="216" height="8" fill="#9AA3AB"/></g>
{fl}
</svg>"""


# ------------------------------------------------------------ pont thermique : isolation intérieure ou extérieure
def svg_pont():
    return f"""<svg class="hd-svg hd-svg-m hd-pt iti" id="hd-pt-svg" viewBox="0 0 560 300" role="img" aria-labelledby="hd-pt-tt">
<title id="hd-pt-tt">Coupe d'un mur extérieur et d'un plancher intermédiaire, isolés par l'intérieur ou par l'extérieur</title>
<defs>{HACHURES.format(id="hd-hach-pt")}<linearGradient id="hd-pt-ext" x1="0" x2="1"><stop offset="0" stop-color="#C7DCF2"/><stop offset="1" stop-color="#EAF2FB"/></linearGradient>
<linearGradient id="hd-pt-int" x1="0" x2="1"><stop offset="0" stop-color="#FCEBDD"/><stop offset="1" stop-color="#F8D2BC"/></linearGradient></defs>
<rect width="250" height="300" fill="url(#hd-pt-ext)"/><rect x="300" width="260" height="300" fill="url(#hd-pt-int)"/>
<text x="16" y="26" class="hd-t hd-t-b" fill="#1F5FA8">Extérieur : 0 °C</text>
<text x="544" y="26" class="hd-t hd-t-b" text-anchor="end" fill="#B42318">Intérieur chauffé : 19 °C</text>
<rect x="250" y="0" width="50" height="300" fill="#BDBFC2" stroke="#6E7479" stroke-width="1.5"/>
<text x="275" y="292" class="hd-t hd-t-s" text-anchor="middle">mur</text>
<rect x="300" y="140" width="260" height="22" fill="#A9ADB2" stroke="#6E7479" stroke-width="1.5"/>
<text x="470" y="184" class="hd-t hd-t-s" text-anchor="middle">plancher (dalle)</text>
<g class="hd-pt-iti"><rect x="300" y="0" width="26" height="140" fill="url(#hd-hach-pt)"/><rect x="300" y="162" width="26" height="138" fill="url(#hd-hach-pt)"/>
  <text x="336" y="64" class="hd-t hd-t-s">isolant</text></g>
<g class="hd-pt-ite"><rect x="222" y="0" width="28" height="300" fill="url(#hd-hach-pt)"/><text x="214" y="64" class="hd-t hd-t-s" text-anchor="end">isolant</text></g>
<polygon class="hd-pt-faible" points="{fleche(470, 88, 150, 88, 4)}"/>
<polygon class="hd-pt-faible" points="{fleche(470, 230, 150, 230, 4)}"/>
<g class="hd-pt-iti"><polygon class="hd-pt-fuite" points="{fleche(520, 151, 120, 151, 15)}"/>
  <circle cx="300" cy="151" r="22" class="hd-pt-zone"/>
  <text x="112" y="132" class="hd-t hd-t-b" text-anchor="end" fill="#B42318">pont thermique</text></g>
</svg>"""


# ------------------------------------------------------------ étanchéité : points faibles (CETE Sud-Ouest)
FUITES = [("Menuiseries extérieures", 41), ("Passages des équipements électriques", 38), ("Trappes", 12),
          ("Tuyauteries", 7), ("Structure du bâtiment", 2)]


def svg_fuites():
    lignes = "".join(
        f'<text x="246" y="{30 + i * 34}" class="hd-t" text-anchor="end">{lib}</text>'
        f'<rect x="256" y="{16 + i * 34}" width="{pct * 7}" height="20" fill="#1F5FA8"/>'
        f'<text x="{262 + pct * 7}" y="{31 + i * 34}" class="hd-t hd-t-b">{pct} %</text>'
        for i, (lib, pct) in enumerate(FUITES))
    return (f'<svg class="hd-svg hd-svg-m" viewBox="0 0 600 186" role="img" aria-label="Points faibles de l\'étanchéité '
            f'à l\'air : ' + ", ".join(f"{lib} {pct} %" for lib, pct in FUITES) + f'">{lignes}</svg>')


# ------------------------------------------------------------ ventilation : plan d'une maison, l'air suit son trajet
def svg_vmc():
    murs = [  # cloisons, avec les passages des portes
        "M30,200 H300 M340,200 H520 M560,200 H740 M780,200 H830", "M30,245 H250 M290,245 H450 M490,245 H570 M610,245 H700 M740,245 H830",
        "M380,30 V200 M605,30 V200", "M330,245 V350 M530,245 V350 M650,245 V350"]
    pieces = [("Séjour", 110, 124), ("Chambre 1", 436, 124), ("Chambre 2", 662, 124), ("Dégagement", 430, 233),
              ("Cuisine", 100, 278), ("Salle de bains", 384, 280), ("WC", 624, 278)]
    noms = "".join(f'<text x="{x}" y="{y}" class="hd-t hd-t-b hd-vmc-np" text-anchor="middle">{n}</text>' for n, x, y in pieces)
    return f"""<svg class="hd-svg" id="hd-vmc-svg" viewBox="0 0 860 400" role="img" aria-labelledby="hd-vmc-tt">
<title id="hd-vmc-tt">Plan d'une maison : l'air neuf entre dans les pièces principales, passe sous les portes et est extrait
dans les pièces de service</title>
<defs>{MARQUEUR.format(id="hd-mk-neuf", c="#1F5FA8")}{MARQUEUR.format(id="hd-mk-vicie", c="#8A6D57")}{MARQUEUR.format(id="hd-mk-tiede", c="#D97A00")}</defs>
<rect x="30" y="30" width="800" height="320" fill="#FFFFFF" stroke="#1C2530" stroke-width="9"/>
<rect x="34" y="34" width="342" height="162" fill="#F4F8FC"/><rect x="384" y="34" width="217" height="162" fill="#F4F8FC"/>
<rect x="609" y="34" width="217" height="162" fill="#F4F8FC"/>
<rect x="34" y="249" width="292" height="97" fill="#FBF3EA"/><rect x="334" y="249" width="192" height="97" fill="#FBF3EA"/>
<rect x="534" y="249" width="112" height="97" fill="#FBF3EA"/><rect x="654" y="249" width="172" height="97" fill="#F1F2EE"/>
<path d="{' '.join(murs)}" fill="none" stroke="#1C2530" stroke-width="5"/>
{noms}
<text x="740" y="264" class="hd-t hd-t-s" text-anchor="middle">local technique</text>
<g id="hd-vmc-flux"></g>
<g class="hd-vmc-sf"><rect x="690" y="276" width="100" height="50" rx="4" class="hd-vmc-caisson"/>
  <text x="740" y="298" class="hd-t hd-t-b" text-anchor="middle">Caisson</text><text x="740" y="315" class="hd-t hd-t-s" text-anchor="middle">VMC</text></g>
<g class="hd-vmc-df"><rect x="690" y="276" width="100" height="50" rx="4" class="hd-vmc-caisson"/>
  <line x1="690" y1="276" x2="790" y2="326" stroke="#46525C" stroke-width="1.5"/><line x1="690" y1="326" x2="790" y2="276" stroke="#46525C" stroke-width="1.5"/>
  <text x="740" y="270" class="hd-t hd-t-s hd-vmc-ech" text-anchor="middle">échangeur</text></g>
<g id="hd-vmc-bouches"></g>
<g id="hd-vmc-temp" class="hd-t hd-t-s"></g>
</svg>"""


# ------------------------------------------------------------ puits canadien : l'air se rapproche de la température du sol
def svg_puits():
    return """<svg class="hd-svg hd-svg-m" id="hd-pu-svg" viewBox="0 0 760 230" role="img" aria-labelledby="hd-pu-tt">
<title id="hd-pu-tt">Puits canadien : l'air neuf circule dans un tube enterré avant d'entrer dans la maison</title>
<defs><linearGradient id="hd-pu-sol" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#D9C6A4"/><stop offset="1" stop-color="#B89A6E"/></linearGradient></defs>
<rect width="760" height="72" fill="#EAF2FB"/><rect y="72" width="760" height="158" fill="url(#hd-pu-sol)"/>
<line x1="0" y1="72" x2="760" y2="72" stroke="#46525C" stroke-width="2"/>
<rect x="590" y="14" width="150" height="58" fill="#FFFFFF" stroke="#1C2530" stroke-width="3"/>
<polygon points="580,16 665,-4 750,16" fill="#8C4A2F"/>
<text x="665" y="40" class="hd-t hd-t-b" text-anchor="middle">Maison</text><text x="665" y="58" class="hd-t hd-t-s" text-anchor="middle">vers la VMC</text>
<rect x="40" y="22" width="22" height="16" fill="#46525C"/><text x="72" y="34" class="hd-t hd-t-s">entrée d'air neuf + filtre</text>
<g id="hd-pu-tube"></g>
<text x="300" y="214" class="hd-t hd-t-b" text-anchor="middle">Sol entre 1,5 et 3 m de profondeur : 12 à 14 °C toute l'année</text>
<text x="72" y="58" class="hd-t hd-t-b" id="hd-pu-tin"></text><text x="626" y="112" class="hd-t hd-t-s">air neuf vers la VMC :</text><text x="626" y="132" class="hd-t hd-t-b" id="hd-pu-tout"></text>
</svg>"""


# ------------------------------------------------------------ figure 11 : cycle de la pompe à chaleur
PAC_ETAPES = [
    (1, "evap", "La chaleur de l'élément extérieur (air, eau, sol) provoque la <b>vaporisation</b> du fluide frigorigène "
                "dans l'<b>évaporateur</b>."),
    (2, "comp", "Ce fluide est ensuite <b>comprimé</b> (dans le <b>compresseur</b>) pour élever sa température."),
    (3, "cond", "Le fluide frigorigène réchauffe l'eau ou l'air de chauffage dans le <b>condenseur</b>. En se "
                "refroidissant, il retourne à l'état liquide."),
    (4, "det", "Le passage dans le <b>détendeur</b> permet d'abaisser la pression du liquide frigorigène et de le "
               "préparer à la vaporisation pour un nouveau cycle."),
]


def svg_pac():
    serp = lambda x: "M{0},236 ".format(x) + " ".join(
        f"L{x + (18 if i % 2 else -18)},{236 - (i + 1) * 9}" for i in range(9)) + f" L{x},146"
    return f"""<svg class="hd-svg" id="hd-pac-svg" viewBox="0 0 860 330" role="img" aria-labelledby="hd-pac-tt">
<title id="hd-pac-tt">Cycle d'une pompe à chaleur : évaporateur, compresseur, condenseur, détendeur</title>
<defs>{MARQUEUR.format(id="hd-mk-pac", c="#46525C")}</defs>
<rect x="8" y="34" width="214" height="288" fill="#E6F2E8" rx="6"/><rect x="232" y="34" width="396" height="288" fill="#F6F7F4" rx="6"/>
<rect x="638" y="34" width="214" height="288" fill="#FBE9DF" rx="6"/>
<text x="115" y="56" class="hd-t hd-t-b" text-anchor="middle">Captage de la chaleur</text>
<text x="115" y="74" class="hd-t hd-t-s" text-anchor="middle">air, eau ou sol</text>
<text x="246" y="56" class="hd-t hd-t-b">Pompe à chaleur</text>
<text x="745" y="56" class="hd-t hd-t-b" text-anchor="middle">Distribution de la chaleur</text>
<text x="745" y="74" class="hd-t hd-t-s" text-anchor="middle">et accumulation</text>
<circle cx="70" cy="128" r="22" fill="#F2B705"/><path d="M40,190 q15,-12 30,0 t30,0 t30,0" fill="none" stroke="#1F5FA8" stroke-width="3"/>
<path d="M40,210 q15,-12 30,0 t30,0 t30,0" fill="none" stroke="#1F5FA8" stroke-width="3"/>
<rect x="36" y="232" width="150" height="40" fill="#B89A6E"/><text x="111" y="257" class="hd-t hd-t-s" text-anchor="middle" fill="#fff">sol</text>
<polygon class="hd-pac-chaleur hd-pac-froid" points="{fleche(170, 192, 262, 192, 10)}"/>
<text x="216" y="176" class="hd-t hd-t-s" text-anchor="middle">chaleur captée</text>
<polygon points="742,96 802,130 682,130" fill="#8C4A2F"/><rect x="692" y="130" width="100" height="92" fill="#fff" stroke="#1C2530" stroke-width="2.5"/>
<path d="M704,206 h76 M704,196 h76 M704,186 h76" stroke="#D97A00" stroke-width="3"/>
<text x="742" y="246" class="hd-t hd-t-s" text-anchor="middle">radiateurs, plancher</text><text x="742" y="262" class="hd-t hd-t-s" text-anchor="middle">chauffant, eau chaude</text>
<polygon class="hd-pac-chaleur hd-pac-chaud" points="{fleche(600, 192, 688, 192, 10)}"/>
<text x="644" y="176" class="hd-t hd-t-s" text-anchor="middle">chaleur cédée</text>
<path d="M430,4 V58" stroke="#1C2530" stroke-width="3" marker-end="url(#hd-mk-pac)"/>
<text x="440" y="18" class="hd-t hd-t-s">énergie motrice (électricité)</text>
<path id="hd-pac-boucle" d="M290,146 V90 H402 M458,90 H580 V146 M580,236 V292 H452 M408,292 H290 V236" fill="none" stroke="#9AA3AB" stroke-width="6" stroke-linejoin="round"/>
<g class="hd-pac-c" id="hd-pac-evap"><rect x="262" y="140" width="56" height="102" rx="5"/><path d="{serp(290)}" class="hd-pac-serp"/>
  <text x="290" y="262" class="hd-t hd-t-b" text-anchor="middle">1 · Évaporateur</text></g>
<g class="hd-pac-c" id="hd-pac-comp"><circle cx="430" cy="90" r="28"/><path d="M414,90 a16,16 0 1,1 16,16" fill="none" stroke="#1C2530" stroke-width="3"/>
  <text x="430" y="136" class="hd-t hd-t-b" text-anchor="middle">2 · Compresseur</text></g>
<g class="hd-pac-c" id="hd-pac-cond"><rect x="552" y="140" width="56" height="102" rx="5"/><path d="{serp(580)}" class="hd-pac-serp"/>
  <text x="580" y="262" class="hd-t hd-t-b" text-anchor="middle">3 · Condenseur</text></g>
<g class="hd-pac-c" id="hd-pac-det"><polygon points="408,280 430,292 408,304"/><polygon points="452,280 430,292 452,304"/>
  <text x="430" y="322" class="hd-t hd-t-b" text-anchor="middle">4 · Détendeur</text></g>
<g id="hd-pac-flux"></g>
</svg>"""


# ------------------------------------------------------------ figure 15 : programmation hebdomadaire (grille cliquable)
JOURS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]


def grille_prog():
    tete = "<tr><th></th>" + "".join(f"<th>{hh}</th>" for hh in range(24)) + "</tr>"
    lignes = "".join(
        f"<tr><th>{j}</th>" + "".join(
            f'<td><button type="button" class="hd-pc" data-d="{d}" data-h="{hh}" aria-pressed="false" '
            f'aria-label="{j}, {hh} h"></button></td>' for hh in range(24)) + "</tr>"
        for d, j in enumerate(JOURS))
    return f'<div class="hd-pg-wrap"><table class="hd-pg" id="hd-pg">{tete}{lignes}</table></div>'


# ------------------------------------------------------------ rendu du cours
def render(h):
    obj = "".join(f"<li>{o}</li>" for o in OBJECTIFS)
    pre = "".join(f"<li>{p}</li>" for p in PREREQUIS)
    # pas de tableau de compétences : le cours ne s'adresse pas à une seule filière
    fiche = (f'<div class="hd-pb"><b>Problématique :</b> {PROBLEMATIQUE}</div>'
             f'<div class="hd-fiche"><div><h3>Objectifs</h3><ul>{obj}</ul></div>'
             f"<div><h3>Prérequis</h3><ul>{pre}</ul></div></div>")
    cs = h.course_section

    def formule(f, unites):
        return f'<div class="formule"><span class="f-main">{f}</span><span class="f-units">{unites}</span></div>'

    def remarque(t):
        return f'<div class="remarque"><p><b>Remarque :</b> {t}</p></div>'

    s1 = cs(1, "hd-bio", "Respecter une architecture bioclimatique",
        "<p>Depuis le 1<sup>er</sup> janvier 2022, les maisons neuves doivent respecter la réglementation "
        "environnementale <b>RE2020</b>, qui fixe plusieurs critères que nous allons détailler.</p>"
        "<p>L'<b>architecture bioclimatique</b> permet d'assurer un très bon confort de vie aux habitants en respectant "
        "l'environnement et en minimisant au maximum le coût énergétique.</p>"
        "<h3>Figure 1 — Principes de l'architecture bioclimatique</h3>"
        '<p class="cours-defi">À toi : change de saison et regarde jusqu\'où le soleil entre dans le séjour ; touche un '
        "principe pour le voir sur la maison.</p>"
        '<div class="hd-fig-i" id="hd-bio-fig"><div class="hd-btns" role="group" aria-label="Saison">'
        '<button type="button" class="hd-b hd-bio-s" data-s="hiver" aria-pressed="true">Hiver</button>'
        '<button type="button" class="hd-b hd-bio-s" data-s="mi" aria-pressed="false">Mi-saison</button>'
        '<button type="button" class="hd-b hd-bio-s" data-s="ete" aria-pressed="false">Été</button></div>'
        + svg_bio() +
        '<p class="hd-out" id="hd-bio-txt" aria-live="polite"></p><div class="hd-notes">' +
        "".join(f'<button type="button" class="hd-note hd-bio-n" data-g="{g}" aria-pressed="false">{t}</button>'
                for g, t in NOTES_BIO) +
        '</div><p class="small">Hauteur du soleil à midi en France métropolitaine (vers 46° de latitude nord) : '
        "environ 21° au solstice d'hiver, 44° aux équinoxes, 67° au solstice d'été.</p></div>"
        "<p>Les pièces de vie sont exposées au sud afin de bénéficier de la lumière et des apports solaires. Au nord, des "
        "pièces peu chauffées (garage, couloir, cellier…) servent de tampon et renforcent l'isolation thermique. À l'est, "
        "les chambres bénéficient du soleil matinal et de la fraîcheur en soirée.</p>"
        "<h3>Où placer chaque pièce ?</h3>" + h.jeu_html(JEU_PIECES, ORIENTATIONS, "jeu-pieces"))

    materiaux = [("ch-ph-parpaing", "Parpaing", "0,95", "Utilisation de ressources non renouvelables."),
                 ("ch-ph-ossature-bois", "Ossature bois", "0,12", "Bilan carbone très bon."),
                 ("ch-ph-monomur", "Brique Monomur<sup>®</sup>", "0,13",
                  "Les briques utilisent de l'argile (ressource non renouvelable)."),
                 ("ch-ph-terre-crue", "Brique de terre crue", "0,6 à 1",
                  "Impact sur l'environnement quasi nul lorsqu'elles sont produites sur chantier.")]
    cartes_mat = '<div class="hd-mats">' + "".join(
        f'<div class="hd-mat">{img(h, n, "Maison en construction : " + html.unescape(t.replace("<sup>®</sup>", "")), "", 260, "hd-mat-f")}'
        f'<b>{t}</b><span class="hd-lam">λ = {l} W/(m·K)</span><span>{c}</span></div>'
        for n, t, l, c in materiaux) + "</div>"
    s2 = cs(2, "hd-dep", "Limiter les déperditions thermiques",
        "<p>Les <b>déperditions thermiques</b> correspondent aux pertes de chaleur de l'habitat par ses parois "
        "extérieures, par ses ponts thermiques et par son renouvellement d'air.</p>"
        "<h3>Figure 2 — Répartition des déperditions thermiques d'une maison</h3>"
        '<p class="cours-defi">Touche une flèche : par où la chaleur s\'échappe-t-elle ?</p>'
        '<div class="hd-fig-i" id="hd-dep-fig">' + svg_deperditions() +
        '<p class="hd-out" id="hd-dep-txt" aria-live="polite">Plus la flèche est large, plus la part des pertes est '
        "grande.</p><p class=\"small\">Ordres de grandeur : arrondies, ces parts totalisent 105 %.</p></div>"
        "<h3>2.1 Compacité des bâtiments</h3>"
        "<p>La forme du bâtiment est aussi importante. On définit le <b>facteur de compacité C</b> d'un bâtiment : c'est "
        "le rapport de la surface des parois en contact avec une zone non chauffée, appelées <b>parois "
        "déperditives</b>, par le volume chauffé.</p>"
        + formule("C = S<sub>p</sub> / V", "avec S<sub>p</sub> surface des parois déperditives en m² et V volume à "
                  "chauffer en m³") +
        remarque("la compacité est la meilleure lorsque le facteur de compacité est le plus faible.") +
        '<div class="simu" id="hd-comp"><h3>Simulateur — Plain-pied ou étage ?</h3>'
        "<p>Pour la même surface habitable, compare deux maisons en forme de pavé : l'une de plain-pied, l'autre à "
        "étage.</p><div class=\"simu-grid\">"
        '<label>Surface habitable <output id="hd-comp-so">100 m²</output><input type="range" id="hd-comp-s" min="60" '
        'max="200" step="10" value="100"></label>'
        '<label>Longueur / largeur <output id="hd-comp-ro">1,5</output><input type="range" id="hd-comp-r" min="1" '
        'max="3" step="0.1" value="1.5"></label></div>'
        '<svg class="hd-svg" id="hd-comp-svg" viewBox="0 0 640 250" role="img" aria-label="Les deux maisons dessinées '
        'à la même échelle"></svg><div class="hd-tab-w"><table class="t hd-tab" id="hd-comp-out"></table></div>'
        '<p class="simu-verdict ok" id="hd-comp-v" aria-live="polite"></p>'
        '<p class="small">Toutes les parois sont comptées déperditives (murs, toiture, plancher bas) ; hauteur d\'un '
        "niveau : 2,5 m.</p></div>"
        "<h3>2.2 Matériaux de construction</h3>"
        "<p>Les matériaux utilisés dans la construction des maisons n'ont pas tous les mêmes caractéristiques "
        "d'isolation. La <b>conductivité thermique (λ)</b> est une caractéristique propre à chaque matériau : elle "
        "caractérise l'aptitude d'un corps à conduire la chaleur. Elle s'exprime en watt par mètre-kelvin "
        "(W/(m·K)).</p>" + remarque("plus λ est faible, plus le matériau est isolant.") +
        "<h3>Parois de matériaux utilisés dans la construction (exemples)</h3>" + cartes_mat +
        '<div class="simu" id="hd-lam"><h3>Simulateur — Quelle épaisseur pour isoler autant ?</h3>'
        "<p>Pour atteindre une même résistance thermique R (partie 2.3), il faut l'épaisseur e = R × λ.</p>"
        '<div class="simu-grid"><label>Résistance visée R <output id="hd-lam-ro">1 m²·K/W</output>'
        '<input type="range" id="hd-lam-r" min="0.5" max="5" step="0.5" value="1"></label></div>'
        '<svg class="hd-svg hd-svg-m" id="hd-lam-svg" viewBox="0 0 640 230" role="img" aria-label="Épaisseur de chaque '
        'matériau pour la résistance visée"></svg>'
        '<p class="small">La laine de verre (λ ≈ 0,035 W/(m·K), valeur usuelle indicative) est ajoutée pour comparer '
        "les matériaux de structure à un isolant.</p></div>"
        "<h3>Isolation des parois</h3><p>Pour limiter au maximum les déperditions thermiques, il faut isoler. Plusieurs "
        "procédés existent.</p><ul><li>L'<b>isolation intérieure</b> consiste à placer les isolants sur la face "
        "intérieure des murs des habitations. Facile à mettre en œuvre, elle permet de réaliser simplement et "
        "rapidement des économies d'énergie.</li></ul>"
        + img(h, "ch-fig03-isolation-interieure", "Isolation par laine de verre (mur, isolant, rails, plâtre) et "
              "isolation par placoplâtre (mur, point de colle, isolant, plâtre, bande à joint)",
              "Figure 3 — Exemples d'isolation intérieure", 1000) +
        "<ul><li>L'<b>isolation extérieure</b> consiste à placer les isolants sur la face extérieure des murs des "
        "habitations. Elle permet de supprimer les ponts thermiques et d'obtenir un haut niveau de performance.</li></ul>"
        + img(h, "ch-fig04-isolation-exterieure", "Isolation extérieure enduite, isolation extérieure à bardage et "
              "toiture végétalisée, couche par couche", "Figure 4 — Exemples d'isolation extérieure et de toiture "
              "végétalisée", 1000) +
        "<h3>Pont thermique : isolation intérieure ou extérieure ?</h3>"
        '<div class="hd-fig-i" id="hd-pt"><div class="hd-btns" role="group" aria-label="Procédé d\'isolation">'
        '<button type="button" class="hd-b hd-pt-b" data-m="iti" aria-pressed="true">Isolation intérieure</button>'
        '<button type="button" class="hd-b hd-pt-b" data-m="ite" aria-pressed="false">Isolation extérieure</button>'
        "</div>" + svg_pont() + '<p class="hd-out" id="hd-pt-txt" aria-live="polite"></p></div>'
        "<h3>2.3 Grandeurs thermiques caractéristiques des matériaux</h3>"
        "<p>Outre la conductivité thermique, il existe d'autres grandeurs thermiques importantes au niveau des "
        "matériaux.</p><ul><li>La <b>résistance thermique R</b> est le critère qui définit la performance d'un produit "
        "isolant vendu dans le commerce. Elle dépend de la conductivité thermique du matériau (λ) et de son épaisseur "
        "(e).</li></ul>" + formule("R = e / λ", "avec e en m, λ en W/(m·K) et R en m²·K/W") +
        "<p>Pour une paroi constituée de plusieurs couches de matériaux différents, la résistance thermique totale est "
        "égale à la somme des résistances thermiques des couches de la paroi :</p>"
        + formule("R<sub>totale</sub> = R<sub>1</sub> + R<sub>2</sub> + R<sub>3</sub> + R<sub>4</sub> + …", "") +
        remarque("plus la résistance thermique est élevée, plus le produit est isolant.") +
        "<ul><li>Le <b>coefficient de transfert thermique U</b> caractérise la quantité de chaleur qui traverse un mètre "
        "carré de matériau lorsqu'il y a une différence de température de 1 K entre les deux faces de la paroi.</li></ul>"
        + formule("U = 1 / R", "avec U en W/(m²·K)") +
        remarque("plus le coefficient de transfert thermique est faible, plus le produit est isolant.") +
        "<ul><li>La <b>déperdition thermique D</b> d'une paroi représente la puissance perdue par la paroi lorsque la "
        "différence de température est de 1 K.</li></ul>"
        + formule("D = U × S = (1 / R) × S", "avec D en W/K et S surface de la paroi en m²") +
        '<div class="simu" id="hd-pa"><h3>Simulateur — Compose ta paroi, couche par couche</h3>'
        "<p>La couche 1 est côté intérieur, la couche 4 côté extérieur. Change un matériau ou une épaisseur : R, U et D se "
        "recalculent, et la courbe rouge montre la température dans l'épaisseur du mur.</p>"
        '<div class="hd-pa-l" id="hd-pa-l"></div><div class="simu-grid">'
        '<label>Surface de la paroi S <output id="hd-pa-so">20 m²</output><input type="range" id="hd-pa-s" min="5" '
        'max="100" step="5" value="20"></label>'
        '<label>Température extérieure <output id="hd-pa-to">0 °C</output><input type="range" id="hd-pa-t" min="-10" '
        'max="15" step="1" value="0"></label></div>'
        '<svg class="hd-svg" id="hd-pa-svg" viewBox="0 0 640 250" role="img" aria-label="Coupe de la paroi et '
        'température dans son épaisseur"></svg>'
        '<div class="simu-out simu-out4" aria-live="polite"><div><span>R totale</span><b id="hd-pa-rt"></b></div>'
        '<div><span>U = 1 / R</span><b id="hd-pa-u"></b></div><div><span>D = U × S</span><b id="hd-pa-d"></b></div>'
        '<div><span>Puissance perdue</span><b id="hd-pa-p"></b></div></div>'
        '<p class="small">Puissance perdue : P = D × (19 °C − température extérieure). Conductivités : valeurs du cours '
        "(parpaing, ossature bois, Monomur, terre crue : 0,8 au milieu de 0,6 à 1) et valeurs usuelles indicatives pour "
        "les autres matériaux.</p></div>"
        "<h3>2.4 Parois vitrées</h3><p>Les parois vitrées permettent l'arrivée de l'éclairage naturel et des apports "
        "solaires passifs, mais elles ont pour inconvénient de provoquer des pertes thermiques.</p>"
        "<h3>Figures 5 et 6 — Vitrages : température de la face intérieure, coefficient U<sub>w</sub> et facteur "
        "solaire S<sub>w</sub></h3>"
        '<div class="hd-fig-i" id="hd-vi"><div class="hd-btns" role="group" aria-label="Type de vitrage">'
        '<button type="button" class="hd-b hd-vi-b" data-v="simple" aria-pressed="false">Simple vitrage</button>'
        '<button type="button" class="hd-b hd-vi-b" data-v="double" aria-pressed="false">Double vitrage standard</button>'
        '<button type="button" class="hd-b hd-vi-b" data-v="vir" aria-pressed="true">Double vitrage performant (VIR, '
        "argon)</button>"
        '<button type="button" class="hd-b hd-vi-b" data-v="triple" aria-pressed="false">Triple vitrage (argon)</button>'
        '</div><div class="hd-vi-row"><svg class="hd-svg" id="hd-vi-svg" viewBox="0 0 420 240" role="img" '
        'aria-label="Le vitrage choisi et la température de sa face intérieure"></svg>'
        '<div class="hd-vi-d"><div class="simu-out" aria-live="polite"><div><span>Face intérieure</span><b id="hd-vi-t">'
        '</b></div><div><span>U<sub>w</sub></span><b id="hd-vi-uw"></b></div><div><span>S<sub>w</sub></span>'
        '<b id="hd-vi-sw"></b></div></div><p class="hd-out" id="hd-vi-txt"></p>'
        '<label class="hd-lab">Surface de la fenêtre <input type="number" id="hd-vi-s" min="0.5" max="10" step="0.5" '
        'value="2"> m²</label><p class="hd-out" id="hd-vi-d" aria-live="polite"></p></div></div>'
        '<p class="small">Valeurs des figures 5 et 6 du cours ; U<sub>w</sub> en W/(m²·K). VIR : vitrage à isolation '
        "renforcée, couche peu émissive.</p></div>"
        + remarque("les parois vitrées sont caractérisées par un coefficient de transfert thermique <b><i>U<sub>w</sub>"
                   "</i></b> et un facteur solaire <b><i>S<sub>w</sub></i></b> (compris entre 0 et 1).") +
        "<p>L'<b>apport solaire passif</b> consiste à laisser entrer dans l'habitat le rayonnement solaire. C'est une "
        "manière efficace et simple de chauffer un logement.</p>"
        "<p>La surface vitrée doit être comprise entre 16 et 18 % de la surface habitable, avec une répartition selon "
        "l'orientation : 50 % au sud, 20 à 30 % à l'est, 20 % à l'ouest, 0 à 10 % au nord.</p>"
        '<div class="simu" id="hd-sv"><h3>Simulateur — Combien de vitrages, et où ?</h3><div class="simu-grid">'
        '<label>Surface habitable <output id="hd-sv-o">100 m²</output><input type="range" id="hd-sv-s" min="50" '
        'max="250" step="5" value="100"></label></div><div class="hd-sv-row">'
        '<svg class="hd-svg" id="hd-sv-svg" viewBox="-40 0 380 300" role="img" aria-label="Répartition des vitrages '
        'autour de la maison"></svg><div class="hd-tab-w"><table class="t hd-tab" id="hd-sv-out"></table></div></div></div>'
        "<h3>2.5 Étanchéité des bâtiments</h3>"
        "<p>Étanchéifier un bâtiment consiste à éliminer toutes les fuites d'air parasites passant au travers de son "
        "enveloppe. Une bonne étanchéité à l'air concourt à la performance énergétique de la maison et au confort de ses "
        "occupants.</p><div class=\"cours-split\"><div><p><b>Test d'étanchéité :</b> la maison est mise sous pression ou "
        "en dépression, entrées d'air et bouches d'aération occultées. Le débit d'air nécessaire au maintien d'une "
        "pression constante permet de déterminer la valeur des fuites d'air (&lt; 0,6 m³/(h·m²)).</p>"
        + remarque("une campagne de mesures de l'étanchéité à l'air menée par le CETE Sud-Ouest dans 123 logements "
                   "révèle que les points faibles sont pour 41 % les menuiseries extérieures ; 38 % les passages des "
                   "équipements électriques ; 12 % les trappes ; 7 % les tuyauteries et 2 % la structure du bâtiment.")
        + "</div>" + img(h, "ch-test-etancheite", "Test d'étanchéité : une porte soufflante munie d'un ventilateur et "
                         "d'un capteur est posée dans l'encadrement de la porte d'entrée", "Le test de la porte "
                         "soufflante", 400) + "</div>"
        "<h3>Les points faibles de l'étanchéité à l'air (123 logements)</h3>" + svg_fuites())

    s3 = cs(3, "hd-air", "Renouveler l'air intérieur",
        "<p>Avec l'amélioration des techniques d'isolation, les habitats sont de plus en plus étanches à l'air. Une "
        "ventilation devient donc nécessaire pour :</p><ul><li>apporter un air intérieur neuf et pourvoir à nos besoins "
        "en oxygène ;</li><li>éliminer l'humidité et les pollutions intérieures ;</li><li>apporter l'oxygène nécessaire "
        "aux appareils à combustion.</li></ul>"
        "<h3>3.1 La ventilation mécanique contrôlée (VMC)</h3><div class=\"hd-deux\"><div>"
        + img(h, "ch-fig07-vmc-simple-flux", "VMC simple flux : l'air neuf entre par les fenêtres du séjour et des "
              "chambres, l'air vicié est aspiré dans la cuisine, la salle de bains et les WC", "Figure 7 — VMC simple "
              "flux", 560) +
        "<p>La <b>VMC simple flux</b> permet d'extraire l'<b>air vicié</b> des pièces de service (cuisine, salle de "
        "bains, toilettes…). De l'<b>air neuf</b> entre par les ouvertures pratiquées au-dessus des fenêtres des pièces "
        "principales.</p></div><div>"
        + img(h, "ch-fig08-vmc-double-flux", "VMC double flux : un caisson avec échangeur aspire l'air vicié et insuffle "
              "l'air neuf réchauffé dans les pièces principales", "Figure 8 — VMC double flux", 560) +
        "<p>La <b>VMC double flux</b> permet d'extraire l'<b>air vicié</b> des pièces de service (cuisine, salle de "
        "bains, toilettes…). Elle aspire de l'air neuf à l'extérieur, qu'elle réchauffe dans un échangeur avant de le "
        "<b>réinjecter</b> dans les pièces principales.</p></div></div>"
        "<h3>Suis l'air dans la maison</h3>"
        '<div class="hd-fig-i" id="hd-vmc"><div class="hd-btns" role="group" aria-label="Type de VMC">'
        '<button type="button" class="hd-b hd-vmc-b" data-m="sf" aria-pressed="true">VMC simple flux</button>'
        '<button type="button" class="hd-b hd-vmc-b" data-m="df" aria-pressed="false">VMC double flux</button></div>'
        + svg_vmc() +
        '<div class="hd-leg"><span class="hd-leg-neuf">air neuf froid</span><span class="hd-leg-tiede">air neuf '
        'réchauffé</span><span class="hd-leg-vicie">air vicié</span></div>'
        '<p class="hd-out" id="hd-vmc-txt" aria-live="polite"></p>'
        '<p class="small">Températures indicatives, pour 0 °C dehors et 20 °C dedans.</p></div>'
        + remarque("il faut prévoir un espace sous les portes afin d'assurer la circulation de l'air.") +
        "<h3>3.2 Puits canadien</h3><div class=\"cours-split\"><div><p>Le <b>puits canadien</b> est un procédé "
        "géothermique qui permet de réchauffer ou de refroidir l'air neuf qui alimente la VMC. Quelle que soit la "
        "saison, la température du sol se maintient entre 12 et 14 °C à une profondeur de 1,5 à 3 m :</p><ul>"
        "<li>l'hiver, le sol est plus chaud que l'air extérieur : l'air qui circule se réchauffe ;</li>"
        "<li>l'été, le sol est plus froid que l'air extérieur : l'air qui circule est refroidi.</li></ul></div>"
        + img(h, "ch-fig09-puits-canadien", "Puits canadien : bouche d'entrée d'air neuf avec filtre, conduit enterré "
              "de 1,5 à 3 m, incliné de 1 à 3 % sur 30 à 50 m, diamètre de l'ordre de 20 cm, couplé à la ventilation",
              "Figure 9 — Principe du puits canadien (température du sol en été et en hiver : 12 à 14 °C)", 620) +
        "</div>"
        '<div class="simu" id="hd-pu"><h3>Simulateur — Dans le tube, l\'air change de température</h3>'
        '<div class="hd-btns"><button type="button" class="hd-b hd-pu-b" data-t="-5" aria-pressed="true">Hiver (−5 °C)'
        '</button><button type="button" class="hd-b hd-pu-b" data-t="32" aria-pressed="false">Été (32 °C)</button></div>'
        '<div class="simu-grid"><label>Température de l\'air extérieur <output id="hd-pu-o">−5 °C</output>'
        '<input type="range" id="hd-pu-t" min="-10" max="35" step="1" value="-5"></label></div>' + svg_puits() +
        '<p class="hd-out" id="hd-pu-txt" aria-live="polite"></p><p class="small">Allure indicative : sol à 13 °C, '
        "l'air garde environ 30 % de son écart avec le sol à la sortie d'un tube de 30 à 50 m.</p></div>")

    s4 = cs(4, "hd-enr", "Utiliser les énergies renouvelables",
        "<h3>4.1 Énergie solaire thermique</h3><div class=\"cours-split\">"
        + img(h, "ch-fig10-solaire-combine", "Système solaire combiné : capteurs solaires thermiques, groupe de "
              "transfert, ballon tampon avec ballon d'eau chaude sanitaire intégré et échangeur, sortie d'eau chaude "
              "sanitaire, chauffage par radiateurs ou plancher chauffant", "Figure 10 — Système solaire combiné", 560) +
        "<div><p>Les installations solaires thermiques utilisent la chaleur du rayonnement solaire pour chauffer un "
        "fluide caloporteur (effet de serre). Ce fluide circule dans un <b>chauffe-eau solaire individuel (CESI)</b> pour "
        "chauffer l'eau chaude sanitaire, ou dans un ballon tampon pour chauffer l'eau du chauffage central.</p></div></div>"
        "<h3>4.2 Énergies de l'air, de l'eau et du sol</h3>"
        "<p>Une <b>pompe à chaleur (PAC)</b> capte les calories présentes dans l'air, le sol ou l'eau et les convertit "
        "pour assurer le chauffage, l'eau chaude sanitaire et le rafraîchissement d'une habitation (aérothermie, "
        "géothermie…).</p><h3>Figure 11 — Principe d'une pompe à chaleur</h3>"
        '<p class="cours-defi">Suis le fluide frigorigène étape par étape, ou lance le cycle.</p>'
        '<div class="hd-fig-i" id="hd-pac"><div class="hd-btns" role="group" aria-label="Étapes du cycle">'
        + "".join(f'<button type="button" class="hd-b hd-pac-b" data-e="{n}" data-c="{c}" data-t="{e(t)}" '
                  f'aria-pressed="false">{n}</button>' for n, c, t in PAC_ETAPES) +
        '<button type="button" class="hd-b ghost" id="hd-pac-go" aria-pressed="false">Lancer le cycle</button></div>'
        + svg_pac() + '<p class="hd-out" id="hd-pac-txt" aria-live="polite">Touche une étape : 1, 2, 3 ou 4.</p></div>'
        "<p>Le <b>coefficient de performance (COP)</b> d'une pompe à chaleur est le rapport entre l'énergie thermique "
        "produite et l'énergie électrique consommée. En bilan annuel, le COP varie entre 2 et 3.</p>"
        + formule("COP = W<sub>thermique produite</sub> / W<sub>électrique consommée</sub>", "") +
        '<div class="simu" id="hd-cop"><h3>Simulateur — Ce que rapporte le COP</h3><div class="simu-grid">'
        '<label>Coefficient de performance COP <output id="hd-cop-o">3</output><input type="range" id="hd-cop-c" min="2" '
        'max="3" step="0.1" value="3"></label>'
        '<label>Besoin de chauffage de la maison <output id="hd-cop-bo">9 000 kWh/an</output><input type="range" '
        'id="hd-cop-b" min="3000" max="20000" step="500" value="9000"></label></div>'
        '<div class="hd-barre" id="hd-cop-bar" aria-hidden="true"><span class="hd-cop-e"></span><span class="hd-cop-g">'
        '</span></div><div class="simu-out" aria-live="polite"><div><span>Électricité consommée</span><b id="hd-cop-e">'
        '</b></div><div><span>Chaleur puisée gratuitement</span><b id="hd-cop-g"></b></div><div><span>Chaleur '
        'produite</span><b id="hd-cop-t"></b></div></div></div>'
        "<h3>4.3 Énergie de l'air</h3><div class=\"cours-split\"><div><p>Le <b>chauffe-eau thermodynamique</b> "
        "fonctionne grâce à une pompe à chaleur intégrée qui récupère les calories contenues dans l'air (air du local "
        "d'implantation, air extérieur, air issu de la VMC…) et assure le chauffage de l'eau chaude sanitaire.</p>"
        + remarque("dans les bâtiments neufs, les exigences de la RE2020 conduisent à privilégier le chauffe-eau "
                   "thermodynamique au chauffe-eau électrique classique.") + "</div>"
        + img(h, "ch-chauffe-eau-thermo", "Chauffe-eau thermodynamique : 1 ventilateur, 2 évaporateur, 3 compresseur, "
              "4 condenseur, 5 détendeur, 6 chauffage d'appoint ; air aspiré, air rejeté", "Le chauffe-eau "
              "thermodynamique : 1 ventilateur, 2 évaporateur, 3 compresseur, 4 condenseur, 5 détendeur, 6 chauffage "
              "d'appoint", 420) + "</div>"
        "<h3>4.4 Énergie bois</h3><p>Le bois, utilisé comme combustible, est une énergie renouvelable (à condition "
        "qu'il soit issu de forêts à gestion durable et que les rejets de poussières et de monoxyde de carbone soient "
        "contrôlés). En brûlant, le bois libère le CO<sub>2</sub> qu'il a emmagasiné durant sa croissance.</p>"
        '<div class="hd-deux"><div>' + img(h, "ch-fig12-bois", "Combustibles issus du bois : bois bûches et "
                                          "plaquettes forestières (industries forestières), granulés de bois et "
                                          "plaquettes de scierie (scieries industrielles)",
                                          "Figure 12 — Origines et transformation du bois-combustible", 560) +
        "</div><div>" + img(h, "ch-fig13-combustibles", "3/4 de stère de bûches donne 1 m³ apparent de plaquettes ; "
                            "500 kg d'écorces équivalent à 220 kg de granulés ; soit 1000 kWh, soit 100 litres de "
                            "fioul", "Figure 13 — Énergie fournie par type de combustible", 560) + "</div></div>"
        '<div class="simu" id="hd-bo"><h3>Simulateur — Le bois d\'une année de chauffage</h3><div class="simu-grid">'
        '<label>Besoin de chauffage <output id="hd-bo-o">10 000 kWh/an</output><input type="range" id="hd-bo-b" '
        'min="2000" max="20000" step="500" value="10000"></label></div>'
        '<div class="hd-tab-w"><table class="t hd-tab" id="hd-bo-out"></table></div>'
        '<p class="small">Équivalences de la figure 13 : 1000 kWh = 3/4 de stère de bûches = 1 m³ apparent de '
        "plaquettes = 500 kg d'écorces = 220 kg de granulés = 100 litres de fioul.</p></div>"
        "<h3>4.5 Utilisation de ces énergies</h3><p>Dans la RE2020, ces énergies renouvelables doivent être utilisées "
        "pour le chauffage et la production d'eau chaude sanitaire (ECS).</p>"
        '<div class="hd-chaine" role="list">'
        '<div role="listitem"><b>Énergie renouvelable</b><span>Bois (granulés)</span><span>Soleil</span><span>Air '
        "(pompe à chaleur)</span></div><i aria-hidden=\"true\">→</i>"
        '<div role="listitem"><b>Générateur de chaleur</b><span>Chaudière</span><span>Ballon tampon</span></div>'
        '<i aria-hidden="true">→</i><div role="listitem"><b>Transport de l\'eau chaude</b><span>Tuyaux rigides en '
        "cuivre</span><span>Tuyaux souples en PER (polyéthylène réticulé)</span></div><i aria-hidden=\"true\">→</i>"
        '<div role="listitem"><b>Émetteurs de chaleur</b><span>Radiateur</span><span>Chauffage au sol</span></div></div>'
        '<p class="hd-cap">Figure 14 — Principe du chauffage central</p>'
        "<p><b>Principe du chauffage central :</b> un générateur de chaleur produit de la chaleur à partir d'une énergie "
        "renouvelable (soleil, bois). Cette chaleur sert à chauffer un liquide caloporteur (eau) que l'on fait circuler "
        "dans des émetteurs de chaleur. Il est possible d'obtenir l'eau chaude sanitaire à l'aide de ces dispositifs.</p>"
        + remarque("les chaudières fioul et gaz sont abandonnées dans la RE2020.") +
        "<h3>À quel maillon de la chaîne appartient chaque élément ?</h3>"
        + h.jeu_html(JEU_CHAUFFAGE, MAILLONS, "jeu-chauffage"))

    eclairages = [("ch-ph-puits-lumiere", "Puits de lumière", "Amener la lumière naturelle dans les zones sombres de "
                   "l'habitat", "Puits de lumière : un tube réfléchissant traverse la toiture"),
                  ("ch-ph-detection-presence", "Détection de présence", "Allumer l'éclairage uniquement lors de la "
                   "présence de personnes", "Détecteur de présence"),
                  ("ch-ph-crepusculaire", "Détection crépusculaire", "Allumer l'éclairage uniquement lorsque la "
                   "luminosité est faible", "Interrupteur crépusculaire modulaire et sa cellule"),
                  ("ch-ph-led", "Tube fluorescent et LED", "Éclairage économique", "Lampe fluocompacte et spot à LED"),
                  ("ch-ph-etiquette", "Étiquette énergétique", "Appareils peu énergivores",
                   "Étiquette énergie, classes de A à G")]
    s5 = cs(5, "hd-conso", "Limiter la consommation énergétique",
        "<h3>5.1 Limiter la consommation des équipements de chauffage</h3>"
        "<p>Pour limiter la consommation énergétique due au chauffage, il est conseillé d'assurer, à l'aide d'une "
        "programmation, une <b>température de confort</b> (en présence des occupants) de l'ordre de 19 °C et une "
        "<b>température réduite</b> (en l'absence des occupants) de l'ordre de 16 °C.</p>"
        "<h3>Figure 15 — Exemple de programmation hebdomadaire</h3>"
        '<p class="cours-defi">Programme ta semaine : touche une heure pour passer du mode éco au mode confort.</p>'
        '<div class="hd-fig-i" id="hd-prog"><div class="hd-btns">'
        '<button type="button" class="hd-b ghost" id="hd-pg-fig">Programme de la figure</button>'
        '<button type="button" class="hd-b ghost" id="hd-pg-tout">Toujours en confort</button>'
        '<button type="button" class="hd-b ghost" id="hd-pg-rien">Toujours en éco</button></div>'
        + grille_prog() +
        '<div class="hd-leg"><span class="hd-leg-eco">mode éco : 16 °C</span><span class="hd-leg-confort">mode '
        "confort : 19 °C</span></div>"
        '<div class="simu-out simu-out4" aria-live="polite"><div><span>Heures en confort</span><b id="hd-pg-c"></b>'
        '</div><div><span>Heures en éco</span><b id="hd-pg-e"></b></div><div><span>Consigne moyenne</span>'
        '<b id="hd-pg-m"></b></div><div><span>Économie de chauffage</span><b id="hd-pg-g"></b></div></div>'
        '<p class="small">Économie estimée par rapport à 19 °C en permanence, avec le repère usuel d\'environ 7 % de '
        "chauffage en moins par degré de moins.</p></div>"
        + img(h, "ch-fig16-programmateur", "Programmateur : capteur de température intérieure, capteur de "
              "température extérieure (pas obligatoire), température ambiante, température de consigne, "
              "programmation ; il envoie des informations de commande (TOR, radio, fil pilote, CPL…) aux émetteurs de "
              "chaleur (chaudière, poêle à bois, convecteurs…)", "Figure 16 — Programmateur de chauffage", 1000) +
        "<h3>5.2 Limiter la consommation des équipements électriques</h3>"
        "<p>Pour limiter la consommation énergétique due à l'éclairage, il faut :</p><ul><li>utiliser des sources "
        "d'éclairage ayant une faible consommation énergétique (LED…) ;</li><li>favoriser l'éclairage naturel et "
        "n'utiliser les sources d'éclairage que si elles sont indispensables.</li></ul>"
        '<div class="hd-ecl">' + "".join(
            f'<div class="hd-ecl-c">{img(h, n, alt, "", 150, "hd-ecl-f")}<b>{t}</b><span>{p}</span></div>'
            for n, t, p, alt in eclairages) + "</div>"
        "<h3>Quelle solution pour chaque situation ?</h3>" + h.jeu_html(JEU_ECLAIRAGE, ECLAIRAGES, "jeu-eclairage") +
        "<h3>5.3 La domotique : gestion intelligente de la maison</h3><div class=\"cours-split\">"
        + img(h, "ch-fig17-domotique", "Fonctions de la domotique : contrôle de l'énergie, confort de vie, protection "
              "du domicile, protection de la personne, interaction à distance", "Figure 17 — Fonctions de la "
              "domotique", 560) +
        "<div><p>La <b>domotique</b> permet de faire communiquer par bus (filaire) ou par radio tous les éléments de "
        "l'habitat afin d'assurer un meilleur confort aux habitants avec une gestion optimale de l'installation et de "
        "l'énergie.</p><p>Principales technologies utilisées :</p><ul><li>en filaire : bus KNX, Ethernet domestique, "
        "Legrand MyHome… ;</li><li>sans fil : Z-Wave, Zigbee, infrarouge, Wi-Fi…</li></ul><p>Pour communiquer avec "
        "l'extérieur (avec un smartphone par exemple), la box domotique est raccordée à la box Internet.</p></div></div>"
        "<h3>Filaire ou sans fil ?</h3>" + h.jeu_html(JEU_LIAISONS, LIAISONS, "jeu-liaisons"))

    s6 = cs(6, "hd-prod", "Produire de l'énergie renouvelable",
        "<p>Une maison à énergie positive (<b>Bepos</b>) produit plus d'énergie qu'elle n'en consomme. Les énergies "
        "renouvelables les plus souvent utilisées pour une maison sont le soleil et le vent.</p>"
        "<h3>6.1 Énergie solaire photovoltaïque</h3><p><b>Principe de l'énergie solaire photovoltaïque :</b> transformer "
        "le rayonnement solaire en électricité à l'aide d'une cellule photovoltaïque.</p>"
        + img(h, "ch-fig18-photovoltaique", "Le rayonnement solaire arrive sur un module photovoltaïque, qui produit "
              "de l'électricité pour une lampe", "Figure 18 — Principe de la conversion photovoltaïque", 620) +
        "<p>Il existe deux types d'installations photovoltaïques : l'installation sur site isolé et l'installation "
        "couplée au réseau.</p><h3>Installation sur site isolé</h3><p>Ce type de montage est adapté aux installations "
        "ne pouvant pas être raccordées au réseau. L'énergie produite doit être directement consommée et/ou stockée "
        "dans des accumulateurs pour permettre de répondre à la totalité des besoins.</p><div class=\"cours-split\">"
        + img(h, "ch-fig19-site-isole", "Site isolé : modules PV, régulateur de charge, accumulateur, onduleur ; "
              "récepteur DC (lampe) et récepteur AC (réfrigérateur)", "Figure 19 — Installation photovoltaïque sur site "
              "isolé", 620) +
        "<div><ul><li>Les <b>panneaux photovoltaïques</b> produisent un courant électrique continu.</li><li>Le "
        "<b>régulateur</b> optimise la charge et la décharge de la batterie suivant sa capacité et assure sa "
        "protection.</li><li>Les <b>accumulateurs</b> (batteries) sont chargés de jour pour pouvoir alimenter la nuit ou "
        "les jours de mauvais temps.</li><li>L'<b>onduleur</b> transforme le courant continu en alternatif pour "
        "alimenter les récepteurs AC.</li><li>Des <b>récepteurs DC</b> spécifiques sont utilisables.</li></ul>"
        + remarque("ces appareils sont particulièrement économes.") + "</div></div>"
        "<h3>Installations couplées directement au réseau</h3><p>Toute l'énergie électrique produite par les capteurs "
        "photovoltaïques est envoyée pour être revendue sur le réseau de distribution. L'installation dispose d'un point "
        "de branchement au réseau. L'énergie injectée au réseau est comptabilisée par un compteur de production.</p>"
        + img(h, "ch-fig20-reseau", "Installation couplée au réseau : modules PV, onduleur, compteurs de production et "
              "de non-consommation, compteur de consommation, réseau ; courant continu en rouge, alternatif en vert",
              "Figure 20 — Installation photovoltaïque couplée au réseau", 1000) +
        "<p>Les <b>modules solaires</b> ou <b>panneaux photovoltaïques</b> sont constitués de cellules solaires "
        "associées en série.</p>"
        + img(h, "ch-fig21-cellules", "Module photovoltaïque : trois rangées de cellules reliées en série, entre une "
              "borne moins et une borne plus", "Figure 21 — Cellules associées en série dans un module", 520) +
        "<div class=\"cours-split\"><div><p>Une <b>cellule</b> est un dispositif semi-conducteur à base de silicium qui "
        "produit un courant électrique continu.</p><p>La <b>mise en série</b> des cellules permet d'obtenir une tension "
        "égale au nombre de cellules multiplié par 0,5 V.</p><p>Un <b>champ photovoltaïque</b> est :</p><ul><li>une "
        "association de panneaux en série (chaîne de modules ou <i>string</i>) ;</li><li>une <b>mise en parallèle</b> de "
        "chaque <i>string</i>, ce qui permet d'augmenter le courant fourni.</li></ul></div>"
        + img(h, "ch-cellule", "Cellule photovoltaïque éclairée par le soleil : elle fournit un courant continu sous "
              "une tension d'environ 0,5 V", "Une cellule : U ≈ 0,5 V", 400) + "</div>"
        "<p>On définit la puissance d'une installation photovoltaïque à l'aide de l'unité <b>watt crête (Wc)</b> : c'est "
        "la puissance maximale délivrée par un module dans des conditions optimales. En première approximation, on "
        "estime qu'un module de 1 m² produit 100 Wc.</p><p>L'<b>onduleur</b> permet de convertir le courant continu "
        "produit par les panneaux photovoltaïques en courant alternatif identique à celui du réseau électrique.</p>"
        '<div class="simu" id="hd-pv"><h3>Simulateur — Construis ton champ photovoltaïque</h3><div class="simu-grid">'
        '<label>Cellules en série par module <select id="hd-pv-c"><option value="36">36</option><option value="60" '
        'selected>60</option><option value="72">72</option></select></label>'
        '<label>Puissance d\'un module de 1 m² <select id="hd-pv-w"><option value="100" selected>100 Wc (valeur du '
        'cours)</option><option value="200">200 Wc (module récent)</option></select></label>'
        '<label>Modules en série par chaîne <output id="hd-pv-no">4</output><input type="range" id="hd-pv-n" min="1" '
        'max="10" step="1" value="4"></label>'
        '<label>Chaînes en parallèle <output id="hd-pv-po">2</output><input type="range" id="hd-pv-p" min="1" max="4" '
        'step="1" value="2"></label></div>'
        '<svg class="hd-svg" id="hd-pv-svg" viewBox="0 0 720 300" role="img" aria-label="Le champ photovoltaïque : '
        'modules en série dans chaque chaîne, chaînes en parallèle vers l\'onduleur"></svg>'
        '<div class="simu-out simu-out4" aria-live="polite"><div><span>Tension d\'un module</span><b id="hd-pv-um"></b>'
        '</div><div><span>Tension du champ</span><b id="hd-pv-u"></b></div><div><span>Courant du champ</span>'
        '<b id="hd-pv-i"></b></div><div><span>Puissance crête</span><b id="hd-pv-pw"></b></div></div>'
        '<p class="small">Courant d\'un module estimé par I = P / U, à la puissance maximale.</p></div>'
        "<h3>6.2 Énergie éolienne</h3><p>Le <b>petit éolien</b> désigne les éoliennes à usage domestique d'une puissance "
        "nominale inférieure ou égale à 36 kilowatts. Elles peuvent être raccordées au réseau électrique ou être "
        "utilisées en site isolé.</p>"
        + img(h, "ch-fig22-eolien", "Le vent fait tourner une éolienne, qui produit de l'énergie électrique",
              "Figure 22 — Principe de la conversion éolienne", 900) +
        "<p>Le principe de raccordement d'une éolienne est identique à celui du solaire photovoltaïque : l'éolienne "
        "remplace le panneau solaire dans les schémas. Deux types d'éoliennes existent.</p>"
        "<h3>Axe horizontal</h3><p>Les éoliennes classiques, horizontales, comportent de 3 à 6 pales en hélice. Elles "
        "sont globalement plus performantes que les verticales, mais elles doivent se trouver face à des vents réguliers "
        "et sur un site subissant peu de turbulences. Dans un environnement boisé, sur un terrain accidenté, parsemé "
        "d'obstacles (bâtiments, végétation…), la vitesse du vent peut vite chuter à mesure que l'on s'approche du sol. "
        "Pour pallier cet inconvénient, le mât doit avoir au moins 20 mètres de haut. Or, à partir de 12 mètres de "
        "hauteur, un permis de construire est exigé. Afin de s'éviter une démarche contraignante, nombre d'utilisateurs "
        "optent délibérément pour un mât trop court, obérant ainsi leurs chances de rentabiliser l'investissement.</p>"
        "<h3>Axe vertical</h3><p>Les éoliennes verticales souffrent d'un déficit de productivité à puissance égale. En "
        "revanche, elles peuvent fonctionner par vents faibles à forts, quelle que soit leur direction. En outre, elles "
        "bénéficient d'un design plus recherché et sont dans l'ensemble moins bruyantes à l'usage.</p>"
        '<div class="hd-tab-w"><table class="t hd-tab"><thead><tr><th></th><th>Axe horizontal</th><th>Axe vertical</th>'
        "</tr></thead><tbody><tr><th>Production</th><td>Plus performante</td><td>Déficit de productivité à puissance "
        "égale</td></tr><tr><th>Vent</th><td>Réguliers, peu de turbulences</td><td>Faibles à forts, quelle que soit leur "
        "direction</td></tr><tr><th>Installation</th><td>Mât d'au moins 20 m (permis de construire au-delà de 12 m)</td>"
        "<td>—</td></tr><tr><th>Usage</th><td>—</td><td>Design plus recherché, moins bruyante</td></tr></tbody></table>"
        '</div><p class="hd-cap">Les deux types d\'éoliennes comparés (d\'après le texte)</p>')

    s7 = cs(7, "hd-syn", "Synthèse : range chaque solution",
        "<p>Pour chaque solution technique, choisis la partie du cours à laquelle elle se rattache.</p>"
        + h.jeu_html(JEU_SYNTHESE, FAMILLES, "jeu-synthese"))
    s8 = h.quiz_section(8, "hd-quiz", QUIZ, "qh_")
    return f"""<div class="cours" id="cours-habitat">
{h.course_head("Cours 1", "Niveau 1", "Habitat durable : concevoir et équiper une maison performante",
               "Les exigences de la RE2020 : architecture bioclimatique, isolation et étanchéité, renouvellement de "
               "l'air, chaleur et électricité d'origine renouvelable, maîtrise des consommations. Environ 3 h, avec une "
               "maison qui vit au fil des saisons, des simulateurs, cinq jeux et un quiz.")}
{fiche}
{h.course_nav([("hd-bio", "Bioclimatique"), ("hd-dep", "Déperditions"), ("hd-air", "Air intérieur"),
               ("hd-enr", "Énergies renouvelables"), ("hd-conso", "Consommation"), ("hd-prod", "Production"),
               ("hd-syn", "Synthèse"), ("hd-quiz", "Quiz")])}
{s1}{s2}{s3}{s4}{s5}{s6}{s7}{s8}
<div class="cours-foot no-print"><a class="btn" href="?ex=qcm-re2020">Réviser : QCM La maison RE2020</a>
<a class="btn ghost" href="?ex=isoler-paroi">S'entraîner : isoler une paroi</a>
<button type="button" class="btn ghost cours-print">Imprimer le cours</button>
<a class="btn ghost" href="?">{h.HOUSE} Retour à l'accueil</a></div>
</div>"""


# ------------------------------------------------------------ comportement (inséré dans l'aiguillage, comme les autres cours)
HD_JS = r"""
  function initCoursHabitat(home) {
    var NS = "http://www.w3.org/2000/svg";
    var calme = !!(window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches);
    function q(s, r) { return (r || home).querySelector(s); }
    function qa(s, r) { return Array.prototype.slice.call((r || home).querySelectorAll(s)); }
    function mk(tag, at, parent) { var el = document.createElementNS(NS, tag); for (var k in at) el.setAttribute(k, at[k]); if (parent) parent.appendChild(el); return el; }
    function tx(parent, x, y, s, cls, anchor) { var t = mk("text", { x: x, y: y, "class": "hd-t " + (cls || ""), "text-anchor": anchor || "start" }, parent); t.textContent = s; return t; }
    function vider(el) { while (el.firstChild) el.removeChild(el.firstChild); }
    function presser(bs, b) { bs.forEach(function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); }); }
    function nb(x, d) { return fr(x, d); }
    function pts(a) { return a.map(function (p) { return p[0].toFixed(1) + "," + p[1].toFixed(1); }).join(" "); }

    initQuiz(home);
    qa(".jeu").forEach(initJeu);
    q(".cours-print").addEventListener("click", function () { window.print(); });

    // ---------- flux animés : des points glissent le long d'un trajet (ventilation, pompe à chaleur) ----------
    var flots = [];
    function flot(parent, chemin, cls, marque, pas, vit, coul) {
      var at = { d: "M" + chemin.map(function (p) { return p[0] + "," + p[1]; }).join(" L"), "class": "hd-fl-p " + cls };
      if (marque) at["marker-end"] = "url(#" + marque + ")";
      mk("path", at, parent);
      var cum = [0];
      for (var i = 1; i < chemin.length; i++) cum.push(cum[i - 1] + Math.hypot(chemin[i][0] - chemin[i - 1][0], chemin[i][1] - chemin[i - 1][1]));
      var L = cum[cum.length - 1], n = Math.max(1, Math.round(L / (pas || 46))), dots = [];
      for (var k = 0; k < n; k++) dots.push(mk("circle", { r: 4.3, "class": "hd-fl-d " + cls }, parent));
      var f = { pts: chemin, cum: cum, L: L, dots: dots, vit: vit || 40, g: parent, cls: cls, coul: coul };
      flots.push(f);
      placer(f, 0);
      return f;
    }
    function point(f, s) {
      var c = f.cum, i = 1;
      while (i < c.length - 1 && c[i] < s) i++;
      var a = f.pts[i - 1], b = f.pts[i], u = (s - c[i - 1]) / ((c[i] - c[i - 1]) || 1);
      return [a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u];
    }
    function placer(f, t) {
      var n = f.dots.length;
      f.dots.forEach(function (d, k) {
        var p = point(f, (t * f.vit + k * f.L / n) % f.L);
        d.setAttribute("cx", p[0].toFixed(1)); d.setAttribute("cy", p[1].toFixed(1));
        if (f.coul) d.setAttribute("class", "hd-fl-d " + f.coul(p));
      });
    }
    var t0 = null;
    function boucle(ts) {
      if (t0 === null) t0 = ts;
      var t = (ts - t0) / 1000;
      flots.forEach(function (f) { if (f.g.getClientRects().length) placer(f, t); });
      requestAnimationFrame(boucle);
    }

    // ---------- 1. maison bioclimatique : le soleil d'hiver entre, celui d'été est arrêté ----------
    (function () {
      var svg = q("#hd-bio-svg");
      if (!svg) return;
      var X0 = 613, YT = 214, YB = 300, SOL = 306, XN = 344, OX = 690, OY = 199, rad = Math.PI / 180;
      var beam = q("#hd-bio-beam"), sun = q("#hd-bio-sun"), rays = q("#hd-bio-rays"), ang = q("#hd-bio-ang"), out = q("#hd-bio-txt");
      var bs = qa(".hd-bio-s"), notes = qa(".hd-bio-n");
      var S = { hiver: [21, "Hiver"], mi: [44, "Mi-saison"], ete: [67, "Été"] };
      function maj(cle) {
        var a = S[cle][0], t = Math.tan(a * rad), c = Math.cos(a * rad), s = Math.sin(a * rad);
        var yLit = Math.max(YT, OY + (OX - X0) * t), p = [];
        if (yLit < YB) {
          p.push([X0, yLit]);
          var xFar = X0 - (SOL - yLit) / t;
          if (xFar < XN) { p.push([XN, yLit + (X0 - XN) * t]); p.push([XN, SOL]); } else p.push([xFar, SOL]);
          p.push([X0 - (SOL - YB) / t, SOL]); p.push([X0, YB]);
        }
        beam.setAttribute("points", pts(p));
        var sx = X0 + 250 * c, sy = 257 - 250 * s;
        sun.setAttribute("transform", "translate(" + sx.toFixed(1) + " " + sy.toFixed(1) + ")");
        vider(rays);
        var cibles = [[OX, OY], [OX + 70, 320]];
        if (yLit < YB) { cibles.push([X0 + 7, (yLit + YB) / 2]); cibles.push([X0 + 7, YB - 3]); }
        cibles.forEach(function (pt) {
          var L = (sx - pt[0]) * c - (sy - pt[1]) * s - 26;
          mk("line", { x1: (pt[0] + L * c).toFixed(1), y1: (pt[1] - L * s).toFixed(1), x2: pt[0], y2: pt[1], "class": "hd-bio-ray" }, rays);
        });
        ang.textContent = "Soleil à midi : " + a + "° au-dessus de l'horizon";
        var part = yLit >= YB ? 0 : (YB - yLit) / (YB - YT);
        out.innerHTML = "<b>" + S[cle][1] + ".</b> " + (part > 0.75 ?
          "Le soleil est bas : il entre profondément dans le séjour, jusqu'au fond de la pièce. Ces apports solaires gratuits chauffent la maison." :
          part > 0 ? "Le soleil entre en partie : l'avancée du toit ombrage déjà le haut du vitrage." :
          "Le soleil est haut : l'avancée du toit (brise-soleil) ombrage tout le vitrage. Pas de surchauffe dans le séjour.");
      }
      bs.forEach(function (b) { b.addEventListener("click", function () { presser(bs, b); maj(b.dataset.s); }); });
      notes.forEach(function (n) {
        n.addEventListener("click", function () {
          var deja = n.getAttribute("aria-pressed") === "true";
          presser(notes, deja ? null : n);
          qa(".hd-bio-g", svg).forEach(function (g) { g.classList.toggle("on", !deja && g.id === "hd-bio-g" + n.dataset.g); });
        });
      });
      maj("hiver");
    })();

    // ---------- 2. déperditions : chaque flèche s'explique ----------
    (function () {
      var arr = qa(".hd-dep-a"), out = q("#hd-dep-txt");
      function choisir(g) {
        arr.forEach(function (a) { a.classList.toggle("sel", a === g); a.setAttribute("aria-pressed", a === g ? "true" : "false"); });
        qa(".hd-dep-p").forEach(function (p) { p.classList.toggle("on", p.id === "hd-dep-p-" + g.dataset.k); });
        out.innerHTML = "<b>" + g.dataset.t + ".</b> " + g.dataset.info;
      }
      arr.forEach(function (a) {
        a.addEventListener("click", function () { choisir(a); });
        a.addEventListener("keydown", function (ev) { if (ev.key === "Enter" || ev.key === " ") { ev.preventDefault(); choisir(a); } });
      });
    })();

    // ---------- 2.1 compacité : plain-pied ou étage, pour la même surface ----------
    (function () {
      var S = q("#hd-comp-s"), R = q("#hd-comp-r"), svg = q("#hd-comp-svg"), tab = q("#hd-comp-out"), v = q("#hd-comp-v");
      if (!S) return;
      var c30 = Math.cos(Math.PI / 6);
      function maison(n, s, r) {
        var A = s / n, l = Math.sqrt(A / r), L = r * l, H = 2.5 * n, V = L * l * H, Sp = 2 * (L + l) * H + 2 * L * l;
        return { n: n, L: L, l: l, H: H, V: V, Sp: Sp, C: Sp / V };
      }
      function dessiner(m, cx, k, titre) {
        var oy = 196 - (m.L + m.l) * 0.5 * k, ox = cx - (m.L - m.l) / 2 * c30 * k;
        function P(x, y, z) { return [ox + (x - y) * c30 * k, oy + (x + y) * 0.5 * k - z * k]; }
        var L = m.L, l = m.l, H = m.H;
        mk("polygon", { points: pts([P(0, l, 0), P(L, l, 0), P(L, l, H), P(0, l, H)]), "class": "hd-comp-f1" }, svg);
        mk("polygon", { points: pts([P(L, 0, 0), P(L, l, 0), P(L, l, H), P(L, 0, H)]), "class": "hd-comp-f2" }, svg);
        mk("polygon", { points: pts([P(0, 0, H), P(L, 0, H), P(L, l, H), P(0, l, H)]), "class": "hd-comp-f3" }, svg);
        if (m.n === 2) mk("polyline", { points: pts([P(0, l, 2.5), P(L, l, 2.5), P(L, 0, 2.5)]), "class": "hd-comp-niv" }, svg);
        tx(svg, cx, 222, titre, "hd-t-b", "middle");
        tx(svg, cx, 242, "C = " + nb(m.C, 2) + " m²/m³", "hd-t-b hd-comp-c", "middle");
      }
      function maj() {
        var s = +S.value, r = +R.value;
        q("#hd-comp-so").textContent = s + " m²";
        q("#hd-comp-ro").textContent = nb(r, 1);
        var a = maison(1, s, r), b = maison(2, s, r);
        var k = Math.min(270 / ((a.L + a.l) * c30), 270 / ((b.L + b.l) * c30), 175 / ((a.L + a.l) / 2 + a.H), 175 / ((b.L + b.l) / 2 + b.H));
        vider(svg);
        dessiner(a, 165, k, "Plain-pied"); dessiner(b, 480, k, "À étage");
        tab.innerHTML = "<thead><tr><th></th><th>Plain-pied</th><th>À étage</th></tr></thead><tbody>" + [
          ["Emprise au sol L × l", function (m) { return nb(m.L, 1) + " m × " + nb(m.l, 1) + " m"; }],
          ["Hauteur", function (m) { return nb(m.H, 1) + " m"; }],
          ["Parois déperditives S<sub>p</sub>", function (m) { return nb(m.Sp, 0) + " m²"; }],
          ["Volume chauffé V", function (m) { return nb(m.V, 0) + " m³"; }],
          ["Facteur de compacité C = S<sub>p</sub> / V", function (m) { return "<b>" + nb(m.C, 2) + " m²/m³</b>"; }]
        ].map(function (row) { return "<tr><th>" + row[0] + "</th><td>" + row[1](a) + "</td><td>" + row[1](b) + "</td></tr>"; }).join("") + "</tbody>";
        var m1 = b.C < a.C ? b : a, m2 = m1 === a ? b : a;
        v.textContent = (m1 === b ? "À étage" : "De plain-pied") + ", C = " + nb(m1.C, 2) + " m²/m³ contre " + nb(m2.C, 2) +
          " : pour le même volume chauffé, " + nb(m2.Sp - m1.Sp, 0) + " m² de parois déperditives en moins. La maison " +
          (m1 === b ? "à étage" : "de plain-pied") + " est la plus compacte.";
      }
      S.addEventListener("input", maj); R.addEventListener("input", maj);
      maj();
    })();

    // ---------- 2.2 épaisseur de chaque matériau pour une même résistance thermique ----------
    (function () {
      var R = q("#hd-lam-r"), svg = q("#hd-lam-svg");
      if (!R) return;
      var M = [["Parpaing", 0.95, 0.95, "0,95"], ["Ossature bois", 0.12, 0.12, "0,12"], ["Brique Monomur", 0.13, 0.13, "0,13"],
               ["Terre crue", 0.6, 1, "0,6 à 1"], ["Laine de verre (isolant)", 0.035, 0.035, "≈ 0,035", "≈"]];
      function lg(m) { return m >= 1 ? nb(m, 2) + " m" : nb(m * 100, m < 0.1 ? 1 : 0) + " cm"; }
      function maj() {
        var r = +R.value, k = 270 / r;
        q("#hd-lam-ro").textContent = nb(r, 1) + " m²·K/W";
        vider(svg);
        M.forEach(function (m, i) {
          var y = 10 + i * 44, e1 = r * m[1], e2 = r * m[2];
          tx(svg, 200, y + 18, m[0], "hd-t-b", "end");
          tx(svg, 200, y + 34, "λ " + (m[4] ? "≈ 0,035" : "= " + m[3]) + " W/(m·K)", "hd-t-s", "end");
          mk("rect", { x: 212, y: y + 8, width: Math.max(2, e1 * k).toFixed(1), height: 24, "class": i === 4 ? "hd-lam-iso" : "hd-lam-b" }, svg);
          if (e2 > e1) mk("rect", { x: (212 + e1 * k).toFixed(1), y: y + 8, width: ((e2 - e1) * k).toFixed(1), height: 24, "class": "hd-lam-plage" }, svg);
          tx(svg, 220 + e2 * k, y + 25, "e = " + lg(e1) + (e2 > e1 ? " à " + lg(e2) : ""), "hd-t-b");
        });
      }
      R.addEventListener("input", maj);
      maj();
    })();

    // ---------- pont thermique : isolation intérieure ou extérieure ----------
    (function () {
      var svg = q("#hd-pt-svg"), out = q("#hd-pt-txt"), bs = qa(".hd-pt-b");
      if (!svg) return;
      var T = {
        iti: "Isolation intérieure : le plancher traverse l'isolant et touche directement le mur. Par sa tranche, la chaleur s'échappe vers l'extérieur : c'est un pont thermique.",
        ite: "Isolation extérieure : l'isolant enveloppe le mur et la tranche du plancher sans interruption. Plus de pont thermique : seules de faibles pertes traversent la paroi isolée." };
      function choisir(b) {
        presser(bs, b);
        svg.classList.toggle("iti", b.dataset.m === "iti"); svg.classList.toggle("ite", b.dataset.m === "ite");
        out.textContent = T[b.dataset.m];
      }
      bs.forEach(function (b) { b.addEventListener("click", function () { choisir(b); }); });
      choisir(bs[0]);
    })();

    // ---------- 2.3 paroi multicouche : R, U, D et température dans l'épaisseur ----------
    (function () {
      var lst = q("#hd-pa-l"), svg = q("#hd-pa-svg");
      if (!lst) return;
      var MAT = [["plat", "Plaque de plâtre", 0.25, "#F1EEE4"], ["lv", "Laine de verre", 0.035, "#F6E27A"],
                 ["lb", "Laine de bois", 0.038, "#D9B77E"], ["pse", "Polystyrène expansé", 0.032, "#E4EAF4"],
                 ["parp", "Parpaing", 0.95, "#B9BDC2"], ["mono", "Brique Monomur", 0.13, "#D88A5B"],
                 ["bois", "Ossature bois", 0.12, "#C8945A"], ["terre", "Terre crue", 0.8, "#B98B5E"], ["end", "Enduit", 1.0, "#E3DCCB"]];
      var MATS = {};
      MAT.forEach(function (m) { MATS[m[0]] = m; });
      var DEF = [["plat", 1.3], ["lv", 10], ["parp", 20], ["end", 1.5]];
      function lam(x) { return nb(x, x < 0.1 ? 3 : 2); }
      lst.innerHTML = DEF.map(function (d, i) {
        return '<div class="hd-pa-r"><span class="hd-pa-n">Couche ' + (i + 1) + (i === 0 ? " (intérieur)" : i === 3 ? " (extérieur)" : "") + "</span>" +
          '<select class="hd-pa-m" aria-label="Matériau de la couche ' + (i + 1) + '"><option value="">— aucune —</option>' +
          MAT.map(function (m) { return '<option value="' + m[0] + '"' + (m[0] === d[0] ? " selected" : "") + ">" + m[1] + " (λ = " + lam(m[2]) + ")</option>"; }).join("") +
          '</select><label class="hd-pa-e">e = <input type="number" min="0" max="60" step="0.5" value="' + d[1] + '" aria-label="Épaisseur de la couche ' + (i + 1) +
          ' en cm"> cm</label><span class="hd-pa-ri"></span></div>';
      }).join("");
      function maj() {
        var S = +q("#hd-pa-s").value, Te = +q("#hd-pa-t").value, couches = [];
        q("#hd-pa-so").textContent = S + " m²";
        q("#hd-pa-to").textContent = nb(Te, 0) + " °C";
        qa(".hd-pa-r", lst).forEach(function (row, i) {
          var m = MATS[q(".hd-pa-m", row).value], ev = parseFloat(String(q("input", row).value).replace(",", ".")), ri = q(".hd-pa-ri", row);
          if (!m || !(ev > 0)) { ri.textContent = ""; return; }
          var e = Math.min(ev, 60), R = e / 100 / m[2];
          couches.push({ i: i + 1, m: m, e: e, R: R });
          ri.innerHTML = "R<sub>" + (i + 1) + "</sub> = " + nb(e / 100, e < 10 ? 3 : 2) + " / " + lam(m[2]) + " = <b>" + nb(R, 2) + "</b> m²·K/W";
        });
        var Rt = couches.reduce(function (s, c) { return s + c.R; }, 0);
        vider(svg);
        if (!Rt) {
          ["#hd-pa-rt", "#hd-pa-u", "#hd-pa-d", "#hd-pa-p"].forEach(function (s) { q(s).textContent = "—"; });
          tx(svg, 320, 130, "Choisis au moins une couche.", "hd-t-b", "middle");
          return;
        }
        var U = 1 / Rt, D = U * S, P = Math.max(0, D * (19 - Te));
        q("#hd-pa-rt").textContent = nb(Rt, 2) + " m²·K/W";
        q("#hd-pa-u").textContent = nb(U, 2) + " W/(m²·K)";
        q("#hd-pa-d").textContent = nb(D, 1) + " W/K";
        q("#hd-pa-p").textContent = nb(P, 0) + " W";
        var tot = couches.reduce(function (s, c) { return s + c.e; }, 0), k = Math.min(7, 380 / tot), x = 130, xe = 130 + tot * k;
        function yT(T) { return 205 - (T - Te) / (19 - Te) * 150; }
        mk("rect", { x: 0, y: 34, width: 130, height: 186, "class": "hd-pa-int" }, svg);
        mk("rect", { x: xe, y: 34, width: 640 - xe, height: 186, "class": "hd-pa-ext" }, svg);
        tx(svg, 6, 24, "Intérieur : 19 °C", "hd-t-b"); tx(svg, 634, 24, "Extérieur : " + nb(Te, 0) + " °C", "hd-t-b", "end");
        var p = [[0, yT(19)], [x, yT(19)]], T = 19;
        couches.forEach(function (c) {
          var w = c.e * k;
          mk("rect", { x: x.toFixed(1), y: 34, width: w.toFixed(1), height: 186, fill: c.m[3], "class": "hd-pa-c" }, svg);
          tx(svg, x + w / 2, 238, w >= 24 ? "R" + c.i : String(c.i), w >= 24 ? "hd-t-b" : "hd-t-s", "middle");
          T -= c.R / Rt * (19 - Te);
          x += w;
          p.push([x, yT(T)]);
        });
        p.push([640, yT(Te)]);
        mk("polyline", { points: pts(p), "class": "hd-pa-temp" }, svg);
        var etiq = [];  // une étiquette par interface, sauf si elle chevauche la précédente (la dernière l'emporte)
        p.slice(1, -1).forEach(function (pt, i) {
          var Ti = 19 - (19 - Te) * couches.slice(0, i).reduce(function (s, c) { return s + c.R; }, 0) / Rt;
          mk("circle", { cx: pt[0].toFixed(1), cy: pt[1].toFixed(1), r: 3.5, "class": "hd-pa-pt" }, svg);
          if (etiq.length && pt[0] - etiq[etiq.length - 1][0] < 52) { if (i === p.length - 3 || i === 1) etiq.pop(); else return; }
          etiq.push([pt[0], pt[1], Ti]);
        });
        etiq.forEach(function (l) { tx(svg, l[0] + 5, l[1] - 8, nb(l[2], 1) + " °C", "hd-t-s hd-pa-tl"); });
      }
      lst.addEventListener("input", maj); lst.addEventListener("change", maj);
      q("#hd-pa-s").addEventListener("input", maj); q("#hd-pa-t").addEventListener("input", maj);
      maj();
    })();

    // ---------- 2.4 vitrages (figures 5 et 6) ----------
    (function () {
      var svg = q("#hd-vi-svg"), bs = qa(".hd-vi-b"), Si = q("#hd-vi-s");
      if (!svg) return;
      var V = { simple: { n: 1, gaz: false, vir: false, t: 6, uw: 5, sw: 0.85, re: false },
                double: { n: 2, gaz: false, vir: false, t: 13, uw: 3, sw: null, re: false },
                vir: { n: 2, gaz: true, vir: true, t: 17, uw: 1.5, sw: 0.7, re: true },
                triple: { n: 3, gaz: true, vir: false, t: 20, uw: 0.7, sw: 0.65, re: true } };
      var cur = "vir";
      function maj() {
        var v = V[cur], s = Math.max(0, parseFloat(String(Si.value).replace(",", ".")) || 0);
        vider(svg);
        mk("rect", { x: 0, y: 0, width: 150, height: 240, "class": "hd-vi-ext" }, svg);
        mk("rect", { x: 150, y: 0, width: 270, height: 240, "class": "hd-vi-int" }, svg);
        tx(svg, 10, 22, "Extérieur", "hd-t-b"); tx(svg, 250, 22, "Intérieur", "hd-t-b");
        var w = 9, g = 22, larg = v.n * w + (v.n - 1) * g, x0 = 150 - larg / 2;
        for (var i = 0; i < v.n; i++) {
          if (i > 0) mk("rect", { x: x0 + i * (w + g) - g, y: 40, width: g, height: 170, "class": v.gaz ? "hd-vi-argon" : "hd-vi-air" }, svg);
          mk("rect", { x: x0 + i * (w + g), y: 40, width: w, height: 170, "class": "hd-vi-verre" }, svg);
        }
        if (v.vir) mk("line", { x1: x0 + w + g - 2, y1: 40, x2: x0 + w + g - 2, y2: 210, "class": "hd-vi-couche" }, svg);
        if (v.gaz) tx(svg, 150, 230, "lame d'argon", "hd-t-s", "middle");
        // thermomètre de la face intérieure
        var h = v.t / 25 * 150, col = v.t < 10 ? "#2C6FB0" : v.t < 16 ? "#7FA3CF" : "#D97A00";
        mk("rect", { x: 330, y: 40, width: 18, height: 160, rx: 9, "class": "hd-vi-tube" }, svg);
        mk("rect", { x: 334, y: (196 - h).toFixed(1), width: 10, height: (h + 6).toFixed(1), fill: col }, svg);
        mk("circle", { cx: 339, cy: 208, r: 15, fill: col }, svg);
        tx(svg, 339, 236, v.t + " °C", "hd-t-b", "middle");
        mk("line", { x1: 150 + larg / 2 + 2, y1: 125, x2: 318, y2: 125, "class": "hd-vi-lien" }, svg);
        tx(svg, 236, 118, "face intérieure", "hd-t-s", "middle");
        q("#hd-vi-t").textContent = v.t + " °C";
        q("#hd-vi-uw").textContent = nb(v.uw, 1) + " W/(m²·K)";
        q("#hd-vi-sw").textContent = v.sw === null ? "non chiffré" : nb(v.sw, 2);
        q("#hd-vi-txt").innerHTML = (v.t <= 10 ? "Paroi froide : on ressent du froid près de la fenêtre, la vapeur d'eau risque de s'y condenser. " :
          v.t < 17 ? "Paroi tiède : un peu d'inconfort près de la fenêtre. " : "Face intérieure presque à la température de la pièce : confortable. ") +
          (v.re ? "<b>Dans le cadre « RE2020 » de la figure 6.</b>" : "<b>Hors du cadre « RE2020 » de la figure 6</b> : trop de pertes.");
        var D = v.uw * s;
        q("#hd-vi-d").innerHTML = "D = U<sub>w</sub> × S = " + nb(v.uw, 1) + " × " + nb(s, 1) + " = <b>" + nb(D, 1) + " W/K</b> : pour 20 °C d'écart entre dedans et dehors, la fenêtre perd " + nb(D * 20, 0) + " W.";
      }
      bs.forEach(function (b) { b.addEventListener("click", function () { presser(bs, b); cur = b.dataset.v; maj(); }); });
      Si.addEventListener("input", maj);
      maj();
    })();

    // ---------- 2.4 surface vitrée et répartition par orientation ----------
    (function () {
      var R = q("#hd-sv-s"), svg = q("#hd-sv-svg"), tab = q("#hd-sv-out");
      if (!R) return;
      var O = [["Sud", 0.5, 0.5], ["Est", 0.2, 0.3], ["Ouest", 0.2, 0.2], ["Nord", 0, 0.1]];
      function plage(a, b) { return a === b ? nb(a, 1) + " m²" : nb(a, 1) + " à " + nb(b, 1) + " m²"; }
      function maj() {
        var s = +R.value, a = 0.16 * s, b = 0.18 * s;
        q("#hd-sv-o").textContent = s + " m²";
        tab.innerHTML = "<thead><tr><th>Orientation</th><th>Part</th><th>Surface vitrée</th></tr></thead><tbody>" +
          O.map(function (o) {
            return "<tr><th>" + o[0] + "</th><td>" + (o[1] === o[2] ? Math.round(o[1] * 100) + " %" : Math.round(o[1] * 100) + " à " + Math.round(o[2] * 100) + " %") +
              "</td><td>" + plage(a * o[1], b * o[2]) + "</td></tr>";
          }).join("") + "</tbody><tfoot><tr><th>Total</th><td>16 à 18 %</td><td><b>" + plage(a, b) + "</b></td></tr></tfoot>";
        vider(svg);
        mk("rect", { x: 100, y: 100, width: 100, height: 100, "class": "hd-sv-m" }, svg);
        tx(svg, 150, 155, "Maison", "hd-t-b", "middle");
        var cotes = { Nord: [150, 92, true, 150, 58], Sud: [150, 208, true, 150, 240], Est: [208, 150, false, 268, 154], Ouest: [92, 150, false, 32, 154] };
        O.forEach(function (o) {
          var c = cotes[o[0]], lgr = Math.max(4, o[2] * 180);
          mk("rect", c[2] ? { x: c[0] - lgr / 2, y: c[1] - 5, width: lgr, height: 10, "class": "hd-sv-v" } : { x: c[0] - 5, y: c[1] - lgr / 2, width: 10, height: lgr, "class": "hd-sv-v" }, svg);
          tx(svg, c[3], c[4], o[0], "hd-t-b", "middle");
          tx(svg, c[3], c[4] + 16, plage(a * o[1], b * o[2]), "hd-t-s", "middle");
        });
      }
      R.addEventListener("input", maj);
      maj();
    })();

    // ---------- 3.1 ventilation : l'air suit son trajet, en simple ou double flux ----------
    (function () {
      var svg = q("#hd-vmc-svg"), out = q("#hd-vmc-txt"), bs = qa(".hd-vmc-b");
      if (!svg) return;
      var gF = q("#hd-vmc-flux"), gB = q("#hd-vmc-bouches"), gT = q("#hd-vmc-temp");
      var sf = mk("g", { "class": "hd-vmc-sf" }, gF), df = mk("g", { "class": "hd-vmc-df" }, gF);
      var PIECES = [[205, 320, 270, 180], [492, 540, 470, 430], [717, 760, 590, 590]];  // entrée, porte, porte de service, bouche
      PIECES.forEach(function (p) {
        var air = [[p[1], 190], [p[1], 214], [p[2], 214], [p[2], 256], [p[3], 300]];
        flot(sf, [[p[0], 40], [p[0], 150]].concat(air), "hd-c-neuf", "hd-mk-neuf", 46, 38);
        flot(df, [[p[0], 112], [p[0], 150]].concat(air), "hd-c-tiede", "hd-mk-tiede", 46, 38);
        [sf, df].forEach(function (g) { flot(g, [[p[3], 300], [p[3], 338], [674, 338], [690, 318]], "hd-c-vicie hd-gaine", "hd-mk-vicie", 46, 38); });
        flot(df, [[740, 276], [740, 236], [p[0], 236], [p[0], 112]], "hd-c-tiede hd-gaine", "hd-mk-tiede", 46, 38);
        mk("rect", { x: p[0] - 17, y: 28, width: 34, height: 9, "class": "hd-vmc-entree hd-vmc-sf" }, gB);
        mk("circle", { cx: p[0], cy: 112, r: 9, "class": "hd-vmc-ins hd-vmc-df" }, gB);
        mk("circle", { cx: p[3], cy: 300, r: 9, "class": "hd-vmc-ext" }, gB);
      });
      flot(sf, [[760, 326], [760, 394]], "hd-c-vicie", "hd-mk-vicie", 30, 38);
      flot(df, [[760, 326], [760, 394]], "hd-c-rejet", "hd-mk-vicie", 30, 38);
      flot(df, [[858, 300], [792, 300]], "hd-c-neuf", "hd-mk-neuf", 30, 38);
      var sfT = mk("g", { "class": "hd-vmc-sf" }, gT), dfT = mk("g", { "class": "hd-vmc-df" }, gT);
      tx(sfT, 226, 54, "entrée d'air : 0 °C", "hd-t-s hd-vmc-et");
      tx(sfT, 768, 390, "rejet : 20 °C", "hd-t-s hd-vmc-et");
      tx(dfT, 220, 108, "insufflation : ≈ 15 °C", "hd-t-s hd-vmc-et");
      tx(dfT, 846, 290, "0 °C", "hd-t-s hd-vmc-et", "end");
      tx(dfT, 768, 390, "rejet : ≈ 5 °C", "hd-t-s hd-vmc-et");
      tx(gT, 166, 290, "extraction : 20 °C", "hd-t-s hd-vmc-et", "end");
      var T = {
        sf: "<b>Simple flux.</b> L'air neuf entre froid (0 °C) par les entrées d'air des pièces principales, traverse le logement en passant sous les portes, puis le caisson l'extrait des pièces de service et le rejette dehors, avec sa chaleur.",
        df: "<b>Double flux.</b> Le caisson aspire l'air neuf dehors (0 °C). Dans l'échangeur, l'air vicié extrait (20 °C) lui cède sa chaleur sans s'y mélanger : l'air neuf est insufflé tiède (≈ 15 °C) dans les pièces principales, l'air vicié repart refroidi (≈ 5 °C)." };
      function choisir(b) {
        presser(bs, b);
        svg.classList.toggle("m-sf", b.dataset.m === "sf"); svg.classList.toggle("m-df", b.dataset.m === "df");
        out.innerHTML = T[b.dataset.m];
      }
      bs.forEach(function (b) { b.addEventListener("click", function () { choisir(b); }); });
      choisir(bs[0]);
    })();

    // ---------- 3.2 puits canadien : l'air se rapproche de la température du sol ----------
    (function () {
      var R = q("#hd-pu-t"), g = q("#hd-pu-tube"), bs = qa(".hd-pu-b");
      if (!R) return;
      var TS = 13, CH = [[51, 38], [51, 150], [560, 176], [610, 176], [610, 72]];
      function mel(a, b, u) { return "rgb(" + [0, 1, 2].map(function (i) { return Math.round(a[i] + (b[i] - a[i]) * u); }).join(",") + ")"; }
      function col(T) {
        return T <= TS ? mel([44, 111, 176], [238, 243, 248], Math.max(0, Math.min(1, (T + 10) / (TS + 10)))) :
          mel([251, 234, 224], [198, 40, 40], Math.max(0, Math.min(1, (T - TS) / (35 - TS))));
      }
      var cum = [0];
      for (var i = 1; i < CH.length; i++) cum.push(cum[i - 1] + Math.hypot(CH[i][0] - CH[i - 1][0], CH[i][1] - CH[i - 1][1]));
      var L = cum[cum.length - 1], s0 = 34;
      function pt(s) { var j = 1; while (j < cum.length - 1 && cum[j] < s) j++; var a = CH[j - 1], b = CH[j], u = (s - cum[j - 1]) / (cum[j] - cum[j - 1]); return [a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u]; }
      function temp(Te, s) { var u = Math.max(0, Math.min(1, (s - s0) / (L - s0))); return TS + (Te - TS) * Math.exp(-1.2 * u); }
      mk("path", { d: "M" + CH.map(function (p) { return p.join(","); }).join(" L"), "class": "hd-pu-gaine" }, g);
      var N = 48, segs = [];
      for (var k = 0; k < N; k++) {
        var a = pt(L * k / N), b = pt(L * (k + 1) / N);
        segs.push(mk("line", { x1: a[0].toFixed(1), y1: a[1].toFixed(1), x2: b[0].toFixed(1), y2: b[1].toFixed(1), "class": "hd-pu-seg" }, g));
      }
      function maj() {
        var Te = +R.value, Ts = temp(Te, L);
        q("#hd-pu-o").textContent = nb(Te, 0) + " °C";
        segs.forEach(function (sg, k) { sg.setAttribute("stroke", col(temp(Te, L * (k + 0.5) / N))); });
        q("#hd-pu-tin").textContent = "air extérieur : " + nb(Te, 0) + " °C";
        q("#hd-pu-tout").textContent = "≈ " + nb(Ts, 1) + " °C";
        q("#hd-pu-txt").innerHTML = Te < TS - 1 ? "L'air extérieur, à " + nb(Te, 0) + " °C, <b>se réchauffe</b> au contact du sol : il arrive dans la maison vers " + nb(Ts, 1) + " °C. Le chauffage a moins à faire." :
          Te > TS + 1 ? "L'air extérieur, à " + nb(Te, 0) + " °C, <b>se rafraîchit</b> au contact du sol : il arrive dans la maison vers " + nb(Ts, 1) + " °C. Un rafraîchissement naturel." :
          "L'air extérieur est déjà proche de la température du sol : le puits canadien change peu de chose.";
        bs.forEach(function (b) { b.setAttribute("aria-pressed", +b.dataset.t === Te ? "true" : "false"); });
      }
      bs.forEach(function (b) { b.addEventListener("click", function () { R.value = b.dataset.t; maj(); }); });
      R.addEventListener("input", maj);
      maj();
    })();

    // ---------- 4.2 cycle de la pompe à chaleur (figure 11) et coefficient de performance ----------
    (function () {
      var svg = q("#hd-pac-svg"), bs = qa(".hd-pac-b"), go = q("#hd-pac-go"), out = q("#hd-pac-txt");
      if (!svg) return;
      function etat(p) {  // état du fluide selon sa place dans la boucle
        if (p[1] <= 91) return p[0] < 430 ? "hd-pac-vf" : "hd-pac-vc";
        if (p[0] >= 579) return p[1] < 146 ? "hd-pac-vc" : p[1] < 236 ? "hd-pac-ch" : "hd-pac-lt";
        if (p[1] >= 291) return p[0] > 430 ? "hd-pac-lt" : "hd-pac-lf";
        return p[1] > 236 ? "hd-pac-lf" : p[1] > 146 ? "hd-pac-ev" : "hd-pac-vf";
      }
      flot(q("#hd-pac-flux"), [[290, 236], [290, 90], [430, 90], [580, 90], [580, 292], [430, 292], [290, 292], [290, 236]], "hd-pac-fl", null, 52, 34, etat);
      var timer = null, n = 0;
      function etape(b) {
        presser(bs, b);
        qa(".hd-pac-c", svg).forEach(function (c) { c.classList.toggle("on", !!b && c.id === "hd-pac-" + b.dataset.c); });
        svg.classList.toggle("e1", !!b && b.dataset.e === "1"); svg.classList.toggle("e3", !!b && b.dataset.e === "3");
        out.innerHTML = b ? "<b>Étape " + b.dataset.e + ".</b> " + b.dataset.t : "Touche une étape : 1, 2, 3 ou 4.";
      }
      bs.forEach(function (b, i) { b.addEventListener("click", function () { n = i; etape(b); }); });
      go.addEventListener("click", function () {
        if (timer) { clearInterval(timer); timer = null; go.setAttribute("aria-pressed", "false"); go.textContent = "Lancer le cycle"; return; }
        go.setAttribute("aria-pressed", "true"); go.textContent = "Arrêter le cycle";
        etape(bs[n % 4]);
        timer = setInterval(function () { n = (n + 1) % 4; etape(bs[n]); }, 3500);
      });
      var C = q("#hd-cop-c"), B = q("#hd-cop-b");
      function cop() {
        var c = +C.value, b = +B.value, el = b / c, gr = b - el;
        q("#hd-cop-o").textContent = nb(c, 1);
        q("#hd-cop-bo").textContent = nb(b, 0) + " kWh/an";
        q("#hd-cop-e").textContent = nb(el, 0) + " kWh";
        q("#hd-cop-g").textContent = nb(gr, 0) + " kWh";
        q("#hd-cop-t").textContent = nb(b, 0) + " kWh";
        var be = q("#hd-cop-bar .hd-cop-e"), bg = q("#hd-cop-bar .hd-cop-g");
        be.style.width = (el / b * 100).toFixed(1) + "%"; bg.style.width = (gr / b * 100).toFixed(1) + "%";
        be.textContent = "électricité " + Math.round(el / b * 100) + " %"; bg.textContent = "chaleur gratuite " + Math.round(gr / b * 100) + " %";
      }
      C.addEventListener("input", cop); B.addEventListener("input", cop);
      cop();
    })();

    // ---------- 4.4 le bois d'une année de chauffage ----------
    (function () {
      var B = q("#hd-bo-b"), tab = q("#hd-bo-out");
      if (!B) return;
      function maj() {
        var u = +B.value / 1000;
        q("#hd-bo-o").textContent = nb(+B.value, 0) + " kWh/an";
        tab.innerHTML = "<thead><tr><th>Combustible</th><th>Quantité pour l'année</th></tr></thead><tbody>" + [
          ["Bois bûches", nb(u * 0.75, 1) + " stères"], ["Plaquettes", nb(u, 1) + " m³ apparents"],
          ["Écorces", nb(u * 500, 0) + " kg"], ["Granulés de bois", nb(u * 220, 0) + " kg"],
          ["Pour comparer : fioul", nb(u * 100, 0) + " litres"]
        ].map(function (r) { return "<tr><th>" + r[0] + "</th><td>" + r[1] + "</td></tr>"; }).join("") + "</tbody>";
      }
      B.addEventListener("input", maj);
      maj();
    })();

    // ---------- 5.1 programmation hebdomadaire (figure 15) ----------
    (function () {
      var grille = q("#hd-pg");
      if (!grille) return;
      var cases = qa(".hd-pc", grille);
      function figure(d, h) { return d === 2 ? h >= 7 && h <= 22 : d >= 5 ? h >= 7 : (h === 6 || h === 7 || (h >= 17 && h <= 22)); }
      function poser(c, on) { c.setAttribute("aria-pressed", on ? "true" : "false"); c.classList.toggle("on", on); }
      function maj() {
        var hc = cases.filter(function (c) { return c.classList.contains("on"); }).length, he = 168 - hc;
        var moy = (19 * hc + 16 * he) / 168, gain = 7 * (19 - moy);
        q("#hd-pg-c").textContent = hc + " h";
        q("#hd-pg-e").textContent = he + " h";
        q("#hd-pg-m").textContent = nb(moy, 1) + " °C";
        q("#hd-pg-g").textContent = gain < 0.05 ? "aucune" : "≈ " + nb(gain, 0) + " %";
      }
      function tout(f) { cases.forEach(function (c) { poser(c, f(+c.dataset.d, +c.dataset.h)); }); maj(); }
      grille.addEventListener("click", function (e) { var c = e.target.closest(".hd-pc"); if (!c) return; poser(c, !c.classList.contains("on")); maj(); });
      q("#hd-pg-fig").addEventListener("click", function () { tout(figure); });
      q("#hd-pg-tout").addEventListener("click", function () { tout(function () { return true; }); });
      q("#hd-pg-rien").addEventListener("click", function () { tout(function () { return false; }); });
      tout(figure);
    })();

    // ---------- 6.1 champ photovoltaïque : série et parallèle ----------
    (function () {
      var svg = q("#hd-pv-svg");
      if (!svg) return;
      var C = q("#hd-pv-c"), W = q("#hd-pv-w"), N = q("#hd-pv-n"), P = q("#hd-pv-p");
      function maj() {
        var c = +C.value, w = +W.value, n = +N.value, p = +P.value, Um = c * 0.5, Im = w / Um, U = n * Um, I = p * Im, Pc = n * p * w;
        q("#hd-pv-no").textContent = n; q("#hd-pv-po").textContent = p;
        q("#hd-pv-um").textContent = c + " × 0,5 = " + nb(Um, 0) + " V";
        q("#hd-pv-u").textContent = n + " × " + nb(Um, 0) + " = " + nb(U, 0) + " V";
        q("#hd-pv-i").textContent = p + " × " + nb(Im, 2) + " = " + nb(I, 1) + " A";
        q("#hd-pv-pw").textContent = (Pc >= 1000 ? nb(Pc / 1000, 1) + " kWc" : Pc + " Wc") + " (" + n * p + " m²)";
        var H = 50 + p * 86;
        svg.setAttribute("viewBox", "0 0 720 " + H);
        vider(svg);
        var x0 = 70, bx = x0 + n * 56 + 6;
        mk("line", { x1: 40, y1: 30, x2: 40, y2: H - 16, "class": "hd-pv-bus hd-pv-m" }, svg);
        mk("line", { x1: bx, y1: 30, x2: bx, y2: H - 16, "class": "hd-pv-bus hd-pv-pl" }, svg);
        tx(svg, 34, 22, "−", "hd-t-b", "middle"); tx(svg, bx, 22, "+", "hd-t-b", "middle");
        for (var i = 0; i < p; i++) {
          var y = 40 + i * 86;
          tx(svg, x0, y - 4, "Chaîne " + (i + 1), "hd-t-s");
          mk("line", { x1: 40, y1: y + 34, x2: x0, y2: y + 34, "class": "hd-pv-fil" }, svg);
          for (var j = 0; j < n; j++) {
            var x = x0 + j * 56;
            mk("rect", { x: x, y: y, width: 44, height: 66, "class": "hd-pv-mod" }, svg);
            for (var r = 1; r < 6; r++) mk("line", { x1: x, y1: y + r * 11, x2: x + 44, y2: y + r * 11, "class": "hd-pv-cel" }, svg);
            mk("line", { x1: x + 22, y1: y, x2: x + 22, y2: y + 66, "class": "hd-pv-cel" }, svg);
            mk("line", { x1: x + 44, y1: y + 34, x2: x + 56, y2: y + 34, "class": "hd-pv-fil" }, svg);
          }
        }
        var ox = Math.min(bx + 26, 640);
        mk("line", { x1: bx, y1: H / 2, x2: ox, y2: H / 2, "class": "hd-pv-fil" }, svg);
        mk("rect", { x: ox, y: H / 2 - 22, width: 74, height: 44, rx: 4, "class": "hd-pv-ond" }, svg);
        tx(svg, ox + 37, H / 2 + 5, "Onduleur", "hd-t-s", "middle");
      }
      [C, W, N, P].forEach(function (el) { el.addEventListener("input", maj); el.addEventListener("change", maj); });
      maj();
    })();

    if (!calme && flots.length) requestAnimationFrame(boucle);
  }
"""

HD_CSS = """
/* ---------- cours 1 : habitat durable (préfixe hd-) ---------- */
body.page-cours-habitat-durable .home-inner{max-width:1180px}
body.cours-page .part-body>p,body.cours-page .part-body>ul,body.cours-page .part-body>ol,body.cours-page .remarque{max-width:none}
.hd-pb{background:var(--papier); border:2px solid var(--encre); border-left:8px solid var(--vert); padding:10px 16px; margin:0 0 12px; font-size:1.02rem}
.hd-fiche{display:grid; grid-template-columns:minmax(0,1.6fr) minmax(0,1fr); gap:12px; margin:0 0 14px}
.hd-fiche>div{background:var(--papier); border:1.5px solid var(--encre); padding:6px 14px 10px}
.hd-fiche h3{margin:4px 0 6px; font:700 1rem var(--f-titre)}
.hd-fiche ul{margin:0; padding-left:1.1rem; font-size:.92rem} .hd-fiche li{margin:.2rem 0}
@media (max-width:900px){ .hd-fiche{grid-template-columns:1fr} }
.hd-svg{display:block; width:100%; height:auto; background:#fff; border:1px solid var(--trait-fin); margin:6px 0; font-family:var(--f-texte)}
.hd-svg-m{max-width:720px}
.hd-t{font-family:var(--f-texte); font-size:13px; fill:var(--encre)} .hd-t-b{font-weight:700; font-size:14px} .hd-t-s{font-size:12px; fill:var(--encre-2)}
.hd-fig-i{margin:6px 0 16px}
.hd-btns{display:flex; flex-wrap:wrap; gap:6px 8px; margin:0 0 6px}
.hd-b{border:1.5px solid var(--encre); background:#fff; padding:5px 12px; font:600 .92rem var(--f-titre); cursor:pointer; border-bottom-width:4px}
.hd-b:hover{background:var(--jaune-pale)}
.hd-b[aria-pressed="true"]{background:var(--encre); color:#fff}
.hd-out{background:var(--jaune-pale); border-left:5px solid var(--jaune); padding:8px 12px; margin:6px 0; min-height:2.4em}
.hd-cap{font-size:.86rem; color:var(--encre-2); margin:4px 0 12px}
.hd-fig figcaption{font-size:.86rem; color:var(--encre-2)}
.hd-fig img{border:1px solid var(--trait-fin)}
.hd-deux{display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:18px}
@media (max-width:820px){ .hd-deux{grid-template-columns:1fr} }
.hd-tab-w{overflow-x:auto}
.hd-tab{margin:8px 0; font-size:.92rem} .hd-tab th{text-align:left}
.hd-lab{display:inline-flex; gap:6px; align-items:center; font-weight:600; font-size:.92rem}
.hd-lab input{width:5.5em; padding:4px 6px; border:1.5px solid var(--encre-2); font:inherit}
.hd-leg{display:flex; flex-wrap:wrap; gap:6px 16px; font-size:.86rem; margin:2px 0}
.hd-leg span::before{content:""; display:inline-block; width:14px; height:14px; border-radius:50%; margin-right:5px; vertical-align:-2px}
.hd-leg-neuf::before{background:#1F5FA8} .hd-leg-tiede::before{background:#E98A00} .hd-leg-vicie::before{background:#8A6D57}
.hd-leg-eco::before{background:#F6D36B; border-radius:2px!important} .hd-leg-confort::before{background:#E4572E; border-radius:2px!important}
/* figure 1 */
.hd-bio-vent{fill:none; stroke:#1F5FA8; stroke-width:2.5; stroke-dasharray:8 6}
.hd-bio-bs{stroke:#8C4A2F; stroke-width:0}
.hd-bio-ray{stroke:#F2B705; stroke-width:3; stroke-dasharray:9 6}
.hd-bio-g.on rect,.hd-bio-g.on .hd-bio-vent{stroke:var(--rouge); stroke-width:3}
.hd-bio-g.on .hd-bio-bs{stroke:var(--rouge); stroke-width:5}
.hd-notes{display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:8px; margin:6px 0}
@media (max-width:820px){ .hd-notes{grid-template-columns:1fr} }
.hd-note{text-align:left; font:inherit; font-size:.9rem; background:#fff; border:2px solid var(--trait); border-left:7px solid var(--vert); padding:8px 10px; cursor:pointer}
.hd-note[aria-pressed="true"]{border-color:var(--rouge); background:var(--rouge-pale)}
/* figure 2 */
.hd-dep-a{cursor:pointer} .hd-dep-a polygon{fill:#E4572E; opacity:.82; stroke:#B42318; stroke-width:1.5}
.hd-dep-a:hover polygon,.hd-dep-a:focus polygon,.hd-dep-a.sel polygon{opacity:1; fill:#B42318}
.hd-dep-a:focus{outline:none} .hd-dep-a:focus-visible text{text-decoration:underline}
.hd-dep-pc{fill:#B42318}
.hd-dep-p.on>*{stroke:var(--rouge)!important; stroke-width:4!important}
/* compacité, matériaux */
.hd-comp-f1{fill:#EFE7D6; stroke:#7A6F5A; stroke-width:1.5} .hd-comp-f2{fill:#DCCFB5; stroke:#7A6F5A; stroke-width:1.5}
.hd-comp-f3{fill:#B9BDC2; stroke:#5A6670; stroke-width:1.5} .hd-comp-niv{fill:none; stroke:#7A6F5A; stroke-dasharray:5 4}
.hd-comp-c{fill:var(--bleu)}
.hd-mats{display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:12px; margin:8px 0 14px}
.hd-mat{display:flex; flex-direction:column; gap:4px; background:#fff; border:1.5px solid var(--encre); padding:8px; font-size:.9rem}
.hd-mat .hd-mat-f{margin:0} .hd-mat img{width:100%; height:130px; object-fit:cover}
.hd-mat b{font:700 1.05rem var(--f-titre)} .hd-lam{font-weight:700; color:var(--bleu)}
.hd-lam-b{fill:#B9BDC2} .hd-lam-iso{fill:#F2B705} .hd-lam-plage{fill:#B9BDC2; opacity:.45}
/* pont thermique */
.hd-pt.iti .hd-pt-ite,.hd-pt.ite .hd-pt-iti{display:none}
.hd-pt-faible{fill:#E98A00; opacity:.75}
.hd-pt-fuite{fill:#B42318; opacity:.9}
.hd-pt-zone{fill:none; stroke:#B42318; stroke-width:3; stroke-dasharray:5 4}
/* paroi */
.hd-pa-l{display:grid; gap:6px; margin:6px 0 10px}
.hd-pa-r{display:flex; flex-wrap:wrap; gap:6px 12px; align-items:center; background:#fff; border:1px solid var(--trait-fin); padding:5px 8px}
.hd-pa-n{font-weight:700; min-width:9.5em}
.hd-pa-r select,.hd-pa-r input{padding:4px 6px; border:1.5px solid var(--encre-2); font:inherit; background:#fff}
.hd-pa-r input{width:5em}
.hd-pa-ri{font-size:.88rem; margin-left:auto}
.hd-pa-c{stroke:#5A6670; stroke-width:1} .hd-pa-int{fill:#FCEBDD} .hd-pa-ext{fill:#E6EEF8}
.hd-pa-temp{fill:none; stroke:#B42318; stroke-width:3} .hd-pa-pt{fill:#B42318}
.hd-pa-tl{fill:#B42318; font-weight:700}
/* vitrages, surface vitrée */
.hd-vi-row,.hd-sv-row{display:grid; grid-template-columns:minmax(0,420px) minmax(0,1fr); gap:16px; align-items:start}
@media (max-width:820px){ .hd-vi-row,.hd-sv-row{grid-template-columns:1fr} }
.hd-sv-row{grid-template-columns:minmax(0,380px) minmax(0,1fr)}
.hd-vi-ext{fill:#E6EEF8} .hd-vi-int{fill:#FCEBDD}
.hd-vi-verre{fill:#9CC3E6; stroke:#1F5FA8; stroke-width:1.5} .hd-vi-air{fill:#F4F8FC} .hd-vi-argon{fill:#E5DCF5}
.hd-vi-couche{stroke:#D9A21B; stroke-width:3; stroke-dasharray:6 3}
.hd-vi-tube{fill:#fff; stroke:#5A6670; stroke-width:1.5} .hd-vi-lien{stroke:#5A6670; stroke-dasharray:4 4}
.hd-sv-m{fill:#F3EEDF; stroke:#7A6F5A; stroke-width:2} .hd-sv-v{fill:#1F5FA8}
/* ventilation */
#hd-vmc-svg.m-sf .hd-vmc-df,#hd-vmc-svg.m-df .hd-vmc-sf{display:none}
.hd-vmc-caisson{fill:#DDE3E8; stroke:#46525C; stroke-width:2}
.hd-vmc-entree{fill:#1F5FA8} .hd-vmc-ins{fill:#fff; stroke:#E98A00; stroke-width:3} .hd-vmc-ext{fill:#fff; stroke:#8A6D57; stroke-width:3}
.hd-vmc-np{fill:var(--encre-2)}
.hd-vmc-et{font-weight:700; fill:var(--encre)}
.hd-fl-p{fill:none; stroke-width:2; opacity:.55; stroke-dasharray:6 5}
.hd-fl-p.hd-gaine{stroke-width:5; opacity:.28; stroke-dasharray:none}
.hd-c-neuf{stroke:#1F5FA8; fill:#1F5FA8} .hd-c-tiede{stroke:#E98A00; fill:#E98A00}
.hd-c-vicie{stroke:#8A6D57; fill:#8A6D57} .hd-c-rejet{stroke:#7FA3CF; fill:#7FA3CF}
.hd-fl-d{stroke:none!important; opacity:.95}
.hd-fl-p.hd-c-neuf,.hd-fl-p.hd-c-tiede,.hd-fl-p.hd-c-vicie,.hd-fl-p.hd-c-rejet{fill:none}
/* puits canadien */
.hd-pu-gaine{fill:none; stroke:#46525C; stroke-width:18; stroke-linejoin:round}
.hd-pu-seg{stroke-width:13; stroke-linecap:round}
/* pompe à chaleur */
.hd-pac-c rect,.hd-pac-c circle,.hd-pac-c polygon{fill:#fff; stroke:#46525C; stroke-width:2.5; transition:fill .3s}
#hd-pac-evap rect{stroke:#1F5FA8} #hd-pac-cond rect{stroke:#B42318}
.hd-pac-c.on rect,.hd-pac-c.on circle,.hd-pac-c.on polygon{fill:var(--jaune-pale); stroke-width:4}
.hd-pac-serp{fill:none; stroke:#7FA3CF; stroke-width:3} #hd-pac-cond .hd-pac-serp{stroke:#E4572E}
.hd-pac-chaleur{opacity:.55} .hd-pac-froid{fill:#3C8D5A} .hd-pac-chaud{fill:#B42318}
#hd-pac-svg.e1 .hd-pac-froid,#hd-pac-svg.e3 .hd-pac-chaud{opacity:1}
.hd-fl-p.hd-pac-fl{display:none}
.hd-pac-vf{fill:#7FB3E0} .hd-pac-vc{fill:#C62828} .hd-pac-ch{fill:#E4572E} .hd-pac-lt{fill:#E98A00} .hd-pac-lf{fill:#1F5FA8} .hd-pac-ev{fill:#4A90D9}
.hd-barre{display:flex; height:30px; border:1.5px solid var(--encre); margin:10px 0 4px; font:700 .82rem var(--f-titre); overflow:hidden}
.hd-barre span{display:flex; align-items:center; padding:0 8px; white-space:nowrap; overflow:hidden; color:#fff}
.hd-cop-e{background:#E98A00} .hd-cop-g{background:#3C8D5A}
/* chauffage central */
.hd-chaine{display:flex; flex-wrap:wrap; align-items:stretch; gap:6px; margin:10px 0 4px}
.hd-chaine>div{flex:1 1 150px; display:flex; flex-direction:column; gap:4px; background:#fff; border:2px solid var(--encre); padding:8px 10px}
.hd-chaine b{font:700 .98rem var(--f-titre); border-bottom:2px solid var(--orange); padding-bottom:3px}
.hd-chaine span{font-size:.9rem; background:var(--orange-pale); padding:2px 6px}
.hd-chaine>i{align-self:center; font-style:normal; font:700 1.5rem var(--f-titre); color:var(--orange)}
/* programmation */
.hd-pg-wrap{overflow-x:auto; margin:4px 0 6px}
.hd-pg{border-collapse:collapse; font-size:.78rem}
.hd-pg th{font-weight:600; padding:1px 3px; text-align:center} .hd-pg tr th:first-child{text-align:right; padding-right:6px}
.hd-pg td{padding:1px}
.hd-pc{display:block; width:24px; height:22px; border:1px solid #D8B04A; background:#F6D36B; cursor:pointer; padding:0}
.hd-pc.on{background:#E4572E; border-color:#B42318}
.hd-pc:focus-visible{outline:3px solid var(--bleu); outline-offset:0}
/* éclairage */
.hd-ecl{display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:10px; margin:8px 0 12px}
.hd-ecl-c{display:flex; flex-direction:column; gap:4px; background:#fff; border:1.5px solid var(--encre); padding:8px; font-size:.88rem}
.hd-ecl-c b{font:700 .98rem var(--f-titre)} .hd-ecl-f{margin:0} .hd-ecl-c img{width:100%; height:110px; object-fit:contain; border:0!important}
/* photovoltaïque */
.hd-pv-mod{fill:#1F4E8C; stroke:#0F2D55; stroke-width:1.5} .hd-pv-cel{stroke:#7FA3CF; stroke-width:.8}
.hd-pv-fil{stroke:#B42318; stroke-width:2.5} .hd-pv-bus{stroke-width:4} .hd-pv-pl{stroke:#B42318} .hd-pv-m{stroke:#1C2530}
.hd-pv-ond{fill:#E6EEF8; stroke:#1F5FA8; stroke-width:2}
@media print{
  .hd-btns,.hd-notes,.hd-b{display:none!important}
  .hd-svg{break-inside:avoid}
  .hd-pg-wrap{overflow:visible}
}
"""


def hd_js():
    return HD_JS
