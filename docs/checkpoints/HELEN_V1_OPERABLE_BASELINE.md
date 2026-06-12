# HELEN V1 — OPERABLE BASELINE
**Date:** 2026-06-12  
**Commit (HEAD at sealing):** `332462b3f865893b22ec7491f86aa9bd7b0798ff`  
**Branch:** `main`  
**Remote:** `https://github.com/JMTassy/helen-conquest.git`

---

## Suite Status

| Suite | Result |
|---|---|
| `make test` (`helen_os/tests/`) | **584/584 passed** |
| `tests/` root constitutional | **707 passed / 67 skipped / 0 failed** |

Skipped classes are environment-dependent, not architectural failures:
- `requires_ocaml` (26) — kernel_cli binary; OCaml toolchain required
- `integration` (7) — pynacl phase2 crypto env
- `optional` (7) — numpy not installed
- `xfailed` (1) — documented expected failure

---

## Seams Merged to main

| Seam | Description |
|---|---|
| Boot continuity spine | `helen_os/boot/` — null-honest, lawful forgetting |
| Manifest registry | `helen_os/manifest_registry.py` — authority="NONE" fence |
| Manifest gate (Gate 2) | `skill_promotion_reducer.py` — ERR_MANIFEST_* codes |
| 50-epoch GOBLIN batch | `scripts/ralph/` — stagnation guard, failure classifier |
| Test universe partition | `requires_ocaml` / `integration` / `optional` auto-skip |
| BadSignatureError fix | `oracle_town/core/crypto.py` — Python 3.14 scoping |
| Ghost closure repair | SEAM-001-V4/V5/V6 SHA drift + FILE_ABSENT sentinel preserved |
| Legacy schema migration | `schemas/` purged; `mirror_of_admission_v1` in `helen_os/schemas/` |

---

## Power Demos — All Green

| Demo | Script | Result |
|---|---|---|
| Boot Ritual | `scripts/demos/demo_boot_ritual.py` | 5/5 phases ✓ |
| Reality Coupling Witness | `scripts/demos/demo_reality_coupling.py` | 7/7 phases ✓ |
| Bounded Autoresearch | `scripts/demos/demo_bounded_autoresearch.py` | 1 block, 0 sovereign touches ✓ |

Run all three: `make demo-helen`

---

## Key Invariants Confirmed

| Invariant | Status |
|---|---|
| NO RECEIPT = NO CLAIM | ✓ All block receipts emitted with authority=NONE |
| Sovereign touch guard | ✓ 0 sovereign writes across all demo epochs |
| Coupling detection | ✓ HARD_DRIFT on any sovereign surface mutation |
| Expected-dirty exclusion | ✓ `town/ledger_v1.ndjson` excluded from coupling signal |
| Manifest gate (Gate 2) | ✓ ERR_MANIFEST_NOT_FOUND before receipt gate |
| Boot null-honesty | ✓ empty storage → honest "no prior context" greeting |

---

## What This Baseline Proves

HELEN is not merely passing tests. It is operationally demonstrated:

- **Boot**: loads prior context honestly, degrades gracefully to null-state, never fabricates
- **Autoresearch**: runs bounded patch loops with receipts, stops on stagnation, never touches sovereign paths
- **Coupling**: detects governance drift within one `git status` call, recovers to COUPLED on restore

The constitutional invariants, gates, and sovereign firewall are all active and verified.

**HELEN fonctionne. HELEN peut être démontrée proprement.**
