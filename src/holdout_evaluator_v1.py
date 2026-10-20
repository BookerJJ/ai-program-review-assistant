import csv
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

from .holdout_cases_v1 import (
    HOLDOUT_CASES,
    validate_holdout_distribution,
)
from .holdout_golden_v1 import (
    GOLDEN_EXPECTATIONS,
    TEST_INPUTS,
    validate_golden_expectations,
)


HOLDOUT_VERSION = "holdout-v1"
PROMPT_VERSION = "fewshot-v0.5"

RESULTS_DIR = (
    Path("results")
    / "holdout_v1"
    / "fewshot_v05"
)

OUTPUT_DIR = (
    Path("results")
    / "holdout_v1"
    / "evaluation"
)

REPORT_PATH = (
    OUTPUT_DIR
    / "holdout_objective_report.json"
)

CASE_CSV_PATH = (
    OUTPUT_DIR
    / "holdout_case_scores.csv"
)

CATEGORY_CSV_PATH = (
    OUTPUT_DIR
    / "holdout_category_summary.csv"
)


EXPECTED_TOP_LEVEL_KEYS = {
    "summary",
    "issues",
    "risks",
    "dependencies",
    "requirement_changes",
    "schedule_impacts",
    "actions",
    "uncertainties",
}


CATEGORIES = [
    "issues",
    "risks",
    "dependencies",
    "requirement_changes",
    "schedule_impacts",
    "actions",
    "uncertainties",
]


EVIDENCE_CATEGORIES = [
    "issues",
    "risks",
    "dependencies",
    "requirement_changes",
    "schedule_impacts",
    "actions",
]


def normalize_text(value: Any) -> str:
    if value is None:
        return ""

    value = str(value)

    value = re.sub(
        r"\s+",
        " ",
        value,
    )

    return value.strip().lower()


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
            f"Missing holdout result: {path}"
        )

    return json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )


def get_path(
    data: Any,
    path: str,
):
    current = data

    for part in path.split("."):

        if isinstance(
            current,
            list,
        ):
            try:
                index = int(part)
            except ValueError:
                return "<missing>"

            if (
                index < 0
                or index >= len(current)
            ):
                return "<missing>"

            current = current[index]

        elif isinstance(
            current,
            dict,
        ):
            if part not in current:
                return "<missing>"

            current = current[part]

        else:
            return "<missing>"

    return current


def category_from_path(
    path: str,
) -> str:
    return path.split(".")[0]


def evaluate_assertion(
    result: dict,
    assertion: dict,
) -> dict:

    path = assertion["path"]
    operation = assertion["op"]

    actual = get_path(
        result,
        path,
    )

    expected = assertion.get(
        "value"
    )

    if operation == "is_null":

        passed = (
            actual is None
        )

    elif operation == "equals":

        passed = (
            normalize_text(actual)
            ==
            normalize_text(expected)
        )

    elif operation == "contains":

        passed = (
            normalize_text(expected)
            in normalize_text(actual)
        )

    else:
        raise ValueError(
            f"Unsupported assertion operation: "
            f"{operation}"
        )

    return {
        "path":
            path,

        "category":
            category_from_path(
                path
            ),

        "operation":
            operation,

        "expected":
            expected,

        "actual":
            actual,

        "passed":
            passed,
    }


def evaluate_evidence(
    result: dict,
    source_text: str,
) -> dict:

    normalized_source = (
        normalize_text(
            source_text
        )
    )

    total = 0
    traceable = 0

    failures = []

    for category in (
        EVIDENCE_CATEGORIES
    ):

        items = result.get(
            category,
            [],
        )

        for item_index, item in enumerate(
            items
        ):

            evidence_list = item.get(
                "evidence",
                [],
            )

            for evidence in evidence_list:

                total += 1

                normalized_evidence = (
                    normalize_text(
                        evidence
                    )
                )

                if (
                    normalized_evidence
                    and normalized_evidence
                    in normalized_source
                ):
                    traceable += 1

                else:
                    failures.append(
                        {
                            "category":
                                category,

                            "item_index":
                                item_index,

                            "evidence":
                                evidence,
                        }
                    )

    if total == 0:
        rate = 1.0
    else:
        rate = (
            traceable
            / total
        )

    return {
        "total":
            total,

        "traceable":
            traceable,

        "rate":
            round(
                rate,
                3,
            ),

        "failures":
            failures,
    }


def evaluate_case(
    output: dict,
    case: dict,
) -> dict:

    test_id = case["id"]

    golden = (
        GOLDEN_EXPECTATIONS[
            test_id
        ]
    )

    result = output.get(
        "result",
        {}
    )

    metadata = output.get(
        "metadata",
        {}
    )

    structural_checks = []

    # ---------------------------------------------------------
    # Schema
    # ---------------------------------------------------------

    actual_keys = set(
        result.keys()
    )

    structural_checks.append(
        {
            "name":
                "top_level_keys",

            "category":
                "schema",

            "passed":
                actual_keys
                ==
                EXPECTED_TOP_LEVEL_KEYS,

            "expected":
                sorted(
                    EXPECTED_TOP_LEVEL_KEYS
                ),

            "actual":
                sorted(
                    actual_keys
                ),
        }
    )

    summary = result.get(
        "summary"
    )

    structural_checks.append(
        {
            "name":
                "summary_present",

            "category":
                "schema",

            "passed":
                (
                    isinstance(
                        summary,
                        str,
                    )
                    and bool(
                        summary.strip()
                    )
                ),

            "expected":
                "non-empty string",

            "actual":
                summary,
        }
    )

    # ---------------------------------------------------------
    # Category counts
    # ---------------------------------------------------------

    category_results = {}

    expected_counts = golden[
        "expected_counts"
    ]

    for category in CATEGORIES:

        actual_items = result.get(
            category,
            [],
        )

        actual_count = (
            len(actual_items)
            if isinstance(
                actual_items,
                list,
            )
            else 0
        )

        expected_count = (
            expected_counts[
                category
            ]
        )

        count_match = (
            actual_count
            ==
            expected_count
        )

        category_results[
            category
        ] = {
            "expected_count":
                expected_count,

            "actual_count":
                actual_count,

            "count_match":
                count_match,
        }

        structural_checks.append(
            {
                "name":
                    f"{category}_count",

                "category":
                    category,

                "passed":
                    count_match,

                "expected":
                    expected_count,

                "actual":
                    actual_count,
            }
        )

    # ---------------------------------------------------------
    # Assertions
    # ---------------------------------------------------------

    assertion_results = []

    for assertion in golden[
        "assertions"
    ]:

        evaluated = (
            evaluate_assertion(
                result,
                assertion,
            )
        )

        assertion_results.append(
            evaluated
        )

        structural_checks.append(
            {
                "name":
                    evaluated["path"],

                "category":
                    evaluated[
                        "category"
                    ],

                "passed":
                    evaluated[
                        "passed"
                    ],

                "expected":
                    evaluated[
                        "expected"
                    ],

                "actual":
                    evaluated[
                        "actual"
                    ],
            }
        )

    # ---------------------------------------------------------
    # IMPORTANT:
    # Evidence is evaluated separately.
    # It is NOT included in Structural Score.
    # ---------------------------------------------------------

    evidence = evaluate_evidence(
        result,
        TEST_INPUTS[test_id],
    )

    passed_checks = sum(
        check["passed"]
        for check in structural_checks
    )

    total_checks = len(
        structural_checks
    )

    structural_score = (
        passed_checks
        / total_checks
        * 100
        if total_checks
        else 0
    )

    return {
        "test_case":
            test_id,

        "language":
            case["language"],

        "scenario_type":
            case[
                "scenario_type"
            ],

        "primary_target":
            case[
                "primary_target"
            ],

        "prompt_version":
            output.get(
                "prompt_version"
            ),

        "status":
            output.get(
                "status"
            ),

        "structural_score":
            round(
                structural_score,
                1,
            ),

        "passed_checks":
            passed_checks,

        "total_checks":
            total_checks,

        "category_results":
            category_results,

        "assertions":
            assertion_results,

        "evidence_traceability":
            evidence,

        "latency_seconds":
            metadata.get(
                "latency_seconds"
            ),

        "input_tokens":
            metadata.get(
                "input_tokens"
            ),

        "output_tokens":
            metadata.get(
                "output_tokens"
            ),

        "total_tokens":
            metadata.get(
                "total_tokens"
            ),

        "manual_review":
            golden[
                "manual_review"
            ],

        "structural_checks":
            structural_checks,
    }


def summarize_group(
    rows: list[dict],
) -> dict:

    if not rows:
        return {
            "cases": 0,
            "average_structural_score": None,
            "average_evidence_traceability": None,
            "average_latency_seconds": None,
            "total_tokens": 0,
        }

    structural_scores = [
        row[
            "structural_score"
        ]
        for row in rows
    ]

    evidence_rates = [
        row[
            "evidence_traceability"
        ]["rate"]
        for row in rows
    ]

    latencies = [
        row[
            "latency_seconds"
        ]
        for row in rows
        if row[
            "latency_seconds"
        ] is not None
    ]

    total_tokens = sum(
        row.get(
            "total_tokens",
            0,
        )
        or 0
        for row in rows
    )

    return {
        "cases":
            len(rows),

        "average_structural_score":
            round(
                sum(
                    structural_scores
                )
                /
                len(
                    structural_scores
                ),
                1,
            ),

        "average_evidence_traceability":
            round(
                sum(
                    evidence_rates
                )
                /
                len(
                    evidence_rates
                ),
                3,
            ),

        "average_latency_seconds":
            (
                round(
                    sum(latencies)
                    / len(latencies),
                    3,
                )
                if latencies
                else None
            ),

        "total_tokens":
            total_tokens,
    }


def build_category_summary(
    evaluations: list[dict],
) -> dict:

    summary = {}

    for category in CATEGORIES:

        count_total = 0
        count_correct = 0

        assertion_total = 0
        assertion_correct = 0

        for row in evaluations:

            category_result = (
                row[
                    "category_results"
                ][category]
            )

            count_total += 1

            if category_result[
                "count_match"
            ]:
                count_correct += 1

            for assertion in row[
                "assertions"
            ]:

                if (
                    assertion[
                        "category"
                    ]
                    != category
                ):
                    continue

                assertion_total += 1

                if assertion[
                    "passed"
                ]:
                    assertion_correct += 1

        summary[
            category
        ] = {
            "count_accuracy":
                round(
                    count_correct
                    / count_total,
                    3,
                )
                if count_total
                else None,

            "assertion_accuracy":
                round(
                    assertion_correct
                    / assertion_total,
                    3,
                )
                if assertion_total
                else None,

            "assertion_count":
                assertion_total,
        }

    return summary


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
            for row
            in evaluations
        }
    )

    by_scenario_type = {}

    for scenario_type in (
        scenario_types
    ):

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
        "holdout_version":
            HOLDOUT_VERSION,

        "prompt_version":
            PROMPT_VERSION,

        "evaluation_role":
            "final_unseen_holdout",

        "evaluation_type":
            "objective_structural",

        "methodology_note":
            (
                "Structural Score excludes "
                "Evidence Traceability. "
                "Evidence is reported as a "
                "separate metric. Manual semantic "
                "review is still required."
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

    evaluations = []

    for case in HOLDOUT_CASES:

        output = load_result(
            case["id"]
        )

        if (
            output.get("status")
            != "success"
        ):
            raise RuntimeError(
                f"{case['id']} "
                "did not complete successfully."
            )

        evaluations.append(
            evaluate_case(
                output,
                case,
            )
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
        "\nFinal Holdout "
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