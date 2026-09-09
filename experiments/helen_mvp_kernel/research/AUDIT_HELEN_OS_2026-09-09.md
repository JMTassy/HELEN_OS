# Security audit — JMTassy/helen-os @ f37737c

Read-only audit. **No file in `helen-os` was modified.** Shallow clone
of `main` at `f37737cfbdc3998f25f4cd77729924197faa0d73`.

## Grading

- **VERIFIED** — read in the source at that commit, file:line given.
- **REPORTED** — asserted by the repo's own docs; the running system
  was NOT inspected. I have no access to the Cloud Run / Railway
  console, so no claim here describes live deployment state.

## Correction to my first reading

From the README alone I said the router violated
`the_gateway_decides_and_the_app_never_names` (law 077). Reading the
code, that was too harsh. `app.py` carries the constitutional
vocabulary throughout — `authority: NONE` on non-sovereign responses,
`authority_class` on registry entries, an explicit
`constitutional_invariant` string, shell execution refused by name at
`app.py:1797`. The discipline **is** present in this repo.

That makes the findings below more surprising, not less: the
vocabulary of admission is there, and the *checks* are self-declared.

---

## F1 — CRITICAL · no caller authentication, wide-open CORS

**VERIFIED** `app.py:92` — `CORS(app)` with no `origins` argument, i.e.
`Access-Control-Allow-Origin: *` on every route. No `before_request`,
no API-key check, no `401` anywhere in the file: the only `403`s are
the role checks in F2.

Consequences, given provider keys are read from the environment
(`app.py:420,455,494`):

1. `/chat` and `/v1/chat/completions` are an **open proxy to the
   owner's paid Anthropic / OpenAI / Google / xAI / Qwen accounts** for
   anyone who can reach the host.
2. Writes are **durable**: memory persists to SQLite
   (`helen_os/memory/_memory_spine.py:19,111`), so unauthenticated
   `POST /memory/items`, `POST /threads`, `POST /sessions` and
   `POST /corpus/mutate` reach disk.

Law: `no ambient authority` (084).

## F2 — HIGH · the privileged actor is supplied by the caller

**VERIFIED** three occurrences, identical shape:

| endpoint | line |
|---|---|
| `POST /threads/<id>/promote` | `app.py:1662` |
| `POST /memory/items/<id>/promote` | `app.py:1713` |
| `POST /corpus/mutate` | `app.py:1145` |

```python
actor = data.get("actor", "")
if actor not in {"MAYOR", "SYSTEM"}:
    return jsonify({"error": "Only MAYOR or SYSTEM may promote"}), 403
```

The role is read from the request body. `-d '{"actor":"MAYOR"}'`
passes. The gate refuses only callers who decline to claim the role.

The storage layer re-checks (`_memory_spine.py:206`,
`VALID_ACTORS = {"MAYOR","SYSTEM"}` at :106) — but against the *same
self-declared string*. That is defence against a typo, not against a
caller.

Law: `the_grantor_may_not_be_the_grantee` (076). The requester mints
its own authority.

## F3 — HIGH · the approval gate returns the requester's own approval

**VERIFIED** `app.py:1818-1839`.

`POST /v1/computer-action/propose` documents the rule correctly:
*"HELEN may propose. Only user approval + reducer validation may
execute."* Then:

```python
approved = data.get("user_approval", False)
...
"execution_ready": approved,
```

`/v1/computer-action/approve` takes `user_approval` from the request
body and returns `execution_ready` equal to it. There is no proposal
store, no check that `proposal_id` was ever issued, and no identity on
the approver. **The party seeking execution supplies the approval.**

**Contained today**: the only consumer of `execution_ready` in the repo
is a test (`tests/test_flask_api.py:201`); nothing executes on it, and
the response carries `authority: NONE`. The severity is what happens
the moment any client treats `execution_ready: true` as a licence.

Laws: `the_grantor_may_not_be_the_grantee` (076),
`executed_without_decision` (030) — EXECUTED and DECIDED collapsed
into one field.

## F4 — MEDIUM · the documented deploy path is not the shipped one

**VERIFIED** no `Dockerfile` at HEAD (a stale `.dockerignore` remains).
The repo ships `Procfile` + `railway.json` (nixpacks, gunicorn). The
README's `docker build -t helen-os .` cannot run as written.

**REPORTED** — from the README's own `gcloud run deploy`, unverified
against any live service:

- `--no-invoker-iam-check` disables the IAM invoker check, i.e. the
  service is invokable without authentication. Combined with F1 there
  is then no gate at any layer.
- `--set-env-vars GOOGLE_API_KEY=...,ANTHROPIC_API_KEY=...` places
  live keys in shell history, and in Cloud Build / audit logs.

Both are unsafe patterns regardless of which deploy path is actually
live. **Which one is live, and its IAM state, I could not check.**

## F5 — INFO

- **No secrets at HEAD.** `git grep` over provider key formats
  (`sk-ant-`, `sk-`, `AIza`, `xai-`, `ghp_`, `github_pat_`, PEM
  headers) returns only two obviously-fake fixtures in
  `tests/test_airi_bridge.py:42,157`. `.env` is gitignored; only
  `.env.template` is tracked. **History was NOT scanned** — the clone
  is `--depth 1`.
- `main` is unprotected (per the repo page).
- 7 PRs open, oldest #1 from 2026-05-17; #2 is "Add HELEN governance
  layer V1", still open after ~4 months.

---

## What would close F1–F3

Not implemented — this was an audit, and the repo was not touched.

1. **One inbound gate before anything else**: a `before_request` that
   requires a caller credential on every route except `/health`, and
   `CORS(app, origins=[...])` narrowed to the actual front-ends.
2. **Derive the actor from that credential, never from the body.**
   `data.get("actor")` must not be the thing the check reads — this is
   the single change that turns F2 from a label into a gate.
3. **Persist proposals.** `/approve` should look up `proposal_id`,
   refuse an unknown one, and refuse when the approving identity is the
   proposing identity. Until an approval is *stored and attributable*,
   `execution_ready` is a mirror.
4. Rotate every provider key that has been passed via `--set-env-vars`,
   and move them to Secret Manager.

## Non-deltas

The running deployments were not inspected: no IAM state, no live URL,
no traffic, no key-usage evidence. Git history was not scanned for
secrets. The 7 open PRs were listed by title only, not reviewed. No
exploitation was attempted against any host — F1–F3 are read from the
source, not demonstrated against a running service.

`authority=false · canon=false · ledger_effect=none`.
