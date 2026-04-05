# Roadmap — Local LLM Assistant (Secure Framework)

## 00 — Secure Environment & Prompt Infrastructure [Status: Completed]
- [x] Setup Docker Compose & Python 3.12 environment (UV)
- [x] Install All Project Dependencies (Security, TUI, Privacy, Extraction)
- [x] Setup SQLCipher encrypted local storage & RBAC Schema
- [x] Initial Model Provisioning (Pull Phi-3 and TinyLlama)
- [x] Define Prompt Versioning structure (YAML) with hot-reload support
- [x] Evals written
- [x] Evals stable and passing
- [x] UAT verified

## 01 — Secure CLI, RBAC Login & Audit Trail [Status: Completed]
- [x] [Subtask 1: CLI Login with Local RBAC]
- [x] [Subtask 2: Immutable Audit Logging System]
- [x] [Subtask 3: Dynamic Model Switching via Ollama API]
- [x] Evals written
- [x] Evals stable and passing
- [x] UAT verified

## 02 — Privacy Pipeline & File Ingestion (PDF/TXT/CSV) [Status: Completed]
- [x] [Subtask 1: PII Masking Pipeline (Regex/Presidio)]
- [x] [Subtask 2: Secure File Extraction with Masking]
- [x] Evals written
- [x] Evals stable and passing
- [x] UAT verified

## 03 — Pro-Grade Prompting (Live/Hot-Reload) [Status: Completed]
- [x] [Subtask 1: Hot-Reload Watcher for Prompt Templates]
- [x] [Subtask 2: Prompt Version Selection in CLI]
- [x] Evals written
- [x] Evals stable and passing
- [x] UAT verified

## 04 — A/B Testing [Status: Completed]
- [x] [Subtask 1: Side-by-Side Model/Prompt Evaluation]
- [x] [Subtask 2: Comparative Performance Metrics]
- [x] Evals written
- [x] Evals stable and passing
- [ ] UAT verified

## 05 — Semantic Guardrails & Knowledge Vault [Status: Completed]
- [x] Subtask 1: Knowledge Vault Schema (SQLCipher)
- [x] Subtask 2: Vault Service & Size Enforcement
- [x] Subtask 3: LLM-as-a-judge (Hallucination Detection)
- [x] Subtask 4: Guardrail Orchestrator (ABEngine Integration)
- [x] Subtask 5: TUI Feedback & Vault Status
- [x] Evals written
- [x] Evals stable and passing
- [ ] UAT verified

## 06 — Advanced TUI Dashboard (Security & Performance) [Status: Completed]
- [x] Subtask 1: Multi-Pane Dashboard Layout (Dockable Panes)
- [x] Subtask 2: Real-time Performance Metrics (Sparklines/Latency)
- [x] Subtask 3: Security & PII Visualization (Masking Stats)
- [x] Subtask 4: Async Data Polling (Metrics/Audit Pipeline)
- [x] Subtask 5: UI Responsiveness Optimization (60 FPS Goal)
- [x] Evals written
- [x] Evals stable and passing
- [ ] UAT verified

## Eval Debt
- None

## ADR Revision Debt
- None
