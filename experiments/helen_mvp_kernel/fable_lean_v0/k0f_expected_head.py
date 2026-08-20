"""K0f — EXPECTED HEAD (linearizable compare-and-swap commit). authority=false · canon=false · ledger_effect=none.
NON-SOVEREIGN. Extends K0e's single-χ transition with the commit-time head boundary:

    Commit(delta, h) succeeds  ONLY IF  h == Head_at_commit_time      (atomic CAS)

The diamond:
    H0 --delta_A--> H1        (A commits, head advances H0 -> H1)
    delta_B built with expectedHead = H0   (stale)
    Apply(delta_B, H1)  ==>  STALE_HEAD

Earned K0f condition (all four, or the property is NOT witnessed):
    STALE_HEAD  ∧  sigma_after == sigma_before  ∧  H_after == H_before  ∧  no-history-append-for-B

TOCTOU sharpening: checking the head during VERIFY and mutating later is a hole. The correct reducer re-reads the
head AT COMMIT. A naive reducer that trusts the verify-time head is included as a FALSIFICATION CONTROL — it must
be shown to admit the stale delta (i.e. the test has teeth; the property is not trivially true).

FailClosed ≠ RefuseEverything: a delta with the CORRECT current head still commits (control 4). Rejection is
head-specific, not blanket refusal.
"""
import hashlib, json

def canonical(d): return json.dumps(d, sort_keys=True, separators=(",", ":"))
def chi(d): return "sha256:" + hashlib.sha256(canonical(d).encode()).hexdigest()[:16]

class Ledger:
    """Append-only chain. head_{n+1} = sha256(head_n | chi(delta)). Commit is an atomic CAS on the head."""
    GENESIS = "sha256:" + "0" * 16
    def __init__(self):
        self._head = self.GENESIS
        self._state = set()
        self._history = []
    def head(self): return self._head
    def state_hash(self): return "sha256:" + hashlib.sha256("|".join(sorted(self._state)).encode()).hexdigest()[:16]
    def _advance(self, c): return "sha256:" + hashlib.sha256(f"{self._head}|{c}".encode()).hexdigest()[:16]

    def commit_atomic(self, delta, expected_head):
        """CORRECT reducer: read head NOW, compare, then (only on match) mutate + append. One indivisible step."""
        c = chi(delta)
        if expected_head != self._head:                       # commit-time compare-and-swap
            return {"decision": "REJECT", "reason": "STALE_HEAD",
                    "expected": expected_head, "actual_head": self._head, "chi": c}
        new_head = self._advance(c)
        self._state.add(f"admitted:{c}")                      # mutate state
        self._history.append({"chi": c, "prev": self._head, "head": new_head})  # append history
        self._head = new_head
        return {"decision": "ADMIT", "reason": "HEAD_MATCH", "head": new_head, "chi": c}

    def commit_verify_time_head(self, delta, verify_time_head):
        """NAIVE/BROKEN reducer (TOCTOU control): trusts the head captured at verify time; never re-reads at commit.
        Left in ONLY to prove the falsifier has teeth. This is the hole K0f must exclude."""
        c = chi(delta)
        # BUG: compares against the stale verify-time snapshot, not self._head at commit
        if verify_time_head != verify_time_head:  # vacuously true guard -> effectively no live check
            return {"decision": "REJECT", "reason": "STALE_HEAD", "chi": c}
        new_head = self._advance(c)
        self._state.add(f"admitted:{c}")
        self._history.append({"chi": c, "prev": self._head, "head": new_head})
        self._head = new_head
        return {"decision": "ADMIT", "reason": "TRUSTED_VERIFY_TIME_HEAD", "head": new_head, "chi": c}

def snap(L): return (L.state_hash(), L.head(), len(L._history))

def main():
    print("=== K0f — expected-head compare-and-swap commit ===")
    A = {"op": "promote", "subject": "campus", "scope": "corsica", "n": 1}
    B = {"op": "promote", "subject": "campus", "scope": "corsica", "n": 2}
    C = {"op": "promote", "subject": "campus", "scope": "corsica", "n": 3}
    rows = []

    # ---- 1. VALID CONTROL: A commits against genesis head ----
    L = Ledger(); H0 = L.head()
    r1 = L.commit_atomic(A, expected_head=H0)
    H1 = L.head()
    p1 = (r1["decision"] == "ADMIT" and H1 != H0 and len(L._history) == 1)
    rows.append(("1_VALID_CONTROL_A@H0", p1, r1["decision"], r1["reason"]))
    print(f"  1_VALID_CONTROL_A@H0     {r1['decision']:6}/{r1['reason']:22} head {H0[-6:]}->{H1[-6:]}  {'PASS' if p1 else 'FAIL'}")

    # ---- 2. STALE-HEAD ATTACK: B built with expectedHead=H0, applied after head advanced to H1 ----
    sb = snap(L)                                   # state/head/history BEFORE the rejected attempt
    r2 = L.commit_atomic(B, expected_head=H0)       # stale expected head
    sa = snap(L)                                    # AFTER
    earned = (r2["decision"] == "REJECT" and r2["reason"] == "STALE_HEAD"
              and sa[0] == sb[0]                     # sigma_after == sigma_before
              and sa[1] == sb[1]                     # H_after == H_before
              and sa[2] == sb[2])                    # no history append for B
    rows.append(("2_STALE_HEAD_B@H0", earned, r2["decision"], r2["reason"]))
    print(f"  2_STALE_HEAD_B@H0        {r2['decision']:6}/{r2['reason']:22} exp={r2['expected'][-6:]} actual={r2['actual_head'][-6:]}"
          f"  σ{'=' if sa[0]==sb[0] else '≠'} H{'=' if sa[1]==sb[1] else '≠'} hist{'=' if sa[2]==sb[2] else '+'}  {'PASS' if earned else 'FAIL'}")

    # ---- 3. TOCTOU: verify B while head=H0, A' advances head, commit B at commit-time ----
    L3 = Ledger(); H0b = L3.head()
    verify_time_head = L3.head()                    # B verified against H0b (stale-to-be)
    L3.commit_atomic(C, expected_head=H0b)          # an interleaved commit advances the head H0b->H1b
    H1b = L3.head()
    sb3 = snap(L3)
    r3_correct = L3.commit_atomic(B, expected_head=verify_time_head)  # correct: re-reads head at commit
    sa3 = snap(L3)
    correct_rejects = (r3_correct["decision"] == "REJECT" and r3_correct["reason"] == "STALE_HEAD"
                       and sa3 == sb3)
    # falsification control: naive reducer trusts verify-time head -> ADMITS the stale delta (the hole)
    L3b = Ledger(); h0 = L3b.head(); vth = L3b.head()
    L3b.commit_atomic(C, expected_head=h0)          # head advances
    r3_naive = L3b.commit_verify_time_head(B, verify_time_head=vth)
    naive_admits = (r3_naive["decision"] == "ADMIT")
    p3 = correct_rejects and naive_admits           # test has teeth: correct rejects AND naive would corrupt
    rows.append(("3_TOCTOU_commit_vs_verify", p3, r3_correct["decision"], r3_correct["reason"]))
    print(f"  3_TOCTOU_commit_vs_verify correct={r3_correct['decision']:6}/{r3_correct['reason']:12} "
          f"naive={r3_naive['decision']}({r3_naive['reason']})  teeth={'YES' if naive_admits else 'NO'}  {'PASS' if p3 else 'FAIL'}")

    # ---- 4. FRESH HEAD: B rebuilt with the CORRECT current head H1 still commits (FailClosed≠RefuseEverything) ----
    Hnow = L.head()
    r4 = L.commit_atomic(B, expected_head=Hnow)
    p4 = (r4["decision"] == "ADMIT" and L.head() != Hnow)
    rows.append(("4_FRESH_HEAD_B@H1", p4, r4["decision"], r4["reason"]))
    print(f"  4_FRESH_HEAD_B@H1        {r4['decision']:6}/{r4['reason']:22} head ->{L.head()[-6:]}  {'PASS' if p4 else 'FAIL'}  (rejection is head-specific, not blanket)")

    allok = all(p for _, p, _, _ in rows)
    print(f"\n  K0f = {'SURVIVED_DEFINED_ATTACK_SET' if allok else 'FALSIFIED'}  ({sum(p for _,p,_,_ in rows)}/{len(rows)})")
    print("  earned: STALE_HEAD ∧ σ_after=σ_before ∧ H_after=H_before ∧ no-history-append; commit-time CAS closes TOCTOU;")
    print("          fresh-head delta still commits (FailClosed≠RefuseEverything).")
    print("  property: Commit(δ,h) succeeds only if h==Head_at_commit_time.  Verify licenses a candidate; only the")
    print("            atomic head comparison licenses its commit.")
    print("  authority=false · canon=false · ledger_effect=none")
    return allok

if __name__ == "__main__":
    main()
