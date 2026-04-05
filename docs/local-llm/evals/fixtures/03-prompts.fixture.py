# Fixtures for Slice 03 Pro-Grade Prompting
TEST_PROMPT_ID = "eval_test_prompt"
TEST_PROMPT_VERSION = "2.0.0"
TEST_PROMPT_YAML = """
id: "eval_test_prompt"
version: "2.0.0"
description: "Used for eval verification"
template: "Hello {{name}}, welcome to {{system}}."
"""

# Render Data
RENDER_VARS = {"name": "Admin", "system": "SecureLocalAI"}
EXPECTED_RENDER = "Hello Admin, welcome to SecureLocalAI."
