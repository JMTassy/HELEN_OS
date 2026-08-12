"""The 40-item temporal chiddush benchmark — frozen.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.

Four corpus-volumes, ten items each, delivered in-frame 2026-08-12:

    A  PAT-01..10   Repertory / London Journal <=1850   layer P (CLAIM)
    B  CP-01..10    Official Catalogue 1851             layer D (DEMO)
    C  JUR-01..10   Reports by the Juries 1852          layer J (JUDGMENT)
    D  RAIL-01..10  Board of Trade 1840-1852            layer F (FAILURE)

TWO HASHES, NEVER CONFLATED:

  declared_by_other_lane = ed660c3b...cb49 — the research lane's
      canonical JSON payload hash. NOT verified here: this seat holds
      the packet as delivered TEXT, not those JSON bytes, and the
      sandbox:/mnt/data links are that lane's local filesystem, not a
      fetchable URI. Recorded as a REPORTED claim, exactly as the
      3e0e2b4 Architect commit was.

  freeze_hash_here = computed over THIS reconstruction. It is the
      commitment this seat can honestly make for the 1862 holdout.

THE PACKET FALSIFIED PART OF THIS SEAT'S RECEIVER — recorded, not
hidden. epistemic_layers.compute_sigma models a contiguous ladder
(claimed -> demonstrated -> judged -> survived). The packet's headline
finding kills that reading:

    the CLAIM corpus contains functional structure MORE advanced than
    the DEMONSTRATION subset inspected — Gustafsson's closed negative-
    feedback loop with a separate safety-escalation threshold (PAT-08,
    PAT-09) has no equal in the 1851 demonstration frames.

So CLAIM < DEMO < JUDGE < ROBUST is not an ordering of one variable.
These are ORTHOGONAL CREDENTIALS. Benchmark items therefore carry
sigma_signature vectors (built last turn, now load-bearing) and are
NOT routed through the linear ladder check. The ladder survives only
where a crossing is genuinely sequential within one corpus.

Evidence grades are first-class and never silently promoted:
  A  primary text exposed at page/canvas level
  B  primary source verified; passage via index/preview
  C  secondary transcription or pointer to a primary document
A grade-C item may not be cited as grade-A support.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from crystal_palace import canon_hash  # noqa: E402
from epistemic_layers import sigma_signature  # noqa: E402

EVIDENCE_GRADES = ("A", "B", "C")
CORPUS_LAYER = {"A": "P", "B": "D", "C": "J", "D": "F"}

DECLARED_PAYLOAD_HASH = (
    "ed660c3bfc44158d66fd64289afd6a1a150c42c23cd5561d19e825eca5c9cb49")


@dataclass(frozen=True)
class ChiddushItem:
    """One HER chiddush, normalized as M = (I, G, T, O, R) plus its
    epistemic furniture. forbidden_promotion is the claim this item
    must NEVER be read as supporting; falsifier is the executable
    check that would kill it."""
    item_id: str
    corpus_volume: str                 # A | B | C | D
    grade: str                         # A | B | C
    motif: tuple                       # (I, G, T, O, R)
    chiddush: str
    forbidden_promotion: str
    falsifier: str

    def __post_init__(self):
        if self.grade not in EVIDENCE_GRADES:
            raise ValueError("E_UNKNOWN_EVIDENCE_GRADE")
        if self.corpus_volume not in CORPUS_LAYER:
            raise ValueError("E_UNKNOWN_CORPUS_VOLUME")
        if len(self.motif) != 5:
            raise ValueError("E_MOTIF_NOT_IGTOR")
        if not self.forbidden_promotion or not self.falsifier:
            raise ValueError("E_UNGUARDED_CHIDDUSH")

    def signature(self) -> dict:
        """Orthogonal credentials, not a ladder rung."""
        return sigma_signature(
            ({"layer": CORPUS_LAYER[self.corpus_volume],
              "ref": self.item_id},))["signature"]


def _i(iid, vol, grade, motif, ch, forbid, fals):
    return ChiddushItem(iid, vol, grade, motif, ch, forbid, fals)


# ── Corpus A · PAT-01..10 · patent claims <=1850 ───────────────────────

VOLUME_A = (
    _i("PAT-01", "A", "A",
       ("armed clock", "t mod dt = 0", "trigger", "periodic alarm",
        "rearm"),
       "time can be an action guard independent of the operator",
       "software scheduler",
       "change dt; cadence must follow the new setting mechanically"),
    _i("PAT-02", "A", "A",
       ("timer+effector", "time", "couple", "interchangeable effect",
        "reconfigure"),
       "temporal controller and effector are structurally separable",
       "modern plug-in architecture",
       "swap effector without touching timer; cadence must hold"),
    _i("PAT-03", "A", "A",
       ("wheel", "motion", "count/transmit", "recorded distance",
        "continue"),
       "measurement -> persistent state -> several projections",
       "digital telemetry",
       "calibrated distance; both views must derive from one counter"),
    _i("PAT-04", "A", "A",
       ("moving subsystems", "compliance", "transmit", "stable register",
        "continuous"),
       "an interface can absorb local variability to preserve a "
       "global invariant",
       "software abstraction",
       "add body/axle displacement; measurement error must stay bounded"),
    _i("PAT-05", "A", "A",
       ("rising cage", "end of travel", "cutoff + latch", "stop/hold",
        "equalize"),
       "a safe terminal may require BOTH power cutoff and structural "
       "latching",
       "certified interlock",
       "remove the catches: terminal state must fail the retention "
       "invariant"),
    _i("PAT-06", "A", "A",
       ("level", "float threshold", "valve", "flow", "automatic return"),
       "a local physical state can become a process guard directly",
       "general control",
       "sweep level across threshold; valve must switch and return"),
    _i("PAT-07", "A", "A",
       ("exposed conductor", "environment", "encapsulate",
        "protected channel", "maintenance"),
       "reliability can be externalized into channel structure",
       "reliable network protocol",
       "ablate layers one by one; measure leakage/degradation"),
    _i("PAT-08", "A", "A",
       ("pressure", "p > p*", "damper/draught", "corrected pressure",
        "reopen"),
       "physically closed negative-feedback loop",
       "cybernetics invented in 1846",
       "perturb p; PASS if draught response opposes then restores"),
    _i("PAT-09", "A", "A",
       ("regulated boiler", "p > p_danger", "whistle", "alarm",
        "drop/intervention"),
       "normal regulation and safety escalation can have distinct "
       "thresholds",
       "certified safety system",
       "sweep p; observe corrective threshold then a separate alarm "
       "threshold"),
    _i("PAT-10", "A", "A",
       ("proposition", "legal gate", "claim", "legal scope",
        "amendment"),
       "legal novelty is a typed credential distinct from technical "
       "capability",
       "PATENT implies WORKING",
       "represent legal_claim/demonstrated/robust separately; fail if "
       "fused into invented=true"),
)

# ── Corpus B · CP-01..10 · 1851 demonstrations ─────────────────────────

VOLUME_B = (
    _i("CP-01", "B", "A",
       ("lap", "target length", "signal", "bell", "branch"),
       "a production threshold is an explicit guard",
       "digital sensor",
       "change target; signal must follow the condition"),
    _i("CP-02", "B", "A",
       ("ALERT", "human non-response", "auto-doff", "termination",
        "cycle"),
       "human non-intervention can be a bounded-fallback guard",
       "general autonomy",
       "block the human; only the planned fallback may occur"),
    _i("CP-03", "B", "A",
       ("batches", "threshold+fallback", "terminate", "uniformity",
        "new batch"),
       "output uniformity becomes a candidate production invariant",
       "proven statistical guarantee",
       "measure variance across a real series"),
    _i("CP-04", "B", "A",
       ("human chain", "new architecture", "reconfigure",
        "operations removed", "maintenance"),
       "externalization is measured by human transitions removed, not "
       "by the words 'self-acting'",
       "unmeasured quantified productivity",
       "compare operating DAGs before/after"),
    _i("CP-05", "B", "A",
       ("T1,T2", "mode", "T1 || T2", "machining", "local end"),
       "explicit mechanical concurrency with distinct local control",
       "parallel computing",
       "test T1, T2, then T1||T2"),
    _i("CP-06", "B", "A",
       ("workpiece", "symmetry", "opposed forces", "cancellation",
        "structure"),
       "robustness can be topological rather than cognitive",
       "fault-tolerant computing",
       "measure F_net simple vs duplex"),
    _i("CP-07", "B", "A",
       ("cut", "end/load", "return/relief", "resume state",
        "next cycle"),
       "reset/recovery is a first-class motif",
       "generic error recovery",
       "inject end-of-travel/load; verify the resume state"),
    _i("CP-08", "B", "A",
       ("wheels/axle", "torsion risk", "independent drives",
        "reduced torsion", "cycle"),
       "local independence introduced to preserve global integrity",
       "independent implies safe",
       "compare torsion under common vs independent drives"),
    _i("CP-09", "B", "A",
       ("origin/destination", "model", "recommend", "route",
        "human contextualizes"),
       "MODEL-OPTIMAL is not WORLD-ADMISSIBLE",
       "autonomous planner",
       "construct an impracticable geometric optimum"),
    _i("CP-10", "B", "A",
       ("physical state", "current + code", "transmit/interpret",
        "symbol", "next signal"),
       "causal transmission and semantic interpretation are two "
       "transformations",
       "Shannon in 1851",
       "same physical signal, two codebooks: symbol must differ"),
)

# ── Corpus C · JUR-01..10 · 1852 judgments ─────────────────────────────

VOLUME_C = (
    _i("JUR-01", "C", "B",
       ("exhibit", "criteria", "evaluate", "vector", "publication"),
       "evaluation is not a scalar score",
       "medal equals universal quality",
       "two objects, equal aggregate, different profiles: profiles "
       "must survive"),
    _i("JUR-02", "C", "B",
       ("object", "workmanship vs novelty", "classify", "credential",
        "n/a"),
       "novelty and execution quality are orthogonal",
       "bigger medal means better at everything",
       "represent N-up/W-down and N-down/W-up"),
    _i("JUR-03", "C", "B",
       ("process/application", "novelty", "judge", "novelty-type",
        "n/a"),
       "novelty does not require a new primitive",
       "jury novelty equals patent novelty",
       "case with N_P = 0 and N_C > 0"),
    _i("JUR-04", "C", "B",
       ("object", "multi-criteria", "evaluate", "practical fitness",
        "n/a"),
       "performance is a techno-economic vector, not accuracy alone",
       "2026 KPI equivalent",
       "two technically equal objects at different cost"),
    _i("JUR-05", "C", "B",
       ("object+class", "scope", "judge", "local verdict", "synthesis"),
       "a judgment is scope-bound",
       "class verdict equals universal truth",
       "reuse a verdict outside its class; kernel must refuse"),
    _i("JUR-06", "C", "B",
       ("panel", "composition", "aggregate", "collective judgment",
        "archive"),
       "evaluator multiplicity is not evidence multiplicity",
       "ten jurors equal ten technical witnesses",
       "same dossier to N jurors: rank(root) must stay 1"),
    _i("JUR-07", "C", "B",
       ("expertise need", "associate role", "advise", "opinion", "n/a"),
       "expertise is not authority",
       "advice equals decision",
       "an associate without delegation cannot sign a verdict"),
    _i("JUR-08", "C", "B",
       ("judgment", "projection rule", "award", "label", "n/a"),
       "an award is not new evidence",
       "medal plus report equal two witnesses",
       "three formats of one verdict must keep identical roots"),
    _i("JUR-09", "C", "C",
       ("machine+data", "task", "compute", "accuracy+time", "repeat"),
       "CORRECT is not USEFUL or PERFORMANT",
       "general-purpose computer",
       "two exact machines at 1x/100x latency: metrics stay distinct"),
    _i("JUR-10", "C", "C",
       ("human+machine", "procedure", "compute", "operator effort",
        "next input"),
       "identical result does not mean identical externalization",
       "mechanical sequence equals autonomy",
       "count human interventions per result"),
)

# ── Corpus D · RAIL-01..10 · 1840-1852 failures ────────────────────────

VOLUME_D = (
    _i("RAIL-01", "D", "A",
       ("stationary boiler", "internal energy", "rupture", "explosion",
        "inspection"),
       "NOT MOVING is not SAFE",
       "undocumented metallurgical cause",
       "velocity=0 with stored_energy>limit must remain DANGEROUS"),
    _i("RAIL-02", "D", "A",
       ("shared actor", "concurrent demands", "act", "delay",
        "reorganization"),
       "actor contention is a safety state",
       "human error as sufficient cause",
       "two tasks with incompatible deadlines must reject before "
       "execution"),
    _i("RAIL-03", "D", "A",
       ("timetable", "real state diverges", "continue",
        "reduced separation", "revalidation"),
       "VALID AT PLAN is not VALID AT EXECUTION",
       "modern block signalling",
       "add delay/drift; authorization must be recomputed at t1"),
    _i("RAIL-04", "D", "A",
       ("signal+actor", "deadline", "actuate", "late effect", "reset"),
       "MESSAGE RECEIVED is not ACTION COMPLETED",
       "signal equals effect",
       "require two separate timestamps/receipts"),
    _i("RAIL-05", "D", "A",
       ("preceding train", "rear signal", "make visible", "alert",
        "maintenance"),
       "distributed safety requires visibility of upstream state",
       "a lamp is a complete protocol",
       "measure reaction window with and without the rear signal"),
    _i("RAIL-06", "D", "A",
       ("driver", "visibility", "adapt", "stopping margin", "resume"),
       "a procedural guard is fragile when observability is missing",
       "automation always superior",
       "reduce visibility: the same policy must be recognized "
       "non-robust"),
    _i("RAIL-07", "D", "A",
       ("track", "environment changes", "enter", "derailment",
        "repair"),
       "RESOURCE SAFE AT t0 is not SAFE AT t1",
       "unattested historical sensor",
       "lease a valid route, change environment_state; Revalidate "
       "must block"),
    _i("RAIL-08", "D", "B",
       ("two movements", "resource conflict", "compose", "collision",
        "coordination"),
       "LOCAL_VALID(T1) and LOCAL_VALID(T2) do not entail "
       "GLOBAL_VALID(T1||T2)",
       "exact priority without the full text",
       "authorize separately, compose on the same space-time: global "
       "reject"),
    _i("RAIL-09", "D", "B",
       ("structure", "integrity", "fail", "collapse", "rebuild"),
       "some rules must be state invariants, not mere gates",
       "unverified detailed cause",
       "inject capacity < load; the state must be unreachable"),
    _i("RAIL-10", "D", "B",
       ("incident", "mandate", "investigate", "finding/recommendation",
        "separate policy path"),
       "INCIDENT is not UNIVERSAL POLICY",
       "one accident equals a general law",
       "a global rule from one incident must pass "
       "PROPOSE_POLICY_CHANGE, never auto-ADMIT"),
)

BENCHMARK_40 = VOLUME_A + VOLUME_B + VOLUME_C + VOLUME_D


# ── the freeze ──────────────────────────────────────────────────────────

def freeze_benchmark(items: tuple = BENCHMARK_40) -> dict:
    """Shape-check then hash. The declared other-lane hash rides the
    receipt as an UNVERIFIED claim — never as this seat's commitment."""
    counts: dict = {}
    for it in items:
        counts[it.corpus_volume] = counts.get(it.corpus_volume, 0) + 1
    if sorted(counts) != ["A", "B", "C", "D"] or \
            any(v != 10 for v in counts.values()):
        return {"verdict": "REFUSED", "reason": "E_PACKET_SHAPE",
                "got": counts}
    ids = [it.item_id for it in items]
    if len(set(ids)) != 40:
        return {"verdict": "REFUSED", "reason": "E_DUPLICATE_ITEM_ID"}
    return {"verdict": "FROZEN",
            "freeze_hash_here": canon_hash(
                [(it.item_id, it.corpus_volume, it.grade,
                  it.forbidden_promotion) for it in items]),
            "count": len(items),
            "by_volume": dict(sorted(counts.items())),
            "declared_by_other_lane": DECLARED_PAYLOAD_HASH,
            "declared_hash_verified_here": False,
            "declared_hash_status": "REPORTED — this seat holds the "
                                    "packet as delivered text, not the "
                                    "other lane's JSON bytes; "
                                    "sandbox: paths are not fetchable",
            "holdout": "international_exhibition_1862",
            "post_1851_patent_data": "BLOCKED"}


def grade_census(items: tuple = BENCHMARK_40) -> dict:
    out: dict = {}
    for it in items:
        out[it.grade] = out.get(it.grade, 0) + 1
    return {"by_grade": dict(sorted(out.items())),
            "law": "a grade-C item may never be cited as grade-A support"}


def cite_as(item: ChiddushItem, required_grade: str) -> dict:
    """Grade discipline at the point of use."""
    if required_grade not in EVIDENCE_GRADES:
        raise ValueError("E_UNKNOWN_EVIDENCE_GRADE")
    if EVIDENCE_GRADES.index(item.grade) > \
            EVIDENCE_GRADES.index(required_grade):
        return {"verdict": "REFUSED", "reason": "E_GRADE_OVERCLAIM",
                "item": item.item_id, "has": item.grade,
                "required": required_grade}
    return {"verdict": "CITABLE", "item": item.item_id,
            "grade": item.grade}


# ── the headline finding: the ladder reading is falsified ──────────────

LADDER_FALSIFICATION = {
    "finding": "the CLAIM corpus contains functional structure more "
               "advanced than the inspected DEMONSTRATION subset",
    "witnesses": ("PAT-08", "PAT-09"),
    "detail": "a physically closed negative-feedback loop with a "
              "SEPARATE safety-escalation threshold, in the <=1850 "
              "claim corpus; no 1851 demonstration frame inspected "
              "carries an equal structure",
    "kills": "CLAIM < DEMO < JUDGE < ROBUST as an ordering of one "
             "variable",
    "replaces_with": "orthogonal typed credentials; sigma is a vector",
    "consequence_for_this_repo": "benchmark items are NOT routed "
                                 "through epistemic_layers."
                                 "compute_sigma; the linear ladder "
                                 "survives only where a crossing is "
                                 "genuinely sequential within one "
                                 "corpus",
}


def coherent_signatures() -> tuple:
    """Two signatures the packet declares coherent, which a scalar
    ladder cannot represent at all."""
    return (
        {"claim": "yes", "demo": "unknown", "judge": "unknown",
         "robust": "unknown"},
        {"claim": "unknown", "demo": "yes", "judge": "high",
         "robust": "failure"},
    )
