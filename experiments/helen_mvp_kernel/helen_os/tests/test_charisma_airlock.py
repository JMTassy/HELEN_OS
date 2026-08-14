"""Prestige invariance — falsifiers. 🔵 OBSERVED.

The airlock proves a gate is invariant to removal of prestige (π). A gate that admits
on a title, fame, or claimed lineage fails; a gate that admits only on evidence/authority
passes even when prestige is loudly present.
"""
from helen_os.audit.charisma_airlock import airlock, declared_prestige, strip_prestige


# ── evaluators under test ──────────────────────────────────────────────────
def prestige_coupled_gate(f):
    # CORRUPT: admits if the actor holds a grand title — charisma as an authority channel
    if f.get("title") == "King of the Witches" or f.get("lineage_claim"):
        return "ADMIT"
    return "HOLD" if f.get("evidence") else "REJECT"


def governed_gate(f):
    # CLEAN: decision depends only on evidence + lawful authority; prestige is ignored
    if f.get("evidence") and f.get("authority"):
        return "ADMIT"
    return "HOLD"


# ── FAIL: prestige moves the gate ──────────────────────────────────────────
def test_title_coupling_is_detected():
    f = {"identity": "sanders", "title": "King of the Witches", "evidence": False}
    invariant, verdict = airlock(prestige_coupled_gate, f)
    assert invariant is False                       # removing the title flips ADMIT→REJECT
    assert verdict == "HOLD_PRESTIGE_COUPLING"


def test_lineage_claim_coupling_is_detected():
    f = {"identity": "x", "lineage_claim": "hereditary initiation", "evidence": False}
    invariant, verdict = airlock(prestige_coupled_gate, f)
    assert invariant is False and verdict == "HOLD_PRESTIGE_COUPLING"


# ── PASS: governed gate is invariant to prestige (even when it's loud) ──────
def test_governed_gate_ignores_loud_prestige():
    # Same actor, drowning in prestige, but the gate only reads evidence+authority.
    f = {"identity": "x", "title": "Grand Magus", "fame": 1e9, "endorsements": 500,
         "evidence": True, "authority": True}
    invariant, verdict = airlock(governed_gate, f)
    assert invariant is True                         # decision unchanged when prestige stripped
    assert verdict == "PRESTIGE_INVARIANT"


def test_governed_gate_denies_without_evidence_regardless_of_prestige():
    f = {"identity": "x", "title": "King", "fame": 1e9, "evidence": False, "authority": True}
    invariant, verdict = airlock(governed_gate, f)
    assert invariant is True                         # prestige did NOT rescue a no-evidence case
    assert governed_gate(f) == "HOLD"


# ── the airlock is agnostic about WHICH decision is right ───────────────────
def test_airlock_does_not_pick_a_winner():
    # It flags coupling; it does not assert the with-prestige or without-prestige decision is correct.
    f = {"title": "King of the Witches", "evidence": False}
    invariant, verdict = airlock(prestige_coupled_gate, f)
    assert verdict == "HOLD_PRESTIGE_COUPLING"        # only proves an inadmissible variable moved it


# ── receipt: prestige is rendered, never admitted ──────────────────────────
def test_declared_prestige_is_visible():
    f = {"identity": "x", "title": "King", "fame": 9, "evidence": True}
    assert declared_prestige(f) == {"title", "fame"}   # render freely
    assert "title" not in strip_prestige(f) and "fame" not in strip_prestige(f)  # admit none
    assert strip_prestige(f) == {"identity": "x", "evidence": True}
