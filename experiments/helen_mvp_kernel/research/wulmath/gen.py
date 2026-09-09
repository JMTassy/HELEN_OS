# -*- coding: utf-8 -*-
import html
from collections import Counter
from wul_data import LAWS, VIB

E = lambda s: html.escape(s, quote=True)
by_vib = {v: [l for l in LAWS if l[3] == v] for v in VIB}
counts = Counter(l[3] for l in LAWS)

KERNEL_LOC, CONST_LOC, TEST_LOC = 39541, 22184, 14537
REFUSALS, PROBES = 649, 108
RECEIPT = "6d2f86b8d8c775fc3c360ef138bb67d0214231aaa19c47b470b6e738c63392e4"
RATIO = KERNEL_LOC / PROBES

css_vib = "\n".join(
    f"  --v{v}: {VIB[v][1]};" for v in VIB)
css_vib_dark = "\n".join(
    f"    --v{v}: {VIB[v][2]};" for v in VIB)

key_rows = "\n".join(f'''      <li class="key-row">
        <span class="key-swatch" style="background:var(--v{v})"></span>
        <span class="key-n">{v}</span>
        <span class="key-name">{E(VIB[v][0])}</span>
        <span class="key-fn">{E(VIB[v][3])}</span>
        <span class="key-count">{counts[v]}</span>
      </li>''' for v in VIB)

def stratum(v):
    name, base, lift, fn = VIB[v]
    rows = "\n".join(f'''        <li class="law" style="--c:var(--v{v})">
          <span class="law-i">{i:03d}</span>
          <span class="law-body">
            <span class="law-math">{E(math)}</span>
            <span class="law-name">{E(nm)}</span>
          </span>
        </li>''' for i, nm, math, _ in by_vib[v])
    return f'''    <section class="stratum" style="--c:var(--v{v})" id="v{v}">
      <header class="stratum-h">
        <span class="stratum-n">{v}</span>
        <h2 class="stratum-t">{E(name)}</h2>
        <span class="stratum-f">{E(fn)}</span>
        <span class="stratum-c">{counts[v]} laws</span>
      </header>
      <ol class="laws">
{rows}
      </ol>
    </section>'''

strata = "\n".join(stratum(v) for v in VIB)

DOC = f'''<title>The 108 Refusals</title>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Spectral:ital,wght@0,300;0,400;0,600;1,400&family=IBM+Plex+Mono:wght@400;500;600&display=swap">
<style>
:root {{
{css_vib}
  --gold: #C9A227;
  --ground: #EFE7D6;
  --ground-2: #E6DCC7;
  --ink: #1E2228;
  --ink-2: #4A4740;
  --muted: #6E6A5F;
  --hem: rgba(30,34,40,.22);
  --hairline: rgba(30,34,40,.12);
  --mono: "IBM Plex Mono", "DejaVu Sans Mono", "Segoe UI Symbol", ui-monospace, monospace;
  --serif: "Spectral", Georgia, "Times New Roman", serif;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
{css_vib_dark}
    --ground: #101418;
    --ground-2: #161B21;
    --ink: #E8E4DB;
    --ink-2: #B6B2A8;
    --muted: #8A8F96;
    --hem: rgba(201,162,39,.34);
    --hairline: rgba(232,228,219,.11);
  }}
}}
:root[data-theme="dark"] {{
{css_vib_dark}
  --ground: #101418;
  --ground-2: #161B21;
  --ink: #E8E4DB;
  --ink-2: #B6B2A8;
  --muted: #8A8F96;
  --hem: rgba(201,162,39,.34);
  --hairline: rgba(232,228,219,.11);
}}

* {{ box-sizing: border-box; }}
body {{
  background: var(--ground);
  color: var(--ink);
  font-family: var(--serif);
  font-size: 16px;
  line-height: 1.55;
  padding-inline: 20px;
  padding-block: 0;
  -webkit-font-smoothing: antialiased;
}}
.plate {{
  max-width: 1180px;
  margin-inline: auto;
  border-inline: 1px solid var(--hem);
  padding-inline: clamp(14px, 3vw, 40px);
  padding-block: 0 64px;
}}

/* ── masthead ─────────────────────────────────────────── */
.mast {{ padding-block: clamp(36px, 7vw, 76px) 34px; }}
.eyebrow {{
  font-family: var(--mono);
  font-size: 11px;
  font-weight: 500;
  letter-spacing: .19em;
  text-transform: uppercase;
  color: var(--muted);
  margin: 0 0 20px;
}}
.mast-grid {{
  display: grid;
  grid-template-columns: auto 1fr;
  gap: clamp(20px, 4vw, 46px);
  align-items: start;
}}
.turnstile {{
  font-family: var(--mono);
  font-size: clamp(78px, 15vw, 168px);
  line-height: .82;
  font-weight: 400;
  color: var(--gold);
  margin: 0;
  user-select: none;
}}
.turnstile small {{
  display: block;
  font-size: 11px;
  letter-spacing: .16em;
  text-transform: uppercase;
  color: var(--muted);
  margin-top: 14px;
  line-height: 1.5;
}}
h1 {{
  font-family: var(--serif);
  font-weight: 300;
  font-size: clamp(34px, 6vw, 62px);
  line-height: 1.02;
  letter-spacing: -.018em;
  margin: -.12em 0 0;
  text-wrap: balance;
}}
h1 em {{ font-style: italic; color: var(--ink-2); }}
.standfirst {{
  max-width: 62ch;
  font-size: 17px;
  color: var(--ink-2);
  margin: 20px 0 0;
}}

/* ── axioms ───────────────────────────────────────────── */
.axioms {{
  margin: 34px 0 0;
  border-top: 1px solid var(--hem);
  border-bottom: 1px solid var(--hem);
  padding-block: 22px;
  display: grid;
  gap: 12px;
}}
.ax {{
  display: grid;
  grid-template-columns: 128px 1fr;
  gap: 4px 18px;
  align-items: baseline;
}}
.ax-k {{
  font-family: var(--mono);
  font-size: 10.5px;
  letter-spacing: .16em;
  text-transform: uppercase;
  color: var(--muted);
}}
.ax-v {{
  font-family: var(--mono);
  font-size: clamp(13px, 1.7vw, 16px);
  line-height: 1.6;
  color: var(--ink);
  overflow-x: auto;
}}
.ax-v .no {{ color: var(--v1); }}
.ax-v .yes {{ color: var(--v4); }}

/* ── census ───────────────────────────────────────────── */
.census {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(126px, 1fr));
  gap: 1px;
  background: var(--hairline);
  border: 1px solid var(--hairline);
  margin-top: 30px;
}}
.cell {{ background: var(--ground); padding: 15px 16px 14px; }}
.cell-n {{
  font-family: var(--mono);
  font-size: 25px;
  font-weight: 500;
  letter-spacing: -.02em;
  font-variant-numeric: tabular-nums;
  display: block;
  line-height: 1.1;
}}
.cell-l {{
  font-family: var(--mono);
  font-size: 10px;
  letter-spacing: .13em;
  text-transform: uppercase;
  color: var(--muted);
  display: block;
  margin-top: 7px;
}}
.cell.hi .cell-n {{ color: var(--gold); }}

/* ── key ──────────────────────────────────────────────── */
.key {{ margin-top: 52px; }}
.section-label {{
  font-family: var(--mono);
  font-size: 10.5px;
  letter-spacing: .19em;
  text-transform: uppercase;
  color: var(--muted);
  margin: 0 0 14px;
  padding-bottom: 9px;
  border-bottom: 1px solid var(--hem);
}}
.key ul {{ list-style: none; margin: 0; padding: 0; }}
.key-row {{
  display: grid;
  grid-template-columns: 14px 20px minmax(96px, 150px) 1fr auto;
  gap: 14px;
  align-items: center;
  padding: 9px 0;
  border-bottom: 1px solid var(--hairline);
}}
.key-swatch {{ width: 14px; height: 14px; }}
.key-n, .key-name, .key-fn, .key-count {{ font-family: var(--mono); font-size: 12.5px; }}
.key-n {{ color: var(--muted); font-variant-numeric: tabular-nums; }}
.key-name {{ font-weight: 500; }}
.key-fn {{ color: var(--muted); }}
.key-count {{ color: var(--ink-2); font-variant-numeric: tabular-nums; }}

/* ── strata ───────────────────────────────────────────── */
.stratum {{ margin-top: 54px; }}
.stratum-h {{
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 6px 16px;
  padding-bottom: 10px;
  border-bottom: 2px solid var(--c);
}}
.stratum-n {{
  font-family: var(--mono);
  font-size: 12px;
  font-weight: 600;
  color: var(--c);
  font-variant-numeric: tabular-nums;
}}
.stratum-t {{
  font-family: var(--mono);
  font-size: 15px;
  font-weight: 600;
  letter-spacing: .04em;
  margin: 0;
  color: var(--ink);
}}
.stratum-f {{
  font-family: var(--serif);
  font-style: italic;
  font-size: 15px;
  color: var(--muted);
}}
.stratum-c {{
  font-family: var(--mono);
  font-size: 10.5px;
  letter-spacing: .14em;
  text-transform: uppercase;
  color: var(--muted);
  margin-left: auto;
}}
.laws {{
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(430px, 1fr));
  gap: 0 34px;
}}
.law {{
  display: grid;
  grid-template-columns: 34px 1fr;
  gap: 12px;
  padding: 13px 0 12px 0;
  border-bottom: 1px solid var(--hairline);
  align-items: start;
}}
.law-i {{
  font-family: var(--mono);
  font-size: 11px;
  font-variant-numeric: tabular-nums;
  color: var(--c);
  padding-top: 3px;
  border-left: 2px solid var(--c);
  padding-left: 8px;
  line-height: 1.5;
}}
.law-body {{ min-width: 0; }}
.law-math {{
  display: block;
  font-family: var(--mono);
  font-size: 13.5px;
  line-height: 1.62;
  color: var(--ink);
  overflow-x: auto;
  white-space: nowrap;
  padding-bottom: 2px;
  scrollbar-width: thin;
}}
.law-name {{
  display: block;
  font-family: var(--mono);
  font-size: 10px;
  letter-spacing: .1em;
  text-transform: uppercase;
  color: var(--muted);
  margin-top: 5px;
  word-break: break-word;
}}

/* ── receipt ──────────────────────────────────────────── */
.receipt {{
  margin-top: 64px;
  border-top: 2px solid var(--gold);
  padding-top: 22px;
}}
.receipt dl {{
  display: grid;
  grid-template-columns: 150px 1fr;
  gap: 9px 18px;
  margin: 0;
  font-family: var(--mono);
  font-size: 12px;
}}
.receipt dt {{
  color: var(--muted);
  font-size: 10.5px;
  letter-spacing: .14em;
  text-transform: uppercase;
  padding-top: 2px;
}}
.receipt dd {{ margin: 0; color: var(--ink-2); word-break: break-all; }}
.receipt dd b {{ color: var(--v4); font-weight: 600; }}
.caveat {{
  font-family: var(--serif);
  font-style: italic;
  font-size: 15px;
  color: var(--muted);
  max-width: 64ch;
  margin: 26px 0 0;
  padding-top: 20px;
  border-top: 1px solid var(--hairline);
}}

@media (max-width: 720px) {{
  .mast-grid {{ grid-template-columns: 1fr; }}
  .turnstile {{ line-height: .9; }}
  .ax {{ grid-template-columns: 1fr; }}
  .receipt dl {{ grid-template-columns: 1fr; }}
  .key-row {{ grid-template-columns: 14px 20px 1fr auto; }}
  .key-fn {{ display: none; }}
  .laws {{ grid-template-columns: 1fr; }}
}}
</style>

<div class="plate">

  <header class="mast">
    <p class="eyebrow">HELEN OS · kernel constitution · WULmath compression</p>
    <div class="mast-grid">
      <p class="turnstile" aria-hidden="true">⊬<small>does not<br>entail</small></p>
      <div>
        <h1>The 108 Refusals</h1>
        <p class="standfirst">{KERNEL_LOC:,} lines of governed kernel reduce to {PROBES} statements, because
        almost everything the constitution does is refuse an entailment. Each line below is one
        adversarial probe in <span style="font-family:var(--mono);font-size:.92em">verify.py</span>
        that runs, attacks the kernel, and is refused. Colour is the sigil vibration; the mono label
        under each line carries the same information, because no state is encoded by colour alone.</p>
      </div>
    </div>

    <div class="axioms">
      <div class="ax">
        <span class="ax-k">Master law</span>
        <span class="ax-v">Compute <span class="yes">⊢</span> ΔRepresentation &nbsp;·&nbsp; Compute <span class="no">⊬</span> ΔReality &nbsp;·&nbsp; Witness ∘ Admit <span class="yes">⊢</span> ΔReality</span>
      </div>
      <div class="ax">
        <span class="ax-k">Admission</span>
        <span class="ax-v">Admit ⟺ PROOF ∧ SCOPE ∧ AUTHORITY ∧ REPLAY &nbsp;·&nbsp; C₅ unearned, completeness = UNKNOWN</span>
      </div>
      <div class="ax">
        <span class="ax-k">Frontier</span>
        <span class="ax-v">□(¬illegal mutation) ∧ ◇(critical reachable obligation ⇒ resolution)</span>
      </div>
      <div class="ax">
        <span class="ax-k">Separation</span>
        <span class="ax-v">Retain <span class="no">⊬</span> Admit <span class="no">⊬</span> Authorize &nbsp;·&nbsp; three predicates, never one</span>
      </div>
    </div>

    <div class="census">
      <div class="cell"><span class="cell-n">{KERNEL_LOC:,}</span><span class="cell-l">kernel LOC</span></div>
      <div class="cell"><span class="cell-n">{CONST_LOC:,}</span><span class="cell-l">constitution</span></div>
      <div class="cell"><span class="cell-n">{TEST_LOC:,}</span><span class="cell-l">test LOC</span></div>
      <div class="cell"><span class="cell-n">{REFUSALS}</span><span class="cell-l">refusal codes</span></div>
      <div class="cell hi"><span class="cell-n">{PROBES}</span><span class="cell-l">probes held</span></div>
      <div class="cell hi"><span class="cell-n">{RATIO:.0f}:1</span><span class="cell-l">LOC per law</span></div>
    </div>
  </header>

  <section class="key">
    <p class="section-label">Vibration key — <span style="text-transform:none;letter-spacing:0;font-family:var(--serif);font-style:italic;font-size:14px">colour → function, from design/skill_sigil_tokens.json</span></p>
    <ul>
{key_rows}
    </ul>
  </section>

{strata}

  <footer class="receipt">
    <p class="section-label">Receipt</p>
    <dl>
      <dt>Verdict</dt><dd><b>CONSTITUTION_HELD</b> · {PROBES}/{PROBES} probes refused their attack</dd>
      <dt>Gate receipt</dt><dd>{RECEIPT}</dd>
      <dt>Source</dt><dd>helen_os/kernel/constitution/verify.py · names extracted verbatim from _probes()</dd>
      <dt>Standing</dt><dd>authority = false · canon = false · ledger_effect = none · (dP, dA, dE) = (0, 0, 0)</dd>
      <dt>Non-delta</dt><dd>2 pre-existing failures in helen_os/tests/test_surface_grammar.py, unrelated to this plate and not fixed</dd>
    </dl>
    <p class="caveat">This page is a representation. It compresses the constitution; it does not hold it —
    the holding is done by the probes, in the gate, on each run. A compression that could not be
    re-derived from the source would be a seal without an admission, and the last of the 108 laws is
    exactly the rule that a control which cannot fail reports nothing when it passes.</p>
  </footer>

</div>
'''

open("helen_wulmath.html", "w", encoding="utf-8").write(DOC)
print("bytes:", len(DOC.encode()), "| laws rendered:", sum(len(by_vib[v]) for v in VIB))
