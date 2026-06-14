# Replay Identity Theorem

## Statement

```
ℐ(L) = [Replay(L)]_∼
```

A research identity is not the current summary of a system.
It is the equivalence class of states reachable by replaying the admissible ledger.

## Plain Language

Identity is not what exists now.
Identity is what can be reconstructed from admissible history.

## Why This Matters for Autoresearch

Standard research systems define knowledge as:

    knowledge = current model state

HELEN defines knowledge as:

    knowledge = replayable admissible claim lineage

The difference: a HELEN knowledge claim survives the destruction of the runtime
because it is grounded in the ledger, not in model weights.

## Universal Application

The theorem applies wherever admissible history is preserved:

| Domain | Destroyed process | What survives |
|---|---|---|
| HELEN runtime | Kernel crash | Ledger replay |
| Software build | Pipeline failure | Provenance + attestation |
| Scientific experiment | Lab destroyed | Published evidence trail |
| Human memory | Cognitive failure | Written records |
| Civilization | Empire collapse | Archives |
| AI system | Model weights wiped | Receipted training data + evals |

In each case: **persistence lives in reproducible history, not in matter.**

## Implication for Autoresearch

An autoresearch conclusion that cannot be replayed from its receipts is not knowledge.
It is a model output.

The question after every epoch:

> Can I reconstruct this conclusion from the evidence bindings alone,
> without accessing the model that generated it?

If yes: the claim is admissible.
If no: the claim is a belief, not a receipt.

## Relation to Obsidian Mirror

The Mirror's output — attractor candidates with lineage pressure — is replayable
because it is computed from fixed corpus hashes and frequency counts.

Given the same HEAD SHA and the same probe definitions, every epoch produces
the same result. This is the determinism requirement: reproducibility is not
optional, it is the admission criterion.

## Shortest Form

```
Reality = admissible replay after destruction.
```
