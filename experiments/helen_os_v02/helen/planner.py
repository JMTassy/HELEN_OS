from helen.ids import new_id
from helen.router import route
from helen.schemas import Intent, Proposal


def plan(intent: Intent) -> Proposal:
    r = route(intent)
    if r == "INSPECT":
        actions = [
            {
                "action_id": new_id("A"),
                "type": "SHELL",
                "command": "pwd",
                "reason": "identify current working directory"
            },
            {
                "action_id": new_id("A"),
                "type": "SHELL",
                "command": "ls",
                "reason": "inspect visible files"
            }
        ]
        expected = ["terminal_stdout"]
    elif r == "MEMORY_LOOKUP":
        actions = [
            {
                "action_id": new_id("A"),
                "type": "NOOP",
                "reason": "memory lookup requires reducer-mediated memory module in later version"
            }
        ]
        expected = ["noop_report"]
    elif r == "ORACLE_GATE":
        actions = [
            {
                "action_id": new_id("A"),
                "type": "NOOP",
                "reason": "oracle gate is planned but not enabled in kernel v0.2"
            }
        ]
        expected = ["gate_stub"]
    else:
        actions = [
            {
                "action_id": new_id("A"),
                "type": "NOOP",
                "reason": "think route produces no external side effect"
            }
        ]
        expected = ["thought_stub"]
    return {
        "proposal_id": new_id("P"),
        "intent_id": intent["intent_id"],
        "route": r,
        "authority": "NON_SOVEREIGN",
        "actions": actions,
        "expected_artifacts": expected
    }
