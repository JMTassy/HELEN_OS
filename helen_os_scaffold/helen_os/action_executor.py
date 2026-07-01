"""
HELEN Action Executor — CWL-Compliant Autonomous Agent Layer

Core principle: HELEN can act, but ONLY within constitutional bounds.
Every action is:
  ✅ Logged (append-only ledger)
  ✅ Authorized (checked against policy)
  ✅ Reversible (or marked immutable)
  ✅ Auditable (full replay possible)
  ❌ Never authority-claiming
  ❌ Never mutating the sovereign ledger

Authority stays with humans. HELEN is the executor, not the decider.
"""

import json
import hashlib
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import subprocess


@dataclass(frozen=True)
class Action:
    """Immutable action record (matches action.schema.json)"""
    action_id: str
    action_type: str
    timestamp: str
    authority: bool  # Always False
    payload: Dict[str, Any]
    authorization_level: str  # "autonomous", "gated", "prohibited"
    status: str  # "pending", "approved", "executing", "executed", "rejected", "failed"
    parent_dialogue_turn: int
    result_hash: Optional[str] = None
    error: Optional[str] = None
    reversible: bool = True
    undo_instruction: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d['authority'] = False  # ALWAYS False
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), separators=(',', ':'), sort_keys=True)

    def hash(self) -> str:
        return hashlib.sha256(self.to_json().encode()).hexdigest()


class ActionPolicy:
    """Load and enforce action policy"""

    # Anchor to this module, not CWD: from the repo root a CWD-relative
    # "helen_os/action_policy.json" would point into the sovereign tree
    # (where the file does not exist) instead of the scaffold
    DEFAULT_POLICY_PATH = str(Path(__file__).resolve().parent / "action_policy.json")

    def __init__(self, policy_path: str = None, kernel: Any = None):
        policy_path = policy_path or self.DEFAULT_POLICY_PATH
        self.policy_path = policy_path
        self.kernel = kernel
        self._load_fallback_policy()

    def _load_fallback_policy(self):
        with open(self.policy_path, 'r') as f:
            self.fallback_policy = json.load(f)

    @property
    def policy(self) -> Dict[str, Any]:
        """Dynamic policy retrieval: Kernel first, then fallback file."""
        if self.kernel:
            active = self.kernel.get_active_policy()
            if active:
                return active
        return self.fallback_policy

    def is_autonomous(self, action_type: str) -> bool:
        """Can HELEN do this without asking?"""
        for action in self.policy['authorization_matrix']['autonomous_actions']:
            if action['action_type'] == action_type:
                return True
        return False

    def is_gated(self, action_type: str) -> bool:
        """Does this require user approval?"""
        for action in self.policy['authorization_matrix']['gated_actions']:
            if action['action_type'] == action_type:
                return True
        return False

    def is_prohibited(self, action_type: str) -> bool:
        """Is this forbidden?"""
        for action in self.policy['authorization_matrix']['prohibited_actions']:
            if action['action_type'] == action_type:
                return True
        return False

    def get_authorization_level(self, action_type: str) -> str:
        """Return 'autonomous', 'gated', or 'prohibited'"""
        if self.is_autonomous(action_type):
            return 'autonomous'
        elif self.is_gated(action_type):
            return 'gated'
        elif self.is_prohibited(action_type):
            return 'prohibited'
        return 'prohibited'  # default: forbid unknown actions


class ActionLedger:
    """Append-only action log (Channel A adjacent, but non-sovereign)"""

    def __init__(self, ledger_path: str = "artifacts/helen_actions.ndjson"):
        self.ledger_path = ledger_path
        Path(self.ledger_path).parent.mkdir(parents=True, exist_ok=True)

    def append(self, action: Action) -> None:
        """Log action to ledger (append-only, immutable)"""
        with open(self.ledger_path, 'a') as f:
            f.write(action.to_json() + '\n')

    def read_all(self) -> List[Action]:
        """Read entire action ledger"""
        actions = []
        if not os.path.exists(self.ledger_path):
            return actions
        with open(self.ledger_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    actions.append(Action(**json.loads(line)))
        return actions

    def count_session_actions(self, action_type: Optional[str] = None) -> int:
        """Count actions in current session"""
        actions = self.read_all()
        if action_type:
            return sum(1 for a in actions if a.action_type == action_type)
        return len(actions)


class ActionExecutor:
    """
    Execute HELEN actions within CWL constraints.

    The core loop:
    1. Check authorization (policy)
    2. Log to ledger (pre-execution)
    3. Execute (sandboxed)
    4. Log result
    5. Return to user
    """

    def __init__(self, policy_path: str = None, ledger_path: str = None, kernel: Any = None):
        self.kernel = kernel
        self.policy = ActionPolicy(policy_path, kernel=kernel)
        self.ledger = ActionLedger(ledger_path or "artifacts/helen_actions.ndjson")
        self.counter = self._next_action_id()

    def _next_action_id(self) -> int:
        """Get next sequential action_id"""
        actions = self.ledger.read_all()
        if not actions:
            return 1
        # Extract numeric part from "action_NNNN"
        last_id = actions[-1].action_id
        numeric = int(last_id.split('_')[1])
        return numeric + 1

    def propose_action(
        self,
        action_type: str,
        payload: Dict[str, Any],
        dialogue_turn: int
    ) -> Tuple[Action, str]:
        """
        Propose an action. Return (action, advice).
        Advice tells user whether this is autonomous, gated, or prohibited.
        """
        auth_level = self.policy.get_authorization_level(action_type)

        action = Action(
            action_id=f"action_{self.counter:04d}",
            action_type=action_type,
            timestamp=datetime.now(timezone.utc).isoformat(),
            authority=False,  # ALWAYS False
            payload=payload,
            authorization_level=auth_level,
            status='pending',
            parent_dialogue_turn=dialogue_turn,
        )

        if auth_level == 'prohibited':
            advice = f"❌ PROHIBITED. {action_type} violates CWL rules."
            action = Action(**{**asdict(action), 'status': 'rejected'})
            self.ledger.append(action)
            return action, advice

        if auth_level == 'autonomous':
            advice = f"✅ AUTONOMOUS. {action_type} will execute immediately."
            return action, advice

        if auth_level == 'gated':
            advice = f"⏳ GATED. {action_type} requires user approval. Reply: APPROVE or REJECT"
            return action, advice

        return action, "❓ UNKNOWN"

    def execute_autonomous(
        self,
        action: Action,
    ) -> Action:
        """Execute an autonomous action immediately"""
        if action.authorization_level != 'autonomous':
            raise ValueError(f"Action {action.action_id} is not autonomous")

        # Update status
        action = Action(**{**asdict(action), 'status': 'executing'})
        self.ledger.append(action)

        try:
            result = self._execute_payload(action.action_type, action.payload)
            result_hash = hashlib.sha256(
                json.dumps(result, separators=(',', ':'), sort_keys=True).encode()
            ).hexdigest()

            action = Action(**{
                **asdict(action),
                'status': 'executed',
                'result_hash': result_hash,
            })
            self.ledger.append(action)
            self.counter += 1
            return action

        except Exception as e:
            action = Action(**{
                **asdict(action),
                'status': 'failed',
                'error': str(e),
            })
            self.ledger.append(action)
            self.counter += 1
            return action

    def execute_gated(
        self,
        action: Action,
        approved: bool,
    ) -> Action:
        """Execute a gated action if user approves"""
        if action.authorization_level != 'gated':
            raise ValueError(f"Action {action.action_id} is not gated")

        if not approved:
            action = Action(**{**asdict(action), 'status': 'rejected'})
            self.ledger.append(action)
            self.counter += 1
            return action

        # Approved: execute
        action = Action(**{**asdict(action), 'status': 'approved'})
        self.ledger.append(action)

        try:
            result = self._execute_payload(action.action_type, action.payload)
            result_hash = hashlib.sha256(
                json.dumps(result, separators=(',', ':'), sort_keys=True).encode()
            ).hexdigest()

            action = Action(**{
                **asdict(action),
                'status': 'executed',
                'result_hash': result_hash,
            })
            self.ledger.append(action)
            self.counter += 1
            return action

        except Exception as e:
            action = Action(**{
                **asdict(action),
                'status': 'failed',
                'error': str(e),
            })
            self.ledger.append(action)
            self.counter += 1
            return action

    def _execute_payload(self, action_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the actual action. Return result dict."""

        if action_type == 'memory_add_fact':
            return self._action_memory_add_fact(payload)
        elif action_type == 'memory_add_lesson':
            return self._action_memory_add_lesson(payload)
        elif action_type == 'file_read':
            return self._action_file_read(payload)
        elif action_type == 'file_write':
            return self._action_file_write(payload)
        elif action_type == 'dialogue_record':
            return self._action_dialogue_record(payload)
        elif action_type == 'decision_record':
            return self._action_decision_record(payload)
        elif action_type == 'git_commit':
            return self._action_git_commit(payload)
        elif action_type == 'transmute':
            return self._action_transmute(payload)
        else:
            raise ValueError(f"Unknown action_type: {action_type}")

    def _action_transmute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an alchemical transmutation (Sovereign Self-Modification).
        This action can only be proposed by the Serpent loop.
        """
        operator = payload.get("operator")
        if operator not in ["ANCHOR", "DISSOLVE", "ELEVATE", "TRANCHE", "IMPETUS", "CORPUS"]:
            raise ValueError(f"Invalid alchemical operator: {operator}")
        
        # In v3, transmute logs the intent to the action ledger.
        # The actual POLICY_UPDATE receipt is issued in the CORPUS phase.
        return {
            "operator": operator,
            "stage_complete": True,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    def _action_memory_add_fact(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Add a fact to HELEN's memory"""
        key = payload['key']
        value = payload['value']
        source = payload.get('source', 'unknown')

        # Load existing memory
        memory_path = "helen_memory.json"
        if os.path.exists(memory_path):
            with open(memory_path, 'r') as f:
                memory = json.load(f)
        else:
            memory = {'version': 'HELEN_MEM_V0', 'facts': {}}

        # Add fact
        memory['facts'][key] = {
            'value': value,
            'source': source,
            'timestamp': datetime.now(timezone.utc).isoformat(),
        }

        # Save
        with open(memory_path, 'w') as f:
            json.dump(memory, f, indent=2)

        return {'key': key, 'value': value, 'saved': True}

    def _action_memory_add_lesson(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Add a lesson to HELEN's wisdom (append-only, never erased)"""
        lesson = payload['lesson']
        evidence = payload['evidence']

        wisdom_path = "helen_wisdom.ndjson"
        entry = {
            'lesson': lesson,
            'evidence': evidence,
            'timestamp': datetime.now(timezone.utc).isoformat(),
        }

        with open(wisdom_path, 'a') as f:
            f.write(json.dumps(entry) + '\n')

        return {'lesson': lesson, 'appended': True}

    def _action_file_read(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Read a file (sandbox: no secrets)"""
        file_path = payload['file_path']

        # Forbidden paths
        forbidden = ['.env', 'secrets/', 'private/', '.aws/', '.ssh/']
        if any(f in file_path for f in forbidden):
            raise PermissionError(f"Cannot read {file_path} (forbidden)")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"{file_path} not found")

        with open(file_path, 'r') as f:
            content = f.read(5000)  # Max 5KB

        return {
            'file_path': file_path,
            'size': len(content),
            'content_hash': hashlib.sha256(content.encode()).hexdigest(),
        }

    def _action_file_write(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Write a file (gated action)"""
        file_path = payload['file_path']
        content = payload['content']

        # Forbidden paths
        forbidden = ['.env', '.git/', 'secrets/', '/Users/']
        if any(f in file_path for f in forbidden):
            raise PermissionError(f"Cannot write to {file_path} (forbidden)")

        # Create parent directory
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, 'w') as f:
            f.write(content)

        return {
            'file_path': file_path,
            'bytes_written': len(content),
            'hash': hashlib.sha256(content.encode()).hexdigest(),
        }

    def _action_dialogue_record(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Record a dialogue turn to ledger"""
        turn = payload['turn']
        user_input = payload['user_input']
        helen_response = payload['helen_response']

        # Append to dialogue log
        dialogue_path = "artifacts/helen_dialogue.ndjson"
        Path(dialogue_path).parent.mkdir(parents=True, exist_ok=True)

        entry = {
            'turn': turn,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'user': user_input,
            'helen': helen_response,
        }

        with open(dialogue_path, 'a') as f:
            f.write(json.dumps(entry) + '\n')

        return {'turn': turn, 'recorded': True}

    def _action_decision_record(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Record a decision"""
        dialogue_turn = payload['dialogue_turn']
        decision = payload['decision']
        rationale = payload.get('rationale', '')

        decision_path = "artifacts/helen_decisions.ndjson"
        Path(decision_path).parent.mkdir(parents=True, exist_ok=True)

        entry = {
            'dialogue_turn': dialogue_turn,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'decision': decision,
            'rationale': rationale,
        }

        with open(decision_path, 'a') as f:
            f.write(json.dumps(entry) + '\n')

        return {'turn': dialogue_turn, 'decision': decision, 'recorded': True}

    def _action_git_commit(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Propose a git commit (gated action)"""
        message = payload['message']
        files = payload.get('files', [])

        # Validate message
        if 'FORCE' in message or '--hard' in message:
            raise ValueError("Unsafe git operation")

        # In real execution, user would do: git commit -m "message"
        # HELEN only proposes, doesn't execute directly

        return {
            'action': 'git_commit_proposed',
            'message': message,
            'files': files,
            'instruction': f'git add {" ".join(files)} && git commit -m "{message}"'
        }

    def summary(self) -> str:
        """Generate summary of actions taken"""
        actions = self.ledger.read_all()
        executed = [a for a in actions if a.status == 'executed']
        rejected = [a for a in actions if a.status == 'rejected']

        return f"""
HELEN ACTION SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━
Total actions proposed: {len(actions)}
Autonomous executed: {len([a for a in executed if a.authorization_level == 'autonomous'])}
Gated executed: {len([a for a in executed if a.authorization_level == 'gated'])}
Rejected: {len(rejected)}
Failed: {len([a for a in actions if a.status == 'failed'])}

Authority claims: {len([a for a in actions if a.authority])} (should be 0)
Non-reversible: {len([a for a in executed if not a.reversible])}
"""


if __name__ == '__main__':
    # Quick test
    executor = ActionExecutor()

    # Propose an autonomous action
    action, advice = executor.propose_action(
        'memory_add_fact',
        {'key': 'test_fact', 'value': 'HELEN can act', 'source': 'test'},
        dialogue_turn=1
    )
    print(f"Proposed: {advice}")
    print(f"Status: {action.status}")

    # Execute it
    executed = executor.execute_autonomous(action)
    print(f"Executed: {executed.status}")
    print(f"Result hash: {executed.result_hash}")

    # Show summary
    print(executor.summary())
