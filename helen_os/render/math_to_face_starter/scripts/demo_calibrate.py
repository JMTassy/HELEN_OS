"""Build REAL/TWIN anchors from reference image sets + optional FAR/FRR proxy.

Run from math_to_face_starter/:
    PYTHONPATH=src python scripts/demo_calibrate.py

Expects:
    refs/real/*.png     HELEN photoreal reference set
    refs/twin/*.png     HELEN anime/manga reference set
    refs/neg/*.png      (optional) other-person faces for negative test

Outputs (prints to stdout) the {mu, tau} dicts you feed into HelenDualCloner.
Wire to a YAML / JSON dump if you want to persist the calibrated gates.
"""
import glob

from helen.embedders import PixelHashEmbedder
from helen.calibrate_anchors import calibrate_from_refs, far_frr_report


def main() -> None:
    embed = PixelHashEmbedder(dim=256)

    real_refs = sorted(glob.glob("refs/real/*.png"))
    twin_refs = sorted(glob.glob("refs/twin/*.png"))
    neg_refs = sorted(glob.glob("refs/neg/*.png"))  # optional

    if not real_refs:
        print("WARNING: no refs/real/*.png found. Populate reference set first.")
    if not twin_refs:
        print("WARNING: no refs/twin/*.png found. Populate reference set first.")

    if real_refs:
        real = calibrate_from_refs(real_refs, embed, method="cosine", quantile=0.99)
        print(f"REAL gate anchor: mu[:5]={real['mu'][:5].tolist()}  tau={real['tau']:.4f}")
    else:
        real = None

    if twin_refs:
        twin = calibrate_from_refs(twin_refs, embed, method="cosine", quantile=0.99)
        print(f"TWIN gate anchor: mu[:5]={twin['mu'][:5].tolist()}  tau={twin['tau']:.4f}")
    else:
        twin = None

    if neg_refs and real:
        r = far_frr_report(real_refs, neg_refs, embed, real["mu"], real["tau"])
        print(f"REAL FAR/FRR: {r}")
    if neg_refs and twin:
        r = far_frr_report(twin_refs, neg_refs, embed, twin["mu"], twin["tau"])
        print(f"TWIN FAR/FRR: {r}")


if __name__ == "__main__":
    main()
