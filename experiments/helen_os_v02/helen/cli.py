import argparse
import json
from pathlib import Path
from helen.kernel import run_intent, load_state
from helen.replay import replay


def init():
    Path("data/receipts").mkdir(parents=True, exist_ok=True)
    Path("data/ledger.ndjson").touch()
    Path("data/state.json").write_text(json.dumps({
        "admitted_receipts": [],
        "last_route": None,
        "last_receipt_id": None,
        "last_proposal_id": None
    }, indent=2))
    Path("policy").mkdir(exist_ok=True)
    if not Path("policy/permissions.json").exists():
        Path("policy/permissions.json").write_text(json.dumps({
            "shell": {
                "allow": ["pwd", "ls", "cat", "head", "tail", "wc", "grep"],
                "deny": ["rm", "sudo", "curl", "wget", "python", "pip", "git", "chmod", "chown", "mv", "cp", "ssh"]
            },
            "network": {"out": "deny"},
            "memory": {"write": "reducer_only"},
            "ship": {"default": "NO_SHIP"}
        }, indent=2))
    print("HELEN OS KERNEL v0.2 initialized.")


def cmd_run(args):
    result = run_intent(args.text, args.effect)
    print(json.dumps(result, indent=2, sort_keys=True))


def cmd_state(args):
    print(json.dumps(load_state(), indent=2, sort_keys=True))


def cmd_replay(args):
    print(json.dumps(replay(), indent=2, sort_keys=True))


def main():
    parser = argparse.ArgumentParser("helen")
    sub = parser.add_subparsers(required=True)

    p = sub.add_parser("init")
    p.set_defaults(func=lambda args: init())

    p = sub.add_parser("run")
    p.add_argument("text")
    p.add_argument("--effect", default="INSPECT")
    p.set_defaults(func=cmd_run)

    p = sub.add_parser("state")
    p.set_defaults(func=cmd_state)

    p = sub.add_parser("replay")
    p.set_defaults(func=cmd_replay)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
