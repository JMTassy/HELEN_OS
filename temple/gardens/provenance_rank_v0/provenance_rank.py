#!/usr/bin/env python3
"""
PROVENANCE_RANK_V0 — the idempotent-provenance kernel, made executable.

This is the "deepest piece" turned into code: evidence combines by UNION of roots,
not by count. It is also JESTER's MIRROR transform made load-bearing — apply the
rule "more mentions ⇒ more support" to itself and it collapses:

    x + x = x            (idempotent provenance semiring; Green–Tannen)
    N_repr ↑  ⇏  N_epi ↑   (representations ≠ independent roots)
    Γ↑ ⇏ A↑ · attention ≠ authority · ΔAuthority = 0

Deterministic · local-first · FABLE_CALLS=0 · authority=false · NO_CLAIM.
Input: items = [{"id":..., "roots":[root_id,...]}].  Roots are taken as ATOMIC
independent origins (stated assumption; deeper root-correlation is future work).
"""
import json, sys
from pathlib import Path


def gf2_rank(rows):
    """Rank of a 0/1 incidence matrix over GF(2) — structural independence check."""
    basis = []
    for r in rows:
        v = set(i for i, b in enumerate(r) if b)
        for b in basis:
            piv = min(b)
            if piv in v:
                v ^= b
        if v:
            basis.append(v)
    return len(basis)


def census(items):
    roots_all = sorted({r for it in items for r in it.get("roots", [])})
    idx = {r: i for i, r in enumerate(roots_all)}
    N_repr = len(items)
    N_epi = len(roots_all)                       # atomic independent origins (union)
    distinct_sets = {tuple(sorted(set(it.get("roots", [])))) for it in items}
    # per-root representation share (how much narrative gravity each root holds)
    share = {r: sum(1 for it in items if r in it.get("roots", [])) / max(1, N_repr)
             for r in roots_all}
    dominant = max(share.items(), key=lambda kv: kv[1]) if share else (None, 0)
    rows = [[1 if r in set(it.get("roots", [])) else 0 for r in roots_all] for it in items]
    rank = gf2_rank(rows)
    return {
        "N_repr": N_repr,
        "N_epi": N_epi,                          # ← effective independent evidence
        "distinct_root_sets": len(distinct_sets),
        "rank_gf2": rank,                        # linear-algebra cross-check
        "inflation_factor": round(N_repr / max(1, N_epi), 2),
        "dominant_root": dominant[0],
        "dominant_share": round(dominant[1], 3),
        "root_shares": {r: round(s, 3) for r, s in sorted(share.items(), key=lambda kv: -kv[1])},
        "law": "evidence = ∪ roots (idempotent) · N_repr⇏N_epi · Γ↑⇏A↑ · ΔA=0",
    }


def mirror(claimed_witnesses, items):
    """JESTER MIRROR: the claim says N witnesses; provenance says how many roots."""
    c = census(items)
    return {
        "claimed_witnesses": claimed_witnesses,
        "independent_roots": c["N_epi"],
        "deflation": f"{claimed_witnesses} → {c['N_epi']}",
        "verdict": ("INFLATED_BY_REPETITION" if c["N_epi"] < claimed_witnesses else "OK"),
        "note": "frame-robustness / repetition is NOT authority (ΔA=0)",
    }


# --- self-test: the real χ* SURVIVED_20 census (from its own citations) ----------
CHI_STAR = (
    [{"id": f"E{e:02d}", "roots": ["Texte_colle.txt"]} for e in (1, 2, 3)] +
    [{"id": f"E{e:02d}", "roots": ["helen_temporal_chiddush_4vol_v1.md"]} for e in range(4, 18)] +
    [{"id": "E18", "roots": ["Fichier_markdown_2.md"]},
     {"id": "E19", "roots": ["Fichier_markdown.md"]},
     {"id": "E20", "roots": ["Fichier_markdown.md"]}]
)


def main():
    if len(sys.argv) > 1 and Path(sys.argv[1]).exists():
        items = json.loads(Path(sys.argv[1]).read_text())
        label = sys.argv[1]
    else:
        items, label = CHI_STAR, "χ* SURVIVED_20 (self-test)"
    c = census(items)
    m = mirror(len(items), items)
    print("═" * 60)
    print(f"  PROVENANCE_RANK · {label}")
    print("═" * 60)
    print(f"  N_repr (representations)      = {c['N_repr']}")
    print(f"  N_epi  (independent roots)    = {c['N_epi']}   ← effective evidence")
    print(f"  rank_gf2 / distinct_root_sets = {c['rank_gf2']} / {c['distinct_root_sets']}")
    print(f"  inflation_factor N_repr/N_epi = {c['inflation_factor']}×")
    print(f"  dominant_root                 = {c['dominant_root']}  ({c['dominant_share']*100:.0f}%)")
    print(f"  MIRROR                        = {m['deflation']}  → {m['verdict']}")
    print("─" * 60)
    print(f"  {c['law']}")
    out = {"label": label, "census": c, "mirror": m,
           "authority": False, "canon": False, "claim": "NO_CLAIM", "authority_delta": 0}
    (Path(__file__).resolve().parent / "PROVENANCE_RANK_SELFTEST.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
