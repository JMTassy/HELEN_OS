"""find_skills — discovery layer over oracle_town/skills/**/SKILL.md.

Pure stdlib. Parses YAML frontmatter manually (no PyYAML dep).

Commands:
    list                — one line per skill
    search <query>      — substring match on name / description / faculty
    json                — full structured dump

Usage:
    python3 oracle_town/skills/meta/find_skills/find_skills.py list
    python3 oracle_town/skills/meta/find_skills/find_skills.py search video
    python3 oracle_town/skills/meta/find_skills/find_skills.py json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

THIS = Path(__file__).resolve()
REPO_ROOT = THIS.parents[4]
SKILLS_ROOT = REPO_ROOT / "oracle_town" / "skills"


def parse_frontmatter(text: str) -> dict:
    """Extract YAML-style frontmatter between first two --- lines. Handles
    simple `key: value` pairs only (sufficient for our SKILL.md convention)."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    out: dict = {}
    for i in range(1, len(lines)):
        line = lines[i]
        if line.strip() == "---":
            break
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            out[key] = value
    return out


def load_skills() -> list[dict]:
    skills = []
    for skill_md in sorted(SKILLS_ROOT.rglob("SKILL.md")):
        fm = parse_frontmatter(skill_md.read_text())
        rel = skill_md.relative_to(REPO_ROOT)
        skills.append({
            "path": str(rel),
            "dir": str(rel.parent),
            "name": fm.get("name", "[incomplete]"),
            "description": fm.get("description", "[incomplete]"),
            "faculty": fm.get("helen_faculty", ""),
            "status": fm.get("helen_status", ""),
            "prerequisite": fm.get("helen_prerequisite", ""),
            "frontmatter_complete": bool(fm.get("name") and fm.get("description")),
        })
    return skills


def cmd_list(skills: list[dict]) -> None:
    print(f"oracle_town/skills/  —  {len(skills)} skills indexed\n")
    for s in skills:
        marker = " " if s["frontmatter_complete"] else "!"
        faculty = s["faculty"][:20] if s["faculty"] else "—"
        status_short = (s["status"].split()[0] if s["status"] else "—")[:10]
        desc = s["description"][:90] + ("…" if len(s["description"]) > 90 else "")
        print(f" {marker} {faculty:20s}  {status_short:10s}  {s['dir']}")
        print(f"     {desc}")
    incomplete = [s for s in skills if not s["frontmatter_complete"]]
    if incomplete:
        print(f"\n! {len(incomplete)} skill(s) with incomplete frontmatter "
              "(missing name or description)")


def cmd_search(skills: list[dict], query: str) -> None:
    q = query.lower()
    hits = [
        s for s in skills
        if q in s["name"].lower()
        or q in s["description"].lower()
        or q in s["faculty"].lower()
    ]
    if not hits:
        print(f"no match for '{query}'")
        return
    print(f"{len(hits)} match(es) for '{query}':\n")
    for s in hits:
        faculty = s["faculty"][:20] if s["faculty"] else "—"
        desc = s["description"][:120] + ("…" if len(s["description"]) > 120 else "")
        print(f"  {s['name']}  [{faculty}]")
        print(f"    {s['dir']}")
        print(f"    {desc}\n")


def cmd_json(skills: list[dict]) -> None:
    print(json.dumps({
        "schema": "find_skills_v1",
        "skills_root": str(SKILLS_ROOT.relative_to(REPO_ROOT)),
        "n_skills": len(skills),
        "skills": skills,
    }, indent=2))


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print(__doc__, file=sys.stderr)
        return 2
    cmd = args[0]
    skills = load_skills()
    if cmd == "list":
        cmd_list(skills)
    elif cmd == "search":
        if len(args) < 2:
            print("usage: search <query>", file=sys.stderr)
            return 2
        cmd_search(skills, " ".join(args[1:]))
    elif cmd == "json":
        cmd_json(skills)
    else:
        print(f"unknown command: {cmd}", file=sys.stderr)
        print(__doc__, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
