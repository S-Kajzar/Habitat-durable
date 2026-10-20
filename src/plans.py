"""Schémas à compléter des exercices, redessinés en SVG avec leurs cases (modèle du dépôt « Chaîne fonctionnelle »,
où ce module dessine les schémas de l'exercice 1.1).

baie() (exercice 1.1) : une pièce en coupe verticale, son mur de façade vu de l'intérieur, deux baies et leurs cotes.
Les six cases reçoivent le vocabulaire de la lecture de plan (hauteur sous plafond, retombée de linteau, hauteur de
baie, allège, trumeau, cote de niveau). Aucune valeur n'est écrite : l'élève reconnaît ce que mesure chaque cote.

paroi() (exercice 1.2) : le mur de la partie habitation du pavillon en coupe horizontale, couche par couche, avec
l'allure de la température dans son épaisseur. Les six cases reçoivent les noms des couches et des deux ambiances.

iti_ite() (exercice 2.1) : deux coupes verticales d'un mur au droit d'un plancher, isolé par l'intérieur puis par
l'extérieur. En ITI, le plancher traverse l'isolant et la chaleur fuit par la liaison (pont thermique) ; en ITE,
l'isolant passe devant le plancher. Les six cases reçoivent les noms des procédés et des éléments.

Format attendu par le générateur (render_plan) : {"svg", "w", "h", "cases": {repère: (x, y, l, h, indication)}, "maxw"},
coordonnées dans le viewBox du dessin.
"""

W, H = 960, 440
PLAFOND, SOL = 60, 360           # sous-face du plancher haut, sol fini
HAUT_BAIE, BAS_BAIE = 97, 250    # haut et bas des baies (retombée, hauteur de baie, allège)
B1, B2 = (330, 477), (673, 820)  # baies : bords gauche et droit


def _cote_v(x, ys):
    """Chaîne de cotes verticale : ligne d'attache et traits obliques à chaque repère."""
    t = "".join(f'<line x1="{x - 7}" y1="{y + 7}" x2="{x + 7}" y2="{y - 7}"/>' for y in ys)
    return f'<g class="lp-cote"><line x1="{x}" y1="{ys[0]}" x2="{x}" y2="{ys[-1]}"/>{t}</g>'


def _cote_h(y, xs):
    t = "".join(f'<line x1="{x - 7}" y1="{y + 7}" x2="{x + 7}" y2="{y - 7}"/>' for x in xs)
    return f'<g class="lp-cote"><line x1="{xs[0]}" y1="{y}" x2="{xs[-1]}" y2="{y}"/>{t}</g>'


def _baie(x1, x2):
    m = (x1 + x2) / 2
    return (f'<rect x="{x1 - 10}" y="{HAUT_BAIE - 13}" width="{x2 - x1 + 20}" height="13" class="lp-linteau"/>'
            f'<rect x="{x1}" y="{HAUT_BAIE}" width="{x2 - x1}" height="{BAS_BAIE - HAUT_BAIE}" class="lp-vitre"/>'
            f'<line x1="{m}" y1="{HAUT_BAIE}" x2="{m}" y2="{BAS_BAIE}" class="lp-cadre"/>'
            f'<line x1="{x1 + 14}" y1="{HAUT_BAIE + 40}" x2="{x1 + 44}" y2="{HAUT_BAIE + 12}" class="lp-reflet"/>'
            f'<rect x="{x1 - 8}" y="{BAS_BAIE}" width="{x2 - x1 + 16}" height="7" class="lp-appui"/>')


def baie():
    svg = f"""<svg class="plan-svg" viewBox="0 0 {W} {H}" role="img" aria-label="Coupe verticale d'une pièce : mur de façade vu de l'intérieur, avec deux baies et six cotes repérées de 1 à 6">
<defs><pattern id="lp-beton" width="10" height="10" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
<rect width="10" height="10" fill="#E3E5E0"/><line x1="0" y1="0" x2="0" y2="10" stroke="#A5ADAA" stroke-width="2"/></pattern></defs>
<rect width="{W}" height="{H}" fill="#FFFFFF"/>
<rect x="150" y="{PLAFOND}" width="790" height="{SOL - PLAFOND}" fill="#FBF8F1"/>
<rect x="150" y="30" width="790" height="{PLAFOND - 30}" fill="url(#lp-beton)" stroke="#46525C" stroke-width="1.5"/>
<rect x="150" y="{SOL}" width="790" height="26" fill="url(#lp-beton)" stroke="#46525C" stroke-width="1.5"/>
<text x="936" y="50" class="lp-t" text-anchor="end">plancher haut</text><text x="936" y="378" class="lp-t" text-anchor="end">plancher bas</text>
<text x="330" y="{PLAFOND + 16}" class="lp-t lp-t-s">plafond</text><text x="490" y="{SOL - 8}" class="lp-t lp-t-s">sol fini</text>
{_baie(*B1)}{_baie(*B2)}
{_cote_v(312, [PLAFOND, HAUT_BAIE, BAS_BAIE, SOL])}
{_cote_v(885, [PLAFOND, SOL])}
{_cote_h(176, [B1[1], B2[0]])}
<g class="lp-niv"><line x1="535" y1="{SOL - 14}" x2="585" y2="{SOL - 14}"/><polygon points="548,{SOL - 14} 572,{SOL - 14} 560,{SOL}"/>
<text x="587" y="{SOL - 18}" class="lp-t">0,00</text></g>
</svg>"""
    cases = {"1": (826, 192, 128, 36, ""), "2": (152, PLAFOND, 150, 36, ""), "3": (152, 155, 150, 36, ""),
             "4": (152, 287, 150, 36, ""), "5": (500, 158, 150, 36, ""), "6": (622, 312, 150, 36, "")}
    return {"svg": svg, "w": W, "h": H, "cases": cases, "maxw": 980, "cls": "lp-fig"}


# ------------------------------------------------------------ exercice 1.2 : la paroi en coupe
PW, PH = 960, 460
CM = 14                                   # échelle : 1 cm d'épaisseur = 14 unités du dessin
HAUT, BAS = 70, 350                       # longueur de mur représentée (coupe horizontale, vue de dessus)
COUCHES = [("platre", 1), ("pse", 10), ("parpaing", 20), ("enduit", 1)]  # de l'intérieur vers l'extérieur, en cm
R_COUCHES = [0.01 / 0.25, 0.10 / 0.032, 0.20 / 0.95, 0.01 / 1.0]         # résistances (DT2 de l'exercice 1.2)
X0 = 260                                  # face intérieure du mur
T_INT, T_EXT = 19, -5                     # températures de part et d'autre (°C)


def _y_temp(t):
    return 110 + (T_INT - t) * 200 / (T_INT - T_EXT)


def paroi():
    xs = [X0]
    for _n, e in COUCHES:
        xs.append(xs[-1] + e * CM)
    x_pl, x_pse, x_pa, x_en, x_ext = xs
    # allure de la température : la chute dans chaque couche est proportionnelle à sa résistance
    rt, t, pts = sum(R_COUCHES), T_INT, [(0, _y_temp(T_INT)), (X0, _y_temp(T_INT))]
    for x, r in zip(xs[1:], R_COUCHES):
        t -= (T_INT - T_EXT) * r / rt
        pts.append((x, _y_temp(t)))
    pts.append((PW, _y_temp(T_EXT)))
    courbe = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    alv = "".join(f'<rect x="{x}" y="{y}" width="110" height="112" rx="6" class="ip-alv"/>'
                  for x in (x_pa + 16, x_pa + 154) for y in (HAUT + 14, HAUT + 154))
    svg = f"""<svg class="plan-svg" viewBox="0 0 {PW} {PH}" role="img" aria-label="Coupe horizontale d'un mur isolé par l'intérieur : quatre couches entre la pièce et l'extérieur, six cases repérées de 1 à 6, et la courbe de température qui passe de 19 °C à −5 °C">
<defs><pattern id="ip-billes" width="12" height="12" patternUnits="userSpaceOnUse"><rect width="12" height="12" fill="#EEF3FA"/>
<circle cx="3" cy="3" r="2.6" fill="none" stroke="#A9BCD6" stroke-width="1"/><circle cx="9" cy="9" r="2.6" fill="none" stroke="#A9BCD6" stroke-width="1"/></pattern>
<pattern id="ip-grain" width="6" height="6" patternUnits="userSpaceOnUse"><rect width="6" height="6" fill="#E6DECB"/><circle cx="2" cy="2" r=".9" fill="#A89B7E"/></pattern></defs>
<rect width="{X0}" height="{PH}" fill="#FBF1E4"/><rect x="{x_ext}" width="{PW - x_ext}" height="{PH}" fill="#E8F1FA"/>
<rect x="{X0}" width="{x_ext - X0}" height="{PH}" fill="#FFFFFF"/>
<rect x="{x_pl}" y="{HAUT}" width="{x_pse - x_pl}" height="{BAS - HAUT}" class="ip-platre"/>
<rect x="{x_pse}" y="{HAUT}" width="{x_pa - x_pse}" height="{BAS - HAUT}" fill="url(#ip-billes)" class="ip-c"/>
<rect x="{x_pa}" y="{HAUT}" width="{x_en - x_pa}" height="{BAS - HAUT}" class="ip-parpaing"/>{alv}
<rect x="{x_en}" y="{HAUT}" width="{x_ext - x_en}" height="{BAS - HAUT}" fill="url(#ip-grain)" class="ip-c"/>
<path d="M{X0 - 12},{HAUT} h{x_ext - X0 + 24} M{X0 - 12},{BAS} h{x_ext - X0 + 24}" class="ip-coupure"/>
<polyline points="{courbe}" class="ip-temp"/>
<text x="16" y="{_y_temp(T_INT) - 10:.0f}" class="ip-t ip-t-temp">19 °C</text>
<text x="{PW - 16}" y="{_y_temp(T_EXT) - 10:.0f}" class="ip-t ip-t-temp" text-anchor="end">−5 °C</text>
<text x="{PW - 16}" y="{PH - 14}" class="ip-t ip-t-s" text-anchor="end">— température dans le mur (allure)</text>
<g class="ip-renvoi"><polyline points="210,30 {x_pl - 8},30 {(x_pl + x_pse) / 2:.0f},{HAUT + 24}"/><circle cx="{(x_pl + x_pse) / 2:.0f}" cy="{HAUT + 24}" r="4"/>
<polyline points="750,30 {x_ext + 8},30 {(x_en + x_ext) / 2:.0f},{HAUT + 24}"/><circle cx="{(x_en + x_ext) / 2:.0f}" cy="{HAUT + 24}" r="4"/>
<line x1="{(x_pse + x_pa) / 2:.0f}" y1="392" x2="{(x_pse + x_pa) / 2:.0f}" y2="{BAS - 24}"/><circle cx="{(x_pse + x_pa) / 2:.0f}" cy="{BAS - 24}" r="4"/>
<line x1="{(x_pa + x_en) / 2:.0f}" y1="392" x2="{(x_pa + x_en) / 2:.0f}" y2="{BAS - 24}"/><circle cx="{(x_pa + x_en) / 2:.0f}" cy="{BAS - 24}" r="4"/></g>
</svg>"""
    c_pse, c_pa = (x_pse + x_pa) / 2, (x_pa + x_en) / 2
    cases = {"1": (50, 190, 150, 36, ""), "2": (60, 12, 150, 36, ""), "3": (c_pse - 75, 392, 150, 36, ""),
             "4": (c_pa - 75, 392, 150, 36, ""), "5": (750, 12, 150, 36, ""), "6": (775, 190, 150, 36, "")}
    return {"svg": svg, "w": PW, "h": PH, "cases": cases, "maxw": 980, "cls": "ip-fig"}


# ------------------------------------------------------------ exercice 2.1 : ITI ou ITE, au droit d'un plancher
IW, IH = 960, 540
I_HAUT, I_BAS = 70, 470                   # hauteur de mur représentée
DALLE = (250, 290)                        # plancher : dessus, dessous
FLECHE_Y = 270


def _fleche(x1, x2, y, cls):
    """Flèche horizontale de x1 vers x2 (x2 < x1) : le flux de chaleur, de l'intérieur vers l'extérieur."""
    return (f'<line x1="{x1}" y1="{y}" x2="{x2 + 14}" y2="{y}" class="{cls}"/>'
            f'<polygon points="{x2},{y} {x2 + 18},{y - 9} {x2 + 18},{y + 9}" class="{cls}-p"/>')


def _coupe(ox, ite):
    """Une coupe : extérieur à gauche, intérieur à droite ; mur en parpaing, isolant, plancher en béton."""
    d1, d2 = DALLE
    h = I_BAS - I_HAUT
    if ite:   # enduit, isolant continu, parpaing, plâtre ; le plancher s'appuie sur le parpaing
        x_en, x_iso, x_pa, x_pl, x_int = ox + 126, ox + 130, ox + 174, ox + 244, ox + 250
        iso = f'<rect x="{x_iso}" y="{I_HAUT}" width="{x_pa - x_iso}" height="{h}" fill="url(#ii-iso)" class="ii-c"/>'
        mur = (f'<rect x="{x_pa}" y="{I_HAUT}" width="{x_pl - x_pa}" height="{h}" fill="url(#ii-parp)" class="ii-c"/>'
               f'<rect x="{x_pl}" y="{I_HAUT}" width="{x_int - x_pl}" height="{h}" class="ii-platre"/>')
        dalle_x = x_pa + 8
        flux = _fleche(ox + 410, x_pa - 12, FLECHE_Y, "ii-flux-faible")  # freinée par l'isolant
    else:     # enduit, parpaing, isolant et plâtre interrompus par le plancher, qui traverse le mur
        x_en, x_pa, x_iso, x_pl, x_int = ox + 166, ox + 170, ox + 240, ox + 284, ox + 290
        iso = "".join(f'<rect x="{x_iso}" y="{y1}" width="{x_pl - x_iso}" height="{y2 - y1}" fill="url(#ii-iso)" '
                      f'class="ii-c"/><rect x="{x_pl}" y="{y1}" width="{x_int - x_pl}" height="{y2 - y1}" '
                      f'class="ii-platre"/>' for y1, y2 in ((I_HAUT, d1), (d2, I_BAS)))
        mur = f'<rect x="{x_pa}" y="{I_HAUT}" width="{x_iso - x_pa}" height="{h}" fill="url(#ii-parp)" class="ii-c"/>'
        dalle_x = x_pa + 8
        flux = _fleche(ox + 410, ox + 24, FLECHE_Y, "ii-flux")
    return (f'<rect x="{ox}" y="{I_HAUT}" width="{x_en - ox}" height="{h}" fill="#E8F1FA"/>'
            f'<rect x="{x_int}" y="{I_HAUT}" width="{ox + 440 - x_int}" height="{h}" fill="#FBF1E4"/>'
            f'<rect x="{x_en}" y="{I_HAUT}" width="4" height="{h}" class="ii-enduit"/>{mur}{iso}'
            f'<rect x="{dalle_x}" y="{d1}" width="{ox + 440 - dalle_x}" height="{d2 - d1}" fill="url(#ii-beton)" '
            f'class="ii-c"/>'
            f'<path d="M{ox},{I_HAUT} h440 M{ox},{I_BAS} h440" class="ii-coupure"/>{flux}'
            f'<text x="{ox + 8}" y="{I_HAUT + 22}" class="ii-t">extérieur</text>'
            f'<text x="{ox + 432}" y="{I_HAUT + 22}" class="ii-t" text-anchor="end">intérieur</text>')


def iti_ite():
    g, d = 20, 500        # origines des deux coupes
    svg = f"""<svg class="plan-svg" viewBox="0 0 {IW} {IH}" role="img" aria-label="Deux coupes verticales d'un mur au droit d'un plancher : à gauche l'isolant est côté intérieur et le plancher le traverse, une grosse flèche de chaleur passe par le plancher ; à droite l'isolant est côté extérieur et passe devant le plancher ; six cases repérées de 1 à 6">
<defs><pattern id="ii-iso" width="12" height="12" patternUnits="userSpaceOnUse"><rect width="12" height="12" fill="#F6E27A"/>
<path d="M0,6 q3,-5 6,0 t6,0" fill="none" stroke="#C9A93A" stroke-width="1.2"/></pattern>
<pattern id="ii-parp" width="10" height="10" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="10" height="10" fill="#C3C8CD"/>
<line x1="0" y1="0" x2="0" y2="10" stroke="#8C949B" stroke-width="2"/></pattern>
<pattern id="ii-beton" width="14" height="14" patternUnits="userSpaceOnUse"><rect width="14" height="14" fill="#D7D9D4"/>
<circle cx="4" cy="4" r="1.3" fill="#8C918A"/><circle cx="10" cy="9" r="1" fill="#8C918A"/></pattern></defs>
<rect width="{IW}" height="{IH}" fill="#FFFFFF"/>
{_coupe(g, False)}{_coupe(d, True)}
<line x1="480" y1="{I_HAUT}" x2="480" y2="{I_BAS}" class="ii-sep"/>
<g class="ii-renvoi"><polyline points="176,318 {g + 182},{DALLE[1] - 8}"/><circle cx="{g + 182}" cy="{DALLE[1] - 8}" r="4"/>
<line x1="595" y1="492" x2="{d + 152}" y2="440"/><circle cx="{d + 152}" cy="440" r="4"/>
<line x1="775" y1="492" x2="{d + 209}" y2="440"/><circle cx="{d + 209}" cy="440" r="4"/>
<line x1="850" y1="226" x2="850" y2="{DALLE[0] + 12}"/><circle cx="850" cy="{DALLE[0] + 12}" r="4"/></g>
</svg>"""
    cases = {"1": (165, 16, 150, 36, ""), "2": (645, 16, 150, 36, ""), "3": (26, 300, 150, 36, ""),
             "4": (520, 492, 150, 36, ""), "5": (700, 492, 150, 36, ""), "6": (775, 190, 150, 36, "")}
    return {"svg": svg, "w": IW, "h": IH, "cases": cases, "maxw": 980, "cls": "ii-fig"}


PLAN_CSS = """
/* ---------- exercice 1.1 : schéma de la baie (préfixe lp-) ---------- */
.lp-fig .plan-svg text{font-family:var(--f-texte)}
.lp-t{font-size:13px; fill:var(--encre-2)} .lp-t-s{font-size:12px; font-style:italic}
.lp-cote line{stroke:var(--encre); stroke-width:1.5}
.lp-linteau{fill:#C9C2B4; stroke:#7A6F5A; stroke-width:1.2} .lp-appui{fill:#C9C2B4; stroke:#7A6F5A; stroke-width:1}
.lp-vitre{fill:#DCEAF7; stroke:#1C2530; stroke-width:3} .lp-cadre{stroke:#1C2530; stroke-width:2.5}
.lp-reflet{stroke:#FFFFFF; stroke-width:3; opacity:.8}
.lp-niv line{stroke:var(--encre); stroke-width:1.5} .lp-niv polygon{fill:var(--encre)} .lp-niv text{fill:var(--encre); font-weight:700}
/* ---------- exercice 1.2 : la paroi en coupe (préfixe ip-) ---------- */
.ip-fig .plan-svg text{font-family:var(--f-texte)}
.ip-t{font-size:13px; fill:var(--encre-2)} .ip-t-s{font-size:12px; font-style:italic} .ip-t-temp{font-size:16px; font-weight:700; fill:#B3261E}
.ip-c{stroke:#5E5848; stroke-width:1.2}
.ip-platre{fill:#F6F3EA; stroke:#5E5848; stroke-width:1.2}
.ip-parpaing{fill:#A9AFB5; stroke:#4B535B; stroke-width:1.4} .ip-alv{fill:#F4F5F6; stroke:#4B535B; stroke-width:1.2}
.ip-coupure{stroke:#46525C; stroke-width:1.5; stroke-dasharray:10 5; fill:none}
.ip-temp{fill:none; stroke:#C8102E; stroke-width:3; stroke-linejoin:round}
.ip-renvoi polyline, .ip-renvoi line{fill:none; stroke:var(--encre); stroke-width:1.4} .ip-renvoi circle{fill:var(--encre)}
/* ---------- exercice 2.1 : ITI ou ITE (préfixe ii-) ---------- */
.ii-fig .plan-svg text{font-family:var(--f-texte)}
.ii-t{font-size:13px; fill:var(--encre-2); font-style:italic}
.ii-c{stroke:#5E5848; stroke-width:1.2} .ii-platre{fill:#F6F3EA; stroke:#5E5848; stroke-width:1}
.ii-enduit{fill:#E6DECB; stroke:#5E5848; stroke-width:1}
.ii-coupure{stroke:#46525C; stroke-width:1.5; stroke-dasharray:10 5; fill:none}
.ii-sep{stroke:var(--trait); stroke-width:2}
.ii-flux{stroke:#C8102E; stroke-width:9; stroke-linecap:round; opacity:.85} .ii-flux-p{fill:#C8102E; opacity:.85}
.ii-flux-faible{stroke:#C8102E; stroke-width:3; stroke-linecap:round; opacity:.7} .ii-flux-faible-p{fill:#C8102E; opacity:.7}
.ii-renvoi polyline, .ii-renvoi line{fill:none; stroke:var(--encre); stroke-width:1.4} .ii-renvoi circle{fill:var(--encre)}
"""
