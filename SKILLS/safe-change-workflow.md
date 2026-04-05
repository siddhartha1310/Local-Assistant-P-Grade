# safe-change-workflow.md — Safe Code Change Workflow
Process for modifying existing code in a large codebase with minimal unintended side effects.
Location: SKILLS/ directory.

TRIGGER: This workflow is MANDATORY for any modification to existing code.
It is NOT required for net-new code with no existing callers.

---

### Artifact Locations
All artifacts produced by this workflow live inside the domain being changed.

```
docs/
└── <domain>/
    ├── CHANGE_LOG.md                        ← updated in Phase 4
    ├── spec/
    │   ├── roadmap.md                       ← updated in Phase 4 (eval debt)
    │   └── <feature>.md                     ← updated if AC changes
    ├── evals/
    │   ├── <feature>.eval.ts                ← new/updated evals from Phase 2
    │   └── fixtures/
    │       ├── dev/
    │       └── uat/
    └── impact/
        ├── <task-name>-impact-map.md        ← one per task, created in Phase 1
        └── <task-name>-baseline.md          ← one per task, created in Phase 1
```

Rules:
- impact/ folder is created per domain on first use.
- One impact map and one baseline per task/change — not per symbol.
- A task may involve multiple symbols/files — all go into the same impact map.
- Impact artifacts are never deleted — they serve as audit trail.
- When a change is complete, add a ## Resolution note at the bottom of the impact map.

---

### Recommended Toolchain by Language

| Language | Reference Finder | Static Analysis | Contract Checker |
|----------|-----------------|-----------------|-----------------|
| TypeScript | `tsc --noEmit`, `ts-prune`, LSP | ESLint, `ts-unused-exports` | TypeScript strict mode |
| JavaScript | `ripgrep (rg)`, ESLint | ESLint, Knip | JSDoc types |
| Python | `pyright`, `pylsp` | `ruff`, `mypy` | `mypy --strict` |
| Go | `gopls`, `go vet` | `staticcheck` | Go interfaces |
| Any language | `ripgrep (rg)` | — | — |

#### Why NOT ctags
ctags only indexes where a symbol is DEFINED — not where it is CALLED, imported, or depended on.
It has no understanding of type contracts, re-exports, or dynamic references.
It will silently miss usages and give a false sense of complete impact analysis.
Use ctags ONLY as a last resort when no language tooling or LSP is available.
Preferred fallback for any language: `ripgrep (rg)` — faster, more complete, regex-capable.

---

### Phase 1 — Understand Before Touching

#### Step 1.1 — Identify the Change Scope
Before any analysis, define the full scope of the task as a single unit:
- List all files, functions, types, and interfaces that will be touched.
- This is the change scope — all impact analysis is done for this scope as a whole, not per symbol.

```
Change Scope — <task name>
Files to be modified:
- <domain>/path/to/file.ts — <what will change>
- <domain>/path/to/file.ts — <what will change>

Symbols affected: <comma separated list>
```

If the scope is unclear or too large → ask the programmer to narrow it before proceeding.

#### Step 1.2 — Find All References for the Change Scope
For all symbols in the change scope combined, find every location they are:
- Called (function/method calls)
- Imported or re-exported
- Extended or implemented (interfaces, classes)
- Referenced in types, generics, or contracts
- Used in config, env, or external-facing APIs

Use the best available tool:
- TypeScript/JavaScript: `tsc --noEmit` + `rg "<symbol>" --type ts` per symbol in scope.
- Python: `pyright` + `rg "<symbol>" --type py`.
- Any language: `rg "<symbol>"` as minimum baseline.
- If LSP available: use "Find All References" per symbol — most accurate.

Never rely on memory or assumptions about where a symbol is used.

#### Step 1.3 — Build Impact Map
One impact map for the entire task. Save to: docs/<domain>/impact/<task-name>-impact-map.md

```
# Impact Map — <task name>
Date: [YYYY-MM-DD]
Change scope: <brief description of what is being changed and why>

## Symbols in Scope
- <symbol 1> in <file>
- <symbol 2> in <file>

## HIGH IMPACT (core logic / shared modules / public API)
- <domain>/path/to/file.ts : line XX — <which symbol, how it is used>

## MEDIUM IMPACT (feature-level / single domain usage)
- <domain>/path/to/file.ts : line XX — <which symbol, how it is used>

## LOW IMPACT (isolated / test-only / config-only)
- <domain>/path/to/file.ts : line XX — <which symbol, how it is used>

## CONTRACTS AFFECTED (types, interfaces, API schemas)
- <domain>/path/to/file.ts : line XX — <brief description>

## UNUSED SYMBOLS
- <symbol> — confirmed unused: yes / no

## Resolution
(filled in after change is complete)
- Change made: [YYYY-MM-DD]
- Outcome: <summary>
- Regressions: none / <description>
```

Present the impact map to the programmer and WAIT for acknowledgement before proceeding.

#### Step 1.4 — Impact Classification Rules

| Classification | Criteria |
|---------------|----------|
| HIGH | Shared modules, core business logic, public APIs, auth, payments, data pipelines |
| MEDIUM | Single feature domain, internal service, non-critical path |
| LOW | Test files, config files, isolated utilities with no downstream callers |
| UNUSED | Zero references — no callers, no imports anywhere |

#### Step 1.5 — Snapshot Baseline Behavior
One baseline snapshot for the entire task. Save to: docs/<domain>/impact/<task-name>-baseline.md

```
# Baseline Snapshot — <task name>
Date: [YYYY-MM-DD]

## Current Behavior
<Brief description of what the affected code currently does as a whole>

## Eval Status
Existing evals passing: Y / N
Eval files covering this change scope:
- docs/<domain>/evals/<feature>.eval.ts — <pass/fail count>

## Known Side Effects
<list any known side effects or "none">

## Post-Change Comparison
(filled in after change is complete)
- Behavior preserved: yes / no
- Intentional changes: <description or "none">
```

---

### Phase 2 — Plan the Change

#### Step 2.1 — Present Change Proposal to Programmer

```
Change Proposal — <task name>

What is changing: <description>
Why: <reason>

Impact Summary:
- HIGH impact zones: <count> files
- MEDIUM impact zones: <count> files
- LOW impact zones: <count> files
- Contracts affected: yes / no

Risks identified:
- <risk 1>
- <risk 2>

Proposed eval coverage:
- <eval 1 targeting which AC>
- <eval 2 targeting which AC>

Artifacts created:
- docs/<domain>/impact/<task-name>-impact-map.md
- docs/<domain>/impact/<task-name>-baseline.md

Recommended approach: <narrowest safe change description>

Do you approve this change plan?
```

WAIT for programmer approval. Do NOT write any changed code without explicit confirmation.

#### Step 2.2 — Generate Targeted Evals
- For every HIGH and MEDIUM impact reference: generate or update evals in docs/<domain>/evals/.
- Evals must test behavioral contracts — not implementation details.
- Tag all new evals @status: wip until change is complete and verified.
- For LOW impact references: verify existing evals cover them. If not, flag to programmer.
- For UNUSED symbols: do not generate evals. See Unused Symbol Protocol.

#### Step 2.3 — Stop and Ask Rules (MANDATORY)
Stop immediately and ask the programmer before proceeding if ANY of these are true:
- More than 3 HIGH impact files found across the change scope.
- A public API, webhook, or external contract is affected.
- A database schema, migration, or ORM model is involved.
- The change scope touches more than 2 domains.
- A type signature or interface contract is changing.
- You are unsure how a dependent file uses a symbol in scope.
- Baseline evals are already failing before the change.

---

### Phase 3 — Execute the Change

#### Step 3.1 — Change Execution Rules
- Make the narrowest possible change — do not refactor unrelated code in the same pass.
- If contracts change: update interface first → then implementations → then callers. In that order.
- If multiple files need updating: do them one file at a time, verify after each.

#### Step 3.2 — Run Targeted Evals Immediately
After the change, before running the full suite:
- Run only the evals generated in Phase 2.
- If any targeted eval fails → STOP. Fix the targeted failure before running full suite.
- Report result to programmer before continuing.

#### Step 3.3 — Run Full Suite
After all targeted evals pass:
- Run the full eval suite.
- Any previously passing eval that now fails = regression. STOP and flag immediately:

```
Regression Detected:
- Eval: docs/<domain>/evals/<file>
- AC: <which acceptance criterion>
- Before change: PASS
- After change: FAIL
- Likely cause: <description>

Do not proceed until programmer reviews this regression.
```

#### Step 3.4 — Update Baseline
Update docs/<domain>/impact/<task-name>-baseline.md — Post-Change Comparison section:
- Confirm all previously passing evals still pass.
- Document any intentional behavioral changes explicitly.

---

### Phase 4 — Validate & Document

#### Step 4.1 — Confirm No Behavioral Regression
Only mark the change complete when all of these are checked:
- [ ] All HIGH impact evals pass
- [ ] All MEDIUM impact evals pass
- [ ] Full suite passes
- [ ] Baseline behavior preserved (or intentional change documented)
- [ ] Programmer has confirmed the change is acceptable

#### Step 4.2 — Update CHANGE_LOG.md
File: docs/<domain>/CHANGE_LOG.md
Entry must include:
- Task name and what changed
- Impact classification (HIGH/MEDIUM/LOW)
- Number of dependent files affected
- Any contracts or types modified
- Reference to: docs/<domain>/impact/<task-name>-impact-map.md

#### Step 4.3 — Eval & Spec Hygiene
- If contracts changed: flag all linked evals as @status: deprecated.
- If new behavior introduced: update the linked spec AC and re-present for approval.
- Update roadmap.md Eval Debt section for any deprecated evals.
- Fill in ## Resolution in docs/<domain>/impact/<task-name>-impact-map.md.

---

### Unused Symbol Protocol
When a symbol in scope has zero references, ask:

```
Symbol <name> appears to have no callers or importers.

Options:
A — Safe to change (no eval needed, low risk)
B — Candidate for cleanup/deletion
C — I am wrong — symbol IS used via dynamic import, reflection, or external consumer

Which is correct?
```

WAIT for programmer to confirm. Never delete an unused symbol without explicit instruction.
If B confirmed: note it in the impact map under ## UNUSED SYMBOLS with reason it is safe to remove.

---

### Failure Safeguards

| Scenario | AI Action |
|----------|-----------|
| Change scope is unclear or too large | Stop, ask programmer to narrow scope first |
| Impact map shows >3 HIGH impact files | Stop, present impact map, do not proceed |
| Baseline evals failing before change | Stop, flag pre-existing failures, do not proceed |
| Type error introduced after change | Stop, revert narrowly, report exact error |
| Full suite regression detected | Stop immediately, do not push, report regression |
| External API contract affected | Stop, escalate for contract versioning decision |
| Cannot determine how a dependent file uses a symbol | Stop, ask programmer — never guess |
| ctags used as primary tool | Warn — results may be incomplete, use rg or tsc instead |

---
