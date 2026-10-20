import time
from typing import TypeVar

from google import genai
from pydantic import BaseModel


T = TypeVar("T", bound=BaseModel)


class GeminiClient:
    """
    Thin Gemini API adapter for this project.

    The client intentionally contains no TPM-specific logic.
    It only handles:
    - Gemini API calls
    - structured output
    - Pydantic validation
    - latency/token metadata
    """

    def __init__(
        self,
        model: str = "gemini-3.8-flash",
        thinking_level: str = "low",
        temperature: float = 0.0,
    ):
        self.model = model
        self.thinking_level = thinking_level
        self.temperature = temperature

        # Automatically reads GEMINI_API_KEY
        self.client = genai.Client()

    def generate_structured(
        self,
        *,
        input_text: str,
        system_prompt: str,
        response_model: type[T],
    ) -> tuple[T, dict]:

        start_time = time.perf_counter()

        interaction = self.client.interactions.create(
            model=self.model,

            # No server-side conversation state needed
            store=False,

            system_instruction=system_prompt,

            input=input_text,

            generation_config={
                "temperature": self.temperature,
                "thinking_level": self.thinking_level,
            },

            response_format={
                "type": "text",
                "mime_type": "application/json",
                "schema": response_model.model_json_schema(),
            },
        )

        latency_seconds = (
            time.perf_counter()
            - start_time
        )

        # Validate Gemini JSON using Pydantic.
        result = response_model.model_validate_json(
            interaction.output_text
        )

        usage = getattr(
            interaction,
            "usage",
            None,
        )

        metadata = {
            "provider": "google",
            "model": self.model,
            "thinking_level": self.thinking_level,
            "temperature": self.temperature,
            "latency_seconds": round(
                latency_seconds,
                3,
            ),
            "input_tokens": (
                getattr(
                    usage,
                    "total_input_tokens",
                    None,
                )
                if usage
                else None
            ),
            "output_tokens": (
                getattr(
                    usage,
                    "total_output_tokens",
                    None,
                )
                if usage
                else None
            ),
            "thinking_tokens": (
                getattr(
                    usage,
                    "total_thought_tokens",
                    None,
                )
                if usage
                else None
            ),
            "total_tokens": (
                getattr(
                    usage,
                    "total_tokens",
                    None,
                )
                if usage
                else None
            ),
        }

        return result, metadata