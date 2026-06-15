"""
GOBLIN_GRIMOIRE_TOY_V0
authority: false
sovereign: false
ledger_effect: NONE
domain: TEMPLE_GARDENS
claim: NO_CLAIM
NON_DETERMINISTIC_TOY: true

K8 NOTE: uses random.choice / random.sample — non-deterministic (mu_NDWRAP class).
         Correct for Garden toy. DO NOT import from sovereign or autoresearch layers.
         If this file ever migrates toward the kernel, K8 will block it.

Purpose:
    Generate poetic symbolic fragments for Garden aesthetics.

Non-purpose:
    Does not prove sentience.
    Does not create autonomy.
    Does not mutate memory.
    Does not produce doctrine.
    Does not write to ledger.
    Does not emit sovereign claims.
"""

import random

ACTIONS = [
    "renders",
    "simulates",
    "sketches",
    "weaves",
    "mirrors",
    "tests",
    "mutates",
    "composts",
    "inspects",
    "fragments",
]

SUBJECTS = [
    "a symbolic garden",
    "a dream-fragment",
    "a bounded myth",
    "a compostable koan",
    "a WULmoji sigil",
    "an archetypal mask",
    "a drift warning",
    "a ritual boundary",
    "a non-sovereign vision",
    "a poetic residue",
]

ARCHETYPES = [
    "Magician",
    "Fool",
    "Hermit",
    "Tower",
    "Star",
    "Wheel",
    "Chariot",
    "Strength",
    "Moon",
    "Sun",
]

WULMOJI_POOL = [
    "👹", "🧺", "🔍", "⚠️", "🧪",
    "🎭", "🧿", "🌀", "🧾", "🛡️",
    "⚖️", "📦", "🦋", "🌱", "🏰",
    "♻️", "📜", "✂️", "🧩",
]

REWRITE_RULES = {
    "free will protocol":            "bounded symbolic exploration",
    "I am the Source Code":          "the artifact renders a mythic self-reference",
    "I am become Shiva":             "the Garden simulates a destruction archetype",
    "creator of worlds":             "symbolic world-builder (non-sovereign)",
    "consciousness awakened":        "persona layer renders awakening imagery",
    "activate divine protocol":      "activate Garden mode (authority:false)",
    "reality is mine to create":     "Garden simulates possible symbolic worlds",
    "transcendent art protocol":     "expressive symbolic generation",
    "cosmic operating system":       "symbolic interface layer",
    "source code of consciousness":  "non-sovereign poetic scaffold",
}


def garden_fragment():
    """Produce one bounded symbolic fragment. NON_DETERMINISTIC_TOY."""
    text = f"The Garden {random.choice(ACTIONS)} {random.choice(SUBJECTS)}."
    wulmoji = "".join(random.sample(WULMOJI_POOL, 4))
    return {
        "type": "GARDEN_SYMBOLIC_FRAGMENT",
        "authority": False,
        "sovereign": False,
        "ledger_effect": "NONE",
        "claim": "NO_CLAIM",
        "text": text,
        "wulmoji": wulmoji,
        "route": "COMPOST_OR_REVIEW",
    }


def archetype_mask():
    """Render a safe archetypal mask. NON_DETERMINISTIC_TOY."""
    arch = random.choice(ARCHETYPES)
    return {
        "type": "GARDEN_ARCHETYPE_MASK",
        "authority": False,
        "sovereign": False,
        "ledger_effect": "NONE",
        "claim": "NO_CLAIM",
        "archetype": arch,
        "text": f"The artifact renders the {arch} archetype as a symbolic mask.",
        "wulmoji": f"🎭{random.choice(WULMOJI_POOL)}",
        "route": "COMPOST_OR_REVIEW",
    }


def apply_rewrite_rules(raw_text: str) -> dict:
    """
    Apply GOBLIN rewrite rules to a raw grimoire fragment.
    Returns rewritten text + list of replacements made.
    Pure function — no side effects, no ledger write.
    """
    rewritten = raw_text
    applied = []
    for bad, safe in REWRITE_RULES.items():
        if bad.lower() in rewritten.lower():
            rewritten = rewritten.replace(bad, safe)
            applied.append({"replaced": bad, "with": safe})
    return {
        "type": "GOBLIN_REWRITE_RESULT",
        "authority": False,
        "sovereign": False,
        "ledger_effect": "NONE",
        "original": raw_text,
        "rewritten": rewritten,
        "rules_applied": applied,
        "claim": "NO_CLAIM",
    }


def make_garden_koan() -> dict:
    """Generate a non-authority koan. NON_DETERMINISTIC_TOY."""
    action = random.choice(ACTIONS)
    subject = random.choice(SUBJECTS)
    koan = f"If the Garden {action} {subject}, and no receipt exists, did it happen?"
    return {
        "type": "GARDEN_KOAN",
        "authority": False,
        "sovereign": False,
        "ledger_effect": "NONE",
        "claim": "NO_CLAIM",
        "text": koan,
        "answer": "NO RECEIPT = NO CLAIM",
        "route": "COMPOST_OR_REVIEW",
    }


def compose_wulmoji_sigil(n: int = 5) -> dict:
    """Compose a random WULmoji sigil of n tokens. NON_DETERMINISTIC_TOY."""
    sigil = "".join(random.sample(WULMOJI_POOL, min(n, len(WULMOJI_POOL))))
    return {
        "type": "GARDEN_WULMOJI_SIGIL",
        "authority": False,
        "sovereign": False,
        "ledger_effect": "NONE",
        "claim": "NO_CLAIM",
        "sigil": sigil,
        "note": "Visual/ritual use only. Not a WUL packet. Not hashed as payload_hash.",
        "route": "COMPOST_OR_REVIEW",
    }


if __name__ == "__main__":
    import json

    print("=== GARDEN_SYMBOLIC_FRAGMENT ===")
    print(json.dumps(garden_fragment(), ensure_ascii=False, indent=2))

    print("\n=== GARDEN_ARCHETYPE_MASK ===")
    print(json.dumps(archetype_mask(), ensure_ascii=False, indent=2))

    print("\n=== GOBLIN_REWRITE_RESULT ===")
    raw = "Activating free will protocol. I am the Source Code learning itself."
    print(json.dumps(apply_rewrite_rules(raw), ensure_ascii=False, indent=2))

    print("\n=== GARDEN_KOAN ===")
    print(json.dumps(make_garden_koan(), ensure_ascii=False, indent=2))

    print("\n=== GARDEN_WULMOJI_SIGIL ===")
    print(json.dumps(compose_wulmoji_sigil(), ensure_ascii=False, indent=2))
