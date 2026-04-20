from .latent import StructuredLatent


class AdapterReal:
    """Shared StructuredLatent → REAL generator conditioning (still structured).

    v0.3: preserves spec; returns StructuredLatent so the generator can read
    z_id / z_control / z_style independently. Upgrade to learned affine/MLP
    adapters when the photoreal generator is wired.
    """
    def __call__(self, z: StructuredLatent) -> StructuredLatent:
        return z


class AdapterTwin:
    """Shared StructuredLatent → TWIN generator conditioning (still structured)."""
    def __call__(self, z: StructuredLatent) -> StructuredLatent:
        return z
