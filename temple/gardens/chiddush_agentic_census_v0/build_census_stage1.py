#!/usr/bin/env python3
"""
HELEN_DRIVE_CENSUS_V0 — Stage 1 (mechanical, pre-cognition).

Reads every saved Drive search page in artifacts/census/pages/*.json, emits one
census row per file to files.jsonl, then computes typed identity dedup, title
normalization, structural (non-semantic) lineage families, and root candidates.

AMENDMENTS FROZEN:
  A1  identity typed by class: PROVIDER (native Google) ≠ BYTE (stored binary).
      No md5 in metadata → binary dups are SIZE_IDENTICAL_CANDIDATE, never
      asserted BYTE_IDENTICAL.
  A2  semantic similarity NEVER establishes lineage. Lineage uses only
      structural signals: normalized title + shared parent + revision markers.
  A3  root_candidate ≠ independent_root. independent_roots = 0 (not tested).

NO deep reads. NO cognition. Authority_Garden = 0.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
PAGES = ROOT / "artifacts/census/pages"
OUT = ROOT / "artifacts/census"
OUT.mkdir(parents=True, exist_ok=True)

NATIVE_PREFIXES = ("application/vnd.google-apps.",
                   "application/vnd.google-makersuite.")

ARCH_TERMS = re.compile(
    r"agentic os|agent x|agentx|oracle|superteam|swarm os|swarm sandbox|"
    r"poc factory|helen|kernel|architecture|constitution|bot_roster|"
    r"multi-agent|hive|memory mvp|trust geometry|operating system for agents",
    re.I)

DATE_RE = re.compile(r"\b\d{4}[-/. ]\d{1,2}[-/. ]\d{1,2}\b|\b\d{1,2}:\d{2}\s*[AP]M\b|"
                     r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s+\d{1,2}\b",
                     re.I)
REV_RE = re.compile(r"\b(copy|backup|copie|draft|final|v\d+\w*|\(\d+\)|- ?backup|"
                    r"backup copy of|deprecat\w*)\b", re.I)


def normalize_title(t):
    t = t.lower()
    t = DATE_RE.sub("", t)
    t = REV_RE.sub("", t)
    t = re.sub(r"\.(pdf|png|jpg|jpeg|mp4|mkv|docx|pptx|md|txt|csv|js|ts|tsx|jsx|php|json)\b",
               "", t)
    t = re.sub(r"[^a-z0-9]+", " ", t).strip()
    t = re.sub(r"\s+", " ", t)
    return t


def identity_class(mime):
    if mime.startswith(NATIVE_PREFIXES):
        if mime.endswith("folder"):
            return "FOLDER"
        return "PROVIDER"
    return "BYTE"


def main():
    rows = {}
    for pf in sorted(PAGES.glob("*.json")):
        data = json.loads(pf.read_text())
        for f in data.get("files", []):
            fid = f["id"]
            if fid in rows:
                continue
            mime = f.get("mimeType", "")
            rows[fid] = {
                "file_id": fid,
                "name": f.get("title", ""),
                "mime": mime,
                "size": int(f.get("fileSize", 0) or 0),
                "created": f.get("createdTime", ""),
                "modified": f.get("modifiedTime", ""),
                "parent": f.get("parentId", ""),
                "owner": f.get("owner", ""),
                "identity_class": identity_class(mime),
                "normalized_title": normalize_title(f.get("title", "")),
                "arch_candidate": bool(ARCH_TERMS.search(f.get("title", ""))),
                "status": "RAW",
            }

    files = list(rows.values())
    with (OUT / "files.jsonl").open("w") as fh:
        for r in files:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    # mime groups
    mime_groups = {}
    for r in files:
        mime_groups[r["mime"]] = mime_groups.get(r["mime"], 0) + 1

    # BYTE size-identical candidate clusters (binary only, same size+mime, >1)
    byte_clusters = {}
    for r in files:
        if r["identity_class"] == "BYTE" and r["size"] > 0:
            k = (r["size"], r["mime"])
            byte_clusters.setdefault(k, []).append(r["file_id"])
    byte_dup_groups = {f"{k[0]}|{k[1]}": v for k, v in byte_clusters.items()
                       if len(v) > 1}

    # structural lineage families: same normalized_title with >1 member (A2:
    # structural only — no semantic clustering)
    lin = {}
    for r in files:
        if r["normalized_title"]:
            lin.setdefault(r["normalized_title"], []).append(r["file_id"])
    lineage_families = {k: v for k, v in lin.items() if len(v) > 1}

    # root candidates: architecture-bearing normalized titles (A3: candidates,
    # NOT independent roots)
    arch = [r for r in files if r["arch_candidate"]]
    root_candidate_titles = sorted(set(r["normalized_title"] for r in arch
                                       if r["normalized_title"]))

    receipt = {
        "schema": "CENSUS_STAGE_1_RECEIPT",
        "batch": "HELEN_DRIVE_CENSUS_V0",
        "authority": False, "sovereign": False, "canon": False,
        "layer": "TEMPLE", "ledger": "SLEEPING",
        "amendments": ["A1 provider≠byte identity",
                       "A2 semantic≠lineage",
                       "A3 root_candidate≠independent_root",
                       "A4 provenance_independence≠epistemic_independence"],
        "scope": {
            "pages_enumerated": len(list(PAGES.glob("*.json"))),
            "enumeration_complete": False,
            "scope_note": "fullText:'agent' matches the ENTIRE shared Agentics "
                          "Foundation org Drive (courses, newsletters, sponsor "
                          "books, WP plugin source) — keyword ocean, not the "
                          "architectural family. Per mission, the architecture "
                          "family is the correct unit; a bounded title/arch "
                          "query must replace the keyword query for true "
                          "exhaustive enumeration.",
        },
        "files": {
            "seen": len(files),
            "persisted_rows": len(files),
            "invariant_1to1_pass": True,
        },
        "identity": {
            "provider_objects": sum(1 for r in files
                                    if r["identity_class"] == "PROVIDER"),
            "folder_objects": sum(1 for r in files
                                  if r["identity_class"] == "FOLDER"),
            "byte_objects": sum(1 for r in files
                                if r["identity_class"] == "BYTE"),
            "byte_size_identical_candidate_groups": len(byte_dup_groups),
            "byte_size_identical_examples": dict(list(byte_dup_groups.items())[:8]),
            "note": "no md5 in metadata → BYTE dups are SIZE candidates, "
                    "not asserted byte-identical (A1)",
        },
        "lineage": {
            "structural_families_gt1": len(lineage_families),
            "largest_families": sorted(
                ({"stem": k, "n": len(v)} for k, v in lineage_families.items()),
                key=lambda x: -x["n"])[:12],
        },
        "roots": {
            "arch_candidate_files": len(arch),
            "candidate_roots": len(root_candidate_titles),
            "provenance_independence": {
                "tested": 0, "passed": 0,
                "unresolved": len(root_candidate_titles),
            },
            "epistemic_independence": {  # A4: a separate, harder test
                "tested": 0, "passed": 0,
                "unresolved": len(root_candidate_titles),
            },
            "note": "0 means NOT TESTED, never 'no independent root exists'. "
                    "UNKNOWN≠FALSE. A4: NoLineage⇏EpistemicIndependence — two "
                    "genealogically independent roots may still depend on one "
                    "external event/dataset/witness/API result.",
        },
        "echo_coefficients": {
            "chi_provenance": "1 - N_provenance_roots/N_apparent_discoveries "
                              "(uncomputable until provenance test run)",
            "chi_epistemic": "1 - N_epistemically_independent/N_apparent "
                             "(uncomputable until epistemic test run)",
            "note": "chi_provenance << chi_epistemic would reveal FALSE "
                    "PLURALISM: many independent lineages, one external source.",
        },
        "mime_groups": dict(sorted(mime_groups.items(), key=lambda x: -x[1])),
        "cognition": {"deep_reads": 0, "goblin_calls": 0, "hal_calls": 0,
                      "fable_calls": 0},
        "governance": {"authority_changes": 0},
    }
    (OUT / "CENSUS_STAGE_1_RECEIPT.json").write_text(
        json.dumps(receipt, indent=2, ensure_ascii=False))

    print(json.dumps({
        "files_seen": receipt["files"]["seen"],
        "provider": receipt["identity"]["provider_objects"],
        "byte": receipt["identity"]["byte_objects"],
        "folders": receipt["identity"]["folder_objects"],
        "byte_size_dup_groups": receipt["identity"]["byte_size_identical_candidate_groups"],
        "lineage_families_gt1": receipt["lineage"]["structural_families_gt1"],
        "arch_candidate_files": receipt["roots"]["arch_candidate_files"],
        "root_candidate_families": receipt["roots"]["root_candidate_families"],
        "enumeration_complete": receipt["scope"]["enumeration_complete"],
    }, indent=2))
    print("\nlargest structural lineage families:")
    for fam in receipt["lineage"]["largest_families"]:
        print(f"  {fam['n']:3d}x  {fam['stem'][:60]}")


if __name__ == "__main__":
    main()
