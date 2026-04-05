# microspec.md — Vertical Micro-Specification Playbook
Single source of truth for how features are broken down, specified, and tracked.
Location: project root alongside GEMINI.md, MEMORY.md, skills.md.

---
---

## Spec Creation Rules
Concept: Organize work into the smallest complete vertical feature slice — not monolithic docs, not disconnected fragments. Every feature goes through two mandatory phases before any code is written: High-Level Breakdown → Micro Spec per Slice.

---

### Phase 1 — High-Level Breakdown (MANDATORY FIRST STEP)
Before creating any spec file, the AI must:
1. Analyze the feature/task and propose a breakdown into vertical slices.
2. **Mandatory Slice 00**: Every project MUST start with `Slice 00 — Technical Environment & Infrastructure`. This spec defines the exact technical stack (language, versions, dependencies, environment paths) AND all cross-cutting architecture decisions. It must be updated continuously as the stack evolves. **Every vertical spec (Slice 01+) is bound by the decisions recorded in Slice 00.**
3. Present the proposed slices to the programmer in this format:

```
Proposed Vertical Breakdown — <Feature Name>

Slice 01 — <Name>: <1 sentence description of what this slice covers> ← starts first
Slice 02 — <Name>: <1 sentence description> ← starts after Slice 01 is complete and verified
Slice 03 — <Name>: <1 sentence description> ← starts after Slice 02 is complete and verified

Each slice is a self-contained deliverable. Work is sequential, not parallel.
Do you approve this breakdown, or would you like to adjust?
```

3. WAIT for programmer approval before creating any spec file or writing any code.
4. If the programmer requests changes to the breakdown, revise and re-present. Never proceed unilaterally.

#### What Makes a Valid Vertical Slice
- It is a complete, testable, and deliverable unit on its own.
- It can be fully built, tested, and demonstrated end-to-end before the next slice begins.
- Slices are worked on sequentially — one slice is completed and verified before the next starts.
- It does not need to wait for another slice to be testable or demonstrable.
- It maps to exactly one micro spec file.

#### Slice Sequencing Rule
- Slices have a natural order — earlier slices may be prerequisites for later ones.
- The breakdown must reflect this order explicitly with sequencing notes (see template above).
- The goal is not parallelism — it is that each slice delivers something testable and real before moving forward.
- No half-built features that cannot be verified stand-alone.
- STRICTLY PROHIBITED: Starting the next slice before the current slice is complete and verified by the programmer.

#### PROHIBITED at Phase 1
- Creating any spec file before breakdown is approved.
- Combining multiple slices into one spec.
- Starting to code while breakdown is under review.
- Starting the next slice before the current slice is complete and verified by the programmer.

---

### Phase 2 — Spec Creation (MANDATORY DRAFTING)
Immediately after the high-level breakdown is approved, the AI must create **Draft Specs** for ALL identified slices. 

**Protocol:**
1. **Initial Draft**: Create every spec file (`01-feature.md`, `02-feature.md`, etc.) with a complete `## Overview` and `## CONTRACT`.
2. **Context Preservation**: The `## INTERNAL` section of these drafts should contain the initial technical strategy and anticipated subtasks to lock in the design intent.
3. **Active Refinement**: Only the spec for the **current** slice is considered "Final" and ready for implementation. Future specs remain as "Drafts" and MUST be refined and re-presented for final approval before their implementation begins.
4. **Consistency**: This ensures Slice 00 decisions are immediately applied across the entire roadmap, preventing architectural drift.

#### File Rules
- File location: docs/<domain>/spec/NN-<feature>.md (sequential number prefix).
- Naming: 01-<feature>.md, 02-<feature>.md
- One spec file per slice — never combine slices.

---

#### Slice 00 — Technical Environment & Infrastructure (Special Template)

Slice 00 is the **complete technical blueprint and horizontal authority layer** for the entire project. All vertical specs (Slice 01+) are constitutionally bound by the decisions recorded here. Its purpose is to ensure every tool, dependency, and architectural constraint is known and documented before any functional logic is built. No vertical spec may introduce a technology, library, or pattern that contradicts an ADR in Slice 00 without first updating it through the conflict protocol below.

**File location:** `docs/<domain>/spec/00-environment.md`

```
## Overview
Define the technical environment, runtime, tooling, and all cross-cutting architecture decisions for this project.
All subsequent specs (Slice 01+) MUST conform to the decisions recorded in the ## Architecture Decisions section below.

## Environment
- Language & Runtime: <e.g., Python 3.12 / Node 20 / Go 1.22>
- Package Manager: <e.g., uv / pnpm / go mod>
- Key Frameworks: <e.g., FastAPI, React, Express>
- Environment Paths: <venv, node_modules, binary locations>
- Local Dev Command: <how to run locally>
- Test Command: <how to run tests>

## Dependencies
List all installed packages with pinned versions.
- <package>==<version> — <one-line purpose>

## Architecture Decisions (ADRs)

Each ADR is a binding constraint on ALL vertical specs.
Before implementing any Slice 01+, the AI must read all ADRs and confirm compliance.

### ADR-001 — Persistence Layer
- **Decision**: <e.g., PostgreSQL via asyncpg>
- **Rationale**: <why this was chosen>
- **Alternatives Considered**: <rejected options>
- **Constraint**: ALL specs MUST use this persistence choice. No spec may introduce a different database or ORM without revising this ADR first.

### ADR-002 — Inter-Spec Communication Style
- **Decision**: <e.g., direct function calls / event bus / in-process message queue>
- **Rationale**: <why>
- **Constraint**: Specs communicate ONLY through their CONTRACT section (see Phase 2 spec template). No spec may directly access another spec's internal implementation.

### ADR-003 — Authentication & Authorization
- **Decision**: <e.g., JWT via python-jose>
- **Constraint**: All protected routes/functions must use this mechanism.

### ADR-00N — <Decision Name>
- **Decision**: ...
- **Constraint**: ...

> Add new ADRs as the project evolves. Never delete an ADR — mark it as superseded and add a new one.

## Acceptance Criteria
Each AC must be independently verifiable (pass/fail).
- AC-1: <technical condition, e.g., "Docker build succeeds">
- AC-2: <technical condition, e.g., "Database encryption key is verified">

## Validation Mandate
Slice 00 is NOT complete until:
1. `docs/<domain>/evals/integration/00-environment.eval.py` (or equivalent) is written.
2. `docs/<domain>/evals/results/integration/00-environment.result.md` contains evidence of verification for every AC, **including actual log output or terminal snippets from the verification run.**

## Technology Conflict Protocol
When a new slice reveals that a better technology choice exists than what is recorded in an existing ADR:
1. DO NOT silently implement the new technology in the new spec.
2. Raise a conflict note to the programmer:
   > "ADR-00X conflict detected in Slice NN — <describe: current decision vs. better option>. Recommend updating ADR-00X before proceeding."
3. WAIT for programmer approval.
4. On approval: update the ADR, mark all affected specs for review in roadmap.md under a `## ADR Revision Debt` section.
5. Only then implement the new technology in the current and affected specs.

> This prevents two specs from independently choosing conflicting technologies and ensures every technology decision is made once, recorded once, and applied consistently.

## Change Log
- [YYYY-MM-DD]: Initial environment setup.
- [YYYY-MM-DD]: ADR-001 updated — <reason>.
```

---

#### Slice 01+ — Feature Spec Template (Standard Template)

Every feature spec follows this template. The key principle: **INTERNAL sections are private. CONTRACT sections are the only surface other specs may depend on.**

```
## Overview
1-2 sentence summary of what and why. Keep it concise.

## CONTRACT
<!-- ------------------------------------------------------------------ -->
<!-- This section is PUBLIC. Other specs may ONLY reference items here.  -->
<!-- Keep this section stable. Any change here is a breaking change.     -->
<!-- ------------------------------------------------------------------ -->

### Callable Interface
<!-- Describe every function, method, or callable this spec exposes to other specs.
     This is NOT always an API — it may be a plain function call, a class method,
     a utility, or a callback. Define the signature precisely. -->

- `functionName(param: ParamType): ReturnType`
  - param: <description>
  - returns: <description>
  - throws: `ErrorType` when <condition>

### Data Shape (if applicable)
<!-- Shared types or schemas another spec may consume.
     Use TypeScript-style typing or Python dataclass notation as appropriate. -->
```
type EntityName = {
  id: string
  fieldName: FieldType
}
```

### Events / Callbacks (if applicable)
<!-- If this spec emits events or accepts callback hooks, define them here. -->
- `onEventName(payload: PayloadType): void` — emitted when <condition>

### Error Contract
<!-- Every error type this spec can surface to its callers. -->
- `NotFoundError`: raised when <entity> does not exist
- `ValidationError`: raised when <condition>

---

## INTERNAL
<!-- ------------------------------------------------------------------ -->
<!-- Everything below is PRIVATE to this spec.                          -->
<!-- Other specs MUST NOT import, call, or depend on anything here.     -->
<!-- Internal implementation can change freely without affecting others. -->
<!-- ------------------------------------------------------------------ -->

### Technical Specification
List language, environment, packages, and technical details used to implement this spec.
Must conform to all ADRs in Slice 00.

### Acceptance Criteria
- AC-1: <testable condition>
- AC-2: <testable condition>

### Subtasks (Static Definitions)
Each subtask must be descriptive, explaining WHAT is being done and WHY (technical rationale).
1. **<Subtask Title>**: <Detailed description of implementation steps> — <Rationale: Why this approach is used>.
2. **<Subtask Title>**: ...

### Out of Scope
Explicitly list what this spec does NOT cover.
```

#### Spec Encapsulation Rules
- **Dependency Rule**: When Slice NN depends on Slice MM, it may ONLY reference items defined in Slice MM's `## CONTRACT` section. Reading, importing, or calling anything from Slice MM's `## INTERNAL` section is PROHIBITED.
- **Stability Rule**: Changes to a spec's `## CONTRACT` are breaking changes. Before modifying a CONTRACT, identify all specs that depend on it and flag them for review in roadmap.md.
- **Internal Freedom Rule**: Changes to a spec's `## INTERNAL` section are safe by default — they cannot break other specs as long as the CONTRACT is preserved.
- **Contract-First Workflow**: When writing a new spec that other specs will depend on, write the `## CONTRACT` section first and get programmer approval before designing the `## INTERNAL` section. Other specs can begin referencing the contract immediately without waiting for the implementation to be complete.

#### Acceptance Criteria Rules
- **Rule of Testability (Hard Rule)**: Each AC MUST be independently verifiable (pass/fail) via code, system state, or observable behavior.
- Avoid vague language like "works", "properly", "correctly". If an AC is not testable → it MUST be rewritten.
- **Rule of Mapping (Hard Rule)**: Each Spec file MUST have exactly one corresponding Eval Script in `docs/<domain>/evals/`.
- **Unified Eval Script**: All ACs for a spec (regardless of whether they are FUNCTION, INTEGRATION, or E2E) are verified within a single script named `NN-feature.eval.py`.
- **Rule of Robustness**: Do NOT rely only on functional tests for system behavior. Include failure scenarios (invalid inputs, timeouts, DB down) for every spec.
- **Rule of Manual Verification (Optional Exception)**: Automated testing is the absolute mandate for all functional and structural requirements. However, manual verification by the programmer is PERMITTED for:
  - **Visual Aesthetics**: Colors, layout alignment, typography, and "polish."
  - **Subjective UX**: The "feel" of TUI responsiveness, interactive feedback, and animations.
  - **Hardware/Env Edge Cases**: Unique laptop GPU passthrough or OS-specific terminal rendering issues that are impractical to automate.
  - **Nuance/Tone**: Subjective AI response quality that escapes objective eval logic.
  - **Requirement**: Any AC verified manually must be explicitly marked as `(MANUAL)` in the spec and documented in the results file with a brief observation note.
- Each AC must be numbered: AC-1, AC-2, AC-3 ...
- Ambiguous ACs are PROHIBITED — flag and rewrite.

#### Static Definition Rule
- Micro-spec files are technical blueprints, NOT task trackers.
- **NO CHECKBOXES**: Use numbered lists (1., 2.) for subtasks. Never use `[ ]` or `[x]`.
- **NO STATUS**: Do not include "Status: Pending/Completed" fields.
- All tracking, checkmarks, and status updates belong ONLY in `roadmap.md`.

#### Approval & Coding Protocol
- Present each micro spec to the programmer and wait for approval before coding.
- **Spec Verification Rule:** For every vertical slice, the AI must present the micro-spec and WAIT for the user to explicitly verify the spec and issue a "proceed" command before starting any implementation or environment setup.
- **Subtask-by-Subtask Execution Rule:** During implementation, the AI MUST execute work sequentially, one subtask at a time. After completing each subtask (including its local verification), the AI must summarize the progress and confirm before moving to the next subtask. Implementing the entire spec in a single step is STRICTLY PROHIBITED.
- **Sequential Block Rule (Hard Rule):** The AI is STRICTLY PROHIBITED from starting the next slice (proposing breakdown, writing spec, or starting implementation) until the current slice has been explicitly marked as `[x] UAT verified` by the programmer in `roadmap.md`.
- Workflow is strictly: Breakdown Approved → Spec Written → Spec Approved → Execute Subtask 1 → Update Roadmap → Execute Subtask 2 → Update Roadmap ... → Write Evals → User UAT → Next Slice.
- Never skip or reverse steps.
- After a slice is complete and verified by the programmer via UAT, present the next slice's spec for approval before starting it.

---

### Phase 3 — Handling New Requirements Mid-Development
When something new comes up during development (new requirement, edge case, scope change), follow this exact protocol before doing anything:

#### Step 1 — Fit Check (MANDATORY)
Before creating anything, ask:

```
A new requirement has come up: <describe it>.

Option A — It fits into existing Slice NN — <Name> under AC-X.
Option B — It does not fit any existing slice and requires a new slice.

Which is correct — should I update the existing spec or propose a new slice?
```

WAIT for programmer confirmation. Never self-decide.

#### Step 2a — If It Fits an Existing Slice
Update in this exact order — do not skip any step:
1. Update the micro spec file (add/modify ACs, subtasks, out of scope).
2. Archive the old version to docs/<domain>/spec/history/ if the change is significant.
3. Add a ## Change Log entry at the bottom of the spec noting what changed and why.
4. Flag all evals linked to this spec as @status: deprecated immediately.
5. Update roadmap.md to reflect the spec change.
6. Inform the programmer: "Spec updated. Linked evals are now deprecated and need review before CI can pass."

#### Step 2b — If It Requires a New Slice
1. Propose the new vertical slice using the Phase 1 breakdown format.
2. Clarify where it fits in the sequence — does it slot in before, after, or between existing slices?
3. Wait for programmer approval.
4. On approval: create the new micro spec file, add it to roadmap.md, create eval stubs.
5. Do NOT write code until spec is approved.

#### PROHIBITED Mid-Development
- Silently adding scope to existing specs without flagging the programmer.
- Creating a new spec file without first checking if it fits an existing slice.
- Writing code for a new requirement before the spec is approved.
- Leaving evals in @status: stable after their linked spec has changed.

---

### Roadmap Rules
Concept: One roadmap.md per domain tracks all spec progress and eval debt.

#### File Rules
- File location: docs/<domain>/spec/roadmap.md
- One roadmap.md per domain — never combine domains.

#### Entry Template

```
## NN — <Feature Name> [Status: Pending / In Progress / Completed]
- [ ] Subtask 1
- [ ] Subtask 2
- [ ] Evals written
- [ ] Evals stable and passing
- [ ] UAT verified
```

#### Rules
- Never delete completed items — check them off only.
- Update roadmap.md at the end of every session — never leave it stale.
- **Full Visibility Rule:** The roadmap must reflect the high-level plan for ALL slices from the start of the project to ensure the user can follow the overall trajectory. Detailed subtasks are added/refined as each slice's spec is created, but the roadmap should always contain the best current estimate for all future tasks.
- **Single Source of Truth Rule:** `roadmap.md` is the ONLY place where progress is tracked. Micro-spec files are technical definitions and must NOT contain checkmarks or status updates.
- A central roadmap.md maps 1:1 to spec files. Each spec = H2. Each subtask = checklist item.
- Never delete old specs. Move outdated versions to history/ to preserve decisions.
- Every spec change must be reflected in roadmap.md in the same session.
- Maintain an ## Eval Debt section at the bottom:

```
## Eval Debt
- [ ] <feature>.eval.ts — deprecated, reason: <spec change summary>
- [ ] <feature>.eval.ts — wip, complete after: <pending feature>
```

- Eval Debt must be zero before any UAT deployment.
- **User-Led UAT Rule (Hard Rule):** The `[ ] UAT verified` checklist item in `roadmap.md` MUST ONLY be checked off by the programmer. The AI is STRICTLY PROHIBITED from marking UAT as complete.

---

### ADR Revision Debt (in roadmap.md)
When an ADR in Slice 00 is updated, add entries here for every spec that must be reviewed for compliance:

```
## ADR Revision Debt
- [ ] Slice 02 — <Name>: review for ADR-001 revision (changed from MongoDB to PostgreSQL)
- [ ] Slice 03 — <Name>: review for ADR-001 revision
```

ADR Revision Debt must be zero before any UAT deployment.


*Last updated: [Update this date each session]*
R-001 revision
```

ADR Revision Debt must be zero before any UAT deployment.


*Last updated: [Update this date each session]*
