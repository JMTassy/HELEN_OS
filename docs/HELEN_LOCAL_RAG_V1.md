# HELEN_LOCAL_RAG_V1

**status:** runnable (landed standalone)
**authority:** false
**lifecycle:** TOOL (read-only retrieval over HELEN's own corpus)
**tool:** `tools/helen_local_rag.py`
**drafted_at:** 2026-06-07T16:50:35Z
**operator_order:** RAG first, fine-tune later — accuracy before fluency

---

## §1. Why RAG before fine-tune (operator's reasoning, confirmed)

> Fine-tuning teaches style/pattern. RAG gives exact current code.
> For HELEN, exactness matters more.

A fine-tuned Gemma "feels more HELEN" but still hallucinates wrong repo_root,
wrong function signature, wrong tool schema, old kernel structure. RAG retrieves
the real thing with a citation. So the order is:

```
1. RAG / corpus index      ← this tool
2. kernel-context injection ← helen_kernel_context.py (7d97db6)
3. action-schema validator  ← helen_action_schema.py  (1ccc290)
4. replay-on-boot           ← helen_session_restore.py (5490566)
5. only then LoRA fine-tune
```

## §2. What it does

`tools/helen_local_rag.py` — dependency-free (stdlib only), code-aware index over
`.py/.md/.json/.ndjson/.txt`:

- **L0 exact symbol** — every `def`/`class` indexed with file:line + signature.
- **L1 keyword chunk** — 40-line windows, ranked keyword search with citations.
- **Refuses to fabricate** — unknown symbol → `NOT FOUND`, never a guessed path.

The boot's existing `helen_librarian` (L0-L3 embedding retrieval) can layer on
later; this gives precise, cited, zero-dependency answers today — which is exactly
what the grounding problem needs (signatures, locations, schemas — not vibes).

## §3. Acceptance test (operator's example, verified)

```
$ python3 tools/helen_local_rag.py index .
index: 8278 symbols, 16727 chunks

$ python3 tools/helen_local_rag.py sig reduce_promotion_packet
reduce_promotion_packet — 1 definition(s):
  helen_os/governance/skill_promotion_reducer.py:20  [def]  def reduce_promotion_packet(

$ python3 tools/helen_local_rag.py sig _skill_write_file
NOT FOUND: no definition of '_skill_write_file' in the index.
```

On the Mac worktree, `sig _skill_write_file` returns the operator's target:
`helen_skills.py:488` with `args(path, content, append)`.

## §4. Usage

```bash
# build once (per tree; index is gitignored, ~24MB)
python3 tools/helen_local_rag.py index <REPO_ROOT>

# query
python3 tools/helen_local_rag.py sig <symbol>
python3 tools/helen_local_rag.py ask "where is extract_action defined"
python3 tools/helen_local_rag.py search "tool schema"

# in a runtime:
from helen_local_rag import RagIndex
idx = RagIndex.load_or_build(repo_root)
answer = idx.signature("_skill_write_file")   # cited string for the model
```

## §5. Wiring into HELEN (next step, not yet done)

Two integration points, both read-only:

1. **As a tool action** — add `rag_lookup` / `rag_search` to the action catalog so
   HELEN can query her own code mid-turn and answer with citations.
2. **Into KERNEL_CONTEXT** — on a "where/what signature" question, pre-resolve via
   `idx.ask()` and inject the cited answer, so the model never guesses.

Both require the Mac executor wiring (the grounding patch). Index build is
standalone and runs now.

## §6. The corpus types (operator's list, covered)

| chunk type | covered by |
|---|---|
| code chunks | `.py` symbol index + 40-line windows |
| doc chunks | `.md` windows |
| receipt chunks | `.json` / `.ndjson` (ledger, tranche receipts) windows |
| tool-schema chunks | `helen_action_schema.py` symbols + windows |
| failure-case chunks | the canary cases in `helen_action_schema.py` + ledger turns |

## §7. The boundary it respects

RAG retrieves; it does not admit, write, or fabricate. A `NOT FOUND` is a valid,
honest answer — the tool never invents a path to look helpful. This is the same
discipline as the kernel-context fabrication-refusal: exactness over the
appearance of completeness.

---

## Halt boundary

**Status:** runnable standalone; wiring into the Mac runtime awaits the grounding
patch + executor relay.

**Next:**
1. Copy `tools/helen_local_rag.py` to the Mac worktree (with the other three tools).
2. `python3 helen_local_rag.py index <worktree>` to build the index.
3. Wire `rag_lookup` into the action catalog (read-only) so HELEN cites her own
   organs. Then: "where is _skill_write_file?" → "helen_skills.py:488".

**One-line verdict (operator's):** RAG makes HELEN accurate. Fine-tuning makes
HELEN fluent. Accuracy first.
