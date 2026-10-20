import csv
import json
import re
from pathlib import Path
from typing import Any

from .benchmark_cases_v1 import BENCHMARK_CASES
from .benchmark_golden_v1 import (
    GOLDEN_EXPECTATIONS,
    TEST_INPUTS,
)


RESULTS_DIR = (
    Path("results")
    / "benchmark_v1"
    / "fewshot_v05"
)

OUTPUT_DIR = (
    Path("results")
    / "benchmark_v1"
    / "evaluation"
)

EXPECTED_PROMPT_VERSION = "fewshot-v0.5"

EXPECTED_RESULT_KEYS = {
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

MISSING = object()


def normalize_text(value: str) -> str:
    value = re.sub(r"\s+", " ", value)
    return value.strip().casefold()


def get_path(
    data: Any,
    path: str,
) -> Any:
    current = data

    try:
        for part in path.split("."):
            if isinstance(current, list):
                current = current[int(part)]
            else:
                current = current[part]

        return current

    except (
        KeyError,
        IndexError,
        TypeError,
        ValueError,
    ):
        return MISSING


def evaluate_assertion(
    result: dict,
    assertion: dict,
) -> dict:
    path = assertion["path"]
    operation = assertion["op"]
    actual = get_path(result, path)

    if operation == "is_null":
        expected = None
        passed = actual is None

    elif operation == "equals":
        expected = assertion["value"]

        if actual is MISSING:
            passed = False

        elif (
            isinstance(actual, str)
            and isinstance(expected, str)
        ):
            passed = (
                normalize_text(actual)
                == normalize_text(expected)
            )

        else:
            passed = actual == expected

    elif operation == "contains":
        expected = assertion["value"]

        passed = (
            isinstance(actual, str)
            and normalize_text(expected)
            in normalize_text(actual)
        )

    else:
        raise ValueError(
            f"Unsupported operation: {operation}"
        )

    return {
        "path": path,
        "category": path.split(".")[0],
        "operation": operation,
        "expected": expected,
        "actual": (
            "<missing>"
            if actual is MISSING
            else actual
        ),
        "passed": passed,
    }


def evaluate_evidence_traceability(
    result: dict,
    source_text: str,
) -> dict:
    """
    Strict evidence test:
    evidence should be directly traceable to
    text in the supplied input.
    """

    normalized_source = normalize_text(
        source_text
    )

    total = 0
    traceable = 0
    failures = []

    for category in EVIDENCE_CATEGORIES:
        items = result.get(category, [])

        for item_index, item in enumerate(items):
            for evidence in item.get(
                "evidence",
                [],
            ):
                total += 1

                found = (
                    normalize_text(evidence)
                    in normalized_source
                )

                if found:
                    traceable += 1
                else:
                    failures.append(
                        {
                            "category": category,
                            "item_index": item_index,
                            "evidence": evidence,
                        }
                    )

    rate = (
        traceable / total
        if total
        else 1.0
    )

    return {
        "total": total,
        "traceable": traceable,
        "rate": round(rate, 3),
        "failures": failures,
    }


def evaluate_case(
    output: dict,
    case: dict,
) -> dict:
    test_id = case["id"]

    expectation = (
        GOLDEN_EXPECTATIONS[test_id]
    )

    result = output.get(
        "result",
        {},
    )

    checks = []

    # ---------------------------------------------
    # Top-level schema structure
    # ---------------------------------------------

    actual_keys = set(result.keys())

    checks.append(
        {
            "name": "top_level_keys",
            "category": "schema",
            "passed": (
                actual_keys
                == EXPECTED_RESULT_KEYS
            ),
            "expected": sorted(
                EXPECTED_RESULT_KEYS
            ),
            "actual": sorted(
                actual_keys
            ),
        }
    )

    summary = result.get("summary")

    checks.append(
        {
            "name": "summary_present",
            "category": "schema",
            "passed": (
                isinstance(summary, str)
                and bool(summary.strip())
            ),
            "expected": "non-empty string",
            "actual": summary,
        }
    )

    # ---------------------------------------------
    # Category count checks
    # ---------------------------------------------

    category_results = {}

    for category in CATEGORIES:
        expected_count = (
            expectation[
                "expected_counts"
            ][category]
        )

        actual_items = result.get(
            category
        )

        actual_count = (
            len(actual_items)
            if isinstance(
                actual_items,
                list,
            )
            else None
        )

        passed = (
            actual_count
            == expected_count
        )

        category_results[category] = {
            "expected_count":
                expected_count,
            "actual_count":
                actual_count,
            "count_match":
                passed,
        }

        checks.append(
            {
                "name":
                    f"{category}_count",
                "category":
                    category,
                "passed":
                    passed,
                "expected":
                    expected_count,
                "actual":
                    actual_count,
            }
        )

    # ---------------------------------------------
    # Golden field assertions
    # ---------------------------------------------

    assertion_results = []

    for assertion in expectation[
        "assertions"
    ]:
        assertion_result = (
            evaluate_assertion(
                result,
                assertion,
            )
        )

        assertion_results.append(
            assertion_result
        )

        checks.append(
            {
                "name":
                    assertion_result[
                        "path"
                    ],
                "category":
                    assertion_result[
                        "category"
                    ],
                "passed":
                    assertion_result[
                        "passed"
                    ],
                "expected":
                    assertion_result[
                        "expected"
                    ],
                "actual":
                    assertion_result[
                        "actual"
                    ],
            }
        )

    # ---------------------------------------------
    # Evidence traceability
    # ---------------------------------------------

    evidence = (
        evaluate_evidence_traceability(
            result,
            TEST_INPUTS[test_id],
        )
    )

    checks.append(
        {
            "name":
                "evidence_traceability",
            "category":
                "evidence",
            "passed":
                evidence["rate"] == 1.0,
            "expected":
                1.0,
            "actual":
                evidence["rate"],
        }
    )

    # ---------------------------------------------
    # Structural score
    #
    # Evidence traceability is evaluated
    # separately and is not included in the
    # Structural Score.
    # ---------------------------------------------

    structural_checks = [
        check
        for check in checks
        if check["category"] != "evidence"
    ]

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

    metadata = output.get(
        "metadata",
        {},
    )

    return {
        "test_case": test_id,
        "language": case["language"],
        "difficulty":
            case["difficulty"],
        "primary_target":
            case["primary_target"],
        "prompt_version":
            output.get(
                "prompt_version"
            ),
        "status":
            output.get("status"),

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
            expectation[
                "manual_review"
            ],

        "checks":
            checks,
    }


def load_results() -> list[dict]:
    evaluations = []

    for case in BENCHMARK_CASES:
        test_id = case["id"]

        filename = (
            test_id
            .lower()
            .replace("-", "")
            + ".json"
        )

        path = (
            RESULTS_DIR
            / filename
        )

        if not path.exists():
            print(
                f"Missing: {path}"
            )
            continue

        output = json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

        if (
            output.get("status")
            != "success"
        ):
            raise RuntimeError(
                f"{test_id} did not "
                "complete successfully. "
                "Execution failures must not be "
                "scored as model-quality failures."
            )

        if (
            output.get("prompt_version")
            != EXPECTED_PROMPT_VERSION
        ):
            raise RuntimeError(
                f"{test_id}: expected prompt "
                f"{EXPECTED_PROMPT_VERSION}, got "
                f"{output.get('prompt_version')}."
            )

        evaluations.append(
            evaluate_case(
                output,
                case,
            )
        )

    return evaluations


def average(
    values: list[float],
) -> float | None:
    if not values:
        return None

    return sum(values) / len(values)


def summarize_group(
    rows: list[dict],
) -> dict:
    scores = [
        row["structural_score"]
        for row in rows
    ]

    evidence_rates = [
        row[
            "evidence_traceability"
        ]["rate"]
        for row in rows
    ]

    latencies = [
        row["latency_seconds"]
        for row in rows
        if row["latency_seconds"]
        is not None
    ]

    return {
        "cases": len(rows),

        "average_structural_score":
            round(
                average(scores),
                1,
            ),

        "average_evidence_traceability":
            round(
                average(
                    evidence_rates
                ),
                3,
            ),

        "average_latency_seconds":
            round(
                average(latencies),
                3,
            ),

        "total_tokens":
            sum(
                row["total_tokens"] or 0
                for row in rows
            ),
    }


def build_category_summary(
    evaluations: list[dict],
) -> dict:
    summary = {}

    for category in CATEGORIES:
        count_checks = []

        assertion_checks = []

        for evaluation in evaluations:
            category_result = (
                evaluation[
                    "category_results"
                ][category]
            )

            count_checks.append(
                category_result[
                    "count_match"
                ]
            )

            for assertion in (
                evaluation[
                    "assertions"
                ]
            ):
                if (
                    assertion["category"]
                    == category
                ):
                    assertion_checks.append(
                        assertion["passed"]
                    )

        count_accuracy = (
            sum(count_checks)
            / len(count_checks)
        )

        assertion_accuracy = (
            sum(assertion_checks)
            / len(assertion_checks)
            if assertion_checks
            else None
        )

        summary[category] = {
            "count_accuracy":
                round(
                    count_accuracy,
                    3,
                ),

            "assertion_accuracy":
                (
                    round(
                        assertion_accuracy,
                        3,
                    )
                    if assertion_accuracy
                    is not None
                    else None
                ),

            "assertion_count":
                len(
                    assertion_checks
                ),
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

        by_language[language] = (
            summarize_group(rows)
        )

    by_difficulty = {}

    for difficulty in (
        "Simple",
        "Medium",
        "Difficult",
    ):
        rows = [
            row
            for row in evaluations
            if row["difficulty"]
            == difficulty
        ]

        by_difficulty[
            difficulty
        ] = summarize_group(
            rows
        )

    return {
        "benchmark_version":
            "benchmark-v1",

        "prompt_version":
            EXPECTED_PROMPT_VERSION,

        "evaluation_type":
            "objective_structural",

        "note": (
            "Structural Score excludes "
            "Evidence Traceability. Evidence "
            "is reported separately, and "
            "Structural scores do not represent "
            "full semantic accuracy. Manual "
            "review is still required."
        ),

        "overall":
            summarize_group(
                evaluations
            ),

        "by_language":
            by_language,

        "by_difficulty":
            by_difficulty,

        "by_category":
            build_category_summary(
                evaluations
            ),

        "cases":
            evaluations,
    }


def save_case_csv(
    evaluations: list[dict],
) -> Path:
    path = (
        OUTPUT_DIR
        / "benchmark_case_scores.csv"
    )

    fields = [
        "test_case",
        "language",
        "difficulty",
        "structural_score",
        "evidence_traceability",
        "latency_seconds",
        "input_tokens",
        "output_tokens",
        "total_tokens",
    ]

    with path.open(
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
                        row["test_case"],

                    "language":
                        row["language"],

                    "difficulty":
                        row["difficulty"],

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

                    "input_tokens":
                        row[
                            "input_tokens"
                        ],

                    "output_tokens":
                        row[
                            "output_tokens"
                        ],

                    "total_tokens":
                        row[
                            "total_tokens"
                        ],
                }
            )

    return path


def save_category_csv(
    category_summary: dict,
) -> Path:
    path = (
        OUTPUT_DIR
        / "benchmark_category_summary.csv"
    )

    fields = [
        "category",
        "count_accuracy",
        "assertion_accuracy",
        "assertion_count",
    ]

    with path.open(
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
            category_summary.items()
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

    return path


def main() -> None:
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    evaluations = load_results()

    if len(evaluations) != 30:
        raise RuntimeError(
            "Expected 30 benchmark "
            f"results, found "
            f"{len(evaluations)}."
        )

    report = build_report(
        evaluations
    )

    report_path = (
        OUTPUT_DIR
        / "benchmark_objective_report.json"
    )

    report_path.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    case_csv = save_case_csv(
        evaluations
    )

    category_csv = (
        save_category_csv(
            report["by_category"]
        )
    )

    print("\n30-Case Benchmark Evaluation")
    print("=" * 60)

    overall = report["overall"]

    print(
        "Overall Structural Score: "
        f"{overall['average_structural_score']}"
    )

    print(
        "Evidence Traceability:    "
        f"{overall['average_evidence_traceability']}"
    )

    print(
        "Average Latency:          "
        f"{overall['average_latency_seconds']} sec"
    )

    print(
        "Total Tokens:             "
        f"{overall['total_tokens']}"
    )

    print("\nBy Language")

    for language, values in (
        report["by_language"].items()
    ):
        print(
            f"{language:<10} "
            f"Structural="
            f"{values['average_structural_score']}, "
            f"Evidence="
            f"{values['average_evidence_traceability']}"
        )

    print("\nBy Difficulty")

    for difficulty, values in (
        report[
            "by_difficulty"
        ].items()
    ):
        print(
            f"{difficulty:<10} "
            f"Structural="
            f"{values['average_structural_score']}, "
            f"Evidence="
            f"{values['average_evidence_traceability']}"
        )

    print("\nFiles created:")
    print(report_path)
    print(case_csv)
    print(category_csv)
