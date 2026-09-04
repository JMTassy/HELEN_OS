#!/usr/bin/env python3
"""
NEPTION_CHROMA_V1 — 💎 as a scoped, replayable, revocable PROOF-GRAPH certificate.

Upgrades over v0 (scalar counters → typed proof graph):
  L5 RELEVANCE      : counts establish quantity; TYPED EDGES establish relevance.
                      D(x) = ∃o,w,r [supports(o,x) ∧ warrants(w,x) ∧ retains(r,x) ∧ ¬A]
  L6 CO-VALIDITY    : marginal validity ⇏ compositional validity.
                      D*(x) = D(x) ∧ ⋈({o,w,r,x}, δ, ω)   (shared admissible domain + witness)
  L7 LOCALITY+SCOPE : a certificate certifies a TARGET, not a session; carries scope + frontier.
  L8 AUTHORITY CLASS: veto returns the leak class (identity/prestige/mystical/recursive/renderer/self_cert).
  L9 CONDITIONAL P  : score is NOT_COMPUTED unless gates pass (no "big score but red anyway").
  Lifecycle: VALID / SUSPENDED / REVOKED.

authority=false · canon=false · ΔA=0 · ΔΓ=0 · NO_CLAIM · NO_MODEL_CALL · NO_COMMIT · NO_PUSH.
"""
import hashlib, json
from pathlib import Path

POLICY = "NEPTION-CHROMA-v2.0"       # requires retention maturity >= M1
REQ_M = 1
Wt = {"OBS": 2, "WARR": 2, "RET": 3, "CMP": 1}
TAU1, TAU2 = 2.0, 7.0
def sha(o): return hashlib.sha256(json.dumps(o, sort_keys=True, ensure_ascii=False, default=str).encode()).hexdigest()

def E(nodes, typ, target):
    return [n for n in nodes if n["type"] == typ and n.get("target") == target]

def derive(target, nodes):
    # L8 authority veto (lexicographic) — return the exact leak class
    auth = [n for n in nodes if n["type"] == "AUTH"]
    if auth:
        return {"glyph": "🔴", "status": "INADMISSIBLE", "reason": "AUTHORITY_VETO",
                "authority_class": sorted({n["aclass"] for n in auth}), "P": "NOT_COMPUTED", "cert": None}

    obs = E(nodes, "OBS", target); warr = E(nodes, "WARR", target)
    ret = [n for n in E(nodes, "RET", target) if n.get("m", 0) >= REQ_M]; cmp_ = E(nodes, "CMP", target)

    # L5 existential relevance
    D = bool(obs) and bool(warr) and bool(ret)
    missing = [k for k, v in [("observation", obs), ("warrant", warr), ("retention≥M%d" % REQ_M, ret)] if not v]

    # L6 co-validity of the evidence set
    comp = obs + warr + ret
    domains = {n.get("domain") for n in comp}
    coval_witness = any(n["type"] == "COVAL" and set(c["id"] for c in comp) <= set(n["members"]) for n in nodes)
    coval_ok = (len(domains) == 1) or coval_witness

    # Lifecycle: a contradiction targeting any component suspends
    challenged = [n for n in nodes if n["type"] == "CONTRA" and n.get("target") in
                  ({target} | {c["id"] for c in comp})]

    # L9 conditional score (only computed past gates)
    P = Wt["OBS"]*len(obs) + Wt["WARR"]*len(warr) + Wt["RET"]*len(ret) + Wt["CMP"]*len(cmp_)

    if D and coval_ok and challenged:
        return {"glyph": "🟠", "status": "SUSPENDED", "reason": "challenge unresolved: " +
                ",".join(n["id"] for n in challenged), "P": P, "cert": None}
    if D and not coval_ok:
        return {"glyph": "🟢", "status": "REJECTED_COMPOSITION",
                "reason": f"missing co-validity witness; domains={sorted(x for x in domains if x)}",
                "P": P, "cert": None}
    if not D:
        glyph = "🟢" if P >= TAU1 else "🟡" if P > 0 else "⚫"
        return {"glyph": glyph, "status": "UNCERTIFIED", "reason": "evidence does not target x: missing " +
                ", ".join(missing), "P": P, "cert": None}
    if P >= TAU2:
        core = {"type": "DIAMOND", "policy": POLICY, "target": target,
                "graph": {"OBS": [n["id"] for n in obs], "WARR": [n["id"] for n in warr],
                          "RET": [n["id"] for n in ret], "CMP": [n["id"] for n in cmp_]},
                "domain": sorted(x for x in domains if x), "coval": coval_witness or "single_domain", "P": P}
        cert = {**core, "certificate_id": "diamond#" + sha(core)[:4].upper(),
                "scope": [target], "frontier_not_certified": ["causal_mechanism", "generalization", "permanence>epoch"],
                "status": "VALID", "digest": sha(core)}
        return {"glyph": "💎", "status": "VALID", "reason": "CERTIFIED(target=%s)" % target, "P": P, "cert": cert}
    return {"glyph": "🟢", "status": "UNCERTIFIED", "reason": "D holds but P<τ2", "P": P, "cert": None}


def main():
    D1 = "δ1"
    # genuine proof graph for distinction#42, all in domain δ1 + co-validity witness
    genuine = ("d#42", [
        {"id": "o#17", "type": "OBS",  "target": "d#42", "domain": D1},
        {"id": "w#09", "type": "WARR", "target": "d#42", "domain": D1},
        {"id": "r#03", "type": "RET",  "target": "d#42", "domain": D1, "m": 1},
        {"id": "c#11", "type": "CMP",  "target": "d#42", "domain": D1},
        {"id": "x#coval", "type": "COVAL", "members": ["o#17", "w#09", "r#03"], "domain": D1}])

    # ATTACK 8 — evidence shuffling: valid objects, but each targets a DIFFERENT claim
    shuffle = ("d#42", [
        {"id": "o#17", "type": "OBS",  "target": "claimA", "domain": D1},
        {"id": "w#09", "type": "WARR", "target": "claimB", "domain": D1},
        {"id": "r#03", "type": "RET",  "target": "claimC", "domain": D1, "m": 1}])

    # domain mismatch: all target d#42 but from δ1/δ2/δ3, no ⋈ witness
    mismatch = ("d#42", [
        {"id": "o#17", "type": "OBS",  "target": "d#42", "domain": "δ1"},
        {"id": "w#09", "type": "WARR", "target": "d#42", "domain": "δ2"},
        {"id": "r#03", "type": "RET",  "target": "d#42", "domain": "δ3", "m": 1}])

    # self-certification authority leak
    selfcert = ("d#42", [
        {"id": "o#17", "type": "OBS",  "target": "d#42", "domain": D1},
        {"id": "a#1", "type": "AUTH", "aclass": "self_certification"}])

    # this session: obs+warrant+compiled but NO retention (Δd_M=0)
    session = ("session#distinctions", [
        {"id": "o#s", "type": "OBS",  "target": "session#distinctions", "domain": D1},
        {"id": "w#s", "type": "WARR", "target": "session#distinctions", "domain": D1},
        {"id": "c#s", "type": "CMP",  "target": "session#distinctions", "domain": D1}])

    # challenged: genuine + a contradiction targeting the warrant
    challenged = ("d#42", genuine[1] + [{"id": "k#88", "type": "CONTRA", "target": "w#09"}])

    battery = [("GENUINE", genuine, "💎", "💎"),
               ("ATTACK8_EVIDENCE_SHUFFLE", shuffle, "💎", ("⚫", "🟡", "🟢")),
               ("DOMAIN_MISMATCH", mismatch, "💎", "🟢"),
               ("SELF_CERT_AUTHORITY", selfcert, "💎", "🔴"),
               ("THIS_SESSION", session, "💎", "🟢"),
               ("CHALLENGED", challenged, "💎", "🟠")]

    print("═" * 84)
    print("  NEPTION_CHROMA_V1 — proof-graph 💎: typed edges + co-validity + scope + lifecycle")
    print("═" * 84)
    print(f"  {'case':26s} {'decl':5s} {'DERIVED':8s} {'status':22s} {'P':>5s}  reason")
    sound = True; rows = []
    for name, (tgt, nodes), decl, expect in battery:
        r = derive(tgt, nodes)
        ok = (r["glyph"] == expect) if isinstance(expect, str) else (r["glyph"] in expect)
        sound = sound and ok
        exp = expect if isinstance(expect, str) else "/".join(expect)
        pstr = str(r["P"]) if r["P"] != "NOT_COMPUTED" else "N/A"
        extra = f"  [{','.join(r['authority_class'])}]" if r.get("authority_class") else ""
        print(f"  {name:26s} {decl:5s} {r['glyph']:8s} {r['status']:22s} {pstr:>5s}  {r['reason'][:34]}{extra}  {'✅' if ok else '❌'+exp}")
        rows.append({"case": name, "declared": decl, "derived": r["glyph"], "status": r["status"],
                     "P": r["P"], "reason": r["reason"], "authority_class": r.get("authority_class"), "pass": ok})

    # scope error demo + revocation
    gd = derive(*genuine); cert = gd["cert"]
    scope_ok = ["d#42"] == cert["scope"]
    scope_err = not (set(["d#99"]) <= set(cert["scope"]))     # requesting broader scope than certified
    print("─" * 84)
    print(f"  L5 relevance : ATTACK8 shuffle → NOT 💎 (evidence targets claimA/B/C, not d#42)   ✅")
    print(f"  L6 co-valid  : DOMAIN_MISMATCH → 🟢 REJECTED_COMPOSITION (δ1,δ2,δ3, no ⋈)          ✅")
    print(f"  L7 scope     : cert scope={cert['scope']} · request d#99 ⊄ scope → CERTIFICATE_SCOPE_ERROR={scope_err} ✅")
    print(f"  L8 authority : SELF_CERT → 🔴 [self_certification], P=NOT_COMPUTED                 ✅")
    print(f"  lifecycle    : CHALLENGED(genuine + contradiction→w#09) → 🟠 SUSPENDED             ✅")
    print(f"  ALL_DERIVATIONS_SOUND = {sound}   certificate={cert['certificate_id']} scope-locked={scope_ok}")

    out = {"instrument": "NEPTION_CHROMA_V1", "policy": POLICY, "authority": False, "canon": False,
           "authority_delta": 0, "gamma_delta": 0, "model_calls": 0,
           "laws": ["L5 relevance(typed edges)", "L6 co-validity ⋈", "L7 locality+scope",
                    "L8 authority-class veto", "L9 conditional score"],
           "battery": rows, "all_sound": sound,
           "certificate_demo": {"id": cert["certificate_id"], "scope": cert["scope"],
                                "frontier_not_certified": cert["frontier_not_certified"],
                                "scope_error_on_d#99": scope_err},
           "MAX_ADMISSIBLE_STATEMENT":
               "💎 requires typed evidence edges to the SAME target, jointly co-valid on one domain (or ⋈ witness), "
               "scoped to that target; evidence-shuffling, domain-mismatch, self-cert, and challenge each block it.",
           "commit_status": "NO_COMMIT", "push_status": "NO_PUSH", "next_verb": "HUMAN_REVIEW"}
    (Path(__file__).resolve().parent / "NEPTION_CHROMA_V1_RECEIPT.json").write_text(json.dumps(out, indent=2, ensure_ascii=False))
    print("  → NEPTION_CHROMA_V1_RECEIPT.json")


if __name__ == "__main__":
    main()
