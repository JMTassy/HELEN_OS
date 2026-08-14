"""CLAIM-LEVEL EPISTEMIC ROOT ACCOUNTING. 🔵 OBSERVED · authority=false.

Bibliographic independence ⊬ epistemic independence. A claim is not corroborated
because it appears in many documents; what matters is how many INDEPENDENT roots
its representations descend from.

    Author(s) ≠ EpistemicRoot(c)          different author ⊬ independent witness
    N_documents ≫ N_epi is normal         Founder→journalist→biography = 1 root
    Λ_proxy = N_representations / N_epi    representational amplification factor
    warrant tracks N_epi, NEVER N_representations   (rep multiplicity ⊬ warrant)

Independence is computed PER CLAIM, not per source: the same book can be a proxy
(N_epi=1) for the subject's origin myth AND an independent root for something the
author personally witnessed. So root accounting is claim-local.

This is the general form of the night's laws: the fabricating-lane banner, the
Crowley/Sanders narrator, and 37 newspapers repeating one interview are the same
shape — representation mass without independent evidence.
Determinism: pure functions.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Representation:
    """One appearance of a claim (a document, quote, article, restatement).
    `root` is the epistemic root it ULTIMATELY derives from — two representations
    sharing a root are dependent (one witness), not two."""
    id: str
    root: str
    kind: str = ""          # metadata only (book/interview/witness/registry/...)


def _component_map(roots: set, dependencies) -> dict:
    """root → component representative, under ~dep (union-find, transitive closure).
    `dependencies` = (root_a, root_b) pairs CONFIRMED to share an upstream and thus
    collapse. Missing edges are NOT collapsed — and NOT assumed independent either
    (see n_unresolved / UNRESOLVED handling)."""
    parent = {r: r for r in roots}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a, b in dependencies:
        if a in parent and b in parent:
            parent[find(a)] = find(b)
    return {r: find(r) for r in roots}


def _root_components(roots: set, dependencies) -> int:
    return len(set(_component_map(roots, dependencies).values()))


def independent_roots(reps) -> set:
    """The raw (pre-collapse) root ids present. For the collapsed COUNT use n_epi."""
    return {r.root for r in reps}


def n_epi(reps, dependencies=()) -> int:
    """Independent epistemic root count for a claim = |R(c)/~dep,c|. Same-id roots
    collapse trivially; `dependencies` collapses DIFFERENT-id roots that share an
    upstream (hidden common dependency)."""
    return _root_components(independent_roots(reps), dependencies)


def n_representations(reps) -> int:
    return len(reps)


def lambda_proxy(reps, dependencies=()) -> float:
    """Λ_proxy = representations / independent roots. 1.0 = every representation is
    its own root. High = amplification without independence. A pressure metric, NOT
    a probability of falsehood."""
    return n_representations(reps) / max(1, n_epi(reps, dependencies))


def proxy_laundering(reps, dependencies=(), warn_at: float = 2.0) -> bool:
    """True when representation mass exceeds independent roots enough to mislead a
    naive 'N sources corroborate' reading. Amplification iff N_rep > N_epi (after
    ~dep collapse); flagged at Λ_proxy ≥ warn_at."""
    ne = n_epi(reps, dependencies)
    return n_representations(reps) > ne and lambda_proxy(reps, dependencies) >= warn_at


def warrant_root_count(reps, dependencies=()) -> int:
    """The quantity a warrant may depend on: INDEPENDENT roots (post-collapse) —
    never the number of representations. Mechanical form of `rep multiplicity ⊬ warrant`."""
    return n_epi(reps, dependencies)


# ── three-valued dependence: UNRESOLVED ≠ INDEPENDENT, UNRESOLVED ≠ DEPENDENT ──
def n_unresolved(reps, unresolved=()) -> int:
    """Distinct roots whose independence is UNRESOLVED (lineage metadata missing).
    Missing provenance must NOT silently count as independence — so n_epi is an
    UPPER bound whenever this is > 0."""
    roots = independent_roots(reps)
    touched = set()
    for a, b in unresolved:
        if a in roots:
            touched.add(a)
        if b in roots:
            touched.add(b)
    return len(touched)


def dependency_uncertainty(reps, unresolved=()) -> float:
    """U_dep = unresolved roots / total roots. High ⇒ n_epi is optimistic; treat with caution."""
    total = len(independent_roots(reps))
    return n_unresolved(reps, unresolved) / max(1, total)


# ── structural (N_epi) vs evaluative (W): N_epi↑ ⊬ W↑ ──
def warrant_supported(reps, dependencies=(), root_quality=None, quality_floor: float = 0.5,
                      min_strong_roots: int = 2) -> bool:
    """Warrant is EVALUATIVE, not structural. N_epi counts independent provenance
    classes; warrant additionally requires enough of those classes to carry
    sufficient-quality evidence. Ten independent RUMORS (N_epi=10, all low quality)
    do NOT warrant a claim: N_epi↑ ⊬ W↑. root_quality maps root id → [0,1]."""
    root_quality = root_quality or {}
    comp = _component_map(independent_roots(reps), dependencies)
    best = {}                                   # component → best root quality in it
    for root, rep in comp.items():
        q = root_quality.get(root, 0.0)
        best[rep] = max(best.get(rep, 0.0), q)
    strong = sum(1 for q in best.values() if q >= quality_floor)
    return strong >= min_strong_roots
