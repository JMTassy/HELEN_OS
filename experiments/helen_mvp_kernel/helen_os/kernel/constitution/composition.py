"""Four-Ceiling Compositional Closure — the real attack surface.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.

The corrected conjecture. Time is NOT the fifth ceiling; time belongs
in the evaluation context of the existing predicates (the ABAC move:
authorization depends on subject, object, operation and environmental
conditions). The attack surface is COMPOSITION:

    exists tau = d1 o ... o dn :
        (forall i. Admit(d_i, r_i) = 1)  AND  Admit*(tau) = 0

Several individually lawful moves composing into an unlawful one.

THE DISCIPLINE ON A HIT (the operator's constraint, and the point of
this module): finding such a tau does NOT earn a fifth ceiling. It
first earns a diagnosis — was Proof, Scope, Authority or Replay merely
defined NON-COMPOSITIONALLY? Only a tau that passes all four
predicates BOTH locally AND compositionally, and is still invalid,
is evidence of a genuinely new invariant.

Three adversarial traces are encoded, one per suspected
non-compositional predicate:

  T-FLOW    A reads X; B trans