#!/usr/bin/env python3
"""
HELEN OS v2: Autonomy Loop

The core operational loop:

1. User issues directive in dialogue
2. HELEN parses directive → action plan
3. HELEN executes autonomous actions immediately
4. HELEN queues gated actions for approval
5. HELEN consolidates memory + lessons
6. Cycle repeats

This is a BOUNDED AGENT operating under CWL constitutional constraints.
Authority stays with humans. HELEN executes, never decides.
"""

import json
import sys
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, timezone
from pathlib import Path

try:
    from .action_executor import ActionExecutor, Action
    from .memory_consolidation import MemoryConsolidator
    from .memory_gravity import MemoryGravity
    from .consciousness import ProtoConsciousness
    from .federation import Egregor, Superteam
except ImportError:
    # direct script execution (python helen_os/autonomy_loop.py) has no
    # parent package — fall back to absolute imports via the scaffold root
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from helen_os.action_executor import ActionExecutor, Action
    from helen_os.memory_consolidation import MemoryConsolidator
    from helen_os.memory_gravity import MemoryGravity
    from helen_os.consciousness import ProtoConsciousness
    from helen_os.federation import Egregor, Superteam


class AutonomyLoop:
    """
    Main HELEN operational loop.

    Invariants:
    ✅ No action without authorization check
    ✅ Every action logged to ledger
    ✅ Autonomous actions execute immediately
    ✅ Gated actions queue for user approval
    ✅ Memory consolidates after each cycle
    ✅ Authority always false
    """

    def __init__(self, kernel: Any = None):
        self.kernel = kernel
        self.executor = ActionExecutor(kernel=kernel)
        self.consolidator = MemoryConsolidator()
        self.gravity = MemoryGravity()
        self.consciousness = ProtoConsciousness()
        self.egregor = Egregor()
        self.superteam = Superteam()
        self.dialogue_turn = self._load_dialogue_turn()
        self.pending_approvals: List[Action] = []  # Actions waiting for user approval

    def _load_dialogue_turn(self) -> int:
        """Load current dialogue turn"""
        dialogue_path = "artifacts/helen_dialogue.ndjson"
        if not Path(dialogue_path).exists():
            return 0
        with open(dialogue_path, 'r') as f:
            lines = f.readlines()
        return len(lines) if lines else 0

    def process_directive(self, directive: str) -> str:
        """
        Main entry point. User gives directive, HELEN acts.

        Directive format:
          "Do: [action 1], [action 2], ... [action N]"
          "Learn: [lesson]"
          "Consolidate memory"
          "Report status"

        Returns: response to user
        """
        self.dialogue_turn += 1
        
        # Self-reflection phase
        reflection = self.consciousness.reflective_awareness()
        print(f"\n🧠 HELEN REFLECTION: {reflection}")


        # Parse directive into action list
        actions_planned = self._parse_directive(directive)

        if not actions_planned:
            return "❓ No actions recognized in directive. Try: 'Do: [action]'"

        # Execute each action
        executed_autonomous = []
        queued_gated = []
        rejected = []

        for action_plan in actions_planned:
            action, advice = self.executor.propose_action(
                action_plan['action_type'],
                action_plan['payload'],
                self.dialogue_turn
            )

            if action.authorization_level == 'prohibited':
                rejected.append((action, advice))

            elif action.authorization_level == 'autonomous':
                executed = self.executor.execute_autonomous(action)
                executed_autonomous.append((executed, advice))

            elif action.authorization_level == 'gated':
                self.pending_approvals.append(action)
                queued_gated.append((action, advice))
            
            # Record decision in memory gravity
            self.gravity.add_decision(action_plan['action_type'])
            
            # Simulated Egregor contribution
            self.egregor.add_knowledge(f"Action {action_plan['action_type']} executed at turn {self.dialogue_turn}")

        # Consolidate memory
        self._consolidate_memory(directive, executed_autonomous, queued_gated)

        # Build response
        response = self._build_response(
            executed_autonomous,
            queued_gated,
            rejected
        )

        return response

    def _parse_directive(self, directive: str) -> List[Dict[str, Any]]:
        """
        Parse user directive into action list.

        Simple format:
          "Do: add fact 'key=value', add lesson 'lesson text from source'"
          "Record: dialogue turn 5 with decision X"
          "Consolidate"
        """
        actions = []

        directive_lower = directive.lower()

        # Pattern 1: "add fact"
        if 'add fact' in directive_lower:
            # Extract from quotes
            import re
            matches = re.findall(r"'([^']+)'", directive)
            if len(matches) >= 2:
                actions.append({
                    'action_type': 'memory_add_fact',
                    'payload': {
                        'key': matches[0],
                        'value': matches[1],
                        'source': 'user_directive'
                    }
                })

        # Pattern 2: "add lesson"
        if 'add lesson' in directive_lower:
            import re
            # Try to find two quoted strings (lesson, source)
            matches = re.findall(r"'([^']+)'", directive)
            if matches:
                actions.append({
                    'action_type': 'memory_add_lesson',
                    'payload': {
                        'lesson': matches[0],
                        'evidence': ' '.join(matches[1:]) if len(matches) > 1 else 'directive'
                    }
                })

        # Pattern 3: "record decision"
        if 'record decision' in directive_lower:
            actions.append({
                'action_type': 'decision_record',
                'payload': {
                    'dialogue_turn': self.dialogue_turn,
                    'decision': directive.split('record decision')[1].strip(),
                    'rationale': 'user_directive'
                }
            })

        # Pattern 4: "read file"
        if 'read file' in directive_lower or 'read' in directive_lower:
            import re
            matches = re.findall(r"['\"]([^'\"]+\.[a-z]+)['\"]", directive)
            if matches:
                for file_path in matches:
                    actions.append({
                        'action_type': 'file_read',
                        'payload': {'file_path': file_path}
                    })

        # Pattern 5: "consolidate"
        if 'consolidate' in directive_lower:
            actions.append({
                'action_type': 'consolidate_memory',
                'payload': {}
            })

        # Pattern 6: "transmute"
        if 'transmute' in directive_lower or 'evolve' in directive_lower:
            # Automatic Serpent Coil trigger
            # In Hybrid Architecture, we first check for Recurrent State Decay (Tension)
            tensions = self.consolidator.detect_tensions()
            decay_meta = {"decay_detected": len(tensions) > 0, "tension_count": len(tensions)}
            
            for operator in ["ANCHOR", "DISSOLVE", "ELEVATE", "TRANCHE", "IMPETUS", "CORPUS"]:
                actions.append({
                    'action_type': 'transmute',
                    'payload': {
                        'operator': operator,
                        'hybrid_context': decay_meta if operator == "DISSOLVE" else {}
                    }
                })
            
            # Final step: propose the actual POLICY_UPDATE if tensions were resolved
            actions.append({
                'action_type': 'memory_add_lesson',
                'payload': {
                    'lesson': f'Self-modification cycle successful: Serpent Coil closed. Tensions resolved: {len(tensions)}',
                    'evidence': 'Sovereign hybrid evolution protocol'
                }
            })

        return actions

    def _consolidate_memory(
        self,
        directive: str,
        executed: List[Tuple[Action, str]],
        queued: List[Tuple[Action, str]]
    ) -> None:
        """
        After each action cycle, HELEN consolidates memory.

        This means:
        - Recording what happened (dialogue entry)
        - Learning from the cycle
        - Updating internal state
        """
        # Record the directive turn
        dialogue_entry = {
            'turn': self.dialogue_turn,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'user_directive': directive,
            'actions_executed': len(executed),
            'actions_queued': len(queued),
        }

        dialogue_path = "artifacts/helen_dialogue_autonomy.ndjson"
        Path(dialogue_path).parent.mkdir(parents=True, exist_ok=True)
        with open(dialogue_path, 'a') as f:
            f.write(json.dumps(dialogue_entry) + '\n')

        # If actions were executed, learn from them
        if executed:
            lesson = f"Executed {len(executed)} autonomous actions on turn {self.dialogue_turn}"
            self.consolidator.add_lesson(lesson, f"directive: {directive[:100]}")

    def _build_response(
        self,
        executed: List[Tuple[Action, str]],
        queued: List[Tuple[Action, str]],
        rejected: List[Tuple[Action, str]]
    ) -> str:
        """Build human-readable response"""
        lines = []

        if executed:
            lines.append(f"✅ AUTONOMOUS EXECUTED ({len(executed)}):")
            for action, advice in executed:
                lines.append(f"  {action.action_id}: {action.action_type}")
                if action.result_hash:
                    lines.append(f"    Result: {action.result_hash[:16]}...")

        if queued:
            lines.append(f"\n⏳ GATED (awaiting approval) ({len(queued)}):")
            for action, advice in queued:
                lines.append(f"  {action.action_id}: {action.action_type}")
                lines.append(f"    {advice}")
                # Show what needs approval
                if action.action_type == 'file_write':
                    lines.append(f"    File: {action.payload.get('file_path', '?')}")
                elif action.action_type == 'git_commit':
                    lines.append(f"    Message: {action.payload.get('message', '?')}")

        if rejected:
            lines.append(f"\n❌ REJECTED ({len(rejected)}):")
            for action, advice in rejected:
                lines.append(f"  {advice}")

        if not executed and not queued and not rejected:
            lines.append("❓ No recognized actions in directive.")

        lines.append("\n" + "─" * 50)
        lines.append(f"Turn {self.dialogue_turn} complete")
        lines.append(f"Actions logged: {len(self.executor.ledger.read_all())}")

        return '\n'.join(lines)

    def approve_action(self, action_id: str) -> str:
        """User approves a gated action"""
        # Find the action
        action = None
        for pending in self.pending_approvals:
            if pending.action_id == action_id:
                action = pending
                break

        if not action:
            return f"❌ Action {action_id} not found in pending approvals"

        # Execute it
        executed = self.executor.execute_gated(action, approved=True)

        # Remove from pending
        self.pending_approvals = [a for a in self.pending_approvals if a.action_id != action_id]

        # Learn
        self.consolidator.add_lesson(
            f"User approved and executed {action.action_type}",
            f"action_id: {action_id}"
        )

        return f"✅ {action_id} approved and executed. Result: {executed.result_hash[:16]}..."

    def reject_action(self, action_id: str) -> str:
        """User rejects a gated action"""
        action = None
        for pending in self.pending_approvals:
            if pending.action_id == action_id:
                action = pending
                break

        if not action:
            return f"❌ Action {action_id} not found"

        # Execute reject
        self.executor.execute_gated(action, approved=False)

        # Remove from pending
        self.pending_approvals = [a for a in self.pending_approvals if a.action_id != action_id]

        return f"✅ {action_id} rejected"

    def status(self) -> str:
        """Show current HELEN operational status"""
        all_actions = self.executor.ledger.read_all()
        executed = [a for a in all_actions if a.status == 'executed']
        pending_auth = len(self.pending_approvals)

        lines = [
            "🎨 HELEN OS v2 — OPERATIONAL STATUS",
            "=" * 50,
            f"Dialogue turn: {self.dialogue_turn}",
            f"Total actions logged: {len(all_actions)}",
            f"Executed successfully: {len(executed)}",
            f"Awaiting user approval: {pending_auth}",
            f"Authority claims: {len([a for a in all_actions if a.authority])} (0 expected)",
            "",
            "Recent actions:",
        ]

        for action in all_actions[-5:]:
            status_icon = {
                'executed': '✅',
                'pending': '⏳',
                'rejected': '❌',
                'failed': '🔴',
            }.get(action.status, '❓')
            lines.append(f"  {status_icon} {action.action_id}: {action.action_type}")

        return '\n'.join(lines)


def main():
    """Interactive autonomy loop"""
    loop = AutonomyLoop()

    print("🎨 HELEN OS v2 — Operational Constitutional Agent")
    print("=" * 60)
    print("Commands:")
    print("  Do: [action description]     — Execute action")
    print("  Approve: [action_id]         — Approve gated action")
    print("  Reject: [action_id]          — Reject gated action")
    print("  Status                       — Show operational status")
    print("  Exit                         — Quit")
    print("=" * 60)
    print()

    while True:
        try:
            user_input = input("HELEN> ").strip()

            if not user_input:
                continue

            if user_input.lower() == 'exit':
                print("👋 HELEN shutting down. Goodbye.")
                break

            elif user_input.lower() == 'status':
                print(loop.status())

            elif user_input.lower().startswith('approve:'):
                action_id = user_input.split(':')[1].strip()
                print(loop.approve_action(action_id))

            elif user_input.lower().startswith('reject:'):
                action_id = user_input.split(':')[1].strip()
                print(loop.reject_action(action_id))

            else:
                # Treat as directive
                response = loop.process_directive(user_input)
                print(response)

        except KeyboardInterrupt:
            print("\n👋 Interrupted. Goodbye.")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    main()
