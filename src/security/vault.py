import sqlite3
import os
from loguru import logger
from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime

# We use the same DB settings as init_db
DB_PATH = os.getenv("DB_PATH", "data/secure_vault.db")
DB_KEY = os.getenv("DB_ENCRYPTION_KEY", "default-insecure-key")

# Limits from Spec 05
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10MB
MAX_VAULT_TOTAL_BYTES = 50 * 1024 * 1024  # 50MB
JUDGE_CONTEXT_LIMIT_CHARS = 8000  # ~2000 tokens

class VaultQuotaExceededError(Exception):
    pass

@dataclass
class VaultEntry:
    id: int
    file_name: str
    content: str
    timestamp: str

from src.security.audit import log_audit_event

class VaultService:
    def __init__(self, db_path: str = DB_PATH, db_key: str = DB_KEY):
        self.db_path = db_path
        self.db_key = db_key
        # Ensure path exists for local dev if not in docker
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def _get_conn(self):
        import sqlcipher3 as sqlite3
        conn = sqlite3.connect(self.db_path)
        conn.execute(f"PRAGMA key = '{self.db_key}';")
        conn.execute("PRAGMA cipher_compatibility = 4;")
        return conn

    def save_to_vault(self, user_id: int, file_name: str, content: str):
        """Persists masked text into the encrypted database with quota enforcement."""
        content_size = len(content.encode('utf-8'))
        
        if content_size > MAX_FILE_SIZE_BYTES:
            raise ValueError(f"File content exceeds single-file limit of {MAX_FILE_SIZE_BYTES} bytes")

        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            
            # 1. Check total quota for user
            cursor.execute("SELECT SUM(LENGTH(content)) FROM knowledge_base WHERE user_id = ?", (user_id,))
            current_total = cursor.fetchone()[0] or 0
            
            if current_total + content_size > MAX_VAULT_TOTAL_BYTES:
                logger.warning(f"Vault quota exceeded for user {user_id}. Current: {current_total}, New: {content_size}")
                log_audit_event("VAULT_QUOTA_EXCEEDED", {"user_id": user_id, "attempted_size": content_size}, user_id=user_id, status="FAILURE")
                raise VaultQuotaExceededError(f"Vault quota exceeded. Max: {MAX_VAULT_TOTAL_BYTES} bytes")

            # 2. Insert content
            cursor.execute(
                "INSERT INTO knowledge_base (user_id, file_name, content) VALUES (?, ?, ?)",
                (user_id, file_name, content)
            )
            conn.commit()
            logger.info(f"Saved '{file_name}' to vault for user {user_id} ({content_size} bytes)")
            log_audit_event("FILE_VAULTED", {"file_name": file_name, "size": content_size}, user_id=user_id)
            
        finally:
            conn.close()

    def get_vault_context(self, user_id: int) -> str:
        """Retrieves all vaulted text for the user, joined and capped by context limits."""
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            # Get most recent entries first
            cursor.execute(
                "SELECT content FROM knowledge_base WHERE user_id = ? ORDER BY timestamp DESC",
                (user_id,)
            )
            rows = cursor.fetchall()
            
            all_content = []
            current_len = 0
            
            for (content,) in rows:
                if current_len + len(content) > JUDGE_CONTEXT_LIMIT_CHARS:
                    # Add partial if space remains
                    remaining = JUDGE_CONTEXT_LIMIT_CHARS - current_len
                    if remaining > 100: # Only bother with substantial chunks
                        all_content.append(content[:remaining])
                    break
                all_content.append(content)
                current_len += len(content)
                
            return "\n---\n".join(all_content)
            
        finally:
            conn.close()

    def list_vault_files(self, user_id: int) -> List[dict]:
        """Returns metadata for all files in the vault."""
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, file_name, LENGTH(content), timestamp FROM knowledge_base WHERE user_id = ?",
                (user_id,)
            )
            return [
                {"id": r[0], "file_name": r[1], "size_bytes": r[2], "timestamp": r[3]}
                for r in cursor.fetchall()
            ]
        finally:
            conn.close()

    def clear_vault(self, user_id: int):
        """Removes all vaulted content for a user."""
        conn = self._get_conn()
        try:
            conn.execute("DELETE FROM knowledge_base WHERE user_id = ?", (user_id,))
            conn.commit()
            logger.info(f"Cleared vault for user {user_id}")
            log_audit_event("VAULT_CLEARED", {"user_id": user_id}, user_id=user_id)
        finally:
            conn.close()

# Global service instance
vault_service = VaultService()
