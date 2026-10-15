/* Thin client for the JSON API plus small UI helpers shared by both pages. */
const $ = id => document.getElementById(id);
const Api = {
  csrf: () => document.querySelector("meta[name=csrf]").content,
  async get(path) { return Api._handle(await fetch("/api/" + path)); },
  async post(path, body) {
    return Api._handle(await fetch("/api/" + path, {method: "POST",
      headers: {"Content-Type": "application/json", "X-CSRFToken": Api.csrf()}, body: JSON.stringify(body)}));
  },
  async _handle(r) { const j = await r.json(); if (!r.ok) throw new Error(j.error || r.statusText); return j; },
};
/* Ignore responses that arrive after a newer request was started. */
function latest() { let n = 0; return async fn => { const id = ++n; const out = await fn(); return id === n ? out : null; }; }
function debounce(fn, ms) { let t; return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); }; }
function showError(e) { const el = $("err"); if (el) el.textContent = e ? e.message : ""; }
function theme() {
  const r = document.documentElement, light = r.dataset.theme === "light" || (!r.dataset.theme && matchMedia("(prefers-color-scheme:light)").matches);
  r.dataset.theme = light ? "dark" : "light"; window.dispatchEvent(new Event("resize"));
}
function tabs(host, names, cb) {
  host.innerHTML = names.map((n, i) => `<button role="tab" aria-selected="${i == 0}" data-i="${i}">${n}</button>`).join("");
  const go = i => { [...host.children].forEach((b, j) => { b.setAttribute("aria-selected", i == j); $("tab" + j).classList.toggle("hide", i != j); }); cb(i); };
  host.onclick = e => { if (e.target.dataset.i !== undefined) go(+e.target.dataset.i); };
  window.gotoTab = go;
}
