import csv
import json
from pathlib import Path

from .benchmark_cases_v1 import BENCHMARK_CASES
from .benchmark_evaluator_v1 import (
    evaluate_case,
    summarize_group,
    build_category_summary,
)


VERSIONS = {
    "fewshot-v0.5": (
        Path("results")
        / "benchmark_v1"
        / "fewshot_v05"
    ),

    "fewshot-boundary-v0.6": (
        Path("results")
        / "benchmark_v1"
        / "fewshot_v06"
    ),
}


OUTPUT_DIR = (
    Path("results")
    / "benchmark_v1"
    / "comparison"
)


def result_path_for(
    results_dir: Path,
    test_id: str,
) -> Path:
    filename = (
        test_id
        .lower()
        .replace("-", "")
        + ".json"
    )

    return results_dir / filename


def load_version_evaluations(
    version_name: str,
    results_dir: Path,
) -> list[dict]:
    evaluations = []

    for case in BENCHMARK_CASES:
        path = result_path_for(
            results_dir,
            case["id"],
        )

        if not path.exists():
            raise FileNotFoundError(
                f"{version_name}: "
                f"missing {path}"
            )

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
                f"{version_name}: "
                f"{case['id']} "
                "did not succeed."
            )

        evaluations.append(
            evaluate_case(
                output,
                case,
            )
        )

    return evaluations


def build_version_report(
    version_name: str,
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

        by_difficulty[difficulty] = (
            summarize_group(rows)
        )

    return {
        "version":
            version_name,

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


def difference(
    new_value,
    old_value,
):
    if (
        new_value is None
        or old_value is None
    ):
        return None

    return round(
        new_value - old_value,
        3,
    )


def build_comparison(
    reports: dict,
) -> dict:
    old = reports[
        "fewshot-v0.5"
    ]

    new = reports[
        "fewshot-boundary-v0.6"
    ]

    overall = {
        "structural_score": {
            "v0.5":
                old["overall"][
                    "average_structural_score"
                ],

            "v0.6":
                new["overall"][
                    "average_structural_score"
                ],
        },

        "evidence_traceability": {
            "v0.5":
                old["overall"][
                    "average_evidence_traceability"
                ],

            "v0.6":
                new["overall"][
                    "average_evidence_traceability"
                ],
        },

        "latency_seconds": {
            "v0.5":
                old["overall"][
                    "average_latency_seconds"
                ],

            "v0.6":
                new["overall"][
                    "average_latency_seconds"
                ],
        },

        "total_tokens": {
            "v0.5":
                old["overall"][
                    "total_tokens"
                ],

            "v0.6":
                new["overall"][
                    "total_tokens"
                ],
        },
    }

    for metric in (
        "structural_score",
        "evidence_traceability",
        "latency_seconds",
        "total_tokens",
    ):
        overall[metric]["delta"] = (
            difference(
                overall[metric]["v0.6"],
                overall[metric]["v0.5"],
            )
        )

    categories = {}

    old_categories = (
        old["by_category"]
    )

    new_categories = (
        new["by_category"]
    )

    for category in (
        old_categories.keys()
    ):
        old_values = (
            old_categories[
                category
            ]
        )

        new_values = (
            new_categories[
                category
            ]
        )

        categories[category] = {
            "count_accuracy": {
                "v0.5":
                    old_values[
                        "count_accuracy"
                    ],

                "v0.6":
                    new_values[
                        "count_accuracy"
                    ],

                "delta":
                    difference(
                        new_values[
                            "count_accuracy"
                        ],
                        old_values[
                            "count_accuracy"
                        ],
                    ),
            },

            "assertion_accuracy": {
                "v0.5":
                    old_values[
                        "assertion_accuracy"
                    ],

                "v0.6":
                    new_values[
                        "assertion_accuracy"
                    ],

                "delta":
                    difference(
                        new_values[
                            "assertion_accuracy"
                        ],
                        old_values[
                            "assertion_accuracy"
                        ],
                    ),
            },
        }

    language = {}

    for lang in (
        "English",
        "Korean",
    ):
        old_value = (
            old["by_language"][
                lang
            ][
                "average_structural_score"
            ]
        )

        new_value = (
            new["by_language"][
                lang
            ][
                "average_structural_score"
            ]
        )

        language[lang] = {
            "v0.5": old_value,
            "v0.6": new_value,
            "delta": difference(
                new_value,
                old_value,
            ),
        }

    difficulty = {}

    for level in (
        "Simple",
        "Medium",
        "Difficult",
    ):
        old_value = (
            old["by_difficulty"][
                level
            ][
                "average_structural_score"
            ]
        )

        new_value = (
            new["by_difficulty"][
                level
            ][
                "average_structural_score"
            ]
        )

        difficulty[level] = {
            "v0.5": old_value,
            "v0.6": new_value,
            "delta": difference(
                new_value,
                old_value,
            ),
        }

    case_comparison = []

    old_cases = {
        row["test_case"]: row
        for row in old["cases"]
    }

    new_cases = {
        row["test_case"]: row
        for row in new["cases"]
    }

    for case in BENCHMARK_CASES:
        test_id = case["id"]

        old_case = old_cases[
            test_id
        ]

        new_case = new_cases[
            test_id
        ]

        case_comparison.append(
            {
                "test_case":
                    test_id,

                "language":
                    case["language"],

                "difficulty":
                    case["difficulty"],

                "v05_structural":
                    old_case[
                        "structural_score"
                    ],

                "v06_structural":
                    new_case[
                        "structural_score"
                    ],

                "structural_delta":
                    difference(
                        new_case[
                            "structural_score"
                        ],
                        old_case[
                            "structural_score"
                        ],
                    ),

                "v05_evidence":
                    old_case[
                        "evidence_traceability"
                    ]["rate"],

                "v06_evidence":
                    new_case[
                        "evidence_traceability"
                    ]["rate"],

                "evidence_delta":
                    difference(
                        new_case[
                            "evidence_traceability"
                        ]["rate"],
                        old_case[
                            "evidence_traceability"
                        ]["rate"],
                    ),
            }
        )

    return {
        "benchmark_version":
            "benchmark-v1",

        "baseline_version":
            "fewshot-v0.5",

        "candidate_version":
            "fewshot-boundary-v0.6",

        "overall":
            overall,

        "by_language":
            language,

        "by_difficulty":
            difficulty,

        "by_category":
            categories,

        "cases":
            case_comparison,
    }


def save_case_csv(
    comparison: dict,
) -> Path:
    path = (
        OUTPUT_DIR
        / "v05_vs_v06_cases.csv"
    )

    fields = [
        "test_case",
        "language",
        "difficulty",
        "v05_structural",
        "v06_structural",
        "structural_delta",
        "v05_evidence",
        "v06_evidence",
        "evidence_delta",
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

        writer.writerows(
            comparison["cases"]
        )

    return path


def save_category_csv(
    comparison: dict,
) -> Path:
    path = (
        OUTPUT_DIR
        / "v05_vs_v06_categories.csv"
    )

    fields = [
        "category",
        "v05_count_accuracy",
        "v06_count_accuracy",
        "count_delta",
        "v05_assertion_accuracy",
        "v06_assertion_accuracy",
        "assertion_delta",
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
            comparison[
                "by_category"
            ].items()
        ):
            count = values[
                "count_accuracy"
            ]

            assertion = values[
                "assertion_accuracy"
            ]

            writer.writerow(
                {
                    "category":
                        category,

                    "v05_count_accuracy":
                        count["v0.5"],

                    "v06_count_accuracy":
                        count["v0.6"],

                    "count_delta":
                        count["delta"],

                    "v05_assertion_accuracy":
                        assertion["v0.5"],

                    "v06_assertion_accuracy":
                        assertion["v0.6"],

                    "assertion_delta":
                        assertion["delta"],
                }
            )

    return path


def main() -> None:
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    reports = {}

    for (
        version_name,
        results_dir,
    ) in VERSIONS.items():

        evaluations = (
            load_version_evaluations(
                version_name,
                results_dir,
            )
        )

        reports[
            version_name
        ] = build_version_report(
            version_name,
            evaluations,
        )

    comparison = (
        build_comparison(
            reports
        )
    )

    json_path = (
        OUTPUT_DIR
        / "v05_vs_v06_comparison.json"
    )

    json_path.write_text(
        json.dumps(
            comparison,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    case_csv = save_case_csv(
        comparison
    )

    category_csv = (
        save_category_csv(
            comparison
        )
    )

    print(
        "\nv0.5 vs v0.6 "
        "Benchmark Comparison"
    )
    print("=" * 65)

    overall = (
        comparison["overall"]
    )

    for metric, values in (
        overall.items()
    ):
        print(
            f"{metric:<24}"
            f"{values['v0.5']} "
            f"-> {values['v0.6']} "
            f"(delta {values['delta']})"
        )

    print(
        "\nCategory Comparison"
    )

    for category, values in (
        comparison[
            "by_category"
        ].items()
    ):
        count = values[
            "count_accuracy"
        ]

        assertion = values[
            "assertion_accuracy"
        ]

        print(
            f"{category:<22} "
            f"count "
            f"{count['v0.5']} "
            f"-> {count['v0.6']} "
            f"({count['delta']}), "
            f"assertion "
            f"{assertion['v0.5']} "
            f"-> {assertion['v0.6']} "
            f"({assertion['delta']})"
        )

    print(
        "\nFiles created:"
    )
    print(json_path)
    print(case_csv)
    print(category_csv)


if __name__ == "__main__":
    main()