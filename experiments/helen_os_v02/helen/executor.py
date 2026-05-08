import subprocess
import shlex
from helen.ids import new_id
from helen.hashing import sha256
from helen.policy import check_action, PolicyViolation


def execute_action(action: dict) -> dict:
    try:
        check_action(action)
        if action["type"] == "NOOP":
            content = {
                "status": "NOOP",
                "reason": action["reason"]
            }
        elif action["type"] == "SHELL":
            result = subprocess.run(
                shlex.split(action["command"]),
                capture_output=True,
                text=True,
                timeout=5
            )
            content = {
                "command": action["command"],
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        else:
            content = {
                "status": "UNKNOWN_ACTION_TYPE",
                "action": action
            }
        return {
            "artifact_id": new_id("ART"),
            "type": "EXECUTION_RESULT",
            "content_hash": sha256(content),
            "content_preview": str(content)[:1000],
            "raw": content
        }
    except PolicyViolation as e:
        content = {
            "status": "DENIED",
            "reason": str(e),
            "action": action
        }
        return {
            "artifact_id": new_id("ART"),
            "type": "POLICY_DENIAL",
            "content_hash": sha256(content),
            "content_preview": str(content)[:1000],
            "raw": content
        }


def execute_proposal(proposal: dict) -> list[dict]:
    return [execute_action(a) for a in proposal["actions"]]
