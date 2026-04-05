# Feature: Privacy Pipeline & File Ingestion
# Spec: docs/local-llm/spec/02-privacy-pipeline.md
# Test Types Included: FUNCTION | INTEGRATION | E2E
# Last reviewed: 2026-04-04
# Status: stable

import pytest
import os
import importlib.util
from loguru import logger
from src.privacy.masking import masking_service
from src.ingestion.extractor import extract_from_file

# Dynamically load fixtures from project source of truth
def load_fixtures():
    fixture_path = os.path.join(os.getcwd(), "docs/local-llm/evals/fixtures/02-privacy.fixture.py")
    spec = importlib.util.spec_from_file_location("privacy_02_fixture", fixture_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

fixtures = load_fixtures()

def test_ac1_pii_masking_email():
    logger.info("Starting test for AC-1: mask_text correctly replaces PII with placeholders.")
    logger.info(f"Input: '{fixtures.EMAIL_PII_TEXT}'")
    
    masked, count = masking_service.mask_text(fixtures.EMAIL_PII_TEXT)

    logger.info(f"Verification: '{fixtures.EMAIL_PLACEHOLDER}' in result")
    
    assert fixtures.EMAIL_PLACEHOLDER in masked
    logger.success("AC-1 PASSED (Email)")

def test_ac1_pii_masking_multiple():
    logger.info("Starting test for AC-1: mask_text handles multiple entity types.")
    logger.info(f"Input: '{fixtures.MULTIPLE_PII_TEXT}'")
    
    masked, count = masking_service.mask_text(fixtures.MULTIPLE_PII_TEXT)
    logger.info(f"Verification: Found '{fixtures.PHONE_PLACEHOLDER}' and '{fixtures.IP_PLACEHOLDER}'")
    
    assert fixtures.PHONE_PLACEHOLDER in masked
    assert fixtures.IP_PLACEHOLDER in masked
    logger.success("AC-1 PASSED (Multiple)")

def test_ac2_txt_extraction():
    logger.info("Starting test for AC-2: extract_from_file supports .txt.")
    test_file = "ac2_test.txt"
    with open(test_file, "w") as f:
        f.write(fixtures.TXT_CONTENT)
    
    extracted = extract_from_file(test_file)
    logger.info(f"Verification: Extracted length {len(extracted)} matches input")
    
    assert extracted == fixtures.TXT_CONTENT
    os.remove(test_file)
    logger.success("AC-2 PASSED (TXT)")

def test_ac3_csv_formatting():
    logger.info("Starting test for AC-3: CSV extraction converts rows into structured text.")
    test_file = "ac3_test.csv"
    with open(test_file, "w") as f:
        f.write(fixtures.CSV_CONTENT)
    
    extracted = extract_from_file(test_file)
    logger.info(f"Verification: 'John Doe' present in formatted string: '{extracted}'")
    
    assert "John Doe" in extracted
    os.remove(test_file)
    logger.success("AC-3 PASSED")

def test_ac4_ac5_ingestion_toggle():
    logger.info("Starting test for AC-4 & AC-5: Ingestion Manager supports Masking Toggle.")
    from src.ingestion.manager import IngestionManager
    
    # Create test file
    with open(fixtures.INTEGRATION_TEST_FILE, "w") as f:
        f.write(fixtures.INTEGRATION_CONTENT)
    
    # 1. Test with Masking ON (AC-5 logic)
    logger.info("Step 1: Processing with Masking ENABLED")
    mgr_on = IngestionManager(use_masking=True)
    result_on, count_on = mgr_on.process_file(fixtures.INTEGRATION_TEST_FILE)
    logger.info(f"Verification: result should be redacted. Result: '{result_on}'")
    assert fixtures.EMAIL_PLACEHOLDER in result_on
    assert "@" not in result_on
    
    # 2. Test with Masking OFF (AC-4 logic)
    logger.info("Step 2: Processing with Masking DISABLED")
    mgr_off = IngestionManager(use_masking=False)
    result_off, count_off = mgr_off.process_file(fixtures.INTEGRATION_TEST_FILE)
    logger.info(f"Verification: result should be raw. Result: '{result_off}'")
    assert "admin@company.com" in result_off
    
    os.remove(fixtures.INTEGRATION_TEST_FILE)
    logger.success("AC-4 & AC-5 PASSED")

def test_ac6_audit_ingestion():
    logger.info("Starting test for AC-6: File ingestion is logged in the audit trail.")
    from src.ingestion.manager import IngestionManager
    from src.security.audit import get_recent_audit_logs
    
    with open(fixtures.INTEGRATION_TEST_FILE, "w") as f:
        f.write(fixtures.INTEGRATION_CONTENT)
        
    mgr = IngestionManager(use_masking=True)
    mgr.process_file(fixtures.INTEGRATION_TEST_FILE, user_id=1) # Log as admin
    
    logs = get_recent_audit_logs(limit=5)
    actions = [log[2] for log in logs]
    logger.info(f"Verification: 'FILE_INGESTED' in recent actions: {actions}")
    
    assert "FILE_INGESTED" in actions
    os.remove(fixtures.INTEGRATION_TEST_FILE)
    logger.success("AC-6 PASSED")

def test_ac7_unsupported_file():
    logger.info("Starting test for AC-7: System rejects unsupported file types.")
    from src.ingestion.extractor import extract_from_file, FileNotSupportedError
    
    test_file = "bad_file.exe"
    with open(test_file, "w") as f:
        f.write("binary data")
        
    try:
        with pytest.raises(FileNotSupportedError):
            extract_from_file(test_file)
        logger.info("Verification: Correctly raised FileNotSupportedError")
        logger.success("AC-7 PASSED")
    finally:
        os.remove(test_file)

def test_ac8_corrupted_file():
    logger.info("Starting test for AC-8: System handles corrupted files.")
    from src.ingestion.extractor import extract_from_file, ExtractionError
    
    # Create a "PDF" that is actually just junk
    test_file = "corrupt.pdf"
    with open(test_file, "w") as f:
        f.write("This is not a real PDF content")
        
    try:
        with pytest.raises(ExtractionError):
            extract_from_file(test_file)
        logger.info("Verification: Correctly caught extraction error for corrupted PDF")
        logger.success("AC-8 PASSED")
    finally:
        os.remove(test_file)
