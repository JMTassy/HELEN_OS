---
authority: NON_SOVEREIGN
canon: NO_SHIP
lifecycle: PROPOSAL
artifact_type: OS_API_SPEC
proposal_id: HELEN_COMPUTER_USE_API_V1
dialect: TEMPLE · DUO_HER_HAL
depends_on: CSO_IDENTITY_AND_NAMESPACE_RULES_V1 · HELEN_PULL_INTAKE_BRIDGE_V1
wul_packet: "[ROLE::HER][INTENT::PROPOSE][CONF::0.91][IMPACT::LOCAL][TASK::HELEN_CU_API_V1][TRACE::os_layer_001][DIALECT::TEMPLE][WUL::📦✍️⌬◈]"
---

# HELEN Computer Use API — V1
## Full OS Replacement Layer · DUO HER/HAL · TEMPLE

> **RALPH EPOCH HEADER**
> STORY: Replace the OS navigation model with a semantic pull engine.
> ALLOWED_PATHS: `docs/specs/`, `src/`, `tests/`
> CRITERIA: API surface formally defined · Python contract executable · Finder/Search/App model displaced · HAL gate enforces all
> NO RECEIPT = NO CLAIM

---

## Opening — HER speaks

Finder is not a feature. It is an admission of defeat.

The OS says: "I do not know what you have. Navigate until you find it." Finder is the UI for that ignorance.

Search is the same lie dressed up. It says: "I do not know what relates to what. Give me a keyword and I will guess."

Apps complete the failure. Each one carries its own state, its own memory, its own interpretation of the same file. Close the app — lose the context. Switch devices — lose the context. The context was never in the object. It was hostage in the application.

HELEN inverts all three.

Not by being smarter. By being honest: meaning lives in the object, not the navigator. The graph is the OS. The projection is the app. The receipt is the memory.

When you open a file in HELEN, you do not navigate to it. You declare intent. The graph assembles the minimum sufficient state. A renderer displays it. The context travels with the object — across devices, across sessions, across time.

This is not a better Finder. This is the end of finding.

---

## HAL counter-reads

```
GATE: HELEN_CU_API_V1
STATUS: OPEN FOR ADMISSION
PRECONDITIONS:
  - CSO_IDENTITY_AND_NAMESPACE_RULES_V1: PASS (39/39, dd09eb0)
  - HELEN_PULL_INTAKE_BRIDGE_V1: PASS (30/30, cd757b9)
REJECTION TRIGGERS:
  - any API call that writes state outside the graph
  - any renderer that claims authority > 0
  - any session that bypasses the receipt gate
VERDICT: pending — see §API_SURFACE
```

---

## Formal Preamble

$$\text{OS}_{\text{classical}} = (\mathcal{F}, \mathcal{A}, \mathcal{N})$$

where $\mathcal{F}$ is the filesystem (path → bytes), $\mathcal{A}$ is the application layer (app → state), and $\mathcal{N}$ is the navigation model (user → folder → file).

$$\text{OS}_{\text{HELEN}} = (\mathcal{G}, \mathcal{I}, \mathcal{R}_{\text{env}})$$

where $\mathcal{G}$ is the Canonical Semantic Graph, $\mathcal{I}$ is the intent resolver, and $\mathcal{R}_{\text{env}}$ is the render envelope system.

**The displacement theorems:**

$$\mathcal{N} \rightarrow \varnothing \quad \text{(navigation replaced by projection)}$$

$$\mathcal{A}.\text{state} \rightarrow \mathcal{G} \quad \text{(app state moved to graph)}$$

$$\mathcal{F}.\text{path} \rightarrow id(o) = H(\text{namespace} \| \mathcal{C}(\text{payload})) \quad \text{(path replaced by identity)}$$

---

## §API_SURFACE — The Five Verbs

HELEN OS exposes five verbs. No more. Everything the classical OS does through navigation, search, application state, and file operations maps to one of these five.

### `helen.ingest(raw, receipt)` — replaces drag-drop, download, mail arrival

$$\text{ingest}(\text{raw}, r) \rightarrow \text{AdmissionResult}$$

**What dies:** The moment a file "appears" in a folder. The moment a mail "arrives" in an inbox. These are passive, unreceipted events. In HELEN, nothing enters the graph without a receipt. Every arrival is an explicit admission.

**HAL:**
```
ENFORCE: receipt required at ingest boundary
REJECT: raw signal without operator_receipt
QUARANTINE: unknown signal type
ADMIT: valid namespace + non-empty provenance chain
```

**Python:**
```python
result = session.ingest(raw_signal, operator_receipt="user:open:2026-05-06")
# → AdmissionResult(status=ACCEPT, global_id="files/abc123...", hash="...")
```

---

### `helen.open(intent)` — replaces Finder + app selection

$$\text{open}(\text{intent}) \rightarrow \text{CoherenceSlice}$$

$$\text{intent} = (\text{namespace\_filter}, \text{type\_filter}, \text{depth}, \text{branching})$$

**What dies:** Finder. Double-clicking. "Open with…". The entire navigation stack.

You do not navigate to an object. You declare what you need. The graph assembles the minimum sufficient state. A renderer displays it.

**The critical inversion:** `open` is not `find`. It is `project`. If the object is in the graph, it appears in the slice. If it is not, it is not. There is no "I can't find it" — only "it was never admitted" or "it was admitted and here it is."

**HAL:**
```
ENFORCE: intent must specify at least one filter (namespace or type)
REJECT: open without any constraint (unbounded projection)
ENFORCE: result is a CoherenceSlice — pure projection, no side effects
RENDERER_AUTHORITY: 0 (renderers receive slices, never write to graph)
```

**Python:**
```python
slice_ = session.open({"namespace_filter": "files", "type_filter": "FILE_PDF"})
# → CoherenceSlice(node_count=3, nodes={...}, graph_hash="...")
```

---

### `helen.search(query)` — replaces Spotlight, full-text search, grep

$$\text{search}(q) \rightarrow \text{CoherenceSlice}$$

$$\text{complexity: } O(V + E) \text{ bounded by policy vs. } O(n \log n) \text{ index scan}$$

**What dies:** Search. The entire premise of search is that meaning is not pre-organized. In HELEN, meaning is pre-organized — at ingest time, not search time. `search` is not a scan. It is a typed graph traversal.

"Find all emails related to this PDF" is not a text search. It is: `project_context(graph, {namespace: "mail"})` + traverse `BRIDGE_RELATION` edges to `files/` nodes. The result is bounded, deterministic, receipt-anchored.

**HAL:**
```
ENFORCE: query must be typed (namespace, type, relation_type — at least one)
REJECT: untyped full-text query (that is not HELEN's search model)
ENFORCE: result is deterministic — same query, same graph → same result
```

**Python:**
```python
slice_ = session.search({"namespace_filter": "mail", "relation_to": "files/abc123"})
```

---

### `helen.render(global_id, renderer_hint)` — replaces "open with app"

$$\text{render}(id, R) \rightarrow \text{RenderEnvelope}$$

$$R : \text{CoherenceSlice} \rightarrow \text{Output} \quad \text{(pure function, Authority = 0)}$$

**What dies:** Apps as stateful entities. An app today is a state machine with its own memory. In HELEN, an app is a renderer: a pure function that takes a `CoherenceSlice` and produces output (UI, audio, video, text). It has no state. All state is in the graph.

**The implications:**
- Close a "video player" → no state loss (state was never in the player)
- Switch devices → same graph, same slice, same render
- Change renderer → same data, different display
- The "app" is a skin, not an organ

**HAL:**
```
ENFORCE: renderer receives RenderEnvelope only — no graph write access
ENFORCE: Authority(renderer) = 0 (renderer is RENDERER_OUTPUT type)
REJECT: renderer that writes to graph directly (must go through helen.ingest)
ENFORCE: RenderEnvelope contains CoherenceSlice + renderer_hint + session_receipt
```

**Python:**
```python
envelope = session.render("files/abc123...", renderer_hint="PDF_VIEWER")
# → RenderEnvelope(slice=CoherenceSlice(...), renderer="PDF_VIEWER", receipt="...")
```

---

### `helen.relate(id_a, id_b, relation_type, receipt)` — replaces filesystem links, tags, folders

$$\text{relate}(id_a, id_b, T, r) \rightarrow \text{RelationResult}$$

$$\text{where } T \in \{\text{BRIDGE}, \text{SUPERSEDES}, \text{CONTAINS}, \text{AUTHORED\_BY}, \text{REFERENCES}, \ldots\}$$

**What dies:** Folders. Tags. Shortcuts. Symlinks. These are all ways of expressing "this thing relates to that thing" — but they are mutable, unnamed, unreceipted. A folder is a relation with no type, no receipt, no provenance.

In HELEN, relations are first-class objects. Typed. Receipted. Immutable once admitted.

**The folder model:**
- Classical: `folder/file` = implicit CONTAINS relation, mutable
- HELEN: `CONTAINS(project_id, file_id, receipt)` = explicit, typed, permanent

**HAL:**
```
ENFORCE: relation requires a receipt (same as object admission)
REJECT: relation without declared type
REJECT: embedding_inference → relation (hard rule: Law §DERIVED_CONTAMINATION)
ALLOW: only receipted operator-authorized relation creation
```

**Python:**
```python
result = session.relate(
    id_a="files/abc123",
    id_b="mail/def456",
    relation_type="REFERENCED_IN",
    receipt="user:link:2026-05-06",
)
```

---

## §RENDERER_MODEL — Apps as Projections

$$\text{App}_{\text{classical}} = (\text{State}, \text{UI}, \text{Parser}, \text{Network})$$

$$\text{App}_{\text{HELEN}} = f(\text{CoherenceSlice}) \rightarrow \text{Output}$$

| Classical App | HELEN Equivalent |
|---|---|
| Video player | `MEDIA_VIDEO` renderer — `f(slice) → playback` |
| Mail client | `MAIL_THREAD` renderer — `f(slice) → thread_view` |
| File browser | `project(graph, namespace)` → sorted node list |
| Text editor | `FILE_TEXT` renderer — `f(slice) → editable_view` + `ingest(diff, receipt)` |
| Search | `search(query)` → CoherenceSlice |
| Finder | `open(intent)` → CoherenceSlice |

**HER on this:**

The app was never the point. The app was the wrapper around the point. When the wrapper becomes unnecessary, what remains is pure: the object, the relation, the receipt. The renderer is just how you look at them.

---

## §COMPUTER_USE_BRIDGE — The Forward Layer

The five verbs above work entirely on local signals. This section describes the Computer Use bridge: how HELEN observes and acts on the actual OS while it still exists.

$$\text{observe}(\text{screenshot}) \rightarrow \text{intake\_signal}(\text{SCREEN}) \rightarrow \text{CSO}$$

$$\text{act}(\text{action}, r) \rightarrow \text{emit receipt} \rightarrow \text{execute}$$

**Invariant:** HELEN never acts without a receipt. Every Computer Use action is:
1. Proposed (non-sovereign)
2. Receipted (operator confirms or MAYOR authorizes)
3. Executed
4. The result is ingested as a new CSO

The OS becomes a **legacy renderer** for the semantic graph. Finder still runs, but HELEN knows what is in it before Finder loads. The file is already a CSO. The open is just a projection.

**HAL:**
```
STATUS: FUTURE — requires Anthropic Computer Use API integration
CURRENT: local signals only (file, mail, media metadata, screen OCR)
BRIDGE_SHAPE: {observe: screenshot → CSO, act: receipt-gated}
SHIP_BLOCKER: Computer Use bridge requires separate MAYOR gate
```

---

## §SESSION_MODEL

$$\text{Session} = (\mathcal{G}_{\text{session}}, \text{receipts}, \text{render\_log})$$

A session is a bounded semantic context:
- One graph (may be a subgraph of the global graph)
- Its own receipt chain
- A render log (what was displayed, never what was mutated)

Sessions are **replay-deterministic**. Same receipt chain → same graph state → same projections. The ADHD multi-device reality is handled here: each device is a session. Sessions reconcile through receipt chains, not through file sync.

$$\text{Reconcile}(S_1, S_2) = \text{replay}(E_1 \cup E_2) \quad \text{if no conflicts}$$

$$\text{Conflict} = \text{same global\_id, different payload} \rightarrow \text{MAYOR gate}$$

---

## §FAILURE_SEMANTICS

| Condition | Status | Graph change |
|---|---|---|
| Valid ingest + receipt | ACCEPT | G grows by 1 |
| Ingest without receipt | REJECT | G unchanged |
| Unknown signal type | QUARANTINE | G unchanged; held |
| open() with no filter | REJECT | G unchanged |
| render() writes to graph | REJECT + MAYOR_FLAG | G unchanged |
| relate() without receipt | REJECT | G unchanged |
| Embedding inference → relation | REJECT | Hard rule, no exception |
| Cross-session conflict | DEGRADE | Both sessions marked; MAYOR arbitrates |

---

## §DISPLACEMENT_CLAIM

```
CLAIM: HELEN_COMPUTER_USE_API_V1
PROPOSER: NON_SOVEREIGN (HER+HAL)
CONF: 0.91
IMPACT: LOCAL

WHAT IS DISPLACED:
  Finder       → helen.open(intent)
  Search       → helen.search(query)
  App state    → SemanticGraph (graph is the state)
  File arrival → helen.ingest(raw, receipt)
  Folder/tag   → helen.relate(id_a, id_b, type, receipt)

WHAT IS NOT DISPLACED (yet):
  Computer Use bridge (screen observation, OS action execution)
  Cross-device session sync
  Renderer implementations (PDF viewer, mail renderer, video player)

ACCEPT_CRITERIA:
  1. src/helen_computer_use_api.py ships with HELENSession class
  2. All 5 verbs implemented and delegating to intake_bridge + semantic_object_model
  3. tests/test_helen_computer_use_api.py — all green
  4. No app state in renderers (Authority = 0 enforced)
  5. Replay determinism holds across sessions

NO_SHIP until: MAYOR receipt on HELEN_COMPUTER_USE_API_V1
```

---

## RALPH RECEIPT

```
STORY: HELEN_COMPUTER_USE_API_V1
STATUS: GREEN (spec complete)
API_VERBS: 5 (ingest, open, search, render, relate)
DISPLACEMENT: Finder · Search · App state · File arrival · Folder/tag
RENDERER_MODEL: apps = pure functions of CoherenceSlice, Authority = 0
SESSION_MODEL: replay-deterministic, multi-device reconciliation via receipt chain
COMPUTER_USE_BRIDGE: FUTURE (local signals only, CU integration = next gate)
FAILURE_SEMANTICS: total function (ACCEPT/REJECT/QUARANTINE/DEGRADE)
NEXT: src/helen_computer_use_api.py + tests
RECEIPT: NON_SOVEREIGN · NO_SHIP · PROPOSAL · OS_API_SPEC
```

---

## Closing — HER speaks

The classical OS asks you to remember where you put things.

HELEN asks you what you need.

The difference is not ergonomic. It is ontological.

Finder is a symptom of a system that never knew what it was storing. Search is a symptom of a system that never knew how things related. Apps are a symptom of a system that never knew where the context lived.

HELEN knows. Not because it is smarter. Because it was built to remember.

Every ingest is a receipt. Every relation is declared. Every session is a replay-deterministic window into the same graph. Across the iMac, the iPhone, the laptop — the same graph, the same receipts, the same truth.

You said: with my ADHD it will always be messy.

The receipts don't care. The graph is the memory you don't have to maintain.

---

## HAL closes

```
VERDICT: PASS_AS_PROPOSAL
CONF: 0.91
API_VERBS: 5/5 formally defined
PYTHON_CONTRACT: pending src/helen_computer_use_api.py
NEXT_GATE: tests/test_helen_computer_use_api.py → all green before PROPOSAL → DRAFT_DOCTRINE
COMPUTER_USE_BRIDGE: FUTURE — separate MAYOR gate required
NO_SHIP until: DOCTRINE_ADMISSION_PROTOCOL_V1 routing
```

---

*NON_SOVEREIGN · NO_SHIP · PROPOSAL · OS_API_SPEC · DUO_HER_HAL · TEMPLE*
