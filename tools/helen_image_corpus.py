#!/usr/bin/env python3
"""
helen_image_corpus.py — extract text from recent images/PDFs -> reference corpus.

WHY (operator request "scan last 2 months images for HELEN/GOBLIN refs to
educate HELEN on the system"): HELEN's vision is broken, and you should not
feed text-bearing screenshots/PDFs to a broken vision model anyway. The
accurate path is OCR + PDF-text extraction into a corpus, then RAG
(helen_local_rag) over it. Text, cited, no vision model required.

WHAT (read-only, no source mutation, no fabrication):
  1. Find images/PDFs modified in the last N days (default 60 = ~2 months).
  2. Extract TEXT:
       - PDFs  -> `pdftotext` (poppler) if available
       - images -> OCR via pytesseract+PIL if available
     If a tool is missing, the file is recorded UNEXTRACTED (never guessed text).
  3. Filter for HELEN/GOBLIN/equivalent reference terms.
  4. Emit a corpus NDJSON (one record per matching chunk) that helen_local_rag
     can index, plus a coverage report (what was extracted vs skipped vs why).

FABRICATION REFUSAL: if extraction tooling is absent, the record is
{"extracted": false, "reason": "..."} — the tool NEVER invents image contents
(this is exactly the R4 vision-speculation failure, avoided).

USAGE (on the Mac):
  python3 helen_image_corpus.py \
      --roots ~/Desktop ~/Documents/GitHub/helen_os_v1 \
      --days 60 --out helen_image_corpus.ndjson
  # then index for RAG:
  python3 helen_local_rag.py index .   # picks up the .ndjson as corpus

authority: false · read-only · cites source file+page; never fabricates content.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

IMAGE_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".tiff", ".bmp"}
PDF_EXT = {".pdf"}

# HELEN/GOBLIN and equivalents — the reference vocabulary to scan for.
REFERENCE_TERMS = [
    "HELEN", "GOBLIN", "HER", "HAL", "REDUCER", "LEDGER", "MAYOR", "REPLAY",
    "RALPH", "CHIDDUSH", "CHIDDHUSH", "TEMPLE", "WULMOJI", "JESTER", "DAN",
    "HERMES", "AIRI", "EGREGOR", "AUTORESEARCH", "NO RECEIPT", "authority",
    "kernel", "tranche", "RIEMANN", "AGI_OS", "DIRECTOR",
]
# Word-boundary anchored so short terms (HER, HAL, DAN) don't match inside
# ordinary words ("weather", "shall", "abundant").
_TERM_RE = re.compile(r"\b(?:" + "|".join(re.escape(t) for t in REFERENCE_TERMS) + r")\b",
                      re.IGNORECASE)


def iter_recent_media(roots: list[Path], days: int):
    cutoff = datetime.now(timezone.utc).timestamp() - days * 86400
    for root in roots:
        root = root.expanduser()
        if not root.exists():
            continue
        for p in root.rglob("*"):
            if not p.is_file():
                continue
            if p.suffix.lower() not in (IMAGE_EXT | PDF_EXT):
                continue
            try:
                if p.stat().st_mtime < cutoff:
                    continue
            except OSError:
                continue
            yield p


def extract_pdf_text(path: Path) -> tuple[str | None, str]:
    """(text, reason). text=None if extraction unavailable/failed."""
    if not shutil.which("pdftotext"):
        return None, "pdftotext (poppler) not installed"
    try:
        out = subprocess.run(["pdftotext", "-layout", str(path), "-"],
                             capture_output=True, text=True, timeout=60)
        if out.returncode != 0:
            return None, f"pdftotext rc={out.returncode}"
        return out.stdout, "ok"
    except Exception as e:
        return None, f"pdftotext error: {e}"


def extract_image_text(path: Path) -> tuple[str | None, str]:
    """(text, reason). OCR via pytesseract+PIL; None if unavailable."""
    try:
        from PIL import Image  # noqa
    except Exception:
        return None, "PIL/Pillow not installed (pip install Pillow)"
    try:
        import pytesseract  # noqa
    except Exception:
        return None, "pytesseract not installed (pip install pytesseract + brew install tesseract)"
    if not shutil.which("tesseract"):
        return None, "tesseract binary not on PATH (brew install tesseract)"
    try:
        from PIL import Image
        import pytesseract
        return pytesseract.image_to_string(Image.open(path)), "ok"
    except Exception as e:
        return None, f"ocr error: {e}"


def find_references(text: str):
    """Return (matched_terms, matching_snippets) — only lines that hit a term."""
    terms = sorted({m.group(0).upper() for m in _TERM_RE.finditer(text)})
    snippets = []
    for ln in text.splitlines():
        if _TERM_RE.search(ln):
            s = ln.strip()
            if s:
                snippets.append(s[:200])
    return terms, snippets


def build_corpus(roots, days, out_path: Path):
    records, report = [], {"extracted": 0, "skipped": 0, "no_refs": 0,
                           "by_reason": {}, "files": 0}
    for p in iter_recent_media(roots, days):
        report["files"] += 1
        kind = "pdf" if p.suffix.lower() in PDF_EXT else "image"
        text, reason = (extract_pdf_text(p) if kind == "pdf"
                        else extract_image_text(p))
        if text is None:
            report["skipped"] += 1
            report["by_reason"][reason] = report["by_reason"].get(reason, 0) + 1
            records.append({"source": str(p), "kind": kind,
                            "extracted": False, "reason": reason,
                            "mtime": datetime.fromtimestamp(p.stat().st_mtime,
                                     timezone.utc).isoformat()})
            continue
        terms, snippets = find_references(text)
        if not terms:
            report["no_refs"] += 1
            continue
        report["extracted"] += 1
        records.append({
            "source": str(p), "kind": kind, "extracted": True,
            "matched_terms": terms,
            "snippets": snippets[:40],
            "char_count": len(text),
            "mtime": datetime.fromtimestamp(p.stat().st_mtime, timezone.utc).isoformat(),
        })
    out_path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in records) + "\n",
                        encoding="utf-8")
    return report


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--roots", nargs="+", required=True, help="dirs to scan")
    ap.add_argument("--days", type=int, default=60, help="modified within N days (default 60)")
    ap.add_argument("--out", default="helen_image_corpus.ndjson")
    args = ap.parse_args()

    roots = [Path(r) for r in args.roots]
    out = Path(args.out)
    print(f"== scanning {[str(r) for r in roots]} (last {args.days} days) ==")
    rep = build_corpus(roots, args.days, out)
    print(f"   files seen:        {rep['files']}")
    print(f"   extracted w/ refs: {rep['extracted']}")
    print(f"   extracted no-refs: {rep['no_refs']}")
    print(f"   skipped (no tool): {rep['skipped']}")
    for reason, n in rep["by_reason"].items():
        print(f"       - {n}x {reason}")
    print(f"   corpus written:    {out}")
    if rep["skipped"] and rep["extracted"] == 0:
        print("\n   >>> nothing extracted. Install: brew install poppler tesseract; "
              "pip install Pillow pytesseract")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
