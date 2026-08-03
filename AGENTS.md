# Team-agent collaboration rules

## Shared corpus

- `data/hust_services/` is the team’s shared, source-of-truth corpus. Do not change its document body or front matter for an individual chunking/metadata experiment.
- A corpus correction (wrong source, missing required metadata, unsafe content) must be agreed by the team. Update the matching entry in `sources.csv` in the same commit.
- Preserve required fields: `doc_id`, `title`, `source_url`, `retrieved_at`, `document_version`, and `audience`. Do not add private, login-only, or personal data.

## Individual experiments

- Work only in `experiments/<your-name>/`. Do not create a second copy of the shared documents.
- Select exactly one built-in strategy: `FixedSizeChunker`, `SentenceChunker`, or `RecursiveChunker`. Record its parameters in your experiment configuration.
- Store personal metadata additions in `metadata_overrides.json` and apply them in memory while building the vector store. Do not edit shared front matter to test a personal metadata profile.
- Everyone uses the same ten documents and the same five group benchmark queries. At least one query must use `metadata_filter={"audience": "student"}`.

## Git workflow for coding agents

- Before editing, run `git status --short`; preserve unrelated work.
- Commit only files within your assigned experiment folder, unless the team explicitly approved a shared-corpus correction.
- Run a relevant verification before committing. Do not use `git reset --hard`, force push, or rewrite another member’s work.
- Agents may commit and push their own scoped changes to the repository’s current branch only after verification. Use a clear commit message.
