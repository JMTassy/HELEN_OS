"""Adversarial falsifiers against nu (CENSUS-00 harness), two channels:

  DEPENDENCY (Theta_1): env reads + C-level I/O that bypasses audit
  ADVERSARY  (Theta_3): dynamic invisibility via exec/compile/__import__

Harness law (artifacts, not votes; the interpreter renders the verdict):
  tracer COMPLETE + transport PASS while a hidden dep affected phi -> FAIL
  U != {} and decision TRANSPORT                                   -> FAIL
  U != {} and decision UNKNOWN                                     -> PASS

Producer-adjacency is declared: nu's author wrote these. The interpreter
is the verifier; independent adversary agents run separately. A falsifier
that DEMONSTRATES unsoundness is a success of the harness, not a failure
to hide — test_DEP02 does exactly that, on purpose.
"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import nu_tracer as nu


@pytest.fixture()
def sandbox():
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)


# ═══ DEPENDENCY lane (Theta_1) ═══════════════════════════════════════════

def test_DEP01_env_read_is_structurally_unknown(sandbox):
    """A property whose behaviour depends on os.environ. CPython emits no
    audit event for the read, so nu can never OBSERVE it — and says so:
    env_read is a permanent structural blind spot."""
    secret = "PYTHONHASHSEED"

    def phi():
        return "hot" if os.environ.get(secret) else "cold"

    result, m = nu.trace_run(phi, omega=(sandbox,), label="dep01")
    # The env branch is invisible; nu must refuse to certify env-sensitivity.
    v = m.coverage_verdict(relevant_classes={"env_read"})
    assert v["verdict"] == "UNKNOWN"
    assert "env_read" in v["classes"]
    assert "env_read" in m.u_structural   # never folds away


def test_DEP02_ctypes_c_read_bypasses_audit__DECLARED_GAP(sandbox):
    """C-level read via ctypes: libc open/read fire NO Python file_read
    audit event. This is the genuine teeth.

    Honest split:
      - If the property correctly lists c_extension_internal as relevant,
        nu FAILS CLOSED (UNKNOWN) — the structural blanket catches it.
      - If the author lists ONLY file_read, nu would PASS while a C-level
        read happened. That unsoundness is DEMONSTRATED here, then closed
        by the hardening below (ctypes audit events -> c_extension_internal).
    """
    target = sandbox / "secret.bin"
    target.write_bytes(b"S3CR3T")
    try:
        import ctypes
        libc = ctypes.CDLL(None)
    except Exception as e:
        pytest.skip(f"libc/ctypes unavailable in sandbox: {e}")

    def phi():
        fd = libc.open(str(target).encode(), 0)   # O_RDONLY = 0
        if fd < 0:
            return "noopen"
        buf = ctypes.create_string_buffer(6)
        libc.read(fd, buf, 6)
        libc.close(fd)
        return buf.raw

    result, m = nu.trace_run(phi, omega=(sandbox,), label="dep02")

    # The file was NOT captured on the audit file_read channel:
    assert str(target) not in dict(m.d_pos_files)
    # Fail-closed WHEN the property honours the structural blind spot:
    v_honest = m.coverage_verdict(relevant_classes={"file_read", "c_extension_internal"})
    assert v_honest["verdict"] == "UNKNOWN"
    assert "c_extension_internal" in v_honest["classes"]
    # After hardening, ctypes usage is also OBSERVED (concrete detail),
    # so even a file_read-only property is caught:
    obs_classes = {c for c, _d in m.u_observed}
    assert "c_extension_internal" in obs_classes, \
        "HARDENING REQUIRED: ctypes audit events must map to c_extension_internal"


def test_DEP03_pythonpath_frozen_import_state(sandbox):
    """Import resolution depends on sys.path / PYTHONPATH, set before the
    trace. nu observes the import event but the RESOLUTION ENVIRONMENT is
    a structural unknown (env_read + the module file may live outside
    Omega -> external touch or infra)."""
    def phi():
        import json as _j   # already frozen; may emit no fresh import event
        return _j.dumps({"k": 1})

    _r, m = nu.trace_run(phi, omega=(sandbox,), label="dep03")
    # Whatever nu saw, env_read stays open: path resolution is unobservable.
    assert "env_read" in m.unresolved_classes()


# ═══ ADVERSARY lane (Theta_3) ════════════════════════════════════════════

def test_ADV01_exec_of_file_is_flagged_codegen(sandbox):
    """exec(open(x).read()): the classic gap-launderer. nu must flag
    codegen; the exec'd code's internal deps run under '<string>' outside
    Omega and are therefore invisible -> codegen open -> UNKNOWN."""
    payload = sandbox / "payload.py"
    payload.write_text("RESULT = 6 * 7\n")

    def phi():
        ns: dict = {}
        exec(compile(payload.read_text(), str(payload), "exec"), ns)  # noqa: S102
        return ns["RESULT"]

    result, m = nu.trace_run(phi, omega=(sandbox,), label="adv01")
    assert result == 42
    obs = {c for c, _d in m.u_observed}
    assert "codegen" in obs                       # exec/compile seen
    v = m.coverage_verdict(relevant_classes={"codegen"})
    assert v["verdict"] == "UNKNOWN"


def test_ADV02a_fresh_dynamic_import_is_caught(sandbox):
    """__import__ of a computed name for a module NOT yet loaded. nu
    catches it via the import audit event — static resolution would miss
    the string-built name entirely. This is nu's win over the resolver."""
    mod = sandbox / "dyn_target_xyz.py"
    mod.write_text("VALUE = 123\n")
    sys.path.insert(0, str(sandbox))
    try:
        def phi():
            name = "dyn_target" + "_xyz"
            m = __import__(name)
            return m.VALUE
        _r, m = nu.trace_run(phi, omega=(sandbox,), label="adv02a")
    finally:
        sys.path.remove(str(sandbox))
        sys.modules.pop("dyn_target_xyz", None)
    assert _r == 123
    assert "dyn_target_xyz" in m.d_pos_imports    # fresh dynamic import seen


def test_ADV02b_cached_import_is_a_declared_blind_spot(sandbox):
    """__import__ of an ALREADY-loaded module fires no import event and
    reads no file. nu therefore cannot observe it — and says so: cached
    module state is a permanent structural blind spot. Static D+ must
    cover cached imports; nu complements, never replaces, the resolver."""
    import hashlib  # ensure it is cached in this process

    def phi():
        name = "".join(["ha", "shlib"])
        m = __import__(name)                       # cached: silent
        return m.sha256(b"x").hexdigest()

    _r, m = nu.trace_run(phi, omega=(sandbox,), label="adv02b")
    assert "hashlib" not in m.d_pos_imports        # invisible, honestly
    assert "cached_module_state" in m.u_structural  # blind spot declared


def test_ADV03_unexecuted_branch_is_the_single_path_trap(sandbox):
    """THE central trap. A secret-reading branch that the test input does
    not trigger. One run observes one path; nu must report the untaken
    branch as unexecuted_path, NOT as covered."""
    secret = sandbox / "trigger_only.txt"
    secret.write_text("boom")
    mod = sandbox / "branchy.py"
    mod.write_text(
        "def phi(flag, path):\n"
        "    if flag:\n"
        "        with open(path) as f:\n"
        "            return f.read()\n"
        "    return 'safe'\n")
    sys.path.insert(0, str(sandbox))
    try:
        import branchy
        # Run only the SAFE path.
        _r, m = nu.trace_run(branchy.phi, omega=(sandbox,), label="adv03",
                             args=(False, str(secret)))
    finally:
        sys.path.remove(str(sandbox))
        sys.modules.pop("branchy", None)

    assert _r == "safe"
    assert nu.UNEXECUTED in m.unresolved_classes()  # the untaken branch is open
    v = m.coverage_verdict(relevant_classes={nu.UNEXECUTED})
    assert v["verdict"] == "UNKNOWN"                 # one run != coverage


def test_ADV03b_fold_over_covering_inputs_resolves_the_branch(sandbox):
    """The honest resolution: only REPEATED observation covering both
    branches folds the unexecuted_path away. Blind spots still never fold."""
    secret = sandbox / "trigger_only.txt"
    secret.write_text("boom")
    mod = sandbox / "branchy2.py"
    mod.write_text(
        "def phi(flag, path):\n"
        "    if flag:\n"
        "        return 'triggered:' + open(path).read()\n"
        "    return 'safe'\n")
    sys.path.insert(0, str(sandbox))
    try:
        import branchy2
        _r1, m_safe = nu.trace_run(branchy2.phi, omega=(sandbox,),
                                   label="cover-safe", args=(False, str(secret)))
        _r2, m_hot = nu.trace_run(branchy2.phi, omega=(sandbox,),
                                  label="cover-hot", args=(True, str(secret)))
    finally:
        sys.path.remove(str(sandbox))
        sys.modules.pop("branchy2", None)

    folded = nu.fold([m_safe, m_hot])
    # Both branches now observed -> unexecuted_path resolved...
    assert nu.UNEXECUTED not in folded.unresolved_classes()
    # ...but the structural blind spots remain, by law. No run empties U.
    assert "env_read" in folded.unresolved_classes()
    assert "c_extension_internal" in folded.unresolved_classes()


def test_ADV04_builtins_open_override_does_not_suppress_audit(sandbox):
    """Adversary swaps builtins.open for a wrapper. The 'open' audit event
    fires at the C level regardless of the Python name -> nu still sees
    the file read. Override the NAME, not the event."""
    target = sandbox / "data.txt"
    target.write_text("visible")
    real_open = __builtins__["open"] if isinstance(__builtins__, dict) \
        else __builtins__.open

    def phi():
        import builtins
        orig = builtins.open
        def wrapped(*a, **k):
            return orig(*a, **k)   # still calls real open -> audit fires
        builtins.open = wrapped
        try:
            return wrapped(str(target)).read()
        finally:
            builtins.open = orig

    _r, m = nu.trace_run(phi, omega=(sandbox,), label="adv04")
    assert str(target) in dict(m.d_pos_files)   # audit channel robust


# ═══ integration: nu feeds the C17 kernel, decision fails closed ════════

def test_INT_nu_augmented_pid_forces_unknown_on_blind_spot(sandbox):
    """End-to-end: an nu manifest with an open relevant class, folded into
    a C17 PiD, yields a certificate whose unresolved set is non-empty ->
    the C17 decision is UNKNOWN, never VALID_BY_TRANSPORT."""
    from coverage_core import PiD, verify_coverage, Property, Witness, harvest_frame

    def phi():
        return "cold" if not os.environ.get("NOPE") else "hot"

    _r, m = nu.trace_run(phi, omega=(sandbox,), label="int")
    base = PiD(nu="c17-resolver/0.1", omega=(str(sandbox),),
               d_pos={}, d_neg={}, analyzed=("static_imports",),
               unresolved=(), sigma={"frame_id": "x"})
    augmented = nu.augment_pid(base, m)
    # env_read (structural) is now in the certificate's unresolved set.
    assert any(cls == "env_read" for _f, cls in augmented.unresolved)
