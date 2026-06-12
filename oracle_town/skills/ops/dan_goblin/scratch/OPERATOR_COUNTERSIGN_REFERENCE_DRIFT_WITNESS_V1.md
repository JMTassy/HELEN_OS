OPERATOR_COUNTERSIGN_V1
Packet:
  oracle_town/skills/ops/dan_goblin/scratch/REDUCER_SUBMISSION_PACKET_V1.json
Target:
  REFERENCE_DRIFT_WITNESS_V1
Operator_Instruction:
  Route this packet to the authorized Reducer surface for decision.
Allowed_Reducer_Decisions:
  - ADMIT
  - REJECT
  - REQUEST_CHANGES
Constraints:
  - This countersign is not admission.
  - This countersign does not mutate ledger.
  - This countersign does not grant sovereignty.
  - Reducer remains the only decision authority.
  - Ledger sleeps unless Reducer returns ADMIT.
Operator_Seal:
  JM_TASSY_MANUAL_COUNTERSIGN
