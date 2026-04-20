"""Identity calibration — build anchors + thresholds from reference sets.

Per operator 2026-04-20 revision: the biggest missing piece from the v0.1
skeleton was the identity calibration layer. This module provides it.

Outputs a gate spec (mu, tau) computed from intra-class distances on a
reference set. Optionally computes FAR/FRR proxy against a negative set.
"""
import os
import numpy as np
from PIL import Image


def calibrate_from_refs(ref_paths, embedder, method: str = "cosine", quantile: float = 0.99):
    """
    Build (mu, tau) from intra-class distances.

    method="cosine":
        mu is mean of unit-normalized embeddings
        tau is the `quantile`-th quantile of cosine distance to mu

    method="diag":
        mu is mean, sigma is per-dim std, tau is quantile of diag_norm_dist

    Returns a dict suitable for feeding into gate_cosine / gate_diag.
    """
    embs = []
    for p in ref_paths:
        img = Image.open(p).convert("RGB")
        embs.append(embedder(img))
    E = np.stack(embs, axis=0).astype(np.float32)
    mu = E.mean(axis=0)
    mu = mu / (np.linalg.norm(mu) + 1e-8)
    if method == "cosine":
        dists = 1.0 - (E @ mu)
        tau = float(np.quantile(dists, quantile))
        return {"metric": "cosine", "mu": mu, "tau": tau}
    elif method == "diag":
        sigma = E.std(axis=0) + 1e-6
        d = np.linalg.norm((E - mu) / sigma, axis=1)
        tau = float(np.quantile(d, quantile))
        return {"metric": "diag", "mu": mu, "sigma": sigma, "tau": tau}
    else:
        raise ValueError("Unknown method")


def far_frr_report(ref_paths, neg_paths, embedder, mu, tau):
    """FAR/FRR proxy: negative set should fail, refs should pass."""
    from .gates import cosine_dist
    pos = []
    for p in ref_paths:
        e = embedder(Image.open(p).convert("RGB"))
        pos.append(cosine_dist(e, mu))
    neg = []
    for p in neg_paths:
        e = embedder(Image.open(p).convert("RGB"))
        neg.append(cosine_dist(e, mu))
    pos = np.array(pos)
    neg = np.array(neg)
    FRR = float((pos > tau).mean())
    FAR = float((neg <= tau).mean())
    return {
        "FRR": FRR,
        "FAR": FAR,
        "pos_mean": float(pos.mean()),
        "neg_mean": float(neg.mean()),
    }
