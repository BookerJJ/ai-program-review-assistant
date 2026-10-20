import csv
import json
from pathlib import Path


EVALUATION_DIR = Path("results") / "evaluation"

HUMAN_EVALUATION_FILE = (
    EVALUATION_DIR / "human_evaluation.csv"
)

STRUCTURAL_EVALUATION_FILE = (
    EVALUATION_DIR / "comparison.csv"
)

COMBINED_OUTPUT_FILE = (
    EVALUATION_DIR / "combined_evaluation.csv"
)

SUMMARY_OUTPUT_FILE = (
    EVALUATION_DIR / "human_evaluation_summary.json"
)


SCORE_FIELDS = [
    "factual_correctness",
    "completeness",
    "unsupported_claim_control",
    "classification_accuracy",
    "meaning_preservation",
]


def load_human_evaluations() -> list[dict]:
    """
    Load manually reviewed semantic evaluation scores.
    """

    rows = []

    with HUMAN_EVALUATION_FILE.open(
        "r",
        encoding="utf-8-sig",
    ) as file:
        reader = csv.DictReader(file)

        for row in reader:
            scores = {}

            for field in SCORE_FIELDS:
                raw_value = row[field].strip()

                if raw_value == "":
                    raise ValueError(
                        f"Missing human score: "
                        f"{row['prompt_version']} "
                        f"{row['test_case']} "
                        f"{field}"
                    )

                score = int(raw_value)

                if score not in (0, 1, 2):
                    raise ValueError(
                        f"Score must be 0, 1, or 2: "
                        f"{row['prompt_version']} "
                        f"{row['test_case']} "
                        f"{field}={score}"
                    )

                scores[field] = score

            total_score = sum(scores.values())

            max_score = (
                len(SCORE_FIELDS) * 2
            )

            semantic_score = (
                total_score
                / max_score
                * 100
            )

            rows.append(
                {
                    "prompt_version":
                        row["prompt_version"],
                    "test_case":
                        row["test_case"],
                    **scores,
                    "semantic_score":
                        round(semantic_score, 1),
                    "review_notes":
                        row["review_notes"],
                }
            )

    return rows


def load_structural_evaluations() -> dict:
    """
    Load the previously generated objective evaluation.
    """

    rows = {}

    with STRUCTURAL_EVALUATION_FILE.open(
        "r",
        encoding="utf-8-sig",
    ) as file:
        reader = csv.DictReader(file)

        for row in reader:
            key = (
                row["prompt_version"],
                row["test_case"],
            )

            rows[key] = row

    return rows


def build_combined_results(
    human_rows: list[dict],
    structural_rows: dict,
) -> list[dict]:
    combined = []

    for human in human_rows:
        key = (
            human["prompt_version"],
            human["test_case"],
        )

        structural = structural_rows.get(key)

        if structural is None:
            raise ValueError(
                f"No structural evaluation found for "
                f"{key}"
            )

        combined.append(
            {
                "prompt_version":
                    human["prompt_version"],
                "test_case":
                    human["test_case"],

                "structural_score":
                    float(
                        structural[
                            "structural_score"
                        ]
                    ),

                "semantic_score":
                    human["semantic_score"],

                "factual_correctness":
                    human[
                        "factual_correctness"
                    ],

                "completeness":
                    human["completeness"],

                "unsupported_claim_control":
                    human[
                        "unsupported_claim_control"
                    ],

                "classification_accuracy":
                    human[
                        "classification_accuracy"
                    ],

                "meaning_preservation":
                    human[
                        "meaning_preservation"
                    ],

                "evidence_traceability_rate":
                    float(
                        structural[
                            "evidence_traceability_rate"
                        ]
                    ),

                "latency_seconds":
                    float(
                        structural[
                            "latency_seconds"
                        ]
                    ),

                "input_tokens":
                    int(
                        structural[
                            "input_tokens"
                        ]
                    ),

                "output_tokens":
                    int(
                        structural[
                            "output_tokens"
                        ]
                    ),

                "total_tokens":
                    int(
                        structural[
                            "total_tokens"
                        ]
                    ),

                "review_notes":
                    human["review_notes"],
            }
        )

    return combined


def save_combined_csv(
    combined: list[dict],
) -> None:
    fields = [
        "prompt_version",
        "test_case",
        "structural_score",
        "semantic_score",
        "factual_correctness",
        "completeness",
        "unsupported_claim_control",
        "classification_accuracy",
        "meaning_preservation",
        "evidence_traceability_rate",
        "latency_seconds",
        "input_tokens",
        "output_tokens",
        "total_tokens",
        "review_notes",
    ]

    with COMBINED_OUTPUT_FILE.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fields,
        )

        writer.writeheader()

        writer.writerows(combined)


def build_summary(
    combined: list[dict],
) -> dict:
    versions = {}

    for row in combined:
        version = row["prompt_version"]

        if version not in versions:
            versions[version] = []

        versions[version].append(row)

    summary = {}

    for version, rows in versions.items():
        case_count = len(rows)

        summary[version] = {
            "cases": case_count,

            "average_structural_score":
                round(
                    sum(
                        row["structural_score"]
                        for row in rows
                    )
                    / case_count,
                    1,
                ),

            "average_semantic_score":
                round(
                    sum(
                        row["semantic_score"]
                        for row in rows
                    )
                    / case_count,
                    1,
                ),

            "average_evidence_traceability":
                round(
                    sum(
                        row[
                            "evidence_traceability_rate"
                        ]
                        for row in rows
                    )
                    / case_count,
                    3,
                ),

            "average_latency_seconds":
                round(
                    sum(
                        row["latency_seconds"]
                        for row in rows
                    )
                    / case_count,
                    3,
                ),

            "total_tokens":
                sum(
                    row["total_tokens"]
                    for row in rows
                ),

            "dimension_averages": {
                field: round(
                    sum(
                        row[field]
                        for row in rows
                    )
                    / case_count,
                    2,
                )
                for field in SCORE_FIELDS
            },
        }

    return summary


def main() -> None:
    print(
        "\nLoading human semantic evaluations..."
    )

    human_rows = load_human_evaluations()

    print(
        f"Loaded {len(human_rows)} human reviews."
    )

    structural_rows = (
        load_structural_evaluations()
    )

    combined = build_combined_results(
        human_rows,
        structural_rows,
    )

    save_combined_csv(combined)

    summary = build_summary(combined)

    SUMMARY_OUTPUT_FILE.write_text(
        json.dumps(
            summary,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print("\nEvaluation Summary")
    print("=" * 60)

    for version, metrics in summary.items():
        print(f"\n{version}")
        print(
            f"Structural Score: "
            f"{metrics['average_structural_score']}"
        )
        print(
            f"Semantic Score:   "
            f"{metrics['average_semantic_score']}"
        )
        print(
            f"Evidence Trace:   "
            f"{metrics['average_evidence_traceability']}"
        )
        print(
            f"Avg Latency:      "
            f"{metrics['average_latency_seconds']} sec"
        )
        print(
            f"Total Tokens:     "
            f"{metrics['total_tokens']}"
        )

    print("\nFiles created:")
    print(COMBINED_OUTPUT_FILE)
    print(SUMMARY_OUTPUT_FILE)


if __name__ == "__main__":
    main()