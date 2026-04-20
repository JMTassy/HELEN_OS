"""Clone both (REAL + TWIN) from a math object + compose a duo poster (v0.3).

Run from math_to_face_starter/:
    PYTHONPATH=src python scripts/demo_duo_from_math.py

Produces helen_duo_poster.png + stdout gate reports.
Replace real_mu/real_tau/twin_mu/twin_tau with calibrate_anchors outputs.
"""
import numpy as np

from helen.types import MathObject
from helen.latent_spec import LatentSpec
from helen.pipeline_dual import HelenDualCloner
from helen.compose_duo_poster import compose_duo_poster


def main() -> None:
    spec = LatentSpec(id_dim=256, control_dim=128, style_dim=128, temporal_dim=0)

    # Placeholder anchors — replace with outputs from demo_calibrate.py on real refs
    real_mu = np.zeros((256,), np.float32)
    real_mu[0] = 1
    real_mu /= np.linalg.norm(real_mu) + 1e-8
    twin_mu = real_mu.copy()
    real_tau = 0.9
    twin_tau = 0.9

    cloner = HelenDualCloner(spec, real_mu, real_tau, twin_mu, twin_tau)

    m = MathObject(payload={
        "tag": "HELEN",
        "primes": [2, 3, 5, 7, 11, 13],
        "zeta_zeros": [14.1347, 21.0220],
        "fractal_dim": 1.618,
    })
    run = cloner.clone(m, seed=42, use_phi_refine=False)

    poster = compose_duo_poster(run.img_real.pil, run.img_twin.pil)
    poster.save("helen_duo_poster.png")

    print("Spec:", spec)
    print("z_id[:5]     :", run.z_shared.z_id[:5].tolist())
    print("z_control[:5]:", run.z_shared.z_control[:5].tolist())
    print("z_style[:5]  :", run.z_shared.z_style[:5].tolist())
    print()
    print("REAL gate:", run.gate_real.passed, run.gate_real.metrics, run.gate_real.reasons)
    print("TWIN gate:", run.gate_twin.passed, run.gate_twin.metrics, run.gate_twin.reasons)
    print("both_passed:", run.both_passed)
    print("Saved: helen_duo_poster.png")


if __name__ == "__main__":
    main()
