"""C17 — Dependency-Coverage Soundness kernel.

NON_SOVEREIGN · authority=false · ledger_effect=none.

HELEN must earn knowledge of its dependency boundary before it may reuse
knowledge across that boundary. The research object is a coverage
certificate, not a Boolean:

    Pi_D = (nu, Omega, D+, D-, analyzed, unresolved, sigma)

Laws implemented here:
  - Property-relative poisoning: U_P != {} => CoverageVerdict = UNKNOWN,
    where U_P is the set of unresolved classes RELEVANT to property P.
    An opaque-but-irrelevant subsystem does not poison unrelated witnesses.
  - not discovered != proved irrelevant: relevance comes from the property
    declaration, never from the resolver's failure to observe something.
  - Ordering: COVERAGE -> STABILITY -> TRANSPORT. Never intersection-test
    first and assume coverage.
  - Decision: UNKNOWN if VerifyCoverage fails; INVALIDATED if coverage
    verifies but dependencies moved; VALID_BY_TRANSPORT only when both hold.
  - Safety asymmetry: false negative transport < false positive transport.
    Every ambiguous branch resolves toward UNKNOWN/INVALIDATED.
  - C13 discipline: derive_support HARVESTS the frame (hashes, listings)
    from the filesystem; the frame is never caller-supplied.

Deterministic: sorted walks, sha256, no wall-time, no randomness.
"""
from __future__ import annotations

import ast
import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path

RESOLVER_VERSION = "c17-resolver/0.1"

UNKNOWN = "UNKNOWN"
INVALIDATED = "INVALIDATED"
VALID_BY_TRANSPORT = "VALID_BY_TRANSPORT"

# Opaque dependency classes for Python, defaulting conservative.
OPAQUE_CLASSES = ("dynamic_import", "subprocess", "env_read", "file_read",
                  "network", "codegen")

_OPAQUE_MARKERS = {
    "dynamic_import": {"__import__", "import_module", "importlib"},
    "subprocess": {"subprocess", "popen", "system"},
    "network": {"socket", "urlopen", "requests", "http"},
    "codegen": {"eval", "exec", "compile"},
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@dataclass(frozen=True)
class Property:
    """What a witness certifies, with its declared sensitivity. Relevance
    is declared by the property author — never inferred from resolver
    silence (not discovered != proved irrelevant)."""
    prop_id: str
    subject_files: tuple            # files whose behavior P speaks about
    relevant_classes: tuple         # opaque classes that could influence P
    discovery_dirs: tuple = ()      # for absence/completeness (C11-style) claims


@dataclass(frozen=True)
class Witness:
    witness_id: str
    prop_id: str
    frame_id: str                   # harvested frame the witness was earned in
    payload: str


def _scan_file(path: Path) -> set[str]:
    """Conservative opaque-class detection: parse failure => all classes."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError):
        return set(OPAQUE_CLASSES)
    found: set[str] = set()
    for node in ast.walk(tree):
        names: set[str] = set()
        if isinstance(node, ast.Call):
            f = node.func
            names.add(getattr(f, "id", getattr(f, "attr", "")).lower())
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            mods = [a.name for a in node.names] if isinstance(node, ast.Import) \
                else [node.module or ""]
            names.update(m.split(".")[0].lower() for m in mods)
        elif isinstance(node, ast.Attribute) and node.attr == "environ":
            found.add("env_read")
        elif isinstance(node, ast.Name) and node.id == "open":
            found.add("file_read")
        for cls, markers in _OPAQUE_MARKERS.items():
            if names & markers:
                found.add(cls)
    return found


def _static_imports(path: Path, omega: tuple[Path, ...]) -> set[Path]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError):
        return set()
    mods: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            mods.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            mods.add(node.module.split(".")[0])
    out = set()
    for root in omega:
        for m in mods:
            cand = root / f"{m}.py"
            if cand.exists():
                out.add(cand)
    return out


@dataclass(frozen=True)
class PiD:
    """The coverage certificate."""
    nu: str
    omega: tuple                    # declared semantic universe (roots)
    d_pos: dict = field(default_factory=dict)    # path -> sha256 (resolved deps)
    d_neg: dict = field(default_factory=dict)    # dir -> sorted listing (discovery)
    analyzed: tuple = ()            # classes actually analyzed
    unresolved: tuple = ()          # opaque classes observed, per file
    sigma: dict = field(default_factory=dict)    # evidence incl. harvested frame


def harvest_frame(omega: tuple[Path, ...]) -> str:
    items = []
    for root in sorted(omega):
        for p in sorted(root.rglob("*")):
            if p.is_file():
                items.append(f"{p.relative_to(root)}:{_sha(p)}")
    return hashlib.sha256("\n".join(items).encode()).hexdigest()


def derive_support(prop: Property, omega: tuple[Path, ...]) -> PiD:
    """Resolve what we know AND record what we explicitly do not know.
    The frame is harvested here, never injected."""
    d_pos: dict[str, str] = {}
    unresolved: list[tuple[str, str]] = []
    for f in prop.subject_files:
        p = Path(f)
        d_pos[str(p)] = _sha(p)
        for dep in sorted(_static_imports(p, omega)):
            d_pos[str(dep)] = _sha(dep)
        for cls in sorted(_scan_file(p)):
            unresolved.append((str(p), cls))
    d_neg = {}
    for d in prop.discovery_dirs:
        dd = Path(d)
        d_neg[str(dd)] = tuple(sorted(str(x.relative_to(dd)) for x in dd.rglob("*") if x.is_file()))
    return PiD(
        nu=RESOLVER_VERSION,
        omega=tuple(str(r) for r in omega),
        d_pos=d_pos,
        d_neg=d_neg,
        analyzed=("static_imports", "file_hashes", "discovery_listing"),
        unresolved=tuple(unresolved),
        sigma={"frame_id": harvest_frame(omega),
               "derivation": "ast static imports + opaque-class scan + dir listing"},
    )


def verify_coverage(pi: PiD, w: Witness, prop: Property,
                    frame_id: str) -> tuple[bool, str]:
    """BindFrame AND BindWitness AND BindModel AND BindScope AND
    CoverageSufficientFor(P). Failure of any binding => UNKNOWN upstream."""
    if pi.nu != RESOLVER_VERSION:
        return False, "E_BIND_MODEL"
    if pi.sigma.get("frame_id") != frame_id:
        return False, "E_BIND_FRAME"
    if w.prop_id != prop.prop_id or w.frame_id != frame_id:
        return False, "E_BIND_WITNESS"
    omega_roots = tuple(Path(o) for o in pi.omega)
    for f in prop.subject_files:
        if not any(Path(f).is_relative_to(r) for r in omega_roots):
            return False, "E_BIND_SCOPE"
    # CoverageSufficientFor(P): property-relative unresolved classes.
    u_p = {cls for (_f, cls) in pi.unresolved if cls in prop.relevant_classes}
    if u_p:
        return False, f"E_UNRESOLVED_RELEVANT:{','.join(sorted(u_p))}"
    return True, "OK"


def stable_deps(pi: PiD, prop: Property) -> tuple[bool, str]:
    """Recompute against the CURRENT disk. D+ instability = changed hash;
    D- instability = the discovery listing moved (a new artifact attacks
    an absence claim even when every inspected file is unchanged)."""
    for path, sha in sorted(pi.d_pos.items()):
        p = Path(path)
        if not p.exists() or _sha(p) != sha:
            return False, f"E_DEP_CHANGED:{path}"
    for d, listing in sorted(pi.d_neg.items()):
        dd = Path(d)
        now = tuple(sorted(str(x.relative_to(dd)) for x in dd.rglob("*") if x.is_file()))
        if now != listing:
            return False, f"E_DISCOVERY_EXPANDED:{d}"
    return True, "OK"


def decide(w: Witness, pi: PiD, prop: Property, frame_id: str) -> dict:
    """COVERAGE -> STABILITY -> TRANSPORT, in that order, fail-closed."""
    ok, reason = verify_coverage(pi, w, prop, frame_id)
    if not ok:
        return {"decision": UNKNOWN, "reason": reason}
    ok, reason = stable_deps(pi, prop)
    if not ok:
        return {"decision": INVALIDATED, "reason": reason}
    new_frame = harvest_frame(tuple(Path(o) for o in pi.omega))
    transported = Witness(witness_id=w.witness_id + "'", prop_id=w.prop_id,
                          frame_id=new_frame, payload=w.payload)
    return {"decision": VALID_BY_TRANSPORT, "reason": "OK",
            "transported": transported}


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)
