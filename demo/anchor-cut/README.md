# ⚖️ The Anchor Cut

### A multi-agent system that provably cannot lie to itself.

Every "self-improving" agent stack hits the same wall: **agreement gets mistaken for
evidence.** Ten agents concur, a loop confirms its own output, a judge rewards what it
can measure — and confident nonsense gets promoted. The Anchor Cut is a small, proven
mechanism that makes that **structurally impossible.**

> **The law:** A self-confirming group of agents cannot promote a claim without a fresh,
> **independent** anchor. *N confirmations from one lineage weigh less than one independent
> contradiction.* **Ten mirrors < one window.**

This isn't a manifesto. It's running code with receipts. Run it yourself in 60 seconds.

---

## Run the proof (no dependencies, ~5 seconds)

```bash
cd proof
python3 test_seam.py          # stdlib only — no pip install, no network, no API keys
```

Expected: **9 tests OK.** The reducer (`proof/seam.py`) takes one claim, any number of
reviews, any number of witnesses, and returns exactly one of:

`HOLD` · `HOLD_REOBSERVE` · `HOLD_CONFLICT` · `REJECT` · `ADMITTABLE`

**Reviews are structurally excluded from the gate.** That is the property being proven,
not a bug: `n` agreeing reviews from the same lineage never move the verdict above `HOLD`
— for `n` = 10, 100, or 1,000,000. Only a *fresh, independent* witness can close the gate.

---

## The receipts (claims must come with proof — including ours)

Everything here is backed by a machine receipt in [`receipts/`](receipts/):

| Receipt | What it proves |
|---|---|
| `seam_receipt.json` | **9/9 deterministic tests.** The 6 required cases + the corollary that multiplicity adds zero admissibility power. `ADMITTABLE` is the ceiling; canon is never mutated. |
| `egregor_superteam_receipt.json` | **Live proof on real models.** 10 local `gemma-4-26B` goblins each read one packet and unanimously (10/10) confirmed a **false** claim → reducer says `HOLD`. One independent `git remote` probe contradicted them → `REJECT`. *10 confirmations < 1 independent contradiction*, executable. |
| `temple_ar_0002_receipt.json` | **Cross-family revalidation.** A mutation that a frozen judge KEPT on one model family (Haiku) was **REJECTED** on another (`gemma-4-26B`) by a pre-registered falsifier — proving the loop doesn't over-generalize and the judge isn't a rubber stamp. `KEEP ≠ SHIP ≠ CANON`. |

---

## Why this is different from AutoGen / CrewAI / LangGraph

Those are **orchestration** — they help agents collaborate to produce a result, and the
result is the endpoint. The Anchor Cut is **governance** — the result is only a *candidate*
that must survive an independent anchor before it is anything.

```
ChatDev-style:  agents → discuss → synthesize → deliverable (END)
Anchor Cut:     agents → synthesize → CANDIDATE → independent anchor → reducer → HOLD | REJECT | ADMITTABLE
```

The difference in one question:
- They ask: *"Can a team of agents produce something useful?"*
- We ask: *"Can a team of agents produce something useful **while proving that agreement
  did not become authority**?"*

---

## Scope & honesty

`authority: false` · `ledger_effect: none` · `canon_effect: false` · **NON_SOVEREIGN.**
`ADMITTABLE` is the highest positive result this code can reach — it means *evidence-qualified
for promotion*, never *promoted*. Nothing here mutates canon. It is a demonstration of one
narrow, checkable property — not a general solution to agent alignment. What it claims, it
proves; what it doesn't prove, it doesn't claim.

Full source & lineage: `experiments/witnessed_loop_graph_seam_v0/` ·
`docs/proposals/EGREGOR_GOVERNED_COGNITION_V0.md` ·
`docs/proposals/INSIGHT_COMPOST_SELECTION_FUNNEL_V0.md`
