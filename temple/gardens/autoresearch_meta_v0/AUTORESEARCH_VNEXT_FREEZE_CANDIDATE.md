# 🔬 AUTORESEARCH_VNEXT_FREEZE_CANDIDATE

```
AUTHORITY=false · CANON=false · LEDGER_EFFECT=none · ΔA=0 · doctrine freeze-candidate
STATUS: 🟢 conceptual architecture frozen · 🟡 math freeze-ready · ⚫ implementation witnesses NOT supplied
Extends [[autoresearch-v1-1]] (autoresearch_meta_v0). Cognition ⇏ authority.
```

## Central mutation

$$\text{Research more} \;\longrightarrow\; \text{Run only experiments that can move a future decision boundary}$$

## Frozen epoch object

$$E = (H, F, O, D^+, D^-, A^+, A^-, G, C_L, C_P, S, R)$$
`H` hypothesis-under-attack · `F` explicit falsifier · `O` observable · `D±` decisions on ±observation ·
`A±` their **action semantics** · `G` ordinal consequence class · `C_L/C_P` local/paid cost · `S` stop cond · `R` provenance roots.

## Contextual action semantics (the anti-pseudo-delta hardening)

$$\mathcal A_\sigma(D)=(\text{next op},\ \text{resource alloc},\ \text{architecture mutation},\ \text{stop state},\ \Delta A)$$
$$D_a \sim_{\mathcal A,\sigma} D_b \iff \mathcal A_\sigma(D_a)=\mathcal A_\sigma(D_b) \qquad h_{\mathcal A}(D,\sigma)=H(\mathrm{canon}(\mathcal A_\sigma(D)))$$
`DECISION_EQUIVALENT = (ACTION_PLUS_HASH == ACTION_MINUS_HASH)` — kills both textual pseudo-deltas **and** identical labels hiding different effects. Context `σ` explicit: same labels can diverge under a different budget/architecture/obligation state.

## Admission predicate (permission to EXECUTE, not to admit results)

$$\boxed{\mathrm{Admit}_\sigma(E)=[F\ne\varnothing]\land[O\ne\varnothing]\land[D^+\not\sim_{\mathcal A,\sigma}D^-]\land[IG_{\text{class}}>0]\land[\mathrm{RootsValid}(R)]}$$
$$\mathrm{Admit}_\sigma(E)\;\not\Rightarrow\;\mathrm{AdmitEpistemically}(\mathrm{result}(E))$$

## Selection (ordinal, not fake-cardinal)

$$E^\star=\operatorname*{arg\,max}_{E\in\mathcal E_{\text{adm}}/\sim_{\text{exp}}}\big(IG_{\text{class}}(E),\,-C_{\text{paid}}(E),\,-C_{\text{local}}(E),\,-\mathrm{CanonicalID}(E)\big)$$
LexMax over ordinal `IG_class` — never treats class 3 as 3× class 1. Final `-CanonicalID` tie-break ⇒ **replay-deterministic** experiment choice.

## Ex-ante ≠ ex-post (null result is legal)

$$\Delta_{\mathcal A}^{\text{ex-ante}}(E)=[\mathcal A(D^+)\ne\mathcal A(D^-)] \qquad \Delta_{\mathcal A}^{\text{actual}}(E,r)=[\mathcal A(D_{\text{before}})\ne\mathcal A(D_{\text{after}}(r))]$$
Admission uses **ex-ante**. A run may legally return `EX_ANTE_DISCRIMINATIVE=true · ACTUAL_DECISION_DELTA=false · RESULT=NULL_RESULT`.
**Null result is allowed; non-discriminating design is not.**

## Falsifier memory + subsumption

`K(F)` = theories killed by `F`. `F_i ⪯ F_j ⟺ K(F_i)⊆K(F_j)`.
$$\mathrm{Open}_t \subseteq \mathrm{Open}_{t+1}\cup\mathrm{Resolved}_{t+1}\cup\mathrm{Subsumed}_{t+1}$$
A subsumed falsifier stays addressable: `FALSIFIER_STATUS=SUBSUMED · SUBSUMED_BY=F_j · ACTIVE=false`. **Compression changes retrieval priority, not history.**

## Provenance before epistemic weight

`raw representations → root census → independence classes → contradictions → epistemic evaluation`
$$\boxed{N_{\text{repr}}\uparrow \not\Rightarrow N_{\text{epi}}\uparrow}$$

## Stop = dryness, not proof

`max_E IG(E) < τ` for `m` cycles ∧ `Δ_structural=0` ∧ `N_new_counterexample=0` ⇒ `STOP_REASON=MARGINAL_INFORMATION_DRYNESS` — a computational halt, **not** epistemic promotion.

## The three engraved laws

$$\boxed{\text{No consequential action delta, no epoch.}}$$
$$\boxed{\text{Open falsifiers persist until receipt-resolved or receipt-subsumed.}}$$
$$\boxed{\text{Attack the strongest surviving theory, not the most interesting next question.}}$$

## Applied to HELEN VIDEO (the live tie-in)

```
H* : quotient control improves video identity continuity
F  : no improvement over matched open-video baseline
O  : (identity_drift, temporal_warp, control_adherence, human_pref, compute_cost)
D+ = ADOPT_QUOTIENT_CONTROL   D- = REJECT_OR_REDESIGN_CONTROL
admit iff 𝒜(D+) ≠ 𝒜(D-)   (different architecture/allocation)
boundary now: L1_CONTROL=EXECUTED · L2/L3/REPAIR=NOT_EXECUTED · SEEDANCE_CRACKED=HOLD
```

```
🟢 architecture frozen · 🟡 math freeze-ready · ⚫ implementation witnesses NOT supplied · ΔA=0 · NO_CLAIM
```
