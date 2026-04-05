# Slice 04 — A/B Testing

## Overview
Implements side-by-side comparative evaluation of different LLM models or prompt versions.

## CONTRACT

### Callable Interface
- `ABEngine.run_test(query: str, config: ABConfig): ABResult`
  - Triggers generation from two configurations in parallel using async orchestration.
  - returns: `ABResult` containing both model outputs and their respective performance metrics.
  - throws: None (errors are captured per generation result).

- `ABEngine.record_preference(test_id: str, preferred_index: int, user_id: int = None): void`
  - Records user preference (winner selection) for a given A/B test run.

- `AsyncGenerator.generate(model: str, prompt: str): GenerationResult`
  - Calls the Ollama REST API asynchronously to generate a response and capture metrics.
  - returns: `GenerationResult` object with response text and detailed performance data.

### Data Shape
```python
@dataclass
class ABConfig:
    model_a: str
    prompt_a: str
    model_b: str
    prompt_b: str

@dataclass
class GenerationResult:
    response: str
    latency_ms: float
    tokens_per_sec: float
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    model: str
    success: bool
    error: Optional[str]

@dataclass
class ABResult:
    test_id: str
    result_a: GenerationResult
    result_b: GenerationResult
```

### Error Contract
- Generation errors are returned within the `GenerationResult.error` field rather than raised, allowing one side of an A/B test to fail while the other succeeds.

---

## INTERNAL

### Technical Specification
- **Concurrency**: `asyncio.gather` for parallel model execution.
- **HTTP Client**: `httpx` for asynchronous communication with the Ollama API.
- **Metrics**: Captures latency, tokens per second, and token counts (prompt/completion).
- **Storage**: Integrates with `metrics_service` to persist results in the SQLCipher database.

### Acceptance Criteria

### Execution
- **AC-1 (INTEGRATION)**: The system executes two model configurations in parallel using async orchestration.
- **AC-2 (INTEGRATION)**: Total generation metrics (Latency, Tokens/sec) are captured for every A/B run.

### TUI Integration
- **AC-3 (E2E)**: The TUI supports a "Dual Mode" display showing two distinct model responses side-by-side.
- **AC-4 (E2E)**: The TUI provides voting buttons (Vote A / Vote B) after a dual generation is complete.

### Persistence
- **AC-5 (INTEGRATION)**: User preferences (winner selection) are saved to the encrypted SQLCipher vault and linked to the unique test ID.
- **AC-6 (INTEGRATION)**: Comparative metrics are stored in the `metrics` table for later analysis.

### Failure Scenarios
- **AC-7 (INTEGRATION)**: If one model configuration fails, the TUI must display the error for that pane while still showing the successful response in the other.
- **AC-8 (FUNCTION)**: Attempting to run an A/B test with unavailable models should be blocked by the UI and return a clear validation error.

### Subtasks (Static Definitions)
1. **ABConfig and ABResult Models**: Define the data structures for configuring and returning test results.
2. **Parallel ABEngine Implementation**: Develop the async engine to coordinate twin generations.
3. **Generator Metric Extraction**: Refine `AsyncGenerator` to parse Ollama's performance headers/metadata.
4. **TUI Split-Pane View**: Create a side-by-side message view in Textual for comparative display.
5. **Preference Capture Logic**: Implement the voting buttons and their link to the persistence layer.

### Out of Scope
- Automatic winner determination (e.g., using a "judge" model).
- Cross-session metric aggregation (individual test tracking only).

## Change Log
- [2026-04-04]: Refactored to align with `SKILLS/microspec.md` standards. Added CONTRACT and INTERNAL sections.
