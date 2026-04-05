# Fixtures for Slice 00 Environment
EXPECTED_DEPENDENCIES = [
    "httpx", "rich", "textual", "pydantic", "pypdf", "pandas", 
    "loguru", "sqlcipher3", "passlib", "presidio_analyzer", 
    "spacy", "watchdog", "yaml", "dotenv"
]

EXPECTED_MODELS = ["phi3:mini", "tinyllama"]
DB_ENCRYPTION_KEY_TEST = "test-key-123"
