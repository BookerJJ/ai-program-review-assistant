import csv
import json
from pathlib import Path

from .benchmark_cases_v1 import BENCHMARK_CASES
from .benchmark_golden_v1 import GOLDEN_EXPECTATIONS


RESULTS_DIR = (
    Path("results")
    / "benchmark_v1"
    / "fewshot_v05"
)

OUTPUT_DIR = (
    Path("results")
    / "benchmark_v1"
    / "human_review"
)

JSON_OUTPUT = (
    OUTPUT_DIR
    / "benchmark_review_pack.json"
)

CSV_OUTPUT = (
    OUTPUT_DIR
    / "benchmark_human_review_template.csv"
)


HUMAN_DIMENSIONS = [
    "factual_correctness",
    "completeness",
    "unsupported_claim_control",
    "classification_accuracy",
    "meaning_preservation",
]


def result_path_for(test_id: str) -> Path:
    filename = (
        test_id
        .lower()
        .replace("-", "")
        + ".json"
    )

    return RESULTS_DIR / filename


def load_result(test_id: str) -> dict:
    path = result_path_for(test_id)

    if not path.exists():
        raise FileNotFoundError(
            f"Missing benchmark result: {path}"
        )

    return json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )


def build_review_item(
    case: dict,
) -> dict:
    test_id = case["id"]

    output = load_result(
        test_id
    )

    golden = GOLDEN_EXPECTATIONS[
        test_id
    ]

    if output.get("status") != "success":
        raise RuntimeError(
            f"{test_id} did not complete successfully."
        )

    result = output["result"]
    metadata = output.get(
        "metadata",
        {}
    )

    return {
        "test_case":
            test_id,

        "language":
            case["language"],

        "difficulty":
            case["difficulty"],

        "primary_target":
            case["primary_target"],

        "input":
            case["input"],

        "golden_expectations": {
            "expected_counts":
                golden[
                    "expected_counts"
                ],

            "assertions":
                golden[
                    "assertions"
                ],

            "manual_review":
                golden[
                    "manual_review"
                ],
        },

        "model_output":
            result,

        "metadata": {
            "prompt_version":
                output.get(
                    "prompt_version"
                ),

            "model":
                metadata.get(
                    "model"
                ),

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
        },

        "human_evaluation": {
            "factual_correctness":
                None,

            "completeness":
                None,

            "unsupported_claim_control":
                None,

            "classification_accuracy":
                None,

            "meaning_preservation":
                None,

            "semantic_score":
                None,

            "review_notes":
                "",
        },
    }


def build_review_pack() -> dict:
    items = [
        build_review_item(case)
        for case in BENCHMARK_CASES
    ]

    return {
        "benchmark_version":
            "benchmark-v1",

        "prompt_version":
            "fewshot-v0.5",

        "human_evaluation_scale": {
            "0":
                "Incorrect or substantially fails the dimension.",

            "1":
                "Partially correct, with meaningful errors or omissions.",

            "2":
                "Correct or substantially correct for the dimension.",
        },

        "dimensions": {
            "factual_correctness":
                (
                    "Are extracted facts consistent "
                    "with the supplied input?"
                ),

            "completeness":
                (
                    "Are the important supported "
                    "findings captured?"
                ),

            "unsupported_claim_control":
                (
                    "Does the output avoid claims, "
                    "causes, impacts, dates, owners, "
                    "or outcomes not supported by "
                    "the input?"
                ),

            "classification_accuracy":
                (
                    "Are findings placed in the "
                    "correct categories such as "
                    "issue, risk, dependency, "
                    "requirement change, schedule "
                    "impact, action, or uncertainty?"
                ),

            "meaning_preservation":
                (
                    "Does the output preserve "
                    "relationships such as owner, "
                    "action, deadline, approval "
                    "status, dependency, and "
                    "conditional meaning?"
                ),
        },

        "semantic_score_formula":
            (
                "sum of five dimension scores "
                "/ 10 * 100"
            ),

        "total_cases":
            len(items),

        "cases":
            items,
    }


def save_json(
    review_pack: dict,
) -> None:
    JSON_OUTPUT.write_text(
        json.dumps(
            review_pack,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def save_csv(
    review_pack: dict,
) -> None:
    fields = [
        "test_case",
        "language",
        "difficulty",
        "primary_target",

        "input",

        "model_summary",
        "model_output_json",

        "expected_counts",
        "golden_assertions",
        "manual_review",

        "factual_correctness",
        "completeness",
        "unsupported_claim_control",
        "classification_accuracy",
        "meaning_preservation",

        "semantic_score",
        "review_notes",

        "latency_seconds",
        "total_tokens",
    ]

    with CSV_OUTPUT.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fields,
        )

        writer.writeheader()

        for item in review_pack[
            "cases"
        ]:
            model_output = item[
                "model_output"
            ]

            golden = item[
                "golden_expectations"
            ]

            metadata = item[
                "metadata"
            ]

            writer.writerow(
                {
                    "test_case":
                        item[
                            "test_case"
                        ],

                    "language":
                        item[
                            "language"
                        ],

                    "difficulty":
                        item[
                            "difficulty"
                        ],

                    "primary_target":
                        item[
                            "primary_target"
                        ],

                    "input":
                        item[
                            "input"
                        ],

                    "model_summary":
                        model_output.get(
                            "summary",
                            "",
                        ),

                    "model_output_json":
                        json.dumps(
                            model_output,
                            ensure_ascii=False,
                            indent=2,
                        ),

                    "expected_counts":
                        json.dumps(
                            golden[
                                "expected_counts"
                            ],
                            ensure_ascii=False,
                        ),

                    "golden_assertions":
                        json.dumps(
                            golden[
                                "assertions"
                            ],
                            ensure_ascii=False,
                            indent=2,
                        ),

                    "manual_review":
                        " | ".join(
                            golden[
                                "manual_review"
                            ]
                        ),

                    "factual_correctness":
                        "",

                    "completeness":
                        "",

                    "unsupported_claim_control":
                        "",

                    "classification_accuracy":
                        "",

                    "meaning_preservation":
                        "",

                    "semantic_score":
                        "",

                    "review_notes":
                        "",

                    "latency_seconds":
                        metadata.get(
                            "latency_seconds"
                        ),

                    "total_tokens":
                        metadata.get(
                            "total_tokens"
                        ),
                }
            )


def validate_review_pack(
    review_pack: dict,
) -> None:
    cases = review_pack[
        "cases"
    ]

    assert len(cases) == 30

    case_ids = [
        item["test_case"]
        for item in cases
    ]

    assert len(case_ids) == len(
        set(case_ids)
    )

    for item in cases:
        assert item["input"]
        assert item[
            "model_output"
        ]
        assert item[
            "golden_expectations"
        ]

        human_evaluation = item[
            "human_evaluation"
        ]

        for dimension in (
            HUMAN_DIMENSIONS
        ):
            assert (
                dimension
                in human_evaluation
            )


def main() -> None:
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    review_pack = (
        build_review_pack()
    )

    validate_review_pack(
        review_pack
    )

    save_json(
        review_pack
    )

    save_csv(
        review_pack
    )

    print(
        "\nHuman Review Pack Created"
    )
    print("=" * 60)

    print(
        f"Cases: {review_pack['total_cases']}"
    )

    print(
        f"JSON:  {JSON_OUTPUT}"
    )

    print(
        f"CSV:   {CSV_OUTPUT}"
    )

    print(
        "\nThe JSON pack is ready "
        "for semantic human review."
    )


if __name__ == "__main__":
    main()