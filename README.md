# ds.source.names

Evidence-based research on personal-name origins, historical forms, borrowing,
notable bearers and population usage. TypeScript libraries will expose source
data to a DeepSeek Harness orchestrator using a local model.

**Current status:** the six core companion repositories have been created and
access verified. The research runner, API clients and encrypted credential wizard
are not implemented yet. The one-time repository creation script and its tests
have been removed; [repositories.json](repositories.json) remains the repository inventory.
The optional demographics repository has not been created.

## Next development milestone

1. Establish the TypeScript project and validated forms, claims and evidence schemas.
2. Implement the Wiktionary client and streaming Kaikki reader in the companion repository.
3. Verify real name lookups and preserve sources, historical forms and uncertainty.
4. Add Wikidata for notable bearers, followed by credentialed sources and statistics.
5. Build the encrypted setup wizard, persistent research graph and Harness orchestration.

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

The vault, canonical research graph, cache, job queue, source-policy rules,
exports, model benchmarks and Harness integration belong in **this repository**.
Source clients remain reusable and do not require a model, Harness or vault.

Read the [design](docs/superpowers/specs/2026-10-26-name-research-design.md)
and [implementation plan](docs/superpowers/plans/2026-10-26-name-research.md)
for the interfaces, source restrictions, implementation order and acceptance checks.

Open-source code licensing does not relicense provider data. Source text,
datasets and images retain their original terms; public exports must preserve
provenance and apply the relevant source-specific rules.
