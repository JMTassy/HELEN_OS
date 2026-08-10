# PORTED ARTIFACTS — PROVENANCE MANIFEST

🧾 STATUS: PORTED COPIES — NON_SOVEREIGN · authority=NONE · not admitted · not wired
Ported 2026-08-10 during Phase 0 consolidation (operator verb: COMMIT).
Source worktrees are ephemeral mirrors; these copies exist to end mirror drift.
Imports are NOT rewritten — wiring into the kernel is a separate lane with its own tests.

## Sources

| Key | Source surface | Branch |
|---|---|---|
| practical-mirzakhani | `~/Desktop/JMT CONSULTING - Releve 24/.claude/worktrees/practical-mirzakhani` | claude/practical-mirzakhani (clean at port time) |
| dreamy-shannon | `~/Desktop/JMT CONSULTING - Releve 24/.claude/worktrees/dreamy-shannon` | claude/dreamy-shannon (dirty at port time) |
| root | `~/Desktop/JMT CONSULTING - Releve 24` | docs/helen-chat-modes (dirty at port time) |

## Keeper rationale (from Phase 0 dual-goblin inventory)

- **helen_knowledge_registry.json** (practical-mirzakhani) — ONLY copy in existence; 57 KB salience/stance corpus. Rescue was the priority of this port.
- **assemble_context_packet.py** — practical-mirzakhani impl kept (fullest, 2026-03-19); dreamy-shannon variant kept alongside for test-union work. Material 71-line diff — reconcile in wiring lane.
- **test_assemble_context_packet.py** — BOTH kept (18 fns practical / 23 fns dreamy); wiring lane merges to union suite.
- **Five judgment skills + base.py** (dreamy-shannon) — authority=NONE contract layer; only complete copy.
- **init_helen_wedge.py** (practical-mirzakhani) — newer than root copy by mtime.
- **avatar_config.json / helen_storage_init.js** — byte-identical root/practical; practical taken.
- **HELEN_AGENT_STACK_V1.md / HELEN_FULL_RECAP_V1.md** — session doctrine docs, 🧾 OBSERVED status only.
- **dirty_logs_10_sessions.jsonl** (root) — replay chaos fixture.

## SHA-256 manifest (at port time)

```
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  dreamy-shannon/helen_city/skills/__init__.py (empty)
308050e2bb90860681df5eb2c277da5412ffa21eee8b21316b3a36fa6a53b517  dreamy-shannon/helen_city/skills/assemble_context_packet.py
cbe70be398b188d06581b8db9801b4071eab7bdeb192df1a6f73177d773b9acb  dreamy-shannon/helen_city/skills/base.py
275b6ec20a930bfc251ad6bb1bb760dc1cc28178994aaf4e57ab4171f4594d0b  dreamy-shannon/helen_city/skills/retrieve_district_law.py
7f55eb49a7bcdf71bcd0e0add232a107c1b29135cb21d1828393c7fb6b44d2b2  dreamy-shannon/helen_city/skills/retrieve_project_profile.py
5552fe93686390ba059d63ec441deb17698a440ff6c62323698367a81ec8a22e  dreamy-shannon/helen_city/skills/retrieve_research_topic.py
9f339f288a2022190a8051e8fc17c17373628e0fb3ba3023b239edf7b0d93474  dreamy-shannon/helen_city/skills/suggest_next_action.py
f2d8780716678e9fed8fd9c09926f7f2f619001f519699f53c45da4fd25b0d9d  dreamy-shannon/helen_city/skills/summarize_active_thread.py
174f4aa5fa2a6d74b438ce054555b88ce053ece4a9b7e46b6d94832f7c37cd1a  dreamy-shannon/helen_city/tests/test_assemble_context_packet.py
3d6c3b654b4ed153aaf57c81c2f7b694fab5505c3079aa8189afde7c24b8cd2d  dreamy-shannon/HELEN_FULL_RECAP_V1.md
5fe3dc4a3261cb0e0eb59fcf26b8d6e36b1a80a69216e60d43bfb9c4777fbd97  practical-mirzakhani/HELEN_AGENT_STACK_V1.md
69070f25dc60746508d631f767c4f047536829098bf14020feddb51f6239356f  practical-mirzakhani/helen_city/knowledge/assemble_context_packet.py
a57e87492cf2c349bd1f1cf7e3b1906921aa3c82794d4a50268891c0051cd633  practical-mirzakhani/helen_city/memory/knowledge/helen_knowledge_registry.json
faab796717582c09f2c55b468af52d83325c3c7325382cfcf5c56dc834c8515d  practical-mirzakhani/helen_city/tests/test_assemble_context_packet.py
50ea4109eca265376ae983b3714cade04b1d01092149c793c74759c9a39d3aae  practical-mirzakhani/helen_os/api/init_helen_wedge.py
183bd7fdc2d1d2301d3c45dd7e9e1b09eb293eaad553a01d9fb8149ac1b62377  practical-mirzakhani/helen_os/config/avatar_config.json
b94b43957af129894c18da00f7c32f4213f3429f9e7e437834b91b72b31ce4a0  practical-mirzakhani/helen_os/config/helen_storage_init.js
c170ce5d27feffe44638cebc9b26b837ac96033f70b02ed21f73fba5d5c1054c  root/helen_os/test_fixtures/dirty_logs_10_sessions.jsonl
```

Mirror discipline: source worktrees were READ, never edited. They remain on disk untouched.
