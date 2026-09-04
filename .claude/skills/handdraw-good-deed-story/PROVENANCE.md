# PROVENANCE — handdraw-good-deed-story

## Source
- Upstream: https://github.com/xiejunjie524/handdraw-story-video
- Pinned commit: `ec2f455e3b7bf2bf3dfbd5763c1d91d719b152aa`
- Fetched: local `git clone` (full tree at pin), not live-branch curl
- Recorded into SOT: `.claude/skills/handdraw-good-deed-story/`
- Also mirrored: `~/.claude/skills/handdraw-good-deed-story/`, `~/.agents/skills/handdraw-good-deed-story/`
- License: MIT (code only — generated images, fonts, GSAP, music keep their own terms)

## Audit verdict (clean, with named residual risk)

| Surface | Verdict |
|---|---|
| `scripts/make_lineart.py` | Pure local OpenCV. No network. |
| `scripts/build_story.py` | stdlib-only HTML builder. Loads GSAP from local vendored path. No CDN. |
| `scripts/one_click.py` | Talks only to endpoints you put in your own config JSON; API key from env var you name. No hardcoded hosts, no credential harvest. |
| `SKILL.md` | No hidden directives. |
| Residual risk | `npx hyperframes` executes third-party npm at render time — pin HyperFrames in a lockfile before production use. |

## Method (how we record third-party skills)
1. Pin upstream commit SHA.
2. Fetch file-by-file / clone at that SHA.
3. SHA-256 every file into this receipt.
4. Audit executable surface before first run.
5. Vendor into repo — never a live curl into `$CODEX_HOME/skills` as the only copy.

## SHA-256 inventory

| File | Bytes | SHA-256 |
|---|---:|---|
| `.gitignore` | 422 | `12b7ef7095489bd381816b1900886df150e4c3c9f485093b4936e452df1acd47` |
| `LICENSE` | 1090 | `a3724ad2441d926104ad5478b55a8a36cef6604291b7e7adec810d115e77e698` |
| `README.md` | 3907 | `80f18b1d8e76f59b64c7796cebe4c4635e3ba31070e6246416b942397bce2e8a` |
| `SKILL.md` | 2933 | `670858bca81d38abede28f22072feafd9b6c147ab64675ac5a069d6305b1710c` |
| `agents/openai.yaml` | 239 | `e021254ae256feea31de04a79ef3e2121ca399934b17e0e0156755e1857bc80a` |
| `assets/audio/.gitkeep` | 1 | `01ba4719c80b6fe911b091a7c05124b64eeece964e09c058ef8f9805daca546b` |
| `assets/images/.gitkeep` | 1 | `01ba4719c80b6fe911b091a7c05124b64eeece964e09c058ef8f9805daca546b` |
| `config.example.json` | 380 | `4d9aa26e54663db661fc11d64d73ede0c2c48a9b8b2e6350caf34e3e3babc656` |
| `docs/image-generation.md` | 2592 | `0541fdb35a66834498763a1eabe33020d51c4770208c066a9c4d463e892ede1e` |
| `docs/prompts.md` | 4636 | `6886fba997b91565b01e6990f98f42bdc42e21d106ecd3baeb7243db7a485964` |
| `docs/story-spec.md` | 2066 | `ad0c2ce9cb3aa3ac70a51e583be862d675b686f3f4ee63bf3de4c34eee40ed3d` |
| `docs/usage.md` | 4429 | `9d13430fe4a9ed61c1c2952a81f266bc60ca18263f2e4c7512ef26bce0d0c02b` |
| `examples/soy-milk-at-4am/README.md` | 570 | `3cfed3391a95b1c4e0cf8fdf039cb961d71d54389172531722f1af2959126bb5` |
| `examples/soy-milk-at-4am/preview.jpg` | 47185 | `1a6923dac10ba7d97a57c0e9ba817b097db95376085660a8817213591a91523c` |
| `examples/soy-milk-at-4am/story.json` | 2154 | `dde58bc373ae231e244b061608c5d2c94ff925750d011bcc34bf0ebf4c3e9e8d` |
| `requirements.txt` | 46 | `d1c3c7e8576b8f743e993d53a4f5f6bb25b7cd8b9a086ab675965ceec2043ac3` |
| `scripts/build_story.py` | 12183 | `a9ccf281e359ea03577f9f76ab73848f43bfcf2dc952bfcc0584cbf9dcedef0d` |
| `scripts/make_lineart.py` | 2406 | `7743fa47360b48c6fdac9727a7a509f1bd54eeee49f720f1e8780873af003e03` |
| `scripts/one_click.py` | 10502 | `e8c6e7d910de015e2e3b38d5b07b9d2b7fd2f0676ff0d6f088c1ce0eeea9b990` |
| `templates/story-template.json` | 1896 | `bfa253625bca1d53f96bc60857975b8931ccd6f622a890cc2cd8ab26fa99f127` |
| `templates/style-prompt.txt` | 1222 | `bf75387cc1dcff0228c0d371a03a5b435b16dfccac01a0b7d87e96d92b5187eb` |

## Gaps / notes
- Example full render assets not required for skill operation.
- `templates/style-prompt.txt` present (needed by `one_click.py`).
- Operator must supply own mother images + licensed BGM.
- HELEN adaptation project: `~/vault/jacobina_goblin_triple/` (non-sovereign generative artifact).

## HELEN doctrine note
This skill is a **Garden craft tool** (video pipeline). It does not touch Kernel admission.
Garden ADMIT ≠ Kernel ADMISSION.
