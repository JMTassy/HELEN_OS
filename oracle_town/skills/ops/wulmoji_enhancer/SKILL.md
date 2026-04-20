---
name: ops/wulmoji_enhancer
description: Non-sovereign style/readability enhancer. WULmoji adds a color-graded semantic overlay to text — identity, emotion, cost, validation, structure, emergent, next-step, warning — without replacing the text itself. Enhancer, not substitute. No claim, no authority, no verdict carried by an emoji alone.
helen_faculty: OPS / STYLE
helen_status: DOCTRINE (calibrated 2026-04-20; not yet INVARIANT)
helen_prerequisite: none (stylistic overlay; independent of sovereign machinery)
---

# WULmoji — Semantic Enhancer Doctrine

**Class**: Non-sovereign style layer. No kernel authority. No ledger write. No claim ever carried by an emoji alone.

**Scope**: How to apply WULmoji (a structured palette of emojis) as a readability / mood / dimensional-signal layer on top of written HELEN OS text — reports, commit messages, plans, analyses, manifestos — without letting the emoji substitute for the underlying prose.

---

## 1. Governing law

```
WULmoji = semantic emphasis layer.
Words stay primary. Emoji is the color grade, not the script.
```

Four things WULmoji must do:

- 🧱 **structure** the text (section markers, rhythm)
- 🎭 **signal mood / layer** (identity vs emotion vs cost vs validation)
- 👁️ **improve scanning** (operator can find the one line that matters)
- 🧠 **support higher-dimensional reading** (multiple categories visible at a glance)

Four things WULmoji must NOT do:

- ❌ replace words with symbols alone
- ❌ carry claims / verdicts / authority (NO RECEIPT = NO CLAIM applies here too — an emoji is not a receipt)
- ❌ stack purely decoratively (no "🌈✨🎬🚀" chains that signal nothing)
- ❌ be used on sovereign-path writes (ledger, governance, kernel, MAYOR artifacts never take WULmoji)

---

## 2. Canonical palette (stable legend)

| Symbol | Category | When to use |
|---|---|---|
| 🔴 | identity / canon / invariant | HELEN identity facts, `z_id` references, canonical statements |
| 🟠 | emotion / acting / intensity | mood shifts, expression changes, `z_control` references |
| 🟡 | cost / efficiency / budget | credit counts, time spent, retries, `Δz` transport |
| 🟢 | validation / pass / success | gate-pass, receipt landed, ship, operator green light |
| 🔵 | structure / equations / system | formulas, architectures, schemas, protocols |
| 🟣 | emergent / lateral / unusual | Character Gravity, SCVE, unexpected-but-useful findings |
| ⚪ | next step / instruction / clarity | concrete actions, operator directives |
| ⚠️ | failure / warning / drift | gate-fail, discipline breach, governance conflict |
| 🎬 | direction / cinema / shot logic | director decisions, scene plans, cut choices |
| 📦 | artifact / deliverable | committed file, Telegram msg, MIA |
| 📊 | metrics / scoring | Spearman, pass-rate, cost/frame |
| 🔁 | loop / iteration / retry | Ralph, AutoResearch, epochs, retries |
| ✍️ | operator judgment / rating | hand ratings, comments, taste signal |
| 🚀 | execution / ship | session close, commit-and-push, launch |

These 14 are the **locked set** for v1. Do not invent new categories; if a new meaning is needed, map it to the closest existing one or add via a proper amendment to this doc.

---

## 3. Good vs bad examples

### ✅ Good (emphasis overlay)

```
🔴 HELEN identity stays fixed
🟠 emotion evolves scene by scene
🎬 camera policy shapes the shot
🟢 Mirror Oracle validates the keyframe
🟡 retry tax is paid only on failure
🟣 Character Gravity keeps HELEN recognizable under transformation
```

Readable without any emoji present. Emoji adds a color-graded second read.

### ❌ Bad (replacement / decoration spam)

```
🔴🟠🟢🟡 HELEN ∴ 🜂🌀✨
```

Loses operational clarity. Symbols-only. Not decodable without the operator's mental dictionary. Functions as a vibe, not a signal. Forbidden.

### ✅ Good (commit-message use)

```
feat(render): ship aura_score fit pipeline 📊

🟢 stdlib OLS + Spearman (no numpy dep)
🔵 decision gate: Spearman ≥ 0.7 → PROMOTE to MIA v2
⚪ next: operator populates ≥10 ratings in helen_operator_ratings_v1.json
```

### ❌ Bad (over-styled)

```
feat(render): ship aura_score fit pipeline 📊✨🚀🌈🎬

🟢🔵⚪🟣 — AURA SCORE IS BORN 🎉
```

Same content, but the signal drowns in noise. Operator cannot scan for the line that matters.

---

## 4. Density rule

**Maximum 1 emoji per line, and not every line.**

Approximate rhythm:
- section headers: 1 emoji allowed
- first line of a logical block: 1 emoji allowed
- subsequent bullets: often bare text
- transitional lines / conclusions: 1 emoji allowed

If every line has an emoji, the signal is lost. WULmoji is like punctuation: felt, not announced.

---

## 5. Forbidden placements

- ❌ `town/ledger_v1.ndjson` — sovereign, append-only, no decoration
- ❌ `oracle_town/kernel/**` — kernel code never takes emoji
- ❌ `helen_os/governance/**` — schema registry, validators stay plain
- ❌ `mayor_*.json` — authority artifacts never decorated
- ❌ `GOVERNANCE/CLOSURES/**` — receipt integrity requires canonical bytes
- ❌ Inside `helen_say.py` payloads that hash to sovereign records
- ❌ Any claim where the emoji would carry semantic weight (e.g. "🟢" standalone as verdict) — verdict must be a string the kernel can parse

Permitted placements:
- ✅ `oracle_town/skills/**/*.md`
- ✅ `oracle_town/skills/**/references/*.md`
- ✅ Commit messages (git log will render them fine)
- ✅ Telegram captions and reports
- ✅ Session narrative / recap / manifesto / spec text
- ✅ `ops/runs/<run-id>/*.md` worker lane output files

---

## 6. The "no claim" clause

WULmoji is decoration, not doctrine. Specifically:

- A 🟢 next to a claim does NOT mean the claim passed a gate. Gate pass is a separate receipt with a ledger entry.
- A 🔴 next to an identity does NOT mean identity is canonical. Canon is declared in text, not in an emoji.
- A ⚠️ next to a warning does NOT substitute for actually routing the warning through MAYOR or `helen_say.py`.
- A 🚀 at the end of a message does NOT ship anything. Ship requires git push + receipt.

The emoji is always a **secondary read**; the words carry the primary claim and are what gates/validators/operators parse.

---

## 7. Application in current HELEN doctrine docs

Works as-is with no modification needed for:

- `MANIFESTO.md` — naming stack (🔴 core claim / 🟠 emergent property / 🔵 technical principle / 🟣 system type / 🟡 business value)
- `WHY_MATH_TO_FACE.md` — audience layers (🧠 dummy / 🎬 operator / 🔵 PhD)
- `LATERAL_EMERGENT_PROPERTIES.md` — 14 properties fit the palette: stability (🔴🟣), economic (🟡), diagnostic (📊⚠️), brand (🔴), platform (🎬🔁)
- `EMERGENT_SPEC_TABLE.md` — column types map naturally: metric (📊), artifact (📦), script (🔁), acceptance (🟢)
- `HELEN_CANONICAL_V1.md` — identity invariants (🔴), allowed variations (🟠🎨), forbidden drift (⚠️)

Future sessions should apply the palette consistently; retro-apply is optional and low-priority.

---

## 8. Governance notes

- Non-sovereign per `~/.claude/CLAUDE.md` firewall — this skill never writes to firewalled paths.
- The doctrine itself does NOT introduce new semantic categories beyond what already exists in the HELEN lexicon. Each emoji maps onto a concept already defined somewhere else.
- Per `NO RECEIPT = NO CLAIM`: no emoji ever carries a claim. The underlying text is the authoritative artifact.
- Per K-tau `mu_DETERMINISM`: same content + same palette rule = same emoji application. No model randomness in emoji choice.

---

## 9. Admission status

**DOCTRINE** — calibrated 2026-04-20 from operator direction. Not yet INVARIANT.

Promotion to INVARIANT requires:
- Second fresh session applies this palette to HELEN OS documentation without ambiguity
- `helen_say.py` receipt binding this document's SHA256 to the ledger
- K2 / Rule 3: the session that promotes must not be the session that authored

Until then: cite as "WULmoji enhancer doctrine v1, operator-calibrated 2026-04-20."

---

## 10. One-line summary

> WULmoji is the color grade, not the script. Words carry the claim; emoji carries the read.
