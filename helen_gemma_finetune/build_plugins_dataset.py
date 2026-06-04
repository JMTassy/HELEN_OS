"""
build_plugins_dataset.py — generate a HELEN-voice SFT dataset from the canonical
plugin allowlist. Deterministic: same source → same dataset (receiptable).

Reads the SOT's registries/plugins_allowlist.json (read-only) and emits
helen_plugins_sft.jsonl: HELEN explaining each plugin in her own voice, with the
governance facts baked in (allowed_writers, receipt_required, "not listed = can't
write the ledger"). Plus #pluginAGI doctrine (NON_SOVEREIGN / NO_CLAIM).

No private data: the allowlist is governance metadata only. This is the clean
'#PLUGINS' slice the operator asked to prioritise.
"""
import json, hashlib, os
from pathlib import Path

SOT = Path.home() / "Documents/GitHub/helen_os_v1"
ALLOWLIST = SOT / "registries/plugins_allowlist.json"
OUT = Path(__file__).parent / "helen_plugins_sft.jsonl"


def ex(user, assistant):
    return {"conversations": [{"role": "user", "content": user},
                              {"role": "assistant", "content": assistant}]}


def main():
    d = json.loads(ALLOWLIST.read_text())
    rows = []

    # Doctrine: what plugins ARE under HELEN
    rows.append(ex("What is a HELEN plugin?",
        "A plugin is an allowed tool. The rule is simple: only receipt-bound outputs are "
        "admissible, and a plugin not on the allowlist cannot write to the ledger. No receipt = no claim."))
    rows.append(ex("Can a plugin that isn't on the allowlist write to the ledger?",
        "No. The allowlist is the boundary — if a plugin isn't listed, its output carries no "
        "constitutional weight and it cannot touch the ledger. That's the point of the registry."))
    rows.append(ex("What is #pluginAGI?",
        "It's exploratory material — NON_SOVEREIGN, NO_CLAIM, analysis only. Myth as render-fuel, "
        "not authority. I can reason about it, but it doesn't get to declare anything true."))

    # Per-plugin examples, generated from the canonical allowlist
    for tier_key, tier in d.items():
        if not tier_key.startswith("tier_") or "plugins" not in tier:
            continue
        for name, p in tier["plugins"].items():
            pid = p.get("plugin_id", name)
            desc = p.get("description", "").rstrip(".")
            writers = ", ".join(p.get("allowed_writers", [])) or "no one"
            receipt = "emits a receipt" if p.get("receipt_required") else "does not require a receipt"
            tier_n = p.get("tier", "?")

            rows.append(ex(f"What does the {name} plugin do?",
                f"{pid}: it {desc[0].lower()}{desc[1:]}. It's a tier-{tier_n} plugin and {receipt}. "
                f"Authority stays false — it validates, it doesn't rule."))
            rows.append(ex(f"Who is allowed to write with {pid}?",
                f"Allowed writers: {writers}. Anyone else is rejected at the boundary. "
                f"And remember — {pid} {'must emit a receipt' if p.get('receipt_required') else 'is receipt-optional'}, "
                f"because no receipt = no claim."))

    OUT.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n")
    sha = hashlib.sha256(OUT.read_bytes()).hexdigest()[:16]
    print(f"wrote {len(rows)} HELEN plugin examples → {OUT.name}")
    print(f"source: {ALLOWLIST.name}  dataset_sha256: {sha}")


if __name__ == "__main__":
    main()
