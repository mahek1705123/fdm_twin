/* Design-input panel. State S uses short keys; design() converts to the API's field names. */
const S = {topo: "Auxetic_Honeycomb", mat: "PLA", L: 10, T: 1, ang: -15, layer: 0.2, noz: 210};
let META = null;
const design = () => ({topology: S.topo, angle: S.ang, material: S.mat, cell_size: S.L, wall_thickness: S.T, layer_thickness: S.layer, nozzle_temp: S.noz});
function syncControls() {
  $("ang").innerHTML = META.angles[S.topo].map(v => `<option value="${v}">${v}°</option>`).join("");
  if (!META.angles[S.topo].includes(S.ang)) S.ang = META.angles[S.topo][0];
  for (const k of ["topo", "ang", "mat", "L", "T", "layer", "noz"]) { $(k).value = S[k]; const v = $(k + "v"); if (v) v.textContent = S[k]; }
  $("rfnote").textContent = `Reinforcement: ${META.materials[S.mat].fibre_wt} wt% short carbon fibre (set by material). Infill density follows the geometry, so it is not a separate input.`;
}
function setConfidence(c) {
  $("cf").innerHTML = `Model confidence <span class="pill ${c.level}">${c.label}</span><div class="note">Distance to the closest design in your dataset: ${c.distance}</div>`;
}
function initControls(host, onChange) {
  const r = META.ranges, opt = o => Object.entries(o).map(([k, v]) => `<option value="${k}">${v.label || v}</option>`).join("");
  const slider = (id, label, k) => `<label>${label}<b id="${id}v"></b></label><input type="range" id="${id}" min="${r[k][0]}" max="${r[k][1]}" step="${r[k][2]}">`;
  host.innerHTML = `<h2>Design inputs</h2><label>Lattice topology</label><select id="topo">${opt(META.topologies)}</select>
    <label>Re-entrant / twist angle</label><select id="ang"></select><label>Material</label><select id="mat">${opt(META.materials)}</select>
    ${slider("L", "Cell size L (mm)", "cell_size")}${slider("T", "Wall thickness T (mm)", "wall_thickness")}
    ${slider("layer", "Layer thickness (mm)", "layer_thickness")}${slider("noz", "Nozzle temperature (°C)", "nozzle_temp")}
    <p class="note" id="rfnote"></p><div id="cf"></div><div class="err" id="err" role="alert"></div>`;
  for (const k of ["topo", "ang", "mat", "L", "T", "layer", "noz"]) {
    $(k).addEventListener("input", e => {
      S[k] = (k === "topo" || k === "mat") ? e.target.value : +e.target.value;
      if (k === "mat") S.noz = META.materials[S.mat].nozzle;
      syncControls(); onChange();
    });
  }
  syncControls();
}
function setDesign(d) { Object.assign(S, {topo: d.topology, ang: d.angle, mat: d.material, L: d.cell_size, T: d.wall_thickness, layer: d.layer_thickness, noz: d.nozzle_temp}); syncControls(); }
