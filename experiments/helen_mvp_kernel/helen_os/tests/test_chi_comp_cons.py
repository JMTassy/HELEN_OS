"""χ_comp + χ_cons — compost stays A=0; consequences never exceed justification.
🔵 OBSERVED."""
import pytest

from helen_os.kernel.admission_types import TypedAdmissionReceipt
from helen_os.kernel.capability import Capability
from helen_os.kernel.sophia import (
    Consequence, FailureReceipt, Seed, compost, consequence_of, negation_licensed,
)

FAIL_R = FailureReceipt("f1", hypothesis="h", kind="REJECT", delta=("obs1",))


# ---------------- χ_comp

def test_comp_01_seed_authority_is_structurally_zero():
    seed = compost(FAIL_R)
    assert seed.authority == 0
    with pytest.raises(AttributeError):
        seed.authority = 1  # frozen + property: no path to authority


def test_comp_02_compost_type_fence():
    seed = compost(FAIL_R)
    assert isinstance(seed, Seed)
    assert not isinstance(seed, (TypedAdmissionReceipt, Capability))
    # absent constructors: sophia exports nothing that builds receipts/capabilities
    import helen_os.kernel.sophia as sophia
    exported = {n: getattr(sophia, n) for n in dir(sophia) if not n.startswith("_")}
    assert TypedAdmissionReceipt not in exported.values()
    assert Capability not in exported.values()


def test_comp_03_reject_licenses_no_negation():
    assert not negation_licensed(FAIL_R)          # Reject(h) ⊬ ¬h
    assert consequence_of(FAIL_R) is None          # and no consequence either
    falsified = FailureReceipt("f2", "h", kind="FALSIFIED", delta=("counterexample",))
    assert negation_licensed(falsified)            # ¬h needs explicit FALSIFIED + Δ


# ---------------- χ_cons

def test_cons_01_empty_delta_no_claim():
    bare = FailureReceipt("f3", "h", kind="UNSUPPORTED", delta=())
    assert consequence_of(bare) is None  # Consequence is a partial map


def test_cons_02_justified_consequence_still_authority_zero():
    justified = FailureReceipt("f4", "h", kind="UNSUPPORTED", delta=("obs1", "obs2"))
    c = consequence_of(justified)
    assert isinstance(c, Consequence)
    assert c.supported_by == ("obs1", "obs2")  # SupportedBy(Δ, consequence)
    assert c.authority == 0                     # still needs Γ to enter G
