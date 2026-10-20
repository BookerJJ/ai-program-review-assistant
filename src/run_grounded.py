import json
from pathlib import Path

from .analyzer import analyze_project
from .prompts import GROUNDED_SYSTEM_PROMPT_V02


TC_001 = """
During today's integration test, the authentication service returned 401 errors for all test accounts.

QA could not complete the planned test cycle.

Backend Engineering is investigating the authentication configuration and will provide an update by Wednesday.

No change to the release date has been discussed.
""".strip()


def main() -> None:
    print("Running TC-001 with Grounded Prompt v0.2...\n")

    result, metadata = analyze_project(
        TC_001,
        system_prompt=GROUNDED_SYSTEM_PROMPT_V02,
    )

    output = {
        "test_case": "TC-001",
        "prompt_version": "grounded-v0.2",
        "metadata": metadata,
        "result": result.model_dump(),
    }

    print(
        json.dumps(
            output,
            indent=2,
            ensure_ascii=False,
        )
    )

    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)

    output_path = results_dir / "grounded_tc001.json"

    output_path.write_text(
        json.dumps(
            output,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(f"\nSaved result to: {output_path}")


if __name__ == "__main__":
    main()