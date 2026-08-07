---
title: HYPERFRAMES_AS_EXPRESSION_RENDERER_V0
status: 🟣 CLAIM
authority: false
claim_status: NO_CLAIM
canon_effect: false
ledger_effect: none
final: HOLD_FOR_OPERATOR
git_commit: no
date: 2026-07-22
governed_by: GARDEN_ONLINE_KERNEL_OFFLINE (deployment membrane)
related:
  - apps/goblin-warren/surfaces/goblin-warren-intro/
  - apps/goblin-warren/surfaces/her-changelog/
  - experiments/helen_voice/
  - project_garden_online_kernel_offline
---

# HYPERFRAMES_AS_EXPRESSION_RENDERER_V0

🟣 **CLAIM · NON_SOVEREIGN · NO_CLAIM.** A narrow integration contract. Authorizes nothing.
Placed in `docs/proposals/` (not `GOVERNANCE/`) by firewall discipline — Claude Code writes
proposals here; `GOVERNANCE/` is operator/sovereign ground.

## Core law

> HyperFrames is HELEN's **non-sovereign audiovisual renderer** — never an autonomous
> decision layer. It turns an approved expression snapshot into a deterministic, local,
> receipted film. It composes; it never marks.

The pipeline:

```
Kernel (offline) ─emits─▶ approved projection packet ─▶ HELEN production skill composes HTML
 ─▶ HyperFrames lint + check + deterministic local render ─▶ MP4 ─▶ verifier ─▶ PRODUCTION_RECEIPT
```

Everything HyperFrames touches carries `authority=false`. The renderer reads a projection;
it cannot write one.

## Why the fit is direct (grounded, not asserted)

This contract is written **from two live productions**, not from imagination:

| Instance | Evidence |
|---|---|
| `goblin-warren-intro` (`d368571`) | 10s 1080p, `check` PASS (contrast 12/12), deterministic seek-safe render, local FFmpeg, no per-render fee |
| `her-changelog` | 35.95s 1080×1080, `check` PASS (21/21 WCAG), cut to HER's real word-timings, local render |

HyperFrames properties that make it HELEN-shaped: plain HTML (not a proprietary timeline) ·
**deterministic render** (the framework itself bans `Date.now`/`Math.random`/network in
compositions — the same determinism law HELEN enforces on the spine) · local execution ·
Apache-2.0 · inspectable source artifacts · agent-native skills · clean separation between
expressive composition and authoritative kernel state.

## The Garden convergence (one artifact, two lives)

The **same HTML composition** is simultaneously a browser-visible expressive surface **and**
a deterministic video source:

```
living static page  +  replayable rendered film   ── with zero write authority
```

A static page has no server, cannot POST, cannot mark (`SURFACE CANNOT MARK`). The film is
its deterministic replay. Both bloom in the online Garden; neither reaches the offline Kernel.

## Integration contract

**Allowed inputs**
- an approved **projection packet** / expression snapshot (text, chosen assets, palette,
  timings) that the offline kernel or operator has released for expression.

**Forbidden authority paths** (fail-closed)
- no write-back to `town/ledger_v1.ndjson`, `helen_os/governance/**`, `helen_os/schemas/**`,
  `oracle_town/kernel/**`, `GOVERNANCE/**`, `mayor_*`;
- no marking, admission, canon mutation, or reducer invocation from any composition or build;
- no network fetch inside a composition (HyperFrames already forbids this).

**Required asset manifest** — every render declares its inputs with hashes:
`{ composition_html_sha256, assets:[{path, sha256}], audio_sha256?, fonts }`.

**Deterministic render requirements** — no wall-clock, no RNG, no network; identical inputs
→ identical output; `hyperframes check` must PASS (0 errors) before render.

**Source & output hashes** — record `composition_sha256`, each asset `sha256`, render params
(`quality, width, height, fps, duration`), and the output `mp4_sha256`.

**Caption requirement** — spoken content ships with a caption/transcript (accessibility, and
so the film is inspectable text, not opaque pixels). `check` WCAG contrast must pass.

**Local-first rendering** — render on-device (local Chrome + FFmpeg). No cloud render, no
per-render fee, no external dependency for the artifact to exist.

**No automatic publication** — rendering ≠ publishing. Putting a film on the public web is a
**separate, explicit operator act** (`hyperframes publish` / push to the Garden). The renderer
never publishes on its own.

## PRODUCTION_RECEIPT_V0 (the missing piece this closes)

The two existing productions passed `check` but **no production receipt was minted** — that
is the gap this contract fixes. Every future render emits:

```json
{
  "schema": "HELEN_PRODUCTION_RECEIPT_V0",
  "artifact": "her_changelog",
  "projection_packet_ref": "…",
  "composition_sha256": "…",
  "asset_manifest": [{"path": "…", "sha256": "…"}],
  "render_params": {"quality": "high", "width": 1080, "height": 1080, "fps": 30, "duration_s": 35.95},
  "check_verdict": {"ok": true, "contrast": "21/21", "errors": 0},
  "output_mp4_sha256": "…",
  "published": false,
  "authority": false, "canon_effect": false, "ledger_effect": "none"
}
```

A production receipt is a **witness that a film was produced deterministically from declared
inputs** — it is NOT an admission of the film's content. `render receipt ⊬ claim admitted`.

## Failure classes

`CHECK_FAILED` · `NONDETERMINISM_DETECTED` · `ASSET_HASH_MISMATCH` · `FORBIDDEN_AUTHORITY_PATH`
· `MISSING_CAPTION` · `RENDER_FAILED` · `CLOUD_RENDER_ATTEMPTED` · `AUTO_PUBLISH_ATTEMPTED`.
Any failure blocks the receipt; a blocked render is not a production.

## What this is not

Not an authorization to auto-publish, not a decision layer, not canon, not a build of the
production skill. `final: HOLD_FOR_OPERATOR`. The only governed mechanisms today are the two
verified renders; this note is their contract, written from their receipts.
