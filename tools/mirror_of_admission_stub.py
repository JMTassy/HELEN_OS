#!/usr/bin/env python3
"""
mirror_of_admission_stub.py — NON_SOVEREIGN · NO_CLAIM
Deterministic stub generator for MIRROR_OF_ADMISSION_V1 artifacts.
No LLM dependency. Heuristic fracture classification only.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def classify_fracture(raw: str, tools: list[str]) -> tuple[str, str]:
    text = raw.lower()
    tool_set = {t.lower() for t in tools}

    if any(w in text for w in ["ledger", "canon", "sovereign", "mayor", "governance"]):
        return (
            "LAW_MISSING",
            "The intent approaches governed state and needs admissibility review.",
        )
    if any(w in text for w in ["akashic", "divine", "prophecy", "sentient", "conscious", "sacred"]):
        return (
            "DREAM_OVERREACH",
            "The symbolic layer risks presenting mythic intensity as factual authority.",
        )
    if any(w in text for w in ["send", "telegram", "video", "backend", "api", "pipeline"]):
        required = {"telegram", "higgsfield"}
        if not required.issubset(tool_set):
            return (
                "TOOL_MISSING",
                "The intent needs execution tools that are not declared available.",
            )
        return (
            "BUILD_BLOCKED",
            "The intent is executable but required artifacts or receipts are missing.",
        )
    return (
        "RECEIPT_MISSING",
        "The intent needs a receipt before it can become an admissible claim.",
    )


def build_mirror(raw_intent: str, tools: list[str]) -> dict:
    fracture_type, explanation = classify_fracture(raw_intent, tools)
    return {
        "artifact_type": "MIRROR_OF_ADMISSION_V1",
        "authority": "NON_SOVEREIGN",
        "canon": "NO_SHIP",
        "status": "NO_CLAIM",
        "input": {
            "raw_intent": raw_intent,
            "current_state_ref": None,
            "available_tools": tools,
            "active_law_ref": "NO_RECEIPT_NO_SHIP",
        },
        "dream_world": {
            "symbolic_pull": "The intent wants to become a meaningful HELEN-facing experience.",
            "emotional_value": "Momentum, coherence, relief from overload, and visible direction.",
            "mythic_form": "A mirror that separates dream, build, and law.",
            "authority": "NON_SOVEREIGN",
        },
        "build_world": {
            "prototype_path": "Create the smallest artifact that makes the intent testable.",
            "required_artifacts": ["schema", "fixture", "validator", "test"],
            "blockers": ["no implementation receipt yet"],
            "first_build_step": "Create one typed artifact and validate it.",
        },
        "law_world": {
            "admissible": False,
            "missing_receipts": ["validation_receipt"],
            "forbidden_paths": [
                "canon mutation",
                "ledger append",
                "authority claim from symbolic intensity",
            ],
            "required_gate": "HAL_VALIDATION",
        },
        "fracture": {"type": fracture_type, "explanation": explanation},
        "next_move": {
            "one_action": "Create and validate one MIRROR_OF_ADMISSION_V1 JSON artifact.",
            "artifact_path": "fixtures/mirror_of_admission/generated_stub.json",
            "receipt_required": True,
        },
    }


def main() -> int:
    if len(sys.argv) < 2:
        print(
            'Usage: tools/mirror_of_admission_stub.py "raw intent" [tool1 tool2 ...]',
            file=sys.stderr,
        )
        return 2
    raw_intent = sys.argv[1]
    tools = sys.argv[2:]
    payload = build_mirror(raw_intent, tools)
    out = ROOT / "fixtures" / "mirror_of_admission" / "generated_stub.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(str(out.relative_to(ROOT)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
