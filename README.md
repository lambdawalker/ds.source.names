# ds.source.names

Evidence-based research on personal-name origins, historical forms, borrowing,
notable bearers and population usage. TypeScript libraries will expose source
data to a DeepSeek Harness orchestrator using a local model.

**Current status:** the six core companion repositories have been created and
access verified. The research runner, API clients and encrypted credential wizard
are not implemented yet. The one-time repository creation script and its tests
have been removed; [repositories.json](repositories.json) remains the repository inventory.
The optional demographics repository has not been created.

## Research storage service

The approved graph-first architecture is implemented for review in
[names.research.store PR #1](https://github.com/lambdawalker/names.research.store/pull/1).
That repository owns the shared TypeScript contracts, Neo4j graph projection,
SQLite finding journal/search cache, normalized Markdown evidence and HTTP/MCP
interfaces. This repository remains the source-client integration and future
DeepSeek Harness orchestrator. JSON is an interchange/report format.

New source clients will submit incremental findings and retained-source metadata
through the storage API. The storage service does not fetch sources or run an LLM.

## Next development milestone

1. Review the implemented TypeScript contracts and storage API in `names.research.store`.
2. Implement the Wiktionary client and streaming Kaikki reader in the companion repository.
3. Verify real name lookups and preserve sources, historical forms and uncertainty.
4. Add Wikidata for notable bearers, followed by credentialed sources and statistics.
5. Build the encrypted setup wizard and Harness orchestration against the storage service.

No credentials are needed for the first milestone. Etymology Explorer remains
blocked on verified Vanguard API documentation. Model selection comes after we
have an evidence-based benchmark; no GPU model has been selected or tested yet.

## Library boundaries

| Repository | Responsibility |
|---|---|
| `names.api.wikimedia-enterprise` | Enterprise authentication and article/snapshot access; evaluate official SDK reuse before implementing a thin TypeScript client |
| `names.api.wiktionary` | WiktAPI lookups and Kaikki JSONL ingestion, preserving etymology evidence |
| `names.api.wikidata` | Name identity, related entities, notable bearers and sourced facts |
| `names.api.behindthename` | Lookup and related forms; no unsupported meaning/history extraction |
| `names.api.etymology-explorer` | Vanguard client after actual API documentation is available |
| `names.data.statistics` | SSA/INSEE dataset importers and IBGE API adapter |
| `names.api.demographics` (optional) | Agify/Genderize/Nationalize estimates, explicitly distinguished from census counts |

The credential vault, provider integration, model benchmarks and Harness integration
belong in **this repository**. Shared research contracts, graph persistence,
evidence documents and the search cache belong in **names.research.store**.
Source clients remain reusable and do not require a model, Harness or vault.

Read the [design](docs/superpowers/specs/2026-10-26-name-research-design.md)
and [implementation plan](docs/superpowers/plans/2026-10-26-name-research.md)
for the interfaces, source restrictions, implementation order and acceptance checks.

Open-source code licensing does not relicense provider data. Source text,
datasets and images retain their original terms; public exports must preserve
provenance and apply the relevant source-specific rules.
