#!/usr/bin/env python3
"""WUL IR v0 — minimal executable falsifier for the 2-goblin delta protocol.

GARDEN / NO_CLAIM. authority=false. Deterministic: no clock, no network,
no randomness. Same packet sequence => same final chain hash (replay).

What this falsifies (type-safety claims of the protocol):
  C1  epistemic laundering is SYNTACTICALLY impossible — no production
      derives TRUE from any state; ACCEPT requires a scope in {T,F,C}
  C2  attacks bind to (id, rev) — stale-rev attacks fail closed
  C3  packets are typed deltas — sovereign fields, missing SRC/TEST,
      over-budget payloads, empty repairs all fail closed
  C4  namespace discipline — foreign-register glyphs in the wire are
      rejected (parser_mode=fail_closed), per SHARED_GLYPH != SHARED_TYPE
  C5  round-trip law P_N(R_N(x)) = x for the WUL projection
  C6  replay — chained state hash identical across two runs

What this does NOT test: token economy vs natural language (needs the
LLM benchmark), cognition, truth of any claim. EXECUTION_RECEIPT of this
run is not evidence for the protocol's usefulness — only its coherence.
"""

import hashlib
import json

NAMESPACE = "WUL_SPEED_V0"
MAX_PACKET_TOKENS = 120
OPS = {"P", "X", "R", "A", "H", "J", "T"}
ACCEPT_SCOPES = {"T", "F", "C"}
SOVEREIGN_FIELDS = {"verdict", "truth", "ship", "no_ship", "decision",
                    "state_mutation", "ledger_pointer", "authority_grant"}
# Foreign registers (Source Atlas governance colors) forbidden in wire:
FOREIGN_GLYPHS = {"\U0001F7E2", "\U0001F7E1", "⚪", "⚫"}
WUL_PROJECTION = {"P": "\U0001F9FE?", "X": "⚔️",
                  "R": "\U0001F501", "A": "✅", "H": "\U0001F33F",
                  "J": "❌", "T": "\U0001F9EA"}
WUL_REVERSE = {v: k for k, v in WUL_PROJECTION.items()}

LEGAL = {  # state machine — note: no state named TRUE exists at all
    ("PROPOSED", "X"): "CHALLENGED",
    ("PROPOSED", "A"): "TEST_SPEC_ACCEPTED",
    ("CHALLENGED", "R"): "REVISED",
    ("REVISED", "X"): "CHALLENGED",
    ("REVISED", "A"): "TEST_SPEC_ACCEPTED",
    ("TEST_SPEC_ACCEPTED", "T"): "TESTED",
    ("PROPOSED", "J"): "REJECTED", ("CHALLENGED", "J"): "REJECTED",
    ("REVISED", "J"): "REJECTED",
    ("PROPOSED", "H"): "HELD", ("CHALLENGED", "H"): "HELD",
    ("REVISED", "H"): "HELD",
}


class Rejected(Exception):
    pass


def canon(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"))


def token_count(pkt):
    return len(canon(pkt).split()) + len(canon(pkt)) // 4


def validate(pkt, state):
    """HAL — fail-closed packet validator."""
    if not isinstance(pkt, dict):
        raise Rejected("NOT_A_PACKET")
    for f in SOVEREIGN_FIELDS & set(map(str.lower, pkt.keys())):
        raise Rejected(f"SOVEREIGN_FIELD:{f}")
    for v in pkt.values():
        if isinstance(v, str) and any(g in v for g in FOREIGN_GLYPHS):
            raise Rejected("CROSS_NAMESPACE_GLYPH")
    op = pkt.get("op")
    if op not in OPS:
        raise Rejected(f"UNKNOWN_OP:{op}")
    hid, rev = pkt.get("id"), pkt.get("rev")
    if not hid or rev is None:
        raise Rejected("MISSING_ID_OR_REV")
    if token_count(pkt) > MAX_PACKET_TOKENS:
        raise Rejected("BUDGET_EXCEEDED")
    if op == "P":
        if hid in state:
            raise Rejected("DUPLICATE_ID")
        if not pkt.get("src"):
            raise Rejected("NO_SRC")          # 🧾? sans source → ❌
        if not pkt.get("test"):
            raise Rejected("NO_TEST")
        return
    if hid not in state:
        raise Rejected("UNKNOWN_ID")
    cur = state[hid]
    if op in {"X", "A", "H", "J", "T"} and rev != cur["rev"]:
        raise Rejected(f"STALE_REV:{rev}!={cur['rev']}")   # C2
    if op == "R":
        if rev != cur["rev"] + 1:
            raise Rejected("REPAIR_MUST_INCREMENT_REV")
        patch = {k: v for k, v in pkt.items()
                 if k not in {"op", "id", "rev"}}
        if not patch or all(cur.get(k) == v for k, v in patch.items()):
            raise Rejected("NO_DELTA")        # UNCHANGED → OMIT
        if (cur["status"], "R") not in LEGAL:
            raise Rejected(f"ILLEGAL_TRANSITION:{cur['status']}+R")
        return
    if op == "A":
        scope = pkt.get("scope")
        if scope not in ACCEPT_SCOPES:
            raise Rejected(f"ACCEPT_NEEDS_SCOPE_T_F_C:{scope}")  # C1
    if op == "T" and "result" not in pkt:
        raise Rejected("TEST_NEEDS_RESULT")
    if (cur["status"], op) not in LEGAL:
        raise Rejected(f"ILLEGAL_TRANSITION:{cur['status']}+{op}")


def apply_packet(pkt, state, chain):
    """FABLE — scheduler: validate, transition, journal with chained hash."""
    validate(pkt, state)
    op, hid = pkt["op"], pkt["id"]
    if op == "P":
        state[hid] = {"rev": 0, "status": "PROPOSED",
                      "claim": pkt.get("rel"), "src": pkt["src"],
                      "test": pkt["test"]}
    elif op == "R":
        state[hid]["rev"] += 1
        state[hid]["status"] = "REVISED"
        for k, v in pkt.items():
            if k not in {"op", "id", "rev"}:
                state[hid][k] = v
    elif op == "T":
        state[hid]["status"] = ("CANDIDATE_SURVIVES"
                                if pkt["result"] == "pass" else "REJECTED")
    else:
        state[hid]["status"] = LEGAL[(state[hid]["status"], op)]
    h = hashlib.sha256((chain[-1] + canon(pkt)).encode()).hexdigest()
    chain.append(h)
    return h


def render_wul(pkt):
    """R_N — WULmoji projection of a wire packet (view, not state)."""
    head = WUL_PROJECTION[pkt["op"]]
    if pkt["op"] == "A":
        head += pkt["scope"]
    rest = {k: v for k, v in pkt.items() if k not in {"op"}}
    return head + " " + canon(rest)


def parse_wul(s):
    """P_N — fail-closed parser of the WUL projection."""
    head, _, rest = s.partition(" ")
    scope = None
    for glyph, op in sorted(WUL_REVERSE.items(), key=lambda x: -len(x[0])):
        if head.startswith(glyph):
            if op == "A":
                scope = head[len(glyph):]
                if scope not in ACCEPT_SCOPES:
                    raise Rejected("PARSE_BAD_SCOPE")
            pkt = json.loads(rest)
            pkt["op"] = op
            if scope:
                pkt["scope"] = scope
            return pkt
    raise Rejected("PARSE_UNKNOWN_HEAD")


def run_session():
    state, chain, log = {}, ["genesis:" + NAMESPACE], []

    legal = [
        {"op": "P", "id": "H3", "rev": 0, "rel": "PAIR_STRUCTURE",
         "src": "C17", "test": "JSD"},
        {"op": "X", "id": "H3", "rev": 0, "alt": "FREQ_EFFECT",
         "test": "MATCHED_NULL"},
        {"op": "R", "id": "H3", "rev": 1, "test": "JSD<q05",
         "null": "C1..C100", "match": "n,freq,pos"},
        {"op": "A", "id": "H3", "rev": 1, "scope": "T"},
        {"op": "T", "id": "H3", "rev": 1, "result": "pass"},
    ]
    for pkt in legal:
        rt = parse_wul(render_wul(pkt))
        assert rt == pkt, "ROUND_TRIP_BROKEN"          # C5
        apply_packet(pkt, state, chain)
        log.append(("OK", pkt["op"], state[pkt["id"]]["status"]))

    illegal = [
        ("P_no_src", {"op": "P", "id": "H4", "rev": 0,
                      "rel": "X", "test": "t"}),
        ("P_no_test", {"op": "P", "id": "H5", "rev": 0,
                       "rel": "X", "src": "s"}),
        ("stale_rev_attack", {"op": "X", "id": "H3", "rev": 0,
                              "alt": "late"}),
        ("accept_no_scope", {"op": "A", "id": "H3", "rev": 1}),
        ("accept_scope_TRUTH", {"op": "A", "id": "H3", "rev": 1,
                                "scope": "TRUTH"}),
        ("sovereign_field", {"op": "P", "id": "H6", "rev": 0, "rel": "x",
                             "src": "s", "test": "t", "verdict": "SHIP"}),
        ("cross_namespace", {"op": "P", "id": "H7", "rev": 0,
                             "rel": "état \U0001F7E2 admis",
                             "src": "s", "test": "t"}),
        ("empty_repair", {"op": "R", "id": "H3", "rev": 2}),
        ("unknown_op", {"op": "Z", "id": "H3", "rev": 1}),
        ("test_after_tested", {"op": "T", "id": "H3", "rev": 1,
                               "result": "pass"}),
    ]
    for name, pkt in illegal:
        try:
            apply_packet(pkt, state, chain)
            log.append(("LEAK", name, "ACCEPTED — FALSIFIED"))
        except Rejected as e:
            log.append(("REJECTED", name, str(e)))

    leaks = [l for l in log if l[0] == "LEAK"]
    return {"final_state": state, "chain_head": chain[-1],
            "chain_len": len(chain), "log": log,
            "type_system_holds": not leaks}


if __name__ == "__main__":
    r1, r2 = run_session(), run_session()
    print("REPLAY_MATCH" if r1["chain_head"] == r2["chain_head"]
          else "REPLAY_DIVERGED")                       # C6
    print("type_system_holds:", r1["type_system_holds"])
    print("H3 terminal:", r1["final_state"]["H3"]["status"],
          "rev", r1["final_state"]["H3"]["rev"])
    print("chain_head:", r1["chain_head"][:16],
          "packets_journaled:", r1["chain_len"] - 1)
    for entry in r1["log"]:
        print("  ", *entry)
    print("NOTE: EXECUTION_RECEIPT != EVIDENCE — this run certifies "
          "coherence of the type system, not usefulness of the protocol.")
