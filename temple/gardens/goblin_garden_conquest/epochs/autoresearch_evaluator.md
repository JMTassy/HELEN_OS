# Temple Autoresearch — Evaluator

**CLAIM_TYPE:** simulation  
**Purpose:** How the simulation evaluates candidate configurations.

---

## Evaluation Schema

```
EVAL_RESULT_V0 = {
  "epoch": N,
  "candidate_axis": "...",
  "candidate_id": "A|B|C",
  "signal": "...",         # observable signal description
  "score": 0.0-1.0,        # normalized evaluation score
  "keep": true|false,
  "reject_reason": "...",  # if keep=false
  "receipt": "...",        # local receipt ID
  "authority": false,
  "sovereign": false
}
```

## Scoring Functions

### Quest Ordering Score
```
score = (compounding_knowledge_chains / total_quests) * 0.6
      + (cross_domain_coverage / total_domains) * 0.4
```

### Map Clarity Score
```
score = (territory_disputes_resolved_by_receipts / total_disputes) * 0.5
      + (player_orientation_clarity) * 0.5
# player_orientation_clarity: 1.0 if map legend is self-explanatory, else 0.5
```

### Bulletin Clarity Score
```
score = (valid_lines / total_lines) * 0.4
      + (information_per_line_normalized) * 0.4
      + (error_signal_present_when_needed) * 0.2
```

### World Model Consistency Score
```
score = 1.0 - (validator_error_count / 10)
# floor at 0.0
```

### Learning Path Score
```
score = (stages_that_reference_prior_stage / total_stages) * 0.7
      + (final_validator_covers_all_stages) * 0.3
```

## Keep Rule

Candidate is KEPT if `score >= 0.7`.  
Candidate is REJECTED if `score < 0.7` with `reject_reason` recorded.  
Ties between candidates resolved by highest `world_model_consistency` score.

---

```
CLAIM_TYPE: simulation
AUTHORITY: false
SOVEREIGN: false
```
