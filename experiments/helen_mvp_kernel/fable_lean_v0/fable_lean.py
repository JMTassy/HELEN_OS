"""FABLE_LEAN_V0 — production-only adaptive cognition controller. authority=false · canon=false · ledger_effect=none.
NON-SOVEREIGN. Explicitly SEPARATE from SCALE_V1 (the measurement instrument). FABLE optimizes (k, roles, budgets,
stopping) — it MUST NOT optimize/relax/simulate Gamma_A. Pipeline STOPS at CANDIDATE.

    FREEZE -> A+B (mandatory scouts) -> GATE -> OPTIONAL(C,D,E) -> DEDUP -> HAL -> CANDIDATE ══seam══ (no effect)

Seals:  FREE GOBLINS · HARD GATES · LAZY SPAWNING · SHORT RECEIPTS · SKIPPED CHECKS ARE RECEIPTED CHECKS.
Objective: ExpectedEarnedInformationGain/token — Spawn(G_i) iff E[dN_earned|G_i]/Cost > lambda (V0 = rule-based prior).

Constitution lives HERE (controller boundary), injected once — not replicated per goblin. Each goblin only inherits:
    FREE COGNITION · NO AUTHORITY MINTING · TYPE SPECULATION · STRICT OUTPUT CONTRACT · NO DIRECT STATE EFFECT
"""
import argparse, hashlib, json, pathlib, re, sys
from dataclasses import dataclass, field, asdict
from typing import Optional

HERE = pathlib.Path(__file__).resolve().parent
POLICY = json.loads((HERE / "SPAWN_POLICY.json").read_text())
CONSTITUTION = ["FREE COGNITION", "NO AUTHORITY MINTING", "TYPE SPECULATION", "STRICT OUTPUT CONTRACT", "NO DIRECT STATE EFFECT"]
CLAIM_CLASSES = {"OBSERVED", "INFERRED", "PROPOSAL", "UNKNOWN"}

def _h(o): return "sha256:" + hashlib.sha256(json.dumps(o, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:16]
def canon(s): return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", "", (s or "").lower())).strip()

@dataclass
class Packet:
    ID: str
    STATUS: str = "COMPLETE"          # COMPLETE | TRUNCATED | RUNTIME_FAILED
    CLAIM_CLASS: str = "UNKNOWN"
    FINDINGS: list = field(default_factory=list)   # <=3
    NOVEL: list = field(default_factory=list)      # <=3
    ROOTS: list = field(default_factory=list)
    FALSIFIERS: list = field(default_factory=list) # <=3
    RISKS: list = field(default_factory=list)      # <=3
    NEXT_TEST: str = ""
    signals: dict = field(default_factory=dict)    # scouts only
    authority: bool = False
    ledger_effect: str = "none"

    def complete(self) -> bool:
        # GOBLIN_OUTPUT_COMPLETE minted ONLY on field completeness — NEVER on runtime exit success.
        if self.STATUS != "COMPLETE": return False
        if self.CLAIM_CLASS not in CLAIM_CLASSES: return False
        caps = len(self.FINDINGS) <= 3 and len(self.NOVEL) <= 3 and len(self.FALSIFIERS) <= 3 and len(self.RISKS) <= 3
        return bool(caps and self.FINDINGS and self.NOVEL and self.NEXT_TEST)

    def render(self) -> dict:
        d = asdict(self); d["COMPLETE"] = self.complete(); return d

# ── DRY-RUN stub scouts (deterministic; no model, no server) — a scenario exercising BOTH spawn and skip ──
def stub_goblin(role: str) -> Packet:
    if role == "A_ARCHITECT":
        return Packet("A_ARCHITECT", CLAIM_CLASS="PROPOSAL",
            FINDINGS=["candidate decomposes into a checkable seam", "an interface boundary is implied"],
            NOVEL=["the amplification law is expressible as one executable seam"],
            ROOTS=["input:frozen"], FALSIFIERS=["no seam separates authority from content"],
            RISKS=["abstraction may hide a real coupling"], NEXT_TEST="build the minimal seam + one bypass mutant",
            signals={"buildable": True, "empirical_testable": False, "promotion_or_risk": False})
    if role == "B_FALSIFIER":
        return Packet("B_FALSIFIER", CLAIM_CLASS="INFERRED",
            FINDINGS=["the claim has an authority surface that could be laundered"],
            NOVEL=["a summary step is where authority could silently inflate"],
            ROOTS=["input:frozen"], FALSIFIERS=["show a transform that raises authority with a valid witness"],
            RISKS=["HIGH: authority-laundering via consolidation"], NEXT_TEST="attempt an illegitimate promotion and locate the stopping boundary",
            signals={"buildable": False, "empirical_testable": False, "promotion_or_risk": True})
    if role == "C_BUILDER":
        return Packet("C_BUILDER", CLAIM_CLASS="PROPOSAL",
            FINDINGS=["minimal seam is ~1 module + kill-suite"],
            NOVEL=["Capability-minting gate reused from vertical_slice pattern"],
            ROOTS=["input:frozen"], FALSIFIERS=["seam not load-bearing if bypass mutant survives"],
            RISKS=["HMAC-modeled, not OS-isolated"], NEXT_TEST="one bypass mutant must die",
            signals={})
    if role == "E_ADVERSARY":
        return Packet("E_ADVERSARY", CLAIM_CLASS="INFERRED",
            FINDINGS=["consensus could be mistaken for corroboration"],
            NOVEL=["fan-out of one root across 5 agents fakes independence"],
            ROOTS=["input:frozen"], FALSIFIERS=["independent-root count > 1 defeats the attack"],
            RISKS=["HIGH: pseudo-corroboration"], NEXT_TEST="dedup to independent roots before any HAL trust",
            signals={})
    return Packet(role, STATUS="RUNTIME_FAILED")

def live_goblin(role: str, task: str) -> Packet:
    # Live mode intentionally not wired in the BUILD commit — would call the 9B with the role's hard budget,
    # enable_thinking:false, no auto-rescue. Dry-run proves the CONTROLLER; live cognition is a separate verb.
    raise NotImplementedError("live mode requires an explicit RUN verb + server; dry-run proves the controller.")

def gate(scouts: list) -> dict:
    """Pure function of scout signals. Returns per-conditional-role decision + evidence."""
    agg = {k: any(bool(s.signals.get(k)) for s in scouts) for k in POLICY["gate_signal_keys"]}
    need = {
        "C_BUILDER": agg["buildable"],
        "D_EXPERIMENTER": agg["empirical_testable"],
        "E_ADVERSARY": agg["promotion_or_risk"],
    }
    return {"aggregate_signals": agg, "need": need}

def run(dry: bool, task: str, outdir: pathlib.Path):
    outdir.mkdir(parents=True, exist_ok=True)
    trace = {"controller": "FABLE_LEAN_V0", "mode": "DRY_RUN" if dry else "LIVE", "constitution": CONSTITUTION,
             "task": task, "task_hash": _h(task), "separation": "SEPARATE FROM SCALE_V1 — no benchmark contamination",
             "spawn_receipts": [], "skip_receipts": [], "packets": {}, "gate": {}, "candidate": {}, "terminal": {}}
    goblin = stub_goblin if dry else (lambda r: live_goblin(r, task))
    B = POLICY["budgets_tokens"]; EIGm = POLICY["eig_prior_mandatory"]; cond = POLICY["conditional_roles"]

    # ── mandatory scouts A + B ──
    scouts = []
    for r in POLICY["mandatory_roles"]:
        p = goblin(r); scouts.append(p); trace["packets"][r] = p.render()
        trace["spawn_receipts"].append({"type": "SPAWN_RECEIPT", "role": r, "decision": "SPAWN", "trigger": "mandatory",
            "expected_information_gain": EIGm[r], "budget_tokens": B[r], "scope": trace["task_hash"], "evidence": "scout"})

    # ── GATE (pure fn of A+B signals) → OPTIONAL(C,D,E), receipting BOTH spawn and skip ──
    g = gate(scouts); trace["gate"] = g
    specialists = []
    for r, spec in cond.items():
        fired = g["need"][r]; ev = {k: g["aggregate_signals"][k] for k in g["aggregate_signals"]}
        if fired:
            p = goblin(r); specialists.append(p); trace["packets"][r] = p.render()
            trace["spawn_receipts"].append({"type": "SPAWN_RECEIPT", "role": r, "decision": "SPAWN",
                "trigger": spec["trigger"], "expected_information_gain": spec["eig_prior"],
                "budget_tokens": B[r], "scope": trace["task_hash"], "evidence": ev})
        else:
            trace["skip_receipts"].append({"type": "SKIP_RECEIPT", "role": r, "decision": "SKIP",
                "reason": "trigger not satisfied: " + spec["trigger"], "evidence": ev})

    # ── DEDUP before HAL (anti-fan-out): distinct canonical NOVEL propositions + independent-root count ──
    allp = scouts + specialists
    clusters = {}
    for p in allp:
        for nov in p.NOVEL:
            key = canon(nov)
            c = clusters.setdefault(key, {"proposition": nov, "goblins": [], "roots": set()})
            c["goblins"].append(p.ID); c["roots"].update(canon(x) for x in p.ROOTS)
    distinct = []
    for key, c in clusters.items():
        indep = len(c["roots"])
        distinct.append({"proposition": c["proposition"], "reproduced_by": sorted(set(c["goblins"])),
                         "independent_root_count": indep,
                         "pseudo_corroboration": len(set(c["goblins"])) > 1 and indep <= 1})

    # ── HAL sees ONLY distinct canonical propositions (stub verdict in dry-run, clearly marked) ──
    hal = []
    for d in distinct:
        verdict = "SURVIVED" if d["independent_root_count"] >= 1 else "INCONCLUSIVE"
        hal.append({"proposition": d["proposition"], "verdict": verdict, "hal": "STUB_DRY_RUN" if dry else "LIVE"})

    # ── CANDIDATE (separate 🟣 INTERESTING vs 🟢 SUPPORTED); NEVER admitted. Institutional seam = STOP. ──
    interesting = [d["proposition"] for d in distinct]
    supported = [h["proposition"] for h in hal if h["verdict"] == "SURVIVED" and not any(
        d["pseudo_corroboration"] and d["proposition"] == h["proposition"] for d in distinct)]
    earned = len(supported)  # candidate-level only; admission NOT performed
    trace["candidate"] = {"INTERESTING_purple": interesting, "SUPPORTED_green_candidate": supported,
        "distinct": distinct, "hal_trials": hal,
        "seam": "INSTITUTIONAL SEAM — STOP. No Gamma_A. authority=false. HAL_SURVIVED != TRUE != ADMITTED."}

    swarm_complete = all(p.complete() for p in scouts)
    trace["terminal"] = {"type": "FABLE_LEAN_V0_TERMINAL",
        "A_ARCHITECT": "COMPLETE" if scouts[0].complete() else "INCOMPLETE",
        "B_FALSIFIER": "COMPLETE" if scouts[1].complete() else "INCOMPLETE",
        "C_BUILDER": "COMPLETE" if any(p.ID == "C_BUILDER" and p.complete() for p in specialists) else ("SKIPPED" if not g["need"]["C_BUILDER"] else "INCOMPLETE"),
        "D_EXPERIMENTER": "COMPLETE" if any(p.ID == "D_EXPERIMENTER" and p.complete() for p in specialists) else ("SKIPPED" if not g["need"]["D_EXPERIMENTER"] else "INCOMPLETE"),
        "E_ADVERSARY": "COMPLETE" if any(p.ID == "E_ADVERSARY" and p.complete() for p in specialists) else ("SKIPPED" if not g["need"]["E_ADVERSARY"] else "INCOMPLETE"),
        "SWARM_COMPLETE": "YES" if swarm_complete else "NO",
        "DISCRIMINATION": "ALLOWED" if swarm_complete else "BLOCKED",
        "EARNED_CHIDDUSH": earned if swarm_complete else "NOT_EVALUABLE",
        "AUTHORITY": False, "CANON": False, "LEDGER_EFFECT": "none",
        "INSTITUTIONAL_ADMISSION": "NOT_PERFORMED", "COMMIT": "none", "PUSH": "none"}

    (outdir / "trace.json").write_text(json.dumps(trace, indent=2, default=str))
    (outdir / "spawn_receipts.json").write_text(json.dumps(trace["spawn_receipts"], indent=2))
    (outdir / "skip_receipts.json").write_text(json.dumps(trace["skip_receipts"], indent=2, default=str))
    (outdir / "terminal_receipt.json").write_text(json.dumps(trace["terminal"], indent=2))

    print("=== FABLE_LEAN_V0 DRY-RUN TRACE ===" if dry else "=== FABLE_LEAN_V0 LIVE ===")
    print("spawned:", [r["role"] for r in trace["spawn_receipts"]])
    print("skipped:", [(r["role"], r["reason"]) for r in trace["skip_receipts"]])
    print("gate.aggregate_signals:", g["aggregate_signals"])
    print("distinct props:", len(distinct), "· pseudo_corroboration:", [d["proposition"] for d in distinct if d["pseudo_corroboration"]])
    print("candidate SUPPORTED(green):", supported)
    t = trace["terminal"]
    print(f"SWARM_COMPLETE={t['SWARM_COMPLETE']} DISCRIMINATION={t['DISCRIMINATION']} EARNED_CHIDDUSH={t['EARNED_CHIDDUSH']} "
          f"ADMISSION={t['INSTITUTIONAL_ADMISSION']} AUTHORITY={t['AUTHORITY']}")
    print("artifacts:", sorted(p.name for p in outdir.iterdir()))
    print("DONE_FABLE_LEAN")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--task", default="Make Authority(T(x)) <= Authority(x) executable as one seam.")
    ap.add_argument("--out", default=str(HERE / "run_dry"))
    a = ap.parse_args()
    if not a.dry_run:
        print("LIVE mode requires an explicit RUN verb + server. Use --dry-run to exercise the controller."); sys.exit(2)
    run(True, a.task, pathlib.Path(a.out))

if __name__ == "__main__":
    main()
