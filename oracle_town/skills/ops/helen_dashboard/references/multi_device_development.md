# HELEN OS — Multi-Device Development

Jean-Marie develops HELEN from 3 devices (2 Macs + iPad). This document defines the sync protocol.

## Rule

**One GitHub. One memory source. Three devices as terminals.**

| Layer | Sync mechanism | Device role |
|---|---|---|
| Code | GitHub (`git pull`/`git push`) | Mac A, Mac B: dev; iPad: read-only |
| Live memory | iCloud Drive or Syncthing (symlink) | All Macs: read/write; iPad: via HELEN interface |
| Secrets/tokens | Local only (`~/.helen_env`, mode 600) | Never committed |

## Before coding on any device

```bash
cd /Users/jean-marietassy/Documents/GitHub/helen_os_v1
bash oracle_town/skills/ops/helen_dashboard/scripts/sync_preflight.sh
git pull --rebase   # if behind
```

## After coding on any device

```bash
git add .
git commit -m "feat(...): description"
git push
```

## On another device before starting work

```bash
git pull --rebase
```

## First-time setup on a new Mac

```bash
# 1. Clone the repo
git clone https://github.com/JMTassy/helen-conquest.git helen_os_v1
cd helen_os_v1

# 2. Set up venv
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# 3. Set up shared memory (iCloud recommended)
bash oracle_town/skills/ops/helen_dashboard/scripts/setup_memory_symlink.sh \
  "$HOME/Library/Mobile Documents/com~apple~CloudDocs/HELEN/memory"

# 4. Start dashboard
bash oracle_town/skills/ops/helen_dashboard/scripts/run_dashboard.sh
# → http://localhost:7700
```

## iPad workflow

The iPad is an **interface/control device**, not a development machine.

- Open `http://<mac-ip>:7700` in Safari to access the dashboard
- Use the MEMORY tab to add memories, write receipts
- Use the Skills panel to review available capabilities
- Do NOT edit code from iPad — use GitHub Mobile only for review

## Memory strategy

```
oracle_town/memory/  ──── gitignored ──── lives in iCloud or Syncthing
oracle_town/memory_template/  ──── versioned ──── structure + placeholders only
```

**To share memory across Macs:**

```bash
# iCloud (recommended)
bash oracle_town/skills/ops/helen_dashboard/scripts/setup_memory_symlink.sh \
  "$HOME/Library/Mobile Documents/com~apple~CloudDocs/HELEN/memory"

# Syncthing alternative
bash oracle_town/skills/ops/helen_dashboard/scripts/setup_memory_symlink.sh \
  "$HOME/Sync/HELEN/memory"
```

Both Macs must run `setup_memory_symlink.sh` pointing to the **same** cloud folder.

## What NOT to do

- Never commit `oracle_town/memory/` (gitignored)
- Never store API keys in the repo (use `~/.helen_env`)
- Never commit without pulling first
- Never have divergent memory across devices (use symlink, not copies)
- Never edit the same file simultaneously on two devices without pulling first

## Conflict resolution

If git conflicts occur:
1. Do NOT force-push
2. Resolve conflicts manually (HELEN files are structured — conflicts are readable)
3. Commit the merge
4. Verify server still starts: `bash scripts/run_dashboard.sh`

## Invariant

HELEN must feel like the same intelligence on every device.
This requires: same code (GitHub) + same memory (symlinked cloud folder).
