import json
from pathlib import Path

from .analyzer import analyze_project
from .prompts import GROUNDED_SYSTEM_PROMPT_V04
from .test_cases import TEST_CASES


PROMPT_VERSION = "grounded-v0.4"
RESULTS_DIR = Path("results") / "smoke_v04"


def run_test_case(test_case: dict) -> dict:
    test_id = test_case["id"]

    print("=" * 60)
    print(
        f"Running {test_id} "
        f"({test_case['language']} / {test_case['difficulty']})"
    )
    print("=" * 60)

    try:
        result, metadata = analyze_project(
            test_case["input"],
            system_prompt=GROUNDED_SYSTEM_PROMPT_V04,
        )

        output = {
            "test_case": test_id,
            "language": test_case["language"],
            "difficulty": test_case["difficulty"],
            "prompt_version": PROMPT_VERSION,
            "status": "success",
            "metadata": metadata,
            "result": result.model_dump(),
        }

    except Exception as error:
        output = {
            "test_case": test_id,
            "language": test_case["language"],
            "difficulty": test_case["difficulty"],
            "prompt_version": PROMPT_VERSION,
            "status": "error",
            "error_type": type(error).__name__,
            "error_message": str(error),
        }

    return output


def save_result(output: dict) -> None:
    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    test_id = output["test_case"].lower().replace("-", "")

    output_path = RESULTS_DIR / f"{test_id}.json"

    output_path.write_text(
        json.dumps(
            output,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(
        json.dumps(
            output,
            indent=2,
            ensure_ascii=False,
        )
    )

    print(f"\nSaved result to: {output_path}\n")


def main() -> None:
    print("\nStarting Grounded Prompt v0.3 Smoke Test\n")

    all_results = []

    for test_case in TEST_CASES:
        output = run_test_case(test_case)

        save_result(output)
        all_results.append(output)

    successful_tests = sum(
        1
        for result in all_results
        if result["status"] == "success"
    )

    failed_tests = len(all_results) - successful_tests

    summary = {
        "prompt_version": PROMPT_VERSION,
        "total_tests": len(all_results),
        "successful_tests": successful_tests,
        "failed_tests": failed_tests,
        "tests": [
            {
                "test_case": result["test_case"],
                "status": result["status"],
                "metadata": result.get("metadata"),
            }
            for result in all_results
        ],
    }

    summary_path = RESULTS_DIR / "summary.json"

    summary_path.write_text(
        json.dumps(
            summary,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print("=" * 60)
    print("Smoke Test Complete")
    print("=" * 60)
    print(f"Total tests:      {len(all_results)}")
    print(f"Successful tests: {successful_tests}")
    print(f"Failed tests:     {failed_tests}")
    print(f"\nSummary saved to: {summary_path}")


if __name__ == "__main__":
    main()