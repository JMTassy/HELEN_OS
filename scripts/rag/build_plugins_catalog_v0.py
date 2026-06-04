"""
build_plugins_catalog_v0.py — RAG catalog v0 for HELEN's jmt_frameworks retriever.

Turns the HAL-admitted local PDF corpus (~/vault/helen_pdf_corpus/text/*.txt) into
PLUGINS_JMT_CATALOG.json in the shape jmt_frameworks expects:
    {"categories": [{"category_name": str, "documents": [ {title, key_rules, ...} ]}]}
retrieve_relevant_frameworks() keyword-matches on title + key_rules, so each doc gets
extracted keywords + salient lines + an excerpt for injection.

Deterministic. No LLM, no model-generated text. Governance:
  * authority=false, NO_CLAIM — the catalog is retrievable evidence, not admitted canon.
  * LOCAL-ONLY — the OUTPUT json holds operator IP excerpts and is NOT pushed to git.
    Only THIS generator (code) is committed. Output path is the operator's machine.
  * Scope is the HAL-admitted set only (financial/admin/TV5-hold docs were never extracted).

Run:  python scripts/rag/build_plugins_catalog_v0.py
Out:  ~/Desktop/oracle_town/PLUGINS_JMT_CATALOG.json  (jmt_frameworks default)
      + ~/vault/helen_pdf_corpus/PLUGINS_JMT_CATALOG.json  (working copy)
"""
import json, re, collections
from datetime import datetime, timezone
from pathlib import Path

CORPUS = Path.home() / "vault/helen_pdf_corpus/text"
OUT_PLUGIN = Path.home() / "Desktop/oracle_town/PLUGINS_JMT_CATALOG.json"
OUT_VAULT = Path.home() / "vault/helen_pdf_corpus/PLUGINS_JMT_CATALOG.json"

EXCERPT_WORDS = 1200
TOP_KEYWORDS = 18
MAX_RULES = 8

# compact EN+FR stopword set (corpus is mixed-language)
STOP = set("""the a an and or of to in on for with is are was were be been being this that these those
it its as at by from into out up down over under then than so but not no nor can will would should could
i you he she we they me him her them my your our their his hers ours theirs do does did has have had
le la les un une des de du au aux et ou est sont etre être avec dans pour par sur sous ce cette ces qui que
quoi dont ne pas plus tres très comme mais donc car ou où son sa ses leur leurs nous vous ils elles je tu il
elle on se si tout tous toute toutes fait faire peut être cela ceci aussi entre vers chez""".split())

WORD = re.compile(r"[a-zà-ÿ0-9]{3,}", re.I)


def keywords(text):
    freq = collections.Counter(w for w in WORD.findall(text.lower()) if w not in STOP and not w.isdigit())
    return [w for w, _ in freq.most_common(TOP_KEYWORDS)]


def key_rules(raw):
    rules, seen = [], set()
    for line in raw.splitlines():
        t = line.strip()
        if 12 <= len(t) <= 120 and (t[0:1].isupper() or any(c in t for c in ":=→")) \
                and re.search(r"[a-zà-ÿ]", t, re.I):
            k = t.lower()
            if k not in seen:
                seen.add(k); rules.append(t)
        if len(rules) >= MAX_RULES:
            break
    return rules


def category_of(stem):
    if stem.startswith("PLUGINS_"):
        return "PLUGINS_JMT"
    if stem.startswith("LOOSE_"):
        return "HELEN_LOOSE"
    if stem.startswith("VRAC_"):
        return "VRAC_VISION"
    return "MISC"


def main():
    cats = {}
    total_words = 0
    for txt in sorted(CORPUS.glob("*.txt")):
        raw = txt.read_text(errors="ignore")
        words = raw.split()
        if len(words) < 20:
            continue
        total_words += len(words)
        stem = txt.stem
        title = re.sub(r"^(PLUGINS_|LOOSE_|VRAC_)", "", stem)
        doc = {
            "title": title,
            "source": txt.name,
            "word_count": len(words),
            "keywords": keywords(raw),
            "key_rules": key_rules(raw),
            "excerpt": " ".join(words[:EXCERPT_WORDS]),
            "authority": False,
        }
        cats.setdefault(category_of(stem), []).append(doc)

    catalog = {
        "schema": "PLUGINS_JMT_CATALOG_V0",
        "authority": False,
        "claim": "NO_CLAIM",
        "status": "NON_SOVEREIGN · LOCAL_ONLY · retrievable evidence, not admitted canon",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "provenance": "HAL-admitted local PDF corpus (PLUGINS_JMT + loose HELEN + admitted VRAC). "
                      "Financial/admin/TV5-hold docs excluded by HAL gate.",
        "doc_count": sum(len(v) for v in cats.values()),
        "total_words": total_words,
        "categories": [
            {"category_name": name, "document_count": len(docs), "documents": docs}
            for name, docs in sorted(cats.items())
        ],
    }

    for out in (OUT_PLUGIN, OUT_VAULT):
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(catalog, ensure_ascii=False, indent=2))

    print(f"catalog: {catalog['doc_count']} docs, {catalog['total_words']} words")
    for c in catalog["categories"]:
        print(f"  {c['category_name']}: {c['document_count']} docs")
    print(f"written → {OUT_PLUGIN}")
    print(f"        → {OUT_VAULT}")
    print("LOCAL-ONLY: catalog json is NOT committed (holds operator IP); generator is.")


if __name__ == "__main__":
    main()
