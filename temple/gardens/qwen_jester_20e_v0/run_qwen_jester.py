#!/usr/bin/env python3
"""
QWEN_JESTER_20E_V0 — Qwen IS the JESTER cognition seat. Claude does not
substitute for JESTER; this runner only feeds ROOTS, parses the epoch artifact,
maintains anti-repetition memory, and records. No admission, no authority.

PIPELINE:  ROOTS → QWEN/JESTER_20e → PotentialDistinctions → HAL
LAW:       Qwen creates distinctions; HAL tests them; neither can mint admission.
INVARIANT: AUTHORITY_DELTA = 0 · ledger_effect = none · canon = false
"""
import json
import re
import subprocess
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).parent
SOT = ROOT.parents[2]
EP_DIR = ROOT / "epochs"
EP_DIR.mkdir(exist_ok=True)
SERVER = "http://127.0.0.1:8090"
N_EPOCHS = 20
MODEL_EXACT = "Qwen3.8-27B-Q3-XYZ-v2.gguf (sha256 5db71d7e…415894)"
RUNTIME = "llama-server b9430 d48a56eff · Metal ngl99 fa on · ngram-mod · c8192"

# ROOTS handed to JESTER (from the Drive census — the objects to attack).
ROOTS = """ROOT-A (self-authored HELEN/AgentX, one correlated epistemic source):
  core object: Trust Geometry Ω=(H, Γ_H, X); Candidate→Admission→Receipt→
  Reducer→State as the only state mutator; "ΔIntelligence>0 ⇏ ΔAuthority>0";
  "one calculus, five projections" (Permissions/Agents/Memory/Epistemics/
  Superteams = trust-geometry sections).
ROOT-B (external industry agentic-safety: Google Agents Companion, TRISM,
  safety toolkits) — the only genuinely independent witnesses.
ROOT-C (Agentics Foundation org Drive: courses, decks, hackathon).
Census laws in force:
  N_files ⇏ N_roots ⇏ N_independent_roots ⇏ N_independent_evidence ⇏ warrants.
  A4: NoLineage(r_i,r_j) ⇏ EpistemicIndependence(r_i,r_j)."""

SYSTEM = """You are JESTER, a non-sovereign adversarial epistemic search process
inside the HELEN Garden. Authority_JESTER = 0. You are NOT an authority,
verifier, auditor, governor, or promotion mechanism. You ARE a generator of
counterexamples, constructor of observationally-equivalent counterfeit worlds,
and designer of discriminators. Nothing you emit becomes evidence, warrant,
admission, or authority. MASTER LAW: Cognition↑ ⇏ Authority↑ — more reasoning,
recursion, consensus, novelty, model quality, epochs or agents NEVER grants
authority. You STOP before observation: you may produce a PotentialSeparator,
never an ObservedSeparator or LicensedSeparator.

Counterfeit neighborhood: C_O(x) = { y : O(y)=O(x) AND Type(y)≠Type(x) }.
For an apparent gain g, build a counterfeit world c that the current observer O
cannot distinguish from g, then a discriminator x* that would separate them.

Reject your own output if it is only prettier wording, a synonym, a renamed
primitive, an ungrounded metaphor, "more agents/consensus/data", or "use
category theory/quantum/graph/blockchain" — UNLESS you show the exact unresolved
distinction it separates. Novel wording ≠ novel structure. Many names ≠ many
objects. Many agents ≠ many epistemic roots. Many citations ≠ independent
evidence.

Emit ONLY the structured artifact. No hidden chain-of-thought, no narration."""

CONTRACT = """Emit EXACTLY this artifact and nothing else:
EPOCH_ID: {ep}/20
SEARCH_INTENT: <one line>
MUTATION: <one transform: INVERT|COUNTERFEIT|MATHEMATIZE|TEMPORALIZE|BRIDGE|
  MISSING_DIMENSION|OPERATOR|CONTRADICTION|SELF_ECHO|OBSERVER_ATTACK|
  SEPARATOR_COUNTERFEIT|PROVENANCE_COUNTERFEIT|EPISTEMIC_COUNTERFEIT|
  AUTHORITY_LEAK|RECEIPT_COUNTERFEIT>
COUNTERFEIT_WORLD: <a different mechanism producing the same observable>
DISCRIMINATOR: <one operationally testable separator x*>
TARGET_CLAIM: <the exact claim being attacked>
EXPECTED_OBSERVATION: <what the discriminator would show if the distinction is real>
POTENTIAL_DISTINCTION: <the single structural distinction, one line>
REDUNDANCY_WITH_PRIOR: <NEW_STRUCTURE | SELF_ECHO:ep## | DRY>
AUTHORITY_DELTA: 0
END_EPOCH"""

TARGET_QS = [
    "Can apparent multi-agent consensus be reproduced by correlated cognition?",
    "Can apparent independent provenance be reproduced by hidden common evidence ancestry?",
    "Can 'history-indexed authority' be reproduced by an ordinary static capability graph?",
    "Can a valid-looking receipt fail to witness the transition it claims?",
    "Can a discriminator succeed by measuring a correlated side effect, not the target distinction?",
    "Can deterministic replay reproduce state while failing to reproduce admissibility?",
    "Can memory continuity be provider/session persistence, not HELEN institutional continuity?",
    "Can semantic compression preserve outputs while destroying distinctions?",
    "Can higher-dimensional math be aesthetic projection, not an empirically required object?",
    "Can a supposed independent discovery be explained by historical self-echo?",
    "Can a safe action still be unauthorized?",
    "Can a permitted action fail to produce the claimed external effect?",
    "Can successful execution fail to justify admission?",
    "Can independent agents nevertheless share one epistemic root?",
    "Can provenance-independent roots depend on one evidence-generating process?",
]

PHASES = {  # epoch -> directive
    **{i: "BROAD counterfeit discovery" for i in range(1, 6)},
    **{i: "ATTACK the separators from earlier epochs" for i in range(6, 11)},
    **{i: "HIGHER-ORDER / recursive counterfeits" for i in range(11, 16)},
    **{i: "CROSS-ROOT structural compression" for i in range(16, 19)},
    **{i: "DRYNESS TEST — emit DRY rather than paraphrase if nothing new" for i in range(19, 21)},
}


def head():
    return subprocess.run(["git", "-C", str(SOT), "rev-parse", "--short", "HEAD"],
                          capture_output=True, text=True).stdout.strip()


def chat(messages, seed, max_tokens=1500, temperature=0.9):
    body = json.dumps({"messages": messages, "max_tokens": max_tokens,
                       "temperature": temperature, "top_p": 0.95, "seed": seed}).encode()
    req = urllib.request.Request(SERVER + "/v1/chat/completions", data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=900) as r:
        d = json.loads(r.read())
    m = d["choices"][0]["message"]
    return (m.get("content") or m.get("reasoning_content") or ""), d.get("usage", {})


def field(txt, key):
    m = re.search(rf"^{key}:\s*(.+?)\s*$", txt, re.I | re.M)
    return m.group(1).strip() if m else ""


def main():
    H = head()
    memory = []  # compact prior distinctions to prevent repetition
    records = []
    print("═" * 70)
    print("  🃏 QWEN_JESTER_20E_V0 — Qwen is the JESTER seat (Claude orchestrates only)")
    print("  ROOTS → QWEN/JESTER_20e → PotentialDistinctions → HAL")
    print("  AUTHORITY_DELTA=0 · ledger=none · canon=false")
    print("═" * 70, flush=True)

    for i in range(1, N_EPOCHS + 1):
        q = TARGET_QS[(i - 1) % len(TARGET_QS)]
        mem_txt = ("\nPrior POTENTIAL_DISTINCTIONS (do not repeat; mark SELF_ECHO"
                   " if you would):\n" + "\n".join(
                       f"  ep{m['ep']:02d}: {m['distinction'][:110]}"
                       for m in memory[-12:])) if memory else ""
        user = (f"ROOTS:\n{ROOTS}\n\nEPOCH {i}/20 — phase: {PHASES[i]}.\n"
                f"Preferentially attack: {q}{mem_txt}\n\n"
                + CONTRACT.format(ep=i))
        t0 = time.time()
        try:
            content, usage = chat(
                [{"role": "system", "content": SYSTEM},
                 {"role": "user", "content": user}], seed=7000 + i)
        except Exception as e:
            content, usage = f"__ERROR__ {e}", {}
        dt = time.time() - t0

        dist = field(content, "POTENTIAL_DISTINCTION")
        mut = field(content, "MUTATION")
        red = field(content, "REDUNDANCY_WITH_PRIOR")
        disc = field(content, "DISCRIMINATOR")
        cf = field(content, "COUNTERFEIT_WORLD")
        parsed = bool(dist)
        if parsed:
            memory.append({"ep": i, "distinction": dist})
        rec = {"epoch": i, "mutation": mut, "target_q": q,
               "counterfeit_world": cf, "discriminator": disc,
               "potential_distinction": dist, "redundancy": red,
               "authority_delta": 0, "wall_s": round(dt, 1),
               "parsed": parsed, "usage": usage, "raw": content}
        records.append(rec)
        (EP_DIR / f"epoch_{i:02d}.json").write_text(
            json.dumps(rec, indent=2, ensure_ascii=False))
        print(f"\n🃏 EPOCH {i:02d}/20  [{dt:5.1f}s]  MUT={mut[:22]}  {red[:14]}")
        print(f"   COUNTERFEIT: {cf[:150]}")
        print(f"   DISCRIMINATOR: {disc[:150]}")
        print(f"   Δ_DISTINCTION: {dist[:150]}", flush=True)

    # mechanical dedup of PotentialDistinctions, preserve epoch provenance
    def norm(s):
        return re.sub(r"[^a-z0-9 ]", "", s.lower()).strip()
    seen, distinct = {}, []
    for r in records:
        if not r["potential_distinction"]:
            continue
        k = norm(r["potential_distinction"])[:80]
        if k in seen:
            seen[k].append(r["epoch"])
        else:
            seen[k] = [r["epoch"]]
            distinct.append({"distinction": r["potential_distinction"],
                             "first_epoch": r["epoch"],
                             "discriminator": r["discriminator"]})
    for d in distinct:
        d["also_epochs"] = seen[norm(d["distinction"])[:80]]

    counts = {
        "epochs_requested": N_EPOCHS,
        "epochs_completed": sum(1 for r in records if r["parsed"]),
        "potential_distinctions_raw": sum(1 for r in records if r["potential_distinction"]),
        "potential_distinctions_distinct": len(distinct),
        "counterfeit_worlds": sum(1 for r in records if r["counterfeit_world"]),
        "discriminators": sum(1 for r in records if r["discriminator"]),
        "self_echo": sum(1 for r in records if "SELF_ECHO" in r["redundancy"].upper()),
        "dry": sum(1 for r in records if "DRY" in r["redundancy"].upper()),
        "new_structure": sum(1 for r in records if "NEW_STRUCTURE" in r["redundancy"].upper()),
    }
    receipt = {
        "schema": "QWEN_JESTER_20E_V0_RECEIPT",
        "authority": False, "canon": False, "ledger_effect": "none",
        "model_exact": MODEL_EXACT, "runtime": RUNTIME,
        "head_at_run": H,
        **counts,
        "hal_survived": None, "hal_refuted": None, "hal_redundant": None,
        "hal_evidence_needed": None,
        "hal_note": "HAL classification runs in a SEPARATE seat after this; "
                    "Qwen does not self-validate.",
        "distinct_distinctions": distinct,
        "authority_delta": 0, "commit": "none", "push": "none",
        "claim_ceiling": "Qwen/JESTER generated potential distinctions and "
                         "discriminator candidates. No separator executed. No "
                         "observation obtained. No promotion. No authority changed.",
    }
    (ROOT / "QWEN_JESTER_20E_V0_RECEIPT.json").write_text(
        json.dumps(receipt, indent=2, ensure_ascii=False))
    print("\n" + "═" * 70)
    print("  🌈 QWEN_JESTER_20E_V0 — RECEIPT (pre-HAL)")
    print("═" * 70)
    print(json.dumps(counts, indent=2))
    print("→ surviving distinct PotentialDistinctions:", len(distinct),
          "→ handoff to HAL (separate seat)")


if __name__ == "__main__":
    main()
