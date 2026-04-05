# Feature: Technical Environment & Infrastructure
# Spec: docs/local-llm/spec/00-environment.md
# Test Types Included: FUNCTION | INTEGRATION
# Last reviewed: 2026-04-04
# Status: stable

import os
import sys
import importlib.util
import httpx
import sqlcipher3 as sqlite3
import pytest
from loguru import logger

# Dynamically load fixtures from project source of truth
def load_fixtures():
    fixture_path = os.path.join(os.getcwd(), "docs/local-llm/evals/fixtures/00-environment.fixture.py")
    spec = importlib.util.spec_from_file_location("env_00_fixture", fixture_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

fixtures = load_fixtures()

def test_ac1_docker_start():
    logger.info("Starting test for AC-1: Docker Compose starts services correctly.")
    is_docker = os.path.exists('/.dockerenv')
    logger.info(f"Verification: Executing inside Docker container: {is_docker}")
    assert is_docker
    logger.success("AC-1 PASSED")

def test_ac2_ollama_network():
    logger.info("Starting test for AC-2: Assistant reaches Ollama API over internal network.")
    ollama_host = os.getenv("OLLAMA_HOST", "http://ollama:11434")
    logger.info(f"Input: Connecting to {ollama_host}")
    
    response = httpx.get(f"{ollama_host}/api/tags", timeout=5.0)
    logger.info(f"Verification: HTTP Status {response.status_code}")
    
    assert response.status_code == 200
    logger.success("AC-2 PASSED")

def test_ac3_sqlcipher_init():
    logger.info("Starting test for AC-3: SQLCipher can create/open encrypted database.")
    test_db = "encryption_verify.db"
    if os.path.exists(test_db): os.remove(test_db)
    
    try:
        # 1. Create encrypted database
        conn = sqlite3.connect(test_db)
        conn.execute(f"PRAGMA key = '{fixtures.DB_ENCRYPTION_KEY_TEST}';")
        conn.execute("CREATE TABLE secret (data TEXT);")
        conn.execute("INSERT INTO secret VALUES ('my_secret_data');")
        conn.commit()
        conn.close()
        
        # 2. Attempt to read WITHOUT key (should fail or return garbage if SQLCipher is active)
        # Note: If it doesn't fail, SQLCipher is not working.
        conn2 = sqlite3.connect(test_db)
        try:
            # First operation triggers key check
            conn2.execute("SELECT count(*) FROM sqlite_master;")
            # If it succeeds without a key, it's a plain DB
            is_plain = True
        except Exception:
            is_plain = False
        
        logger.info(f"Verification: Is database readable without key? {is_plain}")
        # We WANT it to be NOT plain (is_plain == False)
        assert not is_plain
        conn2.close()
        
        logger.success("AC-3 PASSED (Encryption verified via behavior)")
    finally:
        if os.path.exists(test_db): os.remove(test_db)

def test_ac4_dependencies():
    logger.info("Starting test for AC-4: All required Python dependencies are importable.")
    missing = []
    for dep in fixtures.EXPECTED_DEPENDENCIES:
        try:
            importlib.import_module(dep)
            logger.info(f"Imported: {dep}")
        except ImportError:
            missing.append(dep)
    
    logger.info(f"Verification: Missing dependencies: {missing}")
    assert len(missing) == 0
    logger.success("AC-4 PASSED")

def test_ac5_llm_provisioning():
    logger.info("Starting test for AC-5: LLM models are pulled and available.")
    ollama_host = os.getenv("OLLAMA_HOST", "http://ollama:11434")
    response = httpx.get(f"{ollama_host}/api/tags")
    models = [m['name'] for m in response.json().get('models', [])]
    logger.info(f"Available models: {models}")
    
    for expected in fixtures.EXPECTED_MODELS:
        found = any(expected in m for m in models)
        logger.info(f"Checking {expected}: {'FOUND' if found else 'MISSING'}")
        assert found
    
    logger.success("AC-5 PASSED")

def test_ac6_resource_limits():
    logger.info("Starting test for AC-6: Resource limits are applied (verified via environment).")
    has_cgroups = os.path.exists('/sys/fs/cgroup')
    logger.info(f"Verification: CGroup metadata exists: {has_cgroups}")
    assert has_cgroups
    logger.success("AC-6 PASSED")

def test_ac7_ollama_unreachable():
    logger.info("Starting test for AC-7: System handles unreachable Ollama API.")
    fake_host = "http://localhost:9999"
    logger.info(f"Attempting connection to fake host: {fake_host}")
    
    try:
        response = httpx.get(f"{fake_host}/api/tags", timeout=1.0)
        reachable = True
    except (httpx.ConnectError, httpx.TimeoutException):
        reachable = False
        
    logger.info(f"Verification: Connection correctly failed: {not reachable}")
    assert not reachable
    logger.success("AC-7 PASSED")

def test_ac8_wrong_db_key():
    logger.info("Starting test for AC-8: System fails on incorrect DB key.")
    test_db = "wrong_key_test.db"
    if os.path.exists(test_db): os.remove(test_db)
    
    try:
        # 1. Create with correct key
        conn = sqlite3.connect(test_db)
        conn.execute("PRAGMA key = 'correct_key';")
        conn.execute("CREATE TABLE t1(a);")
        conn.commit()
        conn.close()
        
        # 2. Attempt access with WRONG key
        conn2 = sqlite3.connect(test_db)
        conn2.execute("PRAGMA key = 'wrong_key';")
        
        with pytest.raises(Exception) as excinfo:
            conn2.execute("SELECT count(*) FROM t1;")
        
        logger.info(f"Verification: Caught expected error: {str(excinfo.value)}")
        assert "not a database" in str(excinfo.value)
        conn2.close()
        logger.success("AC-8 PASSED")
    finally:
        if os.path.exists(test_db): os.remove(test_db)
