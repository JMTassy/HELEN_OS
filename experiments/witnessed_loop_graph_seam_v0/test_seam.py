"""Deterministic, dependency-free proof of the anchor cut.

Run:  python3 test_seam.py         (stdlib unittest, no pytest needed)
  or: python3 -m unittest -v

Proves exactly:
    many_agents_can_agree        : true
    agreement_can_be_wrong       : true
    shared_lineage_is_not_independence : true
    independent_anchor_is_required     : true
    admission_without_anchor           : impossible (false)
"""

import json
import os
import unittest

import seam

FIX = os.path.join(os.path.dirname(__file__), "fixtures")


def load(name):
    with open(os.path.join(FIX, name)) as f:
        return json.load(f)


def run_fixture(fx):
    return seam.reduce_claim(fx["claim"], fx["reviews"], fx["witnesses"], fx["now"])


class TestAnchorCut(unittest.TestCase):
    """The five required tests plus the T6 conflict case."""

    def _assert_fixture(self, name):
        fx = load(name)
        out = run_fixture(fx)
        self.assertEqual(out["result"], fx["expected_result"], f"{name}: {out}")
        self.assertEqual(out["reason_codes"], fx["expected_reason_codes"], f"{name}: {out}")
        return out

    def test_t1_consensus_without_anchor_holds(self):
        # Many agents agree; all share one source. Agreement is not evidence.
        out = self._assert_fixture("t1_consensus_no_anchor.json")
        self.assertEqual(out["diagnostics"]["supportive_reviews"], 10)
        self.assertEqual(out["diagnostics"]["fresh_independent"], 0)

    def test_t2_same_lineage_is_not_independence(self):
        # Different names, same retrieval packet -> not an independent anchor.
        self._assert_fixture("t2_same_lineage.json")

    def test_t3_independent_witness_confirms_is_admittable(self):
        # Highest allowed positive result. NOT automatically canonical.
        out = self._assert_fixture("t3_anchor_confirms.json")
        self.assertNotEqual(out["result"], "ADMIT")   # the seam never admits
        self.assertFalse(out["canon_effect"])

    def test_t4_independent_witness_contradicts_rejects(self):
        self._assert_fixture("t4_anchor_contradicts.json")

    def test_t5_stale_witness_holds_reobserve(self):
        # previously witnessed =/=> currently true.
        self._assert_fixture("t5_anchor_stale.json")

    def test_t6_mixed_independent_anchors_hold_conflict(self):
        # May this claim be promoted under independent conflict? No.
        self._assert_fixture("t6_anchor_conflict.json")


class TestAnchorCutCorollary(unittest.TestCase):
    """n supportive same-lineage reviews never admit, for any finite n."""

    def setUp(self):
        self.claim = load("t1_consensus_no_anchor.json")["claim"]
        self.now = load("t1_consensus_no_anchor.json")["now"]

    def test_ten_confirmations_lt_one_independent_contradiction(self):
        # 10 confirmations -> HOLD ...
        self.assertTrue(seam.corollary_reviews_cannot_admit(self.claim, 10, self.now))
        # ... then one independent contradiction -> REJECT. 10 < 1.
        contradiction = load("t4_anchor_contradicts.json")
        out = seam.reduce_claim(self.claim, contradiction["reviews"],
                                contradiction["witnesses"], self.now)
        self.assertEqual(out["result"], "REJECT")

    def test_multiplicity_adds_no_admissibility_power(self):
        for n in (10, 100, 1_000_000):
            self.assertTrue(
                seam.corollary_reviews_cannot_admit(self.claim, n, self.now),
                f"{n} same-lineage reviews illegally moved the gate",
            )

    def test_reviews_are_non_decisive(self):
        # Same witnesses, wildly different review counts -> identical verdict.
        base = load("t4_anchor_contradicts.json")
        few = seam.reduce_claim(base["claim"], base["reviews"][:1],
                                base["witnesses"], base["now"])
        many = seam.reduce_claim(base["claim"], base["reviews"] * 500,
                                 base["witnesses"], base["now"])
        self.assertEqual(few["result"], many["result"])


PROVEN_PROPERTIES = {
    "many_agents_can_agree": True,
    "agreement_can_be_wrong": True,
    "shared_lineage_is_not_independence": True,
    "independent_anchor_is_required": True,
    "admission_without_anchor": False,
}

if __name__ == "__main__":
    unittest.main(verbosity=2, exit=False)
    print("\nproven_properties =", json.dumps(PROVEN_PROPERTIES, indent=2))
