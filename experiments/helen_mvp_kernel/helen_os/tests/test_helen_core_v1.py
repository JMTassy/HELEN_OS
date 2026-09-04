"""HELEN_CORE_V1 fixtures — the constitution spine, made falsifiable. 🔵 OBSERVED.

Enforces the seven promotion rules the projection declares. Each is a way a claim could
launder its epistemic status; each test proves the gate refuses it.
"""
from helen_os.core.core_v1 import (
    Claim, Kind, Status, can_promote, invariant_ids, is_live, is_stable, load_spine, module_names,
)

SPINE = load_spine()
NOW = "8a11fd1"


def _claim(status=Status.HYPOTHESIS, kind=Kind.NORMAL, frame=NOW,
           witness=True, contradiction=True, evidence="fx"):
    return Claim("c", "Kernel", status, kind, frame, witness, contradiction, evidence)


# ---- structure: 8 modules, 12 invariants present
def test_spine_shape():
    assert len(SPINE["modules"]) == 8
    assert len(SPINE["invariants"]) == 12
    assert invariant_ids(SPINE) == [f"I{n:02d}" for n in range(1, 13)]
    assert "Kernel" in module_names(SPINE) and "ShellDomains" in module_names(SPINE)


# ---- corpus was MEASURED, not the relayed 16k figure
def test_corpus_measured_not_inherited():
    m = SPINE["meta"]["corpus_measurement"]
    assert m["docs_md_total_lines"] == 78437       # measured @ 8a11fd1
    assert m["docs_md_total_lines"] > 16000        # relayed figure was an underestimate


# ---- FIXTURE 1: candidate cannot appear as stable
def test_candidate_not_stable():
    assert not is_stable(_claim(status=Status.HYPOTHESIS), NOW)
    assert not is_stable(_claim(status=Status.REPORTED), NOW)
    assert is_stable(_claim(status=Status.FRAME_BOUND_PASS), NOW)


# ---- FIXTURE 2: reported cannot appear as proven
def test_reported_not_proven():
    c = _claim(status=Status.REPORTED, evidence="")   # reported, no evidence
    assert can_promote(c, Status.FIXTURE_GREEN, NOW) == (False, "REPORTED_NOT_PROVEN")


# ---- FIXTURE 3: render cannot produce admission
def test_render_not_admission():
    c = _claim(status=Status.FRAME_BOUND_PASS, kind=Kind.RENDER)
    assert can_promote(c, Status.ADMITTED, NOW) == (False, "RENDER_NOT_ADMISSION")


# ---- FIXTURE 4: memory cannot replace replay
def test_memory_not_replay():
    c = _claim(status=Status.FRAME_BOUND_PASS, kind=Kind.MEMORY)
    assert can_promote(c, Status.ADMITTED, NOW) == (False, "MEMORY_NOT_REPLAY")


# ---- FIXTURE 5: missing contradiction forces HOLD
def test_missing_contradiction_holds():
    c = _claim(status=Status.REPORTED, contradiction=False)
    assert can_promote(c, Status.FIXTURE_GREEN, NOW) == (False, "MISSING_CONTRADICTION_HOLD")


# ---- FIXTURE 6: missing witness prevents promotion
def test_missing_witness_no_promotion():
    c = _claim(status=Status.FIXTURE_GREEN, witness=False)
    assert can_promote(c, Status.FRAME_BOUND_PASS, NOW) == (False, "NO_WITNESS")


# ---- FIXTURE 7: stale runtime report cannot become live state
def test_stale_runtime_not_live():
    stale = _claim(status=Status.REPORTED, kind=Kind.RUNTIME, frame="c94fe32")  # other frame
    assert not is_live(stale, NOW)
    # and it cannot be promoted to a current-frame status
    assert can_promote(_claim(status=Status.FIXTURE_GREEN, frame="c94fe32"),
                       Status.FRAME_BOUND_PASS, NOW)[1] == "STALE_FRAME"


# ---- positive control: a fully-earned NORMAL claim DOES promote (non-vacuity)
def test_earned_claim_promotes_through_ladder():
    c = _claim(status=Status.FIXTURE_GREEN, kind=Kind.NORMAL, witness=True,
               contradiction=True, evidence="fx", frame=NOW)
    assert can_promote(c, Status.FRAME_BOUND_PASS, NOW) == (True, "PROMOTED")
    admitted = _claim(status=Status.TRANSPORTED, kind=Kind.NORMAL)
    assert can_promote(admitted, Status.ADMITTED, NOW) == (True, "PROMOTED")


# ---- a no-op / downgrade is not a promotion
def test_non_promotion_denied():
    c = _claim(status=Status.FRAME_BOUND_PASS)
    assert can_promote(c, Status.FIXTURE_GREEN, NOW) == (False, "NOT_A_PROMOTION")
