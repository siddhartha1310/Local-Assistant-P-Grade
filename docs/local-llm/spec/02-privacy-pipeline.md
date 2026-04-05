# Slice 02 — Privacy Pipeline & File Ingestion

## Overview
Implements the privacy-first ingestion layer: a PII masking pipeline and a secure file extraction service.

## CONTRACT

### Callable Interface
- `mask_text(text: str, entities: list[str] = None): str`
  - Scans and redacts PII from the given text using Presidio.
  - returns: Redacted text with placeholders (e.g., `<EMAIL_ADDRESS>`).
  - throws: None (logs error and returns original text or error placeholder).

- `extract_from_file(file_path: str): str`
  - Extracts raw text from `.pdf`, `.txt`, or `.csv` files.
  - returns: Extracted text string.
  - throws: `FileNotSupportedError` if the extension is invalid.
  - throws: `ExtractionError` on read or processing failure.

### Data Shape
- Redaction placeholders follow the format: `<ENTITY_TYPE>` (e.g., `<PHONE_NUMBER>`, `<PERSON>`).

### Error Contract
- `FileNotSupportedError`: Raised when a file with an unsupported extension is provided.
- `ExtractionError`: Raised when file content cannot be read or processed.

---

## INTERNAL

### Technical Specification
- **PII Detection**: Microsoft Presidio (Analyzer + Anonymizer).
- **NLP Backend**: SpaCy (`en_core_web_sm` model).
- **File Extraction**: `pypdf` (PDF), `pandas` (CSV), native Python `open` (TXT).
- **Custom Patterns**: Regex-based recognizers for project-specific formats (e.g., phone numbers).

### Acceptance Criteria

### PII Masking
- **AC-1 (FUNCTION)**: `mask_text` replaces Emails, IPs, and Phone Numbers with specific placeholders (e.g., `<EMAIL_ADDRESS>`).
- **AC-2 (FUNCTION)**: PII detection must be case-insensitive and handle common variations (e.g., different phone formats).

### File Extraction
- **AC-3 (INTEGRATION)**: `extract_from_file` successfully reads text from `.txt`, `.pdf`, and `.csv`.
- **AC-4 (INTEGRATION)**: CSV extraction maintains row structure in the resulting text string.

### TUI Integration
- **AC-5 (E2E)**: The TUI provides a "PII Masking" toggle that immediately enables/disables redaction for subsequent ingestions.
- **AC-6 (E2E)**: Successful file ingestion displays a redacted preview in the TUI chat area.

### Failure Scenarios
- **AC-7 (FUNCTION)**: Attempting to ingest an unsupported file type must raise a `FileNotSupportedError`.
- **AC-8 (INTEGRATION)**: If a file is corrupted or unreadable, the system must log an `ExtractionError` and notify the user via the TUI.

### Subtasks (Static Definitions)
1. **Presidio Integration**: Setup `PIIMaskingService` with standard and custom entity recognizers.
2. **File Extractor Framework**: Implement `extract_from_file` using specialized libraries for each supported type.
3. **Regex Recognizer Development**: Create specific regex patterns for local phone number and IP address formats.
4. **TUI Ingestion Modal**: Develop a file selection dialog in Textual that integrates with the extraction and masking services.
5. **Masking Toggle State**: Manage the PII masking state within the TUI `MainDashboard`.

### Out of Scope
- OCR for scanned PDFs or images.
- Redaction of visual elements in images.

## Change Log
- [2026-04-04]: Refactored to align with `SKILLS/microspec.md` standards. Added CONTRACT and INTERNAL sections.
