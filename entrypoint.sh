#!/bin/bash
set -e

echo "[*] Initializing Secure Local AI Environment..."

# Run DB Initialization (SQLCipher)
uv run python src/init_db.py

# Run LLM Bootstrapping (Ollama pull)
# Note: This runs in the background or sequentially. 
# For now, we run it sequentially to ensure the model is ready.
uv run python src/bootstrap.py

echo "[+] Initialization complete. Starting Assistant..."

# Execute the passed command or the main application if no arguments are provided
if [ $# -eq 0 ]; then
    exec uv run python src/main.py
else
    exec "$@"
fi
