/* GARDEN SCOPE frontend — renders the typed AgentEvent bus into four views.
   THE ONE LAW: every visual attribute is a pure function of a typed event field.
   color = projection(event). Nothing here promotes, admits, or writes state.
   terminal-browser `action` may later filter/navigate this surface — never mutate
   the Garden. P ↛ T. */

const $ = (id) => document.getElementById(id);
const state = { events: [], jspace: null, shown: 0, timer: null };

// ---- projection: event → css class (semantics → presentation, never inverse) ----
function agentClass(a) { return a === "HER" ? "her" : a === "HAL" ? "hal" : "gate"; }
function fitBar(f) {
  if (f == null) return "";
  const n = Math.round(Math.max(0, Math.min(1, f)) * 10);
  return "█".repeat(n) + "░".repeat(10 - n);
}

function rainRow(e) {
  const row = document.createElement("div");
  row.className = "row " + agentClass(e.agent);
  if (e.type === "SPAWN") {
    row.innerHTML = `<span class="seq">${String(e.seq).padStart(2,"0")}</span>` +
      `<span class="tag ${agentClass(e.agent)}">${e.agent} SPAWN</span>` +
      `<span class="name">${esc(e.name)}</span>`;
  } else { // VERDICT
    row.innerHTML = `<span class="seq">${String(e.seq).padStart(2,"0")}</span>` +
      `<span class="tag gate">Φ GATE</span>` +
      `<span class="name">${esc(e.name)}</span> ` +
      `<span class="v-${e.verdict}">${e.verdict}</span>` +
      `<span class="bar">${fitBar(e.fitness)}</span>`;
  }
  return row;
}

// ---- LINEAGE / POPULATION / GRAVEYARD all read the SINGLE reducer J (/api/jspace) ----
// The browser NEVER recomputes typed state; it projects R's output. This is what
// makes CLI(E) ~ Browser(E) hold: one reducer, two dumb projections.
function renderFromJ() {
  const J = state.jspace; if (!J) return;
  // LINEAGE: cross-pollination hyperedges + each node's verdict, straight from R
  const lh = $("lineage"); lh.innerHTML = "";
  const crosses = (J.hyperedges || []).filter(e => e.type === "CROSS");
  for (const e of crosses) {
    const d = document.createElement("div"); d.className = "lin";
    d.innerHTML = `<span class="tag gate">🧬 CROSS</span> ` +
      `<span class="name">${esc(e.src)}</span> <span class="arrow">──▶</span> ` +
      `<span class="name">${esc(e.dst)}</span>`;
    lh.appendChild(d);
  }
  for (const n of [...(J.population||[]), ...(J.hold||[])]) {
    const d = document.createElement("div"); d.className = "lin";
    d.innerHTML = `<span class="tag ${agentClass(n.agent)}">${n.agent||"?"}</span>` +
      `<span class="name">${esc(n.name)}</span> <span class="arrow">→</span> ` +
      `<span class="v-${n.verdict}">${n.verdict||"…"}</span>`;
    lh.appendChild(d);
  }
  if (!lh.children.length) lh.innerHTML = `<div class="empty">awaiting reduction…</div>`;
  // POPULATION: alive below Φ (survive only). Honest-empty when zero crossed.
  const pop = $("population"); pop.innerHTML = "";
  if (!(J.population||[]).length) {
    pop.innerHTML = `<div class="empty">(( typed zone empty — ${J.counters.spawned} dreamed, 0 crossed Φ ))</div>`;
  } else {
    for (const n of J.population) {
      const d = document.createElement("div"); d.className = "row";
      d.innerHTML = `<span class="v-SURVIVES">🟣 ${esc(n.name)}</span> <span class="bar">fit ${n.fitness}</span>`;
      pop.appendChild(d);
    }
  }
  // GRAVEYARD: compost retained (J_memory = surviving ∪ dead), with death-reason
  const gv = $("graveyard"); gv.innerHTML = "";
  for (const n of (J.graveyard||[])) {
    const d = document.createElement("div"); d.className = "row";
    d.innerHTML = `<span class="name">${esc(n.name)}</span> <span class="v-${n.verdict}">${n.verdict}</span>`;
    gv.appendChild(d);
  }
  $("grave-count").textContent = (J.graveyard||[]).length ? `(${J.graveyard.length} dead · retained)` : "";
}

// ---- live-rain replay: reveal events in seq order, then hold ----
function tick() {
  if (state.shown < state.events.length) {
    state.shown++;
    const e = state.events[state.shown - 1];
    const rain = $("rain");
    rain.appendChild(rainRow(e));
    rain.scrollTop = rain.scrollHeight;
    $("rain-count").textContent = `(${state.shown}/${state.events.length})`;
  } else {
    clearInterval(state.timer); state.timer = null;
  }
}

function esc(s) { return (s || "").replace(/[&<>]/g, c => ({ "&":"&amp;","<":"&lt;",">":"&gt;" }[c])); }

async function boot() {
  const st = await fetch("/api/state").then(r => r.json()).catch(() => ({}));
  $("stateline").textContent =
    `${st.schema || "—"} · HER ${st.her_gen}∥HAL ${st.hal_gen} gen · ` +
    `${st.tested} tested → ${st.typed} typed / ${st.compost} compost / ${st.evidence} evidence`;
  state.events = await fetch("/api/events").then(r => r.json()).catch(() => []);
  state.jspace = await fetch("/api/jspace").then(r => r.json()).catch(() => null); // R(E)
  renderFromJ();                        // typed state comes from the ONE reducer
  state.shown = 0; $("rain").innerHTML = "";
  if (state.timer) clearInterval(state.timer);
  state.timer = setInterval(tick, 220); // replay cadence ∈ Θ (presentation pace only)
}
boot();
