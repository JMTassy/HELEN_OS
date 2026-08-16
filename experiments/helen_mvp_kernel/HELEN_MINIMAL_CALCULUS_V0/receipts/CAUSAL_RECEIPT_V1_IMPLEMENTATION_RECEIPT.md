# CAUSAL_RECEIPT_V1 — IMPLEMENTATION RECEIPT (witnessed 2026-08-16)

W_CR1 = ( T3_head      = 478be0e
        , commit_CR1   = <this commit>
        , nu           = sha256:eff29d80be0091c0/CR1
        , schema       = h_C(r) = SHA256( nu || canon(body) || canon(sort{h_C(p)}) )
        , hashAlg      = SHA-256, full digest, parents as unordered sorted set
        , tests        = C1..C10 — WITNESS PASS 10/10 (causal_receipt_witness.py)
        , fixtures     = well-formed DAG + broken DAG + cyclic import + legacy chain,
                         replay via real BoundedExecutor, seeded LinExt sampling
        , migration    = linear_v0 -> V1 causal CHAIN (fail-closed: no antichain
                         invented where independence was never declared),
                         explicit per-receipt provenance {source, seq}
        , rollback     = additive-only: legacy representation byte-identical
                         after migration; discarding V1 loses nothing )

Identities kept distinct and WITNESSED distinct (C8):
  H_bytes != H_causal != H_semantic
  (two exports: bytes differ, causal identity equal, replay state equal)

CLAIM (exact):  Proof(T3 @ 478be0e)  +  Evidence(CR1 |= T3 assumptions)
NOT CLAIMED:    "T3 proved CAUSAL_RECEIPT_V1" · production-scale evidence ·
                anything beyond these fixtures, this seat, this nu.

---
## ADOPTION PACKET (for MAYOR routing — pending ROUTE verb)

CAUSAL_RECEIPT_V1_ADOPTION
  FORMAL_BASE      T3 ladder @ 478be0e (L1-L4', axiom audits archived)   [OK]
  IMPLEMENTATION   causal parent DAG / deterministic nu-bound hash /
                   replay harness                                        [OK]
  ADVERSARIAL      missing-parent [C1] · cycle [C2] · reordered
                   serialization [C8] · missing-edge [C6] ·
                   no-auto-repair [C7]                                   [OK]
  OPERATIONS       migration [C9] · rollback [C10]                       [OK]
  REQUEST          adopt CAUSAL_RECEIPT_V1 for the sovereign spine?
  DEFAULT          HOLD if any witness absent
  worker authority DENY · adoption = MAYOR decision · this shell does not
  and cannot write the sovereign ledger/schemas (firewalled).
