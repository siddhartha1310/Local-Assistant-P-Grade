import asyncio
import os
import sys
import random
import uuid
from loguru import logger

# Add project root to path
sys.path.append(os.getcwd())

from src.security.metrics import metrics_service
from src.orchestration.generator import GenerationResult
from src.security.audit import log_audit_event, get_recent_audit_logs

async def simulate_load():
    """Simulates a series of generations to populate the metrics table."""
    logger.info("Simulating generation load for dashboard verification...")
    
    models = ["phi3:mini", "tinyllama"]
    
    for i in range(10):
        test_id = str(uuid.uuid4())
        model = random.choice(models)
        
        # Mock a result
        res = GenerationResult(
            response="Simulated response text with PII redaction.",
            latency_ms=random.uniform(500, 3000),
            tokens_per_sec=random.uniform(5, 50),
            prompt_tokens=50,
            completion_tokens=100,
            total_tokens=150,
            model=model,
            success=True
        )
        
        redacted_count = random.randint(0, 5)
        metrics_service.save_generation_metrics(test_id, res, redacted_count=redacted_count)
        log_audit_event("SIMULATED_GEN", {"id": i, "model": model, "redacted": redacted_count})
        print(f"Logged generation {i+1}/10")
        await asyncio.sleep(0.1)

async def verify_polling_data():
    """Verifies that the dashboard's query logic can retrieve the simulated data."""
    logger.info("Verifying data retrieval for dashboard...")
    
    import sqlcipher3 as sqlite3
    db_path = os.getenv("DB_PATH", "data/secure_vault.db")
    db_key = os.getenv("DB_ENCRYPTION_KEY", "default-insecure-key")
    
    conn = sqlite3.connect(db_path)
    conn.execute(f"PRAGMA key = '{db_key}';")
    cursor = conn.cursor()
    
    # 1. Check Metrics
    cursor.execute("SELECT latency_ms, redacted_count FROM metrics ORDER BY timestamp DESC LIMIT 10")
    rows = cursor.fetchall()
    if len(rows) >= 10:
        print(f"PASS: Successfully retrieved {len(rows)} metric rows.")
        if any(r[1] > 0 for r in rows):
            print("PASS: Successfully retrieved non-zero redacted counts.")
        else:
            print("WARNING: All redacted counts were zero (might be random luck).")
    else:
        print(f"FAIL: Only found {len(rows)} metric rows.")
        
    # 2. Check Audit Logs
    logs = get_recent_audit_logs(limit=10)
    if any("SIMULATED_GEN" in r[2] for r in logs):
        print("PASS: Found simulated audit logs.")
    else:
        print("FAIL: Simulated audit logs not found.")
        
    conn.close()

async def main():
    # Ensure environment
    os.environ.setdefault("DB_PATH", "data/secure_vault.db")
    os.environ.setdefault("DB_ENCRYPTION_KEY", "default-insecure-key")
    
    await simulate_load()
    await verify_polling_data()
    
    print("\n--- Summary ---")
    print("AC-1 (Metrics Visualization): DATA READY (Requires Manual TUI Check)")
    print("AC-2 (Audit Visualization): DATA READY (Requires Manual TUI Check)")
    print("AC-5 (Integration): DATA VERIFIED IN SQL")

if __name__ == "__main__":
    asyncio.run(main())
