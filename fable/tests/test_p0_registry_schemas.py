"""P0 gate: registry count + 3 core schemas validate. Data only — no runtime."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

try:
    import jsonschema
    from jsonschema import Draft202012Validator
except ImportError:  # pragma: no cover
    jsonschema = None

FABLE = Path(__file__).resolve().parents[1]
SCHEMAS = FABLE / "schemas"
REG = FABLE / "registry"
FIXTURES = FABLE / "tests" / "fixtures"

pytestmark = pytest.mark.skipif(jsonschema is None, reason="jsonschema not installed")


def _load(p: Path):
    return json.loads(p.read_text())


def _validator(name: str) -> Draft202012Validator:
    schema = _load(SCHEMAS / name)
    return Draft202012Validator(schema)


def test_registry_has_exactly_50_goblins():
    doc = _load(REG / "goblins.json")
    assert doc["schema"] == "FableGoblinRegistryV1"
    assert doc["authority"] is False
    assert doc["count"] == 50
    assert len(doc["goblins"]) == 50
    ids = [g["goblin_id"] for g in doc["goblins"]]
    assert len(ids) == len(set(ids))


def test_guild_counts_match_architecture():
    expected = {
        "observers": 8,
        "challengers": 8,
        "causal_analysts": 6,
        "builders": 6,
        "verifier_planners": 5,
        "provenance_keepers": 5,
        "compressors": 4,
        "risk_goblins": 4,
        "chiddush_goblins": 3,
        "reducer_candidates": 1,
    }
    doc = _load(REG / "goblins.json")
    from collections import Counter

    c = Counter(g["guild"] for g in doc["goblins"])
    assert dict(c) == expected


def test_every_registry_entry_matches_schema():
    v = _validator("goblin_registry_entry.schema.json")
    doc = _load(REG / "goblins.json")
    for g in doc["goblins"]:
        errors = sorted(v.iter_errors(g), key=lambda e: e.path)
        assert not errors, f"{g['goblin_id']}: {errors[0].message}"


def test_every_goblin_forbids_admit_and_ledger():
    doc = _load(REG / "goblins.json")
    for g in doc["goblins"]:
        f = set(g["forbidden"])
        assert "admit" in f
        assert "write_ledger" in f
        assert "verify_own_claim" in f
        assert g["authority"] is False
        assert g["output_schema"] == "GoblinProposalV1"


def test_goblin_proposal_fixture_valid():
    v = _validator("goblin_proposal.schema.json")
    inst = _load(FIXTURES / "proposal_ok.json")
    v.validate(inst)


def test_goblin_proposal_rejects_authority_true():
    v = _validator("goblin_proposal.schema.json")
    inst = _load(FIXTURES / "proposal_ok.json")
    bad = dict(inst)
    bad["authority"] = True
    with pytest.raises(jsonschema.ValidationError):
        v.validate(bad)


def test_epoch_fixture_valid():
    v = _validator("epoch.schema.json")
    v.validate(_load(FIXTURES / "epoch_ok.json"))


def test_epoch_rejects_admit_recommendation():
    v = _validator("epoch.schema.json")
    inst = _load(FIXTURES / "epoch_ok.json")
    bad = dict(inst)
    bad["recommendation"] = "ADMIT"
    with pytest.raises(jsonschema.ValidationError):
        v.validate(bad)


def test_compost_fixture_valid():
    v = _validator("compost.schema.json")
    v.validate(_load(FIXTURES / "compost_ok.json"))


def test_compost_rejects_missing_digest():
    v = _validator("compost.schema.json")
    inst = _load(FIXTURES / "compost_ok.json")
    bad = dict(inst)
    del bad["digest"]
    with pytest.raises(jsonschema.ValidationError):
        v.validate(bad)
