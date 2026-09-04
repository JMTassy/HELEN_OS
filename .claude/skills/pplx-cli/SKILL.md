---
name: pplx-cli
description: >
  Install and use Perplexity's pplx CLI for live web search and page-content fetch
  from the terminal. Use to search the web, look up current information or news,
  fetch a URL's content as text, or install and authenticate the pplx command.
  Triggers: search the web, find latest news, use Perplexity, pplx search, install
  pplx CLI, fetch this URL, read this webpage, restrict web search to domains/dates.
---

# pplx — Perplexity web search & content-fetch CLI

## What this skill does

Installs, authenticates, and drives Perplexity's public `pplx` CLI:

- `pplx search web` — live web search
- `pplx content fetch` — page content as text

**Output contract:** success = exit 0 and exactly one JSON object on stdout. Failures: exit 1, empty stdout, one JSON error object on **stderr**.

## Install

Skip if `pplx --version` already works (calver like `2026.07.23.1784784046+c8b317a`).

```sh
curl -fsSL https://github.com/perplexityai/perplexity-cli/releases/latest/download/install.sh | sh
```

- SHA-256-verified, no sudo → `~/.local/bin/pplx` (override: `PPLX_INSTALL_PATH`)
- Ensure `~/.local/bin` is on `PATH`
- Platforms: macOS arm64, Linux x86_64, Linux arm64 only
- Update: `pplx update` · check only: `pplx update --check`

## Auth

- Interactive: `pplx auth login` (TTY only; keys: https://www.perplexity.ai/account/api)
- **Agents / CI:** set `PERPLEXITY_API_KEY` — do **not** use `auth login` non-interactively
- Env var beats stored credentials (`~/Library/Application Support/perplexity/credentials.json` on macOS)
- No key → `AUTHENTICATION` error on first real command

## Search

```sh
pplx search web "kubernetes pod OOMKilled causes"
```

Stdout: `{hits: [{url, title, domain, snippet?, ...}], total, saved_to?}`.

Save-and-preview (keep tokens down):

```sh
pplx search web "kubernetes pod OOMKilled causes" "why does k8s keep killing my pod with OOMKilled" \
  -n 5 --output-dir out --stdout-preview=200
```

- Full JSON at `out/web/{rand}.json` when `--output-dir` / `$PPLX_OUTPUT_DIR` is set
- Extra positionals = **reformulations of the same question**, not separate topics
- Scoping: `pplx search web --help` (`--domains`, date bounds, `--recency-filter`, `--country`)

## Fetch

```sh
pplx content fetch https://example.com/article
```

- http(s) only
- **Check `error` and `is_paywall` before trusting `content`**
- `--no-cache` for live fetch; `--html` adds large `raw_html` (pair with `--output-dir` + `--stdout-preview`)

## When unsure

Every subcommand's `--help` has Input/Stdout/Saved schemas and examples.

## Top pitfalls

1. **`pplx auth login` is TTY-only** — agents use `PERPLEXITY_API_KEY`
2. **`--stdout-preview` needs a save dir** or it is a no-op
3. **Extra positionals = same-query reformulations** — N topics = N invocations
4. **Failures: stderr JSON, empty stdout, exit 1** — parse `error.code`
5. **Date flags: MM/DD/YYYY**, not ISO
6. **Don't combine `--recency-filter` with published-after/before-date**

## Agent workflow

1. Prefer `export PATH="$HOME/.local/bin:$PATH"` in shell sessions
2. Prefer `PPLX_OUTPUT_DIR` under the workspace for saves
3. On failure, read stderr JSON; do not invent hits
4. Cite URLs from `hits[].url` when answering the user
