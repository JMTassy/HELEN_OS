#!/usr/bin/env python3
"""Collapse an artifact list into independent provenance root families.

Fourteen artifacts can be two roots: originals spawn copies, forwards,
exports, revisions, retrospectives and sanctuary copies, none of which
add evidentiary weight. A proxy whose content derives solely from the
subject is the SAME root as the subject (Author(x) != Root(x)).

Input (stdin or file arg): JSON list of artifacts:
    {"id": str,
     "kind": "original" | "copy" | "forward" | "export" | "revision" |
             "retrospective" | "sanctuary_copy" | "proxy",
     "derives_from": str | null}   # required non-null for every non-original

Output (stdout): JSON with root families and the two counts that must
never be conflated: n_artifacts and n_independent_roots.

Deterministic: same input, byte-identical output. Stdlib only.
Run `root_normalizer.py --selftest` before trusting a modified copy.
"""
from __future__ import annotations

import json
import sys

DERIVED_KINDS = frozenset({
    "copy", "forward", "export", "revision", "retrospective",
    "sanctuary_copy", "proxy",
})
KINDS = DERIVED_KINDS | {"original"}


def normalize(artifacts: list[dict]) -> dict:
    ids = [a.get("id") for a in artifacts]
    if len(ids) != len(set(ids)) or any(not i for i in ids):
        return {"ok": False, "reason": "E_DUPLICATE_OR_MISSING_ID"}

    by_id = {a["id"]: a for a in artifacts}
    for a in artifacts:
        kind = a.get("kind")
        if kind not in KINDS:
            return {"ok": False, "reason": "E_UNKNOWN_KIND",
                    "artifact": a["id"]}
        src = a.get("derives_from")
        if kind == "original":
            if src is not None:
                return {"ok": False, "reason": "E_ORIGINAL_WITH_SOURCE",
                        "artifact": a["id"]}
        else:
            # A derived artifact with no declared source cannot be
            # silently promoted to a root — that is exactly the
            # copy != independent-root error. It is refused, not guessed.
            if src is None:
                return {"ok": False, "reason": "E_DERIVED_WITHOUT_SOURCE",
                        "artifact": a["id"]}
            if src not in by_id:
                return {"ok": False, "reason": "E_DANGLING_SOURCE",
                        "artifact": a["id"], "missing": src}

    # Walk each artifact to its root; the walk is finite iff acyclic.
    def root_of(aid: str) -> str | None:
        seen = set()
        cur = aid
        while by_id[cur].get("derives_from") is not None:
            if cur in seen:
                return None
            seen.add(cur)
            cur = by_id[cur]["derives_from"]
        return cur

    families: dict[str, list[str]] = {}
    for a in artifacts:
        r = root_of(a["id"])
        if r is None:
            return {"ok": False, "reason": "E_DERIVATION_CYCLE",
                    "artifact": a["id"]}
        families.setdefault(r, []).append(a["id"])

    fam_sorted = {r: sorted(m) for r, m in sorted(families.items())}
    return {
        "ok": True,
        "n_artifacts": len(artifacts),
        "n_independent_roots": len(fam_sorted),
        "root_families": fam_sorted,
        "law": "copy != independent root; Author(x) != Root(x)",
    }


def selftest() -> None:
    # The canonical 14 -> 2 case: two originals, each buried under a
    # pile of copies/forwards/exports/revisions and one proxy.
    arts = [{"id": "r1", "kind": "original", "derives_from": None},
            {"id": "r2", "kind": "original", "derives_from": None}]
    for i, kind in enumerate(["copy", "forward", "export", "revision",
                              "retrospective", "sanctuary_copy",
                              "proxy"]):
        arts.append({"id": f"a{i}", "kind": kind, "derives_from": "r1"})
    for i, kind in enumerate(["copy", "forward", "copy", "export",
                              "revision"]):
        arts.append({"id": f"b{i}", "kind": kind, "derives_from": "r2"})
    v = normalize(arts)
    assert v["ok"] and v["n_artifacts"] == 14, v
    assert v["n_independent_roots"] == 2, v

    # Chains resolve transitively: copy of a forward of r1 is r1.
    chain = [{"id": "r1", "kind": "original", "derives_from": None},
             {"id": "f", "kind": "forward", "derives_from": "r1"},
             {"id": "c", "kind": "copy", "derives_from": "f"}]
    assert normalize(chain)["n_independent_roots"] == 1

    # A biographer/proxy deriving solely from the subject is the same
    # root — it never mints a second independent witness.
    proxy = [{"id": "subject", "kind": "original", "derives_from": None},
             {"id": "biographer", "kind": "proxy",
              "derives_from": "subject"}]
    assert normalize(proxy)["n_independent_roots"] == 1

    # Refusals, never guesses.
    assert normalize([{"id": "x", "kind": "copy", "derives_from": None}
                      ])["reason"] == "E_DERIVED_WITHOUT_SOURCE"
    assert normalize([{"id": "x", "kind": "copy", "derives_from": "gone"}
                      ])["reason"] == "E_DANGLING_SOURCE"
    assert normalize([{"id": "x", "kind": "original",
                       "derives_from": "y"},
                      {"id": "y", "kind": "original", "derives_from": None}
                      ])["reason"] == "E_ORIGINAL_WITH_SOURCE"
    cyc = [{"id": "p", "kind": "copy", "derives_from": "q"},
           {"id": "q", "kind": "copy", "derives_from": "p"}]
    assert normalize(cyc)["reason"] == "E_DERIVATION_CYCLE"
    assert normalize([{"id": "x", "kind": "vibes", "derives_from": None}
                      ])["reason"] == "E_UNKNOWN_KIND"
    assert normalize([{"id": "x", "kind": "original", "derives_from": None},
                      {"id": "x", "kind": "original", "derives_from": None}
                      ])["reason"] == "E_DUPLICATE_OR_MISSING_ID"

    # Determinism: byte-identical serialization.
    a = json.dumps(normalize(arts), sort_keys=True)
    b = json.dumps(normalize(list(reversed(arts))), sort_keys=True)
    assert a == b
    print("root_normalizer selftest: OK (10 checks)")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
        sys.exit(0)
    src = sys.argv[1] if len(sys.argv) > 1 else None
    data = json.load(open(src)) if src else json.load(sys.stdin)
    out = normalize(data)
    print(json.dumps(out, indent=2, sort_keys=True))
    sys.exit(0 if out.get("ok") else 1)
