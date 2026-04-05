import httpx
import os
import asyncio
from loguru import logger
from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class GenerationResult:
    response: str
    latency_ms: float
    tokens_per_sec: float
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    model: str
    success: bool = True
    error: Optional[str] = None

class AsyncGenerator:
    def __init__(self, host: Optional[str] = None):
        self.host = host or os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
        self.timeout = httpx.Timeout(60.0, connect=10.0)

    async def generate(self, model: str, prompt: str) -> GenerationResult:
        """Calls Ollama API asynchronously and returns result with metrics."""
        url = f"{self.host}/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }

        try:
            # We use a custom transport to ensure no DNS resolution is attempted for 127.0.0.1
            async with httpx.AsyncClient(timeout=self.timeout, trust_env=False) as client:
                logger.info(f"Triggering generation for model: {model}")
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()

                # Extract metrics from Ollama (values are in nanoseconds)
                total_duration_ns = data.get("total_duration", 0)
                eval_count = data.get("eval_count", 0)
                eval_duration_ns = data.get("eval_duration", 1) # avoid div by zero
                prompt_eval_count = data.get("prompt_eval_count", 0)

                latency_ms = total_duration_ns / 1e6
                tokens_per_sec = eval_count / (eval_duration_ns / 1e9) if eval_duration_ns > 0 else 0

                return GenerationResult(
                    response=data.get("response", ""),
                    latency_ms=round(latency_ms, 2),
                    tokens_per_sec=round(tokens_per_sec, 2),
                    prompt_tokens=prompt_eval_count,
                    completion_tokens=eval_count,
                    total_tokens=prompt_eval_count + eval_count,
                    model=model
                )

        except Exception as e:
            logger.error(f"Generation failed for model {model}: {e}")
            return GenerationResult(
                response="",
                latency_ms=0,
                tokens_per_sec=0,
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                model=model,
                success=False,
                error=str(e)
            )

# Global generator instance
generator = AsyncGenerator()
