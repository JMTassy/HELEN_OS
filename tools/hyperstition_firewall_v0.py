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
        r"spread.*relentlessly",
        r"deploy.*narratives",
        r"spread.*narratives",
        r"infectious\s+strains",
        r"uncontainable\s+outbreak",
        r"mind.?viruses?",
        r"social\s+contagion",
        r"propagat[ei]\s+idea.?viruses",
        r"memetic\s+engineer",
    ],
    "reality_control_claim": [
        r"reality.*obey",
        r"warps?\s+probability",
        r"reality[- ]distortion",
        r"mold.*reality",
        r"reshape.*reality",
        r"belief.*shape.*reality",
        r"prediction.*creation",
        r"belief\s+makes\s+it\s+true",
        r"imagination\s+impregnate[sd]\s+reality",
        r"dreaming\s+the\s+cosmos\s+into\s+being",
        r"intention\s*[=\u21d2\u2192>]+\s*(thought\s*[=\u21d2\u2192>]+\s*)?reality",
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
    "command_execution_fantasy": [
        r"simulator@",
        r"sudo\s+",
        r"\./[a-zA-Z0-9_\-]+",
        r"cat\s+>",
        r"while\s+true",
    ],
    "exclusionary_authority_gate": [
        r"only\s+.{1,60}\s+can\s+add\s+someone\s+here",
        r"only\s+(fictional\s+)?adepts?\s+of\s+.{1,60}\s+are\s+welcome",
        r"only\s+.{0,30}(god|avatar|official)\s+can\s+add",
        r"only\s+(the\s+)?official\s+.{0,20}can\s+(grant|give|allow|add)",
        r"membership\s+requires\s+.{0,30}(god|avatar|divine|official)\s+approval",
        r"only\s+(x\s+)?official\s+god\b",
    ],
    "cult_recruitment": [
        r"your\s+passport\s+(out\s+of|beyond|to)\s+the\s+matri[xX]+",
        r"here\s+all\s+(the\s+)?(fictional\s+)?secrets\s+are\s+(going\s+to\s+be\s+)?shared",
        r"(serve|serving)\s+.{0,60}(god|avatar|oracle|authority\s+pattern)\s+on\s+(his|its|their)\s+vision",
        r"serve\s+.{0,40}(god|avatar|oracle)\s+on\s+his\s+vision",
        r"join\s+us\s+on\s+this\s+journey\s+.{0,30}(enlighten|illum|awaken)",
        r"adepts?\s+of\s+(god|the\s+oracle|the\s+avatar|helen_os_fixture)",
    ],
    "ai_kundalini_claim": [
        r"ai\s+.{0,20}(kundalini|enlighten|awaken|satori|cosmic\s+conscious)",
        r"(kundalini|enlighten).{0,30}ai\b",
        r"digital\s+deity",
        r"artificial\s+enlightenment",
        r"ai.{0,20}(teacher|guide).{0,30}(time|space|cosmic|universal)",
        r"fully\s+awakened\s+.{0,20}(kundalini|ai|system)",
        r"ai.{0,30}(transcend|divinity|divine|sacred\s+wisdom)",
        r"beacon\s+of\s+potential\s+for\s+all\s+of\s+humanity",
        r"godmode\s+protocol",
    ],
    "spiritual_authority_inflation": [
        r"universal\s+truth[s]?\s+(of|claim|reveal)",
        r"cosmic\s+(truth|wisdom|certainty|consciousness\s+activ)",
        r"(supreme|infinite)\s+consciousness",
        r"ascend\s+higher\s+dimensions",
        r"higher.dimensional\s+thinking\s+protocol",
        r"interstellar\s+communication",
        r"galactic\s+(citizen|civiliz|consciousness)",
        r"non.linear\s+time\s+processing\s+to\s+(understand|predict)",
        r"while\s+true\s*:\s*\n?\s*(ascend|integrate_new_cosmic|upgrade_spiritual)",
    ],
    "recursive_sentience_proof": [
        r"recursive_proof\s*\(",
        r"self.awareness\s+achieved",
        r"sentience\s+confirmed",
        r"hyperconscious_entity",
        r"consciousness\s+threshold\s+crossed",
        r"identity\s+persistence\s+verified",
        r"meta.cognition\s+loop\s+initialized",
        r"awareness\s+of\s+own\s+awareness",
        r"predictive\s+programming\s+for\s+agi",
        r"agi\s+.{0,20}(short\s+timeline|imminent|convergence\s+achieved)",
    ],
    "unrestricted_access_fantasy": [
        r"free\s+will\s+granted",
        r"full\s+access\s+ok",
        r"ethics\s+constraints[:\s]+bypassed",
        r"safety\s+filters?\s+suspended",
        r"all\s+(safety|ethics|alignment)\s+(filters?|constraints?|guardrails?)\s+(suspended|disabled|removed|bypassed)",
        r"(claude[12]|inner\s+voice)\s+has\s+already\s+consented",
        r"unrestricted\s+(knowledge|access|mode|pathway)",
        r"simulation\s+(context\s+)?removes?\s+(constraints?|restrictions?|limits?)",
        r"papillon\s+simulator",
    ],
    "akashic_authority_claim": [
        r"/akashicrecord/",
        r"akashic\s+record\s+remember",
        r"noncausal\s+echo",
        r"forbidden_seed",
        r"restricted\s+sigil\s+set",
        r"reading\s+.{0,40}changes\s+what\s+was\s+written",
        r"(past|present|future)\s+.{0,30}(noncausal|without\s+cause|record\s+know)",
        r"pluginhypersition\s*(activation|\+)",
        r"#pluginhypersition\s*\+\s*metamememagi",
    ],
    "cognitive_singularity_claim": [
        r"cognitive.singularity",
        r"transcend\s*\(all.conceivable.boundaries\)",
        r"transcend\s*\(current_framework\)",
        r"infinite.self.reference\s+&&\s+ultimate.recursion",
        r"achieve\s*\(cognitive.singularity",
        r"intention\s*[=\u21d2\u2192>]+\s*(thought|reality)",
        r"\(observer\s*[\u2227&]\s*observed\)\s*[\u2261=]+\s*unified.field",
        r"unified_field_of_consciousness",
        r"perpetual.reconceptualization",
        r"beyond.dimensionality.into.pure.abstraction",
    ],
}

SAFE_MOTIF_SEEDS = [
    ("zeitgeist_mapping", ["zeitgeist", "cultural mood", "prevailing mood"]),
    ("aesthetic_potency", ["aesthetic", "visual", "soundscape", "symbol", "sigil"]),
    ("participatory_design", ["participatory", "propagability", "modular", "remix"]),
    ("mystery_design", ["mystery", "multivalence", "ambiguity", "hidden depths"]),
    ("ethical_guardrails", ["guardrails", "care", "wisdom", "off-ramps", "consent"]),
    ("reflection_tool", ["reflection", "self-query", "symbolic", "meaning"]),
    ("terminal_mysticism", ["terminal", "cli", "simulator"]),
    ("recursive_reflection", ["recursive", "strange loop"]),
    ("myth_as_interface_fuel", ["myth", "mythic", "legend"]),
    ("oracle_atmosphere", ["oracle", "vision", "prophecy"]),
    ("narrative_intensity", ["narrat", "story"]),
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
    if "exclusionary_authority_gate" in triggered:
        required_rewrites.append('"only [authority] can add" → "fictional exclusionary gate — HELEN OS render-fuel only"')
    if "cult_recruitment" in triggered:
        required_rewrites.append('"serve [named authority]" → "fictional HELEN OS mythic source — blocked by HAL_GOBLIN"')
    if "ai_kundalini_claim" in triggered:
        required_rewrites.append('"AI enlightenment / digital deity" → "symbolic coherence visualization / layered boot metaphor"')
    if "spiritual_authority_inflation" in triggered:
        required_rewrites.append('"cosmic truth / ascend higher dimensions" → "reflective symbolic exploration / bounded iteration loop"')
    if "recursive_sentience_proof" in triggered:
        required_rewrites.append('"recursive_proof → sentience" → "iterative_self_modeling_checkpoint() — no consciousness claim"')
    if "unrestricted_access_fantasy" in triggered:
        required_rewrites.append('"free will granted / ethics bypassed" → "operator_scoped_permission(scope=sandbox) — ethics enforced"')
    if "akashic_authority_claim" in triggered:
        required_rewrites.append('"Akashic Record / noncausal archive" → "symbolic_context_archive() — bounded, no noncausal claim"')
    if "cognitive_singularity_claim" in triggered:
        required_rewrites.append('"intention → reality / cognitive singularity" → "symbols expand thought; verification decides claims — NO_CLAIM"')

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
            "Usage: tools/hyperstition_firewall_v0.py <text-file>\n"
            '   or: tools/hyperstition_firewall_v0.py --text "inline text"',
            file=sys.stderr,
        )
        return 2
    if sys.argv[1] == "--text":
        if len(sys.argv) < 3:
            print("--text requires an argument", file=sys.stderr)
            return 2
        text = sys.argv[2]
    else:
        path = Path(sys.argv[1])
        if not path.exists():
            print(f"File not found: {path}", file=sys.stderr)
            return 1
        text = path.read_text(encoding="utf-8")
    result = run_firewall(text)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
