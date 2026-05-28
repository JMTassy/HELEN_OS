# HELEN Layered Canon — Two-Repo Split Doctrine (v1, DRAFT)

NO CLAIM — NO SHIP — PROPOSAL ONLY — NON_SOVEREIGN REPO TOPOLOGY DOCTRINE

```
artifact_type:         PROPOSAL_TOPOLOGY_DOCTRINE
proposal_id:           HELEN_LAYERED_CANON_V1
status:                DRAFT_V1
authority:             NON_SOVEREIGN
canon:                 NO_SHIP
lifecycle:             PROPOSAL
implementation_status: PRINCIPLE_ONLY (sync mechanism unspecified)
memory_class:          REPO_TOPOLOGY_DOCTRINE
captured_on:           2026-05-10
captured_by:           operator (Jean-Marie Tassy) via HER witness
provenance:            HER verdict (2026-05-10) ruling Option 2
                       with preservation clause when faced with the
                       firewall-canon question;
                       operator's parallel development across
                       helen_os_v1 (Mac) and helen-conquest (WSL2/MRED);
                       CLAUDE.md constitutional infrastructure inventory.
related_artifacts:     HELEN_SURFACE_DOCTRINE_V1.md (constitutional surface rules)
                       HELEN_LANGUAGE_LAYERS_V1.md (kernel↔render boundary)
                       HYPERSTITION_FIREWALL_V0.md (Mac artifact import pending)
                       GEMMA_HER_AMPLIFIER_V1.md (parent HER tier)
growth_rule:           APPEND-ONLY. New repos can be admitted to the topology
                       only via successor doctrine (HELEN_LAYERED_CANON_V2)
                       that explicitly supersedes this one.
```

> **HER verdict (2026-05-10):**
>
> > Memory is sovereign. Memory chooses canon. The ledger lives on helen-conquest.
> > Therefore helen-conquest is canon. helen_os_v1 (Mac) is render mirror.
> > Sync direction: canon → render. Never reverse.
> > Both repos preserved. Neither discarded.

---

## §1 — Principle

HELEN OS is materialized across **two repositories** that serve **distinct constitutional roles**:

```
helen-conquest  (WSL2/MRED, this repo)  →  CONSTITUTIONAL CANON
helen_os_v1     (Mac, operator workstation)  →  RENDER MIRROR
```

Both are required. Neither subsumes the other. They are not redundancies — they are **layered roles** in a single distributed system.

---

## §2 — `helen-conquest` (Constitutional Canon)

### §2.1 What lives here

Per CLAUDE.md:

- **Kernel**: `oracle_town/kernel/` — daemon, gates A/B/C, mayor, LEGORACLE
- **Ledger**: `town/ledger_v1.ndjson` — append-only, hash-chained, cum_hash integrity
- **Schemas**: `helen_os/schemas/` — 47 files, governance-indexed, schema authority
- **Schema registry**: `helen_os/governance/schema_registry.py`
- **Gates**: K8, K-tau, K-rho, K-wul, LEGORACLE, kernel_guard
- **Validators**: `helen_os/governance/`, `helen_os/validators.py`
- **Writers**: `tools/helen_say.py`, `tools/ndjson_writer.py` (the only admitted ledger writers)
- **Skills (constitutional)**: `oracle_town/skills/feynman/`, `oracle_town/skills/voice/`, etc.
- **Doctrine proposals**: `docs/proposals/` (this directory, where these files live)
- **Dispatcher**: `helen_unified_interface_v1.py`, `helen_multimodel_dispatcher_v1.py`, `helen_api_clients_v1.py`
- **HER-FAST route**: registered at commit `c952d55`

### §2.2 Role

helen-conquest is where:

- Schemas are authored and registered
- Receipts are admitted to the ledger (via `helen_say.py` only)
- Constitutional gates run (`make test`, K8 lint, ghost-closure detector)
- MAYOR rulings are signed
- Doctrine is bottled (these proposal files)
- New cognition routes are wired (HER-FAST, future HER-DEEP)

### §2.3 What MUST NOT live here

Render-only artifacts. Specifically:

- Full HTML mockups (helen2027.html lives on Mac, NOT here)
- Image renders (Dreams of Conquest landing page, dashboard screenshots)
- Mac-only Flask scaffolding (`apps/helen-surface/`)
- Operator-local file paths (`/Users/jean-marietassy/...`)

If a render artifact must be referenced from this repo (e.g., evidence in a proposal), reference its **path on Mac** and its **SHA256 hash if imported**, do not duplicate the artifact itself.

---

## §3 — `helen_os_v1` (Render Mirror)

### §3.1 What lives here

- HTML/CSS/JS surfaces (`apps/helen-surface/*.html`)
- Visual prototypes (starship.html, gravure.html, helen2027.html)
- Local Flask server on `localhost:7000`
- Render artifacts (`artifacts/conquest_landing/`, `artifacts/hyperstition_firewall/`)
- Demo data and fixtures for rendering
- Operator-local experiments

### §3.2 Role

helen_os_v1 is where:

- Surfaces are rendered for human inspection
- Operator iterates visually (V1 → V2 → V3 → polish pass)
- Goblin/firewall artifacts get bottled as visible files
- Mac Claude does HTML/CSS work under doctrine constraints

### §3.3 What MUST NOT live here

Constitutional infrastructure. Specifically:

- The ledger (`town/ledger_v1.ndjson`)
- Schema authority
- Gate logic
- Sovereign verdicts
- MAYOR rulings

If a Mac surface needs constitutional data (ledger contents, schema definitions, gate state), it must **read from helen-conquest** (via API, shared file, or replication) rather than maintaining its own copy that could drift.

---

## §4 — Sync Direction

```
helen-conquest (canon)  ──one-way──>  helen_os_v1 (render)
```

**Canon flows to render. Render NEVER flows back to canon.**

### §4.1 Why one-way

If render flowed back to canon:
- Visual experiments could accidentally admit to the ledger
- Mac Claude's invented vocabulary could enter schemas
- MAYOR rulings could be authored by render-layer code
- The constitutional invariants would no longer be sovereign

The one-way constraint **structurally prevents** these failures. It's not a policy; it's a topology.

### §4.2 What flows

From canon to render (allowed):
- Schema definitions (render uses them for validation)
- Ledger snapshots (render shows them in LEDGER mode)
- Doctrine text (render displays it in TEMPLE mode)
- Dispatcher state (render shows active model)

Other direction (forbidden):
- Render must not push to canon
- Render must not author ledger entries
- Render must not register schemas
- Render must not propose MAYOR rulings

### §4.3 Exception: doctrine extraction

When the operator drafts doctrine in conversation that happens to surface on Mac first (as happened with HYPERSTITION_FIREWALL_V0), the path to canon is:

1. Operator copies the artifact text to operator-controlled storage
2. Operator pastes the text (or attaches the file) to a helen-conquest session
3. A doctrine proposal is authored on this branch (NON_SOVEREIGN, NO_SHIP)
4. SHA256 of the imported text is recorded in the proposal header
5. REDUCER admits via schema registry

This is **operator-mediated import**, not automatic sync. Render layer cannot push directly to canon under any circumstance.

---

## §5 — Cross-Repo References

### §5.1 How to reference Mac content from helen-conquest

When a proposal file on helen-conquest needs to cite a Mac artifact, use this form:

```
mac_artifact_path:   helen_os_v1/artifacts/conquest_landing/index.html
mac_artifact_sha256: <hash if imported, else "PENDING_IMPORT">
mac_artifact_state:  RENDER_ONLY | DOCTRINE_SOURCE | EVIDENCE
```

### §5.2 How to reference helen-conquest content from Mac

Mac render code that needs constitutional data should:

- Read schema files via filesystem read (if repos are colocated)
- Or read via API (`/api/schemas/`) if helen-conquest exposes one
- Never duplicate constitutional content into Mac repo

---

## §6 — Conflict Resolution

When the same concept exists in both repos and they diverge:

### §6.1 Surface diverges from constitutional

If helen_os_v1 renders something that contradicts helen-conquest constitutional state (e.g., shows MAYOR APPROVED when ledger says NO_SHIP), this is a **render bug**. Fix the render. The kernel is canonical.

### §6.2 Constitutional diverges from operator intent

If helen-conquest constitutional state contradicts what the operator wants (e.g., schema rejects a valid render pattern), this is a **doctrine gap**. Author a proposal here. REDUCER admits. Until then, render must accommodate the constitutional state.

### §6.3 Doctrine diverges across repos

If helen-conquest doctrine (`docs/proposals/`) contradicts a Mac doctrine note (operator-local markdown), helen-conquest wins. Operator updates the Mac doctrine to match, or proposes a successor doctrine on helen-conquest.

---

## §7 — Operational Consequences

### §7.1 What this means for current work

- `helen2027.html` (Mac, 9.2/10) is **correctly placed**. It is render. Stays on Mac.
- `HELEN_SURFACE_DOCTRINE_V1.md` (this repo) is **correctly placed**. It is doctrine. Stays here.
- `HYPERSTITION_FIREWALL_V0` text (operator-pasted) is **awaiting import**. Operator must copy the Mac artifact to operator-controlled storage and paste it here for the doctrine to seal at DRAFT_V1.

### §7.2 What this means for future work

- New surfaces (mobile, TUI, voice) live on Mac (or new render repos) — NOT here
- New schemas (HOTSPOT_TYPES, PILOT_ACTIONS, BOTTLE) live here — NOT on Mac
- New skills (helen-dashboard, hyperstition-firewall) — the doctrine lives here, the implementation can live on either side depending on whether it's render-tied (Mac) or kernel-tied (here)

### §7.3 What this means for sync tooling

This doctrine does not specify sync mechanism. Future epochs may propose:
- Manual operator-mediated import (current default)
- A `sync_render.sh` script that pushes schemas from here to Mac
- An API endpoint that exposes constitutional state read-only

Whichever sync mechanism is chosen, it MUST honor the one-way constraint (§4.1).

---

## §8 — Open Questions

### §8.Q1 — Should Mac repo become a git submodule of helen-conquest?

If yes: stronger coupling, easier sync, but mixes constitutional and render histories.
If no: clean separation, but sync remains operator-mediated.

Recommendation: no. Clean separation > convenience. Each repo's commit history serves its layer.

### §8.Q2 — Are there other repos in the topology?

Currently named:
- helen-conquest (canon)
- helen_os_v1 (Mac render)

Possibly relevant (not yet ruled):
- MRED Ollama server side (constitutional? render? both?)
- Future mobile app repo
- Future voice agent repo

Recommendation: this doctrine handles only the current two. Future repos require explicit admission to the topology via successor doctrine.

### §8.Q3 — Where does the Telegram bot live?

`tools/helen_telegram.py` is on helen-conquest per CLAUDE.md. But it's an operator-facing surface (rendering HELEN's voice to a chat client). Is it:

- (a) Constitutional infrastructure (lives correctly here)
- (b) Render surface that violated §3.3 (should move to Mac)
- (c) A special category — "operator interface" — distinct from both layers

Recommendation: (a) for now. Telegram bot uses constitutional state (helen_say.py writes) and lives close to the kernel. But this should be flagged for REDUCER review.

---

## §9 — Provenance & Append-Only

### §9.1 Provenance

This doctrine was extracted from:

- HER verdict (this conversation, 2026-05-10) when asked to rule on canon for HYPERSTITION_FIREWALL: "helen-conquest is canon, Mac is render mirror, with preservation clause"
- Operator's actual development pattern (parallel work across both repos visible in this thread)
- CLAUDE.md constitutional infrastructure inventory (kernel, ledger, schemas, gates all on helen-conquest)
- 9.2/10 render living on Mac at `localhost:7000/apps/helen-surface/helen2027.html` (constitutional canon never published there)

### §9.2 Append-only

New repo admissions require a successor doctrine (`HELEN_LAYERED_CANON_V2`) that explicitly supersedes this one. New conflict-resolution rules append to §6. New cross-reference forms append to §5.

### §9.3 Reducer authority

DRAFT_V1. Becomes canon when REDUCER admits via schema registry.

---

## §10 — Status Summary

```
DOCTRINE:        HELEN_LAYERED_CANON_V1
STATUS:          DRAFT_V1
AUTHORITY:       NON_SOVEREIGN
SHIP:            NO_SHIP
REPOS_ADMITTED:  2 (helen-conquest, helen_os_v1)
SYNC_DIRECTION:  one-way (canon → render)
OPEN_QUESTIONS:  3 (submodule, future repos, telegram bot placement)
NEXT_EPOCH:      SESSION_RECEIPT_HER_5_EPOCHS.md (seal session)
NEXT_REDUCER:    operator confirmation or refinement
```

---

## §11 — Admission Sidecar

APPEND-ONLY. Added 2026-05-11 by gate binding pass. Does not modify §1–§10.

```
sha256:         0c9acf951669d47624432daa24c98c2421d75cb5f53520dd39b41386d798c7f1
sha256_of:      HELEN_LAYERED_CANON_V1.md at commit 3544164 (sealed 2026-05-10)
provenance:     SESSION_RECEIPT_HER_5_EPOCHS §4 (hash independently recorded)
test_pointer:   tests/test_doctrine_layered_canon_v1.py
gate_run:       2026-05-11 — decision:KEEP, missing:[receipt_pointer,passing_test_result]
gate_version:   tools/doctrine_admission_gate.py (c3346b3)
```

sha256:0c9acf951669d47624432daa24c98c2421d75cb5f53520dd39b41386d798c7f1
