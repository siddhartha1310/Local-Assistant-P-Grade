# Local LLM Assistant — Domain Memory

## Overview
A secure, privacy-first local AI framework running via Ollama in a Dockerized environment. Key features include local RBAC, encrypted metrics/audit logs via SQLCipher, PII masking, and hot-reloading prompt versioning.

## Context Tracking
- **Current Slice**: Deployment & Final Hardening
- **Status**: Slices 00-06 completed and verified via E2E evaluation scripts (2026-04-04).
- **Key Constraints**: Laptop-safe resource limits, fully local, SQLCipher encryption, PII redaction.

## Architectural Patterns
- **CLI**: Multi-pane TUI with real-time Metrics (Sparklines) and Security visualization.
- **Security**: Local RBAC, PII masking, and LLM-as-a-judge Hallucination Detection.
- **Data**: Secure Knowledge Vault with 10MB/50MB per-user quotas.

## Known Issues / Debt
- [x] Fixed: NameError in type hints (Optional/ValidationReport).
- [x] Fixed: CSS parsing error in TUI.
- [x] Fixed: Database schema migration for `redacted_count`.
- [ ] Need to verify Docker GPU passthrough for common laptop GPUs (Nvidia/Apple Silicon).
