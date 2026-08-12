# Corpus Reachability Map V0 — what this seat can actually chiddush

`authority=false · claim=NO_CLAIM · non-sovereign` · probed 2026-08-12,
every entry below is an executed receipt, not an assumption.

## Doors that WORK (proven this session)

| Door | Mechanism | Proof | Grade of what it yields |
|---|---|---|---|
| **WebSearch** | server-side, not on this proxy | returned real IA identifiers for Repertory volumes | titles/URLs/snippets — REPORTED, shallow |
| **HF `hf_fs`** (MCP, server-side) | cat/ls/find/search over hf:// | read blbooks README, listed LFS shards | full TEXT files at byte offsets; **binary (parquet/gz) unreadable** |
| **HF `hf://papers`** | arXiv papers as markdown | per tool contract | full-text papers |
| **Package registries** | pypi/npm/crates/go/jsr are in the proxy's noProxy list | AntV tarball fetched earlier via npm | tooling, not corpora |
| **Google Drive / Gmail MCP** | server-side, operator's account | untested this session, tool present | **the intake channel**: operator drops files, this seat reads |
| **WebFetch of claude.ai artifacts** | documented exception | — | own artifacts only |
| **In-frame relay** | operator pastes text/images | ATF specimens, CP frames, 40-case corpus | REPORTED — the workhorse so far |

## Doors that are CLOSED (receipts)

- curl to anything non-registry: CONNECT 403 (archive.org, wikisource,
  gutenberg, hathitrust, ARTFL, quod.lib, wellcome — all tested).
- **WebFetch rides the same egress policy**: `EGRESS_BLOCKED` for
  gutenberg.org and archive.org (tested 2026-08-12). Search sees;
  fetch may not.
- GitHub MCP: scoped to jmtassy/goblin-warren only. Not a corpus door.
- HF binary formats: blbooks is parquet (61 x ~250MB LFS),
  common-pile/project_gutenberg is jsonl.gz — cat cannot serve them,
  and huggingface.co is proxy-blocked for local download.

## What was FOUND behind the open doors

- **Repertory of Patent Inventions volumes exist on IA** with exact
  identifiers (e.g. `in.ernet.dli.2015.21576` = Vol 16, 1841;
  `repertorypatent20unkngoog`; `B-001-003-460`) — located via
  WebSearch, unfetchable from here. These are the ladder's rung-2
  corpus, one Drive-upload away.
- **TheBritishLibrary/blbooks (14M pages, 1500–1899, OCR text)** sits
  on HF — potentially containing Repertory volumes, jury-report
  editions, railway materials — but only in parquet. A server-side
  query route (HF Space running SQL over it) was not found in one
  search; building/finding one is an open door worth an hour.

## Ranked chiddush routes (proactive recommendations)

1. **Drive intake** — the operator downloads the WebSearch-located IA
   volumes and drops them in Google Drive; this seat reads them
   server-side. Note the SEAT LAW: Repertory frames may be read HERE
   for descriptive K_1850 work, but backtest *predictions* against the
   1851 holdout still require a fresh seat.
2. **WebSearch snippet harvesting** — usable now for locating and
   shallow-witnessing (identifiers, dates, titles); never for deep
   frames. Density of snippets is Γ, not A.
3. **hf://papers** — any arXiv-adjacent theory relay can be
   full-text-witnessed instead of REPORTED.
4. **A blbooks query Space** — one dedicated HF Space (duckdb over the
   parquet) would make 14M BL pages searchable server-side. Highest
   ceiling, needs building or finding.
