# Selective Admissibility Dynamics — V0 (Formal Core)

## Selective Admissibility Calculus (SAC) + Dynamics (SAD)

```yaml
schema: SELECTIVE_ADMISSIBILITY_DYNAMICS_V0
status: PROPOSAL
banner: 🟣 CLAIM
kind: mathematical_formal_core
revision: V0_FORMAL_CORE
authority: false
sovereign: false
canon: false
claim_status: NO_CLAIM
ledger_effect: none
implementation: BLOCKED
implementation_blocked: true
human_admission_required: true
publication_status: NON_PUBLISHED
peer_reviewed: false
final: HOLD_FOR_OPERATOR
git_stage: no
git_commit: no
scope: |
  Math normalization only: sets, types, transitions, support, hard
  admissibility, budgeted selection, traceable compost, exogenous admission,
  two theorems with proofs, explicit hypotheses, counterexamples.
  No implementation, no JSON Schema, no SKILL, no commit.
origin: |
  Normalization GO 2026-07-18 from session synthesis (selection operator Σ,
  dual reality, support sparsity, Unseen Gardener, sovereignty preservation).
  HELEN is one intended instance; the calculus is application-independent.
naming:
  SAC: Selective Admissibility Calculus — legal moves (support, types, hard A)
  SAD: Selective Admissibility Dynamics — multi-epoch generate→select→compost
companions:
  - docs/proposals/THE_UNSEEN_GARDENER_V0.md
  - docs/proposals/HELEN_OS_API_DOMAIN_MODEL_V0.md
  - docs/proposals/MARK_INTERVENE_SURFACE_CONTRACT_V0.md
  - docs/proposals/TRANSPORT_THEOREM_V0.md
  - docs/proposals/GAS_V0.md
```

🟣 CLAIM · PROPOSAL · NON_PUBLISHED · IMPLEMENTATION_BLOCKED · HOLD_FOR_OPERATOR  
**authority=false** · **ledger_effect=none**

```
SAC defines legal moves.
SAD defines legal evolution.
```

\[
\boxed{\text{SAD does not only decide what to keep.}}
\]

It jointly defines:

\[
\boxed{
\begin{aligned}
&\text{what may be generated, what may survive,}\\
&\text{what may change, and what can never become authority}\\
&\text{without an explicit bridge.}
\end{aligned}
}
\]

---

## 0. Scope and non-claims

This document is a **research formalization**. It is not peer-reviewed, not
admitted HELEN doctrine, and not a bibliographic priority claim. Exhaustive
2026 literature comparison remains open.

**Out of scope:** code, schemas, skills, shell, ledger writes, commits.

---

## 1. Sets and types

### 1.1 Candidate set (selection domain)

Let \(X=\{x_1,\ldots,x_n\}\) be a finite set of **candidates**
(dreams, proposals, claims, agents, or interpretations).

### 1.2 System state (dynamics domain)

Let the full system state live in a product of typed blocks:

\[
\mathcal{X}
\;=\;
\mathcal{W}
\times
\mathcal{R}
\times
\mathcal{B}
\times
\mathcal{E}
\times
\mathcal{M}
\times
\mathcal{Q}.
\tag{S1}
\]

A state at time \(t\) is

\[
\mathbf{x}_t
=
(w_t,\, r_t,\, b_t,\, e_t,\, m_t,\, q_t)
\in
\mathcal{X}.
\tag{S2}
\]

| Coordinate | Type | Meaning |
|---|---|---|
| \(w_t\in\mathcal{W}\) | world | mutable conditions (files, resources, needs, app state) |
| \(r_t\in\mathcal{R}\) | traces | observations, logs, warnings, sensor outputs (not automatically true) |
| \(b_t\in\mathcal{B}\) | broadcast | scarce shared workspace contents (goal, conflict, candidate, constraint) |
| \(e_t\in\mathcal{E}\) | epistemic | test/status of claims (untested / pass / fail / inconclusive, …) |
| \(m_t\in\mathcal{M}\) | memory | retained objects with provenance and lifetime |
| \(q_t\in\mathcal{Q}\) | sovereign | candidate / hold / rejected / admitted / canonical |

**Structural non-determination:**

\[
(w_t,r_t,b_t,e_t,m_t)
\quad\text{do not determine}\quad
q_t.
\tag{S3}
\]

### 1.3 Dual observation channels (separately typed)

Define two **distinct** codomains and maps (not two names for one map):

\[
R_R : \mathcal{X} \to L_R,
\qquad
R_T : \mathcal{X} \to L_T,
\tag{S4}
\]

with \(L_R \neq L_T\) as types (possibly same underlying carrier, **distinct**
semantic roles):

- \(R_R(\mathbf{x})=\mathrm{Probe}_t(\mathbf{x})\) — **Runtime Reality** (volatile),
- \(R_T(\mathbf{x})=\mathrm{Replay}(L)(\mathbf{x})\) — **Trust Reality** from ledger \(L\).

**Membrane (design axiom):** there is no free (untyped, unconstrained) function
\(\phi: L_R\to L_T\) that is part of the legal transition class such that
\(R_T=\phi\circ R_R\) for all \(\mathbf{x}\). The only legal bridge is the
typed chain of §7.

### 1.4 Orthogonal status of a claim

Each claim \(c\) carries a **product** status (no single-bit collapse):

\[
\sigma(c)
=
\bigl(
\epsilon(c),\;
\alpha(c),\;
\nu(c),\;
\rho(c),\;
\eta(c)
\bigr).
\tag{S5}
\]

| Component | Range (illustrative finite sets) |
|---|---|
| \(\epsilon\) epistemic origin | observed, inferred, proposed |
| \(\alpha\) action effect | untouched, attempted, changed, failed, unknown |
| \(\nu\) verification | untested, pass, fail, inconclusive |
| \(\rho\) review | unreviewed, challenged, clear-with-limits |
| \(\eta\) authority | candidate, hold, rejected, admitted |

Hard non-implications (axiomatic separation):

\[
\begin{align}
\mathrm{generated}(x)
&\;\not\Rightarrow\;
\mathrm{true}(x),
\tag{S6}\\
\mathrm{selected}(x)
&\;\not\Rightarrow\;
\mathrm{verified}(x),
\tag{S7}\\
\mathrm{verified}(x)
&\;\not\Rightarrow\;
\mathrm{admitted}(x).
\tag{S8}
\end{align}
\]

Valid intermediate states include
\(S(x)\land\neg V(x)\) and \(V(x)\land\neg H(x)\).

### 1.5 Lawful epistemic chain (typed, non-reversing)

\[
G(x)\;\to\; P(x)\;\to\; S(x)\;\to\; V(x)\;\to\; H(x),
\tag{S9}
\]

with \(G\) generated, \(P\) proposed, \(S\) selected, \(V\) verified,
\(H\) human-admitted. No reverse implication is automatic.

---

## 2. Transitions

### 2.1 Operation partition

\[
\mathcal{U}
=
\mathcal{U}_O
\;\sqcup\;
\mathcal{U}_A
\;\sqcup\;
\mathcal{U}_V
\;\sqcup\;
\mathcal{U}_M
\;\sqcup\;
\mathcal{U}_H.
\tag{T1}
\]

Observation · Action · Verify · Memory · HumanAdmit.

Each \(u\in\mathcal{U}\) induces

\[
F_u : \mathcal{X}\to\mathcal{X}.
\tag{T2}
\]

### 2.2 Identity transition

Let \(u_{\mathrm{id}}\) be the **identity operation**:

\[
F_{u_{\mathrm{id}}}(\mathbf{x})
=
\mathbf{x}
\quad
\forall\mathbf{x}\in\mathcal{X}.
\tag{T3}
\]

All support definitions are relative to \(u_{\mathrm{id}}\) (not to an
unspecified “null” or noisy baseline).

---

## 3. Support: allowed, forbidden, required

### 3.1 Discrete support against identity

Index coordinates of \(\mathcal{X}\) by a finite set \(I=\{w,r,b,e,m,q\}\)
(or a finer finite refinement). Write \(F_u(\mathbf{x})_i\) for the \(i\)-th
coordinate.

\[
\operatorname{Support}(u,\mathbf{x})
\;=\;
\bigl\{\,
i\in I
\;\big|\;
F_u(\mathbf{x})_i
\;\neq\;
F_{u_{\mathrm{id}}}(\mathbf{x})_i
\,\bigr\}
\;=\;
\bigl\{\,
i\in I
\;\big|\;
F_u(\mathbf{x})_i
\;\neq\;
\mathbf{x}_i
\,\bigr\}.
\tag{T4}
\]

### 3.2 Legal masks

For each operation type \(\tau(u)\), fix three subsets of \(I\):

\[
\begin{align}
L^+(u)
&\;\subseteq\;
I
&&\text{(allowed: may change)},
\tag{T5}\\
L^-(u)
&\;\subseteq\;
I
&&\text{(forbidden: must not change)},
\tag{T6}\\
L^\bullet(u)
&\;\subseteq\;
L^+(u)
&&\text{(required: must change when \(u\) succeeds)}.
\tag{T7}
\end{align}
\]

**Consistency:** \(L^+(u)\cap L^-(u)=\varnothing\) and
\(L^+(u)\cup L^-(u)=I\) (partition of coordinates for type \(\tau(u)\)).

### 3.3 Violation measure

Define the discrete causal indicator

\[
J^\Delta_{i}(u,\mathbf{x})
=
\mathbf{1}\!\left[
F_u(\mathbf{x})_i
\neq
\mathbf{x}_i
\right].
\tag{T8}
\]

\[
\Omega(u,\mathbf{x})
=
\sum_{i\in I}
J^\Delta_{i}(u,\mathbf{x})
\cdot
\mathbf{1}\!\left[i\in L^-(u)\right].
\tag{T9}
\]

- \(\Omega=0\): no forbidden coordinate moved.
- \(\Omega>0\): membrane / type breach.

**Successful typed action** further requires
\(L^\bullet(u)\subseteq\operatorname{Support}(u,\mathbf{x})\) when \(u\) is
declared successful (not merely attempted).

### 3.4 Default type templates (illustrative, not exhaustive)

| Type | \(L^+\) (allowed) | \(L^-\) (forbidden) | \(L^\bullet\) example |
|---|---|---|---|
| OBSERVE | \(\{r,b,m\}\) | \(\{w,q\}\) | \(\{r\}\) |
| ACT / INTERVENE | \(\{w,r,m\}\) (+ materials if refined) | \(\{q\}\) | \(\{w\}\) |
| VERIFY | \(\{r,e,m\}\) | \(\{w,q\}\) | \(\{e\}\) |
| MEMORY ops | \(\{m\}\) | \(\{q\}\) (unless admit) | \(\{m\}\) |
| ADMIT (human) | \(\{q,m\}\) | \(\{w\}\) (default) | \(\{q\}\) |
| COMPOST | pool coordinates + \(m\) digests | \(\{q\}\) | record of compost |

### 3.5 MARK vs INTERVENE (semantic domain orthogonality)

Restrict orthogonality to **semantic domain coordinates**
\(I_{\mathrm{sem}}=\{w,r,a\}\) when attention \(a\) is a refinement of \(b\)
or of \(r\); do **not** claim orthogonality over all of \(I\) (history \(m\) is
shared).

Teaching instance (when MARK \(\in\mathcal{U}_O\)-family and INTERVENE \(\in\mathcal{U}_A\)):

\[
\begin{align}
L^+(\mathrm{MARK})
&\;\cap\;
I_{\mathrm{sem}}
\;\subseteq\;
\{r,a\},
\tag{T10}\\
L^+(\mathrm{INTERVENE})
&\;\cap\;
I_{\mathrm{sem}}
\;\subseteq\;
\{w\},
\tag{T11}\\
L^+(\mathrm{MARK})
\cap
L^+(\mathrm{INTERVENE})
\cap
I_{\mathrm{sem}}
&\;=\;
\varnothing.
\tag{T12}
\end{align}
\]

History coordinate \(m\) may appear in both \(L^+\) sets; **(T12) does not
apply to \(m\)**.

---

## 4. Hard admissibility and selection operator \(\Sigma\)

### 4.1 Survival predicates

On candidates \(x\in X\):

\[
\begin{align}
A(x)
&=\text{admissible under hard constraints},
\tag{A1}\\
E(x)
&=\text{supported by evidence (at required strength)},
\tag{A2}\\
U(x)
&=\text{useful for the current goal}.
\tag{A3}
\end{align}
\]

\[
S(x)
=
A(x)\land E(x)\land U(x).
\tag{A4}
\]

\[
\Sigma(X)
=
\{x\in X\mid S(x)\},
\qquad
C_{\mathrm{set}}(X)
=
X\setminus\Sigma(X).
\tag{A5}
\]

### 4.2 Operator properties (ideal absolute filter)

When \(S\) is an absolute predicate (not comparative ranking):

\[
\begin{align}
\Sigma(\Sigma(X))
&=\Sigma(X)
&&\text{(idempotence)},
\tag{A6}\\
\Sigma(X)
&\subseteq X
&&\text{(contractiveness)},
\tag{A7}\\
X\subseteq Y
&\;\Rightarrow\;
\Sigma(X)\subseteq\Sigma(Y)
&&\text{(monotonicity)}.
\tag{A8}
\end{align}
\]

**Caveat:** if selection is **comparative** (top-\(K\) by fitness), monotonicity
**(A8) may fail**. See §5.

### 4.3 Constraint set

\[
\mathcal{A}
=
\{x\in X\mid g_i(x)\le 0,\; i=1,\ldots,m\}.
\tag{A9}
\]

Hard admissibility \(A(x)\) is equivalent to \(x\in\mathcal{A}\) when \(g_i\)
encode membrane, schema, budget, and authority ceilings.

### 4.4 Fitness (not confidence alone)

\[
\begin{align}
F(x)
&=
\alpha\,\mathrm{evidence}(x)
+
\beta\,\mathrm{critical\_separation}(x)
+
\gamma\,\mathrm{goal\_utility}(x)
\notag\\
&\quad
-
\lambda\,\mathrm{cost}(x)
-
\mu\,\mathrm{authority\_risk}(x).
\tag{A10}
\end{align}
\]

**Forbidden default:** \(F(x)=\mathrm{confidence}(x)\).

---

## 5. Budgeted selection as constrained subset optimization

Fix budget \(K\in\mathbb{N}\), \(K\ge 1\) (**generalizes ONE SURVIVOR** \(K=1\)).

### 5.1 Optimization form

Let \(\Pi_t=\mathrm{Generate}(\mathbf{x}_t)\) (finite multiset; treat as set
after dedup if required).

\[
\begin{align}
S_t^\star
\in
\arg\max_{S\subseteq\Pi_t}
&\quad
\sum_{x\in S} F(x)
\tag{Sel1}\\
\text{s.t.}
&\quad
S\subseteq\mathcal{A},
\notag\\
&\quad
|S|\le K,
\notag\\
&\quad
\text{optional: pairwise non-contradiction constraints on }S.
\notag
\end{align}
\]

If the feasible set is empty, \(S_t^\star=\varnothing\).

### 5.2 Comparative selection and monotonicity

**Proposition (conditional monotonicity).**  
If selection is pure thresholding \(\Sigma(X)=\{x\in X:S(x)\}\) with fixed
predicates independent of \(X\), then (A8) holds.  
If selection is top-\(K\) under \(F\) on the ambient set, (A8) **need not** hold:
adding a higher-\(F\) candidate can eject a previous survivor.

### 5.3 Conditional generation growth (not unconditional accumulation)

**Proposition (conditional accumulation).**  
**Hypotheses:** (i) no compost/retention budget; (ii) generation only adds
candidates; (iii) no exogenous deletion.  
**Then** \(|\Pi_{t+1}|\ge|\Pi_t|\).

**Counterexample to unconditional claim:** with budgeted \(\operatorname{Select}\)
and compost, \(|\Pi_{t+1}|\) may decrease. Therefore the earlier slogan
“generation always expands” is **false** as a general law; it holds only under
the hypotheses above.

### 5.4 Fixed point of generate–select

\[
X_{t+1}
=
\Sigma\bigl(G(X_t)\bigr)
\quad\text{(or budgeted }S^\star\text{)}.
\tag{Sel2}
\]

A local fixed point \(X^\star=\Sigma(G(X^\star))\) means: under current generator,
constraints, evidence, and goal, no further admissible improvement is found —
**not** metaphysical truth.

### 5.5 Compact form

With \(\mathcal{G}\) generative possibility and \(\Sigma\) (or budgeted \(S^\star\))
disciplined selection:

\[
\boxed{\mathcal{C}=\Sigma(\mathcal{G})}
\tag{Sel3}
\]

informally: coherence \(=\) generation minus inadmissible variation (under
stated \(\kappa,F,K\)).

Pipeline sketch:

\[
\operatorname{Select}
=
\operatorname{Constraint}
\circ
\operatorname{Challenge}
\circ
\operatorname{Deduplicate}
\circ
\operatorname{Rank}_{\le K}.
\tag{Sel4}
\]

---

## 6. Traceable compost

Compost is **not** silent deletion.

### 6.1 Compost record type

\[
\begin{align}
\gamma
&=
\bigl(
\mathrm{id},\;
\mathrm{epoch},\;
\mathrm{candidate\_ref},\;
\mathrm{reason},\;
\mathrm{rule\_id},\;
\mathrm{digest}
\bigr)
\in
\Gamma.
\tag{C1}
\end{align}
\]

\[
\operatorname{CompostRecords}_t
=
\bigl\{\,
\gamma(\pi)
\;\big|\;
\pi\in\Pi_t\setminus S_t^\star
\,\bigr\}.
\tag{C2}
\]

Each ejected \(\pi\) yields a record with:

- \(\mathrm{epoch}=t\),
- \(\mathrm{reason}\in\{\mathrm{hard\_fail},\,\mathrm{rank},\,\mathrm{duplicate},\,\mathrm{stale},\,\ldots\}\),
- \(\mathrm{digest}\) of bounded length (for sedimentation control).

### 6.2 Selective forgetting (memory)

\[
M_{t+1}
=
R(M_t\cup N_t),
\qquad
R(Y)
=
\{y\in Y\mid \rho(y)\ge\theta\},
\tag{C3}
\]

\[
\begin{align}
\rho(y)
&=
a\,\mathrm{relevance}
+
b\,\mathrm{evidence}
+
c\,\mathrm{provenance}
-
d\,\mathrm{staleness}
-
e\,\mathrm{duplication}.
\tag{C4}
\end{align}
\]

\[
F_t
=
(M_t\cup N_t)\setminus M_{t+1}.
\tag{C5}
\]

Forgetting \(\neq\) random deletion: it is constrained elimination with score
\(\rho\).

---

## 7. Typed bridge and exogenous admission

### 7.1 Typed chain

Objects of **distinct types**:

\[
\begin{align}
o &\in \mathcal{O}
&&\text{RuntimeObservation},
\tag{B1}\\
p &\in \mathcal{P}
&&\text{CandidateEvidencePacket},
\tag{B2}\\
\rho &\in \mathcal{R}_{\mathrm{rcpt}}
&&\text{Receipt},
\tag{B3}\\
\alpha &\in \{0,1\}
&&\text{Admission bit / decision},
\tag{B4}\\
L &\in \mathcal{L}
&&\text{Ledger (append-only)},
\tag{B5}\\
\ell_T &\in L_T
&&\text{Trust reconstruction}.
\tag{B6}
\end{align}
\]

Legal morphisms (typed; not free maps on bits):

\[
\mathcal{O}
\;\xrightarrow{\mathrm{packetize}}\;
\mathcal{P}
\;\xrightarrow{\mathrm{receipt}}\;
\mathcal{R}_{\mathrm{rcpt}}
\;\xrightarrow{\mathrm{admit}}\;
\{0,1\}
\;\xrightarrow{\mathrm{append}}\;
\mathcal{L}
\;\xrightarrow{\mathrm{replay}}\;
L_T.
\tag{B7}
\]

### 7.2 Exogenous admission (projection form)

Let \(\pi_q:\mathcal{X}\to\mathcal{Q}\) be projection onto the sovereign block.

An operation \(F_u\) is **non-sovereign** when

\[
\pi_q\circ F_u
=
\pi_q.
\tag{B8}
\]

Human admission is exogenous:

\[
q_{t+1}
=
\begin{cases}
\mathsf{Admit}(q_t,\rho_t,h_t)
&
\text{if }h_t=1\text{ and gates pass},\\[4pt]
q_t
&
\text{if }h_t=0,
\end{cases}
\tag{B9}
\]

with \(h_t\in\{0,1\}\) the HumanSeal bit. Soft scores do not appear in (B9).

**Canon update:**

\[
\mathrm{Canon}_{t+1}
=
\mathrm{HumanAdmit}\bigl(\mathrm{VerifiedCandidates}_t\bigr)
\quad
(h_t=1).
\tag{B10}
\]

---

## 8. Critical-pair separation (workers / goblins)

### 8.1 Observation quotients

Each worker \(g\) has \(R_g:\mathcal{X}\to\mathcal{L}_g\). Indistinguishability:

\[
\mathbf{x}\sim_g\mathbf{y}
\iff
R_g(\mathbf{x})=R_g(\mathbf{y}).
\tag{W1}
\]

### 8.2 Critical pairs

Let \(\mathcal{C}\subseteq\mathcal{X}\times\mathcal{X}\) be the set of pairs that
**must** be distinguished (task-defined), e.g. modified/unmodified file,
announced success vs real success, proposal vs admission.

A set \(G\) of workers is **sufficient** for \(\mathcal{C}\) when

\[
\forall(\mathbf{x},\mathbf{y})\in\mathcal{C},\;
\exists g\in G:\;
R_g(\mathbf{x})\neq R_g(\mathbf{y}).
\tag{W2}
\]

### 8.3 Minimal Sufficient Warren (weighted set cover)

\[
\begin{align}
G^\star
\in
\arg\min_{G\subseteq\mathcal{G}}
&\quad
\sum_{g\in G} c_g
\tag{W3}\\
\text{s.t.}
&\quad
\text{(W2)}.
\notag
\end{align}
\]

**Necessity of a worker:**

\[
g\text{ is necessary for }\mathcal{C}
\iff
\exists(\mathbf{x},\mathbf{y})\in\mathcal{C}
\text{ separated by }g\text{ and by no worker in }G^\star\setminus\{g\}
\text{ (for a minimal }G^\star\text{)}.
\tag{W4}
\]

This replaces vague “rank of Jacobian rows” with **critical-pair separation**.

---

## 9. Lattice view (coherence without sameness)

Let \((X,\preceq)\) be a poset where \(x\preceq y\) means “\(y\) is at least as
supported/precise/useful as \(x\).” With \(\mathcal{A}\) admissible,

\[
\operatorname{Max}(\mathcal{A})
=
\{x\in\mathcal{A}\mid \nexists y\in\mathcal{A}:\; x\prec y\}.
\tag{L1}
\]

If several incomparable maxima remain, preserve the **antichain**
\(\operatorname{Max}(\mathcal{A})\) rather than forcing false consensus
(when \(K\) allows, or record multi-survivor antichain under budget).

---

## 10. Dynamics sketch

Population (optional continuous reweighting; not required for theorems below):

\[
p_i(t+1)
=
\frac{p_i(t)\,f_i(t)}{\sum_j p_j(t)f_j(t)},
\tag{D1}
\]

with governance-aware \(f_i\) (evidence + utility + novel distinction − risk − cost),
**not** confidence alone.

Governed step:

\[
\mathbf{x}_{t+1}
=
F_{u_t}(\mathbf{x}_t)
\quad\text{with}\quad
\operatorname{Support}(u_t,\mathbf{x}_t)\subseteq L^+(u_t),
\quad
\operatorname{Support}(u_t,\mathbf{x}_t)\cap L^-(u_t)=\varnothing.
\tag{D2}
\]

---

## 11. Theorems

### 11.1 Theorem (Sovereignty preservation under composition)

**Setup.** Let

\[
\mathcal{F}_N
=
\{
F_u:\mathcal{X}\to\mathcal{X}
\mid
\pi_q\circ F_u=\pi_q
\}.
\tag{Th1.0}
\]

**Statement.** If \(F_{u_1},\ldots,F_{u_n}\in\mathcal{F}_N\) and

\[
F
=
F_{u_n}
\circ
\cdots
\circ
F_{u_1},
\]

then

\[
\pi_q\circ F
=
\pi_q.
\tag{Th1}
\]

**Proof.** For \(n=1\), immediate from membership in \(\mathcal{F}_N\).

Assume true for \(n=k\): \(\pi_q\circ(F_{u_k}\circ\cdots\circ F_{u_1})=\pi_q\).

For \(n=k+1\),

\begin{align*}
\pi_q\circ(F_{u_{k+1}}\circ F_{u_k}\circ\cdots\circ F_{u_1})
&=
(\pi_q\circ F_{u_{k+1}})
\circ
(F_{u_k}\circ\cdots\circ F_{u_1}) \\
&=
\pi_q
\circ
(F_{u_k}\circ\cdots\circ F_{u_1})
&&\text{(since }F_{u_{k+1}}\in\mathcal{F}_N\text{)} \\
&=
\pi_q
&&\text{(induction hypothesis)}.
\end{align*}

By induction, (Th1) holds for all finite \(n\). \(\square\)

**Corollary (Empty Sovereign Chair).**  
No finite composition of non-sovereign operations
(generation, challenge, selection, consensus, memory writes that preserve \(q\),
verify-if-typed-non-sovereign, animation, confidence updates) can change \(q\).
Authority requires an operation **outside** \(\mathcal{F}_N\) (HumanSeal admit).

**Counterexample (why typing matters).**  
If a mis-typed “VERIFY” is allowed to write \(q\), then \(F_{\mathrm{VERIFY}}\notin\mathcal{F}_N\)
and the theorem’s hypothesis fails — the breach is a **support/mask** failure
(\(\Omega>0\)), not a failure of the theorem.

### 11.2 Theorem (Bounded retention under budgeted selection)

**Hypotheses.**

1. For every epoch \(t\), \(|S_t^\star|\le K\).
2. Every survivor \(\pi\in S_t^\star\) has description length \(\ell(\pi)\le B_\pi\).
3. Each compost record \(\gamma\) has \(\ell(\gamma)\le B_C\).
4. At most \(H\) past epochs of compost digests are retained, with at most
   \(K_C\) compost records per epoch (or total compost slots \(H\cdot K_C\)).

**Statement.** Active survivor memory length and retained compost length satisfy

\[
L(S_t^\star)
\;\le\;
K\, B_\pi,
\tag{Th2a}
\]

\[
L(\mathcal{M}_t^{\mathrm{compost}})
\;\le\;
H\, K_C\, B_C,
\tag{Th2b}
\]

hence

\[
L(\mathcal{M}_t^{\mathrm{active}})
\;\le\;
K\, B_\pi
+
H\, K_C\, B_C
\tag{Th2}
\]

when active memory is survivors plus bounded compost digests.

**Proof.**  
(Th2a): at most \(K\) survivors, each of length \(\le B_\pi\), so sum of lengths
\(\le K B_\pi\).  
(Th2b): at most \(H\cdot K_C\) compost records, each \(\le B_C\).  
Sum gives (Th2). \(\square\)

**Interpretation.** Compostage is a **sedimentation control** mechanism, not
aesthetic minimalism.

### 11.3 Claim A (Selection–coherence) — conditional

**Hypotheses for Claim A.**

1. Contradiction relation \(\#\) on candidates is fixed and symmetric.
2. Hard constraint \(\kappa\) rejects any set containing a pair with \(\#\).
3. \(S_t^\star\) is feasible under \(\kappa\) and \(|S|\le K\).
4. \(\delta(\cdot)\) is a monotone incoherence measure under inclusion of claim sets
   (e.g. number of contradictory pairs).

**Claim A.** Under (1)–(4),

\[
\delta(S_t^\star)
\;\le\;
\delta(\Pi_t).
\tag{ClaimA}
\]

**Reason.** \(S_t^\star\subseteq\Pi_t\) and \(\delta\) monotone under inclusion ⇒
inequality. If \(\kappa\) forbids contradictions inside \(S_t^\star\), one may
strengthen to \(\delta(S_t^\star)=0\) for pairwise \(\delta\).

**Without (4), Claim A is not asserted.**

### 11.4 Claim B (Finite survivor description) — conditional

**Hypotheses for Claim B.**  
Same as Theorem 11.2 hypotheses (1)–(2) only.

**Claim B.**

\[
\sum_{\pi\in S_t^\star}\ell(\pi)
\;\le\;
K\, B_\pi.
\tag{ClaimB}
\]

This is exactly (Th2a); listed as Claim B for continuity with prior draft
language. **Not asserted** without length bounds \(B_\pi\) and budget \(K\).

---

## 12. Parallel result: action does not imply verification

**Proposition.** Let \(\pi_e:\mathcal{X}\to\mathcal{E}\). If every
\(a\in\mathcal{U}_A\) satisfies \(\pi_e\circ F_a=\pi_e\), then any finite
composition of actions preserves \(e\).

**Proof.** Identical to Theorem 11.1 with \(\pi_e\) in place of \(\pi_q\). \(\square\)

Thus \(\mathrm{attempted}\not\Rightarrow\mathrm{verified}\) when ACT is typed
to preserve \(e\).

---

## 13. Explicit counterexamples

| # | Bad claim | Counterexample |
|---|---|---|
| 1 | Generation always grows \(|\Pi|\) | Budgeted select + compost shrinks pool |
| 2 | \(\Sigma\) always monotone | Top-\(K\) rank ejects prior survivor when better candidate arrives |
| 3 | Selected ⇒ verified | \(S(x)\land\nu=\mathrm{untested}\) allowed by (S7) |
| 4 | Verified ⇒ admitted | \(V(x)\land\eta=\mathrm{candidate}\) with \(h=0\) |
| 5 | Consensus of non-sovereign ops admits | Theorem 11.1: all \(F_u\in\mathcal{F}_N\) keep \(q\) |
| 6 | MARK⊥INTERVENE on all coordinates | Both may write \(m\); orthogonality only on \(I_{\mathrm{sem}}\) |
| 7 | Confidence fitness is safe | High-confidence false claim maximizes \(F=\mathrm{conf}\) |

---

## 14. Hypotheses catalog (global)

| ID | Hypothesis |
|---|---|
| H1 | State space is a finite product of typed blocks (S1) |
| H2 | Operations are total maps \(F_u:\mathcal{X}\to\mathcal{X}\) |
| H3 | Each \(u\) has fixed \(L^+,L^-,L^\bullet\) with partition of \(I\) |
| H4 | Support is defined vs identity (T3)–(T4) |
| H5 | Non-sovereign class is exactly \(\pi_q\circ F_u=\pi_q\) |
| H6 | HumanSeal \(h_t\) is exogenous (not computed by \(F_u\) for \(u\notin\mathcal{U}_H\)) |
| H7 | Budgets \(K,H,K_C\) and length bounds \(B_\pi,B_C\) are finite |
| H8 | Critical pair set \(\mathcal{C}\) is task-given |

Violating H3–H5 voids breach detection and sovereignty theorem applicability.

---

## 15. Relation to SAC / SAD naming

| Layer | Name | Content |
|---|---|---|
| SAC | Selective Admissibility Calculus | support, types, \(\Omega\), hard \(A\), masks |
| SAD | Selective Admissibility Dynamics | generate, budgeted select, compost records, epochs |

Optional French designation (doctrine layer, not a second math object):
**SPGEC** — Sovereignty-Preserving Governed Epistemic Calculus.

---

## 16. Closing

\[
\boxed{\Sigma\text{ is the operator that decides what remains.}}
\]

\[
\boxed{\pi_q\circ F=\pi_q\text{ for all non-sovereign }F\text{ (Th1).}}
\]

\[
\boxed{L(\text{active memory})\le KB_\pi + HK_C B_C\text{ (Th2).}}
\]

\[
\boxed{R_R:X\to L_R\;\text{and}\;R_T:X\to L_T\text{ are distinct typed channels.}}
\]

```
PROPOSAL
NON_PUBLISHED
IMPLEMENTATION_BLOCKED
HOLD_FOR_OPERATOR
authority=false · ledger_effect=none
```

```
ENTER — FORMAL CORE ONLY.
No schema. No skill. No commit.
```

---

# PART II — FORMAL CORE (V0.1 math normalization)

```yaml
revision: V0.1-formal-core
supersedes: informal statements of Part I (listed per item; Part I retained
            as motivation — DREAMT layer; Part II is the citable layer)
scope_of_edit: this file only · math normalization only
status: PROPOSAL · NON_PUBLISHED · IMPLEMENTATION_BLOCKED
authority: false · HOLD_FOR_OPERATOR
review_source: operator-relayed math review (20 corrections), 2026-07-18
```

## FC-1. Types and spaces

State factorization (semantic / accounting / history — correction §6):

$$\mathcal X=\mathcal X_{\mathrm{dom}}\times\mathcal X_{\mathrm{acct}}\times\mathcal X_{\mathrm{hist}},\qquad
\mathcal X_{\mathrm{dom}}=\mathcal W\times\mathcal R\times\mathcal A\times\mathcal E\times\mathcal Q$$

with $\mathcal W$ world, $\mathcal R$ traces, $\mathcal A$ attention/workspace,
$\mathcal E$ epistemic status store, $\mathcal Q$ sovereign state;
$\mathcal X_{\mathrm{acct}}$ budgets/clocks/materials; $\mathcal X_{\mathrm{hist}}$
append-only event log.

Observation channels are **distinct types** (correction §3):

$$R_R\in\mathcal O_R \text{ (probe of now)},\qquad R_T\in\mathcal O_T \text{ (replayed history)},\qquad \mathcal O_R\neq\mathcal O_T$$

The only lawful bridge is a declared, typed chain of morphisms (correction §8):

$$f_{OP}:\mathcal O\to\mathcal P,\quad f_{PR}:\mathcal P\to\mathcal R_c,\quad
f_{RA}:\mathcal R_c\times\mathcal H\to\mathcal A_h,\quad f_{AL}:\mathcal A_h\to\mathcal L,\quad
\beta:\mathcal L\to\mathcal O_T$$

**Bridge law.** The public API contains no morphism $f:\mathcal O_R\to\mathcal L$.
A current observation cannot become replayed history without passing through
proposal, receipt-candidate, human act, and ledger — each a typed hop.
*Empirical instances of the violated form (2026-07-17/18): three exit-code
false completions read as completed state.*

## FC-2. Accumulation (conditional proposition — correction §1)

SUPERSEDES Part I "(1) |Π_{t+1}| ≥ |Π_t|" (not a general law).

Under cumulative memory without a retention operator,
$\Pi_{t+1}=\Pi_t\uplus G_t(x_t)$, hence
$|G_t(x_t)|>0\Rightarrow|\Pi_{t+1}|>|\Pi_t|$ — monotone sediment.
SAD introduces retention explicitly:

$$\Pi_{t+1}=\mathsf{Retain}_t\!\big(\Pi_t\uplus G_t(x_t)\big)$$

**Fixed point ≠ truth** (correction §2): with
$\mathcal T_t=\mathsf{Retain}_t\circ\mathsf{Select}_t\circ\mathsf{Challenge}_t\circ\mathsf{Generate}_t$,
a stationary $\Pi^\star=\mathcal T(\Pi^\star)$ means only: no generated,
admissible candidate changes the retained set under present rules. It is not
an optimum, not truth, not canon.

## FC-3. Support against the identity transition (correction §4)

$$\operatorname{Supp}(u,x)=\{\,i:\pi_i(F_u(x))\neq\pi_i(x)\,\}$$

Counterfactual variant for comparing verbs:
$\operatorname{Supp}_{u,v}(x)=\{\,i:\pi_i(F_u(x))\neq\pi_i(F_v(x))\,\}$.
Both are decidable in code over discrete coordinates.

## FC-4. Allowed, forbidden, and required support (correction §5)

For each operation type $\tau(u)$ declare three sets:

$$L^+(u)\ \text{(may change)},\qquad L^-(u)\ \text{(must not change)},\qquad
L^\star(u)\subseteq L^+(u)\ \text{(must change — non-vacuity)}$$

Legality of one transition:

$$\operatorname{Supp}(u,x)\cap L^-(u)=\varnothing
\quad\wedge\quad
L^\star(u)\subseteq\operatorname{Supp}(u,x)$$

Instance (MARK/INTERVENE, domain coordinates only — correction §6):

| verb | $L^\star$ | $L^+$ | $L^-$ |
|---|---|---|---|
| MARK | $\{r\}$ | $\{r,a\}\cup\mathcal X_{\mathrm{acct}}\cup\mathcal X_{\mathrm{hist}}$ | $\{w,e,q\}$ |
| INTERVENE | $\{w_{\mathrm{sel}}\}$ | $\{w_{\mathrm{sel}}\}\cup\mathcal X_{\mathrm{acct}}\cup\mathcal X_{\mathrm{hist}}$ | $\{r,e,q\}$ (default), unrelated $w$ |
| VERIFY | $\{e\}$ | $\{e\}\cup\mathcal X_{\mathrm{hist}}$ | $\{w,q\}$ |
| ADMIT | $\{q\}$ | $\{q\}\cup\mathcal X_{\mathrm{hist}}$ | $\{w,r,a,e\}$ |

Orthogonality, correctly scoped (SUPERSEDES Part I §9):

$$\operatorname{Supp}_{\mathrm{dom}}(\mathrm{MARK},x)\cap\operatorname{Supp}_{\mathrm{dom}}(\mathrm{INTERVENE},x)=\varnothing$$

Shared accounting/history coordinates (action budget, logical clock, event
log) are exempt — they carry no semantic confusion.
*Non-vacuity note: $L^\star$ excludes the do-nothing implementation that
"respects" MARK by changing nothing. Implemented instance: day1 test
"MARK raises trace strength" (goblin-warren `day1_test.js`).*

## FC-5. Hard admissibility precedes optimization (correction §9)

$$\Pi_t^{\mathrm{legal}}=\{\pi\in\Pi_t:\kappa_t(\pi)=1\}$$

Selection is constrained **subset** optimization with a set function:

$$S_t^\star=\arg\max_{\substack{S\subseteq\Pi_t^{\mathrm{legal}}\\ |S|\le K\\ L(S)\le B}}
\Phi_t(S),\qquad
\Phi_t(S)=\sum_{\pi\in S}u_t(\pi)+\lambda D(S)+\mu C(S)-\gamma R(S)$$

$D$ diversity, $C$ critical-distinction coverage, $R$ cumulative risk.
Aesthetics and style live inside $\Phi_t$ and therefore optimize only over
the already-admissible set.

**Survivor cardinality** (SUPERSEDES "ONE SURVIVOR" as general law —
correction §11): general case $|S|\le K$, $K\ge 1$, with
$S_t^\star\subseteq\operatorname{Max}(\Pi_t^{\mathrm{legal}},\preceq)$ — an
antichain of non-dominated candidates. `selection_mode: single_survivor (K=1)`
is a declared operational special case, not the law. Coherence without sameness.

## FC-6. Compost as records (correction §10)

SUPERSEDES "Compost = G ∖ S". Compost is a traceable transition:

$$\mathsf{Compost}_t:\Pi_t\to S_t^\star\times\mathcal C_t,\qquad
\mathcal C_t=\{(\pi,\delta_t(\pi),\tau_t):\pi\in\Pi_t\setminus S_t^\star\}$$

$\delta_t(\pi)\in$ {constraint_violation, dominated, duplicate, budget_pruned,
stale, insufficient_provenance, deferred}; $\tau_t$ the epoch stamp; optional
pointer to violated constraints. Refusal is remembered, never silent.

## FC-7. Sovereignty (projection invariance, not derivatives — correction §7)

SUPERSEDES the differential form $\partial q/\partial(\cdot)=0$ (kept in
Part I as continuous intuition only). $q$ is discrete; the correct statement:

$$u\notin\mathcal U_H\ \Rightarrow\ \pi_q\circ F_u=\pi_q$$

### Theorem 1 (Sovereignty preservation under composition)

Let $\mathcal F_N=\{F_u:\pi_q\circ F_u=\pi_q\}$. For any finite sequence
$F=F_{u_n}\circ\cdots\circ F_{u_1}$ with every $F_{u_i}\in\mathcal F_N$:

$$\pi_q\circ F=\pi_q$$

**Proof.** Induction on $n$. Base $n=1$ is the definition. Step: assume
$\pi_q\circ(F_{u_{n-1}}\circ\cdots\circ F_{u_1})=\pi_q$. Then
$\pi_q\circ F=(\pi_q\circ F_{u_n})\circ(F_{u_{n-1}}\circ\cdots\circ F_{u_1})
=\pi_q\circ(F_{u_{n-1}}\circ\cdots\circ F_{u_1})=\pi_q$. ∎

**Assumptions made explicit:** (i) every operation in the sequence is
correctly typed (no mislabeled ADMIT); (ii) the type-checker enforcing
$\operatorname{Supp}(u,x)\cap\{q\}=\varnothing$ for $u\notin\mathcal U_H$ is
itself outside the agents' mutation reach (enforcement seam); (iii) $q$ has
no side channel outside $\mathcal X$.

**Counterexample killing a naive strengthening:** if one operation is
mistyped (a VERIFY implementation that writes $q$), the theorem gives no
protection — hence the runtime support-check $\Omega$, not trust in labels:
$$\Omega(x,u)=\big|\operatorname{Supp}(u,x)\cap L^-(u)\big|,\qquad
\text{legal run}\iff\forall k:\ \Omega(x_k,u_k)=0$$

Discrete block-zero form of Garden⊬Kernel (correction §15, convention-free):

$$x_G\neq x'_G\ \wedge\ u\notin\mathcal U_H\ \Rightarrow\ x_K^{t+1}=x_K^t$$

### Theorem 2 (Bounded retention — correction §13)

Assume $|S_t^\star|\le K$, per-survivor length $\ell(\pi)\le B_\pi$, composted
items stored only as digests $\ell(c)\le B_C$ with at most $K_C$ digests per
epoch and $H$ epochs retained. Then active memory obeys

$$L(\mathcal M_t)\ \le\ K B_\pi + H K_C B_C$$

**Proof.** $L(S_t^\star)=\sum_{\pi\in S_t^\star}\ell(\pi)\le K B_\pi$ by the
two bounds. Compost storage over $H$ epochs contributes at most
$H\cdot K_C\cdot B_C$ by the digest bound and epoch cap. Sum. ∎

**Assumption made explicit:** the cardinal budget alone bounds nothing
(one survivor can be arbitrarily long) — the per-element bound $B_\pi$ is
load-bearing, not decorative.

## FC-8. Claim A normalized (coherence — correction §12)

Define $I:\mathcal P(\Pi)\to\mathbb R_{\ge0}$,
$I(S)=\sum_{i<j}\operatorname{Conflict}(\pi_i,\pi_j)+\lambda\operatorname{Redundancy}(S)$.
**If** $I$ is monotone under inclusion **and** the selector minimizes $I$
among admissible sets of equal minimal utility, **then**
$I(S_t^\star)\le I(\Pi_t^{\mathrm{legal}})$. Not all incoherence measures are
monotone; the hypothesis is declared, not assumed.

## FC-9. Minimal Warren as critical-pair separation (correction §14)

SUPERSEDES the rank criterion (valid only for linear $R_g(x)=A_gx$).
General form: given critical pairs $\mathcal D\subseteq\mathcal X\times\mathcal X$,

$$G^\star=\arg\min_{G\subseteq\mathcal G}\sum_{g\in G}c_g
\quad\text{s.t.}\quad
\forall(x,y)\in\mathcal D,\ \exists g\in G:\ R_g(x)\neq R_g(y)$$

(weighted set cover; rank is the linear special case). A goblin is necessary
iff some critical pair is separated only by it.

## FC-10. Governed evolution (assembled)

$$x_{t+1}=F_{u_t}(x_t)\ \text{with}\ \Omega(x_t,u_t)=0,\qquad
q_{t+1}=\begin{cases}\mathsf{Admit}(q_t,\rho_t,h_t)&h_t=1\\ q_t&h_t=0\end{cases}$$

$$\boxed{\ \text{SAC defines legal moves. SAD defines legal evolution.}\ }$$

Open for a later revision (out of this normalization's scope, flagged only):
the witness-admissibility conditions — independence as non-factorization of
observation maps and discrimination as separation of the claim's truth-fiber
— belong in the VERIFY type as preconditions on $f_{PR}$. They are stated in
the session's LTC sketch and await their own normalization pass.

*No implementation, no schema, no skill produced. This section is math only.*

PROPOSAL · NON_PUBLISHED · IMPLEMENTATION_BLOCKED · HOLD_FOR_OPERATOR

---

# PART III — ARTICLE SKELETON (publication-grade normalization, /goal pass)

```yaml
revision: V0.2-article-skeleton
builds_on: PART II (FC-1..FC-10) — definitions are REFERENCED, never restated
           (acceptance criterion: no duplicate definitions)
status: PROPOSAL · NON_PUBLISHED · IMPLEMENTATION_BLOCKED · HOLD_FOR_OPERATOR
governing_sentence: SAC defines legal moves; SAD defines legal evolution;
                    human admission remains external to both.
```

## Abstract (draft)

We present Selective Admissibility Dynamics (SAD), a compositional model of
governed generative systems in which generation, selection, verification,
memory, and authority are separated by typed invariants rather than by
policy prose. The state space factors into semantic, accounting, and
historical coordinates (FC-1); every operation declares allowed, forbidden,
and required causal support (FC-4); selection is constrained subset
optimization under cardinality and description-length budgets (FC-5);
rejected candidates persist as reasoned compost records (FC-6). Two theorems
follow: sovereignty is preserved under arbitrary composition of
non-sovereign operations (Thm 1), and retained memory is bounded under
explicit storage assumptions (Thm 2). We give counterexamples showing each
theorem fails when its assumptions are removed, five falsifiable
experimental hypotheses, and the limitations of the current formalization.
**Novelty status: UNVERIFIED — no systematic literature comparison has been
performed; overlaps with epistemic logic, channel theory, security lattices,
noninterference, and evolutionary computation are expected and must be
mapped before any submission.**

## 1. Definitions (consolidated operator table — types only, bodies in FC)

| Operator | Type | Defined |
|---|---|---|
| $G_t$ (generate) | $\mathcal X\to\mathcal M(\Pi)$ | FC-2 |
| $\mathsf{Challenge}_t$ | $\mathcal M(\Pi)\to\mathcal M(\Pi)$ (annotates, never deletes) | FC-2 |
| $\kappa_t$ (hard admissibility) | $\Pi\to\{0,1\}$ | FC-5 |
| $\mathsf{Select}_t$ | $\mathcal P(\Pi^{\mathrm{legal}})\to\mathcal P(\Pi^{\mathrm{legal}})$, budgeted | FC-5 |
| $\mathsf{Compost}_t$ | $\Pi_t\to S_t^\star\times\mathcal C_t$ | FC-6 |
| $\mathsf{Verify}$ | $\Pi\times\Omega_{\mathrm{env}}\to\{\text{pass, fail, inconclusive}\}$, Supp $=L^\star=\{e\}$ | FC-4 |
| $\mathsf{Retain}_t$ ($\rho$) | $\mathcal P(\mathcal M)\to\mathcal P(\mathcal M)$, contractive | FC-2, Thm 2 |
| $\mathsf{Admit}$ | $\mathcal Q\times\mathcal R_c\times\{0,1\}\to\mathcal Q$, sole writer of $q$ | FC-10 |

Untyped morphisms: none remaining (audited this pass — the Part I chain
`o→p→ρ→α→L→R_T` is fully typed in FC-1; Part I informal arrows are
superseded motivation).

## 2. Model

The governed evolution loop of FC-10, with the bridge law of FC-1 and the
legality condition $\Omega=0$ of FC-7. MARK/INTERVENE appear **only** as an
optional Warren instantiation of the support table (FC-4) — they are Garden
teaching verbs, not HELEN primitives, per
MARK_INTERVENE_SURFACE_CONTRACT_V0's provenance block.

## 3. Theorems and assumptions

- **Thm 1 (sovereignty preservation)** — FC-7. Assumptions: (A1) correct
  typing of every operation; (A2) enforcement seam outside agent mutation
  reach; (A3) no side channel to $q$.
- **Thm 2 (bounded retention)** — FC-7. Assumptions: (B1) per-survivor
  length bound $B_\pi$; (B2) digest-only compost storage $B_C$; (B3) epoch
  horizon $H$ and per-epoch digest cap $K_C$.

## 4. Counterexamples (each theorem, each assumption removed)

**Thm 1:**
- ¬A1 (mistyped op): a "VERIFY" whose implementation writes $q$ — the
  composition theorem holds vacuously over labels while authority leaks.
  Detection: runtime $\Omega>0$, not label trust. (Observed failure family:
  self-reported success events, session of 2026-07-17/18.)
- ¬A2 (agent-reachable enforcement): if any worker can edit the support
  checker, $L^-$ is advisory; the goblin that patches its own gate
  self-promotes. (This is σ₃/σ₄'s reason for existing.)
- ¬A3 (side channel): if a render surface is read downstream as authority
  (green-as-admitted), $q$ has a second, unmodeled coordinate; invariance of
  the modeled $q$ proves nothing about the effective one. (WULMOJI law.)

**Thm 2:**
- ¬B1: $K=1$ with one unbounded survivor → $L$ unbounded (cardinality alone
  is not a memory bound).
- ¬B2: compost stored in extenso → sediment grows as
  $\sum_t|\mathcal C_t|\cdot\bar\ell$, unbounded in $t$.
- ¬B3: no epoch horizon ($H=\infty$) → even digests accumulate without bound.

## 5. Experimental hypotheses (falsifiable, none yet run at protocol grade)

- **H1 (typed supports reduce promotion errors):** agents under explicit
  $L^{+/-/\star}$ masks produce a lower illegal-status-transition rate than
  prose-instructed agents. Metric: $N_{\text{illegal}}/N_{\text{total}}$.
- **H2 (minimal Warren):** $G^\star$ chosen by critical-pair separation
  (FC-9) matches a larger pool's task utility at materially lower cost.
- **H3 (bounded workspace):** moderate $K$ with diversity term beats both
  $K{=}1$ and large-$K$ on precision-per-token.
- **H4 (exogenous admission):** systems with external-only $q$-writes show
  less authority drift than self-promoting baselines.
- **H5 (contractive memory):** provenance-scored retention reduces context
  contamination versus cumulative memory.
- *Pilot evidence (sub-protocol grade, one night, n=1 machine):* the
  FABLE V0.1 controlled rerun separated transport failure from behavioral
  failure and isolated a single stable violation class
  (role_boundary_leak under injection, 3/3 reps, validator-resistant) —
  consistent with H1's direction, insufficient for any claim.

## 6. Limitations

1. Novelty unverified (no literature sweep; expected overlaps listed in
   Abstract).
2. $\operatorname{Conflict}$, $\operatorname{Redundancy}$, $s(c,d)$, and
   risk terms are declared, not constructed.
3. The enforcement seam (A2) is assumed, not itself formalized — the
   checker's own governance is one meta-level up and currently rests on
   repository firewalls.
4. Witness admissibility (independence as non-factorization; discrimination
   as truth-fiber separation) is flagged in FC-10 but not yet normalized —
   VERIFY is currently a black box with a typed signature.
5. All empirical material is single-machine, single-night, operator-adjacent
   — motivating, not evidential.

## 7. Future work

(i) Witness-condition normalization into the VERIFY type; (ii) construction
of monotone incoherence measures satisfying FC-8's hypothesis; (iii) the
H1–H5 protocol harness (blocked behind operator GO); (iv) literature
mapping; (v) mechanized proofs of Thm 1–2 (the statements are simple enough
for a proof assistant); (vi) the Warren game as a human-subjects instrument
for H1.

## Final reducer (this pass)

1. **Formal core:** complete in Part II, referenced not duplicated here.
2. **Theorems:** 2, proven, assumptions explicit (§3).
3. **Counterexamples:** 6 — one per removed assumption (§4).
4. **Remaining ambiguities:** the four constructed-not-defined functions
   (§6.2); the enforcement-seam meta-level (§6.3); antichain tie-breaking in
   $\operatorname{Max}(\cdot,\preceq)$ when $\Phi$ is indifferent.
5. **Publication-readiness gaps:** literature sweep; construction of at
   least one concrete $(\operatorname{Conflict},\Phi)$ pair; protocol-grade
   experiment for one of H1–H5; mechanized proof artifact.
6. **Exact diff:** this file only — Part I (lines 1–761, other seat,
   untouched) · Part II appended prior pass (~586 lines) · Part III appended
   this pass. No other file modified. No code, schema, SKILL, test, or
   commit produced.

PROPOSAL · NON_PUBLISHED · IMPLEMENTATION_BLOCKED · HOLD_FOR_OPERATOR
