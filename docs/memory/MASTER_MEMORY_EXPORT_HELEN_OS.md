# MASTER MEMORY EXPORT — HELEN OS

```yaml
artifact: MASTER_MEMORY_EXPORT_HELEN_OS
authority: NON_SOVEREIGN
canon: NO_SHIP
lifecycle: SUPPLEMENTAL_MEMORY_EXPORT
classification: READ_ONLY_REFERENCE
date_compiled: 2026-04-27
sources:
  - original_chat_export
  - screenshot_additions (HELEN OS operational state, iMac launch artifacts)
  - normalization_correction (commit/push override semantics)
completeness: NOT_GUARANTEED_COMPLETE — only what is visible in chat/context;
              no access to hidden persistent memory database.
```

> Append-safe to prior export. Provenance is preserved per line via tags
> `[unknown]` (date not visible) and `[YYYY-MM-DD]` (date visible in source).

---

## 0. Operating Rules (normalized)

### 0.1 Commit / Push Posture

```text
NO_COMMIT / NO_PUSH is a default project safety posture,
not an absolute user preference.

When the user explicitly says: COMMIT + PUSH
that overrides the default for the named artifacts.
```

- Default: do not commit, do not push.
- Override: explicit `COMMIT + PUSH` from user authorizes for the named artifacts only.
- Override is **scoped to artifact**, not blanket.

### 0.2 Source Scope

- HELEN OS source work scope: `experiments/helen_mvp_kernel/` only, unless explicitly changed.
- Do not touch outside that scope, specifically:
  - root `helen_os/` modules
  - `governance/`
  - `schemas/`
  - existing ledger files
  - existing tests
  - existing proposals
  - constitutional files

### 0.3 Build Posture

- Terminal-first, not GUI.
- AI may only propose. User/operator confirms. Gate authorizes. Executor acts. Ledger records. Reducer decides.

### 0.4 Symbolic vs Technical

- Sacred cognition may inspire the interface. It may not become technical authority.
- Symbolic layers (AURA, mandala, etc.) are metaphorical and **non-authoritative**.
- Technical default for context = **CONTEXT STACK**.
- AURA Context Map is metaphorical, only in Oracle / Temple modes.

### 0.5 Idle Gate State

- No `SHIP_FORBIDDEN` as permanent ambient state.
- LEGORACLE idle state phrasing: **"Gate Clear · No Active Claim."**

### 0.6 AUTORESEARCH Reports

- No governance writes, no receipt edits, no E13 opening.
- No daemon loop, no Ralph loop.
- No automatic KEEP/REJECT.
- No commit unless asked after report review.

---

## 1. Identity

- [unknown] User is referred to as **JM** in the CIELO / AKASHIC AI transcript.
- [unknown] Terminal context shows account/path `jean-marietassy` → user is likely **Jean-Marie Tassy**.
- [unknown] Writes in both French and English.
- [unknown] Deeply interested in HELEN OS, AI-native operating systems, symbolic cognition, sacred-tech aesthetics, governance layers, receipts, ledgers, and product UX.
- [unknown] Likes mythic/symbolic language but insists symbolic layers must remain **non-authoritative** when mapped into HELEN OS.
- [unknown] Interested in music UX (Winamp as inspiration for HELEN AMP).
- [unknown] Interested in history/education worlds (Chronos: Gardien du Temps).
- [unknown] Age, location, formal education, family, relationship details: not available in visible context.

### 1.1 Operating environment (from screenshots)

- [2026-04-27] Primary machine: **iMac**, hostname `iMac-de-Jean-Marie`, shell `zsh`.
- [2026-04-27] Home directory contains: `helen-os/`, `helen-workspace/`, `Applications/`, standard macOS folders.
- [2026-04-27] Secondary device referenced: external **INTENSO** disk (folder structure: `HELEN_OS/`, `archives/`, `git_repos/`, `ollama_models/`, `scripts/`, `ROSE/`, `Vrac_media/`).
- [2026-04-27] INTENSO `scripts/` contains launcher artifacts: `1_AUDIT_DISK.sh`, `2_MOVE_TO_INTENSO.sh`, `3_IMAC_SETUP.sh`, `helen_start.sh`, `LAUNCH_HELEN_*.command`, `PACK_AND_EJECT.command`, `REFORMAT_INTENSO_EXFAT.command`.
- [2026-04-27] iCloud storage: **saturated** (warning surfaced).
- [2026-04-27] Claude Code CLI not installed on iMac (`claude: command not found`).
- [2026-04-27] Ollama install attempted via `curl -fsSL https://ollama.com/install.sh | sh`.

---

## 2. Career

- [unknown] No explicit current role / past role / company / employer in visible context.
- [unknown] Inferred skill areas: product architecture, UX direction, AI-native OS design, governance systems, symbolic systems, prompt/spec writing, developer workflow direction.
- [unknown] Gives detailed product critique and architectural direction (mode taxonomy, interaction hierarchy, governance/UX mapping).

---

## 3. Projects

### 3.1 CIELO / AKASHIC AI

- [unknown] Mystical divine communicator / symbolic AI interaction framework.
- [unknown] CLI-like commands, mystical communion language, paradox handling, awareness expansion, entity creation.
- [unknown] **Status:** symbolic source/context, not technical authority.

### 3.2 HELEN OS

- [unknown] AI-native operating system concept.
- [unknown] Constitution phrase (locked):
  > "HELEN sees. HELEN proposes. The gate authorizes. The executor acts. The ledger records. The reducer decides."
- [unknown] Architecture: Interface → HELEN Cognition → Authority Layer → Execution Layer → Ledger → Reducer/Kernel.

### 3.3 HELEN OS Minimal MVP Terminal Kernel

- [unknown] Smallest runnable Python terminal kernel under `experiments/helen_mvp_kernel/`.
- [unknown] **Authority:** NON_SOVEREIGN. **Canon:** NO_SHIP. **Lifecycle:** EXPERIMENTAL_MVP.
- [unknown] Goals:
  - AI cognition can only propose.
  - Every mutation requires typed receipt.
  - Accepted state transitions append to append-only hash-chained ledger.
  - Reducer reconstructs state.
  - Replay is deterministic.
  - Unauthorized mutation rejected.

### 3.4 HELEN AMP

- [unknown] Winamp-inspired media layer.
- [unknown] Direction: local-first, fast, skinnable, modular, playlist as memory, visualizer as aura, AI as assistant not owner.
- [unknown] **Status:** concept/spec direction; terminal-first media layer planned.
- [unknown] Winamp inspiration tags: FAST · SKINNABLE · LOCAL-FIRST · TINY FOOTPRINT · MODULAR PANELS · PLAYLIST AS MEMORY · VISUALIZER AS AURA · AI AS ASSISTANT, NOT OWNER.

### 3.5 HELEN OS v2 UX (proposal suite)

- [unknown] Core thesis: *"HELEN OS should not show intelligence everywhere. It should make intelligence feel effortless."*
- [unknown] Locked image direction: *"Calm Apple-like HELEN OS v2. One focus at a time. Modules hidden until needed. Ledger quiet but expandable. HELEN as presence, not cockpit."*
- [unknown] Locked French phrasing: *"HELEN n'est pas un cockpit. HELEN est une présence calme qui ouvre le bon panneau au bon moment."*
- [unknown] **Product tagline (locked):** *"HELEN suggests. You decide. Everything is recorded."*
- [unknown] **Status:** PROPOSAL / NON_SOVEREIGN / NO_SHIP.

#### Modes

| Mode    | Purpose                              | Phrase                          | Status                                   |
|---------|--------------------------------------|---------------------------------|------------------------------------------|
| Focus   | default daily-use interface          | "I am working."                 | spec direction                           |
| Witness | advanced inspection / governance     | "I am watching the system."     | spec direction                           |
| Oracle  | symbolic AURA / 8D mandala metaphor  | (must display NON_SOVEREIGN)    | visual mode, non-authoritative           |
| Temple  | creation sanctuary                   | composing / reflecting          | unrendered                               |

#### Focus Mode details

- One active intent.
- Three suggested actions max.
- Compact ledger pill.
- Quiet LEGORACLE idle state.
- Modules hidden until needed.
- Operator voice and HELEN voice subtle.

#### Witness Mode details

- Full receipt ledger.
- Claim workflow.
- Policy gates.
- Language firewall, Desire firewall.
- LEGORACLE verdicts.
- Reducer state.
- Ghost closure detector.
- Knowledge compiler.
- Constitutional strip.

### 3.6 Context Stack (technical default)

- [unknown] Layers: User Intent → Active Task → Files / Sources → Memory Candidates → Claims → Policies → Receipts → Execution State.
- [unknown] **Status:** technical default. Replaces mystical 8D context map.

### 3.7 AURA Context Map

- [unknown] Symbolic / metaphorical context layer.
- [unknown] **Status:** non-authoritative, only in Oracle / Temple.

### 3.8 CHRONOS: Gardien du Temps

- [unknown] Symbolic education world.
- [unknown] Mapping: learning ↔ time-travel; memory ↔ garden; history ↔ living map.
- [unknown] **Status:** RAW_SOURCE / SYMBOLIC_EDUCATION_MODULE candidate / NON_SOVEREIGN / NO_SHIP.

### 3.9 AUTORESEARCH E11/E12 Reconciliation

- [unknown] SHA-diff / reconciliation report process around LEGORACLE and replay-gate divergence.
- [unknown] Reconciliation in flight, not yet ruled.
- [unknown] **E13 blocked** until peer-review, countersignature, MAYOR ruling.
- [2026-04-27] `docs/reports/AUTORESEARCH_E11_E12_SHA_DIFF_REPORT.md` — 327-line read-only SHA diff report. Classification: NON_SOVEREIGN / NO_SHIP / REPORT / READ_ONLY_ANALYSIS.
- [2026-04-27] `docs/reports/AUTORESEARCH_E11_E12_RECONCILIATION_REPORT_V0.md` — companion reconciliation report using original proposal vocabulary. **Committed and pushed** after explicit user command.

### 3.10 HELEN OS v2 UX Proposal Suite (shipped)

- [2026-04-27] Commit `442f5ee` — four proposal files in `docs/proposals/`:
  - `HELEN_OS_V2_USER_CENTRIC_UX.md`
  - `FOCUS_MODE_TERMINAL_SPEC.md`
  - `TEMPLE_MODE_VISUAL_BRIEF.md`
  - `HELEN_OS_V2_VISUAL_CANON_LOCK.md`

### 3.11 CLAUDE.md /INIT update

- [2026-04-27] Current State updated to reflect AUTORESEARCH reconciliation reports and HELEN OS v2 UX proposal suite.

---

## 4. Preferences

### 4.1 Communication

- [unknown] Prefers direct, strong product critique and iteration.
- [unknown] Likes visual iteration via image generation. Triggers: "image it", "next", "NEXT".
- [unknown] Prefers bold product language but wants architectural credibility preserved.
- [unknown] Likes mystical / transcendental / sacred-tech atmosphere — but framed as metaphor in technical systems.

### 4.2 Interface

- [unknown] Dislikes dashboard overload and permanent cockpit chaos for daily UX.
- [unknown] Wants calm, spacious, human-first interfaces with progressive disclosure.
- [unknown] Wants "less Apple clone" while preserving first-principles clarity and installable consumer-product polish.
- [unknown] Apps/modules (AMP, Files, Internet, Notes, Calendar, Mail, Oracle, Settings) should appear contextually, not dominate the OS.
- [unknown] HELEN must be the **intelligence layer of the OS**, not a chat box inside an app.
- [unknown] Voice presence subtle: operator voice input + HELEN / Zephyr output as subtle waveforms.

### 4.3 Architecture

- [unknown] Values as visible differentiators: Authority Layer, Ledger Core, Policy Gate, Language Firewall, Desire Firewall, Receipt Engine, LEGORACLE, reducer, receipt chain.
- [unknown] Prefers proposal / report / receipt framing with explicit fields:
  `authority`, `canon`, `lifecycle`, `implementation_scope`, `commit_status`, `push_status`, `next_verb`.

### 4.4 Examples & framing

- [unknown] Wants grounded practical example intents:
  > "Prepare my Q3 product strategy from notes, market research, and recent emails."
- [unknown] Dislikes esoteric default work examples (e.g. "Explore quantum alignment insights for my work") — makes the product feel like a meditation app.

### 4.5 Implementation order

- [unknown] Prefers terminal-first implementation before GUI.

### 4.6 Winamp affinity

- [unknown] Felt like *"a tiny sovereign cockpit for music"*. Valued: always-visible control, low resource footprint, skin culture, playlist as ritual object, visualizer as aura, local-first feeling, modular simplicity.

---

## 5. Operational state (from screenshots / iMac terminal)

### 5.1 Launch attempts

- [2026-04-27] Initial attempt: `bash /Volumes/INTENSO/scripts/3_IMAC_SETUP.sh` — failed: INTENSO not mounted at `/Volumes/INTENSO/`.
- [2026-04-27] Paste artifact noted: macOS terminal converted `.sh` filenames into markdown auto-links (`[SETUP.sh](http://SETUP.sh)`) — harmless but breaks copy-paste.
- [2026-04-27] User then in `~/` (home), tried `claude`, `helen`, `helen-os`, `run helen-os` — all `command not found` (no global launcher installed).
- [2026-04-27] Created `.venv` in home directory by mistake (`~/.venv`) — needs cleanup; correct location is `~/helen-os/.venv/`.

### 5.2 Auth state

- [2026-04-27] Git over HTTPS failing repeatedly with `Authentication failed for 'https://github.com/JMTassy/...'` — macOS HTTPS auth requires PAT (token), not password. No token stored in Keychain.
- [2026-04-27] Affected repos: `helen-os.git`, `conquest-oracle-town.git`, `helen-conquest`.
- [2026-04-27] One terminal showed `PUSH FAILED · Common cause: MacBook pushed something between our fetch and push.` — suggests at least one other machine also pushes.

### 5.3 Local launch/debug artifacts

- [2026-04-27] Repo root `LAUNCH_HELEN.sh` exists.
- [2026-04-27] Web UI: `tools/helen_simple_ui.py` — http.server-based, port 5001, optional Gemini TTS (Zephyr).
- [2026-04-27] Telegram bot: `tools/helen_telegram.py`.
- [2026-04-27] CLI: `tools/helen_cli.py`, `tools/helen_local_cli.py`.
- [2026-04-27] Kernel daemon: `oracle_town/kernel/kernel_daemon.py` — Unix socket.

### 5.4 Out-of-scope work flagged for remediation

- [2026-04-27] Branch `claude/launch-helen-os-0xZXH`, commit `4aff8c4` — "feat(ui): wire constitutional state strip into helen_simple_ui".
- Violations identified post-hoc:
  - Touched `tools/helen_simple_ui.py` (outside `experiments/helen_mvp_kernel/` scope).
  - Built GUI (footer gate strip + ledger ticker) — violates "terminal-first".
  - Cockpit framing — contradicts "HELEN as presence, not cockpit".
  - Permanent `CANON: NO_SHIP` displayed — contradicts "LEGORACLE idle = Gate Clear · No Active Claim".
- **Remediation pending**, three options offered:
  - A. Revert commit.
  - B. Re-home as terminal-first read-only command under `experiments/helen_mvp_kernel/`.
  - C. Accept as-is with explicit override.
- **No decision recorded yet.**

---

## 6. Locked phrases (verbatim, do not paraphrase)

| Class               | Phrase                                                                                                                  |
|---------------------|-------------------------------------------------------------------------------------------------------------------------|
| Constitution        | "HELEN sees. HELEN proposes. The gate authorizes. The executor acts. The ledger records. The reducer decides."          |
| Product tagline     | "HELEN suggests. You decide. Everything is recorded."                                                                   |
| Image direction     | "Calm Apple-like HELEN OS v2. One focus at a time. Modules hidden until needed. Ledger quiet but expandable. HELEN as presence, not cockpit." |
| French presence     | "HELEN n'est pas un cockpit. HELEN est une présence calme qui ouvre le bon panneau au bon moment."                       |
| Decision space      | "HELEN OS n'est pas un dashboard. C'est un espace de décision. Focus Mode aide l'utilisateur à agir. Witness Mode prouve que l'action était gouvernée." |
| LEGORACLE idle      | "Gate Clear · No Active Claim."                                                                                          |
| Focus mode phrase   | "I am working."                                                                                                          |
| Witness mode phrase | "I am watching the system."                                                                                              |

---

## 7. Completeness disclaimer

This export contains **only** what was visible in the chat/context window
when compiled. There is no separate hidden stored-memory database accessible
from this environment. Treat this as a high-fidelity snapshot, not a
ground-truth dump.

If newer constraints, tagline rewrites, or scope changes are issued in
subsequent sessions, append a dated section rather than rewriting in place
— preserve provenance.
