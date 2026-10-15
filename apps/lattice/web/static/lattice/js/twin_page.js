/* Digital-twin page: virtual compression test, topology comparison, ANSYS export, FEA check. */
const guard = latest();
let GEOM = null, CUR = null, ST = 0, raf = null, tab = 0, TN = {}, TK = [];
const cssv = n => getComputedStyle(document.documentElement).getPropertyValue(n);
const interp = (pts, x) => { const i = Math.min(pts.length - 2, Math.max(0, Math.floor(x / 0.5))); const a = pts[i], b = pts[i + 1]; return a[1] + (b[1] - a[1]) * ((x - a[0]) / (b[0] - a[0])); };
const energy = (pts, x) => { let e = 0; for (let i = 1; i < pts.length && pts[i][0] <= x + 1e-9; i++) e += (pts[i][1] + pts[i - 1][1]) / 2 * 0.005; return e; };
const KP = (l, v, u) => `<div class="kpi"><small>${l}</small><strong>${v}</strong><em>${u}</em></div>`;

function drawTwin() {
  if (!CUR) return; const nu = CUR.values.NU, sg = interp(CUR.current, ST);
  $("epsv").textContent = "strain " + ST.toFixed(1) + "%";
  drawLattice($("lat"), GEOM, ST / 100, nu, sg / CUR.values.CPS);
  $("rd").innerHTML = KP("Stress", f2(sg), "MPa") + KP("Lateral strain", (-nu * ST).toFixed(1), "%") + KP("Energy absorbed", f2(energy(CUR.current, ST)), "MJ/m³");
  $("kp").innerHTML = TK.map(k => KP(META.targets[k].label, f2(CUR.values[k]), META.targets[k].unit)).join("");
}
function drawCurves() {
  if (!CUR) return;
  $("sl").innerHTML = CUR.series.map((s, i) => `<span><i style="background:${TOPOCOL[i]}"></i>${s.label}${s.selected ? " (selected)" : ""}</span>`).join("");
  lines($("ss"), CUR.series.map((s, i) => ({p: s.points, c: TOPOCOL[i], w: s.selected ? 4 : 2})), {xl: "Compressive strain (%)", yl: "Stress (MPa)", mx: ST});
}
async function refresh() {
  try {
    const r = await guard(() => Promise.all([Api.post("geometry", {design: design()}), Api.post("curves", {design: design()}), Api.post("predict", {design: design()})]));
    if (!r) return; showError(); GEOM = r[0]; CUR = r[1]; setConfidence(r[2].confidence); drawTwin(); drawCurves();
    if (tab === 2) loadApdl(); if (tab === 3) loadCheck();
  } catch (e) { showError(e); }
}
async function loadApdl() {
  try { const r = await Api.post("apdl", {design: design()});
    $("su").innerHTML = "<table>" + r.setup.map(x => `<tr><th>${x[0]}</th><td>${x[1]}</td></tr>`).join("") + "</table>"; $("apdl").value = r.script; } catch (e) { showError(e); }
}
async function loadCheck() {
  const num = id => { const v = parseFloat($(id).value); return isFinite(v) ? v : null; };
  try {
    const r = await Api.post("validate", {design: design(), ansys: {E: num("ve"), CPS: num("vp"), NU: num("vn2")}});
    $("vn").textContent = `Enter results from your ANSYS run for the design on the left. ${r.ansys_rows_in_training} of the ${r.n} rows used to train the twin came from ANSYS FEA, so large gaps usually point to boundary conditions, material data or mesh.`;
    const pill = {agrees: '<span class="pill ok">Agrees (within 10%)</span>', close: '<span class="pill mid">Close (within 25%)</span>', investigate: '<span class="pill low">Investigate</span>'};
    $("vt").innerHTML = "<table><tr><th>Property</th><th>Twin</th><th>ANSYS</th><th>Difference</th><th>Verdict</th></tr>" + r.rows.map(x => `<tr><td>${x.label}</td><td>${f2(x.twin)}</td><td>${x.ansys === null ? "enter value" : f2(x.ansys)}</td><td>${x.diff_pct === null ? "" : (x.diff_pct > 0 ? "+" : "") + x.diff_pct + "%"}</td><td>${pill[x.verdict] || ""}</td></tr>`).join("") + "</table>";
  } catch (e) { showError(e); }
}
(async function boot() {
  try { META = await Api.get("meta"); } catch (e) { document.body.insertAdjacentHTML("afterbegin", `<p class="err" style="padding:16px">${e.message}</p>`); return; }
  TN = META.topologies; TK = Object.keys(META.targets);
  initControls($("ctl"), refresh);
  tabs($("tabs"), ["Virtual test", "Topology comparison", "ANSYS set-up", "Check vs FEA"], i => { tab = i; if (i === 2) loadApdl(); if (i === 3) loadCheck(); drawTwin(); drawCurves(); });
  $("eps").oninput = e => { ST = +e.target.value; drawTwin(); drawCurves(); };
  $("play").onclick = () => {
    if (raf) { cancelAnimationFrame(raf); raf = null; $("play").textContent = "Play"; return; }
    $("play").textContent = "Pause"; if (ST >= 50) ST = 0;
    const step = () => { ST = Math.min(50, ST + 0.4); $("eps").value = ST; drawTwin(); drawCurves(); if (ST >= 50) { raf = null; $("play").textContent = "Replay"; } else raf = requestAnimationFrame(step); };
    raf = requestAnimationFrame(step);
  };
  $("sel").onclick = () => { $("apdl").focus(); $("apdl").select(); };
  $("cp").onclick = async () => { try { await navigator.clipboard.writeText($("apdl").value); $("cps").textContent = "Copied"; } catch (e) { $("apdl").select(); $("cps").textContent = "Press Ctrl+C to copy"; } };
  for (const i of ["ve", "vp", "vn2"]) $(i).oninput = debounce(loadCheck, 250);
  addEventListener("resize", debounce(() => { drawTwin(); drawCurves(); }, 120)); refresh();
})();
