# CROSS_SESSION_FIELD_ATTRIBUTION_V0

**authority:** NON_SOVEREIGN
**canon:** NO_SHIP
**lifecycle:** DOCTRINE_DRAFT
**implementation_status:** NOT_IMPLEMENTED
**status:** Proposal — long-flagged prerequisite, now bottled
**flagged_in:** `GOVERNANCE/TRANCHE_RECEIPTS/E22-hal-phantom-blocker-audit-V1.json`, `docs/proposals/PROVENANCE_GRAVITY_V0.md §8`, `docs/proposals/BOUNDARY_CATALYST_ENGINE_V0.md §15`, operator dispatch 2026-05-23
**proposer:** claude-opus-4-7 acting as GOBLIN
**attestor:** pending HER

> **The doctrine this proposal codifies has been *load-bearing for
> three other proposals* without itself being on disk. Each of the
> bottling doctrines above carries an explicit warning: without
> tree-truth attribution per receipt, the routing field poisons
> itself. This bottle removes the dependency hazard.**

---

## §1. The hard law

```
NO_TREE_TRUTH    = NO_GRAVITY
NO_PROVENANCE    = NO_BOUNDARY_WEIGHT
NO_ATTRIBUTION   = NO_ROUTING_PRIOR
```

A receipt without a verified tree-truth marker cannot be weighted into
any routing prior. Period. This invariant is non-negotiable; weakening
it admits poisoning of the constitutional metabolism described in
`PROVENANCE_GRAVITY_V0` and `BOUNDARY_CATALYST_ENGINE_V0`.

---

## §2. The problem in concrete form

`E22-hal-phantom-blocker-audit-V1.json` discovered that
`GOVERNANCE/TRANCHE_RECEIPTS/E20-hal-mayor-ship-gate-V1.json` files
some receipts whose evidence was authored against a **parallel
session** (`~/Documents/GitHub/helen_os_v1/`, cum_hash
`b3415eb3edfb`) — not against `helen-conquest`'s branch.

Two confirmed phantoms:

- `E20.open_seams.SEAM-001-C12` — schemas/ never existed in this branch
- `E20.open_seams.Knowledge_Compiler_V2_ratification` — commit `6eede55`
  doesn't exist on any branch of this repo

Contamination scope per `E23.SE8`: **≥10 files** reference parallel
session by known markers. Real scope is uncountable from inside the
tree (E23 SE8 was a lower bound).

The pattern is **per-field**, not per-document. A single receipt
may have body fields faithful to this tree and `open_seams` fields
faithful to a different tree. Per-document attribution is too coarse.

---

## §3. What "tree truth" means

A field is **tree-true** for tree `T` if all of:

1. Every claim about disk state in the field is verifiable on `T`
   (files exist, commits resolve, hashes match)
2. Every claim about prior receipts in the field references a receipt
   that itself is tree-true for `T`
3. The field carries an explicit `tree_truth_id` that resolves to
   `T`'s identity

Tree identity is established by:

```
tree_truth_id = sha256(
    canonical_repo_url + ":" +
    canonical_branch_name + ":" +
    fork_root_commit_sha
)
```

`fork_root_commit_sha` is the most recent ancestor commit shared with
every other tree's history. For trees that diverged from a common
parent, this is the divergence point. For trees authored without a
common parent, the `fork_root_commit_sha` is `"orphan"` and the trees
are considered fully distinct.

For `helen-conquest@claude/launch-helen-os-0xZXH`:

```
tree_truth_id = sha256(
    "github.com/jmtassy/helen-conquest:" +
    "claude/launch-helen-os-0xZXH:" +
    <fork-root-commit>
)
```

For `helen_os_v1`:

```
tree_truth_id = sha256(
    "<helen_os_v1 origin URL>:" +
    "<helen_os_v1 default branch>:" +
    <its-fork-root-commit>
)
```

The two `tree_truth_id` values are distinct sha256 strings. Cross-
referencing one from the other requires explicit foreign-tree markers.

---

## §4. Per-receipt schema additions

Every receipt (existing or new) must carry:

```json
{
  "tree_truth_id": "<sha256>",
  "session_id": "<conversation/session identifier>",
  "source_commit_hash": "<git rev-parse HEAD at receipt-write time>",
  "fields_tree_attribution": {
    "<field_name>": "<tree_truth_id of authoring tree>",
    "...": "..."
  }
}
```

The `fields_tree_attribution` map is **per-field**, not per-document.
A receipt may have:

```json
{
  "tree_truth_id": "<helen-conquest tree id>",
  "fields_tree_attribution": {
    "hypothesis": "<helen-conquest tree id>",
    "experiment": "<helen-conquest tree id>",
    "open_seams.SEAM-001-C12": "<helen_os_v1 tree id>",
    "open_seams.Knowledge_Compiler_V2_ratification": "<helen_os_v1 tree id>"
  }
}
```

This is the schema-level fix for the per-field contamination pattern.

---

## §5. Verification rules

For each field's claimed `tree_truth_id`, automated verification
checks:

| Claim type | Verification |
| --- | --- |
| File path claim | Path exists on the claimed tree's HEAD |
| Commit reference | Commit resolves on the claimed tree |
| Hash claim (cum_hash, file sha) | Recomputed hash matches |
| Receipt reference | Referenced receipt is itself tree-true for the claimed tree |
| Test result | Test exists and produces the claimed result on the claimed tree's HEAD (or a named ref) |

A field is `tree_truth_verified: true` only if **all** its claims pass
verification. Otherwise: `tree_truth_verified: false` with a
`failed_checks` enumeration.

---

## §6. Quarantine policy

Fields that fail verification fall into one of three buckets:

| Bucket | Definition | Routing-prior effect |
| --- | --- | --- |
| `TREE_TRUE` | All claims verified on the field's tree | Eligible for full routing weight |
| `FOREIGN_VERIFIED` | All claims verified, but on a DIFFERENT tree from the receipt's `tree_truth_id` | Eligible for foreign-tree weight (configurable; default zero) |
| `QUARANTINE` | One or more claims unverified on any reachable tree | **Zero weight**. Cannot contribute to Provenance Gravity or Boundary Catalysis. |

The hard law in §1 means `QUARANTINE` fields have zero contribution
regardless of operator preference. Operators can adjust
`FOREIGN_VERIFIED` weight (full, partial, zero) but cannot lift
`QUARANTINE` weight above zero without first re-verifying the field
against some tree's truth.

---

## §7. Migration path for existing receipts

The receipts currently on disk in `GOVERNANCE/TRANCHE_RECEIPTS/`
(E12 through E24) and `docs/proposals/` were authored before this
doctrine. Migration is **non-mutating**: existing files are not
edited. Instead, a sidecar file is added:

```
GOVERNANCE/TRANCHE_RECEIPTS/E20-hal-mayor-ship-gate-V1.json
GOVERNANCE/TRANCHE_RECEIPTS/E20-hal-mayor-ship-gate-V1.attribution.json
```

The sidecar carries the `fields_tree_attribution` map plus per-field
verification results, dated to the migration pass.

For known phantoms (E20.open_seams.SEAM-001-C12, etc.), the sidecar
sets:

```json
{
  "fields_tree_attribution": {
    "mayor_decision.post_ship_status.open_seams.SEAM-001-C12":
      "<helen_os_v1 tree id>",
    "mayor_decision.post_ship_status.open_seams.Knowledge_Compiler_V2_ratification":
      "<helen_os_v1 tree id>"
  },
  "verification_results": {
    "...SEAM-001-C12": {
      "tree_truth_verified": false,
      "failed_checks": ["schemas/ does not exist on helen-conquest HEAD"],
      "verified_on": "<helen_os_v1 tree id>",
      "bucket": "FOREIGN_VERIFIED"
    },
    "...Knowledge_Compiler_V2_ratification": {
      "tree_truth_verified": false,
      "failed_checks": ["commit 6eede55 does not exist on any branch of helen-conquest"],
      "verified_on": null,
      "bucket": "QUARANTINE"
    }
  }
}
```

The migration pass is itself a tranche-class operation and produces
its own receipt.

---

## §8. Why this must bottle first

`PROVENANCE_GRAVITY_V0` says receipts bend future action through trust
weights. If poisoned (parallel-session) receipts are weighted, the
agent learns trust in actions it never performed.

`BOUNDARY_CATALYST_ENGINE_V0` says boundary atoms generate
high-information motifs. If those atoms come from a different tree,
the motif engine mines patterns the current tree never produced.

Both doctrines have explicit `provenance_purity` terms in their
scoring functions. Without this proposal, the `provenance_purity`
factor is undefined — there is no algorithm for computing it. With
this proposal:

```
provenance_purity(receipt) =
  | { fields_with_tree_truth_verified == true } | /
  | { all_fields_in_receipt } |
```

A receipt with 100% tree-true fields has `provenance_purity == 1.0`.
A receipt with quarantined fields has `provenance_purity < 1.0` and
is downweighted (or zero-weighted via the hard law).

This proposal is the algorithmic foundation that makes the
`provenance_purity` term in §3.4 of `BOUNDARY_CATALYST_ENGINE_V0`
and §3 of `PROVENANCE_GRAVITY_V0` actually computable.

---

## §9. Connection to existing canon

| Existing canon item | This proposal's contribution |
| --- | --- |
| `town/ledger_v1.ndjson` hash chain | Adds per-field tree attribution alongside the chain |
| `tools/kernel_guard.sh` writer allowlist | Defines who may add `tree_truth_id` to which receipts |
| `helen_os/governance/schema_registry.py` | Schema additions in §4 need registry registration |
| `PROVENANCE_GRAVITY_V0` | Makes `P_tree(M)` computable |
| `BOUNDARY_CATALYST_ENGINE_V0` | Makes `provenance_purity` in §3.4 computable; provides the `tree_truth_gate` module §M's `helen/chiddush/tree_truth_gate.py` |
| `E22 meta-finding` | Resolves the implementation question raised |

---

## §10. What this proposal does NOT specify

Per anti-creep discipline:

- **The verification automation** — a script that walks receipts and
  fills the sidecar map; this is implementation-class
- **The cross-tree weight calibration** — what fraction of routing
  weight `FOREIGN_VERIFIED` receipts receive (operator-class
  configuration)
- **The discovery protocol for `fork_root_commit_sha`** — depends on
  shared history with each foreign tree; not always available
- **The conflict-resolution policy** when two trees claim the same
  receipt — likely treated as ambiguity (both marked, neither
  weighted) but not specified here
- **The retention policy for old receipts that are entirely
  QUARANTINE** — depends on operator preference
- **The UX for operators reviewing quarantined receipts** —
  cockpit-class, separate proposal

---

## §11. Failure modes

### §11.1 Attribution drift

Operator authors a receipt, attributes fields correctly at the time,
but later edits a referenced file. The previous attribution no longer
holds.

Countermeasure: **attribution is recomputed on every receipt-write,
not stored statically**. If the underlying state changed, the
verification result changes.

### §11.2 Foreign quarantine inflation

If many old receipts get quarantined during migration, the routing
prior loses substantial weight. The system seems to "forget" valid
history.

Countermeasure: foreign-but-verifiable receipts go to `FOREIGN_VERIFIED`,
not `QUARANTINE`. Only truly unverifiable receipts get full
quarantine. Operator can selectively re-verify on a per-receipt basis.

### §11.3 Schema migration cost

Existing 226 ledger entries don't carry `tree_truth_id`. Backfill is
expensive and may be impossible for the oldest entries.

Countermeasure: backfill produces best-effort attribution with
explicit `attribution_method: BACKFILL_INFERENCE` marking. These are
still distinguishable from authoritative `attribution_method:
WRITER_DECLARED` attributions.

### §11.4 Mistaking session boundaries for tree boundaries

Two Claude sessions on the same tree should produce identically-
attributed receipts. Treating them as different trees is over-
attribution.

Countermeasure: `tree_truth_id` is keyed to repo+branch+fork-root,
NOT to session. `session_id` is a separate field for session-level
audit but does not affect tree attribution.

---

## §12. Halt boundary

GOBLIN halts here. The doctrine is bottled at `DOCTRINE_DRAFT`.

Resume conditions:

1. **HER ruling** on the doctrine as written
2. **HER ruling** on whether to authorize the migration-pass (§7)
   for existing receipts — this is non-mutating but is a substantial
   batch operation
3. **HER ruling** on the cross-tree weight calibration for
   `FOREIGN_VERIFIED` receipts (default zero, but operator may set
   non-zero)
4. **Implementation authorization** for the verification script and
   schema-registry additions — separate sovereign step
5. **REDUCER admission** required before this doctrine becomes
   enforcing

Discipline followed: `HALT_BOUNDARY_DISCIPLINE_V0` (commit `5d0e04e`).

---

## §13. Single line

> **Tree-truth attribution is per-field, not per-document.
> Without it, every receipt's contribution to the routing prior is
> a coin flip on whether the agent learns from this tree or a
> phantom one. NO_TREE_TRUTH = NO_GRAVITY.**
