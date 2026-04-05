# Feature: Pro-Grade Prompting (Live/Hot-Reload)
# Spec: docs/local-llm/spec/03-pro-grade-prompting.md
# Test Types Included: FUNCTION | INTEGRATION | E2E
# Last reviewed: 2026-04-04
# Status: stable

import os
import pytest
import importlib.util
import time
from loguru import logger
from src.prompts.loader import prompt_loader
from src.prompts.watcher import prompt_watcher

# Dynamically load fixtures
def load_fixtures():
    fixture_path = os.path.join(os.getcwd(), "docs/local-llm/evals/fixtures/03-prompts.fixture.py")
    spec = importlib.util.spec_from_file_location("prompts_03_fixture", fixture_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

fixtures = load_fixtures()

def test_ac1_prompt_loading():
    logger.info("Starting test for AC-1: Prompt templates are loaded from the prompts/ directory.")
    prompt_loader.load_all()
    available = prompt_loader.list_prompts()
    logger.info(f"Verification: Found {len(available)} prompts. List: {available}")
    assert len(available) > 0
    assert any(p['id'] == "default_chat" for p in available)
    logger.success("AC-1 PASSED")

def test_ac2_hot_reload():
    logger.info("Starting test for AC-2: Modifying a YAML file triggers automatic reload.")
    
    # 1. Start watcher
    prompt_watcher.start()
    time.sleep(1) # Allow thread to start
    
    test_file = os.path.join("prompts", "eval_temp.yaml")
    try:
        # 2. Create new prompt file
        logger.info(f"Step 1: Creating temporary prompt file {test_file}")
        with open(test_file, "w") as f:
            f.write(fixtures.TEST_PROMPT_YAML)
        
        # 3. Wait for watcher to detect
        logger.info("Step 2: Waiting for hot-reload...")
        time.sleep(2)
        
        # 4. Verify loader has it
        prompt = prompt_loader.get_prompt(fixtures.TEST_PROMPT_ID)
        logger.info(f"Verification: Found loaded prompt: {prompt}")
        assert prompt is not None
        assert prompt.version == fixtures.TEST_PROMPT_VERSION
        
        logger.success("AC-2 PASSED")
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)
        prompt_watcher.stop()

def test_ac4_prompt_rendering():
    logger.info("Starting test for AC-4: Selecting a prompt applies it (verified via rendering).")
    prompt_loader.load_all()
    
    # Use the default prompt
    prompt = prompt_loader.get_prompt("default_chat")
    logger.info(f"Input variables: query='Hello', content='Some context'")
    result = prompt.render(query="Hello", content="Some context")
    
    logger.info(f"Verification: Redacted context mentioned in output.")
    assert "redacted for PII" in result
    assert "Hello" in result
    assert "Some context" in result
    logger.success("AC-4 PASSED")

def test_ac6_malformed_yaml_resilience():
    logger.info("Starting test for AC-6: Malformed YAML files are ignored and do not crash.")
    malformed_file = os.path.join("prompts", "bad_format.yaml")
    
    with open(malformed_file, "w") as f:
        f.write("id: missing_quote\ntemplate: | \n  unclosed {{ variable")
        
    try:
        # Should not crash
        logger.info("Attempting to load malformed file...")
        prompt_loader.load_all()
        logger.info("Loader survived malformed file.")
        logger.success("AC-6 PASSED")
    finally:
        if os.path.exists(malformed_file):
            os.remove(malformed_file)

def test_ac8_non_existent_prompt():
    logger.info("Starting test for AC-8: System handles request for non-existent prompt ID.")
    # Requesting a random non-existent ID
    res = prompt_loader.get_prompt("does_not_exist_12345")
    logger.info(f"Verification: get_prompt returned {res}")
    # Requirement: return a default fallback OR None (which UI handles)
    # We'll assert it handles it gracefully (returns None)
    assert res is None
    logger.success("AC-8 PASSED")
