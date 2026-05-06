# HELEN Operator Guide V1

Authority: NON_SOVEREIGN
Canon: NO_SHIP until fully expanded
Status: OPERATOR_REFERENCE_DRAFT
Date: 2026-05-06

## 1. Boot HELEN

Run:
cd ~/helen-conquest
source .venv/bin/activate

## 2. Speak to HELEN

Run:
helen "MESSAGE"

## 3. Run semantic dashboard

Run:
.venv/bin/python tools/helen_semantic_dashboard.py

Open:
http://localhost:5003
http://192.168.1.101:5003

Use http, not https.

## 4. Run authority audit

Run:
.venv/bin/python tools/audit_authority.py

## 5. Run K-tau lint

Run:
.venv/bin/python scripts/helen_k_tau_lint.py

## 6. Run K8 lint

Run:
.venv/bin/python scripts/helen_k8_lint.py --mode all_nd

## 7. Run tests

Run:
make test
.venv/bin/pytest tests/test_helen_computer_use_api.py -q

## 8. Git safety

Before switching branches:
git status -sb

If only ledger changed:
git stash push -m "ledger-receipts" -- town/ledger_v1.ndjson

## 9. Dashboard terminal rule

When Flask dashboard is running, that terminal is occupied.
Use CMD+T for a second terminal.

## 10. HELEN message rule

Do not type plain summaries into zsh.
Wrap witness messages:
helen "your message"

## 11. HTTP rule

Local dashboard is HTTP only.
If iPhone tries HTTPS, Flask logs bad request bytes.

## 12. Runtime artifacts

K8 and K-tau runtime artifacts are ignored in .gitignore.

## 13. Current known failures

F-010: NDWRAP violation in hyperframes meditation generator.
F-011: missing provenance sidecars for 3 HELEN director reference images.

## 14. Operator doctrine

No receipt -> no ship.
Dashboard observes.
Ledger remembers.
Reducer decides.
