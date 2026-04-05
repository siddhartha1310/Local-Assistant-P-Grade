# Slice 05 — Semantic Guardrails (Output Integrity) [DRAFT]

## Overview
Implements a Secure Knowledge Vault for persistent ground-truth data and an output validation layer (LLM-as-a-judge) to detect hallucinations and block prohibited content.

## CONTRACT

### Callable Interface
- `save_to_vault(file_name: str, content: str, user_id: int): void`
  - Persists masked text into the encrypted `secure_vault.db`.
  - throws: `VaultQuotaExceededError` if total storage exceeds limits.

- `get_vault_context(user_id: int): str`
  - Retrieves all vaulted text for the user, capped by context limits.

- `validate_output(query: str, response: str, context: str): ValidationReport`
  - Runs the model response through a multi-pass validation pipeline.
  - returns: `ValidationReport` containing pass/fail status and violation details.

- `check_hallucination(context: str, claim: str): bool`
  - Compares the model's claim against the provided Vaulted Context using an LLM-as-a-judge pattern.

### Data Shape
```python
@dataclass
class ValidationReport:
    is_safe: bool
    violations: list[str]
    confidence_score: float
```

### Constraints & Limits
- **Max File Ingestion**: 10MB raw file size.
- **Max Vault Storage**: 50MB of masked text per user in SQLCipher.
- **Judge Context Limit**: 8,000 characters (~2,000 tokens) of context sent to the Judge.

### Error Contract
- `VaultQuotaExceededError`: Raised when storage limits are hit.
- `ValidationError`: Raised if the validation service is unreachable.

---

## INTERNAL

### Technical Specification
- **Persistence Layer**: `knowledge_base` table in SQLCipher: `(id, user_id, file_name, content, timestamp)`.
- **Validation Logic**: Multi-pass filtering (Regex for static, LLM-as-a-judge for semantic).
- **LLM-as-a-judge Pass**: A secondary, rapid LLM call (e.g., Llama-3-8B) that cross-references the model's response against the context stored in the Knowledge Vault. 
- **Entailment Check**: Specialized prompt: "Does the provided context logically support the following claim? Answer YES or NO with a 1-sentence reasoning."

### Acceptance Criteria
- AC-1 (FUNCTION): `save_to_vault` correctly persists masked text and enforces the 50MB quota.
- AC-2 (FUNCTION): The LLM-as-a-judge pass identifies claims that contradict or are not supported by the Vaulted Context.
- AC-3 (E2E): The TUI displays a "Validation Warning" if a response fails a semantic guardrail.
- AC-4 (INTEGRATION): Every validation failure and vault operation is recorded in the encrypted `metrics` and `audit_log` tables.

### Subtasks (Static Definitions)
1. **Knowledge Vault Schema**: Create the `knowledge_base` table in `init_db.py`.
2. **Vault Service**: Implement `save_to_vault` and `get_vault_context` with size enforcement.
3. **LLM-as-a-judge Logic**: Develop the specialized "Judge" prompt and async validation call.
4. **Guardrail Orchestrator**: Integrate the validation pipeline and vault retrieval into the `ABEngine`.
5. **TUI Feedback**: Add a "Vault Status" indicator and UI alerts for flagged content.

### Out of Scope
- Real-time fact-checking against live internet sources.
- Automatic self-correction of responses (detection and flagging only).

## Change Log
- [2026-04-04]: Initial Draft Spec created.
