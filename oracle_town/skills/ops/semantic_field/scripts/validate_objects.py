#!/usr/bin/env python3
"""Validate all semantic objects against the canonical schema. Exit 0 = valid."""
import urllib.request
import json
import sys

REQUIRED    = {"id", "type", "subject", "relations", "confidence",
               "receipts", "timestamp", "provenance", "sovereign", "hash"}
VALID_TYPES = {"EVENT", "EPOCH", "ACTION", "RECEIPT"}
VALID_PROV  = {"kernel", "goblin", "terminal"}

try:
    raw  = urllib.request.urlopen("http://127.0.0.1:7000/api/semantic", timeout=5).read()
    data = json.loads(raw)
except Exception as e:
    print(f"Cannot reach /api/semantic: {e}")
    sys.exit(1)

objects = data.get("objects", [])
errors  = []

for i, o in enumerate(objects):
    oid = o.get("id", f"[{i}]")
    missing = REQUIRED - set(o.keys())
    if missing:
        errors.append(f"{oid}: missing fields {sorted(missing)}")
    if o.get("type") not in VALID_TYPES:
        errors.append(f"{oid}: invalid type '{o.get('type')}'")
    if o.get("provenance") not in VALID_PROV:
        errors.append(f"{oid}: invalid provenance '{o.get('provenance')}'")
    conf = o.get("confidence")
    if conf is not None and not (0.0 <= conf <= 1.0):
        errors.append(f"{oid}: confidence out of range ({conf})")
    if not isinstance(o.get("relations"), list):
        errors.append(f"{oid}: relations must be a list")

if errors:
    print(f"VALIDATION FAILED — {len(errors)} error(s):\n")
    for e in errors:
        print(f"  {e}")
    sys.exit(1)

print(f"OK — {len(objects)} objects valid against canonical schema")
