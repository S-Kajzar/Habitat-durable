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

// Autres écritures justes, demi-points d'unité et confusions plausibles, exercice par exercice :
// { exercice: { case: [[réponse, note attendue (1, 0,5 ou 0)], …] } }.
const AUTRES = {
  // Exercice 1.1 — lecture de plan
  "lecture-plan": {
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
  },
  // Exercice 1.2 — isoler une paroi
  "isoler-paroi": {
    b1_3: [["30", 1], ["29,7", 1], ["environ 30 fois", 1], ["3", 0], ["0,03", 0]],
    b2_3: [["oui", 1], ["Oui, des ponts thermiques", 1], ["non", 0]],
    b2_4: [["polystyrène", 1], ["dans l'isolant", 1], ["le parpaing", 0], ["plâtre", 0]],
    b2_5: [["32 cm", 1], ["0,32 m", 1], ["320 mm", 1], ["32", 0.5], ["31 cm", 0]],
    b3_1_2: [["3,125", 1], ["3,13", 1], ["3,12", 1], ["3,1", 0], ["0,3125", 0], ["312,5", 0]],
    b3_1_3: [["0,21", 1], ["0,2105", 1], ["0,19", 0], ["21", 0]],
    b3_2: [["3,39 m²·K/W", 1], ["3,385 m2.K/W", 1], ["R = 3,39 m²K/W", 1], ["3,39", 0.5], ["338,6 m²·K/W", 0]],
    b3_3: [["0,30 W/(m²·K)", 1], ["0,295 W/m²K", 1], ["0,3 W/m2.K", 1], ["0,29 W/(m²·K)", 1], ["0,30", 0.5],
      ["0,30 W/K", 0.5], ["3,39 W/(m²·K)", 0]],
    b3_4: [["7,4 W/K", 1], ["7,38 W/K", 1], ["7,5 W/K", 1], ["7,4", 0.5], ["0,30 W/K", 0], ["74 W/K", 0]],
    b3_5: [["177 W", 1], ["180 W", 1], ["P = 177,2 W", 1], ["177", 0.5], ["103 W", 0]],
    b4_2: [["96 W/K", 1], ["95,97 W/K", 1], ["96", 0.5], ["7,4 W/K", 0]],
    b4_3: [["13", 1], ["environ 13 fois", 1], ["12,8", 1], ["10", 0]],
    b4_4: [["12,8 cm", 1], ["0,128 m", 1], ["128 mm", 1], ["12,8", 0.5], ["1,28 cm", 0]],
    b4_5: [["14 cm", 1], ["0,14 m", 1], ["14", 0.5], ["12 cm", 0], ["16 cm", 0]],
    b4_6: [["3,80 m", 1], ["3,8 m", 1], ["380 cm", 1], ["3,8", 0.5], ["0,38 m", 0]],
  },
  // Exercice 2.1 — ITI ou ITE
  "iti-ite": {
    e2_1: [["4,01 m²·K/W", 1], ["4,0105 m2.K/W", 1], ["4,01", 0.5], ["401 m²·K/W", 0], ["3,75 m²·K/W", 0]],
    e2_3: [["0,25 W/(m²·K)", 1], ["0,249 W/m²K", 1], ["0,25", 0.5], ["4,01 W/(m²·K)", 0]],
    e2_5: [["39", 1], ["39 %", 1], ["61", 0], ["8", 0]],
    e3_1: [["4104 kWh", 1], ["4 104 kWh", 1], ["4104", 0.5], ["171 kWh", 0]],
    e3_3: [["33", 1], ["33,3 %", 1], ["67", 0]],
    e4_2: [["2,3 h", 1], ["2,28 h", 1], ["2,3 heures", 1], ["2,3", 0.5], ["0,23 h", 0]],
    e4_3: [["4,8 h", 1], ["4,84 heures", 1], ["4,8", 0.5], ["24,2 h", 0]],
    e4_7: [["fibre de bois", 1], ["la fibre de bois", 1], ["polystyrène", 0], ["parpaing", 0]],
    e6_2: [["9,52 m²", 1], ["9,5 m²", 1], ["9,52", 0.5], ["4,76 m²", 0]],
  },
  // Étude de cas 1 — le pavillon face à la RE2020
  "etude-pavillon": {
    d1_3: [["brise-soleil", 1], ["une casquette au-dessus des baies", 1], ["une pergola", 1], ["des volets", 0],
      ["double vitrage", 0]],
    d2_3: [["à étage", 1], ["la maison à étage", 1], ["plain-pied", 0]],
    d2_4: [["63 m²", 1], ["63 m2", 1], ["63", 0.5], ["57 m²", 0]],
    d3_2: [["16,95 m²", 1], ["16,95", 0.5], ["17,95 m²", 0]],
    d3_3: [["15,7", 1], ["15,7 %", 1], ["15,69", 1], ["16", 0], ["0,157", 0]],
    d3_4: [["non", 1], ["Non, 15,7 % < 16 %", 1], ["oui", 0]],
    d3_8: [["610 W", 1], ["610,2 W", 1], ["610", 0.5], ["25,4 W", 0]],
    d4_1: [["1 800 kWh", 1], ["1800 kWh", 1], ["1800", 0.5], ["16 200 kWh", 0]],
    d4_3: [["1188 kg", 1], ["1,188 t", 1], ["1,19 t", 1], ["1188", 0.5], ["24,5 kg", 0]],
    d4_4: [["540 L", 1], ["540 litres", 1], ["540", 0.5]],
    d5_1: [["0,99 m", 1], ["99 cm", 1], ["0,99", 0.5], ["0,33 m", 0]],
    d5_2: [["3,16 m", 1], ["3,159 m", 1], ["316 cm", 1], ["3,16", 0.5], ["3,00 m", 0], ["3,99 m", 0]],
    d5_4: [["16", 1], ["16 modules", 1], ["28", 0], ["24", 0]],
    d5_5: [["1600 Wc", 1], ["1,6 kWc", 1], ["1600", 0.5], ["1600 W", 0.5], ["160 Wc", 0]],
    d5_6: [["144 V", 1], ["144", 0.5], ["18 V", 0], ["288 V", 0]],
    d5_8: [["89", 1], ["88,9 %", 1], ["89 %", 1], ["113", 0]],
  },
};

for (const [k, cases] of Object.entries(AUTRES))
  test(`${k} : autres écritures acceptées, unité manquante, confusions`, { skip: EXOS[k] ? false : "exercice absent" }, () => {
    for (const [id, cas] of Object.entries(cases))
      for (const [ans, attendu] of cas) assert.equal(ok(k, id, ans), attendu, `${id} : ${ans}`);
  });
