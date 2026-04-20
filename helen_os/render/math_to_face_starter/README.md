# math_to_face_starter

**Runnable MVP scaffold** for the dual-canonical HELEN cloner (HELEN_REAL + HELEN_TWIN).

Operator-authored 2026-04-20 starter codebase. Numpy/PIL-based. All backends are stubs — swap them out to make the system real. Faster to iterate than the torch-based `../math_to_face.py` formal interface scaffold.

## Two layers in this package

| Path | Layer | Status |
|---|---|---|
| `helen_os/render/math_to_face.py` | Torch-based formal interface (`HelenIdentity`, `HelenDualIdentity`, `PhiScoreNet`, `math_to_face_helen()`, `paired_render()`) | DOCTRINE scaffold, `NotImplementedError` stubs |
| `helen_os/render/math_to_face_starter/` (this dir) | Numpy/PIL runnable MVP with concrete stubs that produce placeholder PIL images + pass/fail gate reports | RUNNABLE (stubs produce trivial outputs; swap in real backends to make real) |

Both point at the same architectural contract per `oracle_town/skills/video/math_to_face/SKILL.md`. The starter is what you fork/copy-paste into a standalone research repo to iterate quickly. The formal interface is what production HELEN lives against.

## Layout

```
math_to_face_starter/
├── README.md                    (this file)
├── requirements.txt             (torch, numpy, pydantic, Pillow, opencv-python)
├── src/
│   └── helen/
│       ├── __init__.py
│       ├── types.py             (MathObject, Latent, ImageOut, GateReport)
│       ├── mia_dual.py          (IdentityGateSpec, CanonicalProfile, MIAHelenDual)
│       ├── gates.py             (cosine, mahalanobis, identity_gate)
│       ├── phi_sde.py           (diffusion_schedule, phi_drift, refine_phi_sde, ScoreNetStub)
│       ├── models.py            (HStub, EStub, FaceEmbedderStub, GRealStub, GTwinStub)
│       └── pipeline_dual.py     (HelenDualSystem — one H, two Gs, two gates)
└── scripts/
    └── demo_generate_duo.py     (end-to-end demo: math → duo → gate reports)
```

## How to run (stubs)

```bash
cd helen_os/render/math_to_face_starter
python -m pip install -r requirements.txt
PYTHONPATH=src python scripts/demo_generate_duo.py
```

Produces `helen_real.png` and `helen_twin.png` (placeholder rects, labeled) in the current directory, plus stdout gate reports.

## What to swap to make it real (per operator's §3)

Replace in `src/helen/models.py`:

- `HStub` → trained Math→Latent encoder `H: M → R^512`
- `ScoreNetStub` (in `phi_sde.py`) → trained score network `s_θ(z, t) ≈ ∇_z log p_t(z)`
- `GRealStub` → photoreal generator (StyleGAN3 / SDXL / Flux wrapper)
- `GTwinStub` → anime/manga generator (anime diffusion / toon model)
- `FaceEmbedderStub` →
  - REAL: ArcFace (insightface `arcface_resnet50`)
  - TWIN: anime-face embed model OR CLIP-face similarity proxy

Replace in `scripts/demo_generate_duo.py` → gate anchors:
- Compute `μ_e, Σ_e, τ_id` for each profile from curated reference image sets
- Store in `MIAHelenDual.profiles["REAL"].gate` and `...["TWIN"].gate`

## "Cloned" pass/fail definition

A successful clone run is:
- REAL passes REAL gate
- TWIN passes TWIN gate
- (optional) round-trip `E(G(H(m))) ≈ H(m)` within ε

Everything else (styles, moods, outfits) is allowed to vary.

## Cross-references

- `oracle_town/skills/video/math_to_face/SKILL.md` §14 — dual-canonical doctrine
- `oracle_town/skills/video/math_to_face/references/DUO_POSTER_PROMPT.md` — canonical paired scene template
- `oracle_town/skills/video/math_to_face/references/HELEN_MATH_FACE_PROTOCOL.tex` — formal LaTeX protocol
