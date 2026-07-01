"""tests/test_transport_drift.py — AR-DRIFT-001 witnesses.

NON_SOVEREIGN · authority=false · no ledger writes.

Witnesses for the drift algebra laws D1–D4 (transport/drift.py), plus the
three governance instances this session produced empirically, re-expressed
as Δ-statements:

  I1  palette coverage law            Δ = 0   (held by CI since 7b6ee6a)
  I2  cross-namespace divergence      Δ > 0 and exactly the registered set
  I3  K-tau doc↔guard contradiction   Δ > 0   (proven on metal; encoded here
      as a permanent fixture so the violation class has a named witness even
      before the gate itself is fixed)
"""
import itertools
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from transport.drift import Drift, drift, guard_projection
from tools.wulmoji_palette import (
    CONQUEST_BULLETIN_STATES,
    CROSS_NAMESPACE_REUSE,
    GOVERNANCE_STATUS,
)
from tools.wulmoji_ledger_validator import VALID_STATES


# ---------------------------------------------------------------------------
# D1–D4 — the algebra laws
# ---------------------------------------------------------------------------

# Small value universe for exhaustive law checks: mappings over 2 keys with
# values drawn from {0, 1, absent} — 9 mappings, 729 triples.
_KEYS = ("k1", "k2")
_VALUES = (0, 1, None)  # None = key absent


def _mappings():
    for combo in itertools.product(_VALUES, repeat=len(_KEYS)):
        yield {k: v for k, v in zip(_KEYS, combo) if v is not None}


class TestAlgebraLaws:
    def test_d1_identity(self):
        for a in _mappings():
            assert drift(a, a).is_zero()

    def test_d2_symmetry(self):
        for a in _mappings():
            for b in _mappings():
                d_ab, d_ba = drift(a, b), drift(b, a)
                assert d_ab.size() == d_ba.size()
                assert d_ab.transpose() == d_ba

    def test_d3_triangle_exhaustive(self):
        ms = list(_mappings())
        for a in ms:
            for b in ms:
                for c in ms:
                    assert drift(a, c).size() <= drift(a, b).size() + drift(b, c).size()

    def test_d4_soundness(self):
        for a in _mappings():
            for b in _mappings():
                assert drift(a, b).is_zero() == (a == b)


# ---------------------------------------------------------------------------
# I1 — palette coverage law as Δ = 0
# ---------------------------------------------------------------------------

class TestPaletteInstance:
    def test_validator_states_drift_is_zero(self):
        canonical = {g: True for g in CONQUEST_BULLETIN_STATES}
        grammar = {g: True for g in VALID_STATES}
        assert drift(canonical, grammar).is_zero(), (
            "CONQUEST grammar drifted from canonical table — same law as "
            "test_wulmoji_palette_disjointness, expressed as Δ = 0"
        )


# ---------------------------------------------------------------------------
# I2 — cross-namespace divergence: Δ > 0, and exactly the registered set
# ---------------------------------------------------------------------------

class TestCrossNamespaceInstance:
    def test_namespace_drift_matches_registry(self):
        shared = {g: GOVERNANCE_STATUS[g] for g in CONQUEST_BULLETIN_STATES}
        d = drift(shared, CONQUEST_BULLETIN_STATES)
        # Divergence is real (Δ > 0) ...
        assert not d.is_zero()
        # ... structural: no missing keys, only meaning disagreements ...
        assert d.only_left == d.only_right == frozenset()
        # ... and exactly the registered reuse set — no silent divergence.
        assert d.disagreements == frozenset(CROSS_NAMESPACE_REUSE)


# ---------------------------------------------------------------------------
# I3 — K-tau doc↔guard contradiction as a Δ > 0 fixture
# ---------------------------------------------------------------------------

# The doctrine's own case table (CLAUDE.md K-tau rule): the naive call is
# forbidden, the timezone-aware form is the mandated remediation.
_KTAU_DOC_LAW = {
    "datetime.now()": "forbidden",
    "datetime.now(timezone.utc)": "mandated",
}


def _ktau_needle_guard(case: str) -> str:
    """The guard as currently implemented: bare substring needle
    (scripts/helen_k_tau_lint.py DEFAULT_FORBID_TIME_CALLS)."""
    return "forbidden" if "datetime.now(" in case else "mandated"


def _argument_aware_guard(case: str) -> str:
    """The guard the doctrine actually requires: only the bare call is
    forbidden."""
    return "forbidden" if case.replace(" ", "") == "datetime.now()" else "mandated"


class TestKtauGuardInstance:
    def test_current_needle_has_positive_drift_from_doctrine(self):
        g = guard_projection(_KTAU_DOC_LAW, _ktau_needle_guard)
        d = drift(_KTAU_DOC_LAW, g)
        assert not d.is_zero(), "needle guard unexpectedly agrees with doctrine"
        assert d.disagreements == frozenset({"datetime.now(timezone.utc)"}), (
            "the drift is exactly the doc-mandated form — the guard enforces "
            "a coarser law than the doctrine states (proven on metal 2026-07-01)"
        )

    def test_argument_aware_guard_has_zero_drift(self):
        g = guard_projection(_KTAU_DOC_LAW, _argument_aware_guard)
        assert drift(_KTAU_DOC_LAW, g).is_zero(), (
            "the corrected guard shape closes the triangle: Δ(doc, guard) = 0"
        )
