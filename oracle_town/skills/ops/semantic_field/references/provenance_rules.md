# Provenance Rules

Provenance tells the field where an object came from. It determines sovereignty, color, and admissibility.

## kernel

- Source: `experiments/helen_os_v02/data/ledger.ndjson`
- Sovereign: Yes
- Display: Signal amber node
- Hash: Real event hash from ledger
- Receipts: 1 (every ledger entry is receipted by definition)

## goblin

- Source: `oracle_town/skills/ops/dan_goblin/brainstorm/batches/*.jsonl`
- Sovereign: No
- Display: Silver node, opacity proportional to confidence
- Hash: Empty (not hash-chained)
- Receipts: 1 if HAL verdict = PASS, else 0
- Note: Only top-scored epochs (by `her_scoring.score`) are included in the field

## terminal

- Source: `oracle_town/skills/ops/helen_terminal/data/ledger.ndjson`
- Sovereign: No
- Display: Dim silver node
- Hash: Terminal ledger event hash (12 chars)
- Receipts: 1 (terminal actions emit receipts)

## Mixing Rule

Cross-provenance edges (weight 0.7, signal amber tint) connect the top-confidence objects across provenance layers. This visualizes the semantic pull model: verified kernel events attract the highest-quality GOBLIN ideas.
