// Tests unitaires du moteur de correction appliqué aux cases de chaque exercice.
//   node --test tests/correction.test.js
// Le moteur (Grading) et la configuration (__EXOS__) sont lus dans la page générée : on teste exactement ce que
// l'élève utilisera. Chaque exercice ajouté dans src/generer.py est couvert de lui-même, à condition que ses
// réponses de référence soient dans tests/reponses.js.
const test = require("node:test");
const assert = require("node:assert/strict");
const crypto = require("node:crypto");
const fs = require("node:fs");
const path = require("node:path");

const RACINE = path.join(__dirname, "..");
const html = fs.readFileSync(path.join(RACINE, "index.html"), "utf8");
const GABARIT = fs.readFileSync(path.join(RACINE, "src", "gabarit-exercice-interactif.html"), "utf8");
const moteur = (s) => s.slice(s.indexOf("/*GRADING-START*/"), s.indexOf("/*GRADING-END*/"));
const mod = { exports: {} };
new Function("module", moteur(html) + "\nmodule.exports = Grading;")(mod);
const G = mod.exports;
const EXOS = JSON.parse(html.match(/window\.__EXOS__ = (.*?);<\/script>/)[1]);
const REP = require("./reponses.js");
const TYPES = ["num", "kw", "code", "intset", "yesno", "chasles"];

// questions de chaque exercice, lues dans son modèle de page (les identifiants des listes d'étiquettes ne sont
// uniques qu'à l'intérieur d'un exercice)
const PARTS = {};
for (const m of html.matchAll(/<template id="tpl-parts-([\w-]+)">([\s\S]*?)<\/template>/g)) PARTS[m[1]] = m[2];
const QCM = (k) => new Set([...PARTS[k].matchAll(/<div class="fast-q grp qcm" id="(\w+)"/g)].map((m) => m[1] + "_1"));
const AUCUN = Object.keys(EXOS).length ? false : "aucun exercice décrit dans src/generer.py";
const ok = (k, id, ans) => { const r = G.grade(ans, EXOS[k].qcfg[id].grader); return r.invalid ? "invalid" : r.score; };

test("gabarit recopié tel quel : fichier inchangé, style et moteur de correction identiques dans la page", () => {
  // empreinte du gabarit du dépôt « Chaîne fonctionnelle » (lui-même copie conforme de celui du dépôt RDM)
  assert.equal(crypto.createHash("sha256").update(GABARIT).digest("hex"),
    "d39968afd8d398aed6e0b56968445e3b9ddbd19d503efe9adabef898d93db91a");
  assert.equal(moteur(html), moteur(GABARIT));
  const style = (s) => { const i = s.indexOf("<style>:root{"); return s.slice(i, s.indexOf("</style>", i)); };
  assert.equal(style(html), style(GABARIT));
  assert.equal(typeof G.grade, "function");
});

test("configuration : parties pondérées par leur durée, une case = un point, correcteurs connus", { skip: AUCUN }, () => {
  for (const [k, E] of Object.entries(EXOS)) {
    assert.ok(E.parts.length >= 1, k);
    assert.equal(E.parts.reduce((s, p) => s + p.minutes, 0), E.minutes, k);
    assert.equal(E.parts.reduce((s, p) => s + p.points, 0), Object.keys(E.qcfg).length, k);
    for (const [id, c] of Object.entries(E.qcfg)) {
      assert.ok(E.parts.some((p) => p.num === c.part), `${k} ${id} : partie ${c.part}`);
      assert.equal(c.pts, 1, `${k} ${id}`);
      assert.ok(TYPES.includes(c.grader.type), `${k} ${id} : correcteur ${c.grader.type}`);
    }
    assert.equal(E.skcfg && Object.keys(E.skcfg).length, 0, k);
  }
});

test("réponses de référence : une par case (hors QCM) dans tests/reponses.js, toutes justes", { skip: AUCUN }, () => {
  assert.deepEqual(Object.keys(REP).filter((k) => !EXOS[k]), [], "tests/reponses.js : exercice inconnu");
  for (const k of Object.keys(EXOS)) {
    const qcm = QCM(k), ids = Object.keys(EXOS[k].qcfg).filter((id) => !qcm.has(id));
    assert.deepEqual(Object.keys(REP[k] || {}).sort(), ids.sort(), `${k} : cases de tests/reponses.js`);
    for (const id of ids) assert.equal(ok(k, id, REP[k][id]), 1, `${k} ${id} : ${REP[k][id]}`);
  }
});

test("saisie vide refusée sans être notée", { skip: AUCUN }, () => {
  for (const [k, E] of Object.entries(EXOS)) for (const id of Object.keys(E.qcfg)) assert.equal(ok(k, id, "   "), "invalid", `${k} ${id}`);
});

test("valeurs numériques : la valeur seule, sans son unité, vaut un demi-point", { skip: AUCUN }, () => {
  for (const [k, E] of Object.entries(EXOS))
    for (const [id, c] of Object.entries(E.qcfg)) {
      if (c.grader.type !== "num" || !c.grader.unit) continue;
      assert.equal(ok(k, id, String(c.grader.value).replace(".", ",")), 0.5, `${k} ${id}`);
      assert.equal(ok(k, id, `${String(c.grader.value).replace(".", ",")} ${c.grader.unit.label}`), 1, `${k} ${id}`);
    }
});

// Étiquettes proposées à chaque case (lues dans la page : la case nomme sa liste, sous l'énoncé ou dans le bandeau
// du schéma) : la réponse de référence en fait partie, et aucune autre étiquette de la liste n'est acceptée, sauf
// les doubles réponses prévues par la correction (DOUBLES : { exercice: { case: [étiquettes justes] } }).
const DOUBLES = {};
const unesc = (s) => s.replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&amp;/g, "&");
const ETIQUETTES = {}, ATTENDUES = {};
for (const [k, h] of Object.entries(PARTS)) {
  const listes = {};
  for (const m of h.matchAll(/<div class="bank" id="(bk-[\w-]+)"[^>]*>([\s\S]*?)<\/div>/g))
    listes[m[1]] = [...m[2].matchAll(/class="etq"[^>]*>([^<]*)</g)].map((x) => unesc(x[1]));
  for (const m of h.matchAll(/<button type="button" class="dz( dz-f)?" id="dz-(\w+)" data-bank="([\w-]+)"(?: data-attendu="([^"]*)")?/g)) {
    (ETIQUETTES[k] ||= {})[m[2]] = listes[m[3]];
    if (m[1]) (ATTENDUES[k] ||= {})[m[2]] = unesc(m[4]);
  }
}
const SANS_ETIQUETTES = Object.keys(ETIQUETTES).length ? false : "aucune case à étiquettes";

test("étiquettes : la bonne est proposée, les autres de la liste sont refusées", { skip: SANS_ETIQUETTES }, () => {
  for (const [k, cases] of Object.entries(ETIQUETTES))
    for (const [id, bank] of Object.entries(cases)) {
      const juste = REP[k][id];
      assert.ok(bank && bank.includes(juste), `${k} ${id} : « ${juste} » absente de sa liste`);
      assert.equal(new Set(bank).size, bank.length, `${k} ${id} : doublon dans la liste`);
      const acceptees = bank.filter((b) => ok(k, id, b) === 1).sort();
      assert.deepEqual(acceptees, ((DOUBLES[k] || {})[id] || [juste]).slice().sort(), `${k} ${id}`);
    }
});

test("schémas à compléter : le schéma corrigé montre la bonne étiquette", { skip: Object.keys(ATTENDUES).length ? false : "aucun schéma à compléter" }, () => {
  for (const [k, cases] of Object.entries(ATTENDUES))
    for (const [id, att] of Object.entries(cases)) assert.equal(att, REP[k][id], `${k} ${id}`);
});

// Exercice 1.1 (lecture de plan) : autres écritures justes, demi-points d'unité et confusions plausibles.
const LP = EXOS["lecture-plan"] ? {
  a2_5: [["12 cm", 1], ["0,12 m", 1], ["120 mm", 1], ["12", 0.5], ["32 cm", 0]],
  a2_7: [["305 cm", 1], ["3,05 m", 1], ["3050 mm", 1], ["3 050 mm", 1], ["305", 0.5], ["3,05", 0], ["30,5 cm", 0]],
  a3_2: [["13,88 m²", 1], ["13,88 m2", 1], ["S = 4,58 × 3,03 = 13,88 m²", 1], ["13,88", 0.5], ["13,9 m²", 0], ["13,87 m²", 1]],
  a4_3: [["90 cm", 1], ["0,90 m", 1], ["0,9 m", 1], ["900 mm", 1], ["90", 0.5], ["0,9", 0], ["30 cm", 0]],
  a4_5: [["−0,60", 1], ["-0,6", 1], ["-0,60 m", 1], ["0,60", 0], ["-1,25", 0]],
  a4_6: [["33", 1], ["33 %", 1], ["pente de 33 %", 1], ["3,3", 0]],
  a5_1: [["14", 1], ["14 marches", 1], ["15", 0], ["13", 0]],
  a5_2: [["2,60 m", 1], ["260 cm", 1], ["2600 mm", 1], ["2,6", 0.5], ["2,45 m", 0]],
  a5_3: [["185,7 mm", 1], ["185,71 mm", 1], ["18,57 cm", 1], ["185,7", 0.5], ["186 mm", 0], ["173,3 mm", 0]],
  a6_1: [["nord", 1], ["La façade nord", 1], ["sud", 0], ["est", 0]],
  a6_2: [["garage", 1], ["Le garage", 1], ["cellier", 0], ["hall", 0]],
  a6_3: [["sud", 1], ["la façade Sud", 1], ["ouest", 0], ["est", 0]],
} : null;

test("lecture de plan : autres écritures acceptées, unité manquante, confusions", { skip: LP ? false : "exercice absent" }, () => {
  for (const [id, cas] of Object.entries(LP))
    for (const [ans, attendu] of cas) assert.equal(ok("lecture-plan", id, ans), attendu, `${id} : ${ans}`);
});
