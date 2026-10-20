import csv
import json
from pathlib import Path

from .holdout_cases_v1 import HOLDOUT_CASES
from .holdout_golden_v1 import GOLDEN_EXPECTATIONS


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
    / "human_review"
)

JSON_OUTPUT = (
    OUTPUT_DIR
    / "gemini_review_pack.json"
)

CSV_OUTPUT = (
    OUTPUT_DIR
    / "gemini_human_review_template.csv"
)


HUMAN_DIMENSIONS = [
    "factual_correctness",
    "completeness",
    "unsupported_claim_control",
    "classification_accuracy",
    "meaning_preservation",
]


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
            f"{test_id}: test_case mismatch."
        )

    if (
        output.get("comparison_version")
        != COMPARISON_VERSION
    ):
        raise RuntimeError(
            f"{test_id}: comparison version mismatch."
        )

    if (
        output.get("holdout_version")
        != HOLDOUT_VERSION
    ):
        raise RuntimeError(
            f"{test_id}: holdout version mismatch."
        )

    if (
        output.get("prompt_version")
        != PROMPT_VERSION
    ):
        raise RuntimeError(
            f"{test_id}: prompt version mismatch."
        )

    if (
        output.get("provider")
        != PROVIDER
    ):
        raise RuntimeError(
            f"{test_id}: provider mismatch."
        )

    if (
        output.get("model")
        != MODEL
    ):
        raise RuntimeError(
            f"{test_id}: model mismatch."
        )


def build_review_item(
    case: dict,
) -> dict:

    test_id = case["id"]

    output = load_result(
        test_id
    )

    validate_result(
        output,
        test_id,
    )

    golden = (
        GOLDEN_EXPECTATIONS[
            test_id
        ]
    )

    result = output[
        "result"
    ]

    metadata = output.get(
        "metadata",
        {},
    )

    return {
        "test_case":
            test_id,

        "language":
            case[
                "language"
            ],

        "scenario_type":
            case[
                "scenario_type"
            ],

        "primary_target":
            case[
                "primary_target"
            ],

        "input":
            case[
                "input"
            ],

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
            "comparison_version":
                output.get(
                    "comparison_version"
                ),

            "holdout_version":
                output.get(
                    "holdout_version"
                ),

            "prompt_version":
                output.get(
                    "prompt_version"
                ),

            "provider":
                output.get(
                    "provider"
                ),

            "model":
                output.get(
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
        build_review_item(
            case
        )
        for case
        in HOLDOUT_CASES
    ]

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
            "cross_model_human_semantic_review",

        "human_evaluation_scale": {
            "0":
                (
                    "Incorrect or substantially "
                    "fails the dimension."
                ),

            "1":
                (
                    "Partially correct, with "
                    "meaningful errors or omissions."
                ),

            "2":
                (
                    "Correct or substantially "
                    "correct for the dimension."
                ),
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


def validate_review_pack(
    review_pack: dict,
) -> None:

    cases = review_pack[
        "cases"
    ]

    if len(cases) != 20:
        raise RuntimeError(
            "Expected 20 review cases."
        )

    ids = [
        item[
            "test_case"
        ]
        for item in cases
    ]

    if len(ids) != len(
        set(ids)
    ):
        raise RuntimeError(
            "Duplicate test_case IDs found."
        )

    for item in cases:

        if not item["input"]:
            raise RuntimeError(
                f"{item['test_case']}: "
                "input is empty."
            )

        if not item["model_output"]:
            raise RuntimeError(
                f"{item['test_case']}: "
                "model output is empty."
            )

        if not item[
            "golden_expectations"
        ]:
            raise RuntimeError(
                f"{item['test_case']}: "
                "golden expectations missing."
            )

        evaluation = item[
            "human_evaluation"
        ]

        for dimension in (
            HUMAN_DIMENSIONS
        ):

            if (
                dimension
                not in evaluation
            ):
                raise RuntimeError(
                    f"{item['test_case']}: "
                    f"missing {dimension}."
                )


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
        "scenario_type",
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

                    "scenario_type":
                        item[
                            "scenario_type"
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
        "\nGemini Human Review Pack Created"
    )

    print("=" * 70)

    print(
        f"Cases: "
        f"{review_pack['total_cases']}"
    )

    print(
        f"JSON:  "
        f"{JSON_OUTPUT}"
    )

    print(
        f"CSV:   "
        f"{CSV_OUTPUT}"
    )

    print(
        "\nGemini outputs remain unchanged."
    )


if __name__ == "__main__":
    main()