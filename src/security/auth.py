import os
import sqlcipher3 as sqlite3
from passlib.hash import argon2
from loguru import logger
from dataclasses import dataclass
from src.security.audit import log_audit_event

@dataclass
class UserSession:
    username: str
    role: str
    user_id: int

class AuthenticationError(Exception):
    pass

def authenticate_user(username, password):
    db_path = os.getenv("DB_PATH", "/app/data/secure_vault.db")
    db_key = os.getenv("DB_ENCRYPTION_KEY")
    
    try:
        conn = sqlite3.connect(db_path)
        conn.execute(f"PRAGMA key = '{db_key}';")
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT u.id, u.password_hash, r.name 
            FROM users u
            JOIN roles r ON u.role_id = r.id
            WHERE u.username = ?
        """, (username,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            user_id, password_hash, role = result
            if argon2.verify(password, password_hash):
                logger.info(f"User {username} authenticated successfully.")
                session = UserSession(username=username, role=role, user_id=user_id)
                log_audit_event("USER_LOGIN", {"username": username}, user_id=user_id, status="SUCCESS")
                return session
        
        logger.warning(f"Failed login attempt for user: {username}")
        log_audit_event("USER_LOGIN_FAILED", {"attempted_username": username}, status="FAILURE")
        raise AuthenticationError("Invalid username or password.")
        
    except sqlite3.Error as e:
        logger.error(f"Database error during authentication: {e}")
        log_audit_event("AUTH_SYSTEM_ERROR", {"error": str(e)}, status="FAILURE")
        raise AuthenticationError("Authentication system unavailable.")
