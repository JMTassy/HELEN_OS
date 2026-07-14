"""
HELEN_DISPATCH_LAYER_V1: Router Logic

Implements deterministic routing rules for classifying input and emitting DispatchReceipt.

Key invariants:
1. Deterministic: same input → same route + same receipt hash
2. Unresolved → DEFER/REJECT: no action without resolution
3. Promotion/substitution → KERNEL only
4. TEMPLE outputs non-canonical
5. All reason codes frozen
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import hashlib
import uuid
from helen_dispatch_v1_schemas import (
    InputType, RouteType, RouteAuthorityClass, MutationIntent,
    ResolutionStatus, AdmissibilityStatus, AllowedEffect, ForbiddenEffect,
    DispatchReceipt, RejectionPacket, DISPATCH_REASON_CODES,
    canonical_json_hash, hash_dispatch_receipt, validate_reason_codes
)


class DispatchRouter:
    """
    Deterministic router: input → DispatchReceipt.

    Core method: route() takes input dict and returns (DispatchReceipt, optional RejectionPacket).
    """

    def __init__(self, session_id: str, manifest_ref: Optional[str] = None):
        """Initialize router for a session."""
        self.session_id = session_id
        self.manifest_ref = manifest_ref

    def route(
        self,
        input_obj: Dict[str, Any],
        input_id: Optional[str] = None,
        store_refs: Optional[Dict[str, str]] = None,
        pressure_signal_ref: Optional[str] = None,
    ) -> Tuple[DispatchReceipt, Optional[RejectionPacket]]:
        """
        Route an input through dispatch layer.

        Args:
            input_obj: The input object (user query, command, etc.)
            input_id: Optional ID for traceability
            store_refs: Dict of store references {context, ledger, transcript}
            pressure_signal_ref: Reference to associated PRESSURE_SIGNAL_V1

        Returns:
            (DispatchReceipt, optional RejectionPacket if blocked)
        """
        if input_id is None:
            input_id = f"input_{uuid.uuid4().hex[:12]}"

        # Compute deterministic input hash
        input_hash = canonical_json_hash(input_obj)

        # Step 1: Classify input type
        input_type = self._classify_input(input_obj)

        # Step 2: Check resolution (unresolved pointers → defer/reject)
        resolution_status, unresolved_pointers = self._check_resolution(input_obj)

        # Step 3: Determine admissibility
        admissibility_status, reason_codes = self._check_admissibility(
            input_obj, input_type, resolution_status
        )

        # Step 4: Compute routing
        primary_route, secondary_routes, route_codes = self._compute_route(
            input_type, admissibility_status, resolution_status, input_obj
        )

        # Aggregate reason codes
        all_reason_codes = reason_codes + route_codes

        # Step 5: Determine authority class and effects
        route_authority_class = self._route_authority_class(primary_route)
        mutation_intent = self._mutation_intent(input_obj, primary_route)
        allowed_effects, forbidden_effects = self._allowed_forbidden_effects(
            primary_route, mutation_intent
        )

        # Step 6: Build receipt
        timestamp = datetime.utcnow().isoformat() + "Z"
        dispatch_id = f"disp_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

        receipt = DispatchReceipt(
            dispatch_id=dispatch_id,
            timestamp=timestamp,
            session_id=self.session_id,
            input_hash=input_hash,
            input_type=input_type,
            resolution_status=resolution_status,
            admissibility_status=admissibility_status,
            primary_route=primary_route,
            secondary_routes=secondary_routes,
            route_authority_class=route_authority_class,
            mutation_intent=mutation_intent,
            reason_codes=all_reason_codes,
            allowed_effects=allowed_effects,
            forbidden_effects=forbidden_effects,
            pressure_signal_ref=pressure_signal_ref,
            manifest_ref=self.manifest_ref,
            store_refs=store_refs or {},
        )

        # Compute receipt hash
        receipt.receipt_hash = hash_dispatch_receipt(receipt)

        # Step 7: Handle rejection if needed
        rejection_packet = None
        if primary_route in (RouteType.DEFER, RouteType.REJECT):
            rejection_packet = self._build_rejection_packet(
                input_id, primary_route, resolution_status, reason_codes
            )

        # Validate reason codes
        assert validate_reason_codes(all_reason_codes), \
            f"Invalid reason codes: {set(all_reason_codes) - DISPATCH_REASON_CODES}"

        return receipt, rejection_packet

    def _classify_input(self, input_obj: Dict[str, Any]) -> InputType:
        """Deterministically classify input type."""
        # Check for explicit type marker
        if "input_type" in input_obj:
            try:
                return InputType[input_obj["input_type"]]
            except KeyError:
                pass

        # Heuristic classification (in order of precedence)
        if "slash_command" in input_obj:
            return InputType.SLASH_COMMAND
        if "promotion_request" in input_obj or "promote_to" in input_obj:
            return InputType.PROMOTION_REQUEST
        if "pipeline_substitution" in input_obj:
            return InputType.PIPELINE_SUBSTITUTION_REQUEST
        if "temple" in input_obj and input_obj.get("temple") is True:
            return InputType.TEMPLE_OBSERVATION
        if "audit_type" in input_obj:
            return InputType.AUDIT_REQUEST
        if "claim_extraction" in input_obj:
            return InputType.CLAIM_EXTRACTION_REQUEST
        if "source_id" in input_obj and "content" in input_obj:
            return InputType.SOURCE_INGEST
        # memory_op must precede claim_id: a write memory op targeting a claim must
        # reach KERNEL (sovereign), not AGENT (non-sovereign).
        if "memory_op" in input_obj:
            return InputType.MEMORY_REQUEST
        if "claim_id" in input_obj:
            return InputType.CLAIM_OBJECT
        if "claims" in input_obj and isinstance(input_obj.get("claims"), list):
            return InputType.CLAIM_BUNDLE
        if "artifact_type" in input_obj:
            return InputType.ARTIFACT_REQUEST
        if "unresolved_pointers" in input_obj or "pointer" in input_obj:
            return InputType.UNRESOLVED_POINTER
        if input_obj.get("think") is True or "think_preparation" in input_obj:
            return InputType.THINK_PREPARATION

        # Default: treat as user query
        return InputType.USER_QUERY

    def _check_resolution(self, input_obj: Dict[str, Any]) -> Tuple[ResolutionStatus, List[str]]:
        """
        Check if input has unresolved pointers.

        Invariant: unresolved → DEFER or REJECT, no action.
        """
        unresolved = []

        if "unresolved_pointers" in input_obj:
            ptrs = input_obj.get("unresolved_pointers", [])
            if ptrs:
                unresolved.extend(ptrs)

        if "pointer" in input_obj and input_obj.get("pointer"):
            unresolved.append(input_obj["pointer"])

        if unresolved:
            return ResolutionStatus.UNRESOLVED, unresolved

        # Check for partial resolution
        if "partial_resolution" in input_obj:
            return ResolutionStatus.PARTIAL, []

        return ResolutionStatus.RESOLVED, []

    def _check_admissibility(
        self,
        input_obj: Dict[str, Any],
        input_type: InputType,
        resolution_status: ResolutionStatus,
    ) -> Tuple[AdmissibilityStatus, List[str]]:
        """
        Check if we can act on this input.

        Invariant: unresolved input → cannot admit.
        """
        codes = []

        # Rule 1: Unresolved → block
        if resolution_status == ResolutionStatus.UNRESOLVED:
            codes.append("unresolved_pointers_present")
            codes.append("resolution_required_before_action")
            return AdmissibilityStatus.DEFER, codes

        # Rule 2: Promotion/substitution attempts → always admit (route to KERNEL for decision)
        if input_type in (InputType.PROMOTION_REQUEST, InputType.PIPELINE_SUBSTITUTION_REQUEST):
            codes.append("promotion_requested" if input_type == InputType.PROMOTION_REQUEST else "pipeline_substitution_requested")
            return AdmissibilityStatus.ADMIT, codes

        # Rule 3: Temple observations → admit (route to TEMPLE)
        if input_type == InputType.TEMPLE_OBSERVATION:
            codes.append("temple_exploration_mode")
            return AdmissibilityStatus.ADMIT, codes

        # Rule 4: Standard workflow types → admit
        if input_type in (InputType.CLAIM_EXTRACTION_REQUEST, InputType.AUDIT_REQUEST, InputType.ARTIFACT_REQUEST):
            codes.append("multi_step_workflow_detected")
            return AdmissibilityStatus.ADMIT, codes

        # Rule 4b: THINK preparation → admit
        if input_type == InputType.THINK_PREPARATION:
            codes.append("single_transform_detected")
            return AdmissibilityStatus.ADMIT, codes

        # Rule 5: Simple transforms → admit
        if input_type in (InputType.USER_QUERY, InputType.SLASH_COMMAND, InputType.CLAIM_OBJECT):
            codes.append("single_transform_detected")
            return AdmissibilityStatus.ADMIT, codes

        # Rule 6: Ingests and bundles → admit
        if input_type in (InputType.SOURCE_INGEST, InputType.CLAIM_BUNDLE):
            codes.append("multi_step_workflow_detected")
            return AdmissibilityStatus.ADMIT, codes

        # Default: admit (let routing decide)
        return AdmissibilityStatus.ADMIT, codes

    def _compute_route(
        self,
        input_type: InputType,
        admissibility_status: AdmissibilityStatus,
        resolution_status: ResolutionStatus,
        input_obj: Dict[str, Any],
    ) -> Tuple[RouteType, List[RouteType], List[str]]:
        """
        Compute routing decision in strict order.

        Order of precedence:
        1. Unresolved/block → DEFER/REJECT
        2. Promotion/substitution → KERNEL
        3. Temple → TEMPLE
        4. Multi-step → SKILL (or AGENT if atomic)
        5. Single transform → AGENT
        6. Ambiguous → DEFER
        """
        codes = []

        # Rule 1: If not admitted → defer/reject
        if admissibility_status != AdmissibilityStatus.ADMIT:
            if resolution_status == ResolutionStatus.UNRESOLVED:
                codes.append("routing_deferred_incomplete")
                return RouteType.DEFER, [], codes
            else:
                codes.append("routing_rejected_disallowed")
                return RouteType.REJECT, [], codes

        # Rule 2a: Explicit THINK preparation request → THINK route
        # Thinking is not cognition-as-authority; it is bounded preparation
        if input_type == InputType.THINK_PREPARATION:
            codes.append("think_preparation_requested")
            codes.append("routing_to_think_preparation")
            codes.append("think_preparation_non_sovereign")
            return RouteType.THINK, [RouteType.SKILL, RouteType.AGENT], codes

        # Rule 2b: Complex multi-part USER_QUERY with explicit 'think' marker → THINK
        if (input_type == InputType.USER_QUERY
                and input_obj.get("think") is True):
            codes.append("think_preparation_complex_query")
            codes.append("routing_to_think_preparation")
            codes.append("think_preparation_non_sovereign")
            return RouteType.THINK, [RouteType.SKILL, RouteType.AGENT], codes

        # Rule 2c: Promotion/substitution → KERNEL only
        if input_type in (InputType.PROMOTION_REQUEST, InputType.PIPELINE_SUBSTITUTION_REQUEST):
            codes.append("routing_to_kernel_sovereign")
            return RouteType.KERNEL, [RouteType.SKILL, RouteType.TEMPLE], codes

        # Rule 3: Temple → TEMPLE (exploratory, never canonical)
        if input_type == InputType.TEMPLE_OBSERVATION:
            codes.append("routing_to_temple_exploration")
            return RouteType.TEMPLE, [RouteType.DEFER], codes

        # Rule 4: Audit and claim extraction → SKILL (multi-step)
        if input_type in (InputType.AUDIT_REQUEST, InputType.CLAIM_EXTRACTION_REQUEST):
            codes.append("routing_to_skill_workflow")
            return RouteType.SKILL, [RouteType.AGENT], codes

        # Rule 5: Artifact generation → SKILL
        if input_type == InputType.ARTIFACT_REQUEST:
            codes.append("routing_to_skill_workflow")
            return RouteType.SKILL, [RouteType.AGENT], codes

        # Rule 6: Ingests and bundles → SKILL (multi-step processing)
        if input_type in (InputType.SOURCE_INGEST, InputType.CLAIM_BUNDLE):
            codes.append("routing_to_skill_workflow")
            return RouteType.SKILL, [RouteType.AGENT], codes

        # Rule 7: Single objects → AGENT or SKILL depending on intent
        if input_type == InputType.CLAIM_OBJECT:
            # If trying to promote → KERNEL
            if "promote_to" in input_obj:
                codes.append("routing_to_kernel_sovereign")
                return RouteType.KERNEL, [RouteType.SKILL], codes
            else:
                codes.append("routing_to_agent_transform")
                return RouteType.AGENT, [RouteType.SKILL], codes

        # Rule 8: Slash commands
        if input_type == InputType.SLASH_COMMAND:
            cmd = input_obj.get("slash_command", "")
            if cmd in ("/promote", "/init"):
                codes.append("routing_to_kernel_sovereign")
                return RouteType.KERNEL, [RouteType.SKILL], codes
            else:
                codes.append("routing_to_agent_transform")
                return RouteType.AGENT, [RouteType.SKILL], codes

        # Rule 9: User queries → AGENT (single transform) or SKILL if multi-step intent
        if input_type == InputType.USER_QUERY:
            codes.append("routing_to_agent_transform")
            return RouteType.AGENT, [RouteType.SKILL], codes

        # Rule 10: Memory requests → depends on operation
        if input_type == InputType.MEMORY_REQUEST:
            op = input_obj.get("memory_op")
            if op in ("read", "query"):
                codes.append("routing_to_agent_transform")
                return RouteType.AGENT, [], codes
            else:
                codes.append("routing_to_kernel_sovereign")
                return RouteType.KERNEL, [RouteType.SKILL], codes

        # Fallback
        codes.append("routing_deferred_incomplete")
        return RouteType.DEFER, [], codes

    def _route_authority_class(self, route: RouteType) -> RouteAuthorityClass:
        """Map route to authority class."""
        if route == RouteType.KERNEL:
            return RouteAuthorityClass.SOVEREIGN
        elif route in (RouteType.SKILL, RouteType.AGENT, RouteType.THINK):
            # THINK is NON_SOVEREIGN: preparation is not cognition-as-authority
            return RouteAuthorityClass.NON_SOVEREIGN
        elif route == RouteType.TEMPLE:
            return RouteAuthorityClass.EXPLORATORY
        else:  # DEFER, REJECT
            return RouteAuthorityClass.BLOCKED

    def _mutation_intent(self, input_obj: Dict[str, Any], route: RouteType) -> MutationIntent:
        """Determine mutation intent from input."""
        if route == RouteType.KERNEL and "promote_to" in input_obj:
            if input_obj.get("promote_to") == "canonical":
                return MutationIntent.CANONICAL_REQUEST
            elif "pipeline_substitution" in input_obj:
                return MutationIntent.PIPELINE_CHANGE

        if "artifact_type" in input_obj:
            return MutationIntent.DERIVED_WRITE

        if input_obj.get("temple"):
            return MutationIntent.CANDIDATE_WRITE

        if "claim_id" in input_obj:
            return MutationIntent.CANDIDATE_WRITE

        return MutationIntent.NONE

    def _allowed_forbidden_effects(
        self,
        route: RouteType,
        mutation_intent: MutationIntent,
    ) -> Tuple[List[AllowedEffect], List[ForbiddenEffect]]:
        """
        Determine allowed and forbidden effects based on route and intent.

        Hard rule: Only KERNEL can mutate canonical or substitute pipeline.
        """
        forbidden = [
            ForbiddenEffect.CANONICAL_PROMOTION,
            ForbiddenEffect.RECEIPT_MUTATION,
            ForbiddenEffect.PIPELINE_SUBSTITUTION,
            ForbiddenEffect.MEMORY_SCOPE_CHANGE,
            ForbiddenEffect.SILENT_SUBSTITUTION,
        ]

        if route == RouteType.KERNEL:
            # KERNEL can do canonical, but still forbids receipt mutation and silent sub
            allowed = [AllowedEffect.READ_ONLY, AllowedEffect.CANDIDATE_WRITE, AllowedEffect.DERIVED_WRITE]
            forbidden = [
                ForbiddenEffect.RECEIPT_MUTATION,
                ForbiddenEffect.SILENT_SUBSTITUTION,
            ]
        elif route == RouteType.SKILL:
            allowed = [AllowedEffect.READ_ONLY, AllowedEffect.ARTIFACT_WRITE, AllowedEffect.CANDIDATE_WRITE]
        elif route == RouteType.AGENT:
            allowed = [AllowedEffect.READ_ONLY, AllowedEffect.ARTIFACT_WRITE]
        elif route == RouteType.TEMPLE:
            allowed = [AllowedEffect.READ_ONLY, AllowedEffect.CANDIDATE_WRITE]
        elif route == RouteType.THINK:
            # THINK: may only write a bounded preparation trace — nothing more
            # Thinking is not cognition-as-authority; it is cognition-as-auditable-preparation
            allowed = [AllowedEffect.READ_ONLY, AllowedEffect.TRACE_WRITE]
            # All state-affecting writes forbidden — THINK cannot decide, promote, or govern
            forbidden = [
                ForbiddenEffect.CANONICAL_PROMOTION,
                ForbiddenEffect.RECEIPT_MUTATION,
                ForbiddenEffect.PIPELINE_SUBSTITUTION,
                ForbiddenEffect.MEMORY_SCOPE_CHANGE,
                ForbiddenEffect.SILENT_SUBSTITUTION,
            ]
        else:  # DEFER, REJECT
            allowed = [AllowedEffect.READ_ONLY]

        return allowed, forbidden

    def _build_rejection_packet(
        self,
        input_id: str,
        route: RouteType,
        resolution_status: ResolutionStatus,
        reason_codes: List[str],
    ) -> RejectionPacket:
        """Build RejectionPacket for DEFER/REJECT routes."""
        rejection_id = f"rej_{uuid.uuid4().hex[:12]}"
        timestamp = datetime.utcnow().isoformat() + "Z"

        if route == RouteType.DEFER:
            if resolution_status == ResolutionStatus.UNRESOLVED:
                message_class = "resolution_required"
                can_retry = True
                retry_requirements = [
                    "resolve_unresolved_pointers",
                    "attach_source_document",
                    "specify_target_scope",
                ]
            else:
                message_class = "clarify_before_action"
                can_retry = True
                retry_requirements = ["provide_missing_context"]
        else:  # REJECT
            message_class = "out_of_scope"
            can_retry = False
            retry_requirements = []

        return RejectionPacket(
            rejection_id=rejection_id,
            timestamp=timestamp,
            input_id=input_id,
            reason_codes=reason_codes,
            message_class=message_class,
            can_retry=can_retry,
            retry_requirements=retry_requirements,
        )
