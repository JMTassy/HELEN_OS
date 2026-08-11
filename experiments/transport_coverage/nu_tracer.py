"""nu — the Pessimistic Execution Tracer. Earning Pi_D honestly.

NON_SOVEREIGN · authority=false · ledger_effect=none.

C17's static resolver GUESSES dependencies from source shape. It is
optimistic in one direction (it cannot see dynamic imports, computed
paths, reflective calls) and blind in another (it does not know which
branches never run). nu replaces guessing with observation — and then
refuses the trap that observation invites.

    THE TRACER'S LAW:  a trace narrows U; it never empties it.

Three honesty rules, each enforced by construction:

  1. EXECUTED != COVERED. One run observes one path. Every executable
     line not reached, and every function never entered, is recorded as
     an UNRESOLVED dependency (class 'unexecuted_path'), not an absent
     one. This is 'not discovered != proved irrelevant' at runtime.

  2. DECLARED BLIND SPOTS. CPython emits no audit event for
     os.environ reads, C-extension internals, or reflective attribute
     access. nu therefore ALWAYS reports these in u_structural. A
     property sensitive to them can never PASS from tracing alone — the
     tracer states what it cannot see instead of inferring silence.

  3. SCOPE HONESTY. A read outside the declared Omega is not ignored;
     it is reported as an external touch, because the property's scope
     failed to cover something the code actually did.

nu observes; it never blocks. It is a tracer, not an enforcer:
pessimism is in the reporting, never in the runtime behaviour.

Deterministic: sorted output, canonical JSON, no wall-time, no
randomness. The manifest binds to the bytes it observed (per-file
sha256) and to its interpreter frame.
"""
from __future__ import annotations

import ast
import hashlib
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

# --- audit events -> opaque dependency classes ---------------------------
# The runtime's own declaration of security-relevant operations.
AUDIT_CLASS = {
    "import": "dynamic_import",
    "open": "file_read",
    "exec": "codegen",
    "compile": "codegen",
    "subprocess.Popen": "subprocess",
    "os.system": "subprocess",
    "os.exec": "subprocess",
    "os.spawn": "subprocess",
    "socket.connect": "network",
    "socket.getaddrinfo": "network",
    "urllib.Request": "network",
    # Falsifier DEP02 finding: ctypes fires dlopen/dlsym audit events, so a
    # C-level read that bypasses the file_read channel is still OBSERVABLE
    # as native-code usage. This upgrades c_extension_internal from a purely
    # structural blind spot to a concretely-observed one, catching even
    # properties that declare only file_read.
    "ctypes.dlopen": "c_extension_internal",
    "ctypes.dlsym": "c_extension_internal",
    "ctypes.call_function": "c_extension_internal",
    "ctypes.cdata": "c_extension_internal",
    # Independent-adversary DEP finding: os.listdir/os.scandir ARE
    # directory-content reads and DO fire (previously-unmapped) events.
    "os.listdir": "dir_listing",
    "os.scandir": "dir_listing",
}

# What THIS tracer version structurally cannot observe. Never empty:
# an honest instrument publishes its blind spots.
STRUCTURALLY_UNOBSERVABLE = (
    "env_read",              # CPython emits no audit event for os.environ
    "c_extension_internal",  # native code paths are opaque to settrace
    "reflective_attribute",  # getattr/__getattribute__ dispatch is untyped
    "cached_module_state",   # __import__ of an already-loaded module fires
                             # no event; static D+ must cover cached imports
    "file_metadata",         # ADVERSARY finding: os.stat fires NO audit
                             # event; size/mtime deps are unobservable, so
                             # filesystem purity cannot be PASSED by trace
)
# sub_line_branch is NOT always-structural: it is flagged into u_observed
# only when a ternary / boolean short-circuit is actually detected in an
# entered function (see _build), so clean multi-line code can still PASS.

UNEXECUTED = "unexecuted_path"

# Caring about one member of a family means caring about the whole family:
# you cannot declare file_read sensitivity and pretend os.stat is irrelevant.
FAMILIES = (
    frozenset({"file_read", "dir_listing", "file_metadata"}),   # filesystem
    frozenset({UNEXECUTED, "sub_line_branch"}),                  # coverage
)


def expand_relevant(relevant) -> set:
    r = set(relevant)
    for fam in FAMILIES:
        if r & fam:
            r |= fam
    return r


# Only Python MODULE artifacts under interpreter paths are machinery noise.
# A DATA file read under site-packages (a bundled .dat threshold, say) is a
# genuine content dependency and must NOT be silently exempted (crack 3).
_MODULE_ARTIFACT_SUFFIXES = (".py", ".pyc", ".pyo", ".so", ".pyd")

_ACTIVE: list = []          # stack of live recorders
_HOOK_INSTALLED = False


def _sha(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return "UNREADABLE"


def _runtime_infra(p: str) -> bool:
    """Interpreter machinery, not a dependency of the traced property.

    Crack-3 fix: only Python MODULE artifacts (.py/.pyc/.so) under
    interpreter paths are machinery. A NON-module content read under
    those paths (a bundled data file) is a real dependency and is NOT
    exempted here — it falls through to external_touch."""
    under_infra = (p.startswith(sys.prefix) or p.startswith(sys.base_prefix)
                   or "site-packages" in p or "lib/python" in p)
    return under_infra and p.endswith(_MODULE_ARTIFACT_SUFFIXES)


class _Recorder:
    """Append-only sink. Must not perform audited operations itself."""

    def __init__(self, roots: tuple):
        self.roots = roots
        self.audit: list = []            # (class, detail)
        self.lines: set = set()          # (file, lineno) actually executed
        self.codes: dict = {}            # (file, qualname) -> frozenset(lines)

    def in_omega(self, path: str) -> bool:
        return any(path.startswith(r) for r in self.roots)


def _audit_hook(event, args):
    if not _ACTIVE:
        return
    cls = AUDIT_CLASS.get(event)
    if cls is None:
        return
    rec = _ACTIVE[-1]
    try:
        detail = str(args[0]) if args else ""
    except Exception:
        detail = "<undescribable>"
    rec.audit.append((cls, detail))     # record only; never block


def _install_hook():
    """Audit hooks are permanent for the process by design; install once
    and gate on the active-recorder stack."""
    global _HOOK_INSTALLED
    if not _HOOK_INSTALLED:
        sys.addaudithook(_audit_hook)
        _HOOK_INSTALLED = True


def _make_line_tracer(rec: _Recorder):
    def tracer(frame, event, arg):
        code = frame.f_code
        fname = code.co_filename
        if not rec.in_omega(fname):
            return None                  # no line events outside Omega
        if event == "call":
            key = (fname, code.co_qualname)
            if key not in rec.codes:
                # Falsifier ADV03b finding: co_firstlineno (the 'def' /
                # signature line) does not re-execute on call, so it must
                # not be counted among body lines that coverage requires —
                # else fold could never resolve any function.
                rec.codes[key] = frozenset(
                    ln for _s, _e, ln in code.co_lines()
                    if ln is not None and ln != code.co_firstlineno)
        elif event == "line":
            rec.lines.add((fname, frame.f_lineno))
        return tracer
    return tracer


@dataclass(frozen=True)
class TraceManifest:
    """What was OBSERVED — and, load-bearing, what was not."""
    trace_id: str
    omega: tuple
    frame_id: str                        # interpreter + observed bytes
    runs: int
    d_pos_files: tuple = ()              # (path, sha256) read inside Omega
    d_pos_imports: tuple = ()            # module names, incl. dynamic
    u_observed: tuple = ()               # (class, detail) that ACTUALLY happened
    u_structural: tuple = STRUCTURALLY_UNOBSERVABLE
    u_paths: tuple = ()                  # (file, qualname, unexecuted_lines)
    u_unentered: tuple = ()              # (file, qualname) never called at all
    external_touches: tuple = ()         # reads outside Omega — scope concern

    def unresolved_classes(self) -> frozenset:
        """Every class this manifest leaves open. Never empty, by law."""
        cls = {c for c, _d in self.u_observed}
        cls |= set(self.u_structural)
        if self.u_paths or self.u_unentered:
            cls.add(UNEXECUTED)
        return frozenset(cls)

    def coverage_verdict(self, relevant_classes) -> dict:
        """PASS only if NO class relevant to the property remains open.
        The tracer cannot argue a property is safe; it can only report
        that nothing it left unresolved is something the property needs."""
        # Family closure: declaring file_read sensitivity necessarily
        # declares os.stat/os.listdir sensitivity — you cannot care about a
        # file's bytes and disclaim its size or its directory's contents.
        open_relevant = sorted(self.unresolved_classes()
                               & expand_relevant(relevant_classes))
        if self.external_touches:
            return {"verdict": "UNKNOWN", "reason": "E_TOUCHED_OUTSIDE_OMEGA",
                    "detail": list(self.external_touches[:3])}
        if open_relevant:
            return {"verdict": "UNKNOWN", "reason": "E_UNRESOLVED_RELEVANT",
                    "classes": open_relevant}
        return {"verdict": "PASS", "observed_runs": self.runs}


def _build(rec: _Recorder, roots: tuple, label: str, runs: int) -> TraceManifest:
    files, imports, u_obs, external = {}, set(), [], []
    for cls, detail in rec.audit:
        if cls == "dynamic_import":
            imports.add(detail)
            continue
        if cls == "file_read":
            p = detail
            if rec.in_omega(p):
                files[p] = _sha(Path(p))
                continue
            if _runtime_infra(p):
                continue                 # interpreter machinery, not a dep
            external.append(p)
            continue
        u_obs.append((cls, detail))

    # Path coverage: executable lines of ENTERED code objects vs lines hit.
    executed = {(f, ln) for f, ln in rec.lines}
    u_paths = []
    participating = set()
    for (fname, qual), exec_lines in sorted(rec.codes.items()):
        participating.add(fname)
        missed = sorted(ln for ln in exec_lines if (fname, ln) not in executed)
        if missed:
            u_paths.append((fname, qual, tuple(missed)))

    # Functions defined in participating files but never entered at all.
    entered = {(f, q) for f, q in rec.codes}
    entered_names = {(f, q.split(".")[-1]) for f, q in rec.codes}
    unentered = []
    sub_line = []            # (file, funcname) with intra-line branches
    for fname in sorted(participating):
        try:
            tree = ast.parse(Path(fname).read_text(encoding="utf-8"))
        except (OSError, SyntaxError):
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not any(q.split(".")[-1] == node.name for f, q in entered
                           if f == fname):
                    unentered.append((fname, node.name))
                elif (fname, node.name) in entered_names:
                    # Crack-4 detection: an ENTERED function whose body
                    # contains a ternary or boolean short-circuit hides an
                    # untaken behaviour branch that LINE coverage cannot see.
                    if any(isinstance(n, (ast.IfExp, ast.BoolOp))
                           for n in ast.walk(node)):
                        sub_line.append((fname, node.name))
    if sub_line:
        u_obs.append(("sub_line_branch", ";".join(sorted(f"{f}:{n}" for f, n in sub_line))))

    frame_id = hashlib.sha256(canon({
        "python": list(sys.version_info[:3]),
        "files": sorted(files.items()),
    }).encode()).hexdigest()

    return TraceManifest(
        trace_id=f"nu:{label}",
        omega=tuple(sorted(roots)),
        frame_id=frame_id,
        runs=runs,
        d_pos_files=tuple(sorted(files.items())),
        d_pos_imports=tuple(sorted(imports)),
        u_observed=tuple(sorted(set(u_obs))),
        u_paths=tuple(u_paths),
        u_unentered=tuple(sorted(set(unentered))),
        external_touches=tuple(sorted(set(external))),
    )


def trace_run(fn, omega, label="run", args=(), kwargs=None) -> tuple:
    """Observe one execution. Returns (result, TraceManifest)."""
    kwargs = kwargs or {}
    roots = tuple(str(Path(r).resolve()) for r in omega)
    rec = _Recorder(roots)
    _install_hook()
    _ACTIVE.append(rec)
    previous = sys.gettrace()
    sys.settrace(_make_line_tracer(rec))
    try:
        result = fn(*args, **kwargs)
    finally:
        sys.settrace(previous)
        _ACTIVE.pop()
    return result, _build(rec, roots, label, runs=1)


def fold(manifests: list) -> TraceManifest:
    """Coverage earned by REPEATED observation. Positive evidence unions;
    a path stays unresolved only if it was missed in EVERY run. Blind
    spots never fold away — no number of runs empties u_structural."""
    if not manifests:
        raise ValueError("E_NO_OBSERVATIONS")
    base = manifests[0]
    files, imports, u_obs, external, unentered = {}, set(), set(), set(), set()
    hit: dict = {}
    executable: dict = {}
    for m in manifests:
        files.update(dict(m.d_pos_files))
        imports.update(m.d_pos_imports)
        u_obs.update(m.u_observed)
        external.update(m.external_touches)
        for f, q, missed in m.u_paths:
            executable.setdefault((f, q), set()).update(missed)
        for f, q, missed in m.u_paths:
            hit.setdefault((f, q), set())
    for m in manifests:                  # a line missed here may be hit there
        for f, q, missed in m.u_paths:
            still = executable[(f, q)] - set(missed)
            hit[(f, q)] |= still
    for m in manifests:
        unentered |= set(m.u_unentered)
    for m in manifests:                  # entered in ANY run -> not unentered
        entered_names = {q.split(".")[-1] for _f, q, _x in m.u_paths}
        unentered -= {(f, n) for f, n in unentered if n in entered_names}

    u_paths = tuple((f, q, tuple(sorted(executable[(f, q)] - hit[(f, q)])))
                    for f, q in sorted(executable)
                    if executable[(f, q)] - hit[(f, q)])
    return TraceManifest(
        trace_id=base.trace_id + f"+fold{len(manifests)}",
        omega=base.omega, frame_id=base.frame_id, runs=sum(m.runs for m in manifests),
        d_pos_files=tuple(sorted(files.items())),
        d_pos_imports=tuple(sorted(imports)),
        u_observed=tuple(sorted(u_obs)),
        u_paths=u_paths,
        u_unentered=tuple(sorted(unentered)),
        external_touches=tuple(sorted(external)),
    )


def to_unresolved_pairs(m: TraceManifest) -> tuple:
    """Project a manifest into C17's Pi_D.unresolved shape: (file, class).
    This is how nu feeds the existing coverage kernel unchanged."""
    out = []
    for cls, detail in m.u_observed:
        out.append((detail or "<runtime>", cls))
    for f, _q, _missed in m.u_paths:
        out.append((f, UNEXECUTED))
    for f, _q in m.u_unentered:
        out.append((f, UNEXECUTED))
    for cls in m.u_structural:
        out.append(("<tracer-blind-spot>", cls))
    return tuple(sorted(set(out)))


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def augment_pid(pi, manifest: TraceManifest):
    """Integration surface: fold observed evidence into an existing C17
    certificate. Observed reads join D+ (so a later change to a
    dynamically-loaded file INVALIDATES, which static resolution alone
    would miss); observed and structural blind spots join U."""
    from coverage_core import PiD
    d_pos = dict(pi.d_pos)
    d_pos.update({p: h for p, h in manifest.d_pos_files})
    return PiD(
        nu=pi.nu, omega=pi.omega, d_pos=d_pos, d_neg=dict(pi.d_neg),
        analyzed=tuple(sorted(set(pi.analyzed) | {"runtime_observation"})),
        unresolved=tuple(sorted(set(pi.unresolved) | set(to_unresolved_pairs(manifest)))),
        sigma={**pi.sigma, "nu_trace": manifest.trace_id,
               "nu_runs": manifest.runs, "nu_frame": manifest.frame_id},
    )
