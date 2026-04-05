FROM python:3.12-slim-bookworm

# Install build dependencies for SQLCipher and SpaCy
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libssl-dev \
    tcl-dev \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install UV for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# Copy dependency files
COPY pyproject.toml .
COPY README.md .

# Install dependencies using UV
RUN uv sync --no-install-project --no-cache

# Download SpaCy model for PII masking (en_core_web_sm is small and fast)
RUN uv run python -m spacy download en_core_web_sm

# Copy the rest of the application
COPY src/ ./src/
COPY prompts/ ./prompts/
COPY docs/ ./docs/

# Install the project itself
RUN uv sync --no-cache

# Setup volumes and directories
RUN mkdir -p /app/data /app/prompts && chmod 700 /app/data

# Entry point script
COPY entrypoint.sh /app/entrypoint.sh
RUN sed -i 's/\r$//' /app/entrypoint.sh && chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
