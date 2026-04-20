"""HelenDualCloner — v0.3 spec-aware full "clone both" pipeline.

Changes from v0.2:
  - Takes a LatentSpec in the constructor (no hidden dimension assumptions)
  - Adapters return StructuredLatent (not raw vectors) so generators can read slices
  - Generators receive StructuredLatent directly and render latent-dependent images
  - use_phi_refine defaults to False (safe) — flip to True only with real projector/score

Takes pre-calibrated gate anchors (mu, tau) per profile. Use calibrate_anchors.py
upstream to compute them from reference sets.
"""
from dataclasses import dataclass
import numpy as np

from .types import MathObject, ImageOut, GateReport
from .latent_spec import LatentSpec
from .latent import StructuredLatent
from .H_sha256 import H_SHA256
from .phi_sde import refine_phi, ScoreNetStub
from .adapters import AdapterReal, AdapterTwin
from .generators_stub import GRealStub, GTwinStub
from .embedders import PixelHashEmbedder
from .gates import gate_cosine


@dataclass
class DualRun:
    z_shared: StructuredLatent
    z_refined: StructuredLatent
    img_real: ImageOut
    img_twin: ImageOut
    gate_real: GateReport
    gate_twin: GateReport

    @property
    def both_passed(self) -> bool:
        return bool(self.gate_real.passed and self.gate_twin.passed)


class HelenDualCloner:
    """One H shared. Safe-default φ-Refine. Two adapters. Two latent-dependent generators. Two calibrated gates."""

    def __init__(
        self,
        spec: LatentSpec,
        real_mu: np.ndarray,
        real_tau: float,
        twin_mu: np.ndarray,
        twin_tau: float,
    ):
        self.spec = spec
        self.H = H_SHA256(spec)
        self.score = ScoreNetStub()
        self.A_real = AdapterReal()
        self.A_twin = AdapterTwin()
        self.G_real = GRealStub()
        self.G_twin = GTwinStub()
        self.embed_real = PixelHashEmbedder(dim=256)
        self.embed_twin = PixelHashEmbedder(dim=256)
        self.real_mu = real_mu
        self.real_tau = real_tau
        self.twin_mu = twin_mu
        self.twin_tau = twin_tau

    def clone(self, m: MathObject, seed: int = 0, use_phi_refine: bool = False) -> DualRun:
        z = self.H(m)

        if use_phi_refine:
            z_vec = z.as_vector().astype(np.float32)
            z_vec = refine_phi(z_vec, self.score, steps=1, gamma=0.0, seed=seed).astype(np.float32)
            z_ref = StructuredLatent.from_vector(z_vec, spec=self.spec)
        else:
            z_ref = z

        # Adapters preserve structured form; generators read slices
        z_real = self.A_real(z_ref)
        z_twin = self.A_twin(z_ref)

        img_real = self.G_real(z_real)
        img_twin = self.G_twin(z_twin)

        # Embed + gate (pixel-dependent embedder + calibrated anchors)
        e_real = self.embed_real(img_real.pil)
        e_twin = self.embed_twin(img_twin.pil)
        gate_real = gate_cosine(e_real, self.real_mu, self.real_tau)
        gate_twin = gate_cosine(e_twin, self.twin_mu, self.twin_tau)

        return DualRun(
            z_shared=z,
            z_refined=z_ref,
            img_real=img_real,
            img_twin=img_twin,
            gate_real=gate_real,
            gate_twin=gate_twin,
        )
