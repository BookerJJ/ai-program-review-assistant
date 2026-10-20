import os
import time

from ollama import chat

from .prompts import BASELINE_SYSTEM_PROMPT
from .schemas import ProgramReview


DEFAULT_MODEL = "qwen3:8b"


def analyze_project(
    project_text: str,
    model: str | None = None,
    system_prompt: str = BASELINE_SYSTEM_PROMPT,
) -> tuple[ProgramReview, dict]:
    """
    Analyze project text using a local Ollama model.

    Returns:
        1. Parsed ProgramReview object
        2. Metadata including model, latency, and token counts
    """

    model_name = model or os.getenv(
        "OLLAMA_MODEL",
        DEFAULT_MODEL,
    )

    start_time = time.perf_counter()

    response = chat(
        model=model_name,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": project_text,
            },
        ],
        format=ProgramReview.model_json_schema(),
        think=False,
        options={
            "temperature": 0,
        },
    )

    latency_seconds = time.perf_counter() - start_time

    result = ProgramReview.model_validate_json(
        response.message.content
    )

    metadata = {
        "model": model_name,
        "latency_seconds": round(latency_seconds, 3),
        "temperature": 0,
        "thinking": False,
    }

    if response.prompt_eval_count is not None:
        metadata["input_tokens"] = response.prompt_eval_count

    if response.eval_count is not None:
        metadata["output_tokens"] = response.eval_count

    if (
        response.prompt_eval_count is not None
        and response.eval_count is not None
    ):
        metadata["total_tokens"] = (
            response.prompt_eval_count
            + response.eval_count
        )

    return result, metadata