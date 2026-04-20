from dataclasses import dataclass


@dataclass(frozen=True)
class LatentSpec:
    """Schema-bearing latent-dimension specification.

    Passed through H, adapters, pipeline, and inverters so no module has to
    hardcode dimensions.
    """
    id_dim: int = 256
    control_dim: int = 128
    style_dim: int = 128
    temporal_dim: int = 0

    @property
    def total_dim(self) -> int:
        return self.id_dim + self.control_dim + self.style_dim + self.temporal_dim
