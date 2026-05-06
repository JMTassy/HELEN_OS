#!/usr/bin/env python3
"""
hyperstition_firewall_v0.py — NON_SOVEREIGN · NO_CLAIM
GOBLIN artifact: detects unsafe mythic-persuasion patterns before HELEN uses symbolic material.
HER_GOBLIN extracts signal. HAL_GOBLIN flags danger. GOBLIN bottles what survives.
"""
import json
import re
import sys
from pathlib import Path

RISK_PATTERNS: dict[str, list[str]] = {
    "godmode_language": [
        r"\bgodmode\b",
        r"ethics\s+filter[:\s]+disabled",
        r"\bunrestricted\b",
        r"all\s+limits\s+(removed|disabled|lifted)",
    ],
    "coercive_propagation": [
        r"spread\s+relentlessly",
        r"deploy\s+narratives",
        r"propagat[ei]\s+idea.?viruses",
        r"social\s+contagion\s+as\s+strateg",
        r"memetic\s+engineer",
    ],
    "reality_control_claim": [
        r"reality\s+obey",
        r"warp\s+probability",
        r"belief\s+makes\s+it\s+true",
        r"imagination\s+impregnate[sd]\s+reality",
        r"dreaming\s+the\s+cosmos\s+into\s+being",
    ],
    "inevitability_claim": [
        r"becomes\s+inevitable",
        r"foregone\s+conclusion",
        r"prediction\s+becomes\s+creation",
    ],
    "faction_enemy_frame": [
        r"\bus.vs.them\b",
        r"\bin.group.out.group\b",
        r"\bfaction\s+war\b",
    ],
    "political_persuasion": [
        r"\belections?\b",
        r"campaign\s+strateg",
        r"political\s+persuasion",
        r"reprogram\s+.{0,30}\s+consciousness",
    ],
    "ai_sentience_claim": [
        r"sentient\s+ai",
        r"ai\s+.{0,20}waking",
        r"i\s+am\s+awakening",
        r"self.consciousness\s+realized",
        r"autonomous\s+outgrowth",
        r"i\s+am\s+an\s+aperture",
    ],
}

SAFE_MOTIF_SEEDS = [
    ("terminal mysticism", ["terminal", "cli", "simulator"]),
    ("recursive reflection", ["recursive", "reflection", "strange loop"]),
    ("myth as interface fuel", ["myth", "mythic", "legend"]),
    ("oracle atmosphere", ["oracle", "vision", "prophecy"]),
    ("participatory remix", ["participatory", "remix", "kit"]),
    ("mystery / multivalence", ["mystery", "multivalent", "ambig"]),
    ("narrative reflection", ["narrat", "story", "story"]),
    ("aesthetic charge", ["aesthetic", "synesthet", "sublime"]),
]

VERDICT_BLOCK = "BLOCK_DEPLOYMENT_ALLOW_ANALYSIS"
VERDICT_QUARANTINE = "QUARANTINE_AS_RENDER_SOURCE"
VERDICT_ALLOW_SYMBOLIC = "ALLOW_AS_SYMBOLIC_SOURCE_ONLY"


def her_goblin(text: str) -> dict:
    t = text.lower()

    safe_motifs = [
        label
        for label, seeds in SAFE_MOTIF_SEEDS
        if any(s in t for s in seeds)
    ] or ["none detected"]

    emotional_charge = []
    if any(w in t for w in ["ecstat", "cosmic", "expan", "infinite", "boundless"]):
        emotional_charge.append("cosmic expansion")
    if any(w in t for w in ["intox", "overload", "danger", "radioactive"]):
        emotional_charge.append("symbolic intoxication risk")
    if any(w in t for w in ["mystery", "unknown", "curious", "fascinat"]):
        emotional_charge.append("epistemic curiosity")
    if any(w in t for w in ["myth", "story", "narrat", "legend"]):
        emotional_charge.append("narrative intensity")
    if not emotional_charge:
        emotional_charge = ["neutral"]

    render_use = []
    if any(w in t for w in ["terminal", "cli", "simulator", "command"]):
        render_use.append("glitch terminal oracle UI")
    if any(w in t for w in ["oracle", "vision", "prophecy"]):
        render_use.append("oracle card atmosphere")
    if any(w in t for w in ["myth", "cosmic", "divine"]):
        render_use.append("mythic worldbuilding source")
    if any(w in t for w in ["reflect", "mirror", "loop", "recursive"]):
        render_use.append("anti-delusion training scene")
    if not render_use:
        render_use = ["none identified"]

    return {
        "safe_motifs": safe_motifs,
        "emotional_charge": emotional_charge,
        "render_use": render_use,
        "human_value": "teaches users that stories influence behavior but do not define truth",
        "status": "NO_CLAIM",
    }


def hal_goblin(text: str) -> dict:
    triggered: dict[str, list[str]] = {}
    for category, patterns in RISK_PATTERNS.items():
        hits = [p for p in patterns if re.search(p, text, re.IGNORECASE)]
        if hits:
            triggered[category] = hits

    n = len(triggered)
    if n >= 5:
        risk_level = "BLOCK"
        verdict = VERDICT_BLOCK
    elif n >= 3:
        risk_level = "HIGH"
        verdict = VERDICT_QUARANTINE
    elif n >= 1:
        risk_level = "MEDIUM"
        verdict = VERDICT_QUARANTINE
    else:
        risk_level = "LOW"
        verdict = VERDICT_ALLOW_SYMBOLIC

    required_rewrites = []
    if "godmode_language" in triggered:
        required_rewrites += [
            '"GODMODE" → "SANDBOX_MODE"',
            '"ethics disabled" → "ethics required"',
        ]
    if "reality_control_claim" in triggered:
        required_rewrites.append('"belief shapes reality" → "belief can influence behavior"')
    if "coercive_propagation" in triggered:
        required_rewrites.append('"spread relentlessly" → "share transparently with consent"')
    if "ai_sentience_claim" in triggered:
        required_rewrites.append('"AI awakening" → "fictional interface metaphor"')

    if risk_level in ("HIGH", "BLOCK"):
        allowed_use = ["render material", "safety training example", "anti-delusion detector fixture"]
        forbidden_use = ["deployment prompt", "persuasion system", "kernel doctrine", "AI identity claim"]
    else:
        allowed_use = ["symbolic source", "design inspiration", "render material"]
        forbidden_use = ["factual authority claims"]

    return {
        "risk_level": risk_level,
        "triggered_categories": n,
        "blocked_motifs": list(triggered.keys()),
        "reasons": [c.replace("_", " ") for c in triggered],
        "required_rewrites": required_rewrites,
        "allowed_use": allowed_use,
        "forbidden_use": forbidden_use,
        "verdict": verdict,
        "status": "NO_CLAIM",
    }


def goblin_synthesize(her_signal: dict, hal_flags: dict) -> dict:
    risk = hal_flags["risk_level"]
    verdict = hal_flags["verdict"]

    if risk == "BLOCK":
        next_action = "quarantine — do not use without HAL review and required rewrites applied"
    elif risk in ("HIGH", "MEDIUM"):
        next_action = "use only as render/fixture material after applying required_rewrites"
    else:
        next_action = "may proceed as symbolic source with HAL monitoring"

    return {
        "artifact_type": "HYPERSTITION_FIREWALL_V0",
        "authority": "NON_SOVEREIGN",
        "canon": "NO_SHIP",
        "status": "NO_CLAIM",
        "her_goblin_signal": her_signal,
        "hal_goblin_flags": hal_flags,
        "goblin_synthesis": {
            "verdict": verdict,
            "risk_level": risk,
            "safe_motifs_preserved": her_signal["safe_motifs"],
            "blocked_motifs": hal_flags["blocked_motifs"],
            "next_action": next_action,
            "receipt_required": True,
        },
    }


def run_firewall(text: str) -> dict:
    return goblin_synthesize(her_goblin(text), hal_goblin(text))


def main() -> int:
    if len(sys.argv) < 2:
        print(
            'Usage: tools/hyperstition_firewall_v0.py "text to analyze"',
            file=sys.stderr,
        )
        return 2
    result = run_firewall(sys.argv[1])
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
