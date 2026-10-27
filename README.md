# ds.source.names

Evidence-based research on personal-name origins, historical forms, borrowing,
notable bearers and population usage. TypeScript libraries will expose source
data to a DeepSeek Harness orchestrator using a local model.

**Current status:** library roadmap and tested repository bootstrap only. The
research runner, API clients and encrypted credential wizard are not implemented
yet. Repository creation does not install or publish npm packages.

## Create the companion repositories

Requirements: Python 3.10+ and [GitHub CLI](https://cli.github.com/) installed on
your computer. Run these commands from a checkout of this repository:

```sh
gh auth login --hostname github.com
python scripts/create_repositories.py
python scripts/create_repositories.py --apply
```

On Windows, `py -3` can replace `python`. The script works from any directory;
its default manifest is resolved relative to the script, not your terminal.

The first script command is a **dry run**: it prints commands without contacting
GitHub. `--apply` creates the six required repositories listed in
[repositories.json](repositories.json) under **lambdawalker**, with public
visibility, a README and MIT license. It verifies the active account first.
Existing repositories are skipped without changing files, settings or visibility.
Failures stop the run; rerunning skips earlier successes. No repositories are
deleted, no files are overwritten, and no local clones are created.

```sh
# Also create the optional demographic-estimates client:
python scripts/create_repositories.py --include-optional --apply

# Create a specific required repository:
python scripts/create_repositories.py --only names.api.wikidata --apply
```

Use `--gh /path/to/gh` if the CLI is not on PATH. Personal-account repositories
only are supported; organization creation is outside this script's scope. To
change the owner or names, edit the manifest before running it. CLI credentials
are managed by `gh`; this script never asks for, reads or prints a token.

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

## Verify the bootstrap

```sh
python -m unittest discover -s tests -v
```

Tests simulate GitHub command responses and exercise dry-run and failure behavior.
They create no remote repositories. Live creation must be run and verified on
your computer; the current development environment cannot complete CLI login.

Open-source code licensing does not relicense provider data. Source text,
datasets and images retain their original terms; public exports must preserve
provenance and apply the relevant source-specific rules.
