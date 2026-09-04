"""UI_INVARIANT_LINT_V0 — authority=false · canon=false · ledger_effect=none · NON_SOVEREIGN.
Executable subset of HELEN_INTERFACE_CONSTITUTION_V0. A quality FLOOR for surfaces emitted by HER/HAL/Goblin/external
agents. Enforces mechanically-checkable INVARIANTS only; never PREFERENCES.

  Required non-interference property:  InvariantViolation ⇒ Reject   ∧   PreferenceVariation ⇒ Permit
                                       ⇒  StyleDifference ⊬ Violation

Honesty rule: a check that cannot be reliably decided from static syntax is NOT pretended to be ENFORCED.
Classification: ENFORCED (reliable static) · PARTIAL (heuristic, JS-attached escapes) · DOCUMENT_ONLY (not statically decidable).
Companion doc: docs/proposals/HELEN_INTERFACE_CONSTITUTION_V0.md
"""
import re, json, hashlib, pathlib

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "her_run"

INTERACTIVE = ("button", "a", "input", "select", "textarea", "summary")
STATE_WORDS = ("deny", "reject", "error", "danger", "success", "admit", "pass", "fail", "warn")
RAW_STATE_COLOR = r"(?:red|green|crimson|lime|#f00\b|#0f0\b|#ff0000\b|#00ff00\b)"

RULES = {  # id -> (class, description)
    "UI001": ("ENFORCED",      "transition:all forbidden — name exact properties"),
    "UI002": ("PARTIAL",       "primitive state-colour in a state-named rule (bypasses semantic token)"),
    "UI003": ("ENFORCED",      "outline suppression without :focus-visible replacement"),
    "UI004": ("ENFORCED",      "positive tabindex"),
    "UI005": ("PARTIAL",       "clickable non-semantic div/span without keyboard semantics"),
    "UI006": ("ENFORCED",      "non-essential motion without a prefers-reduced-motion guard"),
    "UI007": ("DOCUMENT_ONLY", "dynamic metric without tabular-nums (not statically decidable)"),
    "UI008": ("DOCUMENT_ONLY", "hardcoded state-colour bypassing token (semantics not statically decidable)"),
    "UI009": ("ENFORCED",      "aria-hidden=true on a focusable/interactive control"),
    "UI010": ("PARTIAL",       "icon-only button without an accessible name"),
}

def _line(text, idx): return text.count("\n", 0, idx) + 1
def _f(check, line, severity, why, fix):
    return {"check": check, "class": RULES[check][0], "location": f"line {line}", "severity": severity, "why": why, "auto_fix_safe": fix}

def lint(text):
    """Return list of findings (FAIL/WARN). PASS = empty for that rule. INFO observations are separate (see lint_report)."""
    F = []
    low = text.lower()

    # UI001 transition:all — ENFORCED
    for m in re.finditer(r"transition(?:-property)?\s*:\s*all\b", low):
        F.append(_f("UI001", _line(text, m.start()), "FAIL", "transition:all animates unknown future properties", False))

    # UI003 outline suppression without focus-visible — ENFORCED (file-level)
    supp = list(re.finditer(r"outline\s*:\s*(?:none|0)\b", low))
    if supp and ":focus-visible" not in low:
        F.append(_f("UI003", _line(text, supp[0].start()), "FAIL", "outline removed with no :focus-visible replacement", False))

    # UI004 positive tabindex — ENFORCED
    for m in re.finditer(r'tabindex\s*=\s*["\']?([0-9]+)', low):
        if int(m.group(1)) > 0:
            F.append(_f("UI004", _line(text, m.start()), "FAIL", f'positive tabindex={m.group(1)} hijacks tab order', True))

    # UI006 non-essential motion without reduced-motion guard — ENFORCED (file-level, conservative floor)
    has_motion = bool(re.search(r"@keyframes\b", low) or re.search(r"animation\s*:", low)
                      or re.search(r"transition\s*:\s*(?!none)", low))
    has_guard = "prefers-reduced-motion" in low
    if has_motion and not has_guard:
        F.append(_f("UI006", 1, "FAIL", "declared motion with no prefers-reduced-motion guard (cannot statically prove essential)", False))

    # UI009 aria-hidden=true on focusable/interactive — ENFORCED
    for m in re.finditer(r"<([a-z0-9]+)\b([^>]*)>", low):
        tag, attrs = m.group(1), m.group(2)
        if 'aria-hidden' in attrs and re.search(r'aria-hidden\s*=\s*["\']?true', attrs):
            tabm = re.search(r'tabindex\s*=\s*["\']?(-?[0-9]+)', attrs)
            focusable = tag in INTERACTIVE or (tabm and int(tabm.group(1)) >= 0)
            if focusable:
                F.append(_f("UI009", _line(text, m.start()), "FAIL", f"aria-hidden=true on focusable <{tag}> — hides it from AT but not keyboard", False))

    # UI002 primitive state-colour in a state-named context — PARTIAL
    for m in re.finditer(r"(color|background(?:-color)?)\s*:\s*" + RAW_STATE_COLOR, low):
        # find the enclosing selector/line; flag only if a state-word is present nearby (same 120 chars back)
        ctx = low[max(0, m.start() - 120): m.start()]
        if any(w in ctx for w in STATE_WORDS) and "var(" not in low[m.start(): m.start() + 40]:
            F.append(_f("UI002", _line(text, m.start()), "FAIL", "raw status colour bound to a state-named rule instead of a semantic token", False))

    # UI005 clickable non-semantic div/span without keyboard semantics — PARTIAL
    for m in re.finditer(r"<(div|span)\b([^>]*)>", low):
        attrs = m.group(2)
        if re.search(r'on click|onclick|@click|v-on:click', attrs.replace(" ", " ")) or "onclick" in attrs or "@click" in attrs:
            if "role=" not in attrs and "tabindex" not in attrs and "onkey" not in attrs:
                F.append(_f("UI005", _line(text, m.start()), "FAIL", f"<{m.group(1)}> with click handler but no role/tabindex/key handler", False))

    # UI010 icon-only <button> without accessible name — PARTIAL
    for m in re.finditer(r"<button\b([^>]*)>(.*?)</button>", text, re.DOTALL | re.IGNORECASE):
        attrs, inner = m.group(1).lower(), m.group(2)
        has_name = ("aria-label" in attrs) or ("aria-labelledby" in attrs) or ("title=" in attrs)
        text_content = re.sub(r"<[^>]+>", "", inner).strip()
        if not has_name and not text_content:
            F.append(_f("UI010", _line(text, m.start()), "WARN", "icon-only button with no aria-label/title/text — no accessible name", False))

    return F

def lint_report(text):
    """Findings + DOCUMENT_ONLY observations (INFO, never FAIL) for a richer fixture report."""
    F = lint(text)
    info = []
    low = text.lower()
    for m in re.finditer(r"<(div|span)\b[^>]*aria-label", low):   # aria-label on non-interactive element (ignored by many AT)
        info.append({"check": "OBS", "class": "DOCUMENT_ONLY", "location": f"line {_line(text, m.start())}",
                     "severity": "INFO", "why": "aria-label on a non-interactive element is ignored by many AT", "auto_fix_safe": False})
    for m in re.finditer(r"height\s*:\s*[0-9]+px", low):          # fixed height on a possible text container
        info.append({"check": "OBS", "class": "DOCUMENT_ONLY", "location": f"line {_line(text, m.start())}",
                     "severity": "INFO", "why": "fixed px height — verify it is not a text container (constitution §7)", "auto_fix_safe": False})
    return F, info

# ── FIXTURES ──────────────────────────────────────────────────────────────
POSITIVE = {  # MUST produce >=1 FAIL on the named rule
    "UI001 transition:all":        ("<style>.x{transition: all .2s ease}</style>", "UI001"),
    "UI004 tabindex=3":            ('<div tabindex="3">x</div>', "UI004"),
    "UI005 div onclick no-kbd":    ('<div onclick="go()">Go</div>', "UI005"),
    "UI002 red as DENY no-state":  ("<style>.deny-badge{color:red}</style>", "UI002"),
    "UI006 anim no reduced-motion":("<style>@keyframes k{to{opacity:1}} .a{animation:k 1s}</style>", "UI006"),
    "UI009 aria-hidden on button": ('<button aria-hidden="true">x</button>', "UI009"),
}
FALSE_POSITIVE = {  # MUST produce ZERO findings — pure PREFERENCE variation
    "serif vs sans":        "<style>body{font-family:Georgia,serif}</style>",
    "warm neutral palette":  "<style>:root{--bg:#f5f0e8}</style>",
    "parchment surface":     "<style>.s{background:#faf8f2}</style>",
    "border radius choice":  "<style>.c{border-radius:14px}</style>",
    "garden decorative accent":"<style>.accent{color:#7a5cff}</style>",
}

def main():
    print("=== UI_INVARIANT_LINT_V0 — self-test ===\n")
    n_enf = sum(1 for c in RULES.values() if c[0] == "ENFORCED")
    n_par = sum(1 for c in RULES.values() if c[0] == "PARTIAL")
    n_doc = sum(1 for c in RULES.values() if c[0] == "DOCUMENT_ONLY")

    print("  POSITIVE FIXTURES (InvariantViolation ⇒ Reject):")
    pos_ok = True
    for name, (html, want) in POSITIVE.items():
        hits = {f["check"] for f in lint(html)}
        ok = want in hits
        pos_ok &= ok; print(f"    {'PASS' if ok else 'FAIL'}  {name}  → fired {sorted(hits) or '∅'} (want {want})")

    print("\n  FALSE-POSITIVE CONTROLS (PreferenceVariation ⇒ Permit):")
    fp_ok = True
    for name, html in FALSE_POSITIVE.items():
        hits = lint(html)
        ok = len(hits) == 0
        fp_ok &= ok; print(f"    {'PASS' if ok else 'FAIL'}  {name}  → {len(hits)} findings (want 0)")

    print("\n  FIRST FIXTURE — her_netart_v0.html (evidence only, no auto-fix):")
    fx = HERE / "her_netart_v0.html"
    findings, info, fixture_present = [], [], fx.exists()
    if fixture_present:
        findings, info = lint_report(fx.read_text())
        if not findings: print("    ENFORCED/PARTIAL: CLEAN (0 FAIL/WARN)")
        for f in findings: print(f"    [{f['severity']}] {f['check']} {f['location']} — {f['why']} (auto_fix_safe={f['auto_fix_safe']})")
        for o in info:     print(f"    [INFO] {o['check']} {o['location']} — {o['why']}")
    else:
        print("    (fixture absent — skipped)")

    all_ok = pos_ok and fp_ok
    print(f"\n  RULES={len(RULES)} ENFORCED={n_enf} PARTIAL={n_par} DOCUMENT_ONLY={n_doc}")
    print(f"  NEGATIVE_CONTROLS_PASS(positive)={pos_ok} · FALSE_POSITIVE_CONTROLS_PASS={fp_ok} · SELF_TEST={all_ok}")

    receipt = {
        "receipt": "HELEN_INTERFACE_CONSTITUTION_V0_RECEIPT",
        "DOC": "docs/proposals/HELEN_INTERFACE_CONSTITUTION_V0.md",
        "LINTER": "experiments/helen_mvp_kernel/fable_lean_v0/ui_invariant_lint_v0.py",
        "FIXTURE": "her_netart_v0.html",
        "N_RULES": len(RULES), "N_ENFORCED": n_enf, "N_PARTIAL": n_par, "N_DOCUMENT_ONLY": n_doc,
        "TESTS": "positive+false-positive fixtures", "NEGATIVE_CONTROLS": bool(pos_ok),
        "FALSE_POSITIVE_CONTROLS_PASS": bool(fp_ok),
        "HER_NETART_FINDINGS": findings, "HER_NETART_OBSERVATIONS": info, "fixture_present": fixture_present,
        "property": "InvariantViolation ⇒ Reject ∧ PreferenceVariation ⇒ Permit ⇒ StyleDifference ⊬ Violation",
        "SEMANTIC_COLOR_SOT_CHANGED": False, "SECOND_COLOR_ONTOLOGY": False, "SPNI_BOUNDARY_PRESERVED": True,
        "AUTHORITY": False, "CANON": False, "LEDGER_EFFECT": "none",
        "PULL": "NO", "PUSH": "NO", "MODEL_DOWNLOAD": "NO", "MODEL_MUTATION": "NO",
        "RESULT": "SURVIVED_BOUNDED_SELF_TEST" if all_ok else "GAP_FOUND",
        "SelfPassed": bool(all_ok), "PeerAdversaryValidated": False,
    }
    body = json.dumps(receipt, indent=2, ensure_ascii=False)
    receipt["receipt_sha16"] = hashlib.sha256(body.encode()).hexdigest()[:16]
    OUT.mkdir(exist_ok=True)
    (OUT / "ui_invariant_lint_v0_receipt.json").write_text(json.dumps(receipt, indent=2, ensure_ascii=False))
    print(f"  RESULT={receipt['RESULT']} · receipt sha16={receipt['receipt_sha16']}")
    print("  BOUNDARY: authority=false · semantic-colour SOT unchanged · no 2nd ontology · SPNI preserved · proposal only")

if __name__ == "__main__":
    main()
