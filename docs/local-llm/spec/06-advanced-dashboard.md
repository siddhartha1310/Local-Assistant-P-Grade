# Slice 06 — Advanced TUI Dashboard (Security & Performance)

## Overview
Enhances the TUI with a multi-pane dashboard showing real-time performance metrics, PII masking statistics, and security audit logs.

## CONTRACT

### Callable Interface
- `Dashboard.update_metrics(metrics: dict): void`
  - Refreshes the metrics display with current throughput and latency data.
- `Dashboard.toggle_secure_mode(active: bool): void`
  - Switches the interface between focus modes (e.g., Chat vs. Security Dashboard).

### Events / Callbacks
- `on_dashboard_refresh()`: Emitted when the background worker updates the local metric cache.

---

## INTERNAL

### Technical Specification
- **Framework**: Textual `DataTable`, `Sparkline`, and `ProgressBar` widgets.
- **Data Source**: Real-time polling of SQLCipher `metrics` and `audit_log` tables.
- **Performance**: Async refresh logic to prevent blocking the main chat UI.

### Acceptance Criteria
- AC-1 (E2E): The TUI Dashboard correctly displays average model latency and tokens per second over time.
- AC-2 (E2E): The Audit Pane shows the last 10 security events with real-time updates (5s polling).
- AC-3 (E2E): The PII Masking Pane visualizes the count of redacted entities per session using a Sparkline.
- AC-4 (MANUAL): The dashboard must maintain 60 FPS responsiveness during high-volume generation.
- AC-5 (INTEGRATION): Metrics aggregation must account for both A/B testing and single-model modes.

### Subtasks (Static Definitions)
1. **Multi-Pane Dashboard Layout**: Refactor the main TUI screen into a dockable multi-pane layout using Textual's `Static` and `Container` components.
2. **Real-time Performance Metrics**: Implement visual indicators (Sparklines/ProgressBars) for model latency and throughput.
3. **Security & PII Visualization**: Develop a specialized view for audit trail monitoring and masking statistics.
4. **Async Data Polling**: Implement a background worker to poll and aggregate SQLCipher metrics without blocking the event loop.
5. **UI Responsiveness Optimization**: Profile and optimize widget updates to ensure 60 FPS responsiveness under load.

### Out of Scope
- Interactive chart manipulation (pan/zoom).
- Remote dashboard access (Local TUI only).
- Historical metric trend analysis beyond the current session's runtime.

## Change Log
- [2026-04-04]: Finalized Spec based on roadmap subtasks.
