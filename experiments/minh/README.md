# Minh's experiment

This folder is isolated from the shared HUST source documents. It uses only
`RecursiveChunker` with `chunk_size=450` and adds metadata from
`metadata_overrides.json` in memory when the store is built.

For a meaningful Vietnamese retrieval evaluation, pass `LocalEmbedder()` to
`build_store`; `_mock_embed` is suitable only for structural smoke tests.
