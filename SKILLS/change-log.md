# change-log.md — Change Log Playbook
Single source of truth for how changes are tracked and audited.
Location: project root alongside GEMINI.md, MEMORY.md, skills.md.

---
---

## Change Log Rules
Concept: AI agents move fast. Auditability requires strict, per-change logging.

### File Rules
- File location: docs/<domain>/CHANGE_LOG.md
- One CHANGE_LOG.md per domain.

### What to Log
- Log every production code modification — no exceptions.
- Exclude scratch scripts, temp tests, and experimental files.
- Summary reports must be derived from CHANGE_LOG.md only — never from memory or notes.

### Entry Formats (Choose based on task type)

#### Option A — Build Entry (For new features/slices)
```
### [YYYY-MM-DD] — <Short Title>
- **Files**: `<domain>/path/to/file.ts`, ...
- **Task**: The specific feature or slice being worked on.
- **Implementation**: Step-by-step summary of the logic and changes added.
- **Impact**: What this enables or changes in the system.
```

#### Option B — Fix Entry (For bugs or refactoring)
```
### [YYYY-MM-DD] — <Short Title>
- **File**: `<domain>/path/to/file.ts`
- **Issue**: What was broken or needed.
- **Fix**: What was changed and why.
- **Impact**: What this affects downstream.
```

### Rules
- Never edit or delete past entries.
- If a fix is reverted, add a new entry — do not modify the original.
- Summary reports and retrospectives must be derived from CHANGE_LOG.md only.

---
---

*Last updated: [Update this date each session]*
