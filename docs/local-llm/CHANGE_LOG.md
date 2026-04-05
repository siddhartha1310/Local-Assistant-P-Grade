# Change Log — Local LLM Assistant

## [2026-04-04] — Slice 05: Semantic Guardrails & Knowledge Vault

### Added
- `src/security/vault.py`: Secure Knowledge Vault service with SQLCipher and quota enforcement.
- `src/security/guardrails.py`: Multi-pass validation service (Static + LLM-as-a-judge).
- `prompts/hallucination_judge.yaml`: Specialized judge prompt for entailment checking.
- `docs/local-llm/evals/05-semantic-guardrails.eval.py`: Evaluation script for Slice 05.
- `docs/local-llm/evals/fixtures/04-ab-testing.fixture.py`: Fixtures for A/B testing.
- `docs/local-llm/evals/fixtures/05-semantic-guardrails.fixture.py`: Fixtures for guardrails and vault.
- `docs/local-llm/evals/results/05-semantic-guardrails.result.md`: Verification results.

### Fixed
- `src/ui/app.py`: Resolved `NameError` for `Optional` and `ValidationReport` type hints.
- `src/ui/app.py`: Fixed CSS parsing error (invalid `thin` border value).
- `data/secure_vault.db`: Successfully migrated existing local databases to include the `redacted_count` column.
- `src/security/audit.py`: Fixed DB path resolution to respect environment variables.
- `src/security/vault.py`: Added missing audit logging for vault operations.
- `docs/local-llm/evals/`: Updated legacy evaluation scripts to handle modern service signatures (tuples and model names).

### Changed
- `src/init_db.py`: Added `knowledge_base` table to the encrypted schema.
- `src/orchestration/models.py`: Updated `ABConfig` and `ABResult` to support vaulting and validation reports.
- `src/orchestration/ab_engine.py`: Integrated Vault and Guardrail services into the A/B testing flow.
- `src/ui/app.py`: Updated TUI with Vault controls and Hallucination warnings.
- `src/orchestration/generator.py`: Updated default Ollama host to `127.0.0.1` for local stability.
- `pyproject.toml`: Replaced `sqlcipher3-binary` with `sqlcipher3` for Windows compatibility.
- `gemini.md`: Updated last updated date.
- `docs/local-llm/spec/roadmap.md`: Marked Slice 05 as completed.
- `docs/local-llm/local-llm_memory.md`: Updated current context to Slice 06.
