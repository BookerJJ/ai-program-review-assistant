import csv
import json
from pathlib import Path

from .holdout_cases_v1 import (
    HOLDOUT_CASES,
    validate_holdout_distribution,
)
from .holdout_golden_v1 import (
    validate_golden_expectations,
)
from .holdout_evaluator_v1 import (
    evaluate_case,
    summarize_group,
    build_category_summary,
)


COMPARISON_VERSION = "model-comparison-v1"
HOLDOUT_VERSION = "holdout-v1"
PROMPT_VERSION = "fewshot-v0.5"

PROVIDER = "google"
MODEL = "gemini-3.8-flash"


RESULTS_DIR = (
    Path("results")
    / "model_comparison_v1"
    / "gemini_3_8_flash"
)

OUTPUT_DIR = (
    RESULTS_DIR
    / "evaluation"
)

REPORT_PATH = (
    OUTPUT_DIR
    / "gemini_objective_report.json"
)

CASE_CSV_PATH = (
    OUTPUT_DIR
    / "gemini_case_scores.csv"
)

CATEGORY_CSV_PATH = (
    OUTPUT_DIR
    / "gemini_category_summary.csv"
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


def load_result(
    test_id: str,
) -> dict:

    path = result_path_for(
        test_id
    )

    if not path.exists():
        raise FileNotFoundError(
            f"Missing Gemini result: {path}"
        )

    return json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )


def validate_result(
    output: dict,
    test_id: str,
) -> None:

    if (
        output.get("status")
        != "success"
    ):
        raise RuntimeError(
            f"{test_id} did not "
            "complete successfully."
        )

    if (
        output.get("test_case")
        != test_id
    ):
        raise RuntimeError(
            f"{test_id}: test_case mismatch. "
            f"Found {output.get('test_case')}."
        )

    if (
        output.get("prompt_version")
        != PROMPT_VERSION
    ):
        raise RuntimeError(
            f"{test_id}: expected prompt "
            f"{PROMPT_VERSION}, got "
            f"{output.get('prompt_version')}."
        )

    if (
        output.get("holdout_version")
        != HOLDOUT_VERSION
    ):
        raise RuntimeError(
            f"{test_id}: expected holdout "
            f"{HOLDOUT_VERSION}, got "
            f"{output.get('holdout_version')}."
        )

    if (
        output.get("comparison_version")
        != COMPARISON_VERSION
    ):
        raise RuntimeError(
            f"{test_id}: expected comparison "
            f"{COMPARISON_VERSION}, got "
            f"{output.get('comparison_version')}."
        )

    if (
        output.get("provider")
        != PROVIDER
    ):
        raise RuntimeError(
            f"{test_id}: expected provider "
            f"{PROVIDER}, got "
            f"{output.get('provider')}."
        )

    if (
        output.get("model")
        != MODEL
    ):
        raise RuntimeError(
            f"{test_id}: expected model "
            f"{MODEL}, got "
            f"{output.get('model')}."
        )


def load_evaluations() -> list[dict]:

    evaluations = []

    for case in HOLDOUT_CASES:

        test_id = case["id"]

        output = load_result(
            test_id
        )

        validate_result(
            output,
            test_id,
        )

        evaluations.append(
            evaluate_case(
                output,
                case,
            )
        )

    if len(evaluations) != 20:
        raise RuntimeError(
            "Expected 20 Gemini holdout "
            f"results, found {len(evaluations)}."
        )

    return evaluations


def build_report(
    evaluations: list[dict],
) -> dict:

    by_language = {}

    for language in (
        "English",
        "Korean",
    ):

        rows = [
            row
            for row in evaluations
            if row["language"]
            == language
        ]

        by_language[
            language
        ] = summarize_group(
            rows
        )

    scenario_types = sorted(
        {
            row[
                "scenario_type"
            ]
            for row in evaluations
        }
    )

    by_scenario_type = {}

    for scenario_type in scenario_types:

        rows = [
            row
            for row in evaluations
            if row[
                "scenario_type"
            ]
            == scenario_type
        ]

        by_scenario_type[
            scenario_type
        ] = summarize_group(
            rows
        )

    return {
        "comparison_version":
            COMPARISON_VERSION,

        "holdout_version":
            HOLDOUT_VERSION,

        "prompt_version":
            PROMPT_VERSION,

        "provider":
            PROVIDER,

        "model":
            MODEL,

        "evaluation_role":
            "cross_model_holdout",

        "evaluation_type":
            "objective_structural",

        "methodology_note":
            (
                "Uses the same frozen holdout inputs, "
                "golden expectations, structural "
                "evaluation logic, and strict evidence "
                "traceability method used for the "
                "qwen3:8b final holdout. Structural "
                "Score excludes Evidence Traceability. "
                "Human semantic review remains separate."
            ),

        "overall":
            summarize_group(
                evaluations
            ),

        "by_language":
            by_language,

        "by_scenario_type":
            by_scenario_type,

        "by_category":
            build_category_summary(
                evaluations
            ),

        "cases":
            evaluations,
    }


def save_case_csv(
    evaluations: list[dict],
) -> None:

    fields = [
        "test_case",
        "language",
        "scenario_type",
        "structural_score",
        "evidence_traceability",
        "latency_seconds",
        "total_tokens",
    ]

    with CASE_CSV_PATH.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fields,
        )

        writer.writeheader()

        for row in evaluations:

            writer.writerow(
                {
                    "test_case":
                        row[
                            "test_case"
                        ],

                    "language":
                        row[
                            "language"
                        ],

                    "scenario_type":
                        row[
                            "scenario_type"
                        ],

                    "structural_score":
                        row[
                            "structural_score"
                        ],

                    "evidence_traceability":
                        row[
                            "evidence_traceability"
                        ]["rate"],

                    "latency_seconds":
                        row[
                            "latency_seconds"
                        ],

                    "total_tokens":
                        row[
                            "total_tokens"
                        ],
                }
            )


def save_category_csv(
    report: dict,
) -> None:

    fields = [
        "category",
        "count_accuracy",
        "assertion_accuracy",
        "assertion_count",
    ]

    with CATEGORY_CSV_PATH.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fields,
        )

        writer.writeheader()

        for category, values in (
            report[
                "by_category"
            ].items()
        ):

            writer.writerow(
                {
                    "category":
                        category,

                    "count_accuracy":
                        values[
                            "count_accuracy"
                        ],

                    "assertion_accuracy":
                        values[
                            "assertion_accuracy"
                        ],

                    "assertion_count":
                        values[
                            "assertion_count"
                        ],
                }
            )


def main() -> None:

    validate_holdout_distribution()
    validate_golden_expectations()

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    evaluations = (
        load_evaluations()
    )

    report = build_report(
        evaluations
    )

    REPORT_PATH.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    save_case_csv(
        evaluations
    )

    save_category_csv(
        report
    )

    overall = report[
        "overall"
    ]

    print(
        "\nGemini Holdout "
        "Objective Evaluation"
    )

    print("=" * 70)

    print(
        "Structural Score:       "
        f"{overall['average_structural_score']}"
    )

    print(
        "Evidence Traceability:  "
        f"{overall['average_evidence_traceability']}"
    )

    print(
        "Average Latency:        "
        f"{overall['average_latency_seconds']} sec"
    )

    print(
        "Total Tokens:           "
        f"{overall['total_tokens']}"
    )

    print(
        "\nBy Language"
    )

    for language, values in (
        report[
            "by_language"
        ].items()
    ):

        print(
            f"{language:<10} "
            f"Structural="
            f"{values['average_structural_score']}, "
            f"Evidence="
            f"{values['average_evidence_traceability']}"
        )

    print(
        "\nBy Scenario Type"
    )

    for scenario_type, values in (
        report[
            "by_scenario_type"
        ].items()
    ):

        print(
            f"{scenario_type:<26} "
            f"Structural="
            f"{values['average_structural_score']}, "
            f"Evidence="
            f"{values['average_evidence_traceability']}"
        )

    print(
        "\nBy Category"
    )

    for category, values in (
        report[
            "by_category"
        ].items()
    ):

        print(
            f"{category:<22} "
            f"count="
            f"{values['count_accuracy']}, "
            f"assertion="
            f"{values['assertion_accuracy']}"
        )

    print(
        "\nFiles created:"
    )

    print(
        REPORT_PATH
    )

    print(
        CASE_CSV_PATH
    )

    print(
        CATEGORY_CSV_PATH
    )


if __name__ == "__main__":
    main()