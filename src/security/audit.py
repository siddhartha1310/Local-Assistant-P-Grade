import os
import sqlcipher3 as sqlite3
import json
from loguru import logger
from datetime import datetime

class AuditFailure(Exception):
    pass

def log_audit_event(action, details=None, user_id=None, status="SUCCESS"):
    db_path = os.getenv("DB_PATH", "data/secure_vault.db")
    db_key = os.getenv("DB_ENCRYPTION_KEY", "default-insecure-key")
    
    details_str = json.dumps(details) if details else None
    
    try:
        conn = sqlite3.connect(db_path)
        conn.execute(f"PRAGMA key = '{db_key}';")
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO audit_log (user_id, action, details, status, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, action, details_str, status, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
    except sqlite3.Error as e:
        logger.error(f"Failed to write to audit log at {db_path}: {e}")
        # In a high-security environment, we might want to halt the application
        # if auditing fails. For now, we raise a custom exception.
        raise AuditFailure(f"Security event logging failed: {e}")

def get_recent_audit_logs(limit=50):
    db_path = os.getenv("DB_PATH", "data/secure_vault.db")
    db_key = os.getenv("DB_ENCRYPTION_KEY", "default-insecure-key")
    
    try:
        conn = sqlite3.connect(db_path)
        conn.execute(f"PRAGMA key = '{db_key}';")
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT l.timestamp, u.username, l.action, l.status 
            FROM audit_log l
            LEFT JOIN users u ON l.user_id = u.id
            ORDER BY l.timestamp DESC
            LIMIT ?
        """, (limit,))
        
        logs = cursor.fetchall()
        conn.close()
        return logs
        
    except sqlite3.Error as e:
        logger.error(f"Error retrieving audit logs: {e}")
        return []
