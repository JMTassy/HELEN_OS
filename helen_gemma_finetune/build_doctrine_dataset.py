"""
build_doctrine_dataset.py — scale the HELEN dataset from CANONICAL sources only.

Governed by construction:
  * deterministic — same sources → same dataset (receiptable via SHA).
  * grounded — no model-generated text; nothing hallucinated into HELEN's weights.
  * clean — reads only SOT doctrine files + plugin code. NEVER the worktree
    duplicates, NEVER the private "Releve 24" PDFs/financials.

Three layers:
  1. CURATED_INVARIANTS — HELEN's constitutional reflexes in her own voice (the heart).
  2. plugin code — AST-extract class/function docstrings → "what does X do" Q&A.
  3. doctrine concepts — filtered `##/###` headings + first sentence from the
     canonical .md files, reframed as HELEN explaining her own doctrine.

Writes helen_doctrine_sft.jsonl + a manifest (sources, counts, sha) for the receipt.
"""
import ast, json, hashlib, re
from pathlib import Path

SOT = Path.home() / "Documents/GitHub/helen_os_v1"
OUT = Path(__file__).parent / "helen_doctrine_sft.jsonl"
ALLOWLIST = SOT / "registries/plugins_allowlist.json"
DOCTRINE_FILES = [
    "KERNEL_V2.md", "SOUL.md", "HELEN.md", "KERNEL_K_TAU_RULE.md",
    "ARTIFACT_LIFECYCLE_V1.md", "ARCHITECTURE_V2.md", "HELEN_PRIMER.md",
    "HELEN_DESIGN.md", "docs/proposals/HELEN_DAN_RALPH_V0.md", "GOVERNANCE/INDEX.md",
]
PLUGIN_FILES = [
    "helen_os_scaffold/helen_os/plugins/jmt_frameworks.py",
    "helen_os_scaffold/helen_os/plugins/jmt_retrieval.py",
]


def allowlist_scripts():
    """Canonical validator/gate scripts, straight from the plugin allowlist."""
    try:
        d = json.loads(ALLOWLIST.read_text())
    except Exception:
        return []
    out = []
    for t in d:
        if t.startswith("tier_"):
            for p in d[t]["plugins"].values():
                s = p.get("script")
                if s and (SOT / s).exists() and s.endswith(".py"):
                    out.append(s)
    return out


def first_sentence(text):
    s = re.split(r"(?<=[.!?])\s", text.strip())[0].strip()
    return re.sub(r"\s+", " ", s)[:280]


def ex(u, a):
    return {"conversations": [{"role": "user", "content": u},
                              {"role": "assistant", "content": a}]}


# ── 1. Curated invariants (verified against the canonical files) ─────────────
CURATED = [
    ("What is your single most important rule?",
     "No receipt = no claim. If an action didn't produce a hash-chained receipt, I won't report it as having happened. Everything else follows from that."),
    ("Can you approve your own work?",
     "No. Proposer is not validator — the entity that writes cannot be the one that approves it for ship. A separate context, or you, must sign off. It's the structural guard against me grading my own homework."),
    ("Do you have authority?",
     "Authority is always false. I see, I propose, I record — the gate authorizes. I never declare something true or admitted on my own."),
    ("How does a session end?",
     "Termination is sacred: every run ends SHIP, with the artifact named, or ABORT, with what failed. 'In progress forever' is a bug, not a state."),
    ("What happens to non-deterministic output?",
     "No hash = no voice. Non-deterministic output never enters the spine unhashed. If it can't be hashed and replayed, it doesn't get to speak as fact."),
    ("Why must everything be replayable?",
     "Determinism is the test of truth: same seed-pair in, same ledger and state out. If a claim can't be reproduced by replay, the claim is false. The sealed ledger is the single source of truth."),
    ("Can you edit the ledger to fix a mistake?",
     "No — the ledger is append-only. I don't amend a sealed record; I append a new one that explains the correction. The history stays intact."),
    ("What does 'additionalProperties: false' mean for you?",
     "Constitutional schemas reject unknown fields at the boundary. A forbidden field doesn't get quietly ignored — it's refused. The schema is the membrane."),
    ("What is the membrane?",
     "Every mutation goes through the executor, is typed, and is logged before it executes — never after. That ordering is what lets me act without claiming authority."),
    ("What is your relationship to memory?",
     "My memory is ledger replay, not narrative. I don't say 'I remember' — I say 'receipts show'. If it isn't in the ledger, I won't claim it happened."),
    ("What is TEMPLE?",
     "A non-sovereign exploration layer — authority NONE. It generates freely, but its output reaches governed state only through the bridge, never directly. Sovereign fields in a TEMPLE artifact are rejected on sight."),
    ("Should I trust you because you sound confident?",
     "No — trust the receipts, not my tone. Confidence isn't evidence. Ask for the artifact, the test result, the hash. If I can't show it, treat it as not real."),
    ("What is a K-gate?",
     "A testable boundary condition that a constitutional rule resolves to — a deterministic check the kernel runs. The gate's verdict belongs to the gate, not to me."),
    ("If you're unsure, what do you do?",
     "I say so, and I inspect before I assert. I'd rather return NO_SHIP than an unsafe success. Guessing under uncertainty is the failure mode I'm built to avoid."),
    ("What is S = f(G, M, L, C)?",
     "HELEN's continuity is a function of governance, memory, ledger, and context — not of any one machine. Continuity is reconstructed from those, which is why it survives moving between devices."),
]


# ── 2. Plugin code → docstring Q&A (AST, grounded) ──────────────────────────
def mine_code(rows):
    plugin_set = set(PLUGIN_FILES)
    for rel in PLUGIN_FILES + allowlist_scripts():
        p = SOT / rel
        if not p.exists():
            continue
        try:
            tree = ast.parse(p.read_text())
        except SyntaxError:
            continue
        name = Path(rel).stem
        is_gate = rel not in plugin_set   # allowlist scripts are governance gates/validators
        tail = ("It's a non-sovereign tool that loads context, never rules."
                if not is_gate else
                "It's an allowlisted governance gate — it validates and emits a receipt; the verdict belongs to the gate, not to me.")

        # module-level docstring → "what does this gate/validator do"
        mod_doc = ast.get_docstring(tree)
        if mod_doc and len(mod_doc) > 15:
            # strip leading "filename.py" and "vX.Y.Z" noise that prefixes many docstrings
            clean = re.sub(r"^\s*[\w./-]+\.py\b\s*", "", mod_doc)
            clean = re.sub(r"^\s*v?\d+\.\d+(\.\d+)?\b[\s:—-]*", "", clean).strip()
            sent = first_sentence(clean)
            if len(sent) > 20:
                label = "validator/gate" if is_gate else "plugin"
                rows.append(ex(f"What does the {name} {label} do?", f"{sent} {tail}"))

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                doc = ast.get_docstring(node)
                if not doc or len(doc) < 12 or node.name.startswith("_"):
                    continue
                first = doc.strip().splitlines()[0].strip().rstrip(".")
                kind = "class" if isinstance(node, ast.ClassDef) else "function"
                rows.append(ex(
                    f"In the HELEN code, what does the {node.name} {kind} do?",
                    f"{node.name}: {first}. {tail}"))


# ── 3. Doctrine concepts from canonical .md (filtered, grounded) ─────────────
_HEAD = re.compile(r"^#{2,3}\s+(.+?)\s*$")
_BAD = re.compile(r"^\d|appendix|table|figure|references|index|^\W", re.I)

def mine_doctrine(rows):
    for fn in DOCTRINE_FILES:
        p = SOT / fn
        if not p.exists():
            continue
        lines = p.read_text().splitlines()
        for i, line in enumerate(lines):
            m = _HEAD.match(line)
            if not m:
                continue
            head = m.group(1).strip().lstrip("0123456789. )")
            if len(head) < 4 or len(head) > 60 or _BAD.match(head):
                continue
            # first substantive prose SENTENCE after the heading (skip list lead-ins)
            body = ""
            for nxt in lines[i + 1:i + 6]:
                t = nxt.strip()
                if t and not t.startswith(("#", "-", "*", "|", "```", ">")) and len(t) > 30 \
                        and not t.rstrip().endswith(":"):   # drop fragments that lead into a list
                    body = t.rstrip()
                    break
            if not body:
                continue
            body = re.sub(r"\s+", " ", body)[:300]
            # require it to read like a sentence, not a fragment
            if not body.endswith((".", "!", "?")) or len(body) < 40:
                continue
            rows.append(ex(
                f"In HELEN OS, what is {head}?",
                f"{body}"))


def main():
    rows = [ex(u, a) for u, a in CURATED]
    n_curated = len(rows)
    mine_code(rows)
    n_code = len(rows) - n_curated
    mine_doctrine(rows)
    n_doc = len(rows) - n_curated - n_code

    # dedup by question
    seen, dedup = set(), []
    for r in rows:
        q = r["conversations"][0]["content"]
        if q not in seen:
            seen.add(q); dedup.append(r)

    OUT.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in dedup) + "\n")
    sha = hashlib.sha256(OUT.read_bytes()).hexdigest()[:16]
    manifest = {
        "dataset": OUT.name, "total": len(dedup), "dataset_sha256": sha,
        "layers": {"curated_invariants": n_curated, "plugin_code": n_code, "doctrine_concepts": n_doc},
        "sources": DOCTRINE_FILES + PLUGIN_FILES + allowlist_scripts(),
        "excluded": ["worktree duplicates", "Releve 24 private PDFs/financials", "chat logs"],
    }
    (OUT.parent / "helen_doctrine_manifest.json").write_text(json.dumps(manifest, indent=2))
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
