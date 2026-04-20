import numpy as np
from .types import GateReport


def cosine_dist(a: np.ndarray, b: np.ndarray) -> float:
    a = a / (np.linalg.norm(a) + 1e-8)
    b = b / (np.linalg.norm(b) + 1e-8)
    return 1.0 - float(np.dot(a, b))


def diag_norm_dist(x: np.ndarray, mu: np.ndarray, sigma: np.ndarray) -> float:
    return float(np.linalg.norm((x - mu) / (sigma + 1e-8)))


def gate_cosine(emb: np.ndarray, mu: np.ndarray, tau: float) -> GateReport:
    d = cosine_dist(emb, mu)
    ok = d <= tau
    reasons = [] if ok else [f"cosine_dist={d:.4f} > tau={tau:.4f}"]
    return GateReport(ok, {"cosine_dist": d}, reasons)


def gate_diag(emb: np.ndarray, mu: np.ndarray, sigma: np.ndarray, tau: float) -> GateReport:
    d = diag_norm_dist(emb, mu, sigma)
    ok = d <= tau
    reasons = [] if ok else [f"diag_norm_dist={d:.4f} > tau={tau:.4f}"]
    return GateReport(ok, {"diag_norm_dist": d}, reasons)
