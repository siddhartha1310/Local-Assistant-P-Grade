import os
import sqlcipher3 as sqlite3
from loguru import logger
from datetime import datetime
from src.orchestration.generator import GenerationResult

class MetricsService:
    def __init__(self, db_path: str = None, db_key: str = None):
        self.db_path = db_path or os.getenv("DB_PATH", "/app/data/secure_vault.db")
        self.db_key = db_key or os.getenv("DB_ENCRYPTION_KEY")

    def save_generation_metrics(self, request_id: str, result: GenerationResult, redacted_count: int = 0):
        """Saves metrics for a single generation run."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute(f"PRAGMA key = '{self.db_key}';")
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO metrics (
                    timestamp, request_id, model, latency_ms, 
                    tokens_per_sec, prompt_tokens, completion_tokens, 
                    total_tokens, validation_status, redacted_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                request_id,
                result.model,
                result.latency_ms,
                result.tokens_per_sec,
                result.prompt_tokens,
                result.completion_tokens,
                result.total_tokens,
                "SUCCESS" if result.success else "FAILURE",
                redacted_count
            ))

            conn.commit()
            conn.close()
            logger.info(f"Saved metrics for request {request_id} (Model: {result.model})")

        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")

# Global metrics service
metrics_service = MetricsService()
