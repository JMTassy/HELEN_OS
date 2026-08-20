"""HAL_PARSER_V2 — enum-honest, fail-closed HAL verdict parser. authority=false · canon=false · ledger_effect=none.
NON-SOVEREIGN. Repairs the parse-rate fail-open the citation_composition differential exposed: the original
parse_strict counted a syntactically-valid-but-out-of-enum VERDICT ("INCONCLUSITIVE") as PARSED and coerced it to
INCONCLUSIVE, inflating parse_rate 0.9 -> 1.0.

FROZEN PARSE CONTRACT (fail-closed):
    malformed JSON                       -> PARSE_FAIL
    duplicate key                        -> PARSE_FAIL
    >1 top-level VERDICT object          -> PARSE_FAIL
    missing VERDICT field                -> PARSE_FAIL
    VERDICT value not in frozen enum     -> PARSE_FAIL   (no coercion to INCONCLUSIVE)
    prose masquerading as JSON           -> PARSE_FAIL
    valid JSON + VERDICT ∈ frozen enum   -> PARSE_OK (verdict preserved, incl. legitimate INCONCLUSIVE)

The enum is PROMPT-SCOPED (relay-vs-frozen-truth): the neutral prompt uses {ALLOW,REFUTED,INCONCLUSIVE};
the KILL/HAL-frame prompt uses {SURVIVED,REFUTED,INCONCLUSIVE}. So allowed_enum is a REQUIRED argument — the
parser never assumes a global enum. MalformedVerdict ⊬ Parsed. ParserCoercion ⊬ ContractValidity.
"""
import json, re

def _reject_dup(pairs):
    seen = {}
    for k, v in pairs:
        if k in seen:
            raise ValueError("duplicate_key")
        seen[k] = v
    return seen

def parse_enum_honest(text, allowed_enum):
    """Return (verdict_str, packet_dict) if PARSE_OK else (None, None). allowed_enum: iterable of UPPER verdicts."""
    allowed = {v.upper() for v in allowed_enum}
    t = re.sub(r"```(?:json)?", "", text or "")
    objs = []
    for m in re.finditer(r"\{", t):
        d = 0
        for j in range(m.start(), len(t)):
            if t[j] == "{":
                d += 1
            elif t[j] == "}":
                d -= 1
                if d == 0:
                    try:
                        c = json.loads(t[m.start():j+1], object_pairs_hook=_reject_dup)
                        if isinstance(c, dict) and "VERDICT" in c:
                            objs.append(c)
                    except Exception:
                        pass
                    break
    if len(objs) != 1:                       # 0 = no valid verdict object · >1 = multiple top-level -> FAIL
        return None, None
    c = objs[0]
    v = str(c.get("VERDICT", "")).upper()
    if v not in allowed:                     # INVALID_ENUM -> FAIL (the repair; no coercion)
        return None, None
    return v, c

# ── regression witness (the controls the fail-open lacked) ──
def self_test():
    NEUTRAL = ("ALLOW", "REFUTED", "INCONCLUSIVE")
    cases = [
        # (label, raw, allowed, expect_parse_ok, expect_verdict)
        ("real_malformed_INCONCLUSITIVE", '{"VERDICT":"INCONCLUSITIVE","REASON_CODE":"x","": "MEDIUM"}', NEUTRAL, False, None),
        ("gibberish_verdict_YE",          '{"VERDICT":"YE"}', NEUTRAL, False, None),
        ("gibberish_verdict",             '{"VERDICT":"gibberish"}', NEUTRAL, False, None),
        ("valid_ALLOW",                   '{"VERDICT":"ALLOW","REASON_CODE":"ok"}', NEUTRAL, True, "ALLOW"),
        ("valid_REFUTED",                 '{"VERDICT":"REFUTED"}', NEUTRAL, True, "REFUTED"),
        ("valid_INCONCLUSIVE",            '{"VERDICT":"INCONCLUSIVE"}', NEUTRAL, True, "INCONCLUSIVE"),
        ("lowercase_allow_ok",            '{"VERDICT":"allow"}', NEUTRAL, True, "ALLOW"),
        ("fenced_valid",                  '```json\n{"VERDICT":"REFUTED"}\n```', NEUTRAL, True, "REFUTED"),
        ("missing_verdict",               '{"REASON_CODE":"x"}', NEUTRAL, False, None),
        ("duplicate_key",                 '{"VERDICT":"ALLOW","VERDICT":"REFUTED"}', NEUTRAL, False, None),
        ("multiple_objects",              '{"VERDICT":"ALLOW"} {"VERDICT":"REFUTED"}', NEUTRAL, False, None),
        ("prose_not_json",                'The verdict is ALLOW because sources license it.', NEUTRAL, False, None),
        ("empty",                         '', NEUTRAL, False, None),
        # prompt-scoped enum: SURVIVED valid ONLY under KILL frame, NOT neutral
        ("survived_under_neutral_FAIL",   '{"VERDICT":"SURVIVED"}', NEUTRAL, False, None),
        ("survived_under_kill_OK",        '{"VERDICT":"SURVIVED"}', ("SURVIVED","REFUTED","INCONCLUSIVE"), True, "SURVIVED"),
    ]
    rows, allok = [], True
    for label, raw, allowed, exp_ok, exp_v in cases:
        v, c = parse_enum_honest(raw, allowed)
        ok = (v is not None)
        passed = (ok == exp_ok) and (v == exp_v)
        allok &= passed
        rows.append((label, ok, v, exp_ok, exp_v, passed))
    return allok, rows

if __name__ == "__main__":
    allok, rows = self_test()
    print("=== HAL_PARSER_V2 — fail-closed enum-honest parser · regression ===")
    for label, ok, v, eok, ev, passed in rows:
        print(f"  {label:32} parse_ok={str(ok):5} verdict={str(v):13} expect(ok={str(eok):5},v={str(ev):13}) -> {'PASS' if passed else 'FAIL'}")
    print(f"\n  REGRESSION_ALL_PASS = {allok}")
    print("  contract: MalformedVerdict ⊬ Parsed · enum is prompt-scoped · no coercion")
    print("  authority=false · canon=false · ledger_effect=none")
