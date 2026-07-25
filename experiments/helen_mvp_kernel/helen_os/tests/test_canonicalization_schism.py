"""Witness for FINDING_CANONICALIZATION_SCHISM_V1.

Re-derives every number in the finding from LIVE repo state: AST parse for
call-site counts, real ledger reads for divergence rates.

These tests assert that the schism EXISTS. If the corpus is ever unified
onto one canonicalizer, they go red — and that red is the good news.
Each assertion says so in its own message.

Read-only. NON_SOVEREIGN. authority=false.
"""

import ast
import hashlib
import json
from pathlib import Path

# tests/ -> helen_os/ -> helen_mvp_kernel/ -> experiments/ -> <repo root>
REPO = Path(__file__).resolve().parents[4]
SOVEREIGN = REPO / "town" / "ledger_v1.ndjson"

canon_utf8 = lambda o: json.dumps(o, sort_keys=True, separators=(",", ":"),
                                  ensure_ascii=False).encode("utf-8")
canon_ascii = lambda o: json.dumps(o, sort_keys=True,
                                   separators=(",", ":")).encode("utf-8")
sha = lambda b: hashlib.sha256(b).hexdigest()


def _count_canonicalizer_variants():
    """AST-accurate: only json.dumps calls with BOTH sort_keys and separators."""
    counts = {"utf8": 0, "ascii_explicit": 0, "ascii_default": 0}
    for p in REPO.rglob("*.py"):
        s = str(p)
        if ".venv" in s or "node_modules" in s:
            continue
        try:
            tree = ast.parse(p.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            f = node.func
            name = f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", "")
            if name != "dumps":
                continue
            kw = {k.arg: k.value for k in node.keywords if k.arg}
            if "sort_keys" not in kw or "separators" not in kw:
                continue
            ea = kw.get("ensure_ascii")
            if ea is None:
                counts["ascii_default"] += 1
            elif isinstance(ea, ast.Constant) and ea.value is False:
                counts["utf8"] += 1
            elif isinstance(ea, ast.Constant) and ea.value is True:
                counts["ascii_explicit"] += 1
    return counts


def _sovereign_rows():
    return [json.loads(l) for l in
            SOVEREIGN.read_text(encoding="utf-8").splitlines() if l.strip()]


def test_both_canonicalizers_are_in_active_use():
    """The schism exists: both conventions have substantial call-site counts."""
    c = _count_canonicalizer_variants()
    ascii_total = c["ascii_default"] + c["ascii_explicit"]
    assert c["utf8"] >= 20, (
        f"ensure_ascii=False call sites dropped to {c['utf8']} — corpus may have "
        "been unified. If so, delete this test and celebrate.")
    assert ascii_total >= 20, (
        f"ascii-emitting call sites dropped to {ascii_total} — corpus may have "
        "been unified onto UTF-8. If so, the schism is CLOSED. Good.")


def test_the_two_canonicalizers_disagree_on_unicode():
    """The mechanism itself: identical on ASCII, divergent on non-ASCII."""
    ascii_payload = {"verdict": "PASS", "n": 1}
    assert canon_utf8(ascii_payload) == canon_ascii(ascii_payload)

    unicode_payload = {"verdict": "PASS", "note": "émergence 🟢"}
    assert canon_utf8(unicode_payload) != canon_ascii(unicode_payload)
    assert sha(canon_utf8(unicode_payload)) != sha(canon_ascii(unicode_payload))


def test_sovereign_ledger_validates_under_utf8_convention():
    """Precondition: town/ledger_v1.ndjson is internally consistent under A."""
    rows = _sovereign_rows()
    ok = sum(1 for r in rows if sha(canon_utf8(r["payload"])) == r["payload_hash"])
    assert ok == len(rows), (
        f"sovereign ledger no longer fully validates under ensure_ascii=False "
        f"({ok}/{len(rows)}) — this is a REAL integrity problem, not a schism.")


def test_wrong_convention_validator_would_reject_real_sovereign_events():
    """The consequence: a self-consistent validator on side B rejects ~15%."""
    rows = _sovereign_rows()
    rejected = [r["seq"] for r in rows
                if sha(canon_ascii(r["payload"])) != r["payload_hash"]]
    assert rejected, (
        "no sovereign event is convention-sensitive any more — either the "
        "ledger lost its non-ASCII payloads or the schism was closed.")
    frac = len(rejected) / len(rows)
    assert 0.05 < frac < 0.40, f"rejection fraction moved to {frac:.1%}"
    # the specific early events named in the finding
    assert 8 in rejected and 19 in rejected


def test_multiple_cum_hash_schemes_coexist():
    """V0 (unprefixed) and HELEN_CUM_V1 (domain-separated) are both live."""
    def chain_ok(path, prefix=b""):
        p = REPO / path
        if not p.exists():
            return None
        rows = [json.loads(l) for l in
                p.read_text(encoding="utf-8").splitlines() if l.strip()]
        rows = [r for r in rows if isinstance(r, dict) and "cum_hash" in r]
        if not rows:
            return None
        ok = 0
        for r in rows:
            try:
                if sha(prefix + bytes.fromhex(r["prev_cum_hash"]) +
                       bytes.fromhex(r["payload_hash"])) == r["cum_hash"]:
                    ok += 1
            except Exception:
                pass
        return ok, len(rows)

    v0 = chain_ok("town/ledger_v1.ndjson", b"")
    assert v0 and v0[0] == v0[1], f"V0 scheme broken on sovereign ledger: {v0}"

    v1 = chain_ok("town/ledger_v1_HELEN_CUM_V1_GENESIS.ndjson", b"HELEN_CUM_V1")
    if v1:  # file may be absent on other lineages
        assert v1[0] == v1[1], f"HELEN_CUM_V1 scheme broken: {v1}"
        # and it must NOT validate under V0 — that is what makes it a schism
        v1_under_v0 = chain_ok("town/ledger_v1_HELEN_CUM_V1_GENESIS.ndjson", b"")
        assert v1_under_v0[0] == 0, (
            "HELEN_CUM_V1 ledger now also validates under V0 — schemes converged?")


def test_self_documenting_header_practice_exists_somewhere():
    """HELEN_CUM_V1 states its own rule in row 0. That is the fix pattern."""
    p = REPO / "town" / "ledger_v1_HELEN_CUM_V1_GENESIS.ndjson"
    if not p.exists():
        return
    row0 = json.loads(p.read_text(encoding="utf-8").splitlines()[0])
    spec = row0.get("payload", {}).get("hash_scheme_spec", "")
    assert "HELEN_CUM_V1" in spec and "prev_bytes" in spec, (
        "the one ledger that documented its own hash scheme no longer does")
