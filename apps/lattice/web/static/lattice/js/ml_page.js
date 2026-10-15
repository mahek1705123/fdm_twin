/* ML dashboard page: four tabs, all data from /api. */
const FIELDS = [["cell_size", "Cell size L (mm)", 2], ["wall_thickness", "Wall thickness T (mm)", 3], ["angle", "Angle (deg)", 4],
  ["layer_thickness", "Layer thickness (mm)", 5], ["nozzle_temp", "Nozzle temp (C)", 6], ["E", "Elastic modulus (MPa)", 7],
  ["UTS", "UTS (MPa)", 8], ["CPS", "Compressive peak stress (MPa)", 9], ["NU", "Poisson ratio", 10], ["SEA", "Energy absorption (J/g)", 11], ["RHO", "Relative density (%)", 12]];
const guard = latest();
let LAST = null, TOP = [], MODELS = null, DATA = null, TN = {}, TK = [];
const fill = (id, list, sel) => { $(id).innerHTML = list.map(([k, l]) => `<option value="${k}">${l}</option>`).join(""); if (sel) $(id).value = sel; };
const cssv = n => getComputedStyle(document.documentElement).getPropertyValue(n);

async function renderPredict() {
  const m = $("metric").value, v = $("sx").value, d = design();
  try {
    const r = await guard(() => Promise.all([Api.post("predict", {design: d}), Api.post("geometry", {design: d}),
      Api.post("compare", {design: d, metric: m}), Api.post("sensitivity", {design: d, variable: v, metric: m})]));
    if (!r) return; showError();
    const [p, g, cmp, sens] = r; LAST = p.values; setConfidence(p.confidence);
    $("kpis").innerHTML = TK.map(k => `<div class="kpi"><small>${META.targets[k].label}</small><strong>${f2(p.values[k])}</strong><em>${META.targets[k].unit}</em></div>`).join("");
    const n = p.nearest;
    $("near").innerHTML = n ? `${n.topology}, L ${n.cell_size} mm, T ${n.wall_thickness} mm: modulus <b>${f2(n.E)} MPa</b>, Poisson <b>${n.NU}</b>, SEA <b>${n.SEA} J/g</b>. The prediction differs by ${n.E_diff_pct}% in modulus because the geometry differs.` : "No measured design with this topology and material.";
    const nu = p.values.NU; drawLattice($("lat"), g, 0, 0, 0);
    $("latnote").textContent = (nu < -0.05 ? "Auxetic: the lattice gets wider when stretched." : nu > 0.05 ? "Conventional: the lattice gets narrower when stretched." : "Near-zero Poisson ratio.") + " Wall thickness is drawn to scale with cell size.";
    bars($("cmp"), cmp.items.map((c, i) => ({l: c.label, v: c.value, c: c.selected ? "var(--accent)" : TOPOCOL[i]})), v => f2(v));
    const xmap = {cell_size: S.L, wall_thickness: S.T, nozzle_temp: S.noz};
    lines($("sens"), [{p: sens.points, c: cssv("--cool")}], {xl: $("sx").selectedOptions[0].text, yl: META.targets[m].label + " " + META.targets[m].unit, mx: xmap[v]});
  } catch (e) { showError(e); }
}
async function optimise() {
  $("rstat").textContent = "Searching...";
  try {
    const r = await Api.post("optimise", {goal: $("goal").value, max_density: +$("rm").value, min_modulus: +$("em").value}); showError();
    TOP = r.designs; $("rstat").textContent = `${r.evaluated.toLocaleString()} designs evaluated, ${r.feasible.toLocaleString()} meet your limits.`;
    $("res").innerHTML = TOP.length ? `<table><tr><th>#</th><th>Design</th><th>Modulus MPa</th><th>UTS MPa</th><th>Poisson</th><th>SEA J/g</th><th>Rel. density %</th><th></th></tr>${TOP.map((x, i) => `<tr><td>${i + 1}</td><td>${x.topology_label} ${x.angle}°, ${x.material_label}, L ${x.cell_size}, T ${x.wall_thickness}, layer ${x.layer_thickness}</td><td>${f2(x.values.E)}</td><td>${f2(x.values.UTS)}</td><td>${f2(x.values.NU)}</td><td>${f2(x.values.SEA)}</td><td>${f2(x.values.RHO)}</td><td><button data-a="${i}">Load design</button></td></tr>`).join("")}</table>` : "<p>No design meets these limits. Raise the density limit or lower the modulus floor.</p>";
  } catch (e) { showError(e); $("rstat").textContent = ""; }
}
async function renderModels() {
  try { MODELS = MODELS || await Api.get("models"); } catch (e) { return showError(e); }
  const M = MODELS, k = $("mt").value;
  $("mnote").textContent = `${M.n} lattice rows, ${M.n_test} held out for testing (stratified by topology). ${M.ansys_rows} of the ${M.n} rows are ANSYS FEA validated. Poisson ratio, SEA and density follow near-deterministic scaling in the data, so high scores there are expected. Compressive peak stress is the weakest target.`;
  $("mtab").innerHTML = `<table><tr><th>Model</th>${M.targets.map(t => `<th>${t.label}</th>`).join("")}</tr>${M.models.map(n => `<tr><td>${n}${n === M.deployed ? ' <span class="pill ok">deployed</span>' : ""}</td>${M.targets.map(t => { const v = M.r2[t.key][n], best = Math.max(...M.models.map(q => M.r2[t.key][q])) === v; return `<td style="background:color-mix(in srgb,var(--cool) ${Math.max(0, v) * 55}%,transparent);font-weight:${best ? 700 : 400}">${v.toFixed(3)}</td>`; }).join("")}</tr>`).join("")}</table><p class="note">Test R². Bold is the best per column.</p>`;
  scatter($("avp"), M.test[k].map(q => ({x: q[0], y: q[1], c: TOPOCOL[1]})), {xl: "Actual", yl: "Predicted", same: true});
  bars($("imp"), Object.entries(M.importance[k]).sort((a, b) => b[1] - a[1]).map(([l, v]) => ({l, v})), v => v.toFixed(3));
}
async function renderData() {
  try { DATA = DATA || await Api.get("dataset"); if (!LAST) LAST = (await Api.post("predict", {design: design()})).values; } catch (e) { return showError(e); }
  const fx = FIELDS.find(f => f[0] === $("dx").value), fy = FIELDS.find(f => f[0] === $("dy").value), only = $("dtest").checked;
  const pts = DATA.rows.filter(r => !only || r[13]).map(r => ({x: r[fx[2]], y: r[fy[2]], c: TOPOCOL[r[0]]}));
  const cur = {cell_size: S.L, wall_thickness: S.T, angle: S.ang, layer_thickness: S.layer, nozzle_temp: S.noz, ...LAST};
  $("dleg").innerHTML = DATA.topologies.map((t, i) => `<span><i style="background:${TOPOCOL[i]}"></i>${TN[t]}</span>`).join("");
  scatter($("dsc"), pts, {xl: fx[1], yl: fy[1], log: $("dlog").checked && pts.every(q => q.y > 0), mark: {x: cur[fx[0]], y: cur[fy[0]]}});
}
let tab = 0;
const render = () => [renderPredict, () => {}, renderModels, renderData][tab]();
(async function boot() {
  try { META = await Api.get("meta"); } catch (e) { document.body.insertAdjacentHTML("afterbegin", `<p class="err" style="padding:16px">${e.message}</p>`); return; }
  TN = META.topologies; TK = Object.keys(META.targets);
  initControls($("ctl"), () => { if (tab === 0 || tab === 3) render(); });
  tabs($("tabs"), ["Predict", "Optimise", "Models and test data", "Data explorer"], i => { tab = i; render(); });
  const tl = TK.map(k => [k, META.targets[k].label]);
  fill("metric", tl, "E"); fill("mt", tl, "E"); fill("dx", FIELDS.map(f => [f[0], f[1]]), "RHO"); fill("dy", FIELDS.map(f => [f[0], f[1]]), "E");
  fill("goal", Object.entries(META.goals));
  for (const i of ["metric", "sx"]) $(i).onchange = renderPredict;
  $("mt").onchange = renderModels; for (const i of ["dx", "dy", "dlog", "dtest"]) $(i).onchange = renderData;
  $("run").onclick = optimise; $("rm").oninput = e => $("rmv").textContent = e.target.value + " %"; $("em").oninput = e => $("emv").textContent = e.target.value + " MPa";
  $("res").onclick = e => { const a = e.target.dataset.a; if (a === undefined) return; setDesign(TOP[+a]); gotoTab(0); };
  addEventListener("resize", debounce(render, 120)); render();
})();
