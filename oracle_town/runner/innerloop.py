#!/usr/bin/env python3
"""
ORACLE Inner-Loop Runner: Claude-as-Creative-Town, Local ORACLE as Kernel

Architecture:
- Claude = Creative Town (CT): proposes changes, drafts bundles (NO authority)
- Local codebase = Mayor/Intake/Ledger/Registry/Factory: enforcement + receipts + verdicts

This script orchestrates the recursive loop while maintaining ORACLE invariants.
"""

import json
import hashlib
import yaml
import argparse
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, UTC

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from oracle_town.core.mayor_rsm import MayorRSM, DecisionRecord
from oracle_town.core.policy import Policy
from oracle_town.core.intake_guard import IntakeGuard
from oracle_town.core.schema_validation import validate_schema
from oracle_town.core.ledger import Ledger


@dataclass
class CycleSnapshot:
    """Immutable snapshot of workspace state at cycle start"""
    cycle_id: str
    snapshot_hash: str
    timestamp: str
    repo_files: Dict[str, str]  # path -> content_hash
    git_commit: Optional[str]


@dataclass
class CTContext:
    """Context provided to Creative Town (Claude) - ledger-derived facts only"""
    cycle_id: str
    repo_map: Dict[str, str]  # path -> short summary
    last_decisions: List[Dict[str, Any]]  # Last N decision_record.json
    ledger_summary: Dict[str, int]  # Counts only
    policy_hash: str
    registry_hash: str
    missing_obligations: List[str]
    blocking_reason_frequencies: Dict[str, int]


@dataclass
class ProposalBundle:
    """CT output (untrusted until validated)"""
    proposal_id: str
    cycle_id: str
    proposal_type: str  # "feature", "fix", "refactor", etc.
    description: str
    obligations_claimed: List[str]
    artifacts: List[Dict[str, Any]]  # Files, patches, etc.


@dataclass
class CycleReport:
    """Report for one cycle (append to logs)"""
    cycle_id: str
    timestamp: str
    snapshot_hash: str
    ct_proposal: Optional[ProposalBundle]
    supervisor_pass: bool
    intake_pass: bool
    factory_receipts: List[Dict[str, Any]]
    mayor_decision: Optional[DecisionRecord]
    reflection_input: Dict[str, Any]
    cycle_duration_seconds: float


class WorkspaceSnapshot:
    """Compute snapshot hash of workspace state"""

    def __init__(self, repo_root: Path, allowed_paths: List[str]):
        self.repo_root = repo_root
        self.allowed_paths = allowed_paths

    def capture(self) -> CycleSnapshot:
        """Capture current workspace state"""
        cycle_id = f"CYCLE-{datetime.now(UTC).replace(tzinfo=None).strftime('%Y%m%d-%H%M%S-%f')}"

        # Hash all allowed files
        file_hashes = {}
        for path_pattern in self.allowed_paths:
            for file_path in self.repo_root.glob(path_pattern):
                if file_path.is_file():
                    with open(file_path, 'rb') as f:
                        content_hash = hashlib.sha256(f.read()).hexdigest()
                        rel_path = str(file_path.relative_to(self.repo_root))
                        file_hashes[rel_path] = content_hash

        # Compute overall snapshot hash
        snapshot_data = json.dumps(file_hashes, sort_keys=True)
        snapshot_hash = hashlib.sha256(snapshot_data.encode()).hexdigest()

        return CycleSnapshot(
            cycle_id=cycle_id,
            snapshot_hash=f"sha256:{snapshot_hash}",
            timestamp=datetime.now(UTC).replace(tzinfo=None).isoformat(),
            repo_files=file_hashes,
            git_commit=self._get_git_commit()
        )

    def _get_git_commit(self) -> Optional[str]:
        """Get current git commit hash if available"""
        try:
            import subprocess
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                cwd=self.repo_root,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None


class Supervisor:
    """Pre-Intake sanitization (deterministic, local)"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config['supervisor']
        self.forbidden_keywords = self.config['forbidden_keywords']
        self.forbidden_fields = self.config['forbidden_fields']

    def sanitize(self, proposal_bundle: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Returns: (passed, violations)

        Checks:
        1. NFKC normalization
        2. Forbidden lexicon scan
        3. Forbidden fields (K0 invariant)
        4. Authority leakage patterns
        """
        violations = []

        # Check forbidden fields (recursive)
        forbidden_found = self._check_forbidden_fields(proposal_bundle)
        if forbidden_found:
            violations.extend([f"Forbidden field: {f}" for f in forbidden_found])

        # Check forbidden keywords in text fields
        text_content = json.dumps(proposal_bundle).lower()
        for keyword in self.forbidden_keywords:
            if keyword.lower() in text_content:
                violations.append(f"Forbidden keyword: '{keyword}'")

        # Unicode normalization check
        if self.config.get('nfkc_normalize', True):
            # Check if content is NFKC normalized
            original = json.dumps(proposal_bundle, sort_keys=True)
            import unicodedata
            normalized = unicodedata.normalize('NFKC', original)
            if original != normalized:
                violations.append("Content not NFKC normalized")

        return (len(violations) == 0, violations)

    def _check_forbidden_fields(self, obj: Any, path: str = "") -> List[str]:
        """Recursively check for forbidden fields"""
        forbidden_found = []

        if isinstance(obj, dict):
            for key, value in obj.items():
                current_path = f"{path}.{key}" if path else key
                if key in self.forbidden_fields:
                    forbidden_found.append(current_path)
                # Recurse
                forbidden_found.extend(self._check_forbidden_fields(value, current_path))
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                current_path = f"{path}[{i}]"
                forbidden_found.extend(self._check_forbidden_fields(item, current_path))

        return forbidden_found


class FactoryRunner:
    """Execute receipt plugins and emit attestations"""

    def __init__(self, config: Dict[str, Any], repo_root: Path):
        self.config = config['factory']
        self.repo_root = repo_root
        self.plugins_dir = repo_root / "oracle_town" / "runner" / "factory" / "receipts"

    def execute_receipts(
        self,
        proposal: ProposalBundle,
        staging_dir: Path
    ) -> List[Dict[str, Any]]:
        """
        Execute all enabled receipt plugins.

        Returns: List of attestations (unsigned - Factory must sign)
        """
        attestations = []

        for receipt_type in self.config['enabled_receipts']:
            plugin_path = self.plugins_dir / f"{receipt_type}.py"

            if not plugin_path.exists():
                print(f"⚠️  Receipt plugin not found: {receipt_type}")
                continue

            # Execute plugin (imports the module dynamically)
            try:
                attestation = self._run_plugin(plugin_path, proposal, staging_dir)
                if attestation:
                    attestations.append(attestation)
            except Exception as e:
                print(f"❌ Receipt plugin '{receipt_type}' failed: {e}")

        return attestations

    def _run_plugin(
        self,
        plugin_path: Path,
        proposal: ProposalBundle,
        staging_dir: Path
    ) -> Optional[Dict[str, Any]]:
        """Run a single receipt plugin"""
        # Import plugin module
        import importlib.util
        spec = importlib.util.spec_from_file_location("receipt_plugin", plugin_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Call generate_receipt function
        if hasattr(module, 'generate_receipt'):
            return module.generate_receipt(
                proposal=asdict(proposal),
                staging_dir=str(staging_dir),
                repo_root=str(self.repo_root)
            )
        else:
            raise ValueError(f"Plugin {plugin_path} missing generate_receipt()")


class IdeaTracker:
    """Track idea lifecycle across cycles (ideas.jsonl)"""

    def __init__(self, ideas_path: Path):
        self.ideas_path = ideas_path
        self.ideas_path.parent.mkdir(parents=True, exist_ok=True)

    def track_idea(
        self,
        cycle_id: str,
        proposal: ProposalBundle,
        decision: DecisionRecord,
        receipts_gained: int
    ):
        """Append idea lifecycle event"""
        idea_event = {
            "timestamp": datetime.now(UTC).replace(tzinfo=None).isoformat(),
            "cycle_id": cycle_id,
            "idea_id": proposal.proposal_id,
            "proposal_digest": self._hash_proposal(proposal),
            "decision": decision.decision,
            "blocking_reasons": decision.blocking_reasons,
            "receipts_gained": receipts_gained,
            "receipt_status": len(decision.blocking_reasons) == 0,
        }

        with open(self.ideas_path, 'a') as f:
            f.write(json.dumps(idea_event, sort_keys=True) + '\n')

    def _hash_proposal(self, proposal: ProposalBundle) -> str:
        """Compute stable hash of proposal"""
        data = json.dumps(asdict(proposal), sort_keys=True)
        return hashlib.sha256(data.encode()).hexdigest()


class InnerLoopRunner:
    """Main orchestrator for the recursive loop"""

    def __init__(self, config_path: Path, repo_root: Path):
        self.repo_root = repo_root

        # Load config
        with open(config_path) as f:
            self.config = yaml.safe_load(f)

        # Initialize components
        self.snapshot_engine = WorkspaceSnapshot(
            repo_root,
            self.config['runner']['allowed_read_paths']
        )
        self.supervisor = Supervisor(self.config)
        self.factory = FactoryRunner(self.config, repo_root)
        self.idea_tracker = IdeaTracker(
            repo_root / self.config['ideas']['ideas_stream']
        )

        # Paths
        self.staging_dir = repo_root / self.config['runner']['staging_dir']
        self.state_dir = repo_root / self.config['runner']['state_dir']
        self.logs_dir = repo_root / self.config['runner']['logs_dir']

        # Create directories
        self.staging_dir.mkdir(parents=True, exist_ok=True)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        # Load Mayor components
        policy_path = repo_root / self.config['mayor']['policy_path']
        registry_path = repo_root / self.config['mayor']['registry_path']

        with open(policy_path) as f:
            self.policy = Policy.from_dict(json.load(f))

        self.mayor = MayorRSM(public_keys_path=str(registry_path))
        self.intake_guard = IntakeGuard()

    def run_cycle(self, cycle_num: int, idea_prompt: Optional[str] = None) -> CycleReport:
        """Execute one cycle of the inner loop"""
        print(f"\n{'='*70}")
        print(f"CYCLE {cycle_num}")
        print(f"{'='*70}")

        start_time = datetime.now(UTC).replace(tzinfo=None)

        # 1. Snapshot workspace
        snapshot = self.snapshot_engine.capture()
        print(f"📸 Snapshot: {snapshot.snapshot_hash[:16]}...")

        # 2. Assemble CT context
        ct_context = self._assemble_ct_context(snapshot)

        # 3. Call Creative Town (Claude) - proposal-only
        print(f"🎨 Calling Creative Town...")
        ct_proposal = self._call_creative_town(ct_context, idea_prompt)

        if not ct_proposal:
            print("❌ CT produced no proposal")
            return self._make_empty_report(snapshot, start_time)

        print(f"📝 Proposal ID: {ct_proposal.proposal_id}")

        # 4. Supervisor pre-pass
        print(f"🔍 Supervisor sanitization...")
        supervisor_pass, violations = self.supervisor.sanitize(asdict(ct_proposal))

        if not supervisor_pass:
            print(f"❌ Supervisor REJECTED:")
            for v in violations:
                print(f"   - {v}")
            return self._make_report(snapshot, ct_proposal, supervisor_pass, False, [], None, start_time)

        print(f"✅ Supervisor PASS")

        # 5. Intake validation
        print(f"🚪 Intake validation...")
        intake_pass = self._validate_intake(ct_proposal)

        if not intake_pass:
            print(f"❌ Intake REJECTED")
            return self._make_report(snapshot, ct_proposal, supervisor_pass, False, [], None, start_time)

        print(f"✅ Intake PASS")

        # 6. Factory executes receipts
        print(f"🏭 Factory executing receipts...")
        attestations = self.factory.execute_receipts(ct_proposal, self.staging_dir)
        print(f"📋 Generated {len(attestations)} attestations")

        # 7. Append to ledger
        ledger = self._build_ledger(ct_proposal, attestations)

        # 8. Mayor evaluates
        print(f"⚖️  Mayor evaluation...")
        briefcase = self._build_briefcase(ct_proposal)
        decision = self.mayor.decide(self.policy, briefcase, ledger)

        print(f"🏛️  Decision: {decision.decision}")
        if decision.blocking_reasons:
            print(f"🚫 Blocking reasons:")
            for reason in decision.blocking_reasons:
                print(f"   - {reason}")

        # 9. Track idea
        self.idea_tracker.track_idea(
            snapshot.cycle_id,
            ct_proposal,
            decision,
            len(attestations)
        )

        # 10. Reflection input (ledger-derived only)
        reflection_input = self._build_reflection_input(decision, ledger)

        end_time = datetime.now(UTC).replace(tzinfo=None)
        duration = (end_time - start_time).total_seconds()

        report = CycleReport(
            cycle_id=snapshot.cycle_id,
            timestamp=snapshot.timestamp,
            snapshot_hash=snapshot.snapshot_hash,
            ct_proposal=ct_proposal,
            supervisor_pass=supervisor_pass,
            intake_pass=intake_pass,
            factory_receipts=attestations,
            mayor_decision=decision,
            reflection_input=reflection_input,
            cycle_duration_seconds=duration
        )

        # Write cycle report
        self._write_cycle_report(report)

        return report

    def _assemble_ct_context(self, snapshot: CycleSnapshot) -> CTContext:
        """Assemble context for Creative Town (facts only)"""
        # Load last N decisions
        last_decisions = self._load_last_decisions(n=self.config['creative_town']['include_last_n_decisions'])

        # Compute ledger summary (counts only)
        ledger_summary = {
            "total_attestations": 0,
            "unique_attestors": 0,
            "obligations_covered": 0,
        }

        # Extract blocking reason frequencies
        blocking_reason_freq = {}
        for decision in last_decisions:
            for reason in decision.get('blocking_reasons', []):
                blocking_reason_freq[reason] = blocking_reason_freq.get(reason, 0) + 1

        # Build repo map (file summaries)
        repo_map = self._build_repo_map()

        return CTContext(
            cycle_id=snapshot.cycle_id,
            repo_map=repo_map,
            last_decisions=last_decisions,
            ledger_summary=ledger_summary,
            policy_hash=self.policy.policy_hash,
            registry_hash="sha256:TODO",  # TODO: Get from registry
            missing_obligations=[],  # TODO: Compute from last decisions
            blocking_reason_frequencies=blocking_reason_freq
        )

    def _call_creative_town(self, ct_context: CTContext, idea_prompt: Optional[str]) -> Optional[ProposalBundle]:
        """
        Call Claude (Creative Town) with context.

        NOTE: This is a STUB - real implementation would call Claude API with:
        - CT context
        - Tool restrictions (proposal-only)
        - Structured output schema
        """
        print(f"⚠️  CT call is STUB - returning mock proposal")

        # Mock proposal for testing
        return ProposalBundle(
            proposal_id=f"PROP-{ct_context.cycle_id}",
            cycle_id=ct_context.cycle_id,
            proposal_type="feature",
            description=idea_prompt or "Test proposal for inner loop",
            obligations_claimed=["code_review", "unit_tests"],
            artifacts=[]
        )

    def _validate_intake(self, proposal: ProposalBundle) -> bool:
        """Validate proposal through Intake"""
        try:
            # Schema validation
            proposal_dict = asdict(proposal)
            # TODO: Load and validate against proposal_bundle.schema.json

            # IntakeGuard validation
            violations = self.intake_guard.validate(proposal_dict)
            return len(violations) == 0
        except Exception as e:
            print(f"Intake error: {e}")
            return False

    def _build_ledger(self, proposal: ProposalBundle, attestations: List[Dict]) -> Dict:
        """Build ledger structure for Mayor"""
        return {
            "run_id": proposal.cycle_id,
            "attestations": attestations,
            "metadata": {
                "proposal_id": proposal.proposal_id,
                "timestamp": datetime.now(UTC).replace(tzinfo=None).isoformat()
            }
        }

    def _build_briefcase(self, proposal: ProposalBundle) -> Dict:
        """Build briefcase structure for Mayor"""
        return {
            "run_id": proposal.cycle_id,
            "obligations": proposal.obligations_claimed,
            "description": proposal.description,
            "zone_context": "oracle_town"
        }

    def _build_reflection_input(self, decision: DecisionRecord, ledger: Dict) -> Dict:
        """Build reflection input (ledger-derived facts only)"""
        return {
            "decision": decision.decision,
            "blocking_reasons": decision.blocking_reasons,
            "attestation_count": len(ledger.get('attestations', [])),
            "missing_obligations": [],  # TODO: Compute
        }

    def _build_repo_map(self) -> Dict[str, str]:
        """Build repo map (file -> short summary)"""
        # Simplified: just list files
        repo_map = {}
        for path_pattern in self.config['runner']['allowed_read_paths']:
            for file_path in self.repo_root.glob(path_pattern):
                if file_path.is_file():
                    rel_path = str(file_path.relative_to(self.repo_root))
                    repo_map[rel_path] = f"File: {file_path.suffix}"
        return repo_map

    def _load_last_decisions(self, n: int) -> List[Dict]:
        """Load last N decision records"""
        decisions = []
        # Look in logs for recent cycle reports
        if self.logs_dir.exists():
            report_files = sorted(self.logs_dir.glob("cycle_*.json"), reverse=True)
            for report_file in report_files[:n]:
                with open(report_file) as f:
                    report = json.load(f)
                    if 'mayor_decision' in report and report['mayor_decision']:
                        decisions.append(report['mayor_decision'])
        return decisions

    def _write_cycle_report(self, report: CycleReport):
        """Write cycle report to logs"""
        report_file = self.logs_dir / f"cycle_{report.cycle_id}.json"

        # Convert to dict
        report_dict = asdict(report)
        # Convert dataclasses to dicts
        if report.mayor_decision:
            report_dict['mayor_decision'] = asdict(report.mayor_decision)

        with open(report_file, 'w') as f:
            json.dump(report_dict, f, indent=2, sort_keys=True)

    def _make_empty_report(self, snapshot: CycleSnapshot, start_time: datetime) -> CycleReport:
        """Make empty report for failed cycles"""
        end_time = datetime.now(UTC).replace(tzinfo=None)
        return CycleReport(
            cycle_id=snapshot.cycle_id,
            timestamp=snapshot.timestamp,
            snapshot_hash=snapshot.snapshot_hash,
            ct_proposal=None,
            supervisor_pass=False,
            intake_pass=False,
            factory_receipts=[],
            mayor_decision=None,
            reflection_input={},
            cycle_duration_seconds=(end_time - start_time).total_seconds()
        )

    def _make_report(
        self,
        snapshot: CycleSnapshot,
        proposal: Optional[ProposalBundle],
        supervisor_pass: bool,
        intake_pass: bool,
        receipts: List[Dict],
        decision: Optional[DecisionRecord],
        start_time: datetime
    ) -> CycleReport:
        """Make cycle report"""
        end_time = datetime.now(UTC).replace(tzinfo=None)
        return CycleReport(
            cycle_id=snapshot.cycle_id,
            timestamp=snapshot.timestamp,
            snapshot_hash=snapshot.snapshot_hash,
            ct_proposal=proposal,
            supervisor_pass=supervisor_pass,
            intake_pass=intake_pass,
            factory_receipts=receipts,
            mayor_decision=decision,
            reflection_input={},
            cycle_duration_seconds=(end_time - start_time).total_seconds()
        )

    def run_multi_cycle(self, num_cycles: int, idea_prompt: Optional[str] = None):
        """Run multiple cycles"""
        print(f"\n{'='*70}")
        print(f"ORACLE INNER-LOOP RUNNER")
        print(f"Running {num_cycles} cycles")
        print(f"{'='*70}")

        reports = []
        for i in range(num_cycles):
            report = self.run_cycle(i + 1, idea_prompt)
            reports.append(report)

            # Check kill-switch conditions
            if self._should_kill(reports):
                print(f"\n🛑 Kill-switch activated - stopping loop")
                break

        # Summary
        print(f"\n{'='*70}")
        print(f"LOOP SUMMARY")
        print(f"{'='*70}")
        print(f"Total cycles: {len(reports)}")

        decisions = [r.mayor_decision for r in reports if r.mayor_decision]
        ships = sum(1 for d in decisions if d.decision == "SHIP")
        no_ships = len(decisions) - ships

        print(f"SHIP: {ships}")
        print(f"NO_SHIP: {no_ships}")

    def _should_kill(self, reports: List[CycleReport]) -> bool:
        """Check if kill-switch conditions are met"""
        if len(reports) < 5:
            return False

        # Check last N cycles for repeated blocking reasons
        threshold = self.config['runner']['rejection_kill_threshold']
        last_n = reports[-threshold:]

        # Count repeated blocking reasons
        reason_counts = {}
        for report in last_n:
            if report.mayor_decision and report.mayor_decision.blocking_reasons:
                first_reason = report.mayor_decision.blocking_reasons[0]
                reason_counts[first_reason] = reason_counts.get(first_reason, 0) + 1

        # If any reason appears in all last N cycles, kill
        for count in reason_counts.values():
            if count >= threshold:
                return True

        return False


def main():
    parser = argparse.ArgumentParser(
        description="ORACLE Inner-Loop Runner: Claude-as-Creative-Town"
    )
    parser.add_argument(
        '--cycles',
        type=int,
        default=5,
        help="Number of cycles to run (default: 5)"
    )
    parser.add_argument(
        '--idea',
        type=str,
        help="Initial idea prompt for Creative Town"
    )
    parser.add_argument(
        '--config',
        type=str,
        default="oracle_town/runner/config.yaml",
        help="Config file path (default: oracle_town/runner/config.yaml)"
    )
    args = parser.parse_args()

    # Find repo root
    repo_root = Path(__file__).parent.parent.parent
    config_path = repo_root / args.config

    if not config_path.exists():
        print(f"❌ Config not found: {config_path}")
        sys.exit(1)

    # Run loop
    runner = InnerLoopRunner(config_path, repo_root)
    runner.run_multi_cycle(args.cycles, args.idea)


if __name__ == "__main__":
    main()
