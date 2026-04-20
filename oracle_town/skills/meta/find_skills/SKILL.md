---
name: meta/find_skills
description: Discovery layer over oracle_town/skills/**. Indexes every SKILL.md frontmatter (name, description, faculty, status, prerequisite) and supports keyword search + JSON output. The 40-line stdlib script that turns a 10-skill (soon 20+) library from a blind pile into something queryable. Meta-skill — does not itself do HELEN work; it tells you which skill does.
helen_faculty: META / DISCOVERY
helen_status: DOCTRINE (calibrated 2026-04-21)
helen_prerequisite: none (works on any repo with SKILL.md frontmatter convention)
---

# find_skills — Oracle Town discovery layer

**Class**: Non-sovereign meta-skill. Reads SKILL.md frontmatter only. Writes nothing. Modifies nothing. Makes the skill library searchable.

> *"This Japanese guy installs Find Skills, describes what he wants, gets the right skill out of hundreds. His automated YouTube system is killing it."* — operator observation 2026-04-20.

HELEN already has 10 SKILL.md files across `oracle_town/skills/**`, trending toward 20+. Without discovery, adding more skills makes the library worse, not better. This script closes that gap.

---

## 1. What it does

Walks `oracle_town/skills/**/SKILL.md`, parses YAML frontmatter (stdlib only — no PyYAML dep), and exposes three commands:

- `list` — every skill, one line each: `faculty | status | path — description`
- `search <query>` — filter by substring match in name / description / faculty (case-insensitive)
- `json` — full structured dump for programmatic consumers

## 2. Usage

```bash
# list everything
python3 oracle_town/skills/meta/find_skills/find_skills.py list

# find skills related to video
python3 oracle_town/skills/meta/find_skills/find_skills.py search video

# find skills related to identity gating
python3 oracle_town/skills/meta/find_skills/find_skills.py search "identity"

# machine-readable
python3 oracle_town/skills/meta/find_skills/find_skills.py json
```

## 3. Frontmatter contract (what this skill assumes)

Every SKILL.md in `oracle_town/skills/**` starts with YAML frontmatter between `---` markers. Required fields:

| Field | Type | Example |
|---|---|---|
| `name` | str | `video/math_to_face` |
| `description` | str (1 sentence) | "Sovereign white-box rendering pipeline..." |

Optional but recommended:

| Field | Type | Example |
|---|---|---|
| `helen_faculty` | str | `RENDER / COGNITION` |
| `helen_status` | str | `DOCTRINE`, `INVARIANT`, `DRAFT`, `DEPRECATED` |
| `helen_prerequisite` | str | `helen-director/SKILL.md (peer)` |

Skills missing `name` or `description` are flagged with `[incomplete]` in output but not dropped — discovery should be lossy-tolerant.

## 4. Design notes

- **Pure stdlib** — no PyYAML, no click. 40 lines of Python. Runs on any 3.9+.
- **No embedder, no LLM** — Phase 1 is substring matching. Semantic search (embed descriptions, nearest-neighbor) is a Phase 2 extension if/when the catalog crosses ~50 skills and substring matching gets noisy.
- **Read-only** — never modifies SKILL.md files. Operator discipline: if you want to improve a skill's description, edit the SKILL.md directly; this tool reflects reality, doesn't author it.
- **No caching** — always reads fresh. The cost is linear in skill count × file size (~µs per skill) so caching buys nothing at current scale.

## 5. Position in the marketplace pattern

Per the baoyu-skills reference (2026-04-21): a skill library scales as **many narrow skills + one discovery layer**. This is that discovery layer. It is the **first entry** in what may become a wider `oracle_town/skills/meta/**` category (catalog tooling, promotion reducers, skill-registry queries).

Explicit non-goals:
- Not a skill installer (no `npx skills add ...` equivalent — HELEN is monorepo, not marketplace)
- Not a skill recommender in the "ML sense" (no embeddings in v1)
- Not a quality scorer (does not rank skills by usefulness)

## 6. Status

**DOCTRINE** (calibrated 2026-04-21). Promotion to INVARIANT requires:
- 50+ skills indexed (coverage proof)
- Fresh session verifies `list` / `search` / `json` outputs are deterministic over the canonical catalog
- K-tau `mu_DETERMINISM` gate passes on the reference query set

Until then: cite as "find_skills discovery layer v1, operator-calibrated 2026-04-21."

## 7. One-line summary

> Indexes every SKILL.md frontmatter in the monorepo and lets you grep it — nothing more, nothing less.
