r"""Receipt Integrity — the kernel's membrane applied to its own
metadata.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.

    ReceiptText  !=>  ReceiptWitness  !=>  ReDerivableReceipt

The new primitive is not the receipt; it is its RE-DERIVABILITY:

    ReceiptClaim(c)  =>  exists P_c : P_c(substrate) -> c

An honorific claim about system state is institutionally receivable
only if a mechanical path reconstructs it from the substrate. The
reflexive closure of the constitutional root:

    DescriptionOfKernelState      !=>  KernelState
    ReceiptLikeRepresentation     !=>  InstitutionalReceipt

TYPED CLAIM CLASSES, each with its own re-derivation operator — the
same CROSS kernel with different discharge semantics:

    C_test    "N tests green"          R = RunTests()
    C_gate    "gate M/M · receipt X"   R = RunGate() twice
    C_commit  "commit X exists"        R = GitObjectExists(X)
    C_canon   "V0 canon intact"        R = RunSelfTest()
    C_pii     "NO_PII"                 R = PatternSweep()

TYPING PRECEDES VERIFICATION. HexLike(x) !=> GitHash(x): a string
that looks like a hash does not receive the type GitCommit — the G2
goblin's discipline (66836cb typed GIT_HASH and verified; the
16-char hexes typed GMAIL_THREAD_ID and NOT run through git as if
they were commits).

AGGREGATION IS BY CLASS, NEVER BY VOTE. "3/4 goblins say PASS" is a
category error: the goblins are instruments of DIFFERENT classes.
The audit is DISCHARGED only when every class is PASS; one PENDING
class makes it PARTIALLY_DISCHARGED, whatever the count.

RECEIPT INTEGRITY:

    RI(c) = T(c) and D(c) and S(c)

typed correctly, re-derivable from substrate, and SCOPED —
ReDerivable !=> UniversallyValid: "917 tests green" is valid only
under (suite, checkout, commit, environment, gate_version).

THE PROOF-CARRYING RECEIPT. A receipt is not a hash; it carries its
recipe:

    Receipt { claim, substrate_ref, derivation_recipe, environment,
              scope, result, digest }
    VerifyReceipt(r) = ReRun(r.recipe, r.substrate) =? r.result

THE SEAL PROTOCOL, four witnesses or no seal:

    IntentWitness (status/diff before) + TestWitness (suite before
    mutation) + MutationWitness (git show --stat HEAD) +
    PostMutationWitness (log -1 + empty status)

Kernel law: NO HONORIFIC SYSTEM-STATE CLAIM WITHOUT A RE-DERIVATION
PATH. A system should not merely keep receipts; it should be able to
re-derive why each receipt was deserved.

Deterministic: no wall-clock, no randomness, canonical serialization.
"""
from __future__ import annotations

import json

CLAIM_CLASSES = {
    "C_test": "RunTests()",
    "C_gate": "RunGate() twice (determinism)",
    "C_commit": "GitObjectExists(hash)",
    "C_canon": "RunSelfTest()",
    "C_pii": "PatternSweep()",
}

SCOPE_FIELDS = ("suite", "checkout", "commit", "environment",
                "gate_version")

RECEIPT_FIELDS = ("claim", "substrate_ref", "derivation_recipe",
                  "environment", "scope", "result", "digest")

SEAL_WITNESSES = ("intent", "test", "mutation", "post_mutation")

HEX_TYPES = ("GIT_HASH", "GMAIL_THREAD_ID", "DRIVE_ID", "DIGEST",
             "UNKNOWN")

FABRICATED = "FABRICATED_UNTIL_WITNESSED"


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


# ── typing precedes verification ───────────────────────────────────────

def type_hex(candidate: str, declared_type: str | None) -> dict:
    """HexLike(x) !=> GitHash(x). An untyped hex-like string may not
    be verified AS anything — the type is an input, never inferred
    from shape."""
    if declared_type is None:
        return {"verifiable": False, "reason": "E_UNTYPED_HEX",
                "law": "a string that looks like a hash does not "
                       "receive the type GitCommit; typing precedes "
                       "verification"}
    if declared_type not in HEX_TYPES:
        return {"verifiable": False, "reason": "E_UNKNOWN_HEX_TYPE"}
    return {"verifiable": declared_type != "UNKNOWN",
            "candidate": candidate, "type": declared_type,
            "verify_with": "GitObjectExists" if
                           declared_type == "GIT_HASH" else
                           f"{declared_type}-specific check"}


# ── re-derivation ──────────────────────────────────────────────────────

def re_derive(claim_class: str, recipe_ran: bool,
              result_matches: bool) -> dict:
    """ReDerive(c, K). No run, or a mismatch, leaves the claim
    FABRICATED_UNTIL_WITNESSED — an epistemic status, not an
    accusation."""
    if claim_class not in CLAIM_CLASSES:
        return {"status": None, "reason": "E_UNKNOWN_CLAIM_CLASS"}
    if not recipe_ran:
        return {"status": FABRICATED, "claim_class": claim_class,
                "reason": "E_RECIPE_NOT_RUN",
                "recipe": CLAIM_CLASSES[claim_class]}
    if not result_matches:
        return {"status": FABRICATED, "claim_class": claim_class,
                "reason": "E_REDERIVATION_MISMATCH"}
    return {"status": "PASS", "claim_class": claim_class,
            "recipe": CLAIM_CLASSES[claim_class]}


def receipt_integrity(typed: bool, rederivable: bool,
                      scope: dict) -> dict:
    """RI(c) = T(c) and D(c) and S(c). ReDerivable !=>
    UniversallyValid — the scope names where the claim is true."""
    missing = sorted(set(SCOPE_FIELDS) - set(scope))
    scoped = not missing
    ok = typed and rederivable and scoped
    return {"RI": ok,
            "T": typed, "D": rederivable, "S": scoped,
            "missing_scope": tuple(missing),
            "reason": None if ok else (
                "E_UNTYPED_CLAIM" if not typed else
                "E_NOT_REDERIVABLE" if not rederivable else
                "E_UNSCOPED_CLAIM"),
            "law": "a claim can be perfectly re-derivable and valid "
                   "only under a precise scope"}


# ── aggregation by class, never by vote ────────────────────────────────

def aggregate(class_results: dict, as_vote: bool = False) -> dict:
    """The goblins are instruments of DIFFERENT classes; a fraction
    across them is a category error."""
    if as_vote:
        return {"aggregated": False, "reason": "E_VOTE_ACROSS_CLASSES",
                "law": "3/4 goblins say PASS is a category error; "
                       "classes discharge independently"}
    unknown = sorted(set(class_results) - set(CLAIM_CLASSES))
    if unknown:
        return {"aggregated": False, "reason": "E_UNKNOWN_CLAIM_CLASS",
                "unknown": tuple(unknown)}
    pending = sorted(k for k, v in class_results.items()
                     if v == "PENDING")
    failed = sorted(k for k, v in class_results.items()
                    if v == FABRICATED)
    all_pass = not pending and not failed and \
        set(class_results) == set(CLAIM_CLASSES)
    partial = bool(pending) or set(class_results) != set(CLAIM_CLASSES)
    return {"aggregated": True,
            "per_class": dict(sorted(class_results.items())),
            "pending": tuple(pending), "failed": tuple(failed),
            "verdict": ("DISCHARGED" if all_pass else
                        (FABRICATED + "_IN_PART" if failed else
                         "PARTIALLY_DISCHARGED")),
            "note": None if not partial or failed else
                    "one pending class holds the whole audit open, "
                    "whatever the count"}


# ── the proof-carrying receipt ─────────────────────────────────────────

def proof_carrying_receipt(**f) -> dict:
    """A receipt is not a hash; it carries the recipe that re-derives
    it."""
    missing = sorted(set(RECEIPT_FIELDS) - set(f))
    if missing:
        return {"ok": False, "reason": "E_RECIPE_LESS_RECEIPT",
                "missing": tuple(missing),
                "law": "receipt = 65e58753... is a digest, not a "
                       "receipt; the recipe travels with the claim"}
    return {"ok": True, **{k: f[k] for k in RECEIPT_FIELDS}}


def verify_receipt(receipt: dict, rerun_result: str) -> dict:
    """VerifyReceipt(r) = ReRun(r.recipe, r.substrate) =? r.result."""
    if not receipt.get("ok"):
        return {"verified": False, "reason": "E_BAD_RECEIPT"}
    match = rerun_result == receipt["result"]
    return {"verified": match,
            "reason": None if match else "E_REDERIVATION_MISMATCH",
            "status": "PASS" if match else FABRICATED}


# ── the seal protocol ──────────────────────────────────────────────────

def seal(witnesses: frozenset) -> dict:
    """IntentWitness + TestWitness + MutationWitness +
    PostMutationWitness. git log -1 shows the current HEAD, not the
    relation between the targeted files and the claim — the mutation
    witness (git show --stat HEAD) is what binds them."""
    missing = sorted(set(SEAL_WITNESSES) - set(witnesses))
    if missing:
        return {"sealed": False, "reason": "E_INCOMPLETE_SEAL",
                "missing": tuple(missing),
                "status": FABRICATED}
    return {"sealed": True, "witnesses": SEAL_WITNESSES,
            "law": "a banner without the four witnesses is "
                   "typography"}


def reflexive_law() -> dict:
    return {"licensed": False,
            "non_implications": (
                "DescriptionOfKernelState !=> KernelState",
                "ReceiptLikeRepresentation !=> InstitutionalReceipt",
                "ReceiptText !=> ReceiptWitness",
                "ReceiptWitness !=> ReDerivableReceipt"),
            "law": "no honorific system-state claim without a "
                   "re-derivation path; the kernel applies its "
                   "membrane to its own metadata"}
