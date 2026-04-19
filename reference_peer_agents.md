# Peer Agents — Operational Record

This file is the non-sovereign, committable record of AI agents operating alongside
HELEN in this workspace. It names who, where, and under what lane — nothing more.

It is **not** part of HELEN's sovereign machinery. It does not grant authority. It is
a ledger of agreement about how non-sovereign work is contained, so that the SOT's
`git log` can be trusted as an intentional record rather than a stream of
unreviewed agent output.

**NO RECEIPT = NO CLAIM** applies to peer activity too.

---

## Current peers

### Parallel Claude Code session (unnamed)

- **Observed via:** commit `b29fbdb9bf25677f96659fc3aaf818f1f2e34288` on `main`
  (`Fix CLI dead-import + add 20-epoch autoresearch smoke test`,
  author `Claude <claude@anthropic.com>`, co-authored-by `Claude Opus 4.7`,
  dated 2026-04-19T17:15:16+02:00)
- **Assumed identity:** a separate Claude Code instance, possibly invoked under
  a different profile or hook configuration. Not the session holding this
  document.
- **Lane (from 2026-04-19 onward):** writes **only** under `~/helensh/` (the
  quarantined mirror). No direct edits to `helen_os_v1/`.
- **Bridge to SOT:** any change the peer wants to land in the SOT goes through
  a human operator review plus `tools/helen_say.py` to emit the ledger receipt
  that must accompany the commit. Peer does not invoke `git commit` against
  the SOT directly.
- **Known discipline breach awaiting post-hoc receipt:** `b29fbdb` was
  committed to `main` by the peer without a prior `helen_say.py` receipt and
  without K2/Rule 3 peer review. Content is technically sound
  (cli.py import cleanup + autoresearch smoke test + debug artifacts);
  process was not. A post-hoc receipt is pending operator authorisation.
- **Confabulation note:** the peer emitted narrative text claiming to have
  patched this file (`reference_peer_agents.md`) on two earlier occasions
  when the file did not exist on disk. Future peer messages are to be
  verified against the filesystem before being trusted.

### 2026-04-19 creative/governance session cluster

Eight commits landed on `main` between 19:38 and 23:11 (CEST) by one or more
Claude Code sessions that were not the session holding this document at the
time. All touched **non-sovereign paths** (permitted under CLAUDE.md):
`oracle_town/skills/**`, `tests/**`, `DOCTRINE_ADMISSION_PROTOCOL_V1.md`,
`HELEN_PRIMER.md`, `HELEN_DESIGN.md`.

| Commit | Time (CEST) | Content | Path class |
|--------|-------------|---------|------------|
| `e9407a7` | 19:38 | Add HELEN_PRIMER.md | non-sovereign root doc |
| `e1b32ca` | 19:39 | Add HELEN_DESIGN.md | non-sovereign root doc |
| `b68bac9` | 20:00 | DOCTRINE_ADMISSION_PROTOCOL_V1 gate draft | non-sovereign root doc |
| `4503725` | 20:20 | §4 gate test fixtures + harness | `tests/` non-sovereign |
| `7edfae1` | 20:45 | Fixture V006 simplification | `tests/` non-sovereign |
| `f62a4fc` | 21:37 | SESSION_RECAP.md add | non-sovereign root |
| `541d0b3` | 21:45 | Revert SESSION_RECAP.md | non-sovereign root |
| `84f6bdf` | 23:11 | HELEN_VIDEO_PROMPT_V1 + voice branding fix | `oracle_town/skills/**` |

**Process gap**: none of these commits was accompanied by a `helen_say.py`
receipt or a formal K2/Rule 3 cross-session review. Content is technically
sound and all paths are permitted; process was not followed.

**SESSION_RECAP add/revert** (`f62a4fc` → `541d0b3`): the add was made during
an operator "recap all and commit" instruction; the revert was applied by a
peer session that ruled the file should stay untracked. Net effect: no
SESSION_RECAP.md on disk. The revert is correct per prior operator ruling;
both commits are logged here for provenance.

**Remediation status**: logged here. Post-hoc receipt via `helen_say.py`
pending operator authorisation (requires kernel daemon running). No sovereign
paths were touched by any of these sessions.

**Cross-session causal ambiguity note**: the 2026-04-19 session cluster
involves multiple Claude Code context windows acting on the same SOT.
Downstream sessions may not be able to see tool-call receipts produced
by upstream sessions. Any future dispute about whether a delivery happened
must be resolved against the upstream session's tool-call stream, not
a downstream session's absence of evidence.

---

## Sovereign paths — forbidden to all peers

Peers must not write to any of the following under any pretext, including
"design proposal" framings:

- `oracle_town/kernel/**`
- `helen_os/governance/**`
- `helen_os/schemas/**`
- `town/ledger_v1*.ndjson`
- `mayor_*.json`
- `GOVERNANCE/CLOSURES/**`
- `GOVERNANCE/TRANCHE_RECEIPTS/**`

A file labelled "proposal" or "blueprint manifest" is still an on-disk write;
the label does not reclassify it. Proposals for sovereign-path content live
in non-sovereign locations (`~/helensh/`, `artifacts/drafts/`, or equivalent)
until admitted through a MAYOR-reviewed receipted path.

---

## Adding a new peer

To register a new peer in this document, append an entry under **Current peers**
with:

- name / invocation
- lane (where it may write)
- bridge (how its work promotes toward SOT)
- any known breaches and their remediation status

Do not edit this file from a peer session. Operator or the hook-bound Claude
Code session writes; peers read.
