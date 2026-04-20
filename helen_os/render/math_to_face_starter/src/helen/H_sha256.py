import numpy as np
from .types import MathObject
from .latent import StructuredLatent
from .latent_spec import LatentSpec
from .hash_utils import stable_seed_from_payload, rng_from_seed


def _unit(x: np.ndarray) -> np.ndarray:
    return x / (np.linalg.norm(x) + 1e-8)


class H_SHA256:
    """
    Deterministic baseline encoder H: M → Z_id ⊕ Z_control ⊕ Z_style (+ Z_temporal).
    Replace later with a trained H, but keep the determinism contract
    (same payload → same latent across runs and machines).
    """
    def __init__(self, spec: LatentSpec):
        self.spec = spec

    def __call__(self, m: MathObject) -> StructuredLatent:
        seed = stable_seed_from_payload(m.payload)
        rng = rng_from_seed(seed)
        z_id = _unit(rng.normal(size=(self.spec.id_dim,)).astype(np.float32))
        z_control = _unit(rng.normal(size=(self.spec.control_dim,)).astype(np.float32))
        z_style = _unit(rng.normal(size=(self.spec.style_dim,)).astype(np.float32))
        z_temporal = (
            _unit(rng.normal(size=(self.spec.temporal_dim,)).astype(np.float32))
            if self.spec.temporal_dim
            else np.zeros((0,), np.float32)
        )
        return StructuredLatent(z_id, z_control, z_style, z_temporal, spec=self.spec)
