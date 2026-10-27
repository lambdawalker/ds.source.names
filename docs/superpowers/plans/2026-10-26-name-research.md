# Name Research Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver reusable source clients and an evidence-based, resumable name-research runner.

**Architecture:** Independent TypeScript source libraries return source-native evidence without invoking an LLM. The main repository owns the canonical graph, credential service, persistence and DeepSeek Harness tools. A dependency-free Python bootstrap creates companion repositories using the user's local GitHub CLI authentication.

**Tech Stack:** Node.js 24 LTS, TypeScript, native fetch, Zod, Vitest, SQLite, node:crypto, DeepSeek Harness SDK/plugins; Python 3.10+ standard library for bootstrap.

**Spec:** `docs/superpowers/specs/2026-10-26-name-research-design.md`

## Global Constraints

- Source clients target Node.js 24 LTS with native fetch and expose ESM plus TypeScript declarations.
- Repository names in repositories.json are the authoritative bootstrap inventory.
- Secrets stay in a separate source-tool service outside the Harness process; the Harness receives no provider secrets in its environment.
- No npm publishing or package-name availability is assumed.
- MIT source code does not imply MIT data.
- No automatic uploads of research data, package publication or repository deletion.

## Review Focus

- A 403/network failure while probing repositories must never trigger repository creation (Task 0).
- Visually identical spellings from distinct scripts/origins must remain separate identities (Task 1).
- Three Wiktionary-derived results must not be treated as three independent sources (Task 8).
- A damaged vault or failed refresh must preserve the last valid encrypted file (Task 7).
- A stopped job and a quota-exhausted provider must resume without duplicate claims or hidden spend (Tasks 2, 8, 9).

## Repository map and development order

| Order | Repository | Implement or reuse |
|---|---|---|
| 0 | ds.source.names | Bootstrap, documentation and contracts |
| 1 | names.api.wiktionary | Native-fetch WiktAPI client and streaming Kaikki reader; use existing extracted data instead of rebuilding Wiktextract |
| 2 | names.api.wikidata | Thin search/entity/SPARQL client; avoid a generic RDF abstraction |
| 3 | names.api.wikimedia-enterprise | Evaluate official SDK packaging/language fit before a minimal typed adapter |
| 4 | names.api.behindthename | Small documented JSON API wrapper; no website scraping |
| 5 | names.data.statistics | Official-data adapters and importers; no LLM in ingestion |
| 6 | names.api.etymology-explorer | Implement only from verified Vanguard API documentation |
| Optional | names.api.demographics | Thin wrappers for three estimate APIs if needed |
| Final | ds.source.names | Vault/tool service, graph reconciliation, Harness runner and exports |

Use package.json, tsconfig.json, src/index.ts, tests/*.test.ts and README.md in
each source repository. Add package exports and declaration builds. Install only
the runtime dependencies needed by that adapter; native fetch handles HTTP.
Clients receive an injected clock/fetch when needed for deterministic tests.
Develop against sibling checkouts through npm local-path dependencies initially;
keep implementation commits and dependency revisions recorded before release.

## Shared client boundary

Use structural interfaces, not a new shared repository. Each client exports:

```ts
interface ClientOptions {
  fetch?: typeof globalThis.fetch;
  timeoutMs?: number;
  userAgent: string;
}
interface SourceRecord<T> {
  source: string;
  locator: string;
  retrievedAt: string;
  revision?: string;
  upstreamSource?: string;
  data: T;
}
// Each repository exports a source-specific class and error type.
// Errors: authentication | forbidden | not_found | rate_limit | timeout |
//         network | invalid_response | unsupported.
// Preserve retryAfterMs for rate limits; never include credentials in errors.
```

Document timeout/retry defaults per provider from current documentation. Retry
only idempotent/retry-safe calls within bounded attempt/time budgets. The main
application enforces cross-client quotas. Fixtures are synthetic or explicitly
redistributable; do not commit captured private credentials or licensed text.

### Task 0: Repository bootstrap (this change)

**Files:** `repositories.json`, `scripts/create_repositories.py`, `tests/test_create_repositories.py`, `README.md`.

**Interfaces:** manifest -> selected public repository names; CLI -> dry-run or `gh repo create` without a shell.

- [x] Write regression tests for dry-run, optional selection, invalid names, account mismatch, existing repositories, 403/network failure and creation failure.
- [x] Implement Python bootstrap with explicit --apply, auth check, 404-only creation, stop-on-error and rerun support.
- [x] Verify with `python -m unittest discover -s tests -v` and dry-run the real manifest.
- [ ] User runs bootstrap on their computer; verify the created repositories through the GitHub connector.

### Task 1: Canonical contracts and client packaging

**Files (main):** `package.json`, `tsconfig.json`, `src/domain/forms.ts`, `src/domain/claims.ts`, `src/domain/evidence.ts`, `tests/domain.test.ts`.

**Interfaces:** `normalizeSearchKey(input: string): string`; Zod `FormSchema`, `ClaimSchema`, `EvidenceSchema`; `formIdentity(form): string` includes language/script/origin sense and NFC spelling.

- [ ] Write failing tests: accent-folded lookup does not merge José/Jose identities; different scripts and origin senses remain distinct; claims without evidence cannot have supported status.
- [ ] Run `npm test -- tests/domain.test.ts`; implement versioned schemas, relationship enum and validated identities; rerun until green.
- [ ] Add build/declaration exports and synthetic test fixtures in each ready source repository; `npm run build` and `npm test` must pass before committing each deliverable.

### Task 2: Wiktionary clients

**Files (names.api.wiktionary):** `src/client.ts`, `src/kaikki.ts`, `src/index.ts`, `tests/client.test.ts`, `tests/kaikki.test.ts`.

**Interfaces:** `WiktionaryClient.getWord(word, {edition, language?, signal?}): Promise<SourceRecord<WiktEntry[]>>`; `readKaikki(stream: AsyncIterable<Uint8Array>): AsyncGenerator<SourceRecord<WiktEntry>>`.

- [ ] Inspect live personal-name responses and current Kaikki fields; record exact fixtures and upstream attribution without assuming etymology fields always exist.
- [ ] Write failing tests for Unicode query encoding, homographs, missing etymologies, 429/Retry-After, timeouts, malformed JSON and a JSONL record split across byte chunks.
- [ ] Run tests, implement bounded HTTP parsing and streamed decoding; preserve etymology_text/templates, language and upstream lineage. Do not infer edges in this client.
- [ ] Run full tests/build; opt-in live smoke test one entry; commit with documented coverage and reuse terms.

### Task 3: Wikidata client

**Files (names.api.wikidata):** `src/client.ts`, `src/queries.ts`, `src/index.ts`, `tests/client.test.ts`.

**Interfaces:** `searchNames(text, language)`, `getEntities(ids)`, `findBearers(nameQid, {limit})`, each returning typed SourceRecord arrays.

- [ ] Write failing tests for ambiguous name-vs-person results, QID validation, escaped queries, missing P735, language fallback and bounded bearer pagination.
- [ ] Implement search/entity lookups and narrow parameterized SPARQL templates. Return occupation/date/award/image references when present, preserving references and missing values.
- [ ] Assert bearer results are not population counts and sitelink ranking is labeled as a prominence proxy. Run full tests/build and one live smoke test; commit.

### Task 4: Wikimedia Enterprise adapter

**Files (names.api.wikimedia-enterprise):** `docs/sdk-evaluation.md`, `src/auth.ts`, `src/client.ts`, `src/index.ts`, `tests/auth.test.ts`, `tests/client.test.ts`.

**Interfaces:** `login({username,password}) -> TokenSet`; `refresh(refreshToken) -> TokenSet`; client accepts `getAccessToken(): Promise<string>`; `getArticle(title, project)` and streamed snapshot download.

- [ ] Verify current official SDKs and publish a reuse decision. Prefer a maintained suitable SDK; otherwise wrap the documented minimal endpoints with native fetch.
- [ ] Write failing tests for token expiry, single-flight refresh, rejected credentials, project filter encoding, 429 and truncated streamed downloads.
- [ ] Implement typed responses without pretending article JSON is a parsed root graph. Redact all credentials and return streams for large downloads.
- [ ] Run full tests/build and credential-gated smoke tests. Record quota behavior and public-export policy; commit.

### Task 5: Behind the Name adapter

**Files (names.api.behindthename):** `src/client.ts`, `src/index.ts`, `tests/client.test.ts`, `docs/source-policy.md`.

**Interfaces:** `lookup(name, {exact?})`, `related(name)` -> source records. Credentials supplied as `apiKey` client configuration.

- [ ] Review current API display/caching/redistribution terms separately from paid bulk licensing; document allowed operations and unresolved rights.
- [ ] Write failing tests for no meaning/history fields, key redaction in query URLs, diacritics, documented rate windows and error envelopes.
- [ ] Implement supported operations only, including the documented 2/sec, 400/hour, 4,000/day and 400,000/year ceilings as configurable ceilings reverified at implementation.
- [ ] Run full tests/build and key-gated smoke test; keep public export disabled until policy is established; commit.

### Task 6: Official statistics ingestion

**Files (names.data.statistics):** `src/ssa.ts`, `src/insee.ts`, `src/ibge.ts`, `src/types.ts`, `tests/{ssa,insee,ibge}.test.ts`.

**Interfaces:** `readSsa(archiveStream, release)`, `readInsee(stream, releaseSchema)` -> async StatisticRecord; `IbgeClient.frequency(name, filters)` and `ranking(filters)`.

StatisticRecord includes name, geography, period, sex classification, measure,
count/value, suppression/rounding notes, source locator and release version.

- [ ] Verify official download formats, archive dependencies and current IBGE coverage; pin fixture schema versions and source licenses.
- [ ] Write failing tests for malformed archive entries, traversal paths, incomplete downloads, UTF-8 names, changed INSEE headers, suppression and distinctions between births/population/estimates.
- [ ] Implement streaming import, bounded archive handling and atomic import completion; IBGE records must retain documented census vintage.
- [ ] Run full tests/build and a small release import; prove interrupted imports do not appear complete; commit.

### Task 7: Vault and source-tool service

**Files (main):** `src/vault/{crypto,store}.ts`, `src/cli/setup.ts`, `src/tools/service.ts`, `tests/vault.test.ts`, `tests/tool-service.test.ts`.

**Interfaces:** `createVault(path, passphrase, credentials)`, `unlockVault(path, passphrase)`, `updateVault(...)`; `SourceToolService.call(provider, operation, validatedArgs)` -> bounded evidence, never secrets.

- [ ] Write failing tests for wrong passphrase, modified ciphertext, hostile KDF parameters, interrupted replacement and failed refresh preserving old credentials.
- [ ] Implement hidden-input setup, scrypt/AES-GCM versioned envelope, atomic replacement, restrictive file permissions and credential rotation. Reject unsupported vault versions.
- [ ] Write tests for URL/header/query/error secret redaction, unauthorized operations and provider host changes; implement an allowlisted IPC service with no arbitrary fetch/shell interface.
- [ ] Run full tests/build. Verify the Harness child environment and accessible tools contain no provider credentials; commit.

### Task 8: Evidence storage and graph reconciliation

**Files (main):** `src/storage/{migrations,repository}.ts`, `src/research/{reconcile,budgets}.ts`, `tests/storage.test.ts`, `tests/reconcile.test.ts`.

**Interfaces:** `saveEvidence(record)`, `proposeClaim(claim)`, `acceptClaim(id)`, `checkpoint(job)`, `resumeJob(id)`; claim acceptance requires evidence and policy validation.

- [ ] Write failing tests for shared-root vs direct-descent, borrowing vs usage, competing origins, lineage deduplication and idempotent resume.
- [ ] Implement SQLite migrations, transactions, cache TTL/revisions, graph claims and provenance. Persist quota reservations and research stopping reasons.
- [ ] Test Wiktionary + Kaikki + WiktAPI count as one upstream evidence lineage; unsupported borrowing remains a candidate.
- [ ] Run full tests/build and restart a partially completed fixture job; commit.

### Task 9: DeepSeek Harness runner and local-model evaluation

**Files (main):** `src/harness/{profile,runner}.ts`, `src/cli/research.ts`, `benchmarks/names.csv`, `benchmarks/rubric.md`, `tests/runner.test.ts`.

**Interfaces:** `researchName(input, {jobId, model, budgets}) -> ResearchResult`; `researchBatch(csvPath, options)` creates isolated session IDs and durable checkpoints.

- [ ] Pin a real Harness version; verify current plugin/SDK contracts and local endpoint routing. Disable shell/file tools, automatic uploads and telemetry explicitly.
- [ ] Write failing tests for malformed tool arguments, prompt injection treated as data, quota stop, context rollover, cancellation, interrupted batch and resume without duplicated work.
- [ ] Implement one model session per name, paged evidence tools, bounded continuation sessions and serialized local inference. Reuse verified evidence across sessions through storage.
- [ ] Benchmark fixed difficult names including Juan/Giovanni/Giovany and unrelated homographs, under human-reviewed expected evidence. Compare Qwen3.8-27B quantized vs Qwen3.5-9B on actual 4090 hardware.
- [ ] Record model hash/quantization/template, context, sampling, VRAM, tool validity, citation precision, latency and abstention. Set defaults from results; run full tests/build; commit.

### Task 10: Etymology Explorer and optional demographic clients

**Files:** source-repo `src/client.ts`, `tests/client.test.ts`, `docs/source-policy.md`.

**Interfaces:** EtymologyExplorerClient methods are defined only after verified endpoint docs exist; demographic clients expose `estimate(name, {country?}) -> SourceRecord<Estimate>`.

- [ ] Obtain Vanguard documentation without requesting credentials in chat. Confirm auth/refresh, schema, endpoints, quotas and public reuse rights. Keep integration unavailable with an explicit reason until confirmed.
- [ ] Write failing tests from documented response/error contracts, then implement verified wrappers and credential redaction. Never invent endpoints.
- [ ] If requested, implement demographic wrappers with separate prediction types and shared quota accounting; tests reject conversion into official statistics.
- [ ] Run full tests/build and credential-gated live checks; commit each independently.

### Task 11: Reports, public export policy and integration

**Files (main):** `src/export/{json,markdown,graph,policy}.ts`, `tests/export.test.ts`, `tests/integration.test.ts`, `docs/operations.md`.

**Interfaces:** `exportResearch(result, {audience: 'private'|'public'})` -> versioned JSON/JSONL and Markdown/Mermaid projection.

- [ ] Write failing tests for cycles, multiple roots, borrowed-language usage, missing evidence, restricted provider text, image licenses, suppression notes and output-name collisions.
- [ ] Implement graph projections with repeated-node references; default public exports to permitted fields only, with provenance and required attribution. Unknown policy denies export of source content.
- [ ] Run a fixture-only end-to-end batch covering no results, ambiguous roots, source conflict, quota exhaustion and resume. Verify no secrets/source cache enter git or public output.
- [ ] Document setup, local server settings, model benchmark results, provider enablement, update/resume and data-license handling. Run full tests/build, review changes and commit.

## Immediate handoff

Run the bootstrap locally, then report completion. The next independent deliverable
is Task 1 plus the Wiktionary client. Work on free sources can proceed while
Etymology Explorer documentation is obtained. No live API or local-GPU claim is
considered verified until its explicit smoke test or benchmark has run.
