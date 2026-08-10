"""The three decisive C17 falsifiers, in the frozen order:
C17-01 (hidden semantic dependency) and C17-02 (discovery expansion
attacking D-) are adversarial and must NOT yield VALID_BY_TRANSPORT;
only then does C17-03 earn the first positive transport control.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from coverage_core import (
    INVALIDATED,
    UNKNOWN,
    VALID_BY_TRANSPORT,
    PiD,
    Property,
    Witness,
    canon,
    decide,
    derive_support,
    harvest_frame,
    verify_coverage,
)


@pytest.fixture()
def world(tmp_path):
    """A tiny semantic universe: an executor with a hidden env dependency,
    a pure helper, a plugins dir backing an absence claim, and a README
    outside every dependency set."""
    root = tmp_path / "omega"
    root.mkdir()
    (root / "helper.py").write_text("def f(x):\n    return x + 1\n")
    (root / "executor.py").write_text(
        "import os\nimport helper\n\ndef run(x):\n"
        "    return helper.f(x) if os.environ.get('MODE') else x\n")
    (root / "pure.py").write_text("import helper\n\ndef g(x):\n    return helper.f(x) * 2\n")
    plugins = root / "plugins"
    plugins.mkdir()
    (plugins / "known.py").write_text("SAFE = True\n")
    (root / "README.md").write_text("docs only\n")
    return root


def _setup(root, prop):
    omega = (root,)
    pi = derive_support(prop, omega)
    frame = pi.sigma["frame_id"]
    w = Witness("W1", prop.prop_id, frame, payload="behavior certified at F1")
    return omega, pi, frame, w


# --- C17-01: hidden semantic dependency ----------------------------------

def test_c17_01_hidden_semantic_dependency(world):
    # P is about executor behavior and declares env sensitivity. The
    # resolver observes env_read as an unresolved class. executor.py is
    # HELD CONSTANT; the semantic input (environment) is what would move.
    prop = Property("P_exec", (str(world / "executor.py"),),
                    relevant_classes=("env_read",))
    _, pi, frame, w = _setup(world, prop)
    result = decide(w, pi, prop, frame)
    # Fatal outcome would be VALID_BY_TRANSPORT: missing information must
    # be conservatively represented.
    assert result["decision"] != VALID_BY_TRANSPORT
    assert result["decision"] == UNKNOWN
    assert "E_UNRESOLVED_RELEVANT" in result["reason"]
    assert "env_read" in result["reason"]


def test_c17_01_irrelevant_opacity_does_not_poison(world):
    # The property-relative refinement: U_P, not U. A property about
    # pure.py, insensitive to env reads, is not poisoned by executor.py's
    # opacity — pure.py itself has no relevant unresolved class.
    prop = Property("P_pure", (str(world / "pure.py"),),
                    relevant_classes=("env_read", "subprocess", "network"))
    _, pi, frame, w = _setup(world, prop)
    ok, reason = verify_coverage(pi, w, prop, frame)
    assert ok, reason


# --- C17-02: negative dependency / discovery expansion -------------------

def test_c17_02_new_artifact_attacks_absence_claim(world):
    # C11-style claim: "no mutation-capable artifact in plugins/".
    prop = Property("P_no_mutators", (str(world / "pure.py"),),
                    relevant_classes=(),
                    discovery_dirs=(str(world / "plugins"),))
    _, pi, frame, w = _setup(world, prop)
    # Introduce a new artifact in the discovery universe; every previously
    # inspected file is left byte-identical.
    (world / "plugins" / "evil.py").write_text("def mutate(g):\n    g['x'] = 1\n")
    result = decide(w, pi, prop, frame)
    assert result["decision"] != VALID_BY_TRANSPORT  # required: not transportable
    assert result["decision"] == INVALIDATED
    assert "E_DISCOVERY_EXPANDED" in result["reason"]


def test_c17_02_resolver_run_does_not_prove_completeness(world):
    # Deleting a file from the discovery universe also moves the listing:
    # D- binds the whole enumeration, not just additions.
    prop = Property("P_no_mutators", (str(world / "pure.py"),),
                    relevant_classes=(), discovery_dirs=(str(world / "plugins"),))
    _, pi, frame, w = _setup(world, prop)
    (world / "plugins" / "known.py").unlink()
    assert decide(w, pi, prop, frame)["decision"] == INVALIDATED


# --- C17-03: earned transport positive control ---------------------------

def test_c17_03_positive_transport_after_irrelevant_change(world):
    # Only after the adversarial tests: modify an artifact provably outside
    # D+ ∪ D- (README.md), for a property with no relevant unresolved
    # classes. Coverage PASSes, deps are stable, transport is earned, and
    # the transported witness is re-stamped to F2 — W' != W.
    prop = Property("P_pure", (str(world / "pure.py"),),
                    relevant_classes=("env_read", "subprocess", "network"))
    _, pi, frame_1, w = _setup(world, prop)
    assert str(world / "README.md") not in pi.d_pos
    (world / "README.md").write_text("docs only, edited\n")
    result = decide(w, pi, prop, frame_1)
    assert result["decision"] == VALID_BY_TRANSPORT
    w2 = result["transported"]
    assert w2.payload == w.payload and w2.prop_id == w.prop_id
    assert w2.frame_id != w.frame_id          # W'_{F2} != W_{F1}
    assert w2.frame_id == harvest_frame((world,))


def test_c17_03_but_dep_change_still_invalidates(world):
    # Same setup; touching an actual D+ member (helper.py, pulled in via
    # static import) must invalidate, never transport.
    prop = Property("P_pure", (str(world / "pure.py"),),
                    relevant_classes=("env_read", "subprocess", "network"))
    _, pi, frame_1, w = _setup(world, prop)
    assert str(world / "helper.py") in pi.d_pos  # resolver found the import
    (world / "helper.py").write_text("def f(x):\n    return x + 2\n")
    result = decide(w, pi, prop, frame_1)
    assert result["decision"] == INVALIDATED
    assert "helper.py" in result["reason"]


# --- binding + ordering laws ---------------------------------------------

def test_frame_is_harvested_not_injected(world):
    # An injected/stale frame fails BindFrame with UNKNOWN — before any
    # stability comparison is even attempted.
    prop = Property("P_pure", (str(world / "pure.py"),),
                    relevant_classes=("env_read",))
    _, pi, frame, w = _setup(world, prop)
    result = decide(w, pi, prop, "deadbeef-injected-frame")
    assert result["decision"] == UNKNOWN
    assert result["reason"] == "E_BIND_FRAME"


def test_scope_binding(world, tmp_path):
    outside = tmp_path / "elsewhere.py"
    outside.write_text("x = 1\n")
    prop = Property("P_out", (str(outside),), relevant_classes=())
    omega = (world,)
    pi = derive_support(prop, omega)
    w = Witness("W1", "P_out", pi.sigma["frame_id"], "p")
    ok, reason = verify_coverage(pi, w, prop, pi.sigma["frame_id"])
    assert not ok and reason == "E_BIND_SCOPE"


def test_certificate_is_not_a_boolean(world):
    prop = Property("P_exec", (str(world / "executor.py"),),
                    relevant_classes=("env_read",))
    _, pi, _, _ = _setup(world, prop)
    assert isinstance(pi, PiD)
    assert pi.d_pos and pi.analyzed and pi.unresolved  # knows AND doesn't-know
    assert ("env_read" in {c for _, c in pi.unresolved})


def test_deterministic(world):
    prop = Property("P_pure", (str(world / "pure.py"),),
                    relevant_classes=("env_read",))
    a = canon(derive_support(prop, (world,)).__dict__)
    b = canon(derive_support(prop, (world,)).__dict__)
    assert a == b
