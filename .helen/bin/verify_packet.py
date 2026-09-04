#!/usr/bin/env python3
"""
HELEN M6 — Deterministic packet verifier.

Checks that an artifact claiming to be evidence:
  1. parses as JSON;
  2. declares schema helen.run-packet.v0;
  3. carries a normalizer_seal that re-derives correctly (i.e. was produced
     by normalize.py, not hand-written by a model or human);
  4. has authority == false;
  5. every observation has a source_ref.

Exit 0 = packet admissible AS EVIDENCE INPUT (not as canon).
Exit 1 = REFUSED. The refusal reason is printed as JSON.

This is the bypass-proof: a raw model response, however well-formatted,
cannot pass check 3 because it cannot compute the versioned seal without
running through the normalizer.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from normalize import verify_seal  # noqa: E402


def verify(path: Path) -> dict:
    result = {"artifact": str(path), "admissible_as_evidence": False, "reasons": []}
    try:
        packet = json.loads(path.read_text())
    except Exception as e:
        result["reasons"].append(f"not JSON: {e}")
        return result

    if packet.get("schema") != "helen.run-packet.v0":
        result["reasons"].append("schema is not helen.run-packet.v0 — raw provider output is an attachment, not evidence")
        return result

    if not verify_seal(packet):
        result["reasons"].append("normalizer_seal invalid — artifact did not pass through normalize.py; REFUSED (Law 2: evidence non-creation)")
        return result

    if packet.get("authority") is not False:
        result["reasons"].append("authority must be false on all worker packets (Law 1)")
        return result

    for ob in packet.get("observations", []):
        if not ob.get("source_ref"):
            result["reasons"].append("observation without source_ref")
            return result

    result["admissible_as_evidence"] = True
    result["reasons"].append("seal valid; produced by normalizer; authority false")
    return result


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: verify_packet.py <packet.json>", file=sys.stderr)
        return 2
    result = verify(Path(sys.argv[1]))
    print(json.dumps(result, indent=2))
    return 0 if result["admissible_as_evidence"] else 1


if __name__ == "__main__":
    sys.exit(main())
