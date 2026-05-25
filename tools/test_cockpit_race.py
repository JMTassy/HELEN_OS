"""Deterministic regression test for cockpit stale-snapshot race.

Reproduces the exact scenario observed on
gemma_proposal_2026-05-25T21-59-48Z_iter001.json where a stale
in-memory cockpit clobbered a concurrent HAL annotation.

Asserts:
  1. HAL lane is preserved when operator writes from a stale snapshot
  2. annotation_events records both writes with correct previous values
"""

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import review_cockpit as rc


def main() -> int:
    tmp = Path(tempfile.mkdtemp()) / "race_test.json"
    tmp.write_text(json.dumps({
        "schema_name": "GEMMA_PROPOSAL_RAW_V1",
        "lifecycle_entry": "RAW",
        "auto_promotion_ceiling": "RAW",
        "operator_decision": None,
        "hal_verdict": None,
        "receipt_timestamp_utc": "2026-05-25T00:00:00Z",
    }, indent=2), encoding="utf-8")

    # Session A loads the receipt — both lanes null
    session_a_snapshot = json.loads(tmp.read_text(encoding="utf-8"))
    print(f"T0: Session A loaded. hal={session_a_snapshot['hal_verdict']!r} "
          f"op={session_a_snapshot['operator_decision']!r}")

    # Session B writes hal_verdict (concurrent, while Session A still has its snapshot)
    rc.write_hal_verdict(tmp, {}, "NEEDS_MORE_RECEIPTS", "HAL", "session B HAL write")
    after_b = json.loads(tmp.read_text(encoding="utf-8"))
    print(f"T1: Session B wrote HAL. hal={after_b['hal_verdict']['status']!r} "
          f"op={after_b['operator_decision']!r}")

    # Session A now writes operator_decision using its STALE snapshot.
    # Before the patch, this would clobber hal_verdict back to null.
    rc.write_decision(tmp, session_a_snapshot, "REJECTED", "JM Tassy",
                      "session A op write with stale snapshot")
    after_a = json.loads(tmp.read_text(encoding="utf-8"))
    hal_status = after_a["hal_verdict"]["status"] if after_a["hal_verdict"] else None
    print(f"T2: Session A wrote OP. hal={hal_status!r} "
          f"op={after_a['operator_decision']['status']!r}")
    print()

    # Assertions
    assert after_a["hal_verdict"] is not None, \
        "REGRESSION: HAL lane was clobbered by stale operator write"
    assert after_a["hal_verdict"]["status"] == "NEEDS_MORE_RECEIPTS", \
        f"wrong HAL status: {after_a['hal_verdict']}"
    assert after_a["operator_decision"]["status"] == "REJECTED"
    assert len(after_a["annotation_events"]) == 2, \
        f"expected 2 annotation_events, got {len(after_a['annotation_events'])}"
    assert after_a["annotation_events"][0]["lane"] == "hal_verdict"
    assert after_a["annotation_events"][0]["previous"] is None
    assert after_a["annotation_events"][1]["lane"] == "operator_decision"
    assert after_a["annotation_events"][1]["previous"] is None

    print("PASS: HAL lane preserved through stale-snapshot operator write")
    print(f"PASS: annotation_events has {len(after_a['annotation_events'])} entries")
    for i, ev in enumerate(after_a["annotation_events"]):
        print(f"      [{i}] lane={ev['lane']} actor={ev['actor']!r} "
              f"prev={ev['previous']!r} next.status={ev['next']['status']!r}")

    tmp.unlink()
    return 0


if __name__ == "__main__":
    sys.exit(main())
