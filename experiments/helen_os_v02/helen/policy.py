import json
import shlex
from pathlib import Path


class PolicyViolation(Exception):
    pass


DEFAULT_POLICY_PATH = Path("policy/permissions.json")


def load_policy(path: Path = DEFAULT_POLICY_PATH) -> dict:
    if not path.exists():
        raise PolicyViolation("missing policy/permissions.json")
    return json.loads(path.read_text())


def check_shell_command(command: str, policy: dict | None = None) -> None:
    policy = policy or load_policy()
    parts = shlex.split(command)
    if not parts:
        raise PolicyViolation("empty shell command")
    cmd = parts[0]
    if cmd in policy["shell"]["deny"]:
        raise PolicyViolation(f"denied shell command: {cmd}")
    if cmd not in policy["shell"]["allow"]:
        raise PolicyViolation(f"shell command not explicitly allowed: {cmd}")


def check_action(action: dict, policy: dict | None = None) -> None:
    policy = policy or load_policy()
    if action["type"] == "SHELL":
        check_shell_command(action["command"], policy)
