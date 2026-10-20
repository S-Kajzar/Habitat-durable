// Tests navigateur (Playwright + Chromium) : accueil, cours, parcours entraînement et examen, documents.
//   NODE_PATH=$(npm root -g) node --test tests/navigateur.test.js
// Les cours et les exercices sont lus dans la page générée : chacun de ceux qu'on ajoute est parcouru de lui-même
// (un exercice entièrement juste doit donner 20/20, une copie d'examen vide 0/20, sans erreur JavaScript).
const test = require("node:test");
const assert = require("node:assert/strict");
const path = require("node:path");
const fs = require("node:fs");
const { chromium } = require("playwright");
const REP = require("./reponses.js");

const FILE = path.join(__dirname, "..", "index.html");
const URL = "file://" + FILE;
const HTML = fs.readFileSync(FILE, "utf8");
const EXOS = JSON.parse(HTML.match(/window\.__EXOS__ = (.*?);<\/script>/)[1]);
const COURS = [...HTML.matchAll(/<template id="tpl-(cours-[\w-]+)">/g)].map((m) => m[1]);
let browser;

test.before(async () => { browser = await chromium.launch(); });
test.after(async () => { await browser.close(); });

async function open(url, viewport) {
  const context = await browser.newContext({ viewport: viewport || { width: 1366, height: 900 } });
  const page = await context.newPage();
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  page.on("console", (m) => { if (m.type() === "error") errors.push(m.text()); });
  page.on("dialog", (d) => d.accept());
  await page.goto(url.startsWith("file:") ? url : URL + url);
  return { context, page, errors };
}
const text = (page, sel) => page.locator(sel).first().innerText();
// images partagées (écrites une fois dans la page, posées dans les balises <img data-img> du contenu ouvert) :
// [nom, largeur décodée] de chacune ; 0 si elle ne s'affiche pas
const imagesPartagees = (page) => page.evaluate(() => Promise.all([...document.querySelectorAll("img[data-img]")].map((i) =>
  i.decode().then(() => [i.dataset.img, i.naturalWidth], () => [i.dataset.img, 0]))));
const sansDebord = (page) => page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth);
// une case se remplit comme le fait l'élève : toucher l'étiquette (dans la liste que la case accepte), puis la case ;
// sinon, écrire la réponse
async function poser(page, id, v) {
  const dz = page.locator(`#dz-${id}`);
  if (await dz.count()) {
    await page.locator(`#${await dz.getAttribute("data-bank")}`).getByRole("button", { name: v, exact: true }).click();
    await dz.click();
  } else await page.fill(`#in-${id}`, v);
}
// question posée sur un schéma : son bouton « Valider » est dans le bandeau sous la figure
async function valider(page, qid) {
  for (const sel of [`.btn-plan[data-g=${qid}]`, `#${qid} .btn-validate`, `#${qid} .btn-fast`])
    if (await page.locator(sel).count()) return page.click(sel);
}
// bonnes propositions de chaque QCM, lues dans la configuration du moteur
const bonsQcm = (page) => page.evaluate(() => [...document.querySelectorAll(".qcm")].map((q) => {
  const g = window.__QCFG__[q.querySelector(".sol input").dataset.q].grader;
  return [q.id, q.dataset.multi === "1", (g.equals || g.value.map(String))];
}));

test("accueil : rubriques, cartes illustrées à mots-clés, annonces « En cours d'édition »", async () => {
  const { context, page, errors } = await open("");
  assert.ok(await page.locator("body.hub").count());
  assert.ok(await page.isVisible("#home"));
  assert.ok(!(await page.isVisible("main.page")));
  assert.ok(!(await page.isVisible(".banner")));
  assert.match(await text(page, "#home h1"), /Habitat durable/);
  assert.equal(await page.title(), "Habitat durable — cours et exercices interactifs");
  assert.ok(await page.locator(".home-hero img").evaluate((i) => i.complete && i.naturalWidth > 0), "illustration chargée");
  const h2 = await page.locator("#home h2").allInnerTexts();
  assert.deepEqual(h2.filter((t) => t !== "Les ressources"), ["Les cours", "Les exercices", "Études de cas"]);
  const card = (sel) => page.locator(sel).evaluateAll((cs) => cs.map((c) => [
    c.querySelector(".mc-tag").textContent.trim(), c.querySelector("h3").textContent,
    c.querySelector("a") ? c.querySelector("a").getAttribute("href") : null, c.classList.contains("en-edition")]));
  // une rubrique vide est annoncée par une seule carte « En cours d'édition », sans lien
  for (const sel of [".cours-grid", ".exo-grid", ".etude-grid"]) {
    const cs = await card(sel + " .mode-card");
    assert.ok(cs.length >= 1, sel);
    if (cs.some((c) => c[3])) {
      assert.equal(cs.length, 1, sel);
      assert.equal(cs[0][2], null, sel);
      assert.match(await text(page, sel + " .etat"), /En cours d'édition/);
    }
  }
  assert.deepEqual((await card(".cours-grid .mode-card")).map((c) => c[2]).filter(Boolean), COURS.map((k) => "?ex=" + k));
  const exos = (await card(".exo-grid .mode-card, .etude-grid .mode-card")).map((c) => c[2]).filter((h) => h && h.startsWith("?ex="));
  assert.deepEqual(exos.sort(), Object.keys(EXOS).map((k) => "?ex=" + k).sort());
  // chaque carte : 3 à 5 mots-clés, aucun paragraphe de texte ; une carte publiée a sa vignette
  const cartes = await page.locator("#home .carte-v").evaluateAll((cs) => cs.map((c) => ({
    img: c.querySelector("img.cv-img") ? c.querySelector("img.cv-img").naturalWidth : -1, edition: c.classList.contains("en-edition"),
    mots: c.querySelectorAll(".cv-mots li").length, p: c.querySelectorAll("p:not(.etat)").length })));
  for (const c of cartes) {
    assert.ok(c.mots >= 3 && c.mots <= 5, JSON.stringify(c));
    assert.equal(c.p, 0);
    if (!c.edition) assert.ok(c.img > 0, "carte illustrée : " + JSON.stringify(c));
  }
  // toutes les cartes ont la même taille, d'une rubrique à l'autre
  const tailles = await page.locator("#home .carte-v").evaluateAll((cs) => cs.map((c) => [Math.round(c.offsetWidth), c.offsetHeight]));
  for (const [w, h] of tailles) { assert.equal(w, tailles[0][0]); assert.ok(Math.abs(h - tailles[0][1]) <= 1, JSON.stringify(tailles)); }
  assert.equal(await page.locator("#home .btn-mode").count(), 0);
  await page.setViewportSize({ width: 390, height: 844 });
  assert.ok(await sansDebord(page));
  const src = HTML.replace(/data:[^"]+/g, "");
  assert.doesNotMatch(src, /\b(BTS|STI2D|bac(calaur[ée]at)?|session \d|[ée]preuve|acad[ée]mie|sujet z[ée]ro|brevet)\b/i);
  assert.deepEqual(errors, []);
  await context.close();
});

test("adresse inconnue : retour à l'accueil", async () => {
  const { context, page, errors } = await open("?ex=inconnu");
  assert.ok(await page.locator("body.hub").count());
  assert.ok(await page.locator(".cours-grid").count());
  assert.deepEqual(errors, []);
  await context.close();
});

if (!COURS.length) test("cours", { skip: "aucun cours décrit dans src/generer.py" }, () => {});
for (const k of COURS)
  test(`cours ${k} : page du cours, jeux et quiz jouables, impression, téléphone`, async () => {
    const { context, page, errors } = await open("?ex=" + k);
    assert.ok(await page.locator(`body.cours-page.page-${k}`).count());
    const titre = await text(page, "#home h1");
    assert.equal(await page.title(), `${titre} — cours — Habitat durable`);
    assert.ok(await page.locator("#home .home-head .mc-tag").count(), "étiquette du cours");
    // jeux de classement : la bonne réponse à chaque ligne
    for (const jeu of await page.locator(".jeu").all()) {
      const lignes = jeu.locator(".jeu-l"), n = await lignes.count();
      for (let i = 0; i < n; i++) await lignes.nth(i).locator(`button[data-v="${await lignes.nth(i).getAttribute("data-ok")}"]`).click();
      assert.equal((await jeu.locator(".jeu-s").innerText()).trim(), `${n} / ${n}`);
    }
    // quiz : tout juste, trois étoiles
    const q = await page.locator(".quiz-q").count();
    for (let i = 0; i < q; i++) {
      const fs_ = page.locator(".quiz-q").nth(i);
      await fs_.locator(`input[value="${await fs_.getAttribute("data-ok")}"]`).check();
    }
    if (q) {
      assert.equal((await text(page, "#qz-score")).trim(), `${q} / ${q}`);
      assert.equal((await text(page, "#qz-stars")).trim(), "★★★");
    }
    assert.deepEqual((await imagesPartagees(page)).filter(([, w]) => !w), [], "images partagées affichées");
    await page.emulateMedia({ media: "print" });
    assert.ok(await page.isVisible("#home h1"));
    await page.emulateMedia({ media: "screen" });
    await page.setViewportSize({ width: 390, height: 844 });
    assert.ok(await sansDebord(page));
    assert.deepEqual(errors, []);
    await context.close();
  });

if (!Object.keys(EXOS).length) test("exercices et études de cas", { skip: "aucun exercice décrit dans src/generer.py" }, () => {});
for (const [k, E] of Object.entries(EXOS)) {
  test(`${k} en entraînement : sujet entièrement juste = 20/20`, async () => {
    const { context, page, errors } = await open("?ex=" + k);
    assert.match(await text(page, "#home .home-head"), new RegExp(E.title.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")));
    assert.equal(await page.locator("#home .btn-mode").count(), 2);
    await page.click("[data-mode=training]");
    assert.equal(await text(page, ".cartouche h1"), E.title);
    assert.equal(await text(page, ".cartouche .title p"), E.cartouche);
    assert.equal(await page.locator("#parts .part").count(), E.parts.length);
    // QCM : les bonnes propositions de chaque question
    const qcm = new Set();
    for (const [id, multi, ks] of await bonsQcm(page)) {
      qcm.add(id + "_1");
      for (const key of multi ? ks : [ks[0]]) await page.click(`#${id} .qcm-o[data-k='${key}']`);
      await page.click(`#${id} .btn-fast`);
    }
    // autres questions : la réponse de référence dans chaque case, puis « Valider » question par question
    const questions = new Map();
    for (const id of Object.keys(E.qcfg).filter((x) => !qcm.has(x))) {
      const qid = await page.locator(`#in-${id}`).evaluate((i) => i.closest(".q, .fast-q").id);
      questions.set(qid, (questions.get(qid) || []).concat(id));
    }
    for (const [qid, ids] of questions) {
      for (const id of ids) await poser(page, id, (REP[k] || {})[id]);
      await valider(page, qid);
    }
    assert.equal(await page.locator("#parts .sol.is-ko, #parts .q.is-ko, #parts .is-half").count(), 0);
    assert.equal((await text(page, "#recap .final-note")).trim(), "20,0/20");
    assert.equal((await text(page, "#score-val")).replace(/\s/g, ""), "20,0/20");
    assert.equal(await page.locator(".dz-f.coupe").count(), 0, "les étiquettes justes tiennent dans leur case");
    assert.deepEqual(errors, []);
    await context.close();
  });

  test(`${k} en examen : rien ne filtre avant la remise ; copie vide = 0/20`, async () => {
    const { context, page, errors } = await open("?ex=" + k);
    await page.click("[data-mode=exam]");
    assert.ok(!(await page.isVisible("#score-val")));
    assert.equal(await page.locator("#parts .q-expl:visible").count(), 0);
    await page.evaluate(() => window.dispatchEvent(new Event("beforeprint")));
    await page.emulateMedia({ media: "print" });
    assert.ok(await page.isVisible(".print-nograde"));
    assert.ok(!(await page.isVisible(".print-note-line")));
    assert.equal(await page.locator("#parts .q-expl:visible").count(), 0);
    await page.emulateMedia({ media: "screen" });
    await page.click("#exam-submit");
    assert.match(await text(page, "#exam-warn"), /encore vide/);
    await page.click("#exam-submit");
    assert.ok(await page.locator("body.graded").count());
    assert.equal((await text(page, "#recap .final-note")).trim(), "0,0/20");
    assert.ok(await page.locator("#parts .q-expl:visible").count() > 0, "corrections dévoilées");
    assert.deepEqual(errors, []);
    await context.close();
  });

  test(`${k} : documents et téléphone`, async (t) => {
    const { context, page, errors } = await open("?ex=" + k);
    await page.click("[data-mode=training]");
    const docs = await page.locator(".rail .tab[data-doc]").evaluateAll((ts) => ts.map((x) => x.dataset.doc));
    if (docs.length) {
      await page.click(`.rail .tab[data-doc=${docs[0]}]`);
      assert.ok(await page.locator("body.panel-open").count());
      assert.ok(await page.isVisible(`#doc-${docs[0]}`));
      await page.keyboard.press("Escape");
      assert.equal(await page.locator("body.panel-open").count(), 0);
    } else t.diagnostic("pas de document");
    const images = await imagesPartagees(page);
    assert.ok(images.length >= 1, "illustration de l'exercice");
    assert.deepEqual(images.filter(([, w]) => !w), [], "images partagées affichées");
    await page.setViewportSize({ width: 420, height: 860 });
    assert.ok(await sansDebord(page));
    assert.deepEqual(errors, []);
    await context.close();
  });
}

// Cours 1 (habitat durable) : chaque figure interactive et chaque simulateur réagit, avec les valeurs du cours.
test("cours habitat durable : figures et simulateurs", { skip: COURS.includes("cours-habitat-durable") ? false : "cours absent" }, async () => {
  const { context, page, errors } = await open("?ex=cours-habitat-durable");
  // texte affiché (innerText), ou contenu d'un texte SVG, qui n'a pas d'innerText
  const lire = async (sel) => (await page.locator(sel).first().evaluate((e) => e.innerText ?? e.textContent))
    .replace(/\s+/g, " ").trim();
  // figure 1 : le soleil d'hiver entre jusqu'au fond du séjour, celui d'été est arrêté par l'avancée du toit
  assert.notEqual(await page.locator("#hd-bio-beam").getAttribute("points"), "");
  await page.click(".hd-bio-s[data-s=ete]");
  assert.equal(await page.locator("#hd-bio-beam").getAttribute("points"), "");
  assert.match(await lire("#hd-bio-txt"), /ombrage tout le vitrage/);
  await page.click(".hd-bio-n[data-g='2']");
  assert.ok(await page.locator("#hd-bio-g2.on").count());
  // figure 2 : une flèche explique sa part
  await page.click(".hd-dep-a[data-k=toit] polygon");
  assert.match(await lire("#hd-dep-txt"), /Toiture : 30 %/);
  // compacité : à étage, la maison est plus compacte
  assert.match(await lire("#hd-comp-v"), /À étage, C = 0,98 m²\/m³ contre 1,21/);
  // paroi : R, U, D de la paroi par défaut, puis sans isolant
  assert.equal(await lire("#hd-pa-rt"), "3,13 m²·K/W");
  assert.equal(await lire("#hd-pa-u"), "0,32 W/(m²·K)");
  assert.equal(await lire("#hd-pa-d"), "6,4 W/K");
  await page.locator(".hd-pa-r >> nth=1").locator("select").selectOption("");
  assert.equal(await lire("#hd-pa-rt"), "0,28 m²·K/W");
  assert.equal(await lire("#hd-pa-u"), "3,60 W/(m²·K)");
  // pont thermique : il disparaît avec l'isolation extérieure
  assert.ok(await page.isVisible("#hd-pt-svg .hd-pt-fuite"));
  await page.click(".hd-pt-b[data-m=ite]");
  assert.ok(!(await page.isVisible("#hd-pt-svg .hd-pt-fuite")));
  // vitrages (figures 5 et 6)
  await page.click(".hd-vi-b[data-v=triple]");
  assert.equal(await lire("#hd-vi-t"), "20 °C");
  assert.equal(await lire("#hd-vi-uw"), "0,7 W/(m²·K)");
  await page.click(".hd-vi-b[data-v=simple]");
  assert.match(await lire("#hd-vi-txt"), /Hors du cadre « RE2020 »/);
  // surface vitrée : 16 à 18 % de 100 m², la moitié au sud
  assert.match(await lire("#hd-sv-out"), /Sud 50 % 8,0 à 9,0 m²[\s\S]*Total 16 à 18 % 16,0 à 18,0 m²/);
  // ventilation : simple puis double flux
  assert.ok(await page.locator("#hd-vmc-svg.m-sf").count());
  await page.click(".hd-vmc-b[data-m=df]");
  assert.ok(await page.locator("#hd-vmc-svg.m-df").count());
  assert.match(await lire("#hd-vmc-txt"), /Double flux/);
  // puits canadien : l'air d'été se rafraîchit
  await page.click(".hd-pu-b[data-t='32']");
  assert.equal(await lire("#hd-pu-tout"), "≈ 18,7 °C");
  assert.match(await lire("#hd-pu-txt"), /se rafraîchit/);
  // pompe à chaleur : étape 3, puis le COP
  await page.click(".hd-pac-b[data-e='3']");
  assert.ok(await page.locator("#hd-pac-cond.on").count());
  assert.match(await lire("#hd-pac-txt"), /Étape 3\. Le fluide frigorigène réchauffe/);
  await page.locator("#hd-cop-c").evaluate((e) => { e.value = "2"; e.dispatchEvent(new Event("input")); });
  assert.equal(await lire("#hd-cop-e"), "4 500 kWh");
  // bois : équivalences de la figure 13
  assert.equal(await lire("#hd-bo-out tbody tr:nth-child(4) td"), "2 200 kg");
  // programmation (figure 15) : 82 h de confort, puis toujours en confort
  assert.equal(await lire("#hd-pg-c"), "82 h");
  assert.equal(await lire("#hd-pg-g"), "≈ 11 %");
  await page.click("#hd-pg-tout");
  assert.equal(await lire("#hd-pg-c"), "168 h");
  assert.equal(await lire("#hd-pg-g"), "aucune");
  // champ photovoltaïque : 4 modules de 60 cellules en série, 2 chaînes
  assert.equal(await lire("#hd-pv-u"), "4 × 30 = 120 V");
  assert.equal(await lire("#hd-pv-pw"), "800 Wc (8 m²)");
  assert.equal(await page.locator("#hd-pv-svg .hd-pv-mod").count(), 8);
  assert.deepEqual(errors, []);
  await context.close();
});
