# Temple Autoresearch — Candidate Space

**CLAIM_TYPE:** simulation  
**Purpose:** Map the candidate space for the Temple autoresearch simulation.

---

## Candidate Axes

The simulation explores 5 axes. Each is a question with observable signals only.

### Axis 1: Quest Ordering

```
CANDIDATES:
  A: Linear (difficulty 1→5, knowledge before strategy)
  B: Spiral (alternate domain types, prevent mono-domain lock)
  C: Faction-first (complete one faction's quests before branching)

SIGNAL: receipt chain coherence across epochs
EVALUATION: does the ordering produce compounding knowledge, or isolated facts?
```

### Axis 2: Symbolic Map Layout

```
CANDIDATES:
  A: Concentric (core knowledge at center, factions at edge)
  B: Quadrant (four factions, one quadrant each, Heap at center)
  C: Network (territory as graph, edges = knowledge transfer paths)

SIGNAL: clarity of territory dispute resolution
EVALUATION: does a player understand what territory they're competing for?
```

### Axis 3: Bulletin Clarity

```
CANDIDATES:
  A: 3 lines per bulletin (minimal)
  B: 5 lines per bulletin (fuller signal)
  C: Mixed (error/warning lines included with ⚠️📜)

SIGNAL: information density per validated line
EVALUATION: which format makes the claim state legible at a glance?
```

### Axis 4: World Model Consistency

```
QUESTION: do faction/resource/territory/quest models cohere without contradiction?
SIGNAL: validator error count across checks
EVALUATION: 0 errors = consistent
```

### Axis 5: Learning Path Coherence

```
QUESTION: does Doctrine → Meditation → Bulletin → Validator produce compounding learning?
SIGNAL: can a reader reconstruct the full epistemic posture from the path?
EVALUATION: qualitative — is each stage a natural consequence of the prior?
```

---

```
CLAIM_TYPE: simulation
AUTHORITY: false
SOVEREIGN: false
```
