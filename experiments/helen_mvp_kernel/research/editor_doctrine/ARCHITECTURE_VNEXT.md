# ⎈ HELEN OS vNEXT — Applications outside, HELEN inside

authority=false · canon=false · ledger_effect=none
🟠 TARGET_ARCHITECTURE_CANDIDATE — ruled 2026-08-14, UNBUILT.
Lois exécutables : `vnext_architecture.py` (constitution, testé).
Companion : DOCTRINE_V1.md (couche commerciale).

## LA LOI À CINQ VERBES

    AI proposes. Software governs. Infrastructure isolates.
    Audit proves. Contracts guarantee.

    HELEN's intelligence may be agentic internally;
    its enterprise boundary must be deterministic software.

## LE PIVOT

HELEN OS = plateforme interne (kernel). Le produit commercial = une
application métier qui tourne dessus (Windows→Excel, Salesforce
Platform→Sales Cloud). Le client achète HELEN Research / Knowledge /
Compliance / Intelligence / Ops — jamais HER, HAL, les goblins, Claw
ou Hermes.

## L'ISOMORPHISME DE GOUVERNANCE (l'actif, pas le coût)

    Intent → Proposal → Admission → Receipt → Replay
    ≅
    Request → CandidateOperation → PolicyDecision
            → AuthorizedTransaction → AuditEvent → Replay

Toute la machinerie constitution (admission, reçus, ledger, replay)
descend dans l'infrastructure — où elle devient un différenciateur
qu'un CISO comprend.

## LES QUATRE SÉPARATIONS DURES (encodées)

1. Application ≠ HELEN Core — l'app possède UX/workflows/domaine ;
   le Core possède contexte/évidence/policy/orchestration.
2. ControlPlane ∩ SensibleClient ≈ ∅ — `E_CUSTOMER_DATA_IN_CONTROL_PLANE`.
3. BusinessLogic ⊥ ModelVendor — l'inférence s'adresse par
   (capability, classification, latency, jurisdiction), jamais par
   nom de vendeur : `E_VENDOR_IN_BUSINESS_LOGIC`.
4. Cognition large ; Effet capability-scoped — grants pointés
   (crm.read, email.send), jamais ALL : `E_AMBIENT_AUTHORITY`.

## LA TABLE DE COMPILATION (mythologie → module entreprise)

HELEN→Core Orchestration Runtime · HAL→Policy/Admission Engine ·
SOPHIA→Evidence & Verification Engine · HER→Context & Relationship
Engine · FABLE→Reporting/Narrative Service · Garden→Experimentation
Sandbox · Goblins→Ephemeral Worker Runtime · WUL→Policy/Spec IR ·
Receipt→Audit Event · Ledger→Append-only Audit Store ·
Memory→Governed Context Service.

La mythologie vit à l'intérieur ; toute surface externe qui la
laisse passer est un leak (`E_MYTHOLOGY_ON_EXTERNAL_SURFACE`). Et la
table hérite de la loi éditeur : un nom d'entreprise n'est licite
que contre le comportement témoigné — « Policy/Admission Engine »
est un nom légal pour HAL parce que ses refus sont testés.

## LES LOIS D'ÉTAT

    WorkflowEngine = autorité d'état     LLM = fonction cognitive bornée
    PostgreSQL = état applicatif faisant foi
    VectorIndex = structure dérivée      LLMContext = éphémère

Le modèle exécute CLASSIFY/EXTRACT/VERIFY ; il ne décide jamais que
le workflow a avancé (`E_LLM_IS_NOT_STATE_AUTHORITY`). Un vector
store ne devient jamais silencieusement la vérité institutionnelle
(`E_DERIVED_IS_NOT_AUTHORITATIVE`). Généalogie : le seam
REDUCER-BEGIN/END du jeu V0 est cette loi à l'échelle jouet — l'UI
propose, seuls les reducers mutent S.

## TENANCE, TOPOLOGIE, RELEASE

- Tenant_A ∩ Tenant_B = ∅ (data plane) sauf artefacts control-plane
  explicites — l'isolation comme propriété architecturale.
- Un seul package signé, trois profils (ManagedDedicated / BYOC /
  Sovereign) via adapters — un fork par profil =
  `E_TOPOLOGY_LEAKED_INTO_SEMANTICS` (une SSII déguisée en éditeur).
- ReleaseArtifact = 9-uplet (source_ref, digest, SBOM, migrations,
  config_schema, IaC, runbook, model_policy, restore_procedure) ;
  chaque déploiement répond aux 6 questions d'identité ou il est
  `E_UNIDENTIFIED_DEPLOYMENT`.

## LE RAFFINEMENT TRANSVERSAL (opérateur)

Identity + Policy + Audit + Capability + Tenant Boundary enveloppent
TOUT — application, workflow, appels IA, outils, accès données.
Gouverner seulement les actions IA est la lecture dangereuse,
refusée par nom : `E_ONLY_AI_GOVERNED`.

## WORKERS ÉPHÉMÈRES

Contrat : (input, policy, capabilities, deadline, budget) →
(result, evidence, trace, status). Aucun worker souverain ; aucun
worker ne possède de vérité persistante. Config + plugins, jamais de
forks clients (`Product_i = Core + Configuration_i`).

## LA PORTE ROADMAP

Fondation en 13 items (isolation → identité → workflow → audit →
API → gateway → contexte → observabilité → config → releases
signées → déploiement dédié → BYOC/sovereign → TMA/escrow/DR).
L'expansion des workers autonomes est l'item 14 et
`roadmap_gate` la refuse tant que les 13 ne sont pas faits — le
goulot d'un déploiement 100 k€ n'est jamais « un sub-agent de
plus », c'est « procurement peut-il approuver ce logiciel ».

## RÉSERVES

- 🟠 TOUT est cible : zéro ligne de la plateforme vNext n'existe.
  Les lois sont encodées et testées ; l'architecture qu'elles
  contraignent reste à construire. Premier falsifieur réel : le
  premier item de fondation livré sous ces contraintes.
- 🟠 La table de compilation est nominale tant que chaque module
  entreprise n'a pas son comportement témoigné en production.
- 🟢 Rien de la constitution n'est jeté : elle descend d'un étage.
