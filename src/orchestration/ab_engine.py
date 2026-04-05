import asyncio
import uuid
from loguru import logger
from src.orchestration.generator import generator
from src.orchestration.models import ABConfig, ABResult, ValidationReport
from src.security.metrics import metrics_service
from src.security.audit import log_audit_event
from src.security.vault import vault_service
from src.security.guardrails import guardrail_service

class ABEngine:
    async def run_test(self, query: str, config: ABConfig) -> ABResult:
        """Triggers generation from two configurations in parallel and validates output."""
        test_id = str(uuid.uuid4())
        logger.info(f"Starting A/B test with guardrails: {test_id}")
        log_audit_event("AB_TEST_TRIGGERED", {"test_id": test_id, "query": query, "use_vault": config.use_vault})

        # 1. Retrieve Vaulted Context if enabled
        context = None
        if config.use_vault and config.user_id:
            context = vault_service.get_vault_context(config.user_id)
            logger.info(f"Retrieved {len(context) if context else 0} chars of vaulted context for validation.")

        # 2. Run parallel generations
        # Inject context into prompts if vault is enabled
        prompt_a = f"CONTEXT:\n{context}\n\nUSER QUERY:\n{config.prompt_a}\n{query}" if context else f"{config.prompt_a}\n\n{query}"
        prompt_b = f"CONTEXT:\n{context}\n\nUSER QUERY:\n{config.prompt_b}\n{query}" if context else f"{config.prompt_b}\n\n{query}"

        task_a = generator.generate(config.model_a, prompt_a)
        task_b = generator.generate(config.model_b, prompt_b)

        result_a, result_b = await asyncio.gather(task_a, task_b)

        # 3. Parallel Validation Pass
        val_task_a = guardrail_service.validate_output(query, result_a.response, context)
        val_task_b = guardrail_service.validate_output(query, result_b.response, context)
        
        report_a, report_b = await asyncio.gather(val_task_a, val_task_b)

        # Save metrics for both, including validation status
        metrics_service.save_generation_metrics(test_id, result_a) # existing metrics might need update for val_status
        metrics_service.save_generation_metrics(test_id, result_b)

        return ABResult(
            test_id=test_id,
            result_a=result_a,
            result_b=result_b,
            validation_a=report_a,
            validation_b=report_b
        )

    def record_preference(self, test_id: str, preferred_index: int, user_id: int = None):
        """Records user preference for a test run."""
        # For now, we log it to audit. We could also add a dedicated column to metrics.
        logger.info(f"Recording preference for test {test_id}: Winner={preferred_index}")
        log_audit_event(
            "AB_PREFERENCE_RECORDED", 
            {"test_id": test_id, "winner": "A" if preferred_index == 0 else "B"},
            user_id=user_id
        )

# Global engine instance
ab_engine = ABEngine()
