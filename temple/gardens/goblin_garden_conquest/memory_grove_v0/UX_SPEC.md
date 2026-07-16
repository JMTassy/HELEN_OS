# Memory Grove v0 — UX Spec (proposal only)

```
authority: false
canon: false
ledger_effect: none
claim_status: NO_CLAIM
final: HOLD_FOR_OPERATOR
layer: render/game only
```

## 0. One-line promise

When Lulu (or any goblin) **teaches or learns** something in the Warren,
the world grows **one visible memory object** in the Memory Grove —
a seed, lantern, moss mark, bug label, or tiny shrine —
always showing **where it came from**, never claiming truth.

> Memory can bloom. Truth is still earned.

## 1. Why this slice

Progression v0 fixed the silent wall (mystery dead-end / reload).
The next enrichment is not more systems — it is **the feeling that the world was listening**.

Memory Grove connects:

| Thread | How Grove carries it |
|--------|----------------------|
| Lulu as mini-HELEN | She plants the first objects when she teaches |
| Learning | Each teach/learn event → one object |
| Receipts-as-tokens | Object = game token bound to a **source event** |
| Compost | Compost = failed ideas; Grove = **kept lessons** (still non-truth) |
| Emotional return | Returning players see the same grove (deterministic) |

## 2. Scope (hard membrane)

| Allowed | Forbidden |
|---------|-----------|
| Render / HTML / local JSON / `localStorage` | `town/ledger_v1.ndjson` |
| Garden scratch paths | `oracle_town/kernel/**` |
| Client-only replay of grove state | Reducer / MAYOR / admission verbs |
| Visual “remembered here” language | ADMITTED / CANON / SHIP / truth claims |
| Deterministic layout from event ids | Wall-clock-only placement (non-replayable) |

## 3. Player experience

### 3.1 Where it lives

- **Zone:** soft corner of **Rootglow Grove** (or a quiet strip beside Lulu’s tree in the crib).
- **Not** a new top-bar system. **Not** a sixth menu.
- First object appears with a single soft cue: a heart-spark + Lulu line  
  *“I kept that. Look — the Grove grew.”*
- After that, a small **Grove glyph** (🌱) in the corner of the stage opens the grove panel.

### 3.2 Core loop (rungs, not systems)

```
Notice → Act → Response → Memory (GROVE GROWS) → Return
```

| Moment | What player sees |
|--------|------------------|
| Teach/learn fires | Soft plant animation (0.4–0.8s squash-and-settle) |
| Object lands | Deterministic slot lights; object glyph appears |
| Tap object | Card: **lesson** + **source event** (who / what / when-in-session) |
| Return next session | Same objects, same slots — no shuffle |

### 3.3 Object kinds (visual vocabulary)

| kind | glyph | Feels like | Planted when… |
|------|-------|------------|----------------|
| `seed` | 🌱 | First hope | First lesson with a goblin |
| `lantern` | 🏮 | Kept light | Goblin explains something player can reuse |
| `moss_mark` | 🍃 | Quiet scar of attention | Player notices + names a pattern |
| `bug_label` | 🐛 | Named glitch as friend | A bug is **named** (not fixed as truth) |
| `tiny_shrine` | ⛩ | Gratitude | Player returns and the grove still holds a lesson |

Max **12 objects** on screen in v0 (overflow → compact “older moss” stack; data still kept).

### 3.4 Source event is mandatory UI

Every object card **must** show a **Source** block:

```
SOURCE EVENT
  actor:    Lulu
  type:     teach
  summary:  “Our first bloom is a promise to come back.”
  session:  crib_rung_2
  event_id: evt_…
```

No object without source. Missing source → object does not plant (fail closed in render).

### 3.5 Language law (anti false-green)

| Say | Never say |
|-----|-----------|
| remembered here | admitted |
| grown from | sealed / canon |
| kept in the grove | ledger wrote |
| local to this device | proven true |
| HOLD for you | SHIP / truth |

### 3.6 Empty & first states

- **Empty:** dim soil, soft copy: *“The grove waits for a lesson.”*
- **First plant:** camera nudge / vignette breathe; Lulu line; progress-compatible (does not steal crib dots).
- **Full (12):** new plants animate into “moss stack”; oldest stay inspectable via list.

### 3.7 Interaction budget (one gesture class)

Aligned with One-Gesture Consumption spirit (proposal only, not implemented here):

| Gesture | Grove meaning |
|---------|----------------|
| Tap object | Inspect (source card) |
| Long-press object | “Whisper” — Lulu re-speaks the lesson (no new object) |
| Drag object | Not in v0 (parked) |

### 3.8 Determinism contract (return feel)

Grove state is a **sorted append-only list** of grove objects in client storage:

1. Identity of an object = `sha256(canon(source_event.event_id + kind + actor))[:16]`
2. Slot index = `hash_to_slot(object_id, capacity=12)` — pure function, no `Date.now()` for position
3. Reload / return → rehydrate from storage → re-render same layout
4. Optional `session_seq` for display order among same-slot collisions (stable secondary key)

Wall clock may appear as **display label only** if present; never as layout seed.

## 4. Wiring surface (proposal — not implementing)

| Source event (render) | Default kind |
|-----------------------|--------------|
| Crib first bloom (rung 2) | `seed` |
| Crib return memory (rung 3) | `tiny_shrine` |
| Lulu teaches after quiz-correct | `lantern` |
| Named bug in Bug Nursery | `bug_label` |
| Player inspects compost extract | `moss_mark` |

Hook shape (illustrative):

```js
// render layer only — never import sovereign writers
plantGroveMemory({
  kind: "seed",
  actor: "Lulu",
  event_type: "teach",
  summary: "Our first bloom is a promise to come back.",
  session_key: "crib_rung_2",
  event_id: "evt_crib_first_bloom_v0"
});
```

## 5. Explicit non-goals (v0)

- No multiplayer sync
- No server authority
- No doctrine promotion from grove objects
- No auto-plant on every UI click (only **teach / learn / name / return-memory** classes)
- No “memory score” gamifying admission

## 6. Success criteria (human contact)

A cold first-time player who finishes the crib can:

1. See at least **one** grove object without opening a menu maze.
2. Tap it and read **who** taught and **what** was kept.
3. Leave and return (same browser profile) and still see that object in the **same place**.
4. Never read a sentence that sounds like the ledger moved.

## 7. Relation to other doors

| Door | Relation |
|------|----------|
| Bug Nursery | `bug_label` objects are the soft bridge |
| Lulu’s Almanac | Almanac **pages** can list grove objects for a day |
| Dark Lantern | Unverified glow ≠ grove plant; grove only plants **named local events** |
| Compost Garden | Compost = discarded → extract; Grove = **kept lesson tokens** |
| Council Hand-Off | Grove does not show gate verdicts; only teach/learn |

---

*proposal ⊬ admission · render ⊬ truth · memory can bloom · ledger sleeps*
