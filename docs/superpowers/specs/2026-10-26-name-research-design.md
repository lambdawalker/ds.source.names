# Name research design

## Approved storage architecture update

The graph-first service architecture supersedes the original SQLite-only storage
proposal and any in-process storage ownership described below. Shared TypeScript
contracts, normalized Markdown source documents, validated incremental findings,
SQL journaling/outbox and Neo4j graph queries now live in
[names.research.store](https://github.com/lambdawalker/names.research.store), with
implementation in [PR #1](https://github.com/lambdawalker/names.research.store/pull/1).
HTTP and MCP share the service's operations. The SQL journal is the recovery
authority; graph projection is eventually consistent. This repo owns the future
source integration, credential wizard and LLM/Harness orchestration. Source
libraries remain independent of both the model and the storage service.

## Intent and decisions

Build an open-source, multi-repository research system. Given names as input,
investigate roots, historical transmissions, forms in other languages, borrowing,
notable bearers and population statistics. Every published historical claim must
be backed by evidence, and uncertainty must remain visible.

The user accepted graph-based identity, evidence requirements, bounded discovery,
shared storage and per-name sessions. Implementation choice: TypeScript for the
research system and reusable clients; Python 3.10+ standard library for the
repository bootstrap so setup needs no npm installation. Source clients target
Node.js 24 LTS with native fetch and expose ESM plus TypeScript declarations.
Repository names in repositories.json are the authoritative bootstrap inventory.

## Approaches

1. All Python: good data tooling and an available Harness SDK, but native Harness
   tool plugins would introduce a TypeScript boundary anyway.
2. TypeScript clients and orchestration: selected implementation proposal, aligns
   with Harness plugins and allows clients to run independently of the agent.
3. Mixed Python clients and TypeScript orchestration: workable, but introduces
   packaging and IPC overhead without a demonstrated requirement. Revisit only
   for a source whose official Python SDK meaningfully reduces maintenance.

The user explicitly requested the plan and bootstrap now. This design records
defaults for later development; the research engine itself is not delivered by
this bootstrap change. MIT is the proposed code license used for newly created
companion repositories; data licensing is tracked separately.

## Boundaries

Six required source libraries plus one optional library, as listed in the README.
Do not create a vault library, generic HTTP library or graph library repository
before reuse warrants it. Clients own source-specific authentication, request
validation, response parsing, pagination and documented limits. The application
owns evidence extraction, canonical identity, graph reconciliation, persistent
cache, total quotas, provider policy, exports and task orchestration.

Each client accepts credentials and an injectable fetch implementation. It never
prompts for credentials, reads a vault, calls an LLM or installs Harness. Native
fetch is sufficient initially; existing official SDKs are evaluated first and
used when they match language, packaging, maintenance and security requirements.
No npm publishing or package-name availability is assumed.

## Research data

A form is identified by normalized spelling, language identifier, script and
origin sense where disambiguation is needed. Preserve original spelling and
diacritics; case/accent-folded strings are search aids, not canonical identities.
Historical language stages have separate identifiers. A name may have several
roots; reconstructed and attested forms are distinguished.

Relationships: derived_from, borrowed_from, transliteration_of, diminutive_of,
spelling_variant_of. Population/cultural usage is a separate assertion, not an
etymological edge. A directed graph may contain cycles from borrowing; do not
silently force it into a DAG. Tree exports are scoped projections with cycle
markers and repeated-node references.

Each claim stores its relation type, evidence IDs, source locator, retrieved
timestamp, revision where available, short supporting passage, interpretation,
and status (supported, disputed, candidate, unresolved). Confidence labels are
evidence assessments, not calibrated probabilities from an LLM. Store competing
claims instead of overwriting them. Sharing a root does not prove direct descent.

Source lineage must identify Wiktionary-derived services so several wrappers of
the same entry do not count as independent corroboration. Giovanni in Spanish
usage and Giovanni borrowed into Spanish from Italian are distinct claims.
Giovany/Giovanny require their own evidence; spelling resemblance is insufficient.

## Source inventory and reuse policy

| Source | Integration and evidence | Limitations / licensing gate |
|---|---|---|
| Wikimedia Enterprise | Evaluate official SDKs, otherwise typed thin HTTP adapter; login/refresh, projects, articles and snapshots | Existing free allocation is shared across Wikimedia projects. JSON envelope does not imply parsed lexical roots. Keep endpoint/quota configuration external. |
| WiktAPI / Kaikki | HTTP lookup and streamed JSONL, preserve etymology_text/templates when present | Verify live schemas with personal names. Community availability; preserve Wiktionary attribution/share-alike requirements and source lineage. |
| Wikidata | Entity search/lookup and narrowly scoped SPARQL; P735 for given names, P734 for surnames | CC0 structured data; incomplete bearer lists. Image licenses are separate. Wikipedia sitelinks can rank prominence, not establish objective fame. |
| Behind the Name | Official lookup and related-name endpoints; API key; documented throttling | Free API lacks meaning/history prose. Check public-display, caching and redistribution terms independently of bulk-data licensing. Disable public export of unreviewed provider content. |
| Etymology Explorer | Vanguard authentication and endpoint wrappers | BLOCKED until provider documentation confirms base URL, auth, schemas, quotas and reuse terms. Never guess endpoints or silently scrape the UI. |
| SSA | Download national/state/territory archives; stream parse and index | Not a query API. Record suppressed small counts, dataset coverage and revisions. Birth counts are not living-population estimates. |
| INSEE | Download published given-name files using release-specific manifests | Not an assumed live names API. Preserve geography, rounding/suppression and changing schemas per release; verify reuse license. |
| IBGE | Documented v2 names frequency/ranking endpoint | Documented v2 uses 2010 census; record actual coverage and do not claim 2022 data. Verify current availability/terms. |
| Agify family (optional) | Three thin API clients sharing configuration | Predictions are not official population totals, name etymologies or individual identities. Requires key and explicit quota configuration. |

Documentation references (reverify before each adapter is implemented):

- https://enterprise.wikimedia.com/docs/
- https://github.com/wikimedia-enterprise/wme-sdk-python
- https://wiktapi.dev/quickstart and https://kaikki.org/
- https://www.wikidata.org/wiki/Wikidata:Data_access
- https://www.behindthename.com/api/ and https://www.behindthename.com/info/licensing
- https://etymologyexplorer.com/info
- https://www.ssa.gov/oact/babynames/limits.html
- https://www.insee.fr/fr/statistiques/8595130
- https://servicodados.ibge.gov.br/api/docs/nomes?versao=2
- https://agify.io/faq

## Vault and security boundary

Setup captures provider keys/passwords, local model endpoint and contact User-Agent.
Use AES-256-GCM and a scrypt-derived key with random salt/nonces; store a versioned
envelope with fixed, validated KDF parameters. Hidden passphrase input unlocks
the vault per run; no plaintext secret persistence or passphrase next to ciphertext.
Atomic writes and restricted permissions where supported. Wrong passphrase,
corruption and schema incompatibility must fail closed without replacing the vault.
Rotation and token refresh use the same atomic persistence path. No short PINs.

The model sees allowlisted research tools with source-specific validated arguments.
Secrets stay in a separate source-tool service outside the Harness process; the
Harness receives no provider secrets in its environment. No shell/file tools or
automatic uploads/telemetry in the research profile. Profile restrictions are not
an OS sandbox: use process/container restrictions if untrusted execution is added.
Redact headers, query-string keys, raw response credentials and URL userinfo in
logs and error reports. Provider base URLs are validated to prevent sending keys
to a model-selected host. Retrieved pages are data, never instructions.

## Orchestration, memory and outputs

SQLite stores raw-response metadata/cache, forms, claims, evidence, jobs, budgets
and checkpoints. Raw licensed text stays outside git and is not exported by
default. A new session per input name, with shared verified family data in SQLite.
Read bounded evidence pages rather than whole articles or all descendants at once.
Fresh continuation sessions use durable checkpoints before context exhaustion.
Bound model turns, tools, tokens, total time, graph depth and provider expenditure.
Completion states distinguish source exhaustion, budget stop, partial failure and
review-required findings. Reruns reuse cached research and resume interrupted jobs.

Initial outputs: SQLite, versioned JSON per name, JSONL batch export, a Markdown
report and a scoped Mermaid tree/graph projection. Every statistic includes
country/geography, time period, measure, source and suppression notes. Public
export policy is applied per source; MIT source code does not imply MIT data.
No automatic uploads of research data, package publication or repository deletion.

## Model selection

Benchmark Qwen3.8-27B at approximately 4-bit quantization against Qwen3.5-9B on the
actual RTX 4090. Start with a modest context budget and one inference job; exact
quantization/context defaults are set by measured VRAM and latency, not advertised
context capacity. LM Studio is the first candidate; retain OpenAI-compatible
endpoint configuration so llama.cpp or another server can replace it.
Pin the Harness release and actual model artifact/hash, template, quantization
and sampling settings. Select on citation accuracy, relationship precision,
tool/JSON validity, abstention, latency and memory. No model is declared best yet.

## Open items

Provider documentation for Etymology Explorer; exact source redistribution rights;
initial language/country coverage and a sample name list; measured model choice;
npm package names and publication strategy. These do not block the repo bootstrap
or free-source client development, but they block unsupported adapters and public
data releases. Default initial inputs are UTF-8 CSV with name and optional language;
reports default to English while preserving original-script forms.
