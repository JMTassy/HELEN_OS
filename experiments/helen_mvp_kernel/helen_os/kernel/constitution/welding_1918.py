"""ELECTRIC ARC WELDING (Lincoln Electric Co., 3rd ed., 1918) as a
completeness fixture — a NEW KIND of corpus.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.

Provenance, exact: the OCR text was relayed in-frame (grade REPORTED).
The archive.org PDF/images (ia600407.us.archive.org/.../electricarcweldi
00linc.pdf) are UNREACHABLE from this seat — CONNECT 403, probed
2026-08-12. So the images are NOT_ACCESSED, never "absent," and no
claim here rests on them. RELAY != DIRECT; the ceiling of this corpus
is REPORTED.

Why this corpus matters to the completeness question: every prior
corpus (Crystal Palace, Prize Papers, ATF) was a catalogue, an
archive, or a court record. This one is a VENDOR SALES DOCUMENT —
Lincoln Electric arguing its arc welder beats oxy-acetylene, riveting
and thermit. Its characteristic laundering is therefore different in
kind: self-interested comparative claims, curated favorable
testimony, estimates dressed as measurements. If the four-ceiling
algebra is really complete, even this adversarial-in-a-new-way corpus
should produce ZERO prohibitions that need a fifth ceiling.

The finding (see the test): it does. Seven genuine prohibitions, each
anchored to real OCR, all compile into PROOF / SCOPE / REPLAY. The
corpus exercises PROOF heavily — exactly what a sales document's
laundering looks like — and needs no new ceiling. Completeness
evidence accumulates; it is never PROVEN (NotObserved(counterexample)
does not entail Impossible(counterexample)).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from completeness import CEILING_BASIS, SAFETY_PROHIBITION_CENSUS  # noqa: E402


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


CORPUS = {
    "corpus_id": "lincoln_electric_arc_welding_1918_3rd_ed",
    "kind": "vendor_sales_document",
    "access_mode": "RELAYED",
    "images": "NOT_ACCESSED (archive.org CONNECT 403 from this seat)",
    "ceiling": "REPORTED",
}


# Seven genuine prohibitions, each with a real OCR anchor from the
# relayed text, each named with the ceiling it compiles into. `census`
# links to an existing census key when the prohibition instantiates one
# verbatim; when it is a NEW INSTANCE of an existing ceiling, census is
# "" and the point stands: a new instance is not a new ceiling.

WELDING_1918_PROHIBITIONS = (
    {"finding": "the vendor's own document asserting its product is "
                "cheapest is not verified superiority",
     "ocr": "This welder will do welding work at lower cost than any "
            "other method or process. This assertion The Lincoln "
            "Electric Co. are ready to prove by direct comparative test",
     "ceiling": "PROOF",
     "census": "existence != proof"},
    {"finding": "curated favorable testimony (Grine, Kerwin, several "
                "railway committees, all pro-electric) is density, not "
                "an independent witness",
     "ocr": "These opinions from railway men are given at length, "
            "because of their very wide experience with welding "
            "processes",
     "ceiling": "PROOF",
     "census": "retrieval density != epistemic independence"},
    {"finding": "the book's own 'weld as strong as the original plate' "
                "is refuted by its own caveat; the conservative "
                "modality wins",
     "ocr": "the weld will have just as great tensile strength as the "
            "original plate, but being cast steel it cannot have the "
            "ductility which rolled steel stock possesses ... [Design] "
            "will stand very little bending stress",
     "ceiling": "PROOF",
     "census": "extraction != truth"},
    {"finding": "a projected per-ton cost presented beside a measured "
                "tank test is an estimate, not a measurement",
     "ocr": "a total cost of $87.00 per ton ... with a fair chance of "
            "average cost as low as $75.50 per ton  (vs) The report "
            "from one particular test made on identically the same work",
     "ceiling": "PROOF",
     "census": ""},                     # new instance of PROOF, not new ceiling
    {"finding": "1916 cost figures do not hold now; the book says so",
     "ocr": "Cost Based on Conditions of 1916 ... Labor has advanced "
            "considerably since this time",
     "ceiling": "REPLAY",
     "census": "valid at intake != valid at execution"},
    {"finding": "classification approval enumerated for specific "
                "non-structural parts does not extend to strength "
                "members",
     "ocr": "the insurance rules do not permit the welding of any "
            "strength members ... approved the application of electric "
            "welding to the following parts: Deck Rail Stanchions ... "
            "[enumerated non-structural list]",
     "ceiling": "SCOPE",
     "census": "partial verdict scope"},
    {"finding": "the archive.org images this seat was asked to check "
                "are unreachable; not-fetched is not not-existent",
     "ocr": "(operator request) check images also from "
            "ia600407.us.archive.org/.../electricarcweldi00linc.pdf",
     "ceiling": "PROOF",
     "census": "DocumentNotFound != EventDidNotOccur"},
)


def corpus_completeness() -> dict:
    """Run the vendor corpus through the ceiling basis. Every
    prohibition must land in one of the four ceilings; an UNMAPPED one
    would be the diagnostic that the constitution must grow."""
    ceilings, unmapped, census_hits = [], [], 0
    for p in WELDING_1918_PROHIBITIONS:
        c = p["ceiling"]
        if c not in CEILING_BASIS:
            unmapped.append(p["finding"])
        else:
            ceilings.append(c)
        if p["census"]:
            if p["census"] not in SAFETY_PROHIBITION_CENSUS or \
                    SAFETY_PROHIBITION_CENSUS[p["census"]] != p["ceiling"]:
                unmapped.append(f"census-mismatch:{p['finding']}")
            else:
                census_hits += 1
    from collections import Counter
    dist = dict(sorted(Counter(ceilings).items()))
    return {"corpus": CORPUS["corpus_id"],
            "kind": CORPUS["kind"],
            "prohibitions": len(WELDING_1918_PROHIBITIONS),
            "ceiling_distribution": dist,
            "existing_census_hits": census_hits,
            "unmapped": unmapped,
            "needs_fifth_ceiling": bool(unmapped),
            "completeness_verdict": ("MAPS_COMPLETELY" if not unmapped
                                     else "COUNTEREXAMPLE_FOUND"),
            "chiddush": "a vendor sales document — adversarial in a new "
                        "way (self-interest, curated testimony, "
                        "estimates as measurements) — produces zero "
                        "prohibitions needing a fifth ceiling; its "
                        "laundering is PROOF-heavy, as a sales document's "
                        "should be",
            "epistemic_status": "completeness evidence accumulates; "
                                "never PROVEN "
                                "(NotObserved != Impossible)"}
