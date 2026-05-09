# HELEN Memory Template

`oracle_town/memory_template/` contains the **canonical structure** for HELEN's live memory.
The **live memory** lives in `oracle_town/memory/` — which is gitignored.

## Setup on a new device

### Option A — Local memory (single device)

```bash
mkdir -p oracle_town/memory
cp oracle_town/memory_template/helen_identity.md oracle_town/memory/
cp oracle_town/memory_template/active_context.md oracle_town/memory/
touch oracle_town/memory/long_term_memory.jsonl
touch oracle_town/memory/sovereign_ledger.jsonl
```

### Option B — Shared memory via iCloud (recommended for multi-device)

```bash
# Create the shared folder once on your primary Mac
mkdir -p "$HOME/Library/Mobile Documents/com~apple~CloudDocs/HELEN/memory"
cp oracle_town/memory_template/*.md \
   "$HOME/Library/Mobile Documents/com~apple~CloudDocs/HELEN/memory/"
touch "$HOME/Library/Mobile Documents/com~apple~CloudDocs/HELEN/memory/long_term_memory.jsonl"
touch "$HOME/Library/Mobile Documents/com~apple~CloudDocs/HELEN/memory/sovereign_ledger.jsonl"

# Then symlink from every Mac:
bash oracle_town/skills/ops/helen_dashboard/scripts/setup_memory_symlink.sh \
  "$HOME/Library/Mobile Documents/com~apple~CloudDocs/HELEN/memory"
```

### Option C — Syncthing shared folder

Same as Option B but replace the iCloud path with your Syncthing shared folder path.

## Files

| File | Purpose |
|---|---|
| `helen_identity.md` | Who HELEN is — tone, invariants, creator. Fill in once, rarely changes. |
| `active_context.md` | Boot nucleus — loaded at every HELEN session start. Keep compact. |
| `long_term_memory.jsonl` | Append-only durable memories. One JSON object per line. |
| `sovereign_ledger.jsonl` | Action receipts from Skill runs. One JSON object per line. |

## Rules

- `oracle_town/memory/` is gitignored — never commit live memory
- `oracle_town/memory_template/` is versioned — placeholders and structure only
- Never put secrets, API keys, or client PII in memory files
- Dates must be absolute ISO 8601 (never "next Thursday")
