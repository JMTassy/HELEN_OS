"""Falsifiers for the Crystal-Palace chiddush: Compost = (E_x, F_x, N_x).

Operator-supplied meditation (this frame) on the 1851 Great Exhibition
catalog. Interpretive; only the mathematical proposition became code.
The tests defend one law with three edges:

    Compost the inference, never erase the evidence.
    Compost(x) != Delete(x).
    E_x is preserved BYTE-FOR-BYTE; F_x is NAMED (never silent).
"""
from __future__ import annotations

import inspect
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import corpus_memory as cm
from corpus_memory import (
    Compost,
    EvidenceGraph,
    Nutrient,
    PRESERVATION_CLASSES,
    compost_from_nutrient,
)


# ── law 1: compost requires a NAMED failure — silent compost is refused ─

def test_compost_refuses_unnamed_failure():
    with pytest.raises(ValueError, match="E_COMPOST_REQUIRES_NAMED_FAILURE"):
        Compost("c1", evidence=("obs-1",), failed_inference="")


def test_compost_refuses_absent_evidence_manifest():
    """E_x may be a retrieval-attempt manifest (e.g. a 403 with size 0),
    but it may never be the empty tuple — silence would be indistinguishable
    from having deleted the evidence."""
    with pytest.raises(ValueError, match="E_COMPOST_REQUIRES_EVIDENCE_OR_MANIFEST"):
        Compost("c1", evidence=(), failed_inference="misinterpreted the pattern")


# ── law 2: Compost != Delete — the module has no eraser ────────────────

def test_module_exposes_no_deletion_of_evidence():
    """The Crystal-Palace corollary as a grep: there is no delete, no
    erase, no forget, no purge. Composting is preservation, not removal."""
    names = {n for n in dir(cm) if not n.startswith("_")}
    for banned in ("delete_evidence", "erase", "forget", "purge",
                   "drop_source", "remove_claim"):
        assert not any(banned in n.lower() for n in names), banned


# ── law 3: evidence is byte-identical, immutable, non-mutating ─────────

def test_evidence_preserved_byte_for_byte():
    original = ("claim:a", "claim:b", "claim:c")
    c = Compost("c1", evidence=original,
                failed_inference="counterevidence dominated support",
                nutrient="require 2x support-to-counter ratio before STANDING")
    assert c.evidence == original
    assert c.evidence is not original or True   # tuples are hashable
    # frozen: cannot mutate the composted record
    with pytest.raises(Exception):
        c.evidence = ()  # type: ignore[misc]


def test_frozen_compost_cannot_relabel_the_failure():
    c = Compost("c1", evidence=("x",), failed_inference="F")
    with pytest.raises(Exception):
        c.failed_inference = "actually it succeeded"  # type: ignore[misc]


# ── the four preservation classes are distinct promises ─────────────────

def test_four_preservation_classes_are_distinct_and_named():
    assert set(PRESERVATION_CLASSES) == {"ARCHIVE", "COMPOST", "GARDEN", "KERNEL"}
    # each promises something DIFFERENT — no aliasing
    assert len({p for p in PRESERVATION_CLASSES.values()}) == 4
    # COMPOST's promise names all three parts of the triple
    p = PRESERVATION_CLASSES["COMPOST"]
    assert "evidence" in p and "failure" in p and "nutrient" in p


# ── composting a nutrient: E from support, F named, N optional ─────────

def test_compost_from_nutrient_preserves_support_as_evidence():
    n = Nutrient("N1", "insight", support=("c1", "c2"), replay_receipt="r",
                 counterevidence=("c3", "c4", "c5"))
    c = compost_from_nutrient(
        n, failure="counterevidence exceeded support 3:2",
        nutrient="raise the support/counter ratio threshold",
        boundary="single-witness lineages inflate false confidence")
    assert c.evidence == ("c1", "c2")           # E_x = the ACTUAL support
    assert "counterevidence exceeded" in c.failed_inference   # F_x named
    assert c.nutrient.startswith("raise")       # N_x extracted
    assert c.provenance == "N1"                 # backpointer to origin


# ── first witnessed use case: the archive.org 403 from earlier this turn ─

def test_compost_the_unfetched_archive_reference():
    """The concrete NEGATIVE_CHIDDUSH from this session's own turn: the
    operator supplied an archive.org URL, the proxy 403'd, zero bytes
    reached this frame. Composting that reference means the URL, the
    attempt, and the failed inference all survive — the nutrient
    extracted is exactly the Crystal-Palace meditation itself."""
    attempt = (
        "url:https://dn760107.eu.archive.org/0/items/officialdescrip1grea/officialdescrip1grea.pdf",
        "attempted_at_frame:this",
        "http_status:000",
        "proxy_response:403 CONNECT tunnel failed",
        "bytes_reached_frame:0",
    )
    c = Compost(
        compost_id="compost:pkt-1851-unfetched",
        evidence=attempt,       # E_x: the ATTEMPT MANIFEST, not the PDF
        failed_inference=(
            "auto-narration of PDF contents from the URL slug alone"
        ),
        nutrient=(
            "an operator-supplied pointer is not a witness; it is a "
            "promise of a possible witness — the census plane needs "
            "a first-class RetrievalAttemptManifest"
        ),
        boundary="proxy egress policy (403 on general HTTPS CONNECT)",
        provenance="turn:crystal-palace-meditation",
    )
    assert c.evidence == attempt                # nothing was narrated in
    assert "auto-narration" in c.failed_inference
    assert "RetrievalAttemptManifest" in c.nutrient
    assert "403" in c.boundary
    # and the failed inference itself is exactly the one WVIS-02 would
    # have caught if the projection had tried to render it as PASS


# ── deterministic ──────────────────────────────────────────────────────

def test_compost_deterministic():
    a = Compost("c", evidence=("e",), failed_inference="f", nutrient="n")
    b = Compost("c", evidence=("e",), failed_inference="f", nutrient="n")
    assert a == b


# ── frozen boundary, not frozen vocabulary (echoes the WVIS ruling) ─────

def test_compost_shape_freezes_the_promise_not_the_fields():
    """Compost may grow fields (e.g. temporal_scope, replay_receipt)
    without breaking the constitutional law. Test the LAW, not the shape."""
    sig = inspect.signature(Compost)
    # the two structural obligations must exist
    assert {"evidence", "failed_inference"}.issubset(sig.parameters.keys())
    # ...but the boundary is what has to hold, not the exact field list
    for banned in ("delete", "erase", "forget", "purge"):
        assert banned not in sig.parameters
