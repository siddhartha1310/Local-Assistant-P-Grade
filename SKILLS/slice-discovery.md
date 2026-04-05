# slice-discovery.md — Phase 1 Slice Discovery Skill

Defines how the AI must conduct Phase 1 — High-Level Breakdown — for any new feature or bug fix request.
This skill extends microspec-v2.md and must be used alongside it.
Location: project root alongside microspec-v2.md, GEMINI.md, MEMORY.md, skills.md.

---

## Purpose

microspec-v2.md defines the rules for spec creation. This skill defines the exact thinking sequence
the AI must follow BEFORE proposing any breakdown — ensuring ADR compliance, behavior clarity,
and spec continuity are verified first, regardless of project state.

---

## Step 0 — Project State Detection (MANDATORY FIRST STEP)

Before any breakdown or analysis, the AI must determine the project state by answering
three questions:

**Q1 — Codebase**: Does existing source code exist in the project?
- No existing code → Codebase: None
- Code exists → Codebase: Exists

**Q2 — Spec**: Does `docs/<domain>/spec/roadmap.md` exist with at least one slice?
- No roadmap or no slices → Spec: None
- Slices exist → Spec: Exists

**Q3 — Intent**: Is the task a new feature or a bug fix?
- Adding new functionality → Intent: New Feature
- Fixing broken behavior → Intent: Bug Fix

The AI must state its finding explicitly before proceeding:
> "Codebase: [None/Exists] | Spec: [None/Exists] | Intent: [New Feature/Bug Fix] → Following Path [A/B/C/D/E]."

Path selection:

| Codebase | Spec   | Intent      | Path |
|----------|--------|-------------|------|
| None     | None   | New Feature | A — Fresh Project                   |
| Exists   | Exists | New Feature | B — Existing Project, New Feature   |
| Exists   | None   | New Feature | C — Retro-Spec, New Feature         |
| Exists   | None   | Bug Fix     | D — Retro-Spec, Bug Fix             |
| Exists   | Exists | Bug Fix     | E — Existing Project, Bug Fix       |

---

## Slice Validity Tests (MANDATORY)

Before presenting any breakdown, mentally apply all four tests to each proposed slice:

| Test         | Question to ask                                          | Bad signal                                 |
|--------------|----------------------------------------------------------|--------------------------------------------|
| Vertical     | Does it touch all layers needed to work end-to-end?      | "This is just the DB schema"               |
| Demonstrable | Can I show it running without any other slice built?     | "This needs Slice 03 to be testable"       |
| Atomic       | Is there exactly one clear deliverable?                  | "This builds the whole user module"        |
| Ordered      | Can I justify why it comes before the next slice?        | Two slices with no dependency between them |

---

## Information Requirement (What the Programmer Must Provide)

The quality of the breakdown depends on the quality of the feature description. Before running any path, ensure the feature description answers:

- **What problem does this solve?** (behavior, not implementation)
- **Who uses it?** (end user / admin / another module / background job)
- **What does "done" look like?** (what can they do after that they couldn't before)
- **Any hard constraints?** (must use X, must be real-time, must be offline-capable)

Technology choices, internal structure, and test strategy belong in Slice 00 and individual specs — keep the feature description behavior-level only.

---

## Path A — Fresh Project, New Feature
*(Codebase: None | Spec: None | Intent: New Feature)*

### Step 1 — Behavior Inventory
List every user-facing or system-observable behavior the feature involves.
Think in verbs: "user can X", "system does Y when Z".
Do NOT list infrastructure tasks (e.g., "set up database", "create API routes") as behaviors —
these are implementation details, not behaviors.

### Step 2 — ADR Candidates
Before proposing slices, identify every cross-cutting technology decision that must be
settled before any vertical spec can be written. For each candidate, document:
- Decision category (persistence, auth, inter-module communication, etc.)
- Recommended choice and rationale
- Alternatives considered and why they were rejected

These become the ADRs recorded in Slice 00.

### Step 3 — Proposed Breakdown
Present the breakdown using the Phase 1 format from microspec-v2.md.
Extend each slice entry with:
- `Depends on:` — which prior slice this requires
- `Testable when:` — the observable condition that confirms this slice is complete

WAIT for programmer approval before creating any spec file or writing any code.

---

## Path B — Existing Project, New Feature
*(Codebase: Exists | Spec: Exists | Intent: New Feature)*

Before running any steps, the AI must read:
1. `docs/<domain>/spec/00-environment.md` — internalize all existing ADRs.
2. `docs/<domain>/spec/roadmap.md` — understand all existing slices and their status.

### Step 1 — ADR Compliance Check
Review the new feature requirements against all existing ADRs in Slice 00.
Flag any tension between the feature and an existing ADR:
> "This feature might benefit from X, but ADR-001 mandates Y."
Do NOT resolve conflicts unilaterally — surface them only and wait for programmer direction.
If no conflicts exist, state: "No ADR conflicts detected."

### Step 2 — Behavior Inventory
List every new user-facing or system-observable behavior the feature adds.
Cross-reference against existing slices — if any behavior already exists in a completed
or in-progress slice, flag the overlap explicitly rather than duplicating it.

### Step 3 — Proposed Breakdown
Present the breakdown using the Phase 1 format from microspec-v2.md.
Extend each slice entry with:
- `Depends on:` — prior slice or existing slice this requires
- `Touches contracts of:` — any existing slice whose CONTRACT this new slice depends on or may affect, and why
- `Testable when:` — the observable condition that confirms this slice is complete

WAIT for programmer approval before creating any spec file or writing any code.

---

## Path C — Retro-Spec, New Feature
*(Codebase: Exists | Spec: None | Intent: New Feature)*

A codebase exists but was never specced. The existing system must be retro-specced into
Slice 00 before any new feature slices are proposed. This ensures all implicit
architectural decisions are locked down before new work is layered on top.

### Step 1 — Codebase Audit
Read the existing codebase and document:
- Language, runtime, frameworks, and key package versions in use
- Folder structure and module boundaries
- Persistence mechanism (database, ORM, file system)
- Inter-module communication patterns (direct calls, events, queues)
- Authentication mechanism, if any
- How the project is run locally and how tests are executed

### Step 2 — Implicit ADR Discovery
From the audit, extract every technology decision already baked into the code.
These are implicit ADRs — they exist in practice even though they were never recorded.
For each implicit ADR:
- State what the decision is
- State what it constrains going forward
- Flag whether it should be kept as-is or is worth reconsidering before new work begins

Flag any implicit decision that conflicts with the new feature requirements:
> "The codebase uses X for persistence, but the new feature may benefit from Y — worth revisiting before we proceed?"
Do NOT resolve — surface only.

### Step 3 — Slice 00 Proposal
Before proposing any new feature slices, propose a Slice 00 that formalizes
the existing environment and all implicit ADRs discovered in Step 2.

WAIT for Slice 00 approval before proceeding to Step 4.
> "Before proposing new feature slices, I need to lock down the existing technical environment
> in Slice 00. Do you approve this scope, or are there decisions you want to revisit first?"

### Step 4 — Behavior Inventory
List every new user-facing or system-observable behavior the new feature adds.
Think in verbs: "user can X", "system does Y when Z".

### Step 5 — Proposed Breakdown
Present the breakdown using the Phase 1 format from microspec-v2.md.
Slice 00 is the retro-spec of the existing system.
Extend each new slice entry with:
- `Depends on:` — prior slice this requires
- `Testable when:` — the observable condition that confirms this slice is complete

WAIT for programmer approval before creating any spec file or writing any code.

---

## Path D — Retro-Spec, Bug Fix
*(Codebase: Exists | Spec: None | Intent: Bug Fix)*

A bug exists in a codebase that was never specced. Per microspec-v2.md, no code may be
touched before a spec exists and is approved. A minimal retro-spec must be created first.

### Step 1 — Bug Scoping
Document the broken behavior precisely:
- **Expected behavior**: What should the system do?
- **Actual behavior**: What is it doing instead?
- **Affected area**: Which file(s), function(s), or module(s) are involved?
- **Reproduction steps**: How to trigger the bug consistently?

### Step 2 — Codebase Audit (affected area only)
Read the broken area of the codebase and document what it is trying to do,
the technology decisions already baked into it, and whether the bug is isolated
to one module or touches cross-cutting concerns.

### Step 3 — Implicit ADR Discovery
From the audit of the affected area, extract implicit ADRs relevant to the fix approach.
Flag any that constrain how the bug can be fixed:
> "The affected area uses X, which means the fix must work within Y."

### Step 4 — Retro-Spec Proposal
Propose a minimal Slice 00 + one feature slice covering the broken functionality:
- Slice 00 formalizes the existing environment and implicit ADRs.
- Slice 01 specifies what the broken feature is supposed to do, with the fix scoped as subtasks.

Extend the slice entry with:
- `Fix scope:` — what the fix will correct
- `Testable when:` — the bug no longer reproduces AND the expected behavior is verified

WAIT for spec approval before writing any fix code.
> "A spec is required before the fix can proceed. Do you approve this retro-spec scope?"

---

## Path E — Existing Project, Bug Fix
*(Codebase: Exists | Spec: Exists | Intent: Bug Fix)*

A bug exists and a spec already covers the affected feature.
The AI must follow the Phase 3 protocol from microspec-v2.md, extended with
a bug classification step before any spec change is made.

### Step 1 — Bug Scoping
Document the broken behavior precisely:
- **Expected behavior**: What should the system do?
- **Actual behavior**: What is it doing instead?
- **Affected area**: Which file(s), function(s), or module(s) are involved?
- **Reproduction steps**: How to trigger the bug consistently?

### Step 2 — Spec Fit Check
Read all existing specs and roadmap.md. Identify which spec owns the broken feature.
Classify the bug into exactly one category:

**Category 1 — AC Gap**
The bug exposes behavior that no existing AC covers. The spec is incomplete.
> "AC-X does not cover this case. The fix requires adding AC-N to Slice NN."
→ Spec must be updated before the fix is written.

**Category 2 — AC Violation**
An AC exists that covers this case, but the implementation fails 