// QCM : chaque bonne réponse est acceptée, chaque autre proposition refusée, pour tous les QCM de la page.
//   node --test tests/qcm.test.js
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const html = fs.readFileSync(path.join(__dirname, "..", "index.html"), "utf8");
const code = html.slice(html.indexOf("/*GRADING-START*/"), html.indexOf("/*GRADING-END*/"));
const mod = { exports: {} };
new Function("module", code + "\nmodule.exports = Grading;")(mod);
const G = mod.exports;
const EXOS = JSON.parse(html.match(/window\.__EXOS__ = (.*?);<\/script>/)[1]);
// questions lues dans la page : exercice, identifiant de la case, réponse multiple ou non, repères des propositions
const Q = [];
for (const [, k, h] of html.matchAll(/<template id="tpl-parts-([\w-]+)">([\s\S]*?)<\/template>/g))
  for (const m of h.matchAll(/<div class="fast-q grp qcm" id="(\w+)" data-multi="(\d)">([\s\S]*?)<div class="fast-foot">/g))
    Q.push({ k, id: m[1] + "_1", multi: m[2] === "1", keys: [...m[3].matchAll(/data-k="([^"]+)"/g)].map((x) => x[1]),
             expl: /<p class="why-t">Explication<\/p><p>\S/.test(h.slice(h.indexOf(`id="${m[1]}"`)).split('<div class="fast-q')[0]) });
const grader = (q) => EXOS[q.k].qcfg[q.id].grader;
const juste = (q) => { const g = grader(q); return (g.equals || g.value.map(String)); };
const ok = (q, v) => G.grade(v, grader(q)).ok;
const AUCUN = Q.length ? false : "aucun QCM décrit dans src/generer.py";

test("chaque question : au moins deux propositions, une explication, une case dans la configuration", { skip: AUCUN }, () => {
  for (const q of Q) {
    assert.ok(q.keys.length >= 2, q.id);
    assert.ok(q.expl, `${q.id} : explication vide`);
    assert.equal(grader(q).type, q.multi ? "intset" : "code", q.id);
  }
});

test("réponse unique : la bonne proposition acceptée, toutes les autres refusées", { skip: AUCUN }, () => {
  for (const q of Q.filter((x) => !x.multi)) {
    const bons = juste(q);
    for (const k of q.keys) assert.equal(ok(q, k), bons.includes(k), `${q.id} : ${k}`);
    assert.equal(ok(q, q.keys.join(",")), false, `${q.id} : tout cocher`);
  }
});

test("réponses multiples : il faut toutes les bonnes, et elles seules", { skip: Q.some((x) => x.multi) ? false : "aucune question à plusieurs réponses" }, () => {
  for (const q of Q.filter((x) => x.multi)) {
    const bons = juste(q);
    assert.ok(ok(q, bons.join(",")), q.id);
    if (bons.length > 1) assert.equal(ok(q, bons.slice(1).join(",")), false, `${q.id} : incomplet`);
    const intrus = q.keys.find((k) => !bons.includes(k));
    if (intrus) assert.equal(ok(q, bons.concat(intrus).join(",")), false, `${q.id} : avec un intrus`);
  }
});
