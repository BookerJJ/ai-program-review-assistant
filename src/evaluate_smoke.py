import csv
import json
import re
from pathlib import Path
from typing import Any

from .golden_answers import (
    GOLDEN_EXPECTATIONS,
    TEST_INPUTS,
)


VERSIONS = {
    "grounded-v0.2": Path("results") / "smoke_v02",
    "grounded-v0.3": Path("results") / "smoke_v03",
    "grounded-v0.4": Path("results") / "smoke_v04",
    "fewshot-v0.5": Path("results") / "smoke_v05",
}

OUTPUT_DIR = Path("results") / "evaluation"

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
    """
    Normalize whitespace and case for comparison.
    """

    value = re.sub(r"\s+", " ", value)
    return value.strip().casefold()


def get_path(data: Any, path: str) -> Any:
    """
    Read a nested value using paths such as:

    actions.0.owner
    schedule_impacts.0.duration_change
    """

    current = data

    try:
        for part in path.split("."):
            if isinstance(current, list):
                current = current[int(part)]
            else:
                current = current[part]

        return current

    except (KeyError, IndexError, TypeError, ValueError):
        return MISSING


def add_check(
    checks: list[dict],
    name: str,
    passed: bool,
    expected: Any,
    actual: Any,
) -> None:
    checks.append(
        {
            "name": name,
            "passed": passed,
            "expected": expected,
            "actual": (
                "<missing>"
                if actual is MISSING
                else actual
            ),
        }
    )


def evaluate_assertion(
    result: dict,
    assertion: dict,
) -> dict:
    path = assertion["path"]
    operation = assertion["op"]

    actual = get_path(result, path)

    if operation == "is_null":
        passed = actual is None
        expected = None

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

        if not isinstance(actual, str):
            passed = False

        else:
            passed = (
                normalize_text(expected)
                in normalize_text(actual)
            )

    else:
        raise ValueError(
            f"Unsupported assertion operation: {operation}"
        )

    return {
        "name": f"{path} [{operation}]",
        "passed": passed,
        "expected": expected,
        "actual": (
            "<missing>"
            if actual is MISSING
            else actual
        ),
    }


def evaluate_evidence_traceability(
    result: dict,
    source_text: str,
) -> dict:
    """
    Check whether evidence strings can be found directly
    in the original input.

    This does NOT evaluate whether the evidence logically
    proves the finding. It only checks traceability.
    """

    normalized_source = normalize_text(source_text)

    total_evidence = 0
    traceable_evidence = 0
    failures = []

    for category in EVIDENCE_CATEGORIES:
        for index, item in enumerate(
            result.get(category, [])
        ):
            evidence_items = item.get("evidence", [])

            for evidence in evidence_items:
                total_evidence += 1

                is_traceable = (
                    normalize_text(evidence)
                    in normalized_source
                )

                if is_traceable:
                    traceable_evidence += 1
                else:
                    failures.append(
                        {
                            "category": category,
                            "item_index": index,
                            "evidence": evidence,
                        }
                    )

    if total_evidence == 0:
        rate = 1.0
    else:
        rate = (
            traceable_evidence
            / total_evidence
        )

    return {
        "total_evidence": total_evidence,
        "traceable_evidence": traceable_evidence,
        "traceability_rate": round(rate, 3),
        "failures": failures,
    }


def evaluate_case(
    output: dict,
    test_id: str,
) -> dict:
    expectation = GOLDEN_EXPECTATIONS[test_id]
    source_text = TEST_INPUTS[test_id]

    checks = []

    result = output.get("result", {})

    # --------------------------------------------------
    # Basic format checks
    # --------------------------------------------------

    actual_keys = set(result.keys())

    add_check(
        checks,
        "top_level_keys",
        actual_keys == EXPECTED_RESULT_KEYS,
        sorted(EXPECTED_RESULT_KEYS),
        sorted(actual_keys),
    )

    add_check(
        checks,
        "summary_present",
        (
            isinstance(result.get("summary"), str)
            and bool(result["summary"].strip())
        ),
        "non-empty string",
        result.get("summary"),
    )

    # --------------------------------------------------
    # Category count checks
    # --------------------------------------------------

    for category, expected_count in (
        expectation["expected_counts"].items()
    ):
        actual_value = result.get(category)

        if isinstance(actual_value, list):
            actual_count = len(actual_value)
        else:
            actual_count = MISSING

        add_check(
            checks,
            f"{category}_count",
            actual_count == expected_count,
            expected_count,
            actual_count,
        )

    # --------------------------------------------------
    # Specific objective assertions
    # --------------------------------------------------

    for assertion in expectation["assertions"]:
        checks.append(
            evaluate_assertion(
                result,
                assertion,
            )
        )

    # --------------------------------------------------
    # Evidence traceability
    # --------------------------------------------------

    evidence = evaluate_evidence_traceability(
        result,
        source_text,
    )

    add_check(
        checks,
        "all_evidence_traceable",
        evidence["traceability_rate"] == 1.0,
        1.0,
        evidence["traceability_rate"],
    )

    # --------------------------------------------------
    # Structural score
    #
    # Evidence traceability is evaluated separately and
    # is not included in Structural Score.
    # --------------------------------------------------

    structural_checks = [
        check
        for check in checks
        if check["name"]
        != "all_evidence_traceable"
    ]

    passed_checks = sum(
        1
        for check in structural_checks
        if check["passed"]
    )

    total_checks = len(
        structural_checks
    )

    if total_checks:
        structural_score = (
            passed_checks
            / total_checks
            * 100
        )
    else:
        structural_score = 0.0

    metadata = output.get("metadata", {})

    return {
        "test_case": test_id,
        "prompt_version": output.get(
            "prompt_version"
        ),
        "status": output.get("status"),
        "structural_score": round(
            structural_score,
            1,
        ),
        "passed_checks": passed_checks,
        "total_checks": total_checks,
        "evidence_traceability": evidence,
        "latency_seconds": metadata.get(
            "latency_seconds"
        ),
        "input_tokens": metadata.get(
            "input_tokens"
        ),
        "output_tokens": metadata.get(
            "output_tokens"
        ),
        "total_tokens": metadata.get(
            "total_tokens"
        ),
        "checks": checks,
        "manual_review": expectation[
            "manual_review"
        ],
    }


def load_version_results(
    version: str,
    directory: Path,
) -> list[dict]:
    evaluations = []

    for test_id in GOLDEN_EXPECTATIONS:
        filename = (
            test_id.lower().replace("-", "")
            + ".json"
        )

        result_path = directory / filename

        if not result_path.exists():
            print(
                f"Missing result: {result_path}"
            )
            continue

        output = json.loads(
            result_path.read_text(
                encoding="utf-8"
            )
        )

        if (
            output.get("status")
            != "success"
        ):
            raise RuntimeError(
                f"{version} {test_id} did not "
                "complete successfully. "
                "Execution failures must not be "
                "scored as model-quality failures."
            )

        if (
            output.get("prompt_version")
            != version
        ):
            raise RuntimeError(
                f"{test_id}: expected prompt "
                f"{version}, got "
                f"{output.get('prompt_version')}."
            )

        evaluation = evaluate_case(
            output,
            test_id,
        )

        evaluations.append(evaluation)

    return evaluations


def build_version_summary(
    version: str,
    evaluations: list[dict],
) -> dict:
    if not evaluations:
        return {
            "prompt_version": version,
            "cases": 0,
        }

    average_score = sum(
        item["structural_score"]
        for item in evaluations
    ) / len(evaluations)

    latencies = [
        item["latency_seconds"]
        for item in evaluations
        if item["latency_seconds"] is not None
    ]

    total_tokens = sum(
        item["total_tokens"] or 0
        for item in evaluations
    )

    average_latency = (
        sum(latencies) / len(latencies)
        if latencies
        else None
    )

    return {
        "prompt_version": version,
        "cases": len(evaluations),
        "average_structural_score": round(
            average_score,
            1,
        ),
        "average_latency_seconds": (
            round(average_latency, 3)
            if average_latency is not None
            else None
        ),
        "total_tokens": total_tokens,
    }


def save_csv(
    all_evaluations: list[dict],
) -> Path:
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    csv_path = (
        OUTPUT_DIR
        / "comparison.csv"
    )

    fields = [
        "prompt_version",
        "test_case",
        "structural_score",
        "passed_checks",
        "total_checks",
        "evidence_traceability_rate",
        "latency_seconds",
        "input_tokens",
        "output_tokens",
        "total_tokens",
    ]

    with csv_path.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fields,
        )

        writer.writeheader()

        for item in all_evaluations:
            writer.writerow(
                {
                    "prompt_version":
                        item["prompt_version"],
                    "test_case":
                        item["test_case"],
                    "structural_score":
                        item["structural_score"],
                    "passed_checks":
                        item["passed_checks"],
                    "total_checks":
                        item["total_checks"],
                    "evidence_traceability_rate":
                        item[
                            "evidence_traceability"
                        ][
                            "traceability_rate"
                        ],
                    "latency_seconds":
                        item["latency_seconds"],
                    "input_tokens":
                        item["input_tokens"],
                    "output_tokens":
                        item["output_tokens"],
                    "total_tokens":
                        item["total_tokens"],
                }
            )

    return csv_path


def main() -> None:
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    report = {
        "evaluation_type":
            "objective_structural_evaluation",
        "note": (
            "Structural Score excludes Evidence "
            "Traceability. Evidence is reported "
            "separately. Structural Score does not "
            "measure full semantic accuracy, so manual "
            "review is still required."
        ),
        "versions": {},
    }

    all_evaluations = []

    for version, directory in VERSIONS.items():
        print(
            f"\nEvaluating {version}..."
        )

        evaluations = load_version_results(
            version,
            directory,
        )

        summary = build_version_summary(
            version,
            evaluations,
        )

        report["versions"][version] = {
            "summary": summary,
            "cases": evaluations,
        }

        all_evaluations.extend(
            evaluations
        )

        print(
            f"Average structural score: "
            f"{summary.get('average_structural_score')}%"
        )

        print(
            f"Average latency: "
            f"{summary.get('average_latency_seconds')} sec"
        )

        print(
            f"Total tokens: "
            f"{summary.get('total_tokens')}"
        )

    report_path = (
        OUTPUT_DIR
        / "evaluation_report.json"
    )

    report_path.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    csv_path = save_csv(
        all_evaluations
    )

    print("\nEvaluation complete.")
    print(
        f"JSON report: {report_path}"
    )
    print(
        f"CSV comparison: {csv_path}"
    )


if __name__ == "__main__":
    main()