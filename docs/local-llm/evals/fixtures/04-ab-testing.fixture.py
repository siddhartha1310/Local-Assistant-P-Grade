from src.orchestration.models import ABConfig

# Fixture: Standard A/B Test Config
ab_test_config = ABConfig(
    model_a="phi3",
    prompt_a="You are a helpful assistant.",
    model_b="tinyllama",
    prompt_b="You are a concise assistant.",
    use_vault=False
)

# Fixture: Vault-enabled A/B Test Config
ab_vault_config = ABConfig(
    model_a="phi3",
    prompt_a="Analyze this document carefully.",
    model_b="phi3",
    prompt_b="Summarize this document briefly.",
    use_vault=True,
    user_id=1
)
