import os
import sqlcipher3 as sqlite3
from loguru import logger
from dotenv import load_dotenv
from passlib.hash import argon2

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "/app/data/secure_vault.db")
DB_KEY = os.getenv("DB_ENCRYPTION_KEY", "default-insecure-key")
DEFAULT_ADMIN_USER = os.getenv("DEFAULT_ADMIN_USER", "admin")
DEFAULT_ADMIN_PASSWORD = os.getenv("DEFAULT_ADMIN_PASSWORD", "admin123")

def init_db():
    logger.info(f"Initializing encrypted database at {DB_PATH}...")
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    try:
        # Connect to the database using sqlcipher3
        conn = sqlite3.connect(DB_PATH)

        # Set the passphrase for encryption
        conn.execute(f"PRAGMA key = '{DB_KEY}';")

        # Performance/Compatibility settings
        conn.execute("PRAGMA cipher_compatibility = 4;")

        cursor = conn.cursor()

        # Verify connection/key
        cursor.execute("SELECT count(*) FROM sqlite_master;")

        
        # 1. Create RBAC Tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS roles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            );
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role_id INTEGER,
                FOREIGN KEY (role_id) REFERENCES roles (id)
            );
        """)
        
        # 2. Create Audit Log Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_id INTEGER,
                action TEXT NOT NULL,
                details TEXT,
                status TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            );
        """)
        
        # 3. Create Metrics Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                request_id TEXT,
                model TEXT,
                latency_ms REAL,
                tokens_per_sec REAL,
                prompt_tokens INTEGER,
                completion_tokens INTEGER,
                total_tokens INTEGER,
                validation_status TEXT,
                redacted_count INTEGER DEFAULT 0
            );
        """)

        # 4. Create Knowledge Base Table (Secure Knowledge Vault)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_base (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                file_name TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            );
        """)
        
        # Insert default roles
        cursor.execute("INSERT OR IGNORE INTO roles (name) VALUES ('admin'), ('user');")
        
        # Seed Admin User if not exists
        cursor.execute("SELECT id FROM roles WHERE name = 'admin'")
        admin_role_id = cursor.fetchone()[0]
        
        cursor.execute("SELECT id FROM users WHERE username = ?", (DEFAULT_ADMIN_USER,))
        if not cursor.fetchone():
            hashed_pwd = argon2.hash(DEFAULT_ADMIN_PASSWORD)
            cursor.execute("""
                INSERT INTO users (username, password_hash, role_id) 
                VALUES (?, ?, ?)
            """, (DEFAULT_ADMIN_USER, hashed_pwd, admin_role_id))
            logger.info(f"Seeded default admin user: {DEFAULT_ADMIN_USER}")
        
        conn.commit()
        conn.close()
        logger.success("Encrypted database initialized with RBAC and Audit schemas.")
        
    except Exception as e:
        logger.error(f"Error initializing encrypted database: {e}")
        raise

if __name__ == "__main__":
    init_db()
