#!/usr/bin/env python3
"""
GENESIS_LOOP — lineage-aware evolutionary distinction-search over CHAOS_GARDEN survivors.
STAGED, NOT AUTO-LAUNCHED. Refuses to run until the chaos receipt exists (no seeding on guesses).

Growth law:  Growth_t>0  ⟺  ∃X: Δ_struct(X)>0   (NOT tokens↑).
S_{t+1} = argmax_{X∈beam} Score(X), beam k=2. STOP on dryness (ρ<ε, 3 epochs).
NO_CLAIM · FABLE_CALLS=0 · ΔEvidence=ΔWarrant=ΔAuthority=0.
"""
import json, re, sys, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).parent
RECEIPT = ROOT / "ASYNC_WULMATH_CHAOS_GARDEN_V1_RECEIPT.json"
OUT = ROOT / "genesis";
OLLAMA = "http://localhost:11434/api/chat"
HER = "hf.co/unsloth/gemma-4-26B-A4B-it-GGUF:UD-Q3_K_XL"
HAL = "hf.co/huihui-ai/Huihui-Qwen3.8-27B-abliterated-GGUF:Q2_K"
K, EPS, DRY_MAX, MAX_EPOCHS = 3, 0.34, 3, 24   # K=3: top-3 CHIDDUSH become parents
LAMBDA = 0.35   # anti-monoculture: diversity pressure weight (E7)
PARASITE_G = 0.34   # generativity floor: high descendants + low G = idea-spam parasite (E8)
# LAW: SearchFitness (reproductive) ≠ EpistemicFitness (truth). A wrong object may be a
# great search operator. χ reproduces its transformation T, NEVER its belief.
# χ = (x, ΔS, D, F, T, L, G): object, structural-delta, discriminator, falsifier,
#     induced-search-transform, lineage, downstream-generativity.


def load_seeds():
    # PREFER the hard-gated S0 (HAL counterfeit survivors) over self-reported strangeness.
    S0 = ROOT / "CHIDDUSH_S0.json"
    if S0.exists():
        seeds = json.loads(S0.read_text())
        print(f"GENESIS seeded from HARD-GATED CHIDDUSH_S0 ({len(seeds)} counterfeit-survivors).")
        return seeds
    if not RECEIPT.exists():
        print("SEEDS_NOT_READY — no CHIDDUSH_S0 and no chaos receipt. GENESIS refuses to guess. STOP.")
        sys.exit(0)
    print("⚠ CHIDDUSH_S0 absent — falling back to self-reported top5_strangest (NOT hard-gated).")
    r = json.loads(RECEIPT.read_text())
    seeds = []
    for o in r.get("top5_strangest", []):
        seeds.append({"id": f"S_{len(seeds)}", "q": f"Is «{o['name']}» a distinct structure or a "
                      f"costume of its nearest known relative?", "g": o.get("strange", ""),
                      "c": "", "lineage": [o["name"]], "origin": o["stream"]})
    for c in r.get("cross_pollination_detail", []):   # Δ_HA survivors are the richest seeds
        seeds.append({"id": f"S_{len(seeds)}", "q": f"Does the cross-basin object «{c['name']}» "
                      f"carry structure absent from its parent «{c['parent']}»?",
                      "g": c.get("seed", ""), "c": "", "lineage": [c["parent"], c["name"]],
                      "origin": "CROSS"})
    return seeds


def ollama(model, sys_p, user, temp=0.9, np=480, timeout=420):
    body = json.dumps({"model": model, "stream": False, "think": False,
        "messages": [{"role": "system", "content": sys_p}, {"role": "user", "content": user}],
        "options": {"temperature": temp, "num_predict": np, "top_p": 0.95}}).encode()
    req = urllib.request.Request(OLLAMA, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as x: d = json.loads(x.read())
    m = d.get("message", {}) or {}
    return m.get("content") or m.get("thinking") or ""


def norm(s): return re.sub(r"[^a-z0-9 ]", "", s.lower()).strip()
def field(t, k):
    m = re.search(rf"^{k}:\s*(.+?)\s*$", t, re.I | re.M); return m.group(1).strip() if m else ""


def is_growth(X, lineage):
    """Δ_struct>0: normalized seed not already in lineage AND not self-tagged RENAMING_ONLY."""
    k = norm(X.get("formal_seed", ""))[:60]
    prior = {norm(l)[:60] for l in lineage}
    return bool(k) and k not in prior and "renaming_only" not in X.get("why", "").lower()


def _toks(s): return set(norm(s).split())
def distance(X, pop):
    """1 - max token-overlap with population (structural distance proxy). E7 diversity."""
    a = _toks(X.get("formal_seed", ""))
    if not a or not pop: return 1.0
    best = max((len(a & _toks(p.get("formal_seed", ""))) / max(1, len(a | _toks(p.get("formal_seed", ""))))
                for p in pop if p is not X), default=0.0)
    return round(1 - best, 3)


def score(X, pop):
    # SearchFitness (reproductive), NOT truth: R(h)=αD+βF+γB−δC + λ·diversity
    N = 1.0 if X.get("_growth") else 0.0                    # structural novelty (Δ_𝒮 gated)
    D = 1.0 if X.get("discriminator") else 0.0             # discriminative power
    F = 1.0 if X.get("discriminator") and "test" in (X.get("discriminator", "").lower()+"x") else 0.5  # falsifiability
    C = min(1.0, len(X.get("formal_seed", "")) / 80)       # consequentiality proxy
    R = 0.5 if not X.get("_growth") else 0.0               # redundancy/cost penalty
    div = distance(X, pop)                                  # anti-monoculture
    return round(0.35*N + 0.3*D + 0.15*F + 0.1*C - 0.3*R + LAMBDA*div, 3)


FMT = ("NAME: <..>\nFORMAL_SEED: <one relation>\nWHY_NOT_JUST_RENAMING: <diff | RENAMING_ONLY>\n"
       "DISCRIMINATOR: <cheapest test separating it from its counterfeit>\nEND")


def main():
    OUT.mkdir(exist_ok=True)
    seeds = load_seeds()
    print(f"GENESIS seeded from {len(seeds)} real chaos survivors.", flush=True)
    beam = seeds[:K]
    dry = 0
    log = []
    for e in range(1, MAX_EPOCHS + 1):
        proposals = []
        for S in beam:
            for model, sysp, kind in [(HER, "constructive heterodoxy; mutate the seed structurally", "MUTATE"),
                                       (HAL, "adversarial heterodoxy; construct the nearest counterfeit + its discriminator", "COUNTERFEIT")]:
                u = (f"Seed q: {S['q']}\ng: {S['g'][:200]}\nLineage: {S['lineage']}\n\n"
                     f"{kind} → emit ONE object:\n{FMT}")
                try: raw = ollama(model, sysp, u)
                except Exception as ex: raw = f"__ERROR__ {ex}"
                X = {"parent": S["id"], "kind": kind, "name": field(raw, "NAME"),
                     "formal_seed": field(raw, "FORMAL_SEED"), "why": field(raw, "WHY_NOT_JUST_RENAMING"),
                     "discriminator": field(raw, "DISCRIMINATOR"), "lineage": S["lineage"], "raw": raw}
                X["_growth"] = is_growth(X, S["lineage"])
                X["_transform"] = X.get("kind")   # χ.T: induced search transformation
                proposals.append(X)
        for X in proposals:                        # score AFTER population known (diversity needs peers)
            X["_score"] = score(X, proposals)
        # quotient + dryness
        seen, distinct = set(), []
        for X in proposals:
            k = norm(X["name"] + " " + X["formal_seed"])[:60]
            if X["name"] and k not in seen: seen.add(k); distinct.append(X)
        rho = round(sum(1 for X in distinct if X["_growth"]) / max(1, len(proposals)), 3)
        dry = dry + 1 if rho < EPS else 0
        beam = sorted([X for X in distinct if X["_growth"]] or distinct,
                      key=lambda X: -X["_score"])[:K]
        # promote beam survivors into next seeds (carry lineage forward)
        beam = [{"id": f"S_{e}_{i}", "q": f"Attack the distinction in «{X['name']}»",
                 "g": X["formal_seed"], "c": "", "lineage": X["lineage"] + [X["name"]],
                 "origin": X["kind"]} for i, X in enumerate(beam)]
        log.append({"epoch": e, "rho": rho, "dry": dry, "beam": [b["lineage"][-1] for b in beam]})
        (OUT / f"epoch_{e:02d}.json").write_text(json.dumps({"proposals": proposals, "beam": beam}, indent=2, ensure_ascii=False))
        print(f"🌱 E{e:02d} ρ={rho} dry={dry} beam={[b['lineage'][-1][:28] for b in beam]}", flush=True)
        if dry >= DRY_MAX:
            print(f"STOP_DRYNESS at E{e} (ρ<{EPS} for {DRY_MAX} epochs)"); break

    receipt = {"schema": "GENESIS_LOOP_V0_RECEIPT", "authority": False, "canon": False,
        "claim": "NO_CLAIM", "fable_calls": 0, "authority_delta": 0, "commit": "none", "push": "none",
        "seeded_from": str(RECEIPT.name), "n_seeds": len(seeds),
        "epochs_run": len(log), "stop_reason": "DRYNESS" if dry >= DRY_MAX else "MAX_EPOCHS",
        "trajectory": log, "growth_law": "Growth⟺Δ_struct>0; S_{t+1}=argmax beam; k=%d" % K,
        "claim_ceiling": "Lineage-aware recursive distinction search in a NO_CLAIM Garden. "
                         "No object validated; nothing promoted."}
    (ROOT / "GENESIS_LOOP_V0_RECEIPT.json").write_text(json.dumps(receipt, indent=2, ensure_ascii=False))
    print("🌈 GENESIS receipt written · ΔAuthority=0 · NO_CLAIM")


if __name__ == "__main__":
    main()
