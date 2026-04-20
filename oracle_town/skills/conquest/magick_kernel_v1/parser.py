"""CONQUEST MAGICK reference parser — stdlib only, pure function.

Grammar (per KERNEL_SPEC.md §1):
    ACTE := MANDAT OPUS{1,2} OUTIL{0,1} SEAL{0,1} "/" RESULT

The parser accepts exactly the canonical alphabet (v1). Any other glyph in any
position is rejected. Overlay glyphs (WULmoji) are not recognized here by
design — the kernel stays smaller than the lore.

Public API:
    parse(line: str) -> tuple[bool, dict, str]

Returns:
    (True, parsed_dict, "ok") on valid input
    (False, {}, reason) on rejection
"""
from __future__ import annotations

MANDAT = {"\u271d\ufe0f", "\U0001f339", "\U0001f300"}
OPUS = {"\U0001f702", "\U0001f704", "\U0001f701", "\U0001f703", "\u2697"}
OUTIL = {"\u2694\ufe0f", "\U0001f6e1\ufe0f", "\U0001f4dc", "\u2e38"}
SEAL = {"\u26b0"}
RESULT = {"\U0001f3f0", "\U0001f9f1", "\U0001f311", "\U0001f9e0", "\u2764\ufe0f"}

NAMES = {
    "\u271d\ufe0f": "CROIX",
    "\U0001f339": "ROSE",
    "\U0001f300": "SPIRALE",
    "\U0001f702": "FEU",
    "\U0001f704": "EAU",
    "\U0001f701": "AIR",
    "\U0001f703": "TERRE",
    "\u2697": "QUINTESSENCE",
    "\u2694\ufe0f": "EPEE",
    "\U0001f6e1\ufe0f": "BOUCLIER",
    "\U0001f4dc": "PARCHEMIN",
    "\u2e38": "CROIX_SANG",
    "\u26b0": "CERCUEIL",
    "\U0001f3f0": "FORT",
    "\U0001f9f1": "MUR",
    "\U0001f311": "OMBRE",
    "\U0001f9e0": "ESPRIT",
    "\u2764\ufe0f": "COEUR",
}


def _tokenize(line: str) -> list[str]:
    """Split on whitespace. The canonical format uses space separators."""
    return [t for t in line.strip().split() if t]


def parse(line: str) -> tuple[bool, dict, str]:
    """Parse one acte line. Pure function. Deterministic."""
    toks = _tokenize(line)
    if not toks:
        return False, {}, "empty_line"

    if "/" not in toks:
        return False, {}, "missing_slash_separator"

    slash_idx = toks.index("/")
    left = toks[:slash_idx]
    right = toks[slash_idx + 1:]

    if len(right) != 1:
        return False, {}, f"result_count_wrong (got {len(right)}, want 1)"

    result_tok = right[0]
    if result_tok not in RESULT:
        return False, {}, f"result_not_whitelisted: {result_tok!r}"

    if not left:
        return False, {}, "no_tokens_before_slash"

    mandat_tok = left[0]
    if mandat_tok not in MANDAT:
        return False, {}, f"mandat_not_whitelisted: {mandat_tok!r}"

    rest = left[1:]

    opus_list = []
    i = 0
    while i < len(rest) and rest[i] in OPUS:
        opus_list.append(rest[i])
        i += 1
        if len(opus_list) > 2:
            return False, {}, "too_many_opus (max 2)"

    if len(opus_list) < 1:
        return False, {}, "opus_count_zero (min 1)"

    outil_tok = None
    if i < len(rest) and rest[i] in OUTIL:
        outil_tok = rest[i]
        i += 1

    seal_tok = None
    if i < len(rest) and rest[i] in SEAL:
        seal_tok = rest[i]
        i += 1

    if i < len(rest):
        return False, {}, f"unexpected_tokens_after_seal: {rest[i:]!r}"

    if outil_tok == "\u2e38" and seal_tok is None:
        return False, {}, "croix_sang_requires_cercueil"

    parsed = {
        "mandat": NAMES[mandat_tok],
        "mandat_glyph": mandat_tok,
        "opus": [NAMES[t] for t in opus_list],
        "opus_glyphs": opus_list,
        "outil": NAMES[outil_tok] if outil_tok else None,
        "outil_glyph": outil_tok,
        "seal": NAMES[seal_tok] if seal_tok else None,
        "seal_glyph": seal_tok,
        "result": NAMES[result_tok],
        "result_glyph": result_tok,
    }
    return True, parsed, "ok"


if __name__ == "__main__":
    import sys
    line = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "\u271d\ufe0f \U0001f703 \U0001f6e1\ufe0f \u26b0 / \U0001f9f1"
    valid, parsed, reason = parse(line)
    print(f"input : {line}")
    print(f"valid : {valid}")
    print(f"reason: {reason}")
    if valid:
        print(f"parsed: {parsed}")
