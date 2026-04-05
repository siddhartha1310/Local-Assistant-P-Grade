import re
from dataclasses import dataclass
from typing import List, Optional
from loguru import logger
from src.orchestration.generator import generator, GenerationResult
from src.prompts.loader import prompt_loader
from src.orchestration.models import ValidationReport

class GuardrailService:
    def __init__(self, judge_model: str = "llama3.2:1b"):
        self.judge_model = judge_model
        # Static rules (e.g., block clear AI identification if requested, or specific PII patterns)
        self.blocked_patterns = [
            r"as an AI language model",
            r"I am a large language model",
            r"my knowledge cutoff",
            r"<PASSWORD>",
            r"<SECRET_KEY>"
        ]

    async def validate_output(self, query: str, response: str, context: Optional[str] = None) -> ValidationReport:
        """Runs the model response through a multi-pass validation pipeline."""
        violations = []
        
        # Pass 1: Static Rule-Based Filter
        for pattern in self.blocked_patterns:
            if re.search(pattern, response, re.IGNORECASE):
                violations.append(f"Static Pattern Match: {pattern}")

        # Pass 2: Semantic Hallucination Pass (LLM-as-a-judge)
        if context and response:
            hallucination_report = await self.check_hallucination(context, response)
            if not hallucination_report.is_safe:
                violations.append("Hallucination Detected")
                return ValidationReport(
                    is_safe=False,
                    violations=violations,
                    confidence_score=hallucination_report.confidence_score,
                    reason=hallucination_report.reason
                )

        is_safe = len(violations) == 0
        return ValidationReport(
            is_safe=is_safe,
            violations=violations,
            confidence_score=1.0 if is_safe else 0.0
        )

    async def check_hallucination(self, context: str, claim: str) -> ValidationReport:
        """Compares the model's claim against the provided context using an LLM-as-a-judge pattern."""
        judge_prompt_tpl = prompt_loader.get_prompt("hallucination_judge")
        if not judge_prompt_tpl:
            logger.error("Hallucination judge prompt template not found!")
            return ValidationReport(is_safe=True, violations=[], confidence_score=1.0)

        # Build prompt
        full_prompt = judge_prompt_tpl.template.replace("{{ context }}", context).replace("{{ claim }}", claim)
        
        logger.info(f"Triggering LLM-as-a-judge for hallucination check using model: {self.judge_model}")
        result: GenerationResult = await generator.generate(self.judge_model, full_prompt)
        
        if not result.success:
            logger.error(f"Hallucination judge failed: {result.error}")
            return ValidationReport(is_safe=True, violations=[], confidence_score=1.0)

        # Parse output
        # Format: VERDICT: [YES/NO] \n REASON: [1-sentence explanation]
        response_text = result.response.strip()
        verdict_match = re.search(r"VERDICT:\s*(YES|NO)", response_text, re.IGNORECASE)
        reason_match = re.search(r"REASON:\s*(.*)", response_text, re.IGNORECASE)

        is_safe = True
        reason = reason_match.group(1) if reason_match else "No reason provided"
        
        if verdict_match and verdict_match.group(1).upper() == "NO":
            is_safe = False
            logger.warning(f"Hallucination detected by judge: {reason}")

        return ValidationReport(
            is_safe=is_safe,
            violations=[] if is_safe else ["Hallucination"],
            confidence_score=0.9,
            reason=reason
        )

# Global service instance
guardrail_service = GuardrailService()
