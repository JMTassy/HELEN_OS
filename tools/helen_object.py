#!/usr/bin/env python3
"""
helen_object.py — HELEN Object CLI (SOURCEBOUND_OBJECT_OS_V0)

Usage:
  .venv/bin/python tools/helen_object.py create \
    --source src_meta_muse_spark_2026 \
    --claim "AI is moving toward multimodal ambient surfaces."

Output: SOURCEBOUND_OBJECT_RECEIPT_V0 (JSON, authority=false)
Never writes to ledger. Read-only primitive.
"""
import sys, json, uuid, time, hashlib
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import click
from src.helen_sourcebound_object import SourceboundObject, ObjectStatus


def _auto_id(prefix: str, seed: str) -> str:
    h = hashlib.sha256(seed.encode()).hexdigest()[:10]
    return f"{prefix}_{h}"


@click.group()
def cli():
    """HELEN Object Engine — authority=false"""


@cli.command()
@click.option("--source",   required=True,  help="Source reference (e.g. src_meta_muse_spark_2026)")
@click.option("--claim",    required=True,  multiple=True, help="Claim string (repeat for multiple)")
@click.option("--evidence", multiple=True,  help="Evidence ref (auto-generated if omitted)")
@click.option("--risk",     multiple=True,  help="Risk flag (optional)")
@click.option("--validator",default="PASS", show_default=True,
              type=click.Choice(["PASS", "FAIL"]), help="Validator result")
@click.option("--receipt",  default=None,   help="Receipt ref (auto-generated if omitted)")
@click.option("--replay",   default=None,   help="Replay path (auto-generated if omitted)")
@click.option("--pretty/--no-pretty", default=True, help="Pretty-print JSON output")
def create(source, claim, evidence, risk, validator, receipt, replay, pretty):
    """Create a SourceboundObject and emit a SOURCEBOUND_OBJECT_RECEIPT_V0."""
    ts   = int(time.time())
    oid  = str(uuid.uuid4())
    seed = f"{oid}:{source}:{ts}"

    ev_refs  = list(evidence) if evidence else [_auto_id("ev", seed)]
    rcpt_ref = receipt or _auto_id("rcpt", seed)
    rpl_path = replay or f"replay/sourcebound/{oid}"

    try:
        obj = SourceboundObject(object_id=oid, content=source)
        obj = obj.bind_source(source)
        obj = obj.split_claims(list(claim))
        obj = obj.attach_evidence(ev_refs)
        if risk:
            obj = obj.flag_risks(list(risk))
        obj = obj.validate([validator])

        if obj.status == ObjectStatus.REJECTED:
            out = {
                "type":      "SOURCEBOUND_OBJECT_RECEIPT_V0",
                "object_id": oid,
                "status":    "REJECTED",
                "source_ref": source,
                "claims":    list(claim),
                "validator_results": [validator],
                "authority": False,
                "ts":        ts,
            }
            click.echo(json.dumps(out, indent=2 if pretty else None))
            sys.exit(1)

        obj = obj.attach_receipt(rcpt_ref, rpl_path)
        obj = obj.admit()

        out = {
            "type":              "SOURCEBOUND_OBJECT_RECEIPT_V0",
            "object_id":        obj.object_id,
            "status":           obj.status,
            "source_ref":       obj.source_ref,
            "claims":           list(obj.claims),
            "evidence_refs":    list(obj.evidence_refs),
            "risk_flags":       list(obj.risk_flags),
            "validator_results":list(obj.validator_results),
            "receipt_ref":      obj.receipt_ref,
            "replay_path":      obj.replay_path,
            "hash":             obj.hash(),
            "authority":        obj.authority,
            "ts":               ts,
        }
        click.echo(json.dumps(out, indent=2 if pretty else None))

    except ValueError as e:
        click.echo(json.dumps({"error": str(e), "authority": False}), err=True)
        sys.exit(2)


if __name__ == "__main__":
    cli()
