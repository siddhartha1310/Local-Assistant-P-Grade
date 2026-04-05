# Slice 01 — Secure CLI, RBAC Login & Audit Trail

## Overview
Implements the core security layer: a multi-pane TUI for secure login using local RBAC (SQLCipher) and an immutable audit trail.

## CONTRACT

### Callable Interface
- `authenticate_user(username: str, password: str): UserSession`
  - Validates user credentials against the encrypted SQLCipher database.
  - returns: `UserSession` object containing user metadata.
  - throws: `AuthenticationError` on invalid credentials or database failure.

- `log_audit_event(action: str, details: dict, user_id: int, status: str): void`
  - Records a security-relevant event into the immutable audit trail.
  - action: Type of event (e.g., "USER_LOGIN").
  - details: Structured data about the event.
  - status: "SUCCESS" or "FAILURE".
  - throws: `AuditFailure` if writing to the log fails.

- `get_recent_audit_logs(limit: int): list[tuple]`
  - Retrieves the most recent security logs for display in the TUI.
  - returns: List of log records (timestamp, username, action, status).

### Data Shape
```python
@dataclass
class UserSession:
    username: str
    role: str
    user_id: int
```

### Error Contract
- `AuthenticationError`: Raised when login fails.
- `AuditFailure`: Raised when an audit event cannot be persisted.

---

## INTERNAL

### Technical Specification
- **Environment**: Python 3.12, Textual, SQLCipher3.
- **Security**: Argon2 hashing via `passlib` for password verification.
- **Persistence**: `users`, `roles`, and `audit_log` tables in `secure_vault.db`.
- **UI Components**: `LoginScreen`, `MainDashboard`, `AuditPane`.

### Acceptance Criteria

### Authentication
- **AC-1 (E2E)**: TUI launches correctly and presents a `LoginScreen` as the initial view.
- **AC-2 (INTEGRATION)**: Authentication validates against Argon2 hashes in the encrypted `users` table.
- **AC-3 (E2E)**: Successful login triggers a state change to the `MainDashboard`.

### Auditing
- **AC-4 (INTEGRATION)**: Every login attempt (success/failure) is persisted in the `audit_log` table with timestamps.
- **AC-5 (E2E)**: The `MainDashboard` display includes an Audit Pane that reloads every 5 seconds.

### Model Control
- **AC-6 (E2E)**: Dashboard allows switching between `phi3:mini` and `tinyllama` via a `Select` widget.

### Failure Scenarios
- **AC-7 (INTEGRATION)**: Login with non-existent user or invalid password must return a clear `AuthenticationError` and log a failure.
- **AC-8 (INTEGRATION)**: If the database is locked or inaccessible, authentication must fail gracefully with a system-level error log.

### Subtasks (Static Definitions)
1. **RBAC Schema Implementation**: Create `users` and `roles` tables with constraints in SQLCipher.
2. **Password Hashing Logic**: Integrate `passlib[argon2]` for secure credential storage and verification.
3. **Audit Logger**: Implement the `log_audit_event` function ensuring it uses the same encrypted connection.
4. **TUI Login Flow**: Develop the `LoginScreen` using Textual's `Screen` and `Input` components.
5. **Session Management**: Implement the `UserSession` lifecycle within the TUI application state.

### Out of Scope
- OAuth2/OIDC integration (Local RBAC only).
- Remote log shipping (Audit logs are local only).

## Change Log
- [2026-04-04]: Refactored to align with `SKILLS/microspec.md` standards. Added CONTRACT and INTERNAL sections.
