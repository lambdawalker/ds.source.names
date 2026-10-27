# ds.source.names

Evidence-based research on personal-name origins, historical forms, borrowing,
notable bearers and population usage. TypeScript libraries will expose source
data to a DeepSeek Harness orchestrator using a local model.

**Current status:** Wiktionary, Wikidata, Behind the Name and official statistics clients are implemented, alongside the research storage service and the root-research runner in [ds.names.orchestrator](https://github.com/lambdawalker/ds.names.orchestrator).

All implemented source clients and the database expose agent MCP servers. See the [combined agent MCP setup guide](docs/agent-mcp-setup.md) for configuration, tool coverage, imported SSA/INSEE access and remaining live checks. Wikimedia Enterprise and Etymology Explorer remain unimplemented placeholders.

## Research storage service

The approved graph-first architecture is implemented in
[names.research.store](https://github.com/lambdawalker/names.research.store)
([merged PR #1](https://github.com/lambdawalker/names.research.store/pull/1)).
That repository owns the shared TypeScript contracts, Neo4j graph projection,
SQLite finding journal/search cache, normalized Markdown evidence and HTTP/MCP
interfaces. This repository remains the source-client integration and future
DeepSeek Harness orchestrator. JSON is an interchange/report format.

New source clients will submit incremental findings and retained-source metadata
through the storage API. The storage service does not fetch sources or run an LLM.

## Next development milestone

Connect enrichment sources to the orchestrator's deliberately bounded research phases. Complete Behind the Name's key-gated live check and IBGE's availability-dependent live check, then implement the remaining credentialed clients from verified documentation. Existing source results preserve candidate status and provenance; having an MCP does not automatically enable every tool in the root-only runner.

## Library boundaries

| Repository | Responsibility |
|---|---|
| `names.api.wikimedia-enterprise` | Enterprise authentication and article/snapshot access; evaluate official SDK reuse before implementing a thin TypeScript client |
| `names.api.wiktionary` | Official Wiktionary revision-aware Markdown evidence and WiktAPI structured lookups; future Kaikki bulk ingestion |
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
