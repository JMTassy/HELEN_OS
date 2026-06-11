"""Manifest registry — non-sovereign capability manifest store.

Responsibilities:
  register(manifest)           → ManifestRecord | raises ManifestRegistrationError
  get(manifest_id)             → ManifestRecord | None
  get_by_hash(manifest_hash)   → ManifestRecord | None
  link_skill(skill_id, id)     → None | raises
  get_manifest_for_skill(id)   → ManifestRecord | None
  validate_skill_allowed(...)  → bool

Does NOT:
  - mutate governed/sovereign state
  - append to ledger
  - issue verdicts
  - impersonate MAYOR or Reducer
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Mapping


REQUIRED_AUTHORITY = "NONE"


class ManifestRegistrationError(ValueError):
    """Raised when a manifest fails validation or uniqueness checks."""


@dataclass(frozen=True)
class ManifestRecord:
    manifest_id: str
    manifest_hash: str
    allowed_skills: tuple[str, ...]
    domain_category: str
    provider_class: str
    authority: str
    provenance: dict[str, Any]


def _canonical_hash(manifest: Mapping[str, Any]) -> str:
    raw = json.dumps(manifest, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return "sha256:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()


class ManifestRegistry:
    """In-memory, non-sovereign manifest registry.

    Thread safety: not guaranteed. Single-process use only.
    Persistence: none. Rebuilt from admission receipts on restart.
    """

    def __init__(self) -> None:
        self._by_id: dict[str, ManifestRecord] = {}
        self._by_hash: dict[str, str] = {}       # hash -> manifest_id
        self._skill_map: dict[str, str] = {}     # skill_id -> manifest_id

    # ── registration ─────────────────────────────────────────────────────────

    def register(self, manifest: Mapping[str, Any]) -> ManifestRecord:
        """Validate and store a manifest. Idempotent for identical content."""
        manifest_id = manifest.get("manifest_id")
        if not isinstance(manifest_id, str) or not manifest_id:
            raise ManifestRegistrationError("manifest_id required")

        authority = manifest.get("authority", REQUIRED_AUTHORITY)
        if authority != REQUIRED_AUTHORITY:
            raise ManifestRegistrationError(
                f"manifest authority must be '{REQUIRED_AUTHORITY}', got: {authority!r}"
            )

        allowed_skills = manifest.get("allowed_skills")
        if not isinstance(allowed_skills, list):
            raise ManifestRegistrationError("allowed_skills must be a list")

        domain_category = manifest.get("domain_category")
        if not isinstance(domain_category, str) or not domain_category:
            raise ManifestRegistrationError("domain_category required")

        provider_class = manifest.get("provider_class")
        if not isinstance(provider_class, str) or not provider_class:
            raise ManifestRegistrationError("provider_class required")

        manifest_hash = _canonical_hash(manifest)

        if manifest_id in self._by_id:
            existing = self._by_id[manifest_id]
            if existing.manifest_hash != manifest_hash:
                raise ManifestRegistrationError(
                    f"manifest_id {manifest_id!r} already registered with a different hash — "
                    "update requires deregistration first"
                )
            return existing  # idempotent

        record = ManifestRecord(
            manifest_id=manifest_id,
            manifest_hash=manifest_hash,
            allowed_skills=tuple(str(s) for s in allowed_skills),
            domain_category=domain_category,
            provider_class=provider_class,
            authority=authority,
            provenance=dict(manifest.get("provenance", {})),
        )
        self._by_id[manifest_id] = record
        self._by_hash[manifest_hash] = manifest_id
        return record

    # ── lookup ────────────────────────────────────────────────────────────────

    def get(self, manifest_id: str) -> ManifestRecord | None:
        return self._by_id.get(manifest_id)

    def get_by_hash(self, manifest_hash: str) -> ManifestRecord | None:
        mid = self._by_hash.get(manifest_hash)
        return self._by_id.get(mid) if mid else None

    def get_manifest_for_skill(self, skill_id: str) -> ManifestRecord | None:
        mid = self._skill_map.get(skill_id)
        return self._by_id.get(mid) if mid else None

    # ── skill linkage ─────────────────────────────────────────────────────────

    def link_skill(self, skill_id: str, manifest_id: str) -> None:
        """Link skill_id to a registered manifest. Fails if not registered or not allowed."""
        record = self._by_id.get(manifest_id)
        if record is None:
            raise ManifestRegistrationError(
                f"manifest_id {manifest_id!r} not registered"
            )
        if skill_id not in record.allowed_skills:
            raise ManifestRegistrationError(
                f"skill_id {skill_id!r} not in allowed_skills of manifest {manifest_id!r}"
            )
        self._skill_map[skill_id] = manifest_id

    # ── gate check ────────────────────────────────────────────────────────────

    def validate_skill_allowed(
        self,
        skill_id: str,
        manifest_id: str,
        manifest_hash: str,
    ) -> bool:
        """Return True only when manifest is known, hash matches, and skill is allowed."""
        record = self._by_id.get(manifest_id)
        if record is None:
            return False
        if record.manifest_hash != manifest_hash:
            return False
        return skill_id in record.allowed_skills
