#!/usr/bin/env python3
"""
CORPUS_CENSUS_V0 — Layer 0 ONLY: PHYSICAL + CONTENT DISCOVERY.

Answers exactly one question: what material physically exists, and which
byte-identical representations collapse to the same CONTENT identity?

  Filesystem → ArtifactInstances → ContentEquivalenceClasses [f]_C   (f_i ~_C f_j ⇔ H(f_i)=H(f_j))

THREE IDENTITIES KEPT SEPARATE (never conflated):
  artifact_instance_id   this physical occurrence (path)
  content_hash           byte identity — H(bytes)
  provenance_root_id     UNKNOWN at Layer 0 (needs an explicit witness)

HARD LAW (learned the hard way):
  ContentIdentity ≠ ProvenanceRootIdentity
  duplicate-path collapse ≠ provenance-root resolution   ⇒ PROVENANCE_ROOTS_ASSIGNED = 0

Buckets are CANDIDATE_* proposed types from a lexical head-scan — NOT epistemic types.
Tie-break "speculation wins ties" = conservative quarantine policy, not ontology.
NO ingestion · NO training · NO model call · authority=false · canon=false · ΔA=0 · NO_CLAIM.
"""
import hashlib, json, os
from pathlib import Path

ROOTS = [
    "/Users/jean-marietassy/Documents/GitHub/helen_os_v1/temple",
    "/Users/jean-marietassy/Downloads/CHRONOS",
    "/Users/jean-marietassy/Desktop/PLUGINS_JMT",
    "/Users/jean-marietassy/Desktop/JMT CONSULTING - Releve 24",
]
EXTS = {".md", ".txt", ".pdf"}
EXCLUDE = ("/node_modules/", "/.git/", "/.venv/", "/__pycache__/", "/site-packages/")
MAXDEPTH, HEAD = 4, 20000

KEEP = ["receipt","replay","witness","reducer","append-only","provenance","falsifier",
        "no_claim","authority=false","δa","determinist","trace","admission","no receipt",
        "proposer","validator","idempotent","root-census","membrane","seam","birth test","day_one"]
PROTO = ["grammar","parser","whitelist","allowlist","wulmoji","conquest","runtime","glyph",
         "schema","opcode","canon8k","deterministic simulation","state machine","tokenizer",
         "spec","parsed act","typed effect"]
GARDEN = ["confirmed","detected","measured","quantum","11-dimension","11d","consciousness",
          "multiverse","reality matrix","godmode","hyperstition","cosmolog","sentient","akashic",
          "vortic","faster-than-light","dark matter","superposition","egregore","oracle town",
          "chronos","cielo","magick","ritual","chaos magick","unified theory","vacuum energy"]


def score(text, lex):
    t = text.lower(); return sum(t.count(k) for k in lex)


def classify(path):
    p = Path(path); content = ""; unread = False
    if p.suffix.lower() in (".md", ".txt"):
        try: content = p.read_text(errors="replace")[:HEAD]
        except Exception: unread = True
    else:
        unread = True                                   # pdf/binary: filename-only
    try: content_hash = hashlib.sha256(p.read_bytes()).hexdigest()[:16]   # CONTENT id, NOT a root
    except Exception: content_hash = "unreadable-" + hashlib.sha256(p.name.encode()).hexdigest()[:8]
    blob = p.name + "\n" + content
    k, pr, g = score(blob, KEEP), score(blob, PROTO), score(blob, GARDEN)
    if g > 0 and g >= k and g >= pr: bucket = "CANDIDATE_GARDEN_SPEC"   # quarantine policy
    elif k > 0 and k >= pr:          bucket = "CANDIDATE_KEEP_TRAIN"
    elif pr > 0:                     bucket = "CANDIDATE_PROTOCOL"
    else:                            bucket = "UNTYPED"
    return {"artifact_instance": str(p), "name": p.name, "ext": p.suffix.lower(),
            "content_hash": content_hash, "provenance_root_id": "UNKNOWN",
            "keep": k, "proto": pr, "garden": g, "content_unread": unread, "candidate_bucket": bucket}


def walk(root):
    root = Path(root)
    if not root.exists(): return []
    out, base = [], len(root.parts)
    for dp, dns, fns in os.walk(root):
        if any(x in dp + "/" for x in EXCLUDE) or len(Path(dp).parts) - base > MAXDEPTH:
            dns[:] = []; continue
        for f in fns:
            if Path(f).suffix.lower() in EXTS or f.startswith("#plugin"):
                out.append(os.path.join(dp, f))
    return out


def main():
    paths = sorted({f for r in ROOTS for f in walk(r)})
    rows = [classify(f) for f in paths]

    # content-equivalence classes [f]_C — this is CONTENT collapse, NOT provenance resolution
    by_content = {}
    for r in rows: by_content.setdefault(r["content_hash"], []).append(r)
    reps = [v[0] for v in by_content.values()]          # one representative per content class
    dup_groups = sum(1 for v in by_content.values() if len(v) > 1)

    def count(bucket, over): return sum(1 for r in over if r["candidate_bucket"] == bucket)
    fmts = {}
    for r in rows: fmts[r["ext"]] = fmts.get(r["ext"], 0) + 1
    readable = sum(1 for r in rows if not r["content_unread"])

    block = {
        "CORPUS_CENSUS_V0": "Layer 0 (physical + content discovery only)",
        "PHYSICAL_PATHS": len(rows),
        "UNIQUE_CONTENT_HASHES": len(by_content),
        "BYTE_DUPLICATE_GROUPS": dup_groups,
        "FORMATS": fmts,
        "READABLE_TEXT": readable,
        "CONTENT_UNREAD": len(rows) - readable,
        # candidate buckets counted over CONTENT classes (not paths) so duplication can't inflate them
        "CANDIDATE_KEEP_TRAIN": count("CANDIDATE_KEEP_TRAIN", reps),
        "CANDIDATE_PROTOCOL": count("CANDIDATE_PROTOCOL", reps),
        "CANDIDATE_GARDEN_SPEC": count("CANDIDATE_GARDEN_SPEC", reps),
        "UNTYPED": count("UNTYPED", reps),
        "PROVENANCE_ROOTS_ASSIGNED": 0,
        "EVIDENCE_ROOTS_ASSIGNED": 0,
        "TRAINING_STARTED": False,
        "INGESTION_STARTED": False,
        "AUTHORITY": False, "CANON": False, "LEDGER_EFFECT": "none",
    }
    print("═" * 62)
    for k, v in block.items(): print(f"  {k:26s} = {v if not isinstance(v, dict) else json.dumps(v)}")
    print("═" * 62)
    print("  law: ContentIdentity ≠ ProvenanceRootIdentity ·"
          " duplicate-path collapse ≠ provenance-root resolution")

    receipt = {"schema": "CORPUS_CENSUS_V0", "layer": 0,
               "provenance_boundary": "files-on-disk ≠ live Drive crawl",
               "identities_kept_separate": ["artifact_instance", "content_hash", "provenance_root_id(UNKNOWN)"],
               "status": block,
               "content_classes_over_1": {h: [r["name"] for r in v]
                                          for h, v in by_content.items() if len(v) > 1},
               "candidate_rows": rows}
    (Path(__file__).resolve().parent / "CORPUS_CENSUS_V0.json").write_text(
        json.dumps(receipt, indent=2, ensure_ascii=False))
    print("  → CORPUS_CENSUS_V0.json  (per-instance content_hash + candidate_bucket; roots UNKNOWN)")


if __name__ == "__main__":
    main()
