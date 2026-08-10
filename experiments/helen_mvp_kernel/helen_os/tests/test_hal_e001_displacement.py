"""E001 regression — identity displacement must not PASS. 🔵 OBSERVED.

Autoresearch discovery: a witness borrowing one item's evidence to satisfy another
item passed coverage + global consistency. Per-item attribution closes it.
Goblin: gemma4-12b (local). Confirmed against e476e51 before the fix.
"""
from helen_os.kernel.hal import PASS, UNKNOWN, CoverageReceipt, check, h_v

X = {"items": [{"id": "S1", "secret": "a"}, {"id": "S2", "secret": "b"}]}
surface = lambda x: [i["id"] for i in x["items"]]
derivable = lambda x: [f'{i["id"]}:{i["secret"]}' for i in x["items"]]
item_derivable = lambda x, iid: [
    f'{i["id"]}:{i["secret"]}' for i in x["items"] if i["id"] == iid
]


def _displaced_witness(pkg):
    # S1's evidence is actually S2's ('S2:b'); S2's is legitimately 'S2:b'
    return True, CoverageReceipt(
        input_hash=h_v(pkg), predicate_id="p", predicate_version="1",
        required_item_ids=("S1", "S2"), checked_item_ids=("S1", "S2"),
        evidence_refs=("S2:b", "S2:b"),
        attribution=(("S1", "S2:b"), ("S2", "S2:b")),  # S1 mis-attributed
    )


def _honest_witness(pkg):
    return True, CoverageReceipt(
        input_hash=h_v(pkg), predicate_id="p", predicate_version="1",
        required_item_ids=("S1", "S2"), checked_item_ids=("S1", "S2"),
        evidence_refs=("S1:a", "S2:b"),
        attribution=(("S1", "S1:a"), ("S2", "S2:b")),  # each from itself
    )


def test_e001_displacement_no_longer_passes():
    r = check("disp", X, _displaced_witness, surface, derivable,
              witness_id="w", item_derivable=item_derivable)
    assert r.verdict == UNKNOWN and r.reason_code == "DISPLACED_EVIDENCE"


def test_e001_honest_attribution_still_passes():
    r = check("disp", X, _honest_witness, surface, derivable,
              witness_id="w", item_derivable=item_derivable)
    assert r.verdict == PASS  # positive control: correct per-item binding admitted


def test_e001_legacy_witnesses_unaffected():
    # no item_derivable supplied → old set-subset path, still works for honest data
    r = check("disp", X, _honest_witness, surface, derivable, witness_id="w")
    assert r.verdict == PASS
