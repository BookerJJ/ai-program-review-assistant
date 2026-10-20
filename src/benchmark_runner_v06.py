import json
from datetime import datetime
from pathlib import Path

from .analyzer import analyze_project
from .benchmark_cases_v1 import (
    BENCHMARK_CASES,
    validate_benchmark_distribution,
)
from .prompts import FEWSHOT_SYSTEM_PROMPT_V06


BENCHMARK_VERSION = "benchmark-v1"
PROMPT_VERSION = "fewshot-boundary-v0.6"

RESULTS_DIR = (
    Path("results")
    / "benchmark_v1"
    / "fewshot_v06"
)

# True:
# 이미 결과 파일이 있으면 건너뜁니다.
# 중간에 실행이 끊겼을 때 이어서 실행하기 좋습니다.
SKIP_EXISTING = True


def timestamp() -> str:
    return datetime.now().astimezone().isoformat(
        timespec="seconds"
    )


def result_path_for(test_id: str) -> Path:
    filename = (
        test_id
        .lower()
        .replace("-", "")
        + ".json"
    )

    return RESULTS_DIR / filename


def run_case(
    test_case: dict,
    case_number: int,
    total_cases: int,
) -> dict:
    test_id = test_case["id"]

    print("\n" + "=" * 70)
    print(
        f"[{case_number}/{total_cases}] "
        f"{test_id} | "
        f"{test_case['language']} | "
        f"{test_case['difficulty']}"
    )
    print(
        f"Target: "
        f"{test_case['primary_target']}"
    )
    print("=" * 70)

    started_at = timestamp()

    try:
        result, metadata = analyze_project(
            test_case["input"],
            system_prompt=FEWSHOT_SYSTEM_PROMPT_V06,
        )

        output = {
            "benchmark_version":
                BENCHMARK_VERSION,
            "prompt_version":
                PROMPT_VERSION,
            "test_case":
                test_id,
            "language":
                test_case["language"],
            "difficulty":
                test_case["difficulty"],
            "primary_target":
                test_case["primary_target"],
            "status":
                "success",
            "started_at":
                started_at,
            "completed_at":
                timestamp(),
            "metadata":
                metadata,
            "result":
                result.model_dump(),
        }

    except Exception as error:
        output = {
            "benchmark_version":
                BENCHMARK_VERSION,
            "prompt_version":
                PROMPT_VERSION,
            "test_case":
                test_id,
            "language":
                test_case["language"],
            "difficulty":
                test_case["difficulty"],
            "primary_target":
                test_case["primary_target"],
            "status":
                "error",
            "started_at":
                started_at,
            "completed_at":
                timestamp(),
            "error_type":
                type(error).__name__,
            "error_message":
                str(error),
        }

    return output


def save_result(
    output: dict,
) -> Path:
    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = result_path_for(
        output["test_case"]
    )

    output_path.write_text(
        json.dumps(
            output,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    return output_path


def load_existing_result(
    path: Path,
) -> dict:
    return json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )


def build_summary(
    all_results: list[dict],
    benchmark_started_at: str,
) -> dict:
    successful = [
        result
        for result in all_results
        if result["status"] == "success"
    ]

    failed = [
        result
        for result in all_results
        if result["status"] != "success"
    ]

    latencies = [
        result["metadata"]["latency_seconds"]
        for result in successful
        if result.get("metadata")
        and result["metadata"].get(
            "latency_seconds"
        ) is not None
    ]

    total_input_tokens = sum(
        result["metadata"].get(
            "input_tokens",
            0,
        )
        for result in successful
    )

    total_output_tokens = sum(
        result["metadata"].get(
            "output_tokens",
            0,
        )
        for result in successful
    )

    total_tokens = sum(
        result["metadata"].get(
            "total_tokens",
            0,
        )
        for result in successful
    )

    average_latency = (
        sum(latencies) / len(latencies)
        if latencies
        else None
    )

    by_language = {}

    for language in ("English", "Korean"):
        language_results = [
            result
            for result in all_results
            if result["language"] == language
        ]

        by_language[language] = {
            "total": len(
                language_results
            ),
            "success": sum(
                result["status"]
                == "success"
                for result
                in language_results
            ),
        }

    by_difficulty = {}

    for difficulty in (
        "Simple",
        "Medium",
        "Difficult",
    ):
        difficulty_results = [
            result
            for result in all_results
            if result["difficulty"]
            == difficulty
        ]

        by_difficulty[difficulty] = {
            "total": len(
                difficulty_results
            ),
            "success": sum(
                result["status"]
                == "success"
                for result
                in difficulty_results
            ),
        }

    return {
        "benchmark_version":
            BENCHMARK_VERSION,
        "prompt_version":
            PROMPT_VERSION,
        "started_at":
            benchmark_started_at,
        "completed_at":
            timestamp(),

        "total_cases":
            len(all_results),
        "successful_cases":
            len(successful),
        "failed_cases":
            len(failed),

        "average_latency_seconds":
            (
                round(
                    average_latency,
                    3,
                )
                if average_latency
                is not None
                else None
            ),

        "total_input_tokens":
            total_input_tokens,
        "total_output_tokens":
            total_output_tokens,
        "total_tokens":
            total_tokens,

        "by_language":
            by_language,

        "by_difficulty":
            by_difficulty,

        "failed_test_cases": [
            result["test_case"]
            for result in failed
        ],
    }


def main() -> None:
    validate_benchmark_distribution()

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    benchmark_started_at = timestamp()

    print("\nAI Program Review Assistant")
    print("30-Case Benchmark")
    print("=" * 70)
    print(
        f"Benchmark: {BENCHMARK_VERSION}"
    )
    print(
        f"Prompt:    {PROMPT_VERSION}"
    )
    print(
        f"Cases:     {len(BENCHMARK_CASES)}"
    )
    print(
        f"Output:    {RESULTS_DIR}"
    )

    all_results = []

    total_cases = len(
        BENCHMARK_CASES
    )

    for index, test_case in enumerate(
        BENCHMARK_CASES,
        start=1,
    ):
        output_path = result_path_for(
            test_case["id"]
        )

        if (
            SKIP_EXISTING
            and output_path.exists()
        ):
            print(
                f"\n[{index}/{total_cases}] "
                f"{test_case['id']} "
                f"already exists — skipping."
            )

            existing_result = (
                load_existing_result(
                    output_path
                )
            )

            all_results.append(
                existing_result
            )

            continue

        output = run_case(
            test_case,
            index,
            total_cases,
        )

        saved_path = save_result(
            output
        )

        all_results.append(
            output
        )

        if output["status"] == "success":
            metadata = output[
                "metadata"
            ]

            print(
                f"Status: SUCCESS"
            )
            print(
                f"Latency: "
                f"{metadata.get('latency_seconds')} sec"
            )
            print(
                f"Tokens:  "
                f"{metadata.get('total_tokens')}"
            )
        else:
            print(
                "Status: ERROR"
            )
            print(
                f"{output['error_type']}: "
                f"{output['error_message']}"
            )

        print(
            f"Saved: {saved_path}"
        )

    summary = build_summary(
        all_results,
        benchmark_started_at,
    )

    summary_path = (
        RESULTS_DIR
        / "summary.json"
    )

    summary_path.write_text(
        json.dumps(
            summary,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print("\n" + "=" * 70)
    print("BENCHMARK COMPLETE")
    print("=" * 70)

    print(
        f"Total cases:      "
        f"{summary['total_cases']}"
    )

    print(
        f"Successful:       "
        f"{summary['successful_cases']}"
    )

    print(
        f"Failed:           "
        f"{summary['failed_cases']}"
    )

    print(
        f"Average latency:  "
        f"{summary['average_latency_seconds']} sec"
    )

    print(
        f"Input tokens:     "
        f"{summary['total_input_tokens']}"
    )

    print(
        f"Output tokens:    "
        f"{summary['total_output_tokens']}"
    )

    print(
        f"Total tokens:     "
        f"{summary['total_tokens']}"
    )

    print(
        f"\nSummary saved: "
        f"{summary_path}"
    )


if __name__ == "__main__":
    main()