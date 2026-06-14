---
name: WULMOJI_NORMALIZER_SPEC_V0_1
version: "0.1"
status: NON_SOVEREIGN_SPEC
authority: false
sovereign: false
canon: false
layer: TEMPLE
simulation: DREAM_OF_CONQUEST
date: 2026-06-15
lexicon: docs/specs/WULMOJI_LEXICON_V0_1.json
wul_packet_spec: docs/specs/WUL_PACKET_SPEC_V0_1.md
---

# WULmoji Normalizer Spec v0.1

Canonical normalization pipeline for WULmoji expressions.
Goal: deterministic bytes → deterministic SHA256 → replay-safe hash.

`payload_hash = SHA256(CANON_JSON(AST))`

---

## Purpose

WULmoji tokens are emoji grapheme clusters. The same visual glyph may be encoded
multiple ways (with/without U+FE0F variation selector, NFC vs NFD, etc.).
Without normalization, the same semantic expression produces different byte
sequences on different systems → different SHA256 → replay failure.

This spec fixes the normalization pipeline so that
**one expression → one canonical form → one hash**, across all platforms
and Python versions, without any dependence on system locale, time, or random state.

---

## Scope

This normalizer handles WULmoji v0.1 token expressions as defined in
`WULMOJI_LEXICON_V0_1.json`. It does NOT:

- Parse or validate WUL inter-agent packets (`WUL_PACKET_SPEC_V0_1.md` scope)
- Modify or validate sovereign ledger entries
- Touch `helen_os/schemas/`, `helen_os/governance/`, or `town/ledger_v1.ndjson`
- Interpret semantic meaning or gate verdicts — those belong to the gate layer

---

## Normalization Pipeline

Input: raw UTF-8 string (possibly containing emoji, arrows, bullets, whitespace, text).

### Step 1 — Unicode NFC

```
normalized = unicodedata.normalize("NFC", raw_input)
```

Required first. NFC is the canonical composition form. All subsequent steps
operate on NFC output. NFD input is accepted but immediately promoted to NFC.

### Step 2 — Variation Selector Canonicalization

Strip U+FE0F (VARIATION SELECTOR-16, emoji presentation) and U+FE0E
(VARIATION SELECTOR-15, text presentation) from all positions.

```python
import re
VS_PATTERN = re.compile(r'[︎️]')
stripped = VS_PATTERN.sub('', normalized)
```

Then re-apply the canonical codepoint sequences from `WULMOJI_LEXICON_V0_1.json`.
Each token's `unicode` array is the canonical form. Tokens that include `U+FE0F`
in their lexicon entry receive it back during AST construction (step 5).
Tokens that do not include `U+FE0F` do not.

Rationale: stripping then re-adding from lexicon gives a single canonical byte
sequence regardless of the input encoding variant.

### Step 3 — Grapheme Cluster Tokenization

Split the stripped string into Unicode grapheme clusters.
Reference algorithm: Unicode Standard Annex #29 §Grapheme Cluster Boundaries.

```python
import regex  # third-party; grapheme boundary aware
clusters = regex.findall(r'\X', stripped)
```

Each cluster is one candidate token. Whitespace-only clusters (U+0020, U+0009,
U+000A, U+000D) are discarded between tokens. Whitespace inside a text literal
(if text literals are ever introduced in v0.2+) is preserved as a single
LITERAL node — not applicable in v0.1.

### Step 4 — Lexicon Lookup

For each cluster, look up in the v0.1 lexicon:

```
match = lexicon.lookup(cluster_nfc_stripped)
```

**Lookup key:** NFC of cluster with VS stripped (as produced by steps 1–2).

Result:
- KNOWN token → emit AST node `{class, type, arity, canonical_codepoints}`
- UNKNOWN cluster → emit AST node `{class: "UNKNOWN", type: "UNKNOWN", raw_codepoints: [...], warning: true}`
  Continue parsing. Do NOT raise an error.

### Step 5 — Delimiter Balance Check

After tokenizing the full expression, verify GROUP delimiter balance:

```
depth = 0
for node in tokens:
    if node.type == "GROUP_OPEN":  depth += 1
    if node.type == "GROUP_CLOSE": depth -= 1
    if depth < 0: raise NormalizerError("UNMATCHED_GROUP_CLOSE")
if depth != 0: raise NormalizerError("UNCLOSED_GROUP_OPEN")
```

Imbalanced GROUP delimiters are a **hard error** (not a warning).
All other delimiter violations (e.g. EOM not at end) produce warnings only.

### Step 6 — EOM Boundary Check

If an EOM token (🏁) is present:
- Any token following EOM in the same expression produces a warning: `TOKENS_AFTER_EOM`.
- The AST is truncated at EOM; trailing tokens are preserved in a `trailing` field
  of the AST root for diagnostic purposes.

### Step 7 — AST Construction

Produce a tree from the flat token list using the GROUP_OPEN / GROUP_CLOSE
pairs as scope delimiters:

```json
{
  "ast_version": "0.1",
  "nodes": [
    {"class": "O", "type": "PASS", "canonical": "🟢"},
    {"class": "D", "type": "GROUP_OPEN", "canonical": "🔷"},
    {"class": "E", "type": "EVIDENCE", "canonical": "📚"},
    {"class": "D", "type": "GROUP_CLOSE", "canonical": "🔶"},
    {"class": "D", "type": "EOM", "canonical": "🏁"}
  ],
  "warnings": [],
  "errors": []
}
```

UNKNOWN nodes are included verbatim. The `canonical` field for each node is
the lexicon's canonical codepoint sequence reconstructed as a UTF-8 string.

### Step 8 — Canonical JSON Rendering

Serialize the AST to JSON with these constraints (all are mandatory):

1. **Key order:** alphabetical within each object (Python: `sort_keys=True`)
2. **No trailing whitespace** on any line
3. **Compact separators:** `(',', ':')` — no spaces after `:` or `,`
4. **No BOM** — output is plain UTF-8
5. **No trailing newline** after the closing `}`
6. **Unicode not escaped:** `ensure_ascii=False` — emoji stored as UTF-8, not `\uXXXX`

```python
import json
canonical_json_bytes = json.dumps(
    ast_dict,
    sort_keys=True,
    separators=(',', ':'),
    ensure_ascii=False
).encode('utf-8')
```

### Step 9 — Hash Computation

```python
import hashlib
payload_hash = hashlib.sha256(canonical_json_bytes).hexdigest()
```

Output: 64-character lowercase hex string.

**Invariant:** same WULmoji expression on any platform, any Python ≥ 3.8,
must produce the same `payload_hash`. This is the replay invariant.

---

## Replay Invariant

The normalizer must be deterministic across:

- Python versions (3.8+)
- Operating systems (macOS, Linux, Windows)
- Locale settings (`LANG`, `LC_ALL`)
- Time and clock state — the normalizer takes NO time inputs
- Random state — the normalizer takes NO random inputs

If a test detects hash drift across two identical inputs, it is a normalizer bug.

---

## Failure Modes

| Condition | Severity | Behavior |
|---|---|---|
| Unknown token | WARNING | AST includes UNKNOWN node; parsing continues |
| Unmatched GROUP_CLOSE | ERROR | Raise `NormalizerError("UNMATCHED_GROUP_CLOSE")`; abort |
| Unclosed GROUP_OPEN | ERROR | Raise `NormalizerError("UNCLOSED_GROUP_OPEN")`; abort |
| Tokens after EOM | WARNING | AST truncated at EOM; `trailing` preserved; hash covers truncated AST |
| Non-NFC input | SILENT | Promoted to NFC silently; no warning |
| Empty expression | WARNING | AST has zero nodes; hash is SHA256 of `{"ast_version":"0.1","errors":[],"nodes":[],"warnings":[]}` |
| Non-UTF-8 bytes | ERROR | Raise `NormalizerError("INVALID_UTF8")`; abort |

`NormalizerError` is a typed exception — not a warning, not a log line.
The caller is responsible for catching and reporting it.

---

## Safety Boundary

The normalizer:

- Reads from `WULMOJI_LEXICON_V0_1.json` (at import time; static after load)
- Writes to: **nothing** — it is a pure function
- Does not open network connections
- Does not read from the filesystem during normalization (only at init)
- Does not mutate global state
- Does not write to `town/ledger_v1.ndjson` or any sovereign path
- Does not emit ledger entries or receipts

Hash output is a non-sovereign artifact. If a caller passes the hash to
`tools/helen_say.py`, that is the caller's bridge action, not the normalizer's.

---

## Reference Implementation Sketch

```python
import re
import json
import regex
import hashlib
import unicodedata

VS_PATTERN = re.compile(r'[︎️]')


def normalize(raw: str, lexicon: dict) -> dict:
    nfc = unicodedata.normalize("NFC", raw)
    stripped = VS_PATTERN.sub('', nfc)
    clusters = regex.findall(r'\X', stripped)
    clusters = [c for c in clusters if c.strip()]

    nodes = []
    warnings = []
    errors = []

    for cluster in clusters:
        key = VS_PATTERN.sub('', unicodedata.normalize("NFC", cluster))
        entry = lexicon.get(key)
        if entry:
            nodes.append({
                "class": entry["class"],
                "canonical": entry["canonical"],
                "type": entry["type"]
            })
        else:
            codepoints = [f"U+{ord(c):04X}" for c in cluster]
            nodes.append({
                "class": "UNKNOWN",
                "raw_codepoints": codepoints,
                "type": "UNKNOWN"
            })
            warnings.append(f"UNKNOWN_TOKEN: {codepoints}")

    _check_group_balance(nodes)

    ast = {
        "ast_version": "0.1",
        "errors": errors,
        "nodes": nodes,
        "warnings": warnings
    }

    canon_bytes = json.dumps(
        ast, ensure_ascii=False, separators=(',', ':'), sort_keys=True
    ).encode('utf-8')

    return {
        "ast": ast,
        "payload_hash": hashlib.sha256(canon_bytes).hexdigest()
    }


def _check_group_balance(nodes):
    depth = 0
    for node in nodes:
        if node.get("type") == "GROUP_OPEN":
            depth += 1
        elif node.get("type") == "GROUP_CLOSE":
            depth -= 1
            if depth < 0:
                raise NormalizerError("UNMATCHED_GROUP_CLOSE")
    if depth != 0:
        raise NormalizerError("UNCLOSED_GROUP_OPEN")


class NormalizerError(Exception):
    pass
```

---

## Version History

| Version | Date | Note |
|---|---|---|
| 0.1 | 2026-06-15 | Initial frozen spec. Token classes O/R/D/M/E. GROUP balance hard-error. Unknown token warning-only. |

v0.2 may introduce text literal nodes. v0.1 parsers MUST ignore UNKNOWN nodes
and continue — this is the forward-compatibility contract.

---

```
CLAIM_TYPE: spec
AUTHORITY: false
SOVEREIGN: false
CANON: false
LEDGER_MUTATION: forbidden
SIMULATION_ONLY: false
```
