"""
HELEN Knowledge Sources — corpus boundary registry.

Each source is a separate ingestion surface with its own identity.
Retrieval can filter by source, enabling:
  - "search only my Apple Notes"
  - "search only my plugin corpus"
  - "compare what Notes say vs what plugins say about X"

Sources are not mixed implicitly. Each unit carries its source tag.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class KnowledgeSource:
    id: str
    name: str
    path: str
    description: str
    tag_prefix: str = ""  # auto-added to all units from this source

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "path": self.path,
            "description": self.description,
            "tag_prefix": self.tag_prefix,
        }


# ─── Source Registry ──────────────────────────────────────────────────────────

SOURCES: Dict[str, KnowledgeSource] = {
    "plugins": KnowledgeSource(
        id="plugins",
        name="PLUGINS_JMT",
        path="/Users/jean-marietassy/Desktop/PLUGINS_JMT",
        description="3 years of #plugin notes — AGI, Riemann, LEGORACLE, swarm, consciousness, metaphysics",
        tag_prefix="src_plugins",
    ),
    "apple_notes": KnowledgeSource(
        id="apple_notes",
        name="Apple Notes",
        path="/tmp/helen_notes_export",
        description="1,882 Apple Notes exported via AppleScript — #pluginHELEN, research, daily notes",
        tag_prefix="src_apple_notes",
    ),
    "helen_os": KnowledgeSource(
        id="helen_os",
        name="HELEN OS Codebase",
        path="/Users/jean-marietassy/Documents/GitHub/helen_os_v1",
        description="HELEN OS source — governance, schemas, skills, tools, architecture docs",
        tag_prefix="src_helen_os",
    ),
}


def get_source(source_id: str) -> Optional[KnowledgeSource]:
    return SOURCES.get(source_id)


def list_sources() -> List[KnowledgeSource]:
    return list(SOURCES.values())


def register_source(source: KnowledgeSource):
    SOURCES[source.id] = source
