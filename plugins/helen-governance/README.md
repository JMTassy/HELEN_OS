# helen-governance

Constitutional discipline for Claude work, distilled from HELEN OS.

## What this plugin gives you

Five governance skills that fire when Claude is doing work where
**auditability matters more than throughput**: producing artifacts that
need to defend their own admission, working in code/governance/
infrastructure where silent mutations are dangerous, or staging work
that hands off to a sovereign reviewer.

| Skill | Fires when... | Core directive |
| --- | --- | --- |
| `no-receipt-no-claim` | Producing an action that mutates state | Every action emits a receipt; no receipt → action is constitutionally void |
| `halt-boundary` | Work defers to a sovereign reviewer | Declare a "Halt boundary" §; enumerate resume conditions |
| `goblin-role` | Doing operational work under non-sovereign role | `GOBLIN_CLARITY = Tool + Command + Log + Receipt` |
| `proposer-validator` | Authoring + admitting an artifact | Proposer ≠ Validator. Same actor cannot do both. |
| `doctrinal-diff` | Incoming external doctrine touches existing canon | Diff first; identify restated vs new vs out-of-scope; bottle only the new |

## What this plugin does NOT give you

- No MCP connectors (HELEN governance is conceptual; doesn't bind to external SaaS)
- No autonomous tool execution (the plugin's whole point is that admission is sovereign-class)
- No ML / generative AI capability beyond what Claude already has
- No specific domain knowledge — this is meta-discipline that overlays any other plugin

## Install

```bash
claude plugin marketplace add jmtassy/helen-conquest
claude plugin install helen-governance@helen-conquest
```

(Adjust path per your marketplace setup; or clone the source repo and
add as a local marketplace.)

## Slash commands

- `/helen-governance:receipt` — emit a structured receipt template for an action just taken
- `/helen-governance:halt` — emit a halt-boundary section template for a sovereign handoff
- `/helen-governance:diff` — perform doctrinal diff between an incoming proposal and your existing canon

## Lineage

This plugin is a slice of HELEN OS, an append-only governance kernel
project. The skills here are the five most-portable invariants. The
full HELEN system includes layered architecture (membrane / ledger /
executor / skills / temple), hash-chained ledgers, sovereign verdict
gates, and an identity-gate stack for governed generative media —
none of which are packaged here. This plugin is the discipline, not
the kernel.

## License

Same as HELEN OS source repository.
