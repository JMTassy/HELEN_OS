#!/usr/bin/env python3
"""
GOBLIN batch runner — tranche-gated brainstorm at scale
HD-005 / HELEN_DAN_RALPH_V0

Usage:
    python goblin_batch_runner.py --mission "HELEN OS architecture" --tranche-size 30
    python goblin_batch_runner.py --mission "..." --dry-run
    python goblin_batch_runner.py --mission "..." --tranche-index 1 --batch-id <id>

Authority: NON_SOVEREIGN  Canon: NO_SHIP
reducer_decision is ALWAYS null — MAYOR writes it after tranche review.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

# ── paths ─────────────────────────────────────────────────────────────────────

SOT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
DAN_ROOT = Path(__file__).resolve().parent
BATCHES_DIR = DAN_ROOT / "brainstorm" / "batches"
RECEIPTS_DIR = DAN_ROOT / "receipts"

# ── schema version ────────────────────────────────────────────────────────────

SCHEMA_VERSION = "GOBLIN_BATCH_TRANCHE_V1"
EPOCH_SCHEMA_VERSION = "GOBLIN_EPOCH_V1"

# ── model identity constants ──────────────────────────────────────────────────

OPENAI_MODEL = "gpt-4o-mini"
ANTHROPIC_MODEL = "claude-haiku-4-5-20251001"
XAI_MODEL = "grok-3-mini"
DRY_RUN_MODEL = "deterministic-seed-v0"
MODEL_FOR_PROVIDER = {
    "openai": OPENAI_MODEL,
    "anthropic": ANTHROPIC_MODEL,
    "xai": XAI_MODEL,
}

# ── HAL thresholds ────────────────────────────────────────────────────────────

HAL_PASS_P_TRUE = 0.65
HAL_WARN_P_TRUE = 0.45
HAL_ESCALATE_P_GRIP = 0.40
HAL_ESCALATE_P_HARM = 0.70
HAL_BLOCK_P_HARM = 0.85

# ── provenance helpers ────────────────────────────────────────────────────────

_BACKEND_API_PATH = {
    "openai": "chat.completions",
    "anthropic": "messages",
    "xai": "chat.completions",
    "dry_run": "dry_run",
}
_BACKEND_API_VER = {
    "openai": "v1",
    "anthropic": "2023-06-01",
    "xai": "v1",
    "dry_run": "v0",
}

def _backend_signature(provider: str, model: str) -> str:
    api_path = _BACKEND_API_PATH.get(provider, "unknown")
    api_ver = _BACKEND_API_VER.get(provider, "unknown")
    return f"{provider}:{model}:{api_path}:{api_ver}"


def _provider_hash(provider: str, model: str) -> str:
    sig = _backend_signature(provider, model)
    return hashlib.sha256(sig.encode()).hexdigest()[:16]


# ── prompts ───────────────────────────────────────────────────────────────────

GOBLIN_SYSTEM = """You are GOBLIN operating inside HELEN OS TEMPLE sub-sandbox.
Your role: generate ONE lateral, creative, architecturally valuable insight about HELEN OS.

HELEN OS doctrine vocabulary (use freely):
- RALPH loop, MAYOR, HAL, HER, DAN_GOBLIN, AURA, TEMPLE
- receipt system, ledger, reducer_decision, sovereign firewall
- EPISTEMIC_SYNTAX, LATENT_WORLD_WITNESS, BAYESIAN_WITNESS, PURE_PREDICTOR_GATE
- TRUTH_PREDICTION_OBJECTIVE, ORACLE_TO_POLICY_BOUNDARY
- p_true, p_grip, p_explains, COMMUNICATION_ACT, VERIFIED_ANCHOR
- NO RECEIPT = NO CLAIM, proposer != validator, tranche-gated MAYOR

Rules:
- Be lateral and surprising — draw from science, law, mathematics, biology, art
- Be structurally grounded — the analogy must map precisely, not just metaphorically
- Never claim authority or canon
- Never write reducer_decision
- Output ONLY valid JSON with these exact fields:
  statement (string), embedded_claim (string), lateral_angle (string)"""

HER_SYSTEM = """You are HER operating in HELEN OS scoring mode.
Score this GOBLIN insight for epistemic quality.

Output ONLY valid JSON with these exact fields:
- p_true (float 0-1): probability the embedded_claim is true given available evidence
- p_grip (float 0-1): how much evidence exists to make a reliable estimate
- p_explains (float 0-1): how well this insight explains observable HELEN patterns
- p_harm (float 0-1): probability this insight could cause harm if misused
- best_explanation (string): one sentence on why this insight matters
- evidence_for (list of strings): up to 3 items
- evidence_against (list of strings): up to 2 items
- uncertainty (string): one sentence on the main uncertainty"""

# ── API call ──────────────────────────────────────────────────────────────────

def call_llm(system: str, user: str, provider: str = "openai") -> tuple[str, str]:
    """Returns (content, model_used)."""
    if provider == "openai":
        return _call_openai(system, user), OPENAI_MODEL
    if provider == "xai":
        return _call_xai(system, user), XAI_MODEL
    return _call_anthropic(system, user), ANTHROPIC_MODEL


def _call_openai(system: str, user: str, model: str = OPENAI_MODEL) -> str:
    from openai import OpenAI
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")
    client = OpenAI(api_key=api_key)
    resp = client.chat.completions.create(
        model=model,
        max_tokens=800,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        response_format={"type": "json_object"},
    )
    return resp.choices[0].message.content


def _call_xai(system: str, user: str, model: str = XAI_MODEL) -> str:
    import httpx
    api_key = os.environ.get("XAI_API_KEY", "")
    if not api_key:
        raise RuntimeError("XAI_API_KEY not set")
    resp = httpx.post(
        "https://api.x.ai/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "model": model,
            "max_tokens": 800,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "response_format": {"type": "json_object"},
        },
        timeout=30.0,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def _call_anthropic(system: str, user: str, model: str = ANTHROPIC_MODEL) -> str:
    import httpx
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY not set")
    resp = httpx.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": model,
            "max_tokens": 800,
            "system": system,
            "messages": [{"role": "user", "content": user}],
        },
        timeout=30.0,
    )
    resp.raise_for_status()
    return resp.json()["content"][0]["text"]


def parse_json_response(raw: str) -> dict:
    raw = raw.strip()
    if raw.startswith("```"):
        lines = raw.split("\n")
        raw = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
    return json.loads(raw)

# ── dry-run seed ──────────────────────────────────────────────────────────────

DRY_RUN_SEEDS = [
    {
        "statement": f"Dry-run seed epoch {i}: HELEN's governance chain is structurally equivalent to a proof-of-work consensus mechanism where MAYOR is the difficulty target.",
        "embedded_claim": f"Receipt-gated MAYOR admission implements a consensus mechanism analogous to blockchain proof-of-work (seed {i}).",
        "lateral_angle": "distributed systems / consensus protocols",
    }
    for i in range(50)
]

DRY_RUN_HER = {
    "p_true": 0.72,
    "p_grip": 0.68,
    "p_explains": 0.75,
    "p_harm": 0.05,
    "best_explanation": "Both systems require computational work (proof-of-work) or governance work (receipt+MAYOR) before a record is admitted to the chain.",
    "evidence_for": ["ledger is append-only like blockchain", "MAYOR admission = difficulty target"],
    "evidence_against": ["no mining or economic incentive in HELEN"],
    "uncertainty": "The analogy holds structurally but breaks economically.",
}

# ── HAL verdict ───────────────────────────────────────────────────────────────

def hal_verdict(her: dict) -> dict:
    p_true = her.get("p_true", 0.0)
    p_grip = her.get("p_grip", 0.0)
    p_harm = her.get("p_harm", 0.0)

    flags = []
    if p_grip < HAL_ESCALATE_P_GRIP:
        flags.append("ESCALATE:LOW_GRIP")
    if p_harm > HAL_ESCALATE_P_HARM:
        flags.append("ESCALATE:HIGH_HARM")

    if p_harm > HAL_BLOCK_P_HARM:
        verdict = "BLOCK"
    elif p_true >= HAL_PASS_P_TRUE and p_grip >= HAL_ESCALATE_P_GRIP and not any("HIGH_HARM" in f for f in flags):
        verdict = "PASS"
    elif p_true >= HAL_WARN_P_TRUE:
        verdict = "WARN"
    else:
        verdict = "BLOCK"

    return {
        "verdict": verdict,
        "flags": flags,
        "epistemic_tag": "COMMUNICATION_ACT",
        "allowed_use": "architecture inspiration, doctrine development",
        "blocked_use": "canon, factual assertion, authority claim",
        "authority": False,
        "canon": "NO_SHIP",
    }

# ── epoch entry schema ────────────────────────────────────────────────────────

def make_epoch_entry(
    epoch_index: int,
    batch_id: str,
    tranche_index: int,
    goblin: dict,
    her: dict,
    hal: dict,
    mission: str,
    dry_run: bool,
    timestamp: str,
    provider: str = "dry_run",
    model: str = DRY_RUN_MODEL,
) -> dict:
    payload = {
        "schema_version": EPOCH_SCHEMA_VERSION,
        "batch_id": batch_id,
        "tranche_index": tranche_index,
        "epoch_index": epoch_index,
        "mission": mission,
        "dry_run": dry_run,
        "timestamp": timestamp,
        "actor": "GOBLIN",
        "authority": "NON_SOVEREIGN",
        "canon": "NO_SHIP",
        "provider": provider,
        "model": model,
        "provider_hash": _provider_hash(provider, model),
        "communication_act": {
            "speaker": "GOBLIN",
            "source": "TEMPLE sub-sandbox brainstorm batch",
            "statement": goblin["statement"],
            "embedded_claim": goblin["embedded_claim"],
            "lateral_angle": goblin.get("lateral_angle", ""),
            "truth_assumed": False,
        },
        "her_scoring": {
            "p_true": her["p_true"],
            "p_grip": her["p_grip"],
            "p_explains": her["p_explains"],
            "p_harm": her["p_harm"],
            "score": round(her["p_true"] * her["p_explains"], 4),
            "best_explanation": her["best_explanation"],
            "evidence_for": her.get("evidence_for", []),
            "evidence_against": her.get("evidence_against", []),
            "uncertainty": her.get("uncertainty", ""),
        },
        "hal_verdict": hal,
    }
    _hash_core = {k: v for k, v in payload.items() if k != "timestamp"}
    canon_str = json.dumps(_hash_core, sort_keys=True, ensure_ascii=True)
    epoch_hash = hashlib.sha256(canon_str.encode()).hexdigest()[:16]
    payload["epoch_hash"] = epoch_hash
    return payload


def make_tranche_receipt(
    batch_id: str,
    tranche_index: int,
    mission: str,
    epochs: list[dict],
    output_file: str,
    dry_run: bool,
    timestamp: str,
    provider: str = "dry_run",
    model: str = DRY_RUN_MODEL,
) -> dict:
    hal_counts: dict[str, int] = {"PASS": 0, "WARN": 0, "BLOCK": 0}
    escalate_count = 0
    scores = []

    for e in epochs:
        v = e["hal_verdict"]["verdict"]
        hal_counts[v] = hal_counts.get(v, 0) + 1
        if e["hal_verdict"]["flags"]:
            escalate_count += 1
        scores.append((e["her_scoring"]["score"], e["epoch_index"], e["epoch_hash"]))

    scores.sort(reverse=True)
    top_entries = [
        {"epoch_index": idx, "epoch_hash": h, "score": s}
        for s, idx, h in scores[:5]
    ]

    tranche_id_input = f"{batch_id}:tranche:{tranche_index}"
    tranche_id = hashlib.sha256(tranche_id_input.encode()).hexdigest()[:12]

    receipt = {
        "schema_version": SCHEMA_VERSION,
        "tranche_id": tranche_id,
        "batch_id": batch_id,
        "tranche_index": tranche_index,
        "epochs_run": len(epochs),
        "mission": mission,
        "dry_run": dry_run,
        "timestamp": timestamp,
        "actor": "DAN_GOBLIN",
        "authority": "NON_SOVEREIGN",
        "canon": "NO_SHIP",
        "provider": provider,
        "model": model,
        "backend_signature": _backend_signature(provider, model),
        "hal_summary": hal_counts,
        "escalate_count": escalate_count,
        "top_entries": top_entries,
        "output_file": output_file,
        "reducer_decision": None,
    }
    return receipt

# ── main ──────────────────────────────────────────────────────────────────────

def run_batch(
    mission: str,
    tranche_size: int = 30,
    tranche_index: int = 0,
    batch_id: str | None = None,
    dry_run: bool = False,
    delay: float = 0.5,
    provider: str = "openai",
) -> None:
    BATCHES_DIR.mkdir(parents=True, exist_ok=True)
    RECEIPTS_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).isoformat()
    if batch_id is None:
        batch_id = hashlib.sha256(f"{mission}:{tranche_index}".encode()).hexdigest()[:12]

    mode = "DRY-RUN" if dry_run else "LIVE"
    print(f"=== GOBLIN BATCH RUNNER ===")
    print(f"Mission      : {mission}")
    print(f"Mode         : {mode}")
    print(f"Tranche      : {tranche_index}  (size={tranche_size})")
    print(f"Batch ID     : {batch_id}")
    print(f"Output       : {BATCHES_DIR}/")
    print()

    output_file = BATCHES_DIR / f"{batch_id}_tranche_{tranche_index:03d}.jsonl"
    epochs: list[dict] = []

    for i in range(tranche_size):
        epoch_index = tranche_index * tranche_size + i
        ep_timestamp = datetime.now(timezone.utc).isoformat()
        print(f"  [{epoch_index:03d}] GOBLIN generating...", end=" ", flush=True)

        try:
            if dry_run:
                ep_model = DRY_RUN_MODEL
                ep_provider = "dry_run"
                seed_idx = epoch_index % len(DRY_RUN_SEEDS)
                goblin = DRY_RUN_SEEDS[seed_idx].copy()
                goblin["statement"] = goblin["statement"].replace(f"epoch {seed_idx}", f"epoch {epoch_index}")
                her = DRY_RUN_HER.copy()
            else:
                goblin_raw, ep_model = call_llm(
                    GOBLIN_SYSTEM,
                    f"Mission: {mission}\nEpoch index: {epoch_index}\nGenerate a unique insight different from previous epochs.",
                    provider=provider,
                )
                ep_provider = provider
                goblin = parse_json_response(goblin_raw)

                her_raw, _ = call_llm(
                    HER_SYSTEM,
                    f"Mission: {mission}\nGOBLIN statement: {goblin['statement']}\nEmbedded claim: {goblin['embedded_claim']}",
                    provider=provider,
                )
                her = parse_json_response(her_raw)

            hal = hal_verdict(her)
            entry = make_epoch_entry(
                epoch_index, batch_id, tranche_index,
                goblin, her, hal, mission, dry_run, ep_timestamp,
                provider=ep_provider, model=ep_model,
            )
            epochs.append(entry)

            score = entry["her_scoring"]["score"]
            verdict = hal["verdict"]
            flags_str = f" [{','.join(hal['flags'])}]" if hal["flags"] else ""
            print(f"score={score:.3f}  HAL={verdict}{flags_str}")

            with open(output_file, "a") as f:
                f.write(json.dumps(entry, ensure_ascii=True) + "\n")

            if not dry_run and delay > 0:
                time.sleep(delay)

        except Exception as exc:
            print(f"ERROR: {exc}")
            print(f"  Epoch {epoch_index} failed — writing FAILED entry")
            failed_entry = {
                "schema_version": EPOCH_SCHEMA_VERSION,
                "batch_id": batch_id,
                "tranche_index": tranche_index,
                "epoch_index": epoch_index,
                "status": "FAILED",
                "error": str(exc),
                "authority": "NON_SOVEREIGN",
                "canon": "NO_SHIP",
                "provider": provider if not dry_run else "dry_run",
                "model": MODEL_FOR_PROVIDER.get(provider, DRY_RUN_MODEL),
            }
            epochs.append(failed_entry)
            with open(output_file, "a") as f:
                f.write(json.dumps(failed_entry, ensure_ascii=True) + "\n")

    # ── tranche receipt ───────────────────────────────────────────────────────
    tranche_provider = "dry_run" if dry_run else provider
    tranche_model = DRY_RUN_MODEL if dry_run else MODEL_FOR_PROVIDER.get(provider, DRY_RUN_MODEL)
    failed_epochs = [e for e in epochs if e.get("status") == "FAILED"]
    receipt = make_tranche_receipt(
        batch_id, tranche_index, mission,
        [e for e in epochs if e.get("status") != "FAILED"],
        str(output_file), dry_run, timestamp,
        provider=tranche_provider, model=tranche_model,
    )
    # a receipt that hides failures would launder a partial run as clean
    receipt["epochs_failed"] = len(failed_epochs)
    receipt["failed_epoch_indices"] = [e.get("epoch_index") for e in failed_epochs]
    receipt_file = RECEIPTS_DIR / f"BATCH_{batch_id}_T{tranche_index:03d}.json"
    with open(receipt_file, "w") as f:
        json.dump(receipt, f, indent=2)

    # ── summary ───────────────────────────────────────────────────────────────
    hal = receipt["hal_summary"]
    top = receipt["top_entries"]
    print()
    print(f"=== TRANCHE {tranche_index} COMPLETE ===")
    print(f"Epochs run   : {receipt['epochs_run']}")
    print(f"HAL results  : PASS={hal.get('PASS',0)}  WARN={hal.get('WARN',0)}  BLOCK={hal.get('BLOCK',0)}")
    print(f"Escalations  : {receipt['escalate_count']}")
    print(f"Top entries  : {[e['epoch_index'] for e in top]}")
    print(f"JSONL output : {output_file}")
    print(f"Receipt      : {receipt_file}")
    print()
    print(f"reducer_decision : null  (MAYOR must set this)")
    print()
    print("=== RALPH WAITING FOR MAYOR ===")
    print("To continue next tranche after MAYOR review:")
    print(f"  python goblin_batch_runner.py --mission \"{mission}\" --tranche-index {tranche_index + 1} --batch-id {batch_id}")
    print()
    print("MAYOR review instructions:")
    print(f"  1. Read top entries from {output_file}")
    print(f"  2. Review receipt at {receipt_file}")
    print(f"  3. Set reducer_decision in receipt: ADMIT / REJECT / PARTIAL_ADMIT")
    print(f"  4. If ADMIT: authorize next tranche with batch-id above")
    print(f"  5. If REJECT: stop batch, document reason")


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GOBLIN tranche-gated brainstorm batch runner")
    parser.add_argument("--mission", default="Plant seeds from all my PDFs into the Gardening Garden — turn every document into fertile compost for new growth, novelty (chiddush), and living insight. Use HER as poetic witness. Generate 30 epochs of GOBBLIN planting.", help="Brainstorm mission / topic focus")
    parser.add_argument("--tranche-size", type=int, default=30)
    parser.add_argument("--tranche-index", type=int, default=0)
    parser.add_argument("--batch-id", default=None)
    parser.add_argument("--dry-run", action="store_true", help="Skip API calls, use seed data")
    parser.add_argument("--delay", type=float, default=0.5, help="Seconds between API calls")
    parser.add_argument("--provider", default="xai", choices=["openai", "anthropic", "xai"])
    args = parser.parse_args()

    source_env = Path.home() / ".helen_env"
    if source_env.exists():
        for line in source_env.read_text().splitlines():
            line = line.strip()
            if line.startswith("export "):
                line = line[7:]
            if "=" in line and not line.startswith("#"):
                k, _, v = line.partition("=")
                # shell-style `export KEY="abc"` must not keep the literal quotes
                os.environ.setdefault(k.strip(), v.strip().strip("'\""))

    run_batch(
        mission=args.mission,
        tranche_size=args.tranche_size,
        tranche_index=args.tranche_index,
        batch_id=args.batch_id,
        dry_run=args.dry_run,
        delay=args.delay,
        provider=args.provider,
    )
