"""Safe-default refinement.

v0.3: defaults are identity (no noise, no drift, no score). Flip to stochastic
only with a non-trivial Π_QAM or a trained score network, OR explicitly pass
use_phi_refine=True with non-zero gamma and steps in the pipeline.
"""
import numpy as np


def qam_projection(z: np.ndarray) -> np.ndarray:
    """Placeholder Π_QAM. Replace with real QAM projector."""
    return z


def phi_drift(z: np.ndarray, t: float) -> np.ndarray:
    # Kept for reference; not called by safe-default refine_phi.
    from math import sqrt
    PHI = (1.0 + 5.0 ** 0.5) / 2.0
    return -(PHI ** (-t)) * (z - qam_projection(z))


def diffusion_schedule(t: float, gamma: float) -> float:
    # Kept for reference.
    from math import sqrt
    PHI = (1.0 + 5.0 ** 0.5) / 2.0
    return gamma * sqrt(max(0.0, 1.0 - (PHI ** (-2.0 * t))))


class ScoreNetStub:
    """Trivial score — replace with trained s_θ(z, t) ≈ ∇_z log p_t(z)."""
    def __call__(self, z: np.ndarray, t: float) -> np.ndarray:
        return np.zeros_like(z)


def refine_phi(
    z0: np.ndarray,
    score_net,
    steps: int = 1,
    gamma: float = 0.0,
    seed: int = 0,
) -> np.ndarray:
    """Safe default: identity. No stochastic drift while projector/score are stubs.

    To enable real refinement: pass non-zero gamma + steps > 1 AND ensure
    qam_projection and score_net are real implementations.
    """
    return z0.copy()
