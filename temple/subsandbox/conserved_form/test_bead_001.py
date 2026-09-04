"""BEAD-TEMPLE-CONSERVED-FORM-001 — minimal conservation tests.

The four laws under test (TEMPLE_CONSERVED_FORM_V0 §4):
  1. same input + same mapping -> same coordinate sequence
  2. same coordinate sequence  -> same graph
  3. same graph                -> equivalent visual / rhythm / voxel projections
  4. one altered symbol        -> localized downstream difference
Plus mandatory output #7: independent reproduction.
"""

import bead_compiler as bc

SOURCE = "SHAPE IS SOUND"
ALTERED = "SHAPE IS ROUND"  # one symbol changed: S -> R at normalized index 7


def test_same_input_same_mapping_same_coordinates():
    a = bc.compile_bead(SOURCE)
    b = bc.compile_bead(SOURCE)
    assert a["projections"]["coordinates"] == b["projections"]["coordinates"]
    assert a["packet_hash"] == b["packet_hash"]  # byte-identical, K-tau clean


def test_same_coordinate_sequence_same_graph():
    packet = bc.compile_bead(SOURCE)
    symbols = packet["projections"]["normalized"]
    coords = packet["projections"]["coordinates"]
    rebuilt = bc.build_graph(symbols, coords)
    assert rebuilt == packet["projections"]["graph"]
    assert bc.sha256(rebuilt) == packet["fingerprints"]["graph"]


def test_same_graph_equivalent_projections():
    packet = bc.compile_bead(SOURCE)
    coords = packet["projections"]["coordinates"]
    # Re-render every projection from the intermediate structure alone;
    # equivalence = fingerprint match, not visual resemblance.
    assert bc.sha256(bc.trace2d(coords)) == packet["fingerprints"]["trace2d"]
    assert bc.sha256(bc.voxels(coords)) == packet["fingerprints"]["voxel"]
    assert bc.sha256(bc.rhythm(coords)) == packet["fingerprints"]["rhythm"]


def test_one_altered_symbol_localized_downstream_difference():
    a = bc.compile_bead(SOURCE)
    b = bc.compile_bead(ALTERED)
    na, nb = a["projections"]["normalized"], b["projections"]["normalized"]
    assert len(na) == len(nb) == 12
    div = bc.first_divergence(na, nb)
    assert div == 7  # SHAPEIS|S|OUND vs SHAPEIS|R|OUND

    ca, cb = a["projections"]["coordinates"], b["projections"]["coordinates"]
    assert bc.first_divergence(ca, cb) == 7
    assert ca[:7] == cb[:7]  # upstream strictly conserved

    # Cross-links: every divergent record sits at the altered index or
    # downstream of it — the divergence localizes, it does not smear.
    la, lb = a["projections"]["cross_links"], b["projections"]["cross_links"]
    divergent = [i for i, (x, y) in enumerate(zip(la, lb)) if x != y]
    assert divergent, "an alteration must be visible"
    assert min(divergent) == 7


def test_independent_reproduction():
    """Mandatory output #7: a second, structurally different implementation
    of normalize+coordinates must reach the same coordinate sequence."""
    rows = ["ABCDE", "FGHIK", "LMNOP", "QRSTU", "VWXYZ"]
    table = {ch: [r, c] for r, row in enumerate(rows) for c, ch in enumerate(row)}
    table["J"] = table["I"]
    independent = [table[ch] for ch in SOURCE.upper() if ch in table]

    packet = bc.compile_bead(SOURCE)
    assert independent == packet["projections"]["coordinates"]


def test_ambiguity_log_never_silent():
    packet = bc.compile_bead(SOURCE)
    dropped = [a for a in packet["ambiguities"] if a["rule"] == "DROPPED_NON_ALPHABET"]
    assert len(dropped) == 2  # the two spaces, logged with their indices
    assert [a["index"] for a in dropped] == [5, 8]


def test_packet_constitutional_flags():
    packet = bc.compile_bead(SOURCE)
    assert packet["authority"] is False
    assert packet["canon"] is False
    assert packet["ledger_effect"] == "none"
    assert packet["claim_status"] == "LOCAL_OBSERVATION"
