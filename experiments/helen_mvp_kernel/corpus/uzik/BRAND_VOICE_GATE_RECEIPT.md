# brand_voice GATE — RECEIPT (V1)

🔵 OBSERVED · NON_SOVEREIGN · authority=0 · not admitted · no ledger effect
Operator directive "build brand_voice gate" @ 7c0ff88

## What was done
Turned the UZIK corpus's `lint_checklist` from data into an executable, fail-closed linter:
`helen_os/voice/brand_voice_gate.py` + 11 falsifiers `helen_os/tests/test_brand_voice_gate.py`.

The gate READS `corpus/uzik/UZIK_CORPUS_V1.json` (ban-lists live in the corpus, not hardcoded) and
returns a typed `VoiceResult(verdict, violations, authority=0, checks_run)`. It is a CHECKER, never
an authority: `render ⊬ admitted` — a clean voice check is a candidate, not a decision. No state
mutation, no capability mint, no admit surface.

Three fail-closed checks (any one ⇒ FAIL):
- **BANNED_VOCAB** — word-boundary match on `vocabulary.ban` + `production_verbs.ban`
  (innovation / impact / excellence / leverage / optimize / synergize / …).
- **NEGATIVE_PARALLELISM** (hard ban) — EN "not X but Y" / "don't just X but Y" and FR
  "n'est pas X mais Y" / "non pas X mais Y".
- **UNSOURCED_METRIC** — a percentage / multiplier / 2+-digit number with no source marker on the
  line (claims discipline: `claim ⊬ proof`). A metric WITH `source:` / citation / URL passes.

Verified live: 11/11 falsifiers green (suite 218→229). A hype line
("We leverage innovation to drive impact — not a tool but a revolution, up 40%.") →
FAIL with 5 violations across all three classes.

## Graph-ready
`report(result)` emits a projection-only structured object (checks as nodes, violations by code as
edges, `authority=0`, `canon=false`) that a graph/infographic renderer can draw — but a renderer
may never admit it. No graphing skill is available in this session to invoke, so the gate emits the
structured report rather than call a fabricated tool. `D_render(x) ⊬ A(x)`.

## Honest residuals
- Heuristic, not NLP-complete: negative-parallelism and unsourced-metric detection are conservative
  regexes (false positives preferred to false negatives). Sophisticated rephrasings can evade;
  the checks are DECLARED (`checks_run`), not silent, so a miss is visible, not laundered.
- Enforces the machine-checkable rules only. Register/tone rules (block writing, compression,
  visual-first) are corpus data a human/LLM applies; they are not auto-linted here.
- NON_SOVEREIGN, uncommitted, not pushed. Held for a COMMIT / PUSH verb.
