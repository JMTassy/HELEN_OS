#!/usr/bin/env python3
"""Health-check all HELEN OS dashboard endpoints. Exit 0 = healthy."""
import urllib.request
import json
import sys

BASE = "http://127.0.0.1:7000"
CHECKS = [
    ("/api/status",   "json"),
    ("/api/kernel",   "json"),
    ("/api/goblin",   "json"),
    ("/api/terminal", "json"),
    ("/api/semantic", "json"),
    ("/avatar",       "image"),
    ("/",             "html"),
]

ok = True
for path, kind in CHECKS:
    try:
        r = urllib.request.urlopen(BASE + path, timeout=5)
        code = r.getcode()
        mark = "✓" if code == 200 else "?"
        print(f"  {mark}  {code}  {path}")
    except Exception as e:
        print(f"  ✗  ERR  {path}  — {e}")
        ok = False

if not ok:
    print("\nDashboard not healthy. Start with:")
    print("  oracle_town/skills/ops/helen_dashboard/scripts/run_dashboard.sh")
    sys.exit(1)

# Object field summary
data = json.loads(urllib.request.urlopen(BASE + "/api/semantic", timeout=5).read())
objects = data.get("objects", [])
edges   = data.get("edges", [])
by_prov = {}
for o in objects:
    by_prov[o["provenance"]] = by_prov.get(o["provenance"], 0) + 1

print(f"\n  Field: {len(objects)} objects · {len(edges)} edges")
for prov, count in sorted(by_prov.items()):
    print(f"    {prov:12} {count}")
print("\nDashboard OK")
