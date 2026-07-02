#!/usr/bin/env python3
"""Model routing resolver -- reads docs/spec/model_routing_registry.json
so call sites resolve a ROLE, never hardcode a MODEL TAG.

Fails loud on an unregistered role (fixes the 'silent fallback hides
routing intent' bug MODEL_ROUTING_V1.md section 5 already names once --
generalized here so it can't recur at a new call site).

Usage:
    from tools.model_registry import resolve
    model = resolve("HAL")            # -> "mistral:latest", or raises
    model = resolve("HAL", strict=False)  # -> None if unresolved, warns instead of raising

CLI:
    python3 tools/model_registry.py HAL
    python3 tools/model_registry.py --list
    python3 tools/model_registry.py --check-drift
"""
import json
import os
import sys

REGISTRY_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "docs", "spec", "model_routing_registry.json",
)


class UnregisteredRoleError(Exception):
    pass


def _load():
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def resolve(role, strict=True):
    """Return the resolved model tag for a role, or raise/warn if unknown.

    Deliberately does not silently fall back to a default model for an
    unregistered role -- that silent-fallback pattern is the exact bug
    this registry exists to prevent.
    """
    reg = _load()
    entry = reg["roles"].get(role)
    if entry is None:
        msg = f"role '{role}' is not registered in {REGISTRY_PATH} -- add it, don't guess"
        if strict:
            raise UnregisteredRoleError(msg)
        print(f"WARNING: {msg}", file=sys.stderr)
        return None
    if entry.get("status", "").startswith("RESOLVED_BUT"):
        print(
            f"NOTE: role '{role}' resolves to {entry['resolved_model']!r} "
            f"but status is {entry['status']} -- see {REGISTRY_PATH} for the caveat",
            file=sys.stderr,
        )
    return entry.get("resolved_model")


def list_roles():
    reg = _load()
    return {k: v.get("resolved_model") for k, v in reg["roles"].items()}


def check_drift():
    """Report every role whose status flags an unresolved contradiction."""
    reg = _load()
    drift = {
        k: v for k, v in reg["roles"].items()
        if v.get("status") not in ("RESOLVED", "RESOLVED_BY_DESIGN")
    }
    return drift, reg.get("open_migrations", [])


def main():
    args = sys.argv[1:]
    if not args or args[0] == "--list":
        for role, model in list_roles().items():
            print(f"{role:20s} -> {model}")
        return
    if args[0] == "--check-drift":
        drift, migrations = check_drift()
        if not drift and not migrations:
            print("no drift, no open migrations")
            return
        for role, entry in drift.items():
            print(f"DRIFT  {role:20s} status={entry['status']}")
            for c in entry.get("contradicting_sources", []):
                print(f"       contradicted by {c['file']}:{c.get('line','')} -> {c['value']}")
        for m in migrations:
            print(f"OPEN MIGRATION: {m}")
        return
    role = args[0]
    try:
        model = resolve(role)
        print(model)
    except UnregisteredRoleError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
