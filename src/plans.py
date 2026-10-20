"""Exercice 1.1 (lecture de plan) : schéma à compléter, redessiné en SVG avec ses cases (modèle du dépôt
« Chaîne fonctionnelle », où ce module dessine les schémas de l'exercice 1.1).

baie() : une pièce en coupe verticale, son mur de façade vu de l'intérieur, deux baies et leurs cotes. Les six cases
reçoivent le vocabulaire de la lecture de plan (hauteur sous plafond, retombée de linteau, hauteur de baie, allège,
trumeau, cote de niveau). Aucune valeur n'est écrite : l'élève reconnaît ce que mesure chaque cote.

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


PLAN_CSS = """
/* ---------- exercice 1.1 : schéma de la baie (préfixe lp-) ---------- */
.lp-fig .plan-svg text{font-family:var(--f-texte)}
.lp-t{font-size:13px; fill:var(--encre-2)} .lp-t-s{font-size:12px; font-style:italic}
.lp-cote line{stroke:var(--encre); stroke-width:1.5}
.lp-linteau{fill:#C9C2B4; stroke:#7A6F5A; stroke-width:1.2} .lp-appui{fill:#C9C2B4; stroke:#7A6F5A; stroke-width:1}
.lp-vitre{fill:#DCEAF7; stroke:#1C2530; stroke-width:3} .lp-cadre{stroke:#1C2530; stroke-width:2.5}
.lp-reflet{stroke:#FFFFFF; stroke-width:3; opacity:.8}
.lp-niv line{stroke:var(--encre); stroke-width:1.5} .lp-niv polygon{fill:var(--encre)} .lp-niv text{fill:var(--encre); font-weight:700}
"""
