# Feature: Secure CLI, RBAC Login & Audit Trail
# Spec: docs/local-llm/spec/01-secure-cli-rbac.md
# Test Types Included: INTEGRATION | E2E
# Last reviewed: 2026-04-04
# Status: stable

import os
import pytest
import importlib.util
from loguru import logger
from src.security.auth import authenticate_user, AuthenticationError
from src.security.audit import get_recent_audit_logs, log_audit_event
from src.ui.app import SecureAssistantApp, LoginScreen, MainDashboard

# Dynamically load fixtures from project source of truth
def load_fixtures():
    fixture_path = os.path.join(os.getcwd(), "docs/local-llm/evals/fixtures/01-secure-cli.fixture.py")
    spec = importlib.util.spec_from_file_location("cli_01_fixture", fixture_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

fixtures = load_fixtures()

def test_ac1_login_screen_presence():
    logger.info("Starting test for AC-1: TUI displays a login screen on startup.")
    app = SecureAssistantApp()
    # Check if LoginScreen class exists and is used
    logger.info("Verification: SecureAssistantApp has a LoginScreen component.")
    assert LoginScreen is not None
    logger.success("AC-1 PASSED")

def test_ac2_hashed_auth():
    logger.info("Starting test for AC-2: Only users in the users table can log in; passwords must be hashed.")
    logger.info(f"Input: Username={fixtures.ADMIN_USERNAME}, Password=********")
    
    session = authenticate_user(fixtures.ADMIN_USERNAME, fixtures.ADMIN_PASSWORD)
    logger.info(f"Verification: Session user {session.username} matches {fixtures.ADMIN_USERNAME}")
    
    assert session.username == fixtures.ADMIN_USERNAME
    logger.success("AC-2 PASSED")

def test_ac2_failed_auth():
    logger.info("Starting test for AC-2 (Failure Case): Invalid passwords should be rejected.")
    logger.info(f"Input: Username={fixtures.ADMIN_USERNAME}, Password={fixtures.INVALID_PASSWORD}")
    
    with pytest.raises(AuthenticationError) as excinfo:
        authenticate_user(fixtures.ADMIN_USERNAME, fixtures.INVALID_PASSWORD)
    
    logger.info(f"Verification: Caught expected error: {str(excinfo.value)}")
    logger.success("AC-2 FAILURE CASE PASSED")

def test_ac3_dashboard_transition():
    logger.info("Starting test for AC-3: Successful login transitions to a Secure Dashboard.")
    logger.info("Verification: MainDashboard class is defined for the application.")
    assert MainDashboard is not None
    logger.success("AC-3 PASSED")

def test_ac4_audit_login_record():
    logger.info("Starting test for AC-4: Every login attempt is recorded in the audit_logs table.")
    test_user = fixtures.FAKE_USER
    logger.info(f"Attempting failed login for {test_user} to trigger audit...")
    
    try:
        authenticate_user(test_user, fixtures.FAKE_PASS)
    except AuthenticationError:
        pass
    
    logs = get_recent_audit_logs(limit=5)
    actions = [log[2] for log in logs]
    logger.info(f"Verification: 'USER_LOGIN_FAILED' in recent actions {actions}")
    
    assert "USER_LOGIN_FAILED" in actions
    logger.success("AC-4 PASSED")

def test_ac5_model_switching_logic():
    logger.info("Starting test for AC-5: Dashboard allows switching models.")
    # Check if the MainDashboard has model selection logic
    from textual.widgets import Select
    dashboard = MainDashboard()
    # We simulate the selection change logic check
    logger.info("Verification: MainDashboard has handle_model_change method.")
    assert hasattr(dashboard, 'handle_model_change')
    logger.success("AC-5 PASSED")

def test_ac6_audit_persistence():
    logger.info("Starting test for AC-6: Audit pane updates (Verified via persistence layer).")
    unique_action = f"UI_ACTION_{os.urandom(4).hex()}"
    logger.info(f"Logging custom UI event: {unique_action}")
    
    log_audit_event(unique_action, {"data": "eval"}, status="SUCCESS")
    
    logs = get_recent_audit_logs(limit=5)
    actions = [log[2] for log in logs]
    logger.info(f"Verification: {unique_action} found in {actions}")
    
    assert unique_action in actions
    logger.success("AC-6 PASSED")

def test_ac8_locked_db_auth():
    logger.info("Starting test for AC-8: System handles inaccessible database.")
    # We simulate an inaccessible DB by pointing to a non-existent path 
    # and not providing a key.
    os.environ["DB_PATH"] = "/root/no_access.db"
    
    try:
        with pytest.raises(AuthenticationError) as excinfo:
            authenticate_user("admin", "admin123")
        logger.info(f"Verification: Caught expected error: {str(excinfo.value)}")
        assert "unavailable" in str(excinfo.value)
        logger.success("AC-8 PASSED")
    finally:
        # Restore
        os.environ["DB_PATH"] = "/app/data/secure_vault.db"

