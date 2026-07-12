"""Phase 0 phi-SDE trace, deterministic Euler-Maruyama integration.

Phase 0 strict mode:
    qam_projection = "zero"  (Pi_QAM(z) = 0; identity rejected per HAL)
    noise_mode     = "ZERO_NOISE"
    gamma          = 0.0

Discretization:
    z_{t+dt} = z_t - dt * phi^{-t} * (z_t - Pi_QAM(z_t))

With Pi_QAM(z) = 0 this becomes:
    z_{t+dt} = z_t * (1 - dt * phi^{-t})

A monotone contraction with a strictly POSITIVE floor — not a contraction
to zero. Total drift mass int_0^inf phi^(-t) dt = 1/ln(phi) is finite, so
the product converges to c > 0 (c = 0.112408840028 for dt=0.1; continuous
limit e^(-1/ln phi) = 0.125169442295). An earlier version of this docstring
claimed contraction "toward 0"; corrected 2026-07-12 per Law 5 — see
experiments/helen_mvp_kernel/THEOREM_PHI_CONTRACTION_FLOOR_V1.md.
Phase 0 success criterion is hash determinism, not the contraction rate.
"""

from __future__ import annotations

import math
from typing import List, Tuple

PHI = (1.0 + math.sqrt(5.0)) / 2.0


def _qam_projection(z: List[float], mode: str) -> List[float]:
    if mode == "zero":
        return [0.0] * len(z)
    if mode == "identity":
        return list(z)
    raise ValueError(f"unknown qam_projection: {mode!r}")


def integrate(
    z0: List[float],
    T: float,
    dt: float,
    gamma: float,
    noise_seed: int,
    noise_mode: str,
    qam_projection: str,
) -> Tuple[List[float], int, List[float]]:
    """Run the Phase 0 phi-SDE trace.

    Returns (z_T, n_steps, trace_norms) where trace_norms[i] is the
    L2 norm of z at step i (used for the trace_hash fingerprint).
    """
    if noise_mode != "ZERO_NOISE":
        raise NotImplementedError(
            "Phase 0 strict: only ZERO_NOISE supported. SEEDED arrives in Phase 1."
        )
    if gamma != 0.0:
        # Phase 0 also pins gamma=0 to encode the no-noise regime
        raise ValueError(f"Phase 0 strict: gamma must be 0.0, got {gamma}")

    n_steps = int(round(T / dt))
    if n_steps < 1:
        raise ValueError("T/dt must give at least one step")

    z = list(z0)
    trace_norms: List[float] = []

    for step in range(n_steps):
        t = step * dt
        # Norm at start of step (for trace hash)
        norm = math.sqrt(sum(x * x for x in z))
        trace_norms.append(norm)

        phi_neg_t = PHI ** (-t)
        proj = _qam_projection(z, qam_projection)
        # z_new = z - dt * phi^{-t} * (z - proj)
        z = [z[i] - dt * phi_neg_t * (z[i] - proj[i]) for i in range(len(z))]

    # Final norm (post-loop)
    final_norm = math.sqrt(sum(x * x for x in z))
    trace_norms.append(final_norm)

    return z, n_steps, trace_norms


def z_T_summary(z_T: List[float], precision: int = 12) -> dict:
    """Return string-formatted z_T summary at fixed precision."""
    fmt = "{:.12f}"
    norm = math.sqrt(sum(x * x for x in z_T))
    first_8 = z_T[:8]
    return {
        "norm": fmt.format(norm),
        "first_8": [fmt.format(x) for x in first_8],
        "min": fmt.format(min(z_T)),
        "max": fmt.format(max(z_T)),
    }
