#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Génère la page « Habitat durable » (index.html) : un accueil sur le modèle du dépôt « Chaîne fonctionnelle »
(lui-même repris du dépôt « Résistance des matériaux »), puis les cours, les exercices et les études de cas,
chacun ouvert par ?ex=….

    python3 src/generer.py

Le bloc <style> du gabarit, le moteur de correction (Grading) et le moteur applicatif sont recopiés tels quels ;
seules les entrées propres au sujet du moteur applicatif sont remplacées, chaque remplacement étant vérifié :
DECOR, DR_NAMES, le texte de la fenêtre « Imprimer les DR », le libellé « Diagramme validé » des questions à
plusieurs cases et CONSEIL_MIN, lu dans window.__CONSEIL_MIN__ puisque la durée conseillée dépend de l'exercice
ouvert. Un petit script d'aiguillage, exécuté avant les moteurs, installe le contenu demandé par l'adresse.

Aucun cours, exercice ni étude n'est encore décrit : chaque rubrique de l'accueil l'annonce par une carte « En cours
d'édition », remplacée d'elle-même dès qu'un cours (COURS), un exercice ou une étude (EXO_DEFS) est ajouté.
Les exemples complets (exercice à étiquettes posées sur des schémas, QCM, cours interactifs) sont dans le dépôt
« Chaîne fonctionnelle ».
"""
import base64
import copy
import html
import json
import pathlib
import re
import struct
import types
import unicodedata

import cours_habitat
import qcm

ROOT = pathlib.Path(__file__).resolve().parent.parent
GABARIT = ROOT / "src" / "gabarit-exercice-interactif.html"
IMAGES = ROOT / "src" / "images"
SORTIE = ROOT / "index.html"
TITRE = "Habitat durable"


# ============================================================ outils
def png(name):
    data = (IMAGES / f"{name}.png").read_bytes()
    w, h = struct.unpack(">II", data[16:24])
    return "data:image/png;base64," + base64.b64encode(data).decode(), w, h


def esc(s):
    return html.escape(s, quote=True)


def frac(a, b):
    return f'<span class="frac"><span>{a}</span><span>{b}</span></span>'


def fr(x, d=1):
    return f"{x:,.{d}f}".replace(",", " ").replace(".", ",")


def figure(name, alt, caption, maxw, cls="fig"):
    src, w, h = png(name)
    return (f'<figure class="{cls}" style="max-width:{maxw}px"><img src="{src}" alt="{esc(alt)}" '
            f'width="{w}" height="{h}">' + (f"<figcaption>{caption}</figcaption>" if caption else "") + "</figure>")


def jpg(name):
    """Photo JPEG intégrée en data URI ; dimensions lues dans le segment SOF."""
    data = (IMAGES / f"{name}.jpg").read_bytes()
    i = 2
    while i < len(data):
        marker, size = data[i + 1], struct.unpack(">H", data[i + 2:i + 4])[0]
        if marker in (0xC0, 0xC1, 0xC2):
            h, w = struct.unpack(">HH", data[i + 5:i + 9])
            return "data:image/jpeg;base64," + base64.b64encode(data).decode(), w, h
        i += 2 + size
    raise ValueError(f"{name}.jpg : dimensions introuvables")


def photo(name, alt, caption, maxw, cls="fig"):
    src, w, h = jpg(name)
    return (f'<figure class="{cls}" style="max-width:{maxw}px"><img src="{src}" alt="{esc(alt)}" '
            f'width="{w}" height="{h}">' + (f"<figcaption>{caption}</figcaption>" if caption else "") + "</figure>")


def sub_once(text, pattern, repl, flags=0):
    """Remplacement vérifié : le motif doit apparaître exactement une fois."""
    new, n = re.subn(pattern, lambda m: repl, text, flags=flags)
    assert n == 1, f"motif introuvable ou multiple : {pattern!r} ({n})"
    return new


def svg(name):
    """Dessin SVG intégré en data URI ; dimensions lues dans les attributs width et height de sa balise <svg>."""
    data = (IMAGES / f"{name}.svg").read_text(encoding="utf-8")
    tag = re.search(r"<svg\b[^>]*>", data).group(0)
    w, h = (round(float(re.search(rf'\b{a}="([\d.]+)"', tag).group(1))) for a in ("width", "height"))
    return "data:image/svg+xml;base64," + base64.b64encode(data.encode("utf-8")).decode(), w, h


def image(name):
    """Image de src/images, quel que soit son format : JPEG, sinon PNG, sinon SVG."""
    for ext, lire in (("jpg", jpg), ("png", png), ("svg", svg)):
        if (IMAGES / f"{name}.{ext}").exists():
            return lire(name)
    raise FileNotFoundError(f"src/images/{name}.jpg, .png ou .svg introuvable")


# ============================================================ correcteurs (moteur Grading du gabarit)
def P(*alts):
    """Motif de mots-clés : chaque argument liste des mots équivalents séparés par « | », en minuscules et sans
    accents ; la réponse doit contenir un mot de chaque argument (une petite faute de frappe est tolérée)."""
    return [a.split("|") for a in alts]


def KW(*motifs, forbid=""):
    # forbid : mots qui rendent la réponse fausse ; ils sont comparés avec la même tolérance aux fautes de frappe
    # (« interieure » refuserait aussi « exterieure », à deux lettres près : on écrit « interieur »).
    g = {"type": "kw", "any": list(motifs)}
    if forbid:
        g["forbid"] = forbid.split("|")
    return g


# Les correcteurs du moteur, en plus des mots-clés : valeur numérique avec unité, oui ou non. Le moteur connaît aussi
# « code » (réponse exacte, utilisée par les QCM), « intset » (ensemble de numéros) et « chasles » (voir le gabarit).
def unite_normee(u):
    """Écriture d'une unité telle que le moteur la compare (normUnit et unitCheck du gabarit) : minuscules, sans
    accents, exposants en chiffres, séparateurs retirés ; « m²·K/W » → « m2k/w »."""
    s = unicodedata.normalize("NFD", u.lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub("[⁻−–—‐‑]", "-", s)
    s = s.translate(str.maketrans("¹²³⁰⁴⁵⁶⁷⁸⁹", "1230456789"))
    s = re.sub(r"[.·∙⋅*×_,;:()\[\]'\"’`^]", " ", s)
    return "".join(t for t in s.split() if re.search("[a-z°]", t))


def NUM(valeur, unite=None, accepte=(), tol=0, rel=0.01):
    """Valeur numérique : juste à rel près (1 % par défaut) ou à tol près. Avec une unité (« m²·K/W »), une valeur
    juste sans unité, ou avec une autre unité, vaut un demi-point ; accepte : autres écritures de l'unité admises."""
    g = {"type": "num", "value": valeur}
    if tol:
        g["absTol"] = tol
    if rel:
        g["relTol"] = rel
    if unite:
        formes = [unite_normee(u) for u in (unite, *accepte)]
        g["unit"] = {"label": unite, "accept": list(dict.fromkeys(formes))}
    return g


def OUI_NON(valeur):
    """Réponse qui commence par « oui » ou « non » (le moteur reconnaît aussi « convient », « insuffisant »…)."""
    return {"type": "yesno", "value": bool(valeur)}


# ============================================================ blocs de contenu
# Une partie d'exercice : {"title": …, "minutes": durée conseillée (elle fixe la pondération), "intro": [HTML…],
# "blocks": [Q(…), GRP(…), QBAR(…), HTML(…)…]} et, si des cases sont posées sur un schéma, "plan" (voir render_plan).
def HTML(raw):
    return {"kind": "html", "html": raw}


def QBAR(docs, ans="ci-dessous"):
    return {"kind": "qbar", "docs": list(docs), "ans": ans}


def Q(stem, hint, grader, expected, why):
    """Question à une case (saisie libre, touche Entrée ou bouton « Valider »), un point : grader KW, NUM, OUI_NON…"""
    return {"kind": "q", "stem": stem, "hint": hint, "grader": grader, "expected": expected, "why": why}


def GRP(stem, hint, fields, why, etiquettes=None, liste="Étiquettes", zones=None):
    """Question à plusieurs cases validées ensemble (mécanisme « fast-q » du gabarit), une case = un point.
    fields : liste de (libellé de la case, correcteur, réponse attendue affichée dans la correction).
    etiquettes : liste d'étiquettes à glisser dans les cases (réutilisables, avec des intrus), triée à l'affichage ;
    sans liste, chaque case est un champ de saisie. liste : titre de la liste (les questions d'une même partie qui
    ont les mêmes étiquettes la partagent). zones : repères des cases sur le schéma de la partie (part["plan"]).
    Le gabarit compte une case juste ou fausse, sans demi-point : une valeur avec unité se demande dans une question
    à une case (Q) ; ici, NUM sans unité, l'unité étant donnée dans le libellé de la case (« Épaisseur (cm) »)."""
    assert not any(gr.get("unit") for _l, gr, _a in fields), f"unité dans une question à plusieurs cases : {stem}"
    g = {"kind": "grp", "stem": stem, "hint": hint, "fields": fields, "why": why}
    if etiquettes:
        g["bank"], g["bank_t"] = sorted(etiquettes, key=ordre_etiquettes), liste
    if zones:
        assert etiquettes and len(zones) == len(fields), stem
        g["zones"] = list(zones)
    return g


def calc(s):
    return f'<span class="calc">{s}</span>'


# ------------------------------------------------------------ étiquettes à glisser dans les cases
# La correction reste celle du moteur : tests/correction.test.js vérifie, pour chaque case, que sa bonne étiquette
# est proposée et que les autres étiquettes de sa liste sont refusées.
def ordre_etiquettes(e):
    """Ordre alphabétique, sans tenir compte de l'article ni des accents : la liste ne souffle pas la réponse."""
    sans = re.sub(r"^(le |la |les |l')", "", e.lower())
    return unicodedata.normalize("NFD", sans).encode("ascii", "ignore").decode()


def etiquette_attendue(bank, attendu):
    """Étiquette de la liste qui donne la réponse attendue, écrite dans la case du schéma corrigé : celle par laquelle
    commence la réponse affichée dans la correction, sinon celle qui en partage le plus de mots
    (tests/correction.test.js vérifie qu'elle est juste)."""
    a = re.sub(r"<[^>]+>", "", attendu).lower()

    def mots(s):
        return set(re.findall(r"\w+", s.lower()))
    return max(bank, key=lambda e: (a.startswith(e.lower()), len(mots(e) & mots(a)), -len(e)))


# ============================================================ rendu HTML
def render_q(q, part):
    """Question à une case : saisie libre, corrigée par le moteur (mots-clés, valeur et unité, oui ou non)."""
    qid, label = q["id"], q["label"]
    return f"""
        <div class="q" id="{qid}" data-q="{qid}">
          <p class="q-stem"><span class="q-num">{label}</span> <strong>{q['stem']}</strong></p>
          <p class="q-hint" id="h-{qid}">{q['hint']}</p>
          <div class="q-row">
            <input type="text" class="q-input" id="in-{qid}" aria-label="Réponse {label}" aria-describedby="h-{qid}" autocomplete="off" autocapitalize="off" spellcheck="false">
            <button type="button" class="btn btn-validate">Valider</button>
            <span class="q-status" aria-live="polite"></span>
            <span class="print-only pstat">Non validée : comptée fausse</span>
          </div>
          <p class="q-msg" role="alert"></p>
          <div class="q-expl" hidden>
            <p class="q-unit-msg" hidden></p>
            <p class="q-expected"><span>Réponse attendue :</span> {q['expected']}</p>
            <div class="q-why">{q['why']}</div>
          </div>
        </div>"""


def etiquettes(bank):
    return "".join(f'<button type="button" class="etq" draggable="true" aria-pressed="false">{esc(t)}</button>'
                   for t in bank)


def render_grp(g, part):
    """Question à plusieurs cases : structure « fast-q » du gabarit (un bouton, une correction commune).
    Chaque case garde le champ lu par le moteur (masqué) ; on la remplit en y glissant une étiquette de la liste.
    Sans liste d'étiquettes, le champ lu par le moteur est une case de saisie.
    Question posée sur un schéma (« zones ») : ses cases sont sur la figure (render_plan) ; le bloc garde les champs,
    le bouton relayé par le bandeau et la correction, et ne s'affiche qu'une fois la question corrigée."""
    gid, label = g["id"], g["label"]
    plan = bool(g.get("zones"))

    def case(fid):
        if not g.get("bank"):
            return (f'<input type="text" class="q-input" id="in-{fid}" data-q="{fid}" aria-labelledby="lb-{fid}" '
                    'autocomplete="off" autocapitalize="off" spellcheck="false">')
        if plan:
            return f'<input type="hidden" id="in-{fid}" data-q="{fid}">'
        return (f'<input type="hidden" id="in-{fid}" data-q="{fid}"><button type="button" class="dz" id="dz-{fid}" '
                f'data-bank="bk-{gid}" aria-labelledby="lb-{fid} dzv-{fid}"><span class="dz-v" id="dzv-{fid}">case vide'
                '</span></button>')
    rows = "".join(
        f'<div class="grp-l"><span class="grp-lab" id="lb-{fid}">{fl}</span><div class="sol">{case(fid)}'
        f'<span class="mark" aria-live="polite"></span></div></div>'
        for fid, (fl, _g, _e) in zip(g["fids"], g["fields"]))
    bank = ("" if plan or not g.get("bank") else f'<div class="bank" id="bk-{gid}" role="group" aria-label="Étiquettes '
            f'de la question {label}"><span class="bank-t">{g["bank_t"]}</span>{etiquettes(g["bank"])}</div>')
    sol = "".join(f"<tr><td>{fl}</td><td>{e}</td></tr>" for fl, _g, e in g["fields"])
    n = len(g["fields"])
    return f"""
        <div class="fast-q grp{' sur-plan' if plan else ''}" id="{gid}">
          <p class="q-stem"><span class="q-num">{label}</span> <strong>{g['stem']}</strong></p>
          <p class="q-hint">{g['hint']}</p>{bank}
          <div class="grp-fields" role="group" aria-label="Cases de la question {label}">{rows}</div>
          <div class="fast-foot"><button type="button" class="btn btn-fast">Valider {'les ' + str(n) + ' cases' if n > 1 else 'la case'}</button>
            <span class="q-status" aria-live="polite"></span></div>
          <p class="q-msg" role="alert"></p>
          <div class="q-expl" hidden>
            <table class="t grp-sol"><thead><tr><th>Case</th><th>Réponse attendue</th></tr></thead><tbody>{sol}</tbody></table>
            <div class="q-why"><p class="why-t">Démarche</p>{g['why']}</div>
          </div>
        </div>"""


def render_plan(p):
    """Plan de travail d'une partie : les énoncés des questions posées sur le schéma, le schéma et ses cases (boutons
    placés en pourcentage du viewBox), puis le bandeau des étiquettes et des boutons « Valider », collé au bas de
    l'écran tant que le schéma est visible. Les questions qui ont la même liste d'étiquettes la partagent."""
    pl, n = p["plan"], p["num"]
    grps = [b for b in p["blocks"] if b["kind"] == "grp" and b.get("zones")]
    listes = []
    for g in grps:
        for li in listes:
            if li["etq"] == g["bank"]:
                li["grps"].append(g)
                break
        else:
            listes.append({"etq": g["bank"], "titre": g["bank_t"], "grps": [g]})
    for i, li in enumerate(listes):
        li["id"] = f"bk-{n}-{i + 1}"
        for g in li["grps"]:
            g["bank_id"] = li["id"]
    W, H = pl["w"], pl["h"]

    def pc(v, total):
        return f"{v / total * 100:.3f}%"
    cases = []
    for g in grps:
        for fid, cle, (_fl, _g, att) in zip(g["fids"], g["zones"], g["fields"]):
            x, y, w, h, ind = pl["cases"][cle]
            cases.append(
                f'<button type="button" class="dz dz-f" id="dz-{fid}" data-bank="{g["bank_id"]}" '
                f'data-attendu="{esc(etiquette_attendue(g["bank"], att))}" style="left:{pc(x, W)};top:{pc(y, H)};'
                f'width:{pc(w, W)};height:{pc(h, H)}" aria-labelledby="lb-{fid} dzv-{fid}">'
                + (f'<span class="dz-n" aria-hidden="true">{cle}</span>' if cle.isdigit() else "") +
                f'<span class="dz-in"><span class="dz-v" id="dzv-{fid}">case vide</span>'
                + (f'<span class="dz-p" aria-hidden="true">{ind}</span>' if ind else "") +
                '<span class="dz-a" aria-hidden="true"></span></span></button>')
    enonces = "".join(f'<li><span class="q-num">{g["label"]}</span> <strong>{g["stem"]}</strong> '
                      f'<span class="plan-hint">{g["hint"]}</span></li>' for g in grps)
    banques = "".join(
        f'<div class="bank" id="{li["id"]}" role="group" aria-label="Étiquettes « {li["titre"]} » '
        f'({", ".join(g["label"] for g in li["grps"])})"><span class="bank-t">{li["titre"]}</span>'
        f'{etiquettes(li["etq"])}</div>' for li in listes)
    boutons = "".join(
        f'<button type="button" class="btn-plan" data-g="{g["id"]}" data-label="{g["label"]}" '
        f'aria-label="Valider la question {g["label"]}">{g["label"]} <small>· {len(g["fields"])} '
        f'case{"s" if len(g["fields"]) > 1 else ""}</small></button>' for g in grps)
    style = f"--u:{100 / W:.5f}cqw" + (f";max-width:{pl['maxw']}px" if pl.get("maxw") else "")
    return f"""
      <div class="plan" id="plan-{n}">
        <ol class="plan-qs">{enonces}</ol>
        <figure class="plan-fig {pl.get('cls', '')}"><div class="plan-scroll"><div class="plan-canvas" style="{style}">{pl['svg']}{''.join(cases)}</div></div>
          <figcaption>{pl['caption']}</figcaption></figure>
        <div class="plan-tray" role="group" aria-label="Étiquettes de la partie {n}">{banques}
          <div class="plan-val only-training"><span class="bank-t">Valider</span>{boutons}</div>
          <p class="plan-msg" role="status" aria-live="polite"></p></div>
      </div>"""


def render_qbar(b):
    chips = " ".join(f'<button type="button" class="doc-chip" data-doc="{d}" aria-pressed="false">{d}</button>'
                     for d in b["docs"])
    return (f'\n      <div class="qbar" role="group" aria-label="{b["label"]}"><div class="qb-num">{b["label"]}</div>'
            f'<div class="qb-docs">Documents à consulter : {chips}</div><div class="qb-ans">Répondre : {b["ans"]}</div></div>')


def item_points(b):
    return {"q": 1, "grp": len(b.get("fields", ())), "sk": len(b.get("criteria", ()))}.get(b["kind"], 0)


def part_points(p):
    return sum(item_points(b) for b in p["blocks"])


def hm(minutes):
    h, m = divmod(minutes, 60)
    return f"{h}\u00a0h\u00a0{m:02d}" if h else f"{m}\u00a0min"


HOUSE = ('<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2.3" '
         'stroke-linejoin="round" stroke-linecap="round"><path d="M3 11.5 12 4l9 7.5"/>'
         '<path d="M5.5 9.8V20h4.5v-5.5h4V20h4.5V9.8"/></svg>')

QLABEL = {}
CUR = {"total": 1}


def pct(minutes):
    return fr(minutes / CUR["total"] * 100, 1)


def render_part(p):
    pts = part_points(p)
    body = "\n      ".join(p["intro"])
    blocks = []
    premiere = next((b["id"] for b in p["blocks"] if b.get("zones")), None)
    for b in p["blocks"]:
        if b.get("id") and b["id"] == premiere:  # le schéma à compléter précède la première question posée sur lui
            blocks.append(render_plan(p))
        if b["kind"] == "q":
            blocks.append(render_q(b, p))
        elif b["kind"] == "grp" and b.get("qcm"):
            blocks.append(qcm.render_qcm(b, AIDES_QCM))
        elif b["kind"] == "grp":
            blocks.append(render_grp(b, p))
        elif b["kind"] == "qbar":
            blocks.append(render_qbar(b))
        else:
            blocks.append(b["html"])
    n = p["num"]
    return f"""
  <section class="part" id="partie-{n}" aria-labelledby="t-partie-{n}">
    <header class="part-head"><div class="part-num" aria-hidden="true">{n}</div>
      <div><h2 id="t-partie-{n}"><span class="sr-only">Partie {n} : </span>{p['title']}</h2>
        <div class="duree">Durée conseillée : {hm(p['minutes'])} · Barème : {pts} points, soit {pct(p['minutes'])} % de la note</div></div></header>
    <div class="part-body">
      {body}{''.join(blocks)}
    </div>
  </section>"""


def prepare_exo(e):
    """Copie et numérote les parties d'un exercice (Q1.1, Q1.2…) ; calcule sa configuration pour les moteurs."""
    parts = copy.deepcopy(e["parts"])
    for i, p in enumerate(parts):
        p["num"] = str(i + 1)
        k = 0
        for b in p["blocks"]:
            if b["kind"] in ("q", "grp"):
                k += 1
                b["id"] = f"{e['prefix']}{p['num']}_{k}"
                b["label"] = f"Q{p['num']}.{k}"
                QLABEL[b["id"]] = b["label"]
                if b["kind"] == "grp":
                    b["fids"] = [f"{b['id']}_{j + 1}" for j in range(len(b["fields"]))]
                if b.get("zones"):  # cases posées sur le schéma de la partie
                    assert "plan" in p and all(z in p["plan"]["cases"] for z in b["zones"]), (e["key"], b["stem"])
        # figures qui suivent la correction d'une partie (le RAV4 du dépôt Chaîne fonctionnelle) : identifiants de
        # ses questions
        grp_ids = " ".join(b["id"] for b in p["blocks"] if b["kind"] in ("q", "grp"))
        p["intro"] = [x.replace("__GRP__", grp_ids) for x in p.get("intro", [])]
        # la barre de documents prend le numéro de la question qui la suit
        for j, b in enumerate(p["blocks"]):
            if b["kind"] == "qbar":
                nxt = next((x for x in p["blocks"][j + 1:] if x["kind"] in ("q", "grp")), None)
                b["label"] = nxt["label"] if nxt else f"Partie {p['num']}"
    e["P"] = parts
    e["minutes"] = sum(p["minutes"] for p in parts)
    e["n_q"] = sum(1 for p in parts for b in p["blocks"] if b["kind"] in ("q", "grp"))
    e["n_cases"] = sum(item_points(b) for p in parts for b in p["blocks"] if b["kind"] in ("q", "grp"))
    e["points"] = sum(part_points(p) for p in parts)
    qcfg, parts_cfg = {}, []
    for p in parts:
        parts_cfg.append({"num": p["num"], "title": p["title"], "minutes": p["minutes"],
                          "duration": hm(p["minutes"]), "points": part_points(p)})
        for b in p["blocks"]:
            if b["kind"] == "q":
                qcfg[b["id"]] = {"label": b["label"], "part": p["num"], "pts": 1, "grader": b["grader"]}
            elif b["kind"] == "grp":
                for fid, (fl, g, _x) in zip(b["fids"], b["fields"]):
                    qcfg[fid] = {"label": f"{b['label']} — {re.sub(r'<[^>]+>', '', fl)}", "part": p["num"],
                                 "pts": 1, "grader": g}
    np_ = len(parts)
    e["cfg"] = {"title": e["title"], "minutes": e["minutes"], "duree": hm(e["minutes"]),
                "cartouche": f"{e['n_q']} questions" + ("" if e.get("qcm") else f", {e['n_cases']} cases notées") +
                             f", réparties en {np_} partie"
                             f"{'s' if np_ > 1 else ''} pondérée{'s' if np_ > 1 else ''} par leur durée.",
                "parts": parts_cfg, "qcfg": qcfg, "skcfg": {}}


def render_docs(e):
    rail, tabs, secs = [], [], []
    first_dt = True
    for key, title, kind, is_dt, content in sorted((d for d in DOCS if d[0] in e["docs"]),
                                                   key=lambda d: (d[3], d[0])):
        if is_dt and first_dt:
            rail.append('<div class="grp" aria-hidden="true"></div>')
            first_dt = False
        cls = "tab dt" if is_dt else "tab"
        rail.append(f'<button type="button" class="{cls}" data-doc="{key}" aria-selected="false" title="{esc(title)}">{key}</button>')
        tabs.append(f'<button type="button" data-doc="{key}" aria-selected="false">{key}</button>')
        secs.append(f'<section class="doc" id="doc-{key}" data-title="{key} : {esc(title)}" data-kind="{kind}">{content}\n</section>')
    return "".join(rail), "".join(tabs), "\n".join(secs)


def pastille(level):
    if not level:
        return ""
    return f' <span class="pastille n{level.split()[-1]}">{level}</span>'


def render_exo_home(e):
    src, w, h = image(e["hero"][0])
    docs = sorted(e["docs"], key=lambda k: (k[:2] != "DP", k))
    docs_txt = (", ".join(docs[:-1]) + " et " + docs[-1]) if len(docs) > 1 else (docs[0] if docs else "")
    facts = ('<div class="home-facts">'
             f'<div><b>{len(e["P"])} parties</b><span>{e["n_q"]} questions</span></div>'
             f'<div><b>{hm(e["minutes"])}</b><span>durée conseillée</span></div>' +
             (f'<div><b>{len(docs)} documents</b><span>{docs_txt}</span></div>' if docs else
              '<div><b>Une réponse</b><span>ou plusieurs, à choisir</span></div>') +
             (f'<div><b>{e["n_q"]} points</b><span>un par question</span></div></div>' if e.get("qcm") else
              f'<div><b>{e["n_cases"]} cases</b><span>un point chacune</span></div></div>'))
    return (f'<div class="home-top"><div class="home-top-l"><header class="home-head"><span class="mc-tag">{e["tag"]}</span>{pastille(e.get("level"))}'
            f'<h1 id="home-title">{e["title"]}</h1><p class="home-sub">{e["sub"]}</p></header>{facts}</div>'
            f'<figure class="home-hero"><img src="{src}" alt="{esc(e["hero"][1])}" width="{w}" height="{h}">'
            f'<figcaption class="small">{e["hero"][2]}</figcaption></figure></div>')


MODES_HTML = """<h2 class="home-choose">Choisis ton mode de travail</h2>
<div class="modes">
  <article class="mode-card">
    <div class="mc-head"><span class="mc-tag">Mode 1</span><h3>Mode entraînement</h3></div>
    <p class="mc-lead">Pour apprendre en avançant, question par question.</p>
    <ul><li>Chaque question se valide isolément ; la démarche corrigée s'affiche aussitôt.</li>
      <li>La note pondérée s'actualise en continu dans le bandeau.</li>
      <li>Les documents et le chronomètre restent disponibles, sans contrainte de temps.</li></ul>
    <button type="button" class="btn btn-mode" data-mode="training">Commencer l'entraînement</button>
  </article>
  <article class="mode-card exam">
    <div class="mc-head"><span class="mc-tag">Mode 2</span><h3>Mode examen</h3></div>
    <p class="mc-lead">Pour se placer dans les conditions d'une évaluation.</p>
    <ul><li>Aucune correction et aucune note pendant la composition ; les réponses restent modifiables.</li>
      <li>Le chronomètre tourne, à comparer à la durée conseillée.</li>
      <li>En fin de sujet, le bouton « J'ai fini, je fais corriger ma copie » dévoile d'un coup les corrections, les notes par partie et la note globale.</li></ul>
    <button type="button" class="btn btn-mode" data-mode="exam">Composer en mode examen</button>
  </article>
</div>
<p class="home-note small">Le mode se choisit une seule fois : pour en changer, reviens à l'accueil (onglet maison) et rouvre l'exercice. Rien n'est enregistré sur l'ordinateur.</p>
<p class="home-back"><a class="btn ghost" href="?">""" + HOUSE + """ Retour à l'accueil</a></p>"""

# Consignes d'un exercice : on assemble les paragraphes utiles (modes, sorte de réponses, documents, barème).
CONSIGNES_MODES = """<p class="only-training"><strong>Mode entraînement.</strong> Remplis les cases d'une question puis clique sur « Valider » : une réponse validée est définitive et sa correction s'affiche aussitôt.</p>
    <p class="only-exam"><strong>Mode examen.</strong> Compose tout le sujet sans correction ni note : tes réponses restent modifiables jusqu'au bout. Le bouton « J'ai fini, je fais corriger ma copie », en fin de sujet, dévoile d'un coup les corrections, les notes par partie et la note globale.</p>"""
CONSIGNES_SAISIE = """
    <p><strong>Réponses à écrire.</strong> Écris ta réponse dans la case, puis valide avec le bouton ou la touche Entrée. Pour un calcul, donne la valeur et son unité : une valeur juste sans son unité, ou avec une autre, ne vaut qu'un demi-point.</p>"""
CONSIGNES_ETIQUETTES = """
    <p><strong>Des étiquettes à glisser.</strong> <strong>Glisse</strong> une étiquette sur une case, ou <strong>touche</strong> une étiquette (les cases qui l'acceptent s'éclairent) puis la case ; au clavier : Entrée sur l'étiquette, puis Entrée sur la case. Une étiquette peut servir plusieurs fois, certaines ne servent pas. Pour vider une case, touche-la ou ramène son étiquette dans la liste. Quand les cases sont posées sur un schéma, les étiquettes et les boutons « Valider » sont dans le bandeau sous le schéma, qui reste à l'écran pendant que tu fais défiler la figure.</p>
    <p><strong>Une question, plusieurs cases.</strong> Les cases d'une même question se valident ensemble ; chaque case vaut un point.</p>"""
CONSIGNES_DOCS = """
    <p>Le dossier de présentation (DP) et le dossier technique (DT) s'ouvrent avec les onglets sur le bord droit, ou avec les boutons des en-têtes de question.</p>"""
CONSIGNES_BAREME = """
    <p><strong>Barème pondéré par la durée conseillée</strong> : chaque partie est notée sur 20, puis pèse au prorata de son temps. Le récapitulatif de fin de sujet donne le détail partie par partie.</p>"""


# ============================================================ DOCUMENTS (dossiers de présentation et techniques)
# (clé, titre, nature, dossier technique ?, contenu HTML) ; un exercice cite les clés de ses documents dans "docs".
# Exemple dans le dépôt « Chaîne fonctionnelle » : DOCS (DP1, DT1).
DOCS = [
]


# ============================================================ EXERCICES ET ÉTUDES (accueil et configuration)
# Ajouter un exercice : décrire ses parties, puis l'ajouter ici ; "etude": True le range dans la rubrique « Études de
# cas ». La carte apparaît d'elle-même sur l'accueil (et remplace l'annonce « En cours d'édition »). Modèle :
#   {"key": "isolation-paroi", "prefix": "a", "tag": "Exercice 1.1", "level": "Niveau 1",
#    "title": "…", "sub": "phrase de présentation", "parts": [{"title": …, "minutes": …, "intro": […], "blocks": […]}],
#    "docs": ["DP1"], "consignes": CONSIGNES_MODES + CONSIGNES_SAISIE + CONSIGNES_DOCS + CONSIGNES_BAREME,
#    "hero": ("image", "texte alternatif", "légende"), "mots": [3 à 5 mots-clés], "vign": "carte-…", "valt": "…"}
# QCM : "qcm": True, "parts": [qcm.partie(…), …], "consignes": qcm.CONSIGNES. Le préfixe (une lettre, propre à
# chaque exercice) précède les identifiants des cases (a1_2 : partie 1, question 2) ; les réponses de référence
# de chaque case sont dans tests/reponses.js.
EXO_DEFS = [
]


# ============================================================ ACCUEIL
# Cartes de l'accueil : une vignette (src/images/carte-*, outils/preparer-images.sh) et 3 à 5 mots-clés, sans texte.
# Un cours : {"key": "cours-…" (le préfixe « cours- » est exigé par l'aiguillage), "tag": "Cours 1", "level":
# "Niveau 1", "title": …, "mots": […], "vign": "carte-cours-1", "alt": …, "render": fonction qui rend le cours
# (HTML), et, s'il est interactif, "js" (script qui définit sa fonction d'initialisation), "init" (son nom), "css"}.
COURS = [
    {"key": "cours-habitat-durable", "tag": "Cours 1", "level": "Niveau 1", "title": "Habitat durable : maison performante",
     "mots": ["Bioclimatique", "Isolation", "Ventilation", "Énergies renouvelables", "RE2020"], "vign": "carte-cours-1",
     "alt": "Maison en coupe équipée d'une VMC double flux",
     "render": lambda: cours_habitat.render(AIDES_COURS), "js": cours_habitat.hd_js(), "init": "initCoursHabitat",
     "css": cours_habitat.HD_CSS},
]
# Pages annexes (formulaire, fiches…) : {"rubrique": "ressources" ou "exercices", "tag", "title", "href", "bouton",
# "mots", "vign", "alt"} ; la rubrique « Les ressources » n'apparaît que si elle a une carte.
LIENS = [
]
# Rubriques encore vides : une carte « En cours d'édition » les annonce (étiquette, titre, mots-clés).
COURS_A_VENIR = ("Cours 1", "Premier cours", ["Notions", "Animations", "Jeux", "Quiz"])
EXO_A_VENIR = ("Exercice 1.1", "Premier exercice", ["Entraînement", "Examen", "Note sur 20"])
ETUDE_A_VENIR = ("Étude 1", "Étude de cas", ["Bâtiment réel", "Plusieurs notions", "Choix argumentés"])
OUVRIR = ("Ouvrir l'exercice", "Ouvrir l'étude")


def carte(tag, title, mots, href, bouton, vign=None, alt="", cls=""):
    """Carte de l'accueil : vignette, étiquette, titre, mots-clés, bouton."""
    img = '<div class="cv-img cv-vide" aria-hidden="true"></div>'
    if vign:  # images des cartes : src/images/carte-*, tirées des exercices (outils/preparer-images.sh)
        src, w, h = image(vign)
        img = f'<img class="cv-img" src="{src}" alt="{esc(alt)}" width="{w}" height="{h}" loading="lazy">'
    mots_html = '<ul class="cv-mots">' + "".join(f"<li>{m}</li>" for m in mots) + "</ul>"
    btn = f'<a class="btn" href="{href}">{bouton}</a>' if href else '<p class="small ex-meta etat">En cours d\'édition</p>'
    return (f'<article class="mode-card carte-v {cls}">{img}<div class="mc-head"><span class="mc-tag">{tag}</span>'
            f"<h3>{title}</h3></div>{mots_html}{btn}</article>")


def _exo_card(e):
    return carte(e["tag"] + pastille(e.get("level")), e["title"], e["mots"], f'?ex={e["key"]}',
                 OUVRIR[bool(e.get("etude"))], e["vign"], e["valt"])


def _lien_card(c):
    return carte(c["tag"], c["title"], c["mots"], c["href"], c["bouton"], c["vign"], c["alt"])


def a_venir(tag, title, mots):
    return carte(tag, title, mots, None, None, None, "", "en-edition")


def render_hub():
    src, w, h = image("accueil")
    cours = "".join(carte(c["tag"] + pastille(c.get("level")), c["title"], c["mots"], f'?ex={c["key"]}', "Lire le cours",
                          c["vign"], c["alt"], "cours-card") for c in COURS) or a_venir(*COURS_A_VENIR)
    ressources = "".join(_lien_card(c) for c in LIENS if c["rubrique"] == "ressources")
    cards = ("".join(_exo_card(e) for e in EXO_DEFS if not e.get("etude")) +
             "".join(_lien_card(c) for c in LIENS if c["rubrique"] == "exercices")) or a_venir(*EXO_A_VENIR)
    etudes = "".join(_exo_card(e) for e in EXO_DEFS if e.get("etude")) or a_venir(*ETUDE_A_VENIR)
    return (f'<div class="home-top"><div class="home-top-l"><header class="home-head"><h1 id="home-title">{TITRE}</h1>'
            "<p class=\"home-sub\">Concevoir, rénover et habiter un logement qui consomme peu d'énergie, en produit une "
            "partie, économise l'eau et choisit ses matériaux. Des cours, des exercices et des études de cas "
            "interactifs, à faire en mode entraînement ou en mode examen.</p></header></div>"
            f'<figure class="home-hero"><img src="{src}" alt="Maison dessinée : panneaux solaires sur le toit, murs '
            f"isolés par l'extérieur, arbre qui l'ombrage et cuve de récupération de l'eau de pluie\" "
            f'width="{w}" height="{h}">'
            "<figcaption class=\"small\">Quelques leviers d'un habitat durable.</figcaption></figure></div>"
            f'<h2 class="home-choose">Les cours</h2><div class="ex-grid cours-grid">{cours}</div>' +
            (f'<h2 class="home-choose">Les ressources</h2><div class="ex-grid form-grid">{ressources}</div>'
             if ressources else "") +
            f'<h2 class="home-choose">Les exercices</h2><div class="ex-grid exo-grid">{cards}</div>'
            f'<h2 class="home-choose">Études de cas</h2><div class="ex-grid etude-grid">{etudes}</div>'
            f'<p class="home-note small">Pastilles : {pastille("Niveau 1").strip()} premier niveau, '
            f'{pastille("Niveau 2").strip()} niveau approfondi. Les études de cas reprendront des bâtiments réels et '
            "mobiliseront plusieurs notions. Chaque exercice propose le mode entraînement (correction question par "
            "question) ou le mode examen (correction à la remise de la copie). Rien n'est enregistré sur "
            "l'ordinateur.</p>")


def course_head(tag, level, title, sub):
    return (f'<div class="home-top home-top-single"><div class="home-top-l"><header class="home-head">'
            f'<span class="mc-tag">{tag}</span>{pastille(level)}<h1 id="home-title">{title}</h1>'
            f'<p class="home-sub">{sub}</p></header></div></div>')


def course_section(n, ident, titre, body):
    return (f'<section class="part cours-sec" id="{ident}" aria-labelledby="{ident}-t"><header class="part-head">'
            f'<div class="part-num" aria-hidden="true">{n}</div><div><h2 id="{ident}-t" style="padding:14px 16px">{titre}'
            f'</h2></div></header><div class="part-body">{body}</div></section>')


def course_nav(items):
    return ('<nav class="cours-nav no-print" aria-label="Étapes du cours">' +
            "".join(f'<a href="#{a}">{n}. {t}</a>' for n, (a, t) in enumerate(items, 1)) + "</nav>")


def quiz_html(questions, name):
    """Quiz noté (moteur initQuiz) : questions = [(énoncé, [choix], indice juste, explication)]."""
    return "".join(
        f'<fieldset class="quiz-q" data-ok="{ok}"><legend><span class="q-num">{i + 1}</span> {q}</legend>' +
        "".join(f'<label><input type="radio" name="{name}{i}" value="{j}"> {o}</label>' for j, o in enumerate(opts)) +
        f'<p class="quiz-fb" aria-live="polite"></p><p class="quiz-why" hidden>{why}</p></fieldset>'
        for i, (q, opts, ok, why) in enumerate(questions))


def quiz_section(n, ident, questions, name):
    return course_section(n, ident, "Quiz : vérifie tes connaissances",
                          f'<p>Choisis une réponse : la correction s\'affiche aussitôt.</p><div class="quiz">'
                          f'{quiz_html(questions, name)}</div><div class="quiz-score" aria-live="polite">'
                          f'<span id="qz-score">0 / {len(questions)}</span><span id="qz-stars" aria-hidden="true"></span>'
                          '<button type="button" class="btn ghost" id="qz-reset">Recommencer</button></div>')


def jeu_html(lignes, choix, ident):
    """Jeu de classement : chaque ligne (libellé, clé juste) propose les mêmes boutons (clé, texte)."""
    rows = "".join(
        f'<div class="jeu-l" data-ok="{ok}"><span>{t}</span>' +
        "".join(f'<button type="button" class="btn ghost" data-v="{k}">{n}</button>' for k, n in choix) +
        '<b class="jeu-fb" aria-live="polite"></b></div>' for t, ok in lignes)
    return (f'<div class="jeu" id="{ident}">{rows}<p class="jeu-score" aria-live="polite">Score : '
            f'<span class="jeu-s">0 / {len(lignes)}</span> <button type="button" class="btn ghost jeu-reset">'
            'Recommencer</button></p></div>')


# ============================================================ COURS — éléments communs (quiz, jeux, cartes)
COURS_COMMUN_JS = r"""
  function initQuiz(root) {
    function q(s) { return root.querySelector(s); }
    function qa(s) { return Array.prototype.slice.call(root.querySelectorAll(s)); }
    var qs = qa(".quiz-q");
    function score() {
      var n = qs.filter(function (f) { return f.classList.contains("is-ok"); }).length;
      var done = qs.filter(function (f) { return f.classList.contains("done"); }).length;
      var st = n === qs.length ? 3 : n >= qs.length - 2 ? 2 : n >= 2 ? 1 : 0;
      q("#qz-score").textContent = n + " / " + qs.length;
      q("#qz-stars").textContent = done === qs.length ? "★★★".slice(0, st) + "☆☆☆".slice(0, 3 - st) : "";
    }
    qs.forEach(function (fs) {
      fs.addEventListener("change", function (e) {
        if (fs.classList.contains("done")) return;
        var ok = e.target.value === fs.getAttribute("data-ok");
        fs.classList.add("done", ok ? "is-ok" : "is-ko");
        fs.querySelector(".quiz-fb").textContent = ok ? "✔ Bonne réponse !" : "✘ Pas tout à fait.";
        fs.querySelector(".quiz-why").hidden = false;
        Array.prototype.forEach.call(fs.querySelectorAll("input"), function (i) {
          i.disabled = true;
          if (i.value === fs.getAttribute("data-ok")) i.parentNode.classList.add("good");
        });
        score();
      });
    });
    q("#qz-reset").addEventListener("click", function () {
      qs.forEach(function (fs) {
        fs.classList.remove("done", "is-ok", "is-ko");
        fs.querySelector(".quiz-fb").textContent = "";
        fs.querySelector(".quiz-why").hidden = true;
        Array.prototype.forEach.call(fs.querySelectorAll("input"), function (i) { i.disabled = false; i.checked = false; i.parentNode.classList.remove("good"); });
      });
      score();
    });
    score();
  }
  // jeu de classement : un clic par ligne, le bon bouton est montré en cas d'erreur
  function initJeu(box) {
    var lignes = Array.prototype.slice.call(box.querySelectorAll(".jeu-l"));
    function score() {
      box.querySelector(".jeu-s").textContent = lignes.filter(function (l) { return l.classList.contains("is-ok"); }).length + " / " + lignes.length;
    }
    lignes.forEach(function (l) {
      Array.prototype.forEach.call(l.querySelectorAll("button"), function (b) {
        b.addEventListener("click", function () {
          if (l.classList.contains("is-ok") || l.classList.contains("is-ko")) return;
          var good = l.getAttribute("data-ok"), ok = b.getAttribute("data-v") === good;
          l.classList.add(ok ? "is-ok" : "is-ko");
          b.classList.add(ok ? "pick-ok" : "pick-ko");
          if (!ok) l.querySelector('button[data-v="' + good + '"]').classList.add("pick-good");
          l.querySelector(".jeu-fb").textContent = ok ? "✔" : "✘";
          score();
        });
      });
    });
    box.querySelector(".jeu-reset").addEventListener("click", function () {
      lignes.forEach(function (l) {
        l.classList.remove("is-ok", "is-ko");
        l.querySelector(".jeu-fb").textContent = "";
        Array.prototype.forEach.call(l.querySelectorAll("button"), function (b) { b.classList.remove("pick-ok", "pick-ko", "pick-good"); });
      });
      score();
    });
    score();
  }
  // cartes à retourner
  function initCartes(root) {
    Array.prototype.forEach.call(root.querySelectorAll(".carte"), function (b) {
      b.addEventListener("click", function () { b.setAttribute("aria-expanded", b.getAttribute("aria-expanded") === "true" ? "false" : "true"); });
    });
  }
  function fr(x, d) { return x.toLocaleString("fr-FR", { minimumFractionDigits: d, maximumFractionDigits: d }).replace(/^-/, "−"); }
"""

COURS_COMMUN_CSS = """
/* ---------- cours interactifs (repris du dépôt RDM) ---------- */
.cours .part{margin-bottom:22px}
.cours-nav{display:flex; flex-wrap:wrap; gap:6px; margin:0 0 16px}
.cours-nav a{font:600 .92rem var(--f-titre); color:var(--encre); background:var(--papier); border:1.5px solid var(--encre); padding:5px 12px; text-decoration:none}
.cours-nav a:hover{background:var(--jaune-pale)}
.cours-defi{font-weight:700; color:var(--bleu)}
.cours .part-body h3{font:700 1.12rem var(--f-titre); margin:18px 0 6px}
.formule{display:flex; flex-wrap:wrap; gap:14px 28px; align-items:center; border:2px solid var(--rouge); background:#fff; padding:10px 18px; margin:12px 0; max-width:680px}
.formule .f-main{font:700 1.5rem var(--f-titre); line-height:2}
.formule .f-units{font-size:.9rem; color:var(--encre-2)}
.simu{border:2px solid var(--bleu); background:var(--bleu-pale); padding:12px 16px; margin:14px 0}
.simu h3{margin:0 0 8px!important; font:700 1.15rem var(--f-titre); color:var(--bleu)}
.simu-grid{display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:10px 18px}
@media (max-width:640px){ .simu-grid{grid-template-columns:1fr} }
.simu-grid label{display:flex; flex-direction:column; gap:4px; font-weight:600; font-size:.92rem}
.simu-grid output{font:700 1rem var(--f-titre); color:var(--bleu)}
.simu-grid input[type=range]{width:100%; accent-color:var(--bleu)}
.simu-grid select{padding:5px; border:1.5px solid var(--encre-2); background:#fff; font:inherit}
.simu-out{display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:8px; margin:12px 0 8px}
.simu-out div{background:var(--encre); color:#fff; padding:6px 10px}
.simu-out span{display:block; font-size:.78rem; color:#D7DDE2}
.simu-out b{font:700 1.1rem var(--f-titre); color:var(--jaune)}
.simu-out4{grid-template-columns:repeat(4,minmax(0,1fr))}
@media (max-width:760px){ .simu-out,.simu-out4{grid-template-columns:repeat(2,minmax(0,1fr))} }
.simu-verdict{font-weight:700; margin:8px 0 4px}
.simu-verdict.ok{color:var(--vert)} .simu-verdict.ko{color:var(--rouge)}
.simu-defi{margin-top:8px; background:#fff; border:1px dashed var(--bleu); padding:6px 10px}
.simu-defi summary{cursor:pointer; font-weight:600}
.exemple{background:#F6F7F4; border:1px solid var(--trait-fin); padding:6px 16px; margin-top:12px}
.exemple h3{font:700 1.05rem var(--f-titre); margin:10px 0 4px}
.remarque{border-left:6px solid var(--jaune); background:var(--jaune-pale); padding:8px 14px; margin:12px 0; max-width:80ch}
.remarque p{margin:.2rem 0}
.quiz{display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:12px}
.quiz-q{border:1.5px solid var(--encre); background:#fff; padding:8px 14px 10px; margin:0}
.quiz-q legend{font-weight:700; padding:0 4px}
.quiz-q label{display:block; padding:3px 0; cursor:pointer}
.quiz-q.is-ok{border-color:var(--vert); background:var(--vert-pale)}
.quiz-q.is-ko{border-color:var(--rouge); background:var(--rouge-pale)}
.quiz-q label.good{font-weight:700; color:var(--vert)}
.quiz-fb{margin:4px 0 0; font-weight:700}
.quiz-q.is-ok .quiz-fb{color:var(--vert)} .quiz-q.is-ko .quiz-fb{color:var(--rouge)}
.quiz-why{margin:2px 0 0; font-size:.9rem}
.quiz-score{display:flex; align-items:center; gap:14px; margin:14px 0 0; font:700 1.3rem var(--f-titre)}
#qz-stars{color:var(--jaune); font-size:1.6rem; letter-spacing:2px}
.jeu{border:2px solid var(--encre); background:#fff; padding:10px 14px; margin:12px 0 0}
.jeu-l{display:flex; flex-wrap:wrap; gap:6px 8px; align-items:center; padding:6px 0; border-top:1px solid var(--trait-fin)}
.jeu-l>span{flex:1 1 240px; font-weight:600}
.jeu-l .btn{padding:4px 9px; font-size:.88rem}
.jeu-l .btn.pick-ok{background:var(--vert); border-color:var(--vert); color:#fff}
.jeu-l .btn.pick-ko{background:var(--rouge); border-color:var(--rouge); color:#fff}
.jeu-l .btn.pick-good{outline:3px solid var(--vert); outline-offset:1px}
.jeu-l.is-ok{background:var(--vert-pale)} .jeu-l.is-ko{background:var(--rouge-pale)}
.jeu-fb{min-width:1.5em; font-size:1.1rem} .jeu-l.is-ok .jeu-fb{color:var(--vert)} .jeu-l.is-ko .jeu-fb{color:var(--rouge)}
.jeu-score{display:flex; align-items:center; gap:12px; font:700 1.2rem var(--f-titre); margin:8px 0 0}
.jeu-score .btn{font-size:.9rem; padding:5px 12px}
.cartes{display:grid; grid-template-columns:repeat(auto-fill,minmax(220px,1fr)); gap:12px; margin:8px 0 14px}
.carte{display:flex; flex-direction:column; gap:6px; align-items:flex-start; text-align:left; min-height:96px; padding:12px 14px; border:2px solid var(--encre); border-left-width:8px; background:var(--jaune-pale); font:inherit; cursor:pointer}
.carte.c-info{border-left-color:var(--bleu)} .carte.c-ener{border-left-color:var(--orange)}
.carte b{font:700 1.15rem var(--f-titre); letter-spacing:.03em}
.carte.c-info b{color:var(--bleu)} .carte.c-ener b{color:var(--orange)}
.carte .dos{display:none; font-size:.93rem}
.carte .dos i{display:block; margin-top:4px; font-style:normal; color:var(--encre-2)}
.carte[aria-expanded="true"]{background:#fff}
.carte[aria-expanded="true"] .dos{display:block}
.carte[aria-expanded="false"]::after{content:"Clique pour retourner"; font-size:.8rem; color:var(--encre-2)}
.cours-foot{display:flex; flex-wrap:wrap; gap:10px; margin:6px 0 0}
.cours-foot .small{align-self:center}
@media print{
  body.cours-page #home{display:block!important; padding:0}
  .no-print,.cours-nav,.cours-foot{display:none!important}
  .quiz-why[hidden]{display:block!important}
  .carte .dos{display:block!important}
  .carte::after{display:none!important}
}
"""


# ============================================================ COURS — assemblage
# le QCM reçoit les fonctions d'images du générateur
AIDES_QCM = types.SimpleNamespace(png=png, jpg=jpg, image=image, IMAGES=IMAGES)

# un cours peut vivre dans son propre module (src/cours_….py) ; il reçoit les éléments communs des cours
AIDES_COURS = types.SimpleNamespace(course_head=course_head, course_section=course_section, course_nav=course_nav,
                                    quiz_section=quiz_section, jeu_html=jeu_html, HOUSE=HOUSE, figure=figure,
                                    photo=photo, image=image, esc=esc, fr=fr, frac=frac)
COURS_JS = (COURS_COMMUN_JS + "".join(c.get("js", "") for c in COURS) +
            "\n  var INIT = { " + ", ".join(f'"{c["key"]}": {c["init"]}' for c in COURS if c.get("init")) + " };\n")
COURS_CSS = COURS_COMMUN_CSS + "".join(c.get("css", "") for c in COURS)


# ============================================================ AIGUILLAGE
ROUTER_JS = r"""<script>/* Aiguillage : accueil, cours ou exercice selon ?ex=… — s'exécute avant les moteurs du gabarit */
(function () {
  "use strict";
  var EXOS = window.__EXOS__, ex = new URLSearchParams(location.search).get("ex") || "";
  function $(s) { return document.querySelector(s); }
  function tpl(id) { return document.getElementById(id).innerHTML; }__COURS_JS__
  var home = $("#home .home-inner");
  window.__PARTS__ = []; window.__QCFG__ = {}; window.__SKCFG__ = {}; window.__CONSEIL_MIN__ = 0;
  if (Object.prototype.hasOwnProperty.call(EXOS, ex)) {
    var E = EXOS[ex];
    window.__PARTS__ = E.parts; window.__QCFG__ = E.qcfg; window.__SKCFG__ = E.skcfg;
    window.__CONSEIL_MIN__ = E.minutes;
    document.title = E.title + " — __TITRE__ — exercice interactif";
    document.body.classList.add("exo-" + ex);
    $(".rail").innerHTML = tpl("tpl-rail-" + ex) + '<div class="grp" aria-hidden="true"></div>' +
      '<a class="tab tab-home" href="?" title="Retour à l\'accueil" aria-label="Retour à l\'accueil">__HOUSE__</a>';
    $(".dp-tabs").innerHTML = tpl("tpl-tabs-" + ex);
    $(".dp-body").innerHTML = tpl("tpl-docs-" + ex);
    $("#parts").innerHTML = tpl("tpl-parts-" + ex);
    $(".consignes").innerHTML = tpl("tpl-consignes-" + ex);
    home.innerHTML = tpl("tpl-home-" + ex) + tpl("tpl-modes");
    $(".cartouche h1").textContent = E.title;
    $(".cartouche .title p").textContent = E.cartouche;
    Array.prototype.forEach.call(document.querySelectorAll(".print-conseil"), function (el) { el.textContent = E.duree; });
  } else {
    document.body.classList.add("hub");
    var page = document.getElementById("tpl-" + ex) && /^cours-/.test(ex) ? "tpl-" + ex : "tpl-hub";
    home.innerHTML = tpl(page);
    if (page !== "tpl-hub") {
      document.body.classList.add("cours-page", "page-" + ex);
      if (typeof INIT[ex] === "function") INIT[ex](home);
      document.title = home.querySelector("h1").textContent + " — cours — __TITRE__";
    } else document.title = "__TITRE__ — cours et exercices interactifs";
  }
})();
</script>"""


CONTENT_CSS = """<style>
/* ---------- compléments de contenu (hors gabarit) : écriture des calculs, documents ---------- */
.eq{margin:.35rem 0 .55rem; overflow-x:auto; line-height:2.1}
.frac{display:inline-flex; flex-direction:column; vertical-align:middle; text-align:center; margin:0 .12em; line-height:1.25}
.frac>span{padding:0 .25em; white-space:nowrap}
.frac>span:first-child{border-bottom:1px solid currentColor}
.doc-text ol,.doc-text ul{padding-left:1.2rem}
.doc-text li{margin:.2rem 0}
.dp-svg{display:block; width:100%; height:auto; background:#fff; border:1px solid var(--trait-fin); margin:10px 0; font-family:var(--f-texte)}
.doc-text tr.dt-i td:first-child{border-left:5px solid var(--bleu)}
.doc-text tr.dt-e td:first-child{border-left:5px solid var(--orange)}
.calc{display:inline-block; font:600 .9rem ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; background:#fff; border:1px solid var(--trait); padding:2px 8px; margin:2px 0}
.cours-split{display:flex; gap:18px; align-items:flex-start; flex-wrap:wrap}
.cours-split>div{flex:1 1 300px}
.cours-split>.fig{flex:0 1 auto; margin:0 auto}
.part-body .fig{margin:14px auto}

/* ---------- questions à plusieurs cases (mécanisme « fast-q » du gabarit) ---------- */
.grp{margin:14px 0 6px; padding:10px 0 12px 14px; border-left:3px solid var(--trait-fin)}
.grp-fields{display:flex; flex-direction:column; gap:6px; margin:8px 0 4px; max-width:820px}
.grp-l{display:grid; grid-template-columns:minmax(150px,.9fr) minmax(0,1.3fr); gap:4px 14px; align-items:center; padding:2px 0; border-bottom:1px dashed var(--trait-fin)}
.grp-lab{font-size:.95rem}
.grp .sol{display:flex; align-items:center; gap:8px}
/* étiquettes à glisser (ou toucher puis toucher la case) ; le champ lu par le moteur est masqué */
.bank{display:flex; flex-wrap:wrap; align-items:center; gap:6px; margin:8px 0 10px; padding:8px 10px; background:var(--bleu-pale); border:1px solid var(--trait-fin); max-width:820px}
.bank-t{font:700 .78rem var(--f-titre); text-transform:uppercase; letter-spacing:.04em; color:var(--encre-2); margin-right:4px}
.etq{font:600 .9rem var(--f-texte); color:var(--encre); background:#fff; border:1.5px solid var(--bleu); border-radius:3px; padding:5px 10px; cursor:grab; touch-action:manipulation; user-select:none}
.etq:hover{background:#EAF1FA}
.etq:focus-visible,.dz:focus-visible{outline:3px solid var(--jaune); outline-offset:1px}
.etq[aria-pressed="true"]{background:var(--bleu); color:#fff}
.etq.is-drag{opacity:.45}
.etq:disabled{cursor:default; opacity:.5; background:#fff; color:var(--encre)}
.dz{flex:1 1 auto; min-width:0; min-height:40px; text-align:left; font:600 .95rem var(--f-texte); color:var(--encre); background:#fff; border:1.5px dashed var(--encre-2); border-radius:3px; padding:7px 10px; cursor:pointer}
.dz .dz-v{display:block}
.dz:not(.filled) .dz-v{font-weight:400; font-style:italic; color:#7A848C}
.dz.filled{border-style:solid; border-color:var(--bleu); cursor:grab}
.dz.cible:not(:disabled),.dz.over{background:var(--jaune-pale); border-color:var(--orange)}
.dz:disabled{cursor:default; background:#F2F3F1}
.grp .sol.is-ok .dz{border:2px solid var(--vert); background:var(--vert-pale)}
.grp .sol.is-ko .dz{border:2px solid var(--rouge); background:var(--rouge-pale)}
.grp .sol .mark{flex:0 0 4.6em; font-size:.82rem; font-weight:700}
.grp .sol.is-ok .mark{color:var(--vert)} .grp .sol.is-ko .mark{color:var(--rouge)}
.grp .fast-foot .q-status{font-weight:700}
.grp-sol{max-width:780px; margin:4px 0 8px}
.grp-sol td:last-child{font-weight:600}
.q-why .why-t{font:700 .95rem var(--f-titre); margin:.6rem 0 .2rem}
.q-why .compo{max-width:640px}
@media (max-width:620px){ .grp-l{grid-template-columns:minmax(0,1fr)} }

/* ---------- schémas à compléter (cases posées sur la figure, bandeau d'étiquettes collant) ---------- */
.plan{margin:12px 0 16px}
.plan-qs{list-style:none; margin:0 0 10px; padding:8px 12px; display:grid; gap:5px; border-left:3px solid var(--bleu); background:#FAFAF8}
.plan-qs li{font-size:.95rem; line-height:1.4}
.plan-qs .plan-hint{font-size:.86rem; color:var(--encre-2)}
.plan-fig{margin:0; padding:10px 10px 6px; background:#fff; border:1px solid var(--trait-fin)}
.plan-fig figcaption{font-size:.86rem; color:var(--encre-2); margin-top:6px}
.plan-scroll{overflow-x:auto}
.plan-canvas{position:relative; min-width:640px; margin:0 auto; container-type:inline-size}
.plan-svg{display:block; width:100%; height:auto; font-family:var(--f-texte)}
.plan .rv-chaine{border:0}
/* une case du schéma : bouton posé sur son bloc, en pourcentage du dessin ; police à l'échelle du dessin */
.plan-canvas .dz{position:absolute; display:flex; align-items:center; justify-content:center; min-height:0; padding:2px 5px;
  text-align:center; font-size:clamp(9px, calc(14.5 * var(--u)), 15px); line-height:1.16; background:rgba(255,255,255,.72);
  border:1.5px dashed #5A6670; border-radius:4px}
.plan-canvas .dz-in{display:block; width:100%}
.plan-canvas .dz.coupe .dz-in{overflow-wrap:anywhere}
.plan-canvas .dz:not(.filled) .dz-v{position:absolute; width:1px; height:1px; overflow:hidden; clip:rect(0 0 0 0); white-space:nowrap}
.plan-canvas .dz-p{color:#69737B; font-style:italic; font-weight:400}
.plan-canvas .dz.filled .dz-p,.plan-canvas .dz:disabled .dz-p{display:none}
.plan-canvas .dz.filled{background:#fff; border:2px solid var(--bleu)}
.plan-canvas .dz.cible:not(:disabled),.plan-canvas .dz.over{background:var(--jaune-pale); border:2px solid var(--orange)}
.plan-canvas .dz:disabled{background:#F2F3F1; cursor:default}
.plan-canvas .dz.is-ok{background:var(--vert-pale); border:2px solid var(--vert)}
.plan-canvas .dz.is-ko{background:var(--rouge-pale); border:2px solid var(--rouge)}
.plan-canvas .dz.is-ko .dz-v{color:var(--rouge); text-decoration:line-through}
.plan-canvas .dz-a{display:none}
.plan-canvas .dz.is-ko .dz-a{display:block; color:var(--vert); font-weight:700}
.plan-canvas .dz.is-ko.filled .dz-a::before{content:"→\\00a0"}
.plan-canvas .dz-n{--nb:clamp(9px, calc(13 * var(--u)), 13px); position:absolute; left:-.55em; top:-.6em; width:1.75em; height:1.75em;
  display:flex; align-items:center; justify-content:center; border-radius:50%; background:var(--rouge); color:#fff;
  font:700 var(--nb)/1 var(--f-texte); box-shadow:0 0 0 1.5px #fff}
/* le repère déborde dans le coin de la case : la première ligne du texte s'en écarte */
.plan-canvas .dz-n+.dz-in::before{content:""; float:left; width:calc(1.15 * clamp(9px, calc(13 * var(--u)), 13px)); height:calc(1.1 * clamp(9px, calc(13 * var(--u)), 13px))}
/* bandeau : les étiquettes de la partie et ses boutons « Valider », collés au bas de l'écran tant que le schéma est visible */
.plan-tray{position:sticky; bottom:var(--banner); z-index:6; display:grid; gap:3px; padding:6px 10px 7px; background:var(--bleu-pale);
  border:1px solid var(--trait-fin); border-top:2px solid var(--bleu); box-shadow:0 -5px 12px rgba(28,37,48,.13)}
.plan-tray .bank{margin:0; padding:2px 0; gap:5px; background:none; border:0; max-width:none}
.plan-tray .bank+.bank{border-top:1px dashed #C3D3E8; padding-top:4px}
.plan-tray .etq{font-size:.84rem; padding:3px 9px}
.plan-val{display:flex; flex-wrap:wrap; align-items:center; gap:5px; padding-top:5px; border-top:1px solid #C3D3E8}
.btn-plan{font:700 .86rem var(--f-titre); color:#fff; background:var(--encre); border:0; border-radius:2px; padding:5px 11px; cursor:pointer}
.btn-plan small{font:600 .78rem var(--f-texte); opacity:.85}
.btn-plan:hover:not(:disabled){background:#2E3B47}
.btn-plan:disabled{cursor:default}
.btn-plan.ok{background:var(--vert)} .btn-plan.moy{background:var(--orange)} .btn-plan.ko{background:var(--rouge)}
.plan-msg{margin:2px 0 0; font-size:.86rem; color:var(--encre)}
.plan-msg:empty{display:none}
/* une question posée sur le schéma ne garde sous la figure que sa correction, une fois validée */
.grp.sur-plan:not(.fait){display:none}
.grp.sur-plan .q-hint,.grp.sur-plan .grp-fields,.grp.sur-plan .btn-fast{display:none}
@media (max-width:700px),(max-height:560px){ .plan-tray{position:static; box-shadow:none} }

/* ---------- accueil, cours et retour (d'après le dépôt RDM) ---------- */
a.btn{display:inline-flex; align-items:center; gap:8px; text-decoration:none}
a.btn svg,.c-top svg{width:18px; height:18px; flex:0 0 auto}
.tab-home{display:flex; align-items:center; justify-content:center; padding:8px 0 8px 4px; background:var(--encre); color:var(--jaune); text-decoration:none}
.tab-home svg{width:22px; height:22px; display:block}
.tab-home:hover{background:#2E3B47}
.c-top{margin:0 0 12px}
.c-top a{display:inline-flex; align-items:center; gap:6px; font:600 .95rem var(--f-titre); color:var(--encre); text-decoration:none; border:1.5px solid var(--encre); background:var(--papier); padding:5px 12px 5px 10px}
.c-top a:hover{background:var(--jaune-pale)}
#home{padding:20px 20px 32px}
.home-top{display:grid; grid-template-columns:minmax(0,1.6fr) minmax(0,1fr); gap:14px; align-items:stretch; margin:0 0 14px}
.home-top-single{grid-template-columns:1fr}
.home-top-l{display:flex; flex-direction:column; gap:10px; min-width:0}
.home-top .home-head{padding:14px 20px; flex:1}
.home-top .home-head h1{margin:6px 0 6px; font-size:clamp(1.4rem,2.4vw,1.85rem)}
.home-top .home-sub{font-size:.95rem}
.home-top .home-hero{margin:0; padding:8px; display:flex; flex-direction:column; justify-content:center; min-width:0}
.home-top .home-hero img{width:auto!important; max-width:100%; max-height:160px; margin:0 auto}
body.hub .home-top .home-hero img{max-height:210px}
.home-top .home-hero figcaption{font-size:.78rem; line-height:1.3; margin-top:4px}
.home-top .home-facts{grid-template-columns:repeat(4,minmax(0,1fr)); gap:8px; margin:0}
.home-top .home-facts div{padding:6px 10px}
.home-top .home-facts b{font-size:1.02rem}
.home-top .home-facts span{font-size:.76rem; line-height:1.3; display:block; white-space:nowrap; overflow:hidden; text-overflow:ellipsis}
@media (max-width:980px){ .home-top .home-facts{grid-template-columns:repeat(2,minmax(0,1fr))} }
@media (max-width:820px){ .home-top{grid-template-columns:1fr} }
#home .home-choose{margin:18px 0 8px; font-size:1.25rem}
#home .mode-card{padding:12px 18px 14px}
#home .mode-card .mc-lead{margin:2px 0 4px; font-size:.92rem}
#home .mode-card ul{margin:0 0 10px; font-size:.9rem; line-height:1.45}
#home .mode-card li{margin:.15rem 0}
#home .mode-card .btn{padding:9px 16px}
#home .home-note{margin:10px 0 0}
.home-back{margin:12px 0 0}
.ex-grid{display:grid; grid-template-columns:repeat(auto-fill,minmax(250px,1fr)); gap:16px}
.ex-grid .mode-card p{margin:4px 0 8px; font-size:.95rem}
.ex-grid .mode-card .ex-meta{margin:0 0 12px; font-size:.85rem}
.ex-grid .mode-card h3{font-size:1.2rem}
.ex-grid .mc-head{flex-direction:column; align-items:flex-start; gap:6px}
.ex-grid .mode-card .btn{margin-top:auto; align-self:flex-start}
.ex-grid .en-edition{border-style:dashed; border-color:var(--trait)}
.ex-grid .en-edition h3,.ex-grid .en-edition p{color:var(--encre-2)}
.ex-grid .etat{font-weight:700; color:var(--orange)}
/* cartes de l'accueil : image, titre, mots-clés ; toutes de la même taille, dans toutes les rubriques */
body.hub .ex-grid{grid-template-columns:repeat(auto-fill,minmax(260px,1fr)); grid-auto-rows:1fr}
.carte-v{display:grid; grid-template-rows:auto auto 62px 46px; gap:8px; padding:0 0 16px!important; overflow:hidden; height:100%}
body.hub .carte-v>*:not(.cv-img){margin-left:18px; margin-right:18px}
.carte-v .cv-img{display:block; width:100%; height:auto; aspect-ratio:16/9; object-fit:cover; background:#fff; border-bottom:2px solid var(--encre); margin:0}
.carte-v .cv-vide{background:repeating-linear-gradient(135deg,#F4F5F2 0 12px,#ECEEEA 12px 24px)}
.carte-v .mc-head{margin:6px 18px 0}
.carte-v h3{margin:0; min-height:2.4em; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden; line-height:1.2}
#home .carte-v .cv-mots{display:flex; flex-wrap:wrap; align-content:flex-start; gap:5px; list-style:none; margin:0 18px; padding:0}
#home .carte-v .cv-mots li{margin:0}
body.hub .carte-v .btn,body.hub .carte-v .etat{align-self:end; justify-self:start; margin-top:0; margin-bottom:0}
.cv-mots li{font:600 .8rem var(--f-titre); background:var(--bleu-pale); color:var(--encre); border:1px solid #C9D8EC; padding:2px 8px; border-radius:12px; white-space:nowrap}
.en-edition .cv-img{filter:grayscale(1) opacity(.55)}
.en-edition .cv-mots li{background:#F4F5F2; border-color:var(--trait-fin); color:var(--encre-2)}
.pastille{display:inline-block; font:700 .72rem var(--f-titre); letter-spacing:.03em; background:var(--vert); color:#fff; padding:2px 8px; margin-left:6px; vertical-align:middle}
.pastille.n2{background:var(--bleu)}
.mc-tag .pastille{margin-left:8px; font-size:.68rem; padding:1px 6px}

__COURS_CSS__
@media print{
  .c-top,.home-back{display:none!important}
  /* correctif repris du dépôt RDM : dans le gabarit, « .sketch .q-expl[hidden] » l'emporte sur
     « body:not(.corrections-open) .q-expl » et imprimerait la correction des tracés avant la remise de la copie */
  body:not(.corrections-open) .sketch .q-expl[hidden]{display:none!important}
  .eq{overflow:visible; line-height:1.7}
  .grp-l{break-inside:avoid}
  .bank{background:none; padding:4px 0; border:0} .etq{border-width:1px; padding:1px 6px; font-size:8.5pt}
  .dz{min-height:0; padding:3px 8px} .dz:not(.filled) .dz-v{visibility:hidden}
  .plan-tray{display:none} .plan-scroll{overflow:visible} .plan-canvas{min-width:0} .plan-fig{break-inside:avoid}
  .plan-canvas .dz{padding:1px 3px} .plan-canvas .dz-p{visibility:hidden}
}
</style>"""


# ============================================================ ASSEMBLAGE
DECOR_JS = """  var DECOR = {
    // aucun tracé dans les exercices actuels : une entrée par fond de tracé (voir le dépôt RDM)
  };
"""
DR_NAMES_JS = """  var DR_NAMES = {
    // aucun tracé dans les exercices actuels
  };
"""
DATA_RE = re.compile(r"data:image/(?:png|jpeg|svg\+xml);base64,[A-Za-z0-9+/=]+")


ETIQUETTES_JS = r"""<script>/* Étiquettes : glisser une étiquette sur une case, ou la toucher puis toucher la case.
   La case garde le champ (masqué) que lit le moteur du gabarit ; on y écrit l'étiquette et on signale « input ».
   Chaque case porte la liste d'étiquettes qu'elle accepte (data-bank). Les cases peuvent être posées sur
   les schémas ; sous chaque schéma, un bandeau réunit les étiquettes de la partie et des boutons qui relaient les
   boutons « Valider » des questions ; la case du schéma reprend l'état (juste, faux) que le moteur donne au champ. */
(function () {
  "use strict";
  var parts = document.getElementById("parts");
  if (!parts || !parts.querySelector(".bank")) return;
  var sel = null, drag = null;
  function $$(s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); }
  function inp(dz) { return document.getElementById("in-" + dz.id.slice(3)); }
  function banque(el) { return el.classList.contains("dz") ? document.getElementById(el.dataset.bank) : el.closest(".bank"); }
  function cases(bk) { return $$('.dz[data-bank="' + bk.id + '"]'); }
  function msgDe(el) { var pl = el.closest(".plan"); return pl ? pl.querySelector(".plan-msg") : el.closest(".fast-q").querySelector(".q-msg"); }
  function choisir(b) {
    if (sel) { sel.setAttribute("aria-pressed", "false"); cases(banque(sel)).forEach(function (d) { d.classList.remove("cible"); }); }
    sel = b && b !== sel ? b : null;
    if (sel) { sel.setAttribute("aria-pressed", "true"); cases(banque(sel)).forEach(function (d) { if (!d.disabled) d.classList.add("cible"); }); }
  }
  /* case d'un schéma : le texte doit tenir dans le bloc dessiné ; on réduit la police s'il le faut */
  function ajuster(dz) {
    if (!dz.classList.contains("dz-f")) return;
    var c = dz.querySelector(".dz-in"), t, min;
    function deborde() { return c.offsetHeight > dz.clientHeight - 2 || c.scrollWidth > c.clientWidth + 1; }
    dz.style.fontSize = ""; dz.classList.remove("coupe");
    t = parseFloat(getComputedStyle(dz).fontSize); min = t * 0.7;
    while (deborde() && t > min) { t -= 0.5; dz.style.fontSize = t + "px"; }
    if (deborde()) dz.classList.add("coupe");  /* en dernier recours, un mot trop long se coupe */
  }
  function poser(dz, v) {
    var i = inp(dz);
    if (i.disabled) return;
    i.value = v;
    dz.classList.toggle("filled", !!v);
    dz.querySelector(".dz-v").textContent = v || "case vide";
    dz.draggable = !!v;
    ajuster(dz);
    msgDe(dz).textContent = "";
    i.dispatchEvent(new Event("input", { bubbles: true }));
  }
  parts.addEventListener("click", function (e) {
    var b = e.target.closest(".etq"), dz = e.target.closest(".dz"), v = e.target.closest(".btn-plan");
    if (v) { valider(v); return; }
    if (b && !b.disabled) {
      choisir(b);
      if (sel && e.detail === 0) {  /* au clavier : on passe à la première case libre qui accepte l'étiquette */
        var libres = cases(banque(sel)).filter(function (d) { return !d.disabled; });
        var d = libres.filter(function (x) { return !inp(x).value; })[0] || libres[0];
        if (d) d.focus();
      }
      return;
    }
    if (!dz || dz.disabled) return;
    if (sel && banque(sel) === banque(dz)) { poser(dz, sel.textContent); choisir(null); dz.focus(); }
    else if (sel) msgDe(dz).textContent = "Cette case attend une étiquette de la liste « " + banque(dz).querySelector(".bank-t").textContent + " ».";
    else if (inp(dz).value) poser(dz, "");
    else msgDe(dz).textContent = "Choisis d'abord une étiquette dans la liste, puis touche la case.";
  });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape" && sel) choisir(null); });
  parts.addEventListener("dragstart", function (e) {
    var b = e.target.closest && e.target.closest(".etq, .dz");
    if (!b || b.disabled) { e.preventDefault(); return; }
    var surCase = b.classList.contains("dz"), v = surCase ? inp(b).value : b.textContent;
    if (!v || (surCase && inp(b).disabled)) { e.preventDefault(); return; }
    choisir(null);
    drag = { v: v, from: surCase ? b : null, bk: banque(b), el: b };
    b.classList.add("is-drag");
    cases(drag.bk).forEach(function (d) { if (!d.disabled && d !== b) d.classList.add("cible"); });
    e.dataTransfer.effectAllowed = "copyMove";
    e.dataTransfer.setData("text/plain", v);
  });
  parts.addEventListener("dragend", function () {
    if (drag) drag.el.classList.remove("is-drag");
    $$(".dz.over, .dz.cible", parts).forEach(function (d) { d.classList.remove("over", "cible"); });
    drag = null;
  });
  function cible(e) {
    if (!drag) return null;
    var t = e.target.closest && e.target.closest(".dz, .bank");
    if (!t) return null;
    if (t.classList.contains("bank")) return t === drag.bk ? t : null;
    return !t.disabled && banque(t) === drag.bk ? t : null;
  }
  parts.addEventListener("dragover", function (e) {
    var t = cible(e);
    if (!t) return;
    e.preventDefault();
    e.dataTransfer.dropEffect = drag.from ? "move" : "copy";
    if (t.classList.contains("dz")) t.classList.add("over");
  });
  parts.addEventListener("dragleave", function (e) {
    var t = e.target.closest && e.target.closest(".dz");
    if (t && !t.contains(e.relatedTarget)) t.classList.remove("over");
  });
  parts.addEventListener("drop", function (e) {
    var t = cible(e);
    if (!t) return;
    e.preventDefault();
    t.classList.remove("over");
    if (t.classList.contains("bank")) { if (drag.from) poser(drag.from, ""); return; }
    if (t === drag.from) return;
    var ancien = inp(t).value;
    poser(t, drag.v);
    if (drag.from) poser(drag.from, ancien);  /* glisser d'une case à l'autre : les deux étiquettes s'échangent */
  });

  /* bandeau du schéma : chaque bouton relaie le bouton « Valider » de sa question, puis en reprend l'état */
  function valider(v) {
    var g = document.getElementById(v.dataset.g), btn = g.querySelector(".btn-fast");
    if (btn.disabled) return;
    btn.click();
    relayer(g, true);
  }
  function relayer(g, clic) {
    var v = document.querySelector('.btn-plan[data-g="' + g.id + '"]');
    if (!v) return;
    var btn = g.querySelector(".btn-fast"), m = v.closest(".plan").querySelector(".plan-msg"), lab = v.dataset.label;
    var msg = g.querySelector(".q-msg").textContent;
    if (btn.disabled) {
      var n = $$(".sol", g).length, ok = $$(".sol.is-ok", g).length;
      g.classList.add("fait");
      v.disabled = true;
      v.innerHTML = lab + " <small>· " + ok + "/" + n + "</small>";
      v.classList.add(ok === n ? "ok" : ok ? "moy" : "ko");
      if (clic) m.textContent = lab + " : " + g.querySelector(".q-status").textContent + ". La correction s'affiche sous le schéma.";
    } else {
      if (btn.dataset.confirm) v.innerHTML = lab + " <small>· valider quand même</small>";
      if (clic && msg) m.textContent = lab + " : " + msg;
    }
  }
  /* une case validée (entraînement) ou corrigée (examen) est verrouillée par le moteur : la case du schéma reprend
     son état, et la liste d'étiquettes se verrouille quand toutes ses cases le sont */
  function marquer(i) {
    var dz = document.getElementById("dz-" + i.id.slice(3)), sol = i.closest(".sol");
    if (!dz) return;
    dz.disabled = true; dz.draggable = false; dz.classList.remove("cible");
    if (dz.classList.contains("dz-f")) {
      dz.classList.toggle("is-ok", sol.classList.contains("is-ok"));
      dz.classList.toggle("is-ko", sol.classList.contains("is-ko"));
      dz.querySelector(".dz-a").textContent = sol.classList.contains("is-ko") ? dz.dataset.attendu : "";
      ajuster(dz);
    }
    var bk = banque(dz);
    if (cases(bk).every(function (d) { return d.disabled; })) {
      $$(".etq", bk).forEach(function (b) { b.disabled = true; b.draggable = false; });
      if (sel && banque(sel) === bk) choisir(null);
    }
  }
  new MutationObserver(function (ms) {
    ms.forEach(function (m) {
      var t = m.target;  /* ne réagir qu'aux champs et aux boutons du moteur : sinon la boucle s'entretient */
      if (!t.disabled) return;
      if (t.tagName === "INPUT") marquer(t);
      else if (t.classList.contains("btn-fast")) relayer(t.closest(".fast-q"), false);
    });
  }).observe(parts, { subtree: true, attributes: true, attributeFilter: ["disabled"] });
  /* le schéma change de taille (fenêtre, panneau des documents) : les textes des cases s'y réajustent */
  if (window.ResizeObserver) {
    var ro = new ResizeObserver(function (es) { es.forEach(function (x) { $$(".dz-f.filled, .dz-f:disabled", x.target).forEach(ajuster); }); });
    $$(".plan-canvas", parts).forEach(function (c) { ro.observe(c); });
  }
})();
</script>"""


def verifier():
    """Cohérence des descriptions : adresses et préfixes uniques, documents cités existants."""
    cles = [e["key"] for e in EXO_DEFS] + [c["key"] for c in COURS]
    assert len(set(cles)) == len(cles), f"adresse ?ex= en double : {cles}"
    assert all(c["key"].startswith("cours-") for c in COURS), "la clé d'un cours commence par « cours- »"
    assert not any(e["key"].startswith("cours-") for e in EXO_DEFS), "« cours- » est réservé aux cours"
    prefixes = [e["prefix"] for e in EXO_DEFS]
    assert len(set(prefixes)) == len(prefixes), f"préfixe d'exercice en double : {prefixes}"
    docs = {d[0] for d in DOCS}
    for e in EXO_DEFS:
        assert set(e["docs"]) <= docs, f"{e['key']} : document inconnu {set(e['docs']) - docs}"
    for c in LIENS:
        assert c["rubrique"] in ("ressources", "exercices"), c["title"]


def build():
    verifier()
    g = GABARIT.read_text(encoding="utf-8")

    # le commentaire d'en-tête du gabarit cite « <style> » : on part de la vraie balise
    s0 = g.index("<style>:root{")
    style = g[s0:g.index("</style>", s0) + len("</style>")]
    grading = re.search(r"<script>/\*GRADING-START\*/.*?</script>", g, re.S).group(0)
    app_start = g.index("<script>(function () {")
    app = g[app_start:g.rindex("</script>") + len("</script>")]

    # entrées du moteur réservées au sujet ; la durée conseillée dépend de l'exercice ouvert
    app = sub_once(app, r"var CONSEIL_MIN = \d+;", "var CONSEIL_MIN = window.__CONSEIL_MIN__ || 0;")
    app = sub_once(app, r"  var DECOR = \{\n.*?\n  \};\n", DECOR_JS, re.S)
    app = sub_once(app, r"  var DR_NAMES = \{\n.*?\n  \};\n", DR_NAMES_JS, re.S)
    app = sub_once(app, r"Quatre pages, une par document", "Une page par document réponse")
    app = sub_once(app, r'btn\.textContent = "Diagramme validé";', 'btn.textContent = "Réponses validées";')

    templates, exos_cfg = [], {}
    for e in EXO_DEFS:
        prepare_exo(e)
    for e in EXO_DEFS:
        CUR["total"] = e["minutes"]
        parts_html = "".join(render_part(p) for p in e["P"])
        rail, tabs, secs = render_docs(e)
        k = e["key"]
        templates += [f'<template id="tpl-rail-{k}">{rail}</template>',
                      f'<template id="tpl-tabs-{k}">{tabs}</template>',
                      f'<template id="tpl-docs-{k}">{secs}</template>',
                      f'<template id="tpl-home-{k}">{render_exo_home(e)}</template>',
                      f'<template id="tpl-consignes-{k}">{e["consignes"]}</template>',
                      f'<template id="tpl-parts-{k}">{parts_html}\n</template>']
        exos_cfg[k] = e["cfg"]
    templates.append(f'<template id="tpl-modes">{MODES_HTML}</template>')
    templates.append(f'<template id="tpl-hub">{render_hub()}</template>')
    for c in COURS:
        templates.append(f'<template id="tpl-{c["key"]}">{c["render"]()}</template>')

    config = f"<script>window.__EXOS__ = {json.dumps(exos_cfg, ensure_ascii=False)};</script>"
    router = (ROUTER_JS.replace("__COURS_JS__", COURS_JS).replace("__TITRE__", TITRE)
              .replace("__HOUSE__", HOUSE.replace("'", "\\'")))

    page = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{TITRE} — cours et exercices interactifs</title>
<meta name="description" content="Habitat durable, cours et exercices interactifs : concevoir, rénover et habiter un logement économe en énergie et en eau, aux matériaux bien choisis.">
{style}
{CONTENT_CSS.replace("__COURS_CSS__", COURS_CSS + qcm.QCM_CSS)}
</head>
<body class="no-mode">

<nav class="rail" aria-label="Dossiers de présentation et dossier technique"></nav>

<aside id="docpanel" aria-label="Documents du sujet" aria-hidden="true">
  <div class="dp-head">
    <h3 id="dp-title">Documents</h3>
    <button type="button" id="dp-out" aria-label="Réduire">−</button><span id="dp-zoom" class="small">100 %</span>
    <button type="button" id="dp-in" aria-label="Agrandir">+</button>
    <button type="button" id="dp-fit">Ajuster</button>
    <button type="button" id="dp-close">Fermer</button>
  </div>
  <div class="dp-tabs" role="tablist" aria-label="Choisir un document"></div>
  <div class="dp-body"></div>
</aside>

<section id="home" aria-labelledby="home-title"><div class="home-inner"></div></section>

<main class="page">
  <section class="print-only print-summary">
    <p>Élève : <span class="print-nom"></span> | Copie imprimée le <span class="print-date"></span></p>
    <p>Mode : <span class="print-mode"></span> | Temps de rédaction : <strong class="print-time"></strong> (durée conseillée : <span class="print-conseil"></span>)</p>
    <p class="print-note-line">Note finale pondérée : <strong class="final-note"></strong></p>
    <p class="print-nograde">Copie non corrigée : les corrections et la note n'apparaissent qu'après la remise de la copie en mode examen.</p>
  </section>

  <nav class="c-top" aria-label="Navigation"><a href="?">{HOUSE} Accueil</a></nav>

  <header class="cartouche">
    <div class="title">
      <h1>{TITRE}</h1>
      <p></p></div>
    <div class="nom"><label for="nom-eleve">Nom et prénom</label><input id="nom-eleve" type="text" autocomplete="name"></div>
  </header>

  <div class="consignes"></div>

  <div id="parts"></div>

  <section class="recap" id="recap" aria-labelledby="t-recap">
    <header class="recap-head"><h2 id="t-recap">Récapitulatif et note finale</h2>
      <p class="small">Les cases non validées comptent comme fausses. Chaque partie est ramenée sur 20, puis pondérée par sa durée conseillée.</p></header>
    <div id="exam-submit-wrap">
      <p class="es-lead">Ta copie n'est pas encore corrigée : aucune réponse n'est verrouillée, tu peux encore revenir sur les questions.</p>
      <button type="button" class="btn btn-exam" id="exam-submit">J'ai fini, je fais corriger ma copie</button>
      <p class="es-warn" id="exam-warn" role="alert"></p>
    </div>
    <div id="recap-graded">
      <div class="recap-wrap">
        <table class="t recap-table">
          <thead><tr><th>Partie</th><th>Durée</th><th>Poids</th><th>Points</th><th>Note /20</th><th>Contribution</th></tr></thead>
          <tbody id="recap-body"></tbody>
          <tfoot><tr><th colspan="4">Note globale pondérée</th><th class="final-note"></th><th></th></tr></tfoot>
        </table>
      </div>
      <p class="final-detail small"></p>
    </div>
    <div class="recap-foot" id="recap-foot"><button type="button" class="btn btn-print">Imprimer ma copie</button>
      <span class="small no-print">L'impression reprend tes réponses, les corrections et ce récapitulatif.</span>
      <a class="btn ghost no-print" href="?">{HOUSE} Retour à l'accueil</a></div>
  </section>
</main>

<footer class="banner" aria-label="Suivi de la composition">
  <div class="score-block"><div class="lab">Note provisoire</div><div class="score" id="score-val">–<small>/20</small></div></div>
  <div class="exam-block"><div class="lab">Mode examen</div><div class="exam-state">Note masquée</div></div>
  <div class="timer-block"><div class="lab">Temps</div><div class="timer" id="timer-val">0:00:00</div></div>
  <div class="count" id="score-count" aria-live="polite"></div>
  <div class="spacer"></div>
  <button type="button" class="btn-docs" id="btn-docs">Documents</button>
</footer>

{chr(10).join(templates)}

{config}
{router}
{grading}
{app}
{ETIQUETTES_JS}
{qcm.images_js(AIDES_QCM)}
{qcm.QCM_JS}
</body>
</html>
"""
    SORTIE.write_text(page, encoding="utf-8")
    imgs = sum(len(m) for m in DATA_RE.findall(page))
    print(f"{SORTIE.name} : {len(page.encode('utf-8')) / 1024:.0f} Kio, dont images {imgs / 1024:.0f} Kio (base64)")
    for e in EXO_DEFS:
        print(f"  ?ex={e['key']} : {len(e['P'])} parties, {e['n_q']} questions, {e['n_cases']} cases, "
              f"{e['points']} points, {hm(e['minutes'])}")
    for c in COURS:
        print(f"  ?ex={c['key']} : {c['tag']} — {c['title']}")
    vides = [r for r, n in (("cours", len(COURS)),
                            ("exercices", sum(not e.get("etude") for e in EXO_DEFS) +
                             sum(c["rubrique"] == "exercices" for c in LIENS)),
                            ("études de cas", sum(bool(e.get("etude")) for e in EXO_DEFS))) if not n]
    if vides:
        print(f"  en cours d'édition : {', '.join(vides)}")


if __name__ == "__main__":
    build()
