from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from src.orchestration.generator import GenerationResult

@dataclass
class ValidationReport:
    is_safe: bool
    violations: List[str]
    confidence_score: float
    reason: Optional[str] = None

@dataclass
class ABConfig:
    model_a: str
    prompt_a: str
    model_b: str
    prompt_b: str
    use_vault: bool = False
    user_id: Optional[int] = None

@dataclass
class ABResult:
    test_id: str
    result_a: GenerationResult
    result_b: GenerationResult
    preference: Optional[int] = None  # 0 for A, 1 for B
    validation_a: Optional[ValidationReport] = None
    validation_b: Optional[ValidationReport] = None
