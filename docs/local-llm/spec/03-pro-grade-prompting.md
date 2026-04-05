# Slice 03 — Pro-Grade Prompting (Live/Hot-Reload)

## Overview
Implements a "Prompt as Code" system with a hot-reloading watcher for YAML-based prompt templates.

## CONTRACT

### Callable Interface
- `PromptLoader.load_all(): Dict[str, PromptTemplate]`
  - Loads all YAML prompt templates from the configured directory.
  - returns: Dictionary mapping prompt IDs to `PromptTemplate` objects.

- `PromptLoader.get_prompt(prompt_id: str): Optional[PromptTemplate]`
  - Retrieves a specific prompt template by its unique ID.

- `PromptTemplate.render(**kwargs: Any): str`
  - Renders the prompt template using Jinja2 with provided context variables.
  - returns: Fully rendered prompt string.

- `PromptWatcher.start(): void`
  - Initializes the file system observer to watch for changes in the prompts directory.
  - Automatically triggers reloads and registered callbacks on file events.

### Data Shape
```python
@dataclass
class PromptTemplate:
    id: str
    version: str
    description: str
    template: str
    filename: str
    metadata: dict
```

### Events / Callbacks
- `add_callback(callback: Callable): void`
  - Registers a function to be called whenever a prompt file is modified or created.

### Error Contract
- `PromptReloadError`: Logged when a malformed YAML file fails to load (loader skips the file and keeps previous version).

---

## INTERNAL

### Technical Specification
- **Template Engine**: Jinja2 for variable interpolation and logic.
- **Serialization**: PyYAML for prompt template storage on disk.
- **File Watching**: `watchdog` library for cross-platform file system events.
- **Monitoring**: Audit log integration for every reload event.

### Acceptance Criteria

### Loading & Watching
- **AC-1 (INTEGRATION)**: All YAML files in the `prompts/` directory are loaded into memory on application startup.
- **AC-2 (INTEGRATION)**: Modifying, creating, or deleting a YAML file in `prompts/` triggers an automatic reload of the prompt cache within 2 seconds.

### Prompt Logic
- **AC-3 (FUNCTION)**: Prompts support Jinja2 variables (e.g., `{{query}}`, `{{content}}`) and render correctly with user-provided data.
- **AC-4 (INTEGRATION)**: Every successful or failed prompt reload is recorded in the audit log.

### TUI Integration
- **AC-5 (E2E)**: The TUI displays a list of all currently loaded prompts and allows the user to select one for the active session.
- **AC-6 (E2E)**: The TUI prompt list updates automatically when the file watcher detects a change on disk.

### Failure Scenarios
- **AC-7 (FUNCTION)**: Malformed YAML files must not crash the loader; the system should log an error and keep the previous valid version.
- **AC-8 (FUNCTION)**: Requesting a non-existent prompt ID must return a default fallback prompt.

### Subtasks (Static Definitions)
1. **PromptTemplate Model**: Define the dataclass and Jinja2 rendering logic.
2. **YAML Prompt Loader**: Implement the directory scanning and file parsing logic.
3. **Hot-Reload Watcher**: Integrate `watchdog` to monitor the `prompts/` directory and trigger reloads.
4. **TUI Prompt Selector**: Develop a `Select` widget and list view in Textual for managing active prompts.
5. **Watcher-UI Sync**: Implement the callback mechanism to update the TUI state when prompts are reloaded.

### Out of Scope
- Prompt optimization suggestions (e.g., auto-improving prompt text).
- Remote prompt sync (GitHub/S3).

## Change Log
- [2026-04-04]: Refactored to align with `SKILLS/microspec.md` standards. Added CONTRACT and INTERNAL sections.
