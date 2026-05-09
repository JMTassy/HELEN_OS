#!/usr/bin/env python3
"""Inspect /api/semantic — print object summary by provenance, type, and confidence."""
import urllib.request
import json
import sys
from collections import Counter

try:
    raw  = urllib.request.urlopen("http://127.0.0.1:7000/api/semantic", timeout=5).read()
    data = json.loads(raw)
except Exception as e:
    print(f"Cannot reach /api/semantic: {e}")
    sys.exit(1)

objects = data.get("objects", [])
edges   = data.get("edges", [])

if not objects:
    print("No objects in semantic field.")
    sys.exit(0)

by_prov = Counter(o["provenance"] for o in objects)
by_type = Counter(o["type"]       for o in objects)
conf_avg = sum(o.get("confidence", 0) for o in objects) / len(objects)
receipted = sum(1 for o in objects if o.get("receipts", 0) > 0)
sovereign = sum(1 for o in objects if o.get("sovereign"))

print(f"Objects : {len(objects)}")
print(f"Edges   : {len(edges)}")
print(f"Receipted: {receipted}/{len(objects)}")
print(f"Sovereign: {sovereign}/{len(objects)}")
print(f"Avg conf : {conf_avg:.3f}")
print()
print("By provenance:")
for prov, count in sorted(by_prov.items()):
    print(f"  {prov:12} {count}")
print()
print("By type:")
for typ, count in sorted(by_type.items()):
    print(f"  {typ:12} {count}")
print()
print("Top 5 by confidence:")
for o in sorted(objects, key=lambda x: x.get("confidence", 0), reverse=True)[:5]:
    h = o.get("hash", "")[:8] or "–"
    print(f"  [{o.get('confidence',0):.3f}] {o['type']:8} {o['provenance']:10} {h}  {o.get('subject','')[:58]}")
