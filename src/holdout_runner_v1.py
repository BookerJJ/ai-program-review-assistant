import json
from datetime import datetime
from pathlib import Path

from .analyzer import analyze_project
from .holdout_cases_v1 import (
    HOLDOUT_CASES,
    validate_holdout_distribution,
)
from .holdout_golden_v1 import (
    validate_golden_expectations,
)
from .prompts import FEWSHOT_SYSTEM_PROMPT_V05


HOLDOUT_VERSION = "holdout-v1"
PROMPT_VERSION = "fewshot-v0.5"

RESULTS_DIR = (
    Path("results")
    / "holdout_v1"
    / "fewshot_v05"
)

# Existing result files are NEVER overwritten.
# This allows interrupted runs to resume without
# generating a second answer for the same holdout case.
SKIP_EXISTING = True


def timestamp() -> str:
    return datetime.now().astimezone().isoformat(
        timespec="seconds"
    )


def result_path_for(
    test_id: str,
) -> Path:
    filename = (
        test_id
        .lower()
        .replace("-", "")
        + ".json"
    )

    return RESULTS_DIR / filename


def load_existing_result(
    path: Path,
) -> dict:
    return json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )


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
        f"{test_case['scenario_type']}"
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
            system_prompt=FEWSHOT_SYSTEM_PROMPT_V05,
        )

        output = {
            "holdout_version":
                HOLDOUT_VERSION,

            "prompt_version":
                PROMPT_VERSION,

            "test_case":
                test_id,

            "language":
                test_case["language"],

            "scenario_type":
                test_case[
                    "scenario_type"
                ],

            "primary_target":
                test_case[
                    "primary_target"
                ],

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
            "holdout_version":
                HOLDOUT_VERSION,

            "prompt_version":
                PROMPT_VERSION,

            "test_case":
                test_id,

            "language":
                test_case["language"],

            "scenario_type":
                test_case[
                    "scenario_type"
                ],

            "primary_target":
                test_case[
                    "primary_target"
                ],

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

    if output_path.exists():
        raise FileExistsError(
            "Refusing to overwrite existing "
            f"holdout result: {output_path}"
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


def build_summary(
    all_results: list[dict],
    holdout_started_at: str,
) -> dict:

    successful = [
        result
        for result in all_results
        if result.get("status")
        == "success"
    ]

    failed = [
        result
        for result in all_results
        if result.get("status")
        != "success"
    ]

    latencies = [
        result["metadata"][
            "latency_seconds"
        ]
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
        sum(latencies)
        / len(latencies)
        if latencies
        else None
    )

    by_language = {}

    for language in (
        "English",
        "Korean",
    ):
        language_results = [
            result
            for result in all_results
            if result["language"]
            == language
        ]

        by_language[language] = {
            "total":
                len(
                    language_results
                ),

            "success":
                sum(
                    result["status"]
                    == "success"
                    for result
                    in language_results
                ),
        }

    scenario_types = sorted(
        {
            case["scenario_type"]
            for case in HOLDOUT_CASES
        }
    )

    by_scenario_type = {}

    for scenario_type in (
        scenario_types
    ):
        scenario_results = [
            result
            for result in all_results
            if result["scenario_type"]
            == scenario_type
        ]

        by_scenario_type[
            scenario_type
        ] = {
            "total":
                len(
                    scenario_results
                ),

            "success":
                sum(
                    result["status"]
                    == "success"
                    for result
                    in scenario_results
                ),
        }

    return {
        "holdout_version":
            HOLDOUT_VERSION,

        "prompt_version":
            PROMPT_VERSION,

        "evaluation_role":
            "final_unseen_holdout",

        "started_at":
            holdout_started_at,

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

        "by_scenario_type":
            by_scenario_type,

        "failed_test_cases": [
            result["test_case"]
            for result in failed
        ],
    }


def main() -> None:

    # ---------------------------------------------
    # Freeze validation
    # ---------------------------------------------

    validate_holdout_distribution()
    validate_golden_expectations()

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    holdout_started_at = timestamp()

    print(
        "\nAI Program Review Assistant"
    )

    print(
        "FINAL HOLDOUT EVALUATION"
    )

    print("=" * 70)

    print(
        f"Holdout:   "
        f"{HOLDOUT_VERSION}"
    )

    print(
        f"Prompt:    "
        f"{PROMPT_VERSION} "
        "(FROZEN)"
    )

    print(
        f"Cases:     "
        f"{len(HOLDOUT_CASES)}"
    )

    print(
        f"Output:    "
        f"{RESULTS_DIR}"
    )

    print(
        "\nIMPORTANT:"
    )

    print(
        "Existing holdout outputs "
        "will not be overwritten."
    )

    all_results = []

    total_cases = len(
        HOLDOUT_CASES
    )

    for index, test_case in enumerate(
        HOLDOUT_CASES,
        start=1,
    ):

        output_path = result_path_for(
            test_case["id"]
        )

        # -----------------------------------------
        # Preserve the original holdout output
        # -----------------------------------------

        if (
            SKIP_EXISTING
            and output_path.exists()
        ):
            print(
                f"\n[{index}/{total_cases}] "
                f"{test_case['id']} "
                "already exists — "
                "preserving original output."
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

        # -----------------------------------------
        # First and only model generation
        # -----------------------------------------

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

        if (
            output["status"]
            == "success"
        ):
            metadata = output[
                "metadata"
            ]

            print(
                "Status: SUCCESS"
            )

            print(
                "Latency: "
                f"{metadata.get('latency_seconds')} "
                "sec"
            )

            print(
                "Tokens:  "
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

    # ---------------------------------------------
    # Summary
    # ---------------------------------------------

    summary = build_summary(
        all_results,
        holdout_started_at,
    )

    summary_path = (
        RESULTS_DIR
        / "summary.json"
    )

    # summary may be regenerated safely because
    # it does not change individual model outputs.
    summary_path.write_text(
        json.dumps(
            summary,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(
        "\n" + "=" * 70
    )

    print(
        "HOLDOUT RUN COMPLETE"
    )

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
        f"{summary['average_latency_seconds']} "
        "sec"
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
        "\nBy Language"
    )

    for language, values in (
        summary[
            "by_language"
        ].items()
    ):
        print(
            f"{language:<10} "
            f"{values['success']}"
            f"/{values['total']}"
        )

    print(
        "\nBy Scenario Type"
    )

    for scenario_type, values in (
        summary[
            "by_scenario_type"
        ].items()
    ):
        print(
            f"{scenario_type:<26} "
            f"{values['success']}"
            f"/{values['total']}"
        )

    print(
        "\nSummary saved:"
    )

    print(
        summary_path
    )


if __name__ == "__main__":
    main()