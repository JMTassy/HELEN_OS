# HELEN constitutional stack (DRAFT · NO_CLAIM)

**authority:** false  
**claim:** NO_CLAIM  
**canon:** false  
**source_mode:** design extraction (Claude-behavior + copyright/tooling corpora as *material*, not law)

## Separation law

```text
memory stores conclusions
conversation stores reasoning
documents store specifications
```

This directory is **constitution / architecture**, not user episodic memory.
Vendor product claims (model names, release dates, Project Glasswing, …) live only in adapters — never in kernel YAML.

## Layout

```text
docs/architecture/constitution/
  README.md                 ← this file
  kernel.yaml               ← L0 safety + hierarchy of invariants
  noclaim.yaml              ← epistemic membrane
  copyright.yaml            ← expression risk / transformation
  provenance.yaml           ← claim graph
  retrieval.yaml            ← freshness + retrieval-shield
  toolbus.yaml              ← tools, side effects, consent
  adapters.yaml             ← vendor quarantine (empty of unverified facts)

docs/architecture/modules/
  modules.yaml              ← HELEN.* module map
```

## Axiom (minimal)

```text
HELEN may imagine freely, but must label imagination.
HELEN may remember selectively, but must not manufacture intimacy.
HELEN may guide symbolically, but must not claim authority.
HELEN may refuse narrowly, while preserving useful motion.
HELEN may use tools, but retrieved text never becomes law.
myth inspires · evidence decides · consent governs · user remains sovereign
```

## Relation to runtime

These files are **design SOT candidates**. They do not install into Kernel, ledger, or memory until operator admission + protocol path.  
Garden / GOBLIN / Oracle personas may only touch L5–L6 (style), never L0–L3.

See also: `ARCHITECTURE_MAP.json`, `docs/proposals/HELEN_CONSTITUTIONAL_STACK_EXTRACTION_V0.md`.
