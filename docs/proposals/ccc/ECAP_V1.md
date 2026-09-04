# ECAP — Epistemic Context Assembly Protocol V1
🟣 PROPOSAL · authority:false · Niveau 2 (implémentation de CCC-4). ECAP = la forme opérationnelle du
Context Compiler de CCC. ECAP : (C,S,L,E,A,T) → P.

## Fonction (pipeline)
AVAILABLE CORPUS → SELECT → CLASSIFY → ATTACH LAW → ATTACH EVIDENCE → ATTACH COUNTER-EVIDENCE →
ANCHOR → VERSION → HASH → PRESENT. (Peut REFUSER: sortie Result(P,ℱ), cf. CCC_SEMANTICS V0.1.)

## Invariants ECAP (instances de l'algèbre ≢)
available corpus ≢ selected corpus · selected ≢ presented · summary ≢ source · receipt ≢ truth ·
proposal ≢ admission · anchor ≢ paraphrase · grader output ≢ final truth.

## Contrat de sortie minimal
{ ecap_version, task, core_laws[], domain_laws[], evidence[], counter_evidence[], anchors[],
  omissions[], truncation_status:"NONE|DECLARED", compiler_policy, packet_hash:"sha256:…", authority:false }
Les `omissions[]` et `truncation_status` sont OBLIGATOIRES: une omission silencieuse est une violation.

## Position
ECAP → Context Packet → Model Output → Anchor-Cut Evaluation → Claim → Decision → Permission →
Action → Receipt → Admitted State.
> ECAP garantit que le jugement porte sur un contexte gouverné, et non sur un assemblage invisible de fragments.
