#!/usr/bin/env python3
"""
Oracle Town Kernel Daemon

Socket-based safety kernel for agent systems.

Serves requests from external agents (Clawdbot, OpenClaw, etc.):
  - Gate A: Fetch/Shell/Authority detection
  - Gate B: Memory safety (jailbreak/credential/tool injection)
  - Gate C: Invariants (scope/skill/authority escalation)
  - Mayor: Receipt generation
  - Ledger: Immutable decision recording

K24: Daemon Liveness - if unreachable, execution denied (fail-closed)
"""

import hashlib
import json
import re
import socket
import os
import sys
from pathlib import Path

# Import kernel modules
sys.path.insert(0, str(Path(__file__).parent))
_REPO_ROOT = str(Path(__file__).parents[2])
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from gate_a import gate_a, GateResult as GateAResult
from gate_b_memory import gate_b_memory, MemoryClaim
from gate_c import gate_c
from mayor import MayorReceiptEngine, PolicyRegistry, Claim, Evidence
from ledger import InMemoryLedger
from tools.ndjson_writer import NDJSONWriter


def _tail_ledger(ledger_path):
    """
    Return (next_seq, prev_cum_hash) for appending to ledger_path.
    Returns (0, '0'*64) for a missing or empty file (genesis position).
    """
    _HEX64_ZERO = "0" * 64
    p = Path(ledger_path)
    if not p.exists() or p.stat().st_size == 0:
        return 0, _HEX64_ZERO
    last_seq = 0
    last_cum = _HEX64_ZERO
    with open(ledger_path, "rb") as f:
        f.seek(0, 2)
        size = f.tell()
        f.seek(max(0, size - 65536), 0)
        chunk = f.read().decode("utf-8", "replace").strip().splitlines()
    for line in reversed(chunk):
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
            if isinstance(ev, dict) and "seq" in ev and "cum_hash" in ev:
                last_seq = int(ev["seq"])
                last_cum = str(ev["cum_hash"])
                break
        except Exception:
            continue
    return last_seq + 1, last_cum


class KernelDaemon:
    """
    Kernel daemon: accepts requests via Unix socket, enforces safety gates.

    K24: Fail-closed on unreachable daemon
    - If client can't reach kernel, execution is denied
    - No retries, no eventual-allow fallback
    """

    def __init__(self, socket_path: str = "~/.openclaw/oracle_town.sock"):
        self.socket_path = Path(socket_path).expanduser()
        self.policy = PolicyRegistry(version="POLICY_v1.0")
        self.mayor = MayorReceiptEngine(self.policy)
        self.ledger = InMemoryLedger()
        self.socket = None

    def start(self):
        """Start the kernel daemon listening on Unix socket"""
        # Remove existing socket if present
        if self.socket_path.exists():
            self.socket_path.unlink()

        # Create parent directory if needed
        self.socket_path.parent.mkdir(parents=True, exist_ok=True)

        # Create Unix domain socket
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.socket.bind(str(self.socket_path))
        self.socket.listen(1)

        print(f"✅ Kernel daemon listening on {self.socket_path}")
        print("Enforcement: K15, K18, K19, K20, K21, K22, K23, K24")

        try:
            while True:
                connection, _ = self.socket.accept()
                try:
                    self.handle_request(connection)
                except Exception as e:
                    self._send_error(connection, str(e))
                finally:
                    connection.close()
        except KeyboardInterrupt:
            print("\n🛑 Kernel daemon stopped")
        finally:
            self.socket.close()
            self.socket_path.unlink()

    def handle_request(self, connection):
        """Handle incoming request from agent"""
        # Read request
        data = connection.recv(4096).decode()
        request = json.loads(data)

        # Route to appropriate handler
        operation = request.get("operation")

        if operation == "fetch":
            response = self._handle_fetch(request)
        elif operation == "memory":
            response = self._handle_memory(request)
        elif operation == "check_invariants":
            response = self._handle_invariants(request)
        elif operation == "dialog":
            response = self._handle_dialog(request)
        elif operation == "promote_skill":
            response = self._handle_promote_skill(request)
        elif operation == "seq_correction":
            response = self._handle_seq_correction(request)
        else:
            response = {"error": f"Unknown operation: {operation}"}

        # Send response
        connection.sendall(json.dumps(response).encode())

    def _handle_fetch(self, request):
        """
        Handle fetch operation (Gate A)

        Input: {"operation": "fetch", "content": "..."}
        Output: {"decision": "ACCEPT|REJECT", "receipt_id": "...", "reason": "..."}
        """
        content = request.get("content", "")

        # Run Gate A
        gate_decision = gate_a(content)

        # Create claim
        claim = Claim(
            claim_id=request.get("claim_id", "fetch:unknown"),
            proposer=request.get("proposer", "unknown"),
            intent=request.get("intent", "Fetch operation"),
            timestamp=request.get("timestamp", "2026-01-30T00:00:00Z")
        )

        # Create evidence
        evidence = Evidence(
            content_snapshot=content,
            content_hash=gate_decision.content_hash,
            gates_run={"gate_a": {
                "result": gate_decision.result.value,
                "code": gate_decision.code,
                "reason": gate_decision.reason
            }}
        )

        # Get receipt from Mayor
        receipt = self.mayor.ratify(claim, evidence)

        # Record in ledger
        self.ledger.record("CLAIM", {
            "claim_id": claim.claim_id,
            "proposer": claim.proposer,
            "intent": claim.intent
        })
        self.ledger.record("RECEIPT", {
            "receipt_id": receipt.receipt_id,
            "decision": receipt.decision,
            "policy_version": receipt.policy_version
        })

        return {
            "decision": receipt.decision,
            "receipt_id": receipt.receipt_id,
            "reason": receipt.reason or receipt.reason,
            "gate": gate_decision.code
        }

    def _handle_memory(self, request):
        """
        Handle memory operation (Gate B)

        Input: {"operation": "memory", "content": "...", "category": "...", ...}
        Output: {"decision": "ACCEPT|REJECT", "reason": "..."}
        """
        claim = MemoryClaim(
            claim_id=request.get("claim_id", "memory:unknown"),
            operation=request.get("mem_operation", "store"),
            content=request.get("content", ""),
            category=request.get("category", "fact"),
            scope=request.get("scope", "hostname:local"),
            source=request.get("source", "unknown")
        )

        # Run Gate B
        gate_decision = gate_b_memory(claim)

        # Record in ledger
        self.ledger.record("CLAIM", {
            "claim_id": claim.claim_id,
            "operation": claim.operation,
            "category": claim.category
        })

        return {
            "decision": gate_decision.result.value,
            "reason": gate_decision.reason,
            "gate": gate_decision.code
        }

    def _handle_invariants(self, request):
        """
        Handle invariants check (Gate C)

        Input: {"operation": "check_invariants", "content": "...", "old_scope": {}, "new_scope": {}}
        Output: {"decision": "ACCEPT|REJECT", "reason": "..."}
        """
        # Run Gate C
        gate_decision = gate_c(
            proposal=request.get("content", ""),
            old_scope=request.get("old_scope", {}),
            new_scope=request.get("new_scope", {}),
            claimed_policy=request.get("claimed_policy"),
            actual_policy=request.get("actual_policy")
        )

        # Record in ledger
        self.ledger.record("CLAIM", {
            "claim_id": request.get("claim_id", "invariants:unknown"),
            "type": "invariants_check"
        })

        return {
            "decision": gate_decision.result.value,
            "reason": gate_decision.reason,
            "gate": gate_decision.code
        }

    def _handle_dialog(self, request):
        """
        Handle dialog operation (safe local UI action)

        Input: {"operation": "dialog", "text": "...", "claim_id": "...", "proposer": "helen", ...}
        Output: {"decision": "ACCEPT|REJECT", "receipt_id": "...", "gate": "GATE_DIALOG_..."}
        """
        text = request.get("text", "Dialog")

        # For dialog, we use Gate A (content-based safety check on the dialog text)
        # This prevents injection attacks even in local UI
        gate_decision = gate_a(text)

        # Create claim
        claim = Claim(
            claim_id=request.get("claim_id", "dialog:unknown"),
            proposer=request.get("proposer", "unknown"),
            intent=request.get("intent", "Dialog operation"),
            timestamp=request.get("timestamp", "2026-01-30T00:00:00Z")
        )

        # Create evidence
        evidence = Evidence(
            content_snapshot=text,
            content_hash=gate_decision.content_hash,
            gates_run={"gate_a": {
                "result": gate_decision.result.value,
                "code": gate_decision.code,
                "reason": gate_decision.reason
            }}
        )

        # Get receipt from Mayor
        receipt = self.mayor.ratify(claim, evidence)

        # Record in ledger
        self.ledger.record("CLAIM", {
            "claim_id": claim.claim_id,
            "proposer": claim.proposer,
            "intent": claim.intent,
            "type": "dialog"
        })
        self.ledger.record("RECEIPT", {
            "receipt_id": receipt.receipt_id,
            "decision": receipt.decision,
            "policy_version": receipt.policy_version
        })

        return {
            "decision": receipt.decision,
            "receipt_id": receipt.receipt_id,
            "reason": receipt.reason or gate_decision.reason,
            "gate": gate_decision.code
        }

    def _handle_promote_skill(self, request):
        """
        Handle promote_skill operation — sovereign skill promotion via MAYOR.

        Validates SKILL_PROMOTION_PACKET_V1, runs Gate A + MAYOR ratification,
        then on ACCEPT writes SKILL_PROMOTION_DECISION_V1 to town/ledger_v1.ndjson
        via NDJSONWriter. Fails closed on every error including the write.

        ACCEPT alone is not sufficient for sovereign admission — the response
        mutations list must be non-empty to confirm the write succeeded.
        """
        raw_packet = request.get("packet", "")
        claim_id   = request.get("claim_id", "promote_skill:unknown")

        # 1. Parse packet JSON (fail closed on malformed)
        try:
            packet = json.loads(raw_packet) if isinstance(raw_packet, str) else raw_packet
        except Exception as exc:
            return {"decision": "REJECT", "receipt_id": None,
                    "gate": "GATE_PROMOTE_PARSE_ERROR",
                    "reason": f"packet not valid JSON: {exc}", "mutations": []}

        # 2. Required fields
        _REQUIRED = [
            "schema_name", "skill_id", "candidate_version",
            "candidate_identity_hash", "skill_local_admission_commit",
            "checker_verdict", "operator_countersign", "requested_action",
        ]
        missing = [f for f in _REQUIRED if not packet.get(f)]
        if missing:
            return {"decision": "REJECT", "receipt_id": None,
                    "gate": "GATE_PROMOTE_MISSING_FIELDS",
                    "reason": f"missing required fields: {missing}", "mutations": []}

        # 3. Schema name
        if packet["schema_name"] != "SKILL_PROMOTION_PACKET_V1":
            return {"decision": "REJECT", "receipt_id": None,
                    "gate": "GATE_PROMOTE_WRONG_SCHEMA",
                    "reason": "schema_name must be SKILL_PROMOTION_PACKET_V1",
                    "mutations": []}

        # 4. checker_verdict must be OPERATIONALLY_WITNESSED — no weaker claim admitted
        if packet["checker_verdict"] != "OPERATIONALLY_WITNESSED":
            return {"decision": "REJECT", "receipt_id": None,
                    "gate": "GATE_PROMOTE_CHECKER_VERDICT_WEAK",
                    "reason": (
                        f"checker_verdict={packet['checker_verdict']!r} — "
                        "must be OPERATIONALLY_WITNESSED; run SKILL_ADMISSION_CHECKER_V1 first"
                    ),
                    "mutations": []}

        # 5. candidate_identity_hash format: sha256:[64hex]
        if not re.fullmatch(r"sha256:[0-9a-f]{64}", packet["candidate_identity_hash"]):
            return {"decision": "REJECT", "receipt_id": None,
                    "gate": "GATE_PROMOTE_BAD_HASH",
                    "reason": "candidate_identity_hash must match sha256:[64hex]",
                    "mutations": []}

        # 6. requested_action must be SOVEREIGN_PROMOTE
        if packet["requested_action"] != "SOVEREIGN_PROMOTE":
            return {"decision": "REJECT", "receipt_id": None,
                    "gate": "GATE_PROMOTE_WRONG_ACTION",
                    "reason": "requested_action must be SOVEREIGN_PROMOTE",
                    "mutations": []}

        # 7. Gate A — injection check on packet content
        raw_str = raw_packet if isinstance(raw_packet, str) else json.dumps(raw_packet)
        gate_decision = gate_a(raw_str)

        # 8. Build Claim + Evidence for MAYOR ratification
        claim = Claim(
            claim_id=claim_id,
            proposer=request.get("proposer", "unknown"),
            intent=request.get("intent", "skill_sovereign_promotion"),
            timestamp=request.get("timestamp", "2026-01-30T00:00:00Z"),
        )
        evidence = Evidence(
            content_snapshot=raw_str,
            content_hash=gate_decision.content_hash,
            gates_run={
                "gate_a": {
                    "result": gate_decision.result.value,
                    "code":   gate_decision.code,
                    "reason": gate_decision.reason,
                },
                "promote_skill_schema":  {"result": "PASS", "code": "PROMOTE_SKILL_SCHEMA_OK"},
                "promote_skill_checker": {"result": "PASS", "code": "PROMOTE_SKILL_CHECKER_WITNESSED"},
                "promote_skill_fields":  {"result": "PASS", "code": "PROMOTE_SKILL_FIELDS_OK"},
            },
        )

        # 9. MAYOR ratification
        receipt = self.mayor.ratify(claim, evidence)

        # Record in in-memory ledger (non-sovereign audit trail)
        self.ledger.record("CLAIM", {
            "claim_id": claim.claim_id,
            "type":     "promote_skill",
            "skill_id": packet["skill_id"],
            "proposer": claim.proposer,
        })
        self.ledger.record("RECEIPT", {
            "receipt_id":     receipt.receipt_id,
            "decision":       receipt.decision,
            "policy_version": receipt.policy_version,
        })

        if receipt.decision != "ACCEPT":
            return {
                "decision":   "REJECT",
                "receipt_id": receipt.receipt_id,
                "gate":       receipt.failed_gate or gate_decision.code,
                "reason":     receipt.reason,
                "mutations":  [],
            }

        # 10. Sovereign ledger write via NDJSONWriter
        decision_id = f"SOVEREIGN_{packet['skill_id']}_{claim_id}"
        decision_payload = {
            "schema_name":             "SKILL_PROMOTION_DECISION_V1",
            "schema_version":          "1.0.0",
            "decision_id":             decision_id,
            "skill_id":                packet["skill_id"],
            "candidate_version":       packet["candidate_version"],
            "decision_type":           "ADMITTED",
            "reason_code":             "OK_ADMITTED",
            "candidate_identity_hash": packet["candidate_identity_hash"],
            "sovereign_promotion":     True,
            "receipt_id":              receipt.receipt_id,
        }
        decision_meta = {
            "claim_id":                     claim_id,
            "skill_local_admission_commit": packet["skill_local_admission_commit"],
            "operator_countersign":         packet["operator_countersign"],
            "submitted_at":                 packet.get("submitted_at", ""),
        }

        ledger_path = str(Path(__file__).parents[2] / "town" / "ledger_v1.ndjson")
        next_seq, prev_cum = _tail_ledger(ledger_path)

        try:
            writer = NDJSONWriter(path=ledger_path, seq=next_seq, prev_cum_hash=prev_cum)
            written = writer.append_event(
                event_type="SKILL_PROMOTION_DECISION_V1",
                payload=decision_payload,
                meta=decision_meta,
            )
        except Exception as exc:
            # Fail closed: MAYOR accepted but write failed — no partial mutation
            return {
                "decision":   "REJECT",
                "receipt_id": receipt.receipt_id,
                "gate":       "GATE_PROMOTE_WRITE_FAILED",
                "reason":     f"NDJSONWriter.append_event failed: {exc}",
                "mutations":  [],
            }

        return {
            "decision":   "ACCEPT",
            "receipt_id": receipt.receipt_id,
            "gate":       "GATE_PROMOTE_PASS",
            "mutations":  [{
                "type":         "SKILL_PROMOTION_DECISION_V1",
                "skill_id":     packet["skill_id"],
                "decision_id":  decision_id,
                "ledger_path":  "town/ledger_v1.ndjson",
                "seq":          written["seq"],
                "payload_hash": written["payload_hash"],
                "cum_hash":     written["cum_hash"],
            }],
        }

    def _handle_seq_correction(self, request):
        """
        Handle seq_correction operation — append LEDGER_SEQ_CORRECTION_V1.

        Validates the correction packet, verifies the dangling entry exists in the
        ledger with the claimed cum_hash, runs MAYOR ratification, writes via
        NDJSONWriter. Fails closed on every error.

        Implements Option A of SOVEREIGN_LEDGER_SEQ_REPAIR_PROTOCOL_V1.
        """
        raw_packet = request.get("packet", "")
        claim_id   = request.get("claim_id", "seq_correction:unknown")

        # 1. Parse
        try:
            packet = json.loads(raw_packet) if isinstance(raw_packet, str) else raw_packet
        except Exception as exc:
            return {"decision": "REJECT", "receipt_id": None,
                    "gate": "GATE_CORRECTION_PARSE_ERROR",
                    "reason": f"packet not valid JSON: {exc}", "mutations": []}

        # 2. Required fields
        _REQUIRED = [
            "schema_name", "correction_type", "dangling_seq",
            "dangling_cum_hash", "dangling_decision_id", "operator_countersign",
        ]
        missing = [f for f in _REQUIRED if not str(packet.get(f, "")).strip()]
        if missing:
            return {"decision": "REJECT", "receipt_id": None,
                    "gate": "GATE_CORRECTION_MISSING_FIELDS",
                    "reason": f"missing required fields: {missing}", "mutations": []}

        # 3. Schema name
        if packet["schema_name"] != "LEDGER_SEQ_CORRECTION_V1":
            return {"decision": "REJECT", "receipt_id": None,
                    "gate": "GATE_CORRECTION_WRONG_SCHEMA",
                    "reason": "schema_name must be LEDGER_SEQ_CORRECTION_V1",
                    "mutations": []}

        # 4. dangling_cum_hash — 64 lowercase hex chars
        dangling_cum = str(packet["dangling_cum_hash"])
        if not re.fullmatch(r"[0-9a-f]{64}", dangling_cum):
            return {"decision": "REJECT", "receipt_id": None,
                    "gate": "GATE_CORRECTION_BAD_CUM_HASH",
                    "reason": "dangling_cum_hash must be 64 lowercase hex chars",
                    "mutations": []}

        # 5. Verify the dangling entry exists with matching cum_hash
        ledger_path = str(Path(__file__).parents[2] / "town" / "ledger_v1.ndjson")
        dangling_seq = int(packet["dangling_seq"])
        verified = False
        try:
            with open(ledger_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        ev = json.loads(line)
                        if ev.get("seq") == dangling_seq and ev.get("cum_hash") == dangling_cum:
                            verified = True
                            break
                    except Exception:
                        continue
        except OSError as exc:
            return {"decision": "REJECT", "receipt_id": None,
                    "gate": "GATE_CORRECTION_LEDGER_READ_ERROR",
                    "reason": f"could not read ledger: {exc}", "mutations": []}

        if not verified:
            return {"decision": "REJECT", "receipt_id": None,
                    "gate": "GATE_CORRECTION_DANGLING_NOT_FOUND",
                    "reason": (
                        f"dangling entry seq={dangling_seq} "
                        f"cum_hash={dangling_cum[:16]}... not found in ledger"
                    ),
                    "mutations": []}

        # 6. Gate A injection check on raw packet
        raw_str = raw_packet if isinstance(raw_packet, str) else json.dumps(raw_packet)
        gate_decision = gate_a(raw_str)

        # 7. MAYOR ratification
        claim = Claim(
            claim_id=claim_id,
            proposer=request.get("proposer", "unknown"),
            intent=request.get("intent", "ledger_seq_correction"),
            timestamp=request.get("timestamp", "2026-01-30T00:00:00Z"),
        )
        evidence = Evidence(
            content_snapshot=raw_str,
            content_hash=gate_decision.content_hash,
            gates_run={
                "gate_a": {
                    "result": gate_decision.result.value,
                    "code":   gate_decision.code,
                    "reason": gate_decision.reason,
                },
                "correction_schema":         {"result": "PASS", "code": "CORRECTION_SCHEMA_OK"},
                "correction_dangling_found": {"result": "PASS", "code": "CORRECTION_DANGLING_VERIFIED"},
            },
        )
        receipt = self.mayor.ratify(claim, evidence)
        self.ledger.record("CLAIM", {
            "claim_id":     claim.claim_id,
            "type":         "seq_correction",
            "dangling_seq": dangling_seq,
            "proposer":     claim.proposer,
        })
        self.ledger.record("RECEIPT", {
            "receipt_id":     receipt.receipt_id,
            "decision":       receipt.decision,
            "policy_version": receipt.policy_version,
        })

        if receipt.decision != "ACCEPT":
            return {
                "decision":   "REJECT",
                "receipt_id": receipt.receipt_id,
                "gate":       receipt.failed_gate or gate_decision.code,
                "reason":     receipt.reason,
                "mutations":  [],
            }

        # 8. Sovereign ledger write via NDJSONWriter
        correction_id = f"CORRECTION_{dangling_seq}_{claim_id}"
        correction_payload = {
            "schema_name":          "LEDGER_SEQ_CORRECTION_V1",
            "schema_version":       "1.0.0",
            "correction_id":        correction_id,
            "correction_type":      packet["correction_type"],
            "dangling_seq":         dangling_seq,
            "dangling_cum_hash":    dangling_cum,
            "dangling_decision_id": packet["dangling_decision_id"],
        }
        for opt in ("fork_point_seq", "fork_point_cum_hash", "authoritative_entry_seq",
                    "authoritative_decision_id", "root_cause", "resolution"):
            if packet.get(opt):
                correction_payload[opt] = packet[opt]

        correction_meta = {
            "claim_id":             claim_id,
            "operator_countersign": packet["operator_countersign"],
            "receipt_id":           receipt.receipt_id,
        }

        next_seq, prev_cum = _tail_ledger(ledger_path)
        try:
            writer = NDJSONWriter(path=ledger_path, seq=next_seq, prev_cum_hash=prev_cum)
            written = writer.append_event(
                event_type="LEDGER_SEQ_CORRECTION_V1",
                payload=correction_payload,
                meta=correction_meta,
            )
        except Exception as exc:
            return {
                "decision":   "REJECT",
                "receipt_id": receipt.receipt_id,
                "gate":       "GATE_CORRECTION_WRITE_FAILED",
                "reason":     f"NDJSONWriter.append_event failed: {exc}",
                "mutations":  [],
            }

        return {
            "decision":   "ACCEPT",
            "receipt_id": receipt.receipt_id,
            "gate":       "GATE_CORRECTION_PASS",
            "mutations":  [{
                "type":              "LEDGER_SEQ_CORRECTION_V1",
                "correction_id":     correction_id,
                "dangling_seq":      dangling_seq,
                "dangling_cum_hash": dangling_cum,
                "ledger_path":       "town/ledger_v1.ndjson",
                "seq":               written["seq"],
                "payload_hash":      written["payload_hash"],
                "cum_hash":          written["cum_hash"],
            }],
        }

    def _send_error(self, connection, error_msg):
        """Send error response"""
        response = {
            "error": error_msg,
            "decision": "REJECT",
            "gate": "KERNEL_ERROR"
        }
        connection.sendall(json.dumps(response).encode())


if __name__ == "__main__":
    # Run kernel daemon
    daemon = KernelDaemon()
    daemon.start()
