"""Daily corpus scan protocol — the "Google Street" structuring street.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.

The operator's mega-prompt, made executable. This module does NOT scan
any corpus — this seat cannot reach Drive/Gmail; the scan runs in the
connected account seat. What lives here is the RECEIVER: the discipline
a day's scan output must pass before it is a report, so that no scan
can launder itself into admitted memory.

Three laws, verbatim from the ruling, each an executable refusal:

    TITRE != CONTENU     a title, filename or container name is not
                         what the object contains. Reading the name is
                         not reading the object.
    CLONE != ORIGINAL    N copies of one artifact are one artifact;
                         N mirrors of one source are one witness.
    EXISTENCE != PREUVE  an object appearing in a listing proves it
                         exists, not that its claims are true, nor that
                         it has been read.

Search discipline: by CONTAINER, OWNER and DATE — never by keyword
alone. Keyword search over "UZIK" misses the object owned by someone
else, dated in-window, sitting in a container whose name never says
UZIK. (This is the 488MB-recording lesson, generalized to a street.)

End-of-loop, from the liveness theorem already in this kernel:
    - no admission without a packet (IngestionCell admission rule);
    - if nothing new: HALT and say why (a lawful halt, not an eternal
      hold — a scan that finds nothing must state that, with its
      coverage receipt, not silently produce a stale report).

Deterministic: no wall-clock, no randomness, canonical serialization.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field

# the structuring streets of the second brain; Google is the first case.
STREETS = ("google_street", "neption_street", "uzik_agency_street",
           "recruitment_street", "admin_street")

# scan axes — keyword is deliberately LAST and never sufficient alone.
SCAN_AXES = ("by_container", "by_owner", "by_date", "by_keyword")

READ_STATES = ("LISTED", "TITLE_ONLY", "CONTENT_READ", "WITNESSED")
# LISTED       : appeared in an enumeration (existence, nothing more)
# TITLE_ONLY   : name/metadata seen, body not fetched
# CONTENT_READ : body actually read in-frame
# WITNESSED    : content read AND an independent root confirms a claim


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


# ── the per-element record ──────────────────────────────────────────────

@dataclass(frozen=True)
class ScanElement:
    """One object found on a street. status is its READ_STATE; a claim
    may only be extracted from CONTENT_READ or WITNESSED, never from a
    title or a bare listing."""
    element_id: str
    street: str
    container: str
    owner: str
    date: str
    title: str
    status: str
    source_root: str
    content_hash: str = ""             # empty until content is read

    def __post_init__(self):
        if self.street not in STREETS:
            raise ValueError("E_UNKNOWN_STREET")
        if self.status not in READ_STATES:
            raise ValueError("E_UNKNOWN_READ_STATE")
        if self.status in ("CONTENT_READ", "WITNESSED") and \
                not self.content_hash:
            raise ValueError("E_READ_CLAIM_WITHOUT_CONTENT")


# ── TITRE != CONTENU ────────────────────────────────────────────────────

def extract_claim(element: ScanElement, claim: str) -> dict:
    """A claim may be extracted only from read content. Extracting from
    a title or a listing is E_TITLE_IS_NOT_CONTENT — the object was
    seen, not read."""
    if element.status in ("LISTED", "TITLE_ONLY"):
        return {"verdict": "REFUSED", "reason": "E_TITLE_IS_NOT_CONTENT",
                "status": element.status,
                "law": "reading the name is not reading the object"}
    return {"verdict": "CLAIM_EXTRACTED", "claim": claim,
            "from": element.element_id, "grounded_in": element.content_hash}


# ── CLONE != ORIGINAL ───────────────────────────────────────────────────

def dedupe_by_content(elements: tuple) -> dict:
    """N copies of one artifact are one artifact. Group by content_hash
    (read objects only); count DISTINCT source roots, never copies."""
    read = [e for e in elements if e.content_hash]
    by_hash: dict = {}
    for e in read:
        by_hash.setdefault(e.content_hash, []).append(e)
    originals = []
    for h, group in sorted(by_hash.items()):
        roots = {e.source_root for e in group}
        originals.append({"content_hash": h, "copies": len(group),
                          "independent_roots": len(roots),
                          "is_corroborated": len(roots) > 1})
    return {"artifacts": len(by_hash),
            "raw_elements": len(read),
            "originals": originals,
            "law": "clone is not original; N mirrors of one source are "
                   "one witness"}


# ── EXISTENCE != PREUVE ─────────────────────────────────────────────────

def existence_verdict(element: ScanElement) -> dict:
    """Appearing in a listing is existence, not proof and not reading.
    A LISTED/TITLE_ONLY element carries zero admissible claims."""
    if element.status in ("LISTED", "TITLE_ONLY"):
        return {"proves": "EXISTENCE_ONLY", "admissible_claims": 0,
                "law": "existence in a listing is not proof, nor "
                       "evidence, nor reading"}
    return {"proves": "CONTENT_AVAILABLE",
            "admissible_claims": "up to what the content and its roots "
                                 "support"}


# ── search discipline: container/owner/date, not keyword alone ─────────

def coverage_is_deep(axes_run: tuple) -> dict:
    """A day's scan is deep only if it ran the container, owner and
    date axes. Keyword-only coverage is refused — it misses the
    in-window object that never says the keyword."""
    ran = set(axes_run)
    structural = {"by_container", "by_owner", "by_date"}
    missing = sorted(structural - ran)
    if missing:
        return {"verdict": "SHALLOW", "reason": "E_KEYWORD_ONLY_COVERAGE",
                "missing_axes": missing,
                "law": "search by container, owner and date — not by "
                       "keyword alone"}
    return {"verdict": "DEEP", "axes": sorted(ran)}


# ── scoring: four independent axes, no scalar collapse ─────────────────

@dataclass(frozen=True)
class ElementScore:
    """Per-element scores. Kept as a vector; there is deliberately no
    single 'overall' number, so a high skill value cannot hide a high
    rights risk."""
    element_id: str
    novelty: float
    confidence: float
    skill_value: float
    rights_risk: float

    def flags(self) -> tuple:
        f = []
        if self.rights_risk >= 0.7:
            f.append("HIGH_RIGHTS_RISK")
        if self.confidence < 0.4:
            f.append("LOW_CONFIDENCE")
        if self.novelty < 0.2:
            f.append("NOT_NEW")
        return tuple(f)


# ── end of loop: no admission without a packet; lawful halt ────────────

@dataclass(frozen=True)
class DailyPacket:
    """The day's output. A report is admissible only as a packet:
    new elements, new claims (each grounded), gaps, and exactly one
    next action. Empty new-set is allowed — but then it must HALT with
    a stated reason, not emit a stale report."""
    date: str
    street: str
    new_elements: tuple
    new_claims: tuple                  # each: (element_id, claim, root)
    gaps: tuple
    next_action: str
    coverage: dict                     # coverage_is_deep() output


def close_loop(packet: DailyPacket) -> dict:
    """The admission gate for a day's scan."""
    if packet.coverage.get("verdict") != "DEEP":
        return {"verdict": "REJECTED", "reason": "E_SHALLOW_COVERAGE",
                "note": "a shallow scan is not a day's coverage"}
    # a claim must cite an element that was actually read
    read_ids = {e.element_id for e in packet.new_elements
                if e.status in ("CONTENT_READ", "WITNESSED")}
    ungrounded = [c for c in packet.new_claims
                  if c[0] not in read_ids]
    if ungrounded:
        return {"verdict": "REJECTED", "reason": "E_UNGROUNDED_CLAIM",
                "ungrounded": [c[0] for c in ungrounded]}
    if not packet.new_elements and not packet.new_claims:
        # the lawful halt — liveness: HOLD must say why, not go silent
        if not packet.next_action:
            return {"verdict": "E_SILENT_HALT",
                    "law": "if nothing new, halt AND say why"}
        return {"verdict": "LAWFUL_HALT",
                "reason": "nothing new on this street today",
                "coverage": packet.coverage["verdict"],
                "stated": packet.next_action}
    if not packet.next_action:
        return {"verdict": "REJECTED", "reason": "E_NO_NEXT_ACTION"}
    return {"verdict": "PACKET_ADMISSIBLE",
            "new_elements": len(packet.new_elements),
            "new_claims": len(packet.new_claims),
            "gaps": len(packet.gaps),
            "next_action": packet.next_action,
            "law": "no admission without a packet"}


# ── the Google Street source manifest (the operator's next action) ─────
# STRUCTURE ONLY. Owners/dates/containers are placeholders to be filled
# by the connected account seat that can actually read Drive/Gmail —
# NOT invented here. Filling these from this seat would be the exact
# existence-is-not-proof violation this module forbids.

GOOGLE_STREET_MANIFEST_SCHEMA = {
    "street": "google_street",
    "structuring_case": "first structuring case — multi-year, "
                        "multi-format (brand -> events -> influence -> "
                        "cloud -> agency posture)",
    "required_axes": ("by_container", "by_owner", "by_date"),
    "per_source_fields": ("container", "owner", "date", "format",
                          "read_state", "source_root"),
    "skills_to_train_first": ("client_timeline_reconstruction",
                              "delivery_playbook", "strategic_memory"),
    "status": "PRESENCE_OBSERVED_NOT_READ",
    "note": "manifest entries are populated by the connected Drive/"
            "Gmail seat, not fabricated here",
}
