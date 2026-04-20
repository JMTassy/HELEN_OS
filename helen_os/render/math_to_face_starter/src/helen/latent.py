from dataclasses import dataclass
import numpy as np
from .latent_spec import LatentSpec

Array = np.ndarray


@dataclass(frozen=True)
class StructuredLatent:
    """Typed decomposition of the shared latent, carrying its schema."""
    z_id: Array
    z_control: Array
    z_style: Array
    z_temporal: Array
    spec: LatentSpec

    def as_vector(self) -> Array:
        return np.concatenate(
            [self.z_id, self.z_control, self.z_style, self.z_temporal], axis=0
        )

    @staticmethod
    def from_vector(z: Array, spec: LatentSpec) -> "StructuredLatent":
        assert z.shape[0] == spec.total_dim, (z.shape, spec)
        a = 0
        z_id = z[a:a + spec.id_dim]; a += spec.id_dim
        z_control = z[a:a + spec.control_dim]; a += spec.control_dim
        z_style = z[a:a + spec.style_dim]; a += spec.style_dim
        z_temporal = (
            z[a:a + spec.temporal_dim] if spec.temporal_dim
            else np.zeros((0,), dtype=z.dtype)
        )
        return StructuredLatent(z_id, z_control, z_style, z_temporal, spec=spec)
