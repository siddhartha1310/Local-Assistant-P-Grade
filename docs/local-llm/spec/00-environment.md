# Slice 00 — Technical Environment & Infrastructure

## Overview
Defines the technical environment, runtime, tooling, and all cross-cutting architecture decisions for the Local LLM Assistant.
All subsequent specs (Slice 01+) MUST conform to the decisions recorded in the ## Architecture Decisions section below.

## Environment
- Language & Runtime: Python 3.12 (slim-bookworm)
- Package Manager: uv
- Key Frameworks: Textual (TUI), Pydantic (Data), SQLCipher3 (Database)
- Environment Paths: 
  - Venv: `/app/.venv` (within container)
  - Data: `/app/data` (SQLCipher DB)
  - Prompts: `/app/prompts` (YAML templates)
- Local Dev Command: `docker-compose up --build`
- Test Command: `uv run pytest`

## Dependencies
- `sqlcipher3-binary==0.5.2` — Encrypted SQLite database.
- `textual==0.58.0` — TUI framework for secure CLI.
- `httpx==0.27.0` — Async HTTP client for Ollama API.
- `pydantic==2.7.1` — Data validation and settings management.
- `presidio-analyzer==2.2.351` — PII detection engine.
- `presidio-anonymizer==2.2.351` — PII redaction engine.
- `spacy==3.7.4` — NLP backend for Presidio.
- `passlib[argon2]==1.7.4` — Secure password hashing.
- `loguru==0.7.2` — Structured logging.
- `watchdog==4.0.0` — File system events for hot-reloading.
- `jinja2==3.1.4` — Prompt template rendering.

## Architecture Decisions (ADRs)

### ADR-001 — Encrypted Persistence Layer
- **Decision**: SQLCipher (via `sqlcipher3-binary`) for all local storage.
- **Rationale**: Provides military-grade AES-256 encryption for user data, metrics, and audit logs.
- **Constraint**: ALL specs MUST use the encrypted vault. No plaintext SQLite or JSON storage permitted.

### ADR-002 — Secure TUI Interface
- **Decision**: Textual framework for a terminal-based UI.
- **Rationale**: Minimizes attack surface compared to a web UI while providing a rich, multi-pane experience.
- **Constraint**: All user interactions must happen through the Textual TUI.

### ADR-003 — Local LLM Orchestration
- **Decision**: Ollama running in a separate Docker container.
- **Rationale**: Clean separation of concerns and easy resource management (CPU/MEM limits).
- **Constraint**: Communication with LLMs must go through the Ollama REST API.

### ADR-004 — PII Redaction Strategy
- **Decision**: Presidio + SpaCy for multi-layer PII masking.
- **Rationale**: Industry-standard, highly configurable, and runs entirely locally.
- **Constraint**: All ingested content must pass through the masking pipeline if enabled.

## Acceptance Criteria

### Infrastructure
- **AC-1 (INTEGRATION)**: Docker Compose successfully orchestrates the `ollama` and `assistant` containers within a shared network.
- **AC-2 (INTEGRATION)**: The `assistant` service establishes a successful HTTP connection to the `ollama` API.
- **AC-3 (INTEGRATION)**: SQLCipher correctly initializes an encrypted database; file header must NOT be identifiable as standard SQLite.

### Dependencies & Resources
- **AC-4 (FUNCTION)**: All mandatory Python libraries (Loguru, Passlib, SQLCipher3, etc.) are successfully importable.
- **AC-5 (INTEGRATION)**: Models defined in `.env` (`phi3:mini`, `tinyllama`) are present in the local Ollama registry.
- **AC-6 (INTEGRATION)**: Resource limits (CPU/Memory) specified in `.env` are active on the containers.

### Failure Scenarios
- **AC-7 (INTEGRATION)**: If Ollama is unreachable, the `bootstrap.py` script must log a clear error and retry/exit without hanging.
- **AC-8 (INTEGRATION)**: If the wrong `DB_ENCRYPTION_KEY` is used, the system must fail with a clear "HMAC check failed" or "File is not a database" error.

## Validation Mandate
Slice 00 is NOT complete until:
1. `docs/local-llm/evals/integration/test_00_environment.py` is written.
2. `docs/local-llm/results/integration/00-environment.result.md` contains evidence of verification for every AC.

## Change Log
- [2026-04-04]: Refactored to align with `SKILLS/microspec.md` standards. Added Environment and ADR sections.
