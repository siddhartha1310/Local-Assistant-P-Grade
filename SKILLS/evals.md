# evals.md — Eval Generation & Lifecycle Playbook
Single source of truth for how evals are written, maintained, and run across environments.
Location: project root alongside GEMINI.md, MEMORY.md, skills.md.

---
---

## Eval Generation Rules
Concept: Every feature with acceptance criteria MUST have a corresponding test.
These rules ensure tests are environment-agnostic, traceable, and validate real system behavior.

---

### The 10 Mandatory Testing Rules (HARD RULES)

**RULE 1: Every Acceptance Criterion (AC) MUST be testable**
- Avoid vague language like "works", "properly", "correctly".
- Each AC must be verifiable via code, system state, or observable behavior.
- If an AC is not testable → it must be rewritten.

**RULE 2: Every AC MUST have at least one test**
- No AC should exist without a corresponding test.
- Tests must validate real behavior, not assumptions.

**RULE 3: Choose the correct test type based on AC nature**
- **FUNCTION** (pure logic, no external dependency) → must have an eval/unit test.
- **INTEGRATION** (DB, API, filesystem, Docker, external services) → must have an integration test using real components.
- **E2E** (UI, CLI, full user flow, system interaction) → must have an end-to-end test simulating real usage.

**RULE 4: Do NOT rely only on eval tests**
- Eval tests validate logic, NOT system behavior.
- If AC involves DB, UI, or runtime flow → eval alone is insufficient.

**RULE 5: Prefer real systems over mocks**
- Use real DB (or test DB), real API, or containers where possible.
- Mock only when absolutely necessary and explicitly justified.

**RULE 6: Cover failure scenarios**
- Each spec must include tests for: invalid inputs, authentication failures, system failures (DB down, API timeout, etc.).

**RULE 7: Map every AC to a test**
- Maintain clear mapping in the result file: AC → Test Type → Test Case.
- Missing mapping = incomplete spec.

**RULE 8: Add system-level validation**
- Ensure at least one test validates full workflow (e.g., login → dashboard → action → audit log).

**RULE 9: Reject incomplete specs**
- If spec contains only unit/eval tests → REJECT.
- If integration or E2E is required but missing → REJECT.

**RULE 10: Final validation check**
- Ask: "Can all tests pass while system is still broken?"
- If YES → tests are insufficient → add integration/E2E tests.

---

### Detailed Logging Requirement (MANDATORY)
- **High Visibility**: Every test case in an eval script MUST include detailed logging using `loguru`.
- **AC-to-Log Mapping (Hard Rule)**: Every Acceptance Criterion (AC) from the spec MUST have a corresponding log entry in the eval script.
- **Log Structure**: Each test MUST log:
  1. **Start Trace**: `logger.info("Starting test for AC-X: <criteria_name>")`
  2. **Input/Context**: Log the specific data from fixtures being used.
  3. **Step Trace**: Log internal logic execution.
  4. **Verification**: Log the actual result vs. expected result before assertion.
  5. **Final Status**: `logger.success("AC-X PASSED")` on success.
- **Result Transparency**: The final `.result.md` file MUST contain the captured logs for **every single AC**. If a log for an AC is missing, the verification is considered incomplete.

---

## Integrity & Truthfulness in Evaluation (MANDATORY)

- **No Synthetic Passes**: It is STRICTLY PROHIBITED to claim a "PASS" in any eval result file based on implementation logic alone.
- **Evidence Requirement**: Every "PASS" must be backed by empirical evidence (e.g., a terminal log, a tool output, or a code-driven verification).
- **Environment Barriers**: If an eval cannot be run due to environment limitations (e.g., no Docker access), it MUST be marked as `READY FOR VERIFICATION` or `PENDING USER EXECUTION`.
- **User Confirmation**: For technical setups (Slice 00), the AI must ask the user to run the setup and provide the resulting logs before marking the slice as completed.

---

### Eval Results & Transparency
- Every evaluation run MUST generate a detailed result file.
- File location: `docs/<domain>/evals/results/<type>/NN-<feature>.result.md`
- **Deep Verification Rule (Hard Rule)**: The result file must not just say "Pass". It MUST include:
  - **Input Data**: The exact raw data passed into the function (referenced from fixtures).
  - **Raw Output**: The exact data received back from the system.
  - **Log Evidence**: Actual code-fenced log output for **every AC tested**.
  - **Verification Logic**: A clear explanation of *why* this constitutes a pass.
- Results allow the user to verify implementation details without reading raw logs.

---

### Eval File Rules
- **Structure**: All evaluation scripts are stored in a flat `evals/` directory. Fixtures and results are stored in their respective flat subdirectories:
  - Scripts: `docs/<domain>/evals/NN-feature.eval.py`
  - Fixtures: `docs/<domain>/evals/fixtures/NN-feature.fixture.py`
  - Results: `docs/<domain>/evals/results/NN-feature.result.md`
- Every eval file must begin with this header block:

```
// Feature: <feature name>
// Spec: docs/<domain>/spec/NN-<feature>.md
// Test Types Included: FUNCTION | INTEGRATION | E2E
// Last reviewed: [YYYY-MM-DD]
// Status: stable | wip | deprecated
```

- Each script MUST contain ALL relevant tests (Functional, Integration, and E2E) required to verify its linked spec.
- Test files must only test ACs from its linked spec — no cross-spec logic in one file.
- When linked spec is archived to history/, review evals and update or mark deprecated.

---

### Environment-Agnostic Evals
- NEVER hardcode environment URLs, credentials, simulator endpoints, or API keys in evals.
- Always read environment config from process.env or a centralized config loader.
- Every eval file must work across dev, UAT, and prod by swapping config only.

---

### Adapter / Provider Pattern
- Wrap ALL external services (APIs, simulators, queues, DBs) behind a provider interface.
- Generate three artifacts for every external dependency:
  - `docs/<domain>/evals/providers/<service>.provider.interface.ts` — the contract
  - `docs/<domain>/evals/providers/mock-<service>.provider.ts` — used in dev/local evals
  - `docs/<domain>/evals/providers/real-<service>.provider.ts` — used in UAT/prod evals
- Evals MUST receive providers via dependency injection. Never import a concrete provider directly inside an eval file.

---

### Seed Data & Fixtures
- **No Hardcoded Test Data (Hard Rule)**: It is STRICTLY PROHIBITED to have hardcoded test strings, query objects, or expected results inside test scripts. 
- **Mandatory Usage**: All test data MUST be stored in dedicated fixture files and imported. Any test found with hardcoded data must be rejected and refactored.
- **Categorization**: 
  - `docs/<domain>/evals/fixtures/common/` (Shared across types)
  - `docs/<domain>/evals/fixtures/functional/` (Pure data for logic tests)
  - `docs/<domain>/evals/fixtures/integration/` (Configuration/State for system tests)
  - `docs/<domain>/evals/fixtures/e2e/` (User scenarios/UI states)
- The number `NN` in filenames MUST match the corresponding vertical slice.
- Fixtures must be realistic but never contain real PII or production credentials.

---

### Eval–Spec Traceability
- Every acceptance criterion in the spec must map to at least one eval case.
- Add a comment above each eval block referencing its source AC:
  `// AC: <criteria description> [spec: docs/<domain>/spec/NN-<feature>.md#AC-N]`
- If an AC has no eval, it is considered untested and MUST be flagged to the user.
- When a spec file is modified, immediately flag all evals referencing that spec as @status: deprecated.

---

### Eval Lifecycle Tagging
- Every eval block MUST carry a status tag:

```
// @status: stable      ← trusted, runs in CI, fails build if broken
// @status: wip         ← feature incomplete, runs but does NOT fail build
// @status: deprecated  ← spec changed, skipped with warning logged in CI
```

- Deprecated and wip evals must be tracked in `docs/<domain>/spec/roadmap.md` — `## Eval Debt` section.

#### Eval Debt Format
```markdown
## Eval Debt
- [ ] <feature>.eval.ts — deprecated, reason: <spec change summary>
- [ ] <feature>.eval.ts — wip, complete after: <pending feature>
```

- **Zero Debt Rule:** Eval Debt must be zero before any UAT deployment or merging to main.
- STRICTLY PROHIBITED: Merging to main or deploying to UAT with any eval tagged wip or deprecated.

---

### Eval Pyramid by Environment
Do not run all evals in all environments. Follow this tiering:

| Environment | Eval Types |
|-------------|-----------|
| Dev/Local | Feature evals only (mock providers OK) |
| PR / CI | Full suite (all stable evals, fail on broken) |
| Staging | Integration + contract tests (mock external) |
| UAT | E2E + smoke tests (real providers, real data) |
| Prod | Smoke + synthetic monitoring only |

---

### Eval Execution Workflow
Follow this order strictly:
1. While coding → run only the current feature's evals for fast feedback
2. Before PR → run full suite locally, all must be stable and passing
3. CI on PR → full suite runs automatically, blocks merge if any stable eval fails
4. Before UAT deploy → run UAT-tier evals, 100% stable coverage required
5. Before prod deploy → run smoke tests only

---

### Linter Safety Rule
- Reject any eval file that contains hardcoded values matching: localhost, simulator URLs, or raw API keys.
- Flag these to the user immediately and refactor before committing.

---
---

*Last updated: [Update this date each session]*
