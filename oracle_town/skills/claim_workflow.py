"""
K2 Claim Workflow Handler — No Self-Validation

This module manages the claim lifecycle:
1. Skill generates LP-### claim (map generation claim)
2. Foreman receives claim in pending.md
3. Foreman approves/rejects/merges
4. Claim flows to next phase (drafting, visualization, etc.)

K2 Rule: Proposer (MapGeneratorSkill) ≠ Validator (Foreman)
"""

import json
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime, UTC
from dataclasses import dataclass, asdict


@dataclass
class Claim:
    """Represents a claim for Foreman curation"""
    claim_id: str
    type: str  # "map_generation", "connection", "energy_observation", etc.
    author: str  # "MapGeneratorSkill", "LateralPattern", etc.
    statement: str  # The actual claim
    map_hash: Optional[str] = None  # For map generation claims
    status: str = "pending"  # pending, accepted, rejected, merged
    created_at: str = ""
    curated_at: Optional[str] = None
    curator: Optional[str] = None
    curation_reason: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)

    @staticmethod
    def from_dict(data: Dict) -> "Claim":
        """Create Claim from dictionary"""
        return Claim(**data)


class ClaimWorkflow:
    """Manages claim lifecycle: proposal → pending → curation → accepted/rejected"""

    def __init__(self, pending_path: Optional[str] = None, accepted_path: Optional[str] = None, rejected_path: Optional[str] = None):
        """
        Initialize claim workflow manager.

        Args:
            pending_path: Path to pending.md (Foreman inbox)
            accepted_path: Path to accepted.md (approved claims)
            rejected_path: Path to rejected.md (audit trail)
        """
        self.pending_path = Path(pending_path or "artifacts/pending.md")
        self.accepted_path = Path(accepted_path or "artifacts/accepted.md")
        self.rejected_path = Path(rejected_path or "artifacts/rejected.md")

        # Ensure parent directories exist
        self.pending_path.parent.mkdir(parents=True, exist_ok=True)

    def propose_claim(self, claim: Claim) -> None:
        """
        Propose a claim to Foreman (write to pending.md).

        K2 Rule: Skill proposes, Foreman validates (not self-validating).

        Args:
            claim: Claim to propose
        """
        if not claim.created_at:
            claim.created_at = datetime.now(UTC).replace(tzinfo=None).isoformat()

        # Append claim to pending.md (Foreman inbox)
        with open(self.pending_path, "a") as f:
            f.write(f"\n## {claim.claim_id}\n")
            f.write(f"**Author:** {claim.author}\n")
            f.write(f"**Type:** {claim.type}\n")
            f.write(f"**Statement:** {claim.statement}\n")
            if claim.map_hash:
                f.write(f"**Map Hash:** {claim.map_hash}\n")
            f.write(f"**Status:** {claim.status}\n")
            f.write(f"**Created At:** {claim.created_at}\n")

    def accept_claim(self, claim_id: str, curator: str, reason: str = "") -> None:
        """
        Accept a claim (Foreman decision).

        K2 approved: Foreman (validator) accepts skill's (proposer) claim.

        Args:
            claim_id: ID of claim to accept
            curator: Who approved (Foreman role)
            reason: Curation reason (optional)
        """
        # Find and remove from pending
        claim_data = self._find_and_remove_from_pending(claim_id)
        if not claim_data:
            raise ValueError(f"Claim {claim_id} not found in pending")

        claim = Claim.from_dict(claim_data) if isinstance(claim_data, dict) else claim_data
        claim.status = "accepted"
        claim.curated_at = datetime.now(UTC).replace(tzinfo=None).isoformat()
        claim.curator = curator
        claim.curation_reason = reason

        # Write to accepted.md
        self._write_claim(self.accepted_path, claim)

    def reject_claim(self, claim_id: str, curator: str, reason: str = "") -> None:
        """
        Reject a claim (Foreman decision).

        K2 rejected: Foreman declines skill's claim with audit trail.

        Args:
            claim_id: ID of claim to reject
            curator: Who rejected (Foreman role)
            reason: Rejection reason (required for audit)
        """
        # Find and remove from pending
        claim_data = self._find_and_remove_from_pending(claim_id)
        if not claim_data:
            raise ValueError(f"Claim {claim_id} not found in pending")

        claim = Claim.from_dict(claim_data) if isinstance(claim_data, dict) else claim_data
        claim.status = "rejected"
        claim.curated_at = datetime.now(UTC).replace(tzinfo=None).isoformat()
        claim.curator = curator
        claim.curation_reason = reason or "No reason provided"

        # Write to rejected.md (audit trail)
        self._write_claim(self.rejected_path, claim)

    def _find_and_remove_from_pending(self, claim_id: str) -> Optional[Dict]:
        """
        Find claim in pending.md and remove it.

        Returns:
            Claim data if found, None otherwise
        """
        if not self.pending_path.exists():
            return None

        # Parse pending.md (Markdown format with claim blocks)
        with open(self.pending_path, "r") as f:
            content = f.read()

        # Simple parser: find ## claim_id block
        start = content.find(f"## {claim_id}")
        if start == -1:
            return None

        # Find next ## or end of file
        end = content.find("\n##", start + 1)
        if end == -1:
            end = len(content)

        # Extract claim block
        claim_block = content[start:end]

        # Remove from content
        new_content = content[:start] + content[end:]

        # Write back
        with open(self.pending_path, "w") as f:
            f.write(new_content)

        # Parse claim (simple key-value extraction from Markdown)
        return self._parse_claim_block(claim_block, claim_id)

    def _parse_claim_block(self, block: str, claim_id: str) -> Dict:
        """
        Parse Markdown claim block to dictionary.

        Expected format:
        ## CLAIM-ID
        **Author:** value
        **Type:** value
        **Statement:** value
        **Map Hash:** value (optional)
        **Status:** value
        etc.
        """
        data = {"claim_id": claim_id, "map_hash": None}

        for line in block.split("\n"):
            if "**Author:**" in line:
                data["author"] = line.split("**Author:**")[1].strip()
            elif "**Type:**" in line:
                data["type"] = line.split("**Type:**")[1].strip()
            elif "**Statement:**" in line:
                data["statement"] = line.split("**Statement:**")[1].strip()
            elif "**Map Hash:**" in line:
                data["map_hash"] = line.split("**Map Hash:**")[1].strip()
            elif "**Status:**" in line:
                data["status"] = line.split("**Status:**")[1].strip()

        return data

    def _write_claim(self, path: Path, claim: Claim) -> None:
        """Write claim to file"""
        with open(path, "a") as f:
            f.write(f"\n## {claim.claim_id}\n")
            f.write(f"**Author:** {claim.author}\n")
            f.write(f"**Type:** {claim.type}\n")
            f.write(f"**Statement:** {claim.statement}\n")
            if claim.map_hash:
                f.write(f"**Map Hash:** {claim.map_hash}\n")
            f.write(f"**Status:** {claim.status}\n")
            f.write(f"**Curated At:** {claim.curated_at}\n")
            f.write(f"**Curator:** {claim.curator}\n")
            if claim.curation_reason:
                f.write(f"**Reason:** {claim.curation_reason}\n")

    def get_pending_claims(self) -> List[Dict]:
        """Get all pending claims from pending.md"""
        if not self.pending_path.exists():
            return []

        claims = []
        with open(self.pending_path, "r") as f:
            content = f.read()

        # Parse all ## blocks as claims
        blocks = content.split("## ")[1:]  # Skip first empty split
        for block in blocks:
            lines = block.split("\n")
            claim_id = lines[0].strip()
            claim_data = {"claim_id": claim_id}

            for line in lines[1:]:
                if line.startswith("**Author:**"):
                    claim_data["author"] = line.split("**Author:**")[1].strip()
                elif line.startswith("**Type:**"):
                    claim_data["type"] = line.split("**Type:**")[1].strip()
                elif line.startswith("**Statement:**"):
                    claim_data["statement"] = line.split("**Statement:**")[1].strip()

            if claim_data:
                claims.append(claim_data)

        return claims

    def get_accepted_claims(self) -> List[Dict]:
        """Get all accepted claims"""
        if not self.accepted_path.exists():
            return []
        # Similar to get_pending_claims
        return self._read_claims_from_file(self.accepted_path)

    def get_rejected_claims(self) -> List[Dict]:
        """Get all rejected claims (audit trail)"""
        if not self.rejected_path.exists():
            return []
        return self._read_claims_from_file(self.rejected_path)

    def _read_claims_from_file(self, path: Path) -> List[Dict]:
        """Helper to read all claims from a file"""
        if not path.exists():
            return []

        claims = []
        with open(path, "r") as f:
            content = f.read()

        blocks = content.split("## ")[1:]
        for block in blocks:
            lines = block.split("\n")
            claim_id = lines[0].strip()
            claim_data = {"claim_id": claim_id, "map_hash": None}

            for line in lines[1:]:
                if "**Author:**" in line:
                    claim_data["author"] = line.split("**Author:**")[1].strip()
                elif "**Type:**" in line:
                    claim_data["type"] = line.split("**Type:**")[1].strip()
                elif "**Statement:**" in line:
                    claim_data["statement"] = line.split("**Statement:**")[1].strip()
                elif "**Map Hash:**" in line:
                    claim_data["map_hash"] = line.split("**Map Hash:**")[1].strip()
                elif "**Status:**" in line:
                    claim_data["status"] = line.split("**Status:**")[1].strip()

            if claim_data:
                claims.append(claim_data)

        return claims
