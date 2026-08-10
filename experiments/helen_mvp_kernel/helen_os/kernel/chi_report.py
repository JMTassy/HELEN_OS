"""Machine-readable χ⁺ report — 🔵 OBSERVED · NON_SOVEREIGN sandbox.

Scoped statuses only: PASS / PASS_SCOPED / INCOMPLETE / FAIL — never a green
banner. chi_med with any unclassified surface is INCOMPLETE by law.
"""
from __future__ import annotations

from helen_os.ledger.hash_chain import canonical_json, sha256_hex


def build_report(
    *,
    gov: dict,
    mem: dict,
    med: dict,
    comp: dict,
    cons: dict,
    seat: str = "laptop",
) -> dict:
    med = dict(med)
    if med.get("mutation_surfaces_unclassified", 0) > 0:
        med["verdict"] = "INCOMPLETE"
    inventory = med.get("surface_inventory", [])
    med["inventory_hash"] = "sha256:" + sha256_hex(canonical_json(sorted(inventory)))
    report = {
        "chi_gov": gov,
        "chi_mem": mem,
        "chi_med": med,
        "chi_comp": comp,
        "chi_cons": cons,
        "seat": seat,
        "claim_scope": "enumerated-and-tested surfaces only; not a universal claim",
    }
    report["report_hash"] = "sha256:" + sha256_hex(canonical_json(report))
    return report
