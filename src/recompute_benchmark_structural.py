import argparse
import json
from copy import deepcopy
from pathlib import Path


EVIDENCE_CATEGORY = "evidence"


def load_json(path: Path) -> dict:
    return json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )


def save_json(
    path: Path,
    data: dict,
) -> None:

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def mean(
    values: list[float],
) -> float | None:

    if not values:
        return None

    return round(
        sum(values) / len(values),
        1,
    )


def clean_structural_checks(
    checks: list[dict],
) -> list[dict]:

    return [
        check
        for check in checks
        if check.get("category")
        != EVIDENCE_CATEGORY
    ]


def recompute_case(
    case: dict,
) -> dict:

    corrected = deepcopy(
        case
    )

    checks = case.get(
        "checks",
        []
    )

    if not isinstance(
        checks,
        list,
    ):
        raise ValueError(
            f"{case.get('test_case')}: "
            "'checks' is not a list"
        )

    structural_checks = (
        clean_structural_checks(
            checks
        )
    )

    if not structural_checks:
        raise ValueError(
            f"{case.get('test_case')}: "
            "no structural checks found"
        )

    passed_checks = sum(
        1
        for check in structural_checks
        if check.get("passed")
        is True
    )

    total_checks = len(
        structural_checks
    )

    structural_score = round(
        (
            passed_checks
            / total_checks
        )
        * 100,
        1,
    )

    # Preserve the original contaminated values
    # for methodology/audit traceability.
    corrected[
        "legacy_structural_score"
    ] = case.get(
        "structural_score"
    )

    corrected[
        "legacy_passed_checks"
    ] = case.get(
        "passed_checks"
    )

    corrected[
        "legacy_total_checks"
    ] = case.get(
        "total_checks"
    )

    # Correct values.
    corrected[
        "structural_score"
    ] = structural_score

    corrected[
        "passed_checks"
    ] = passed_checks

    corrected[
        "total_checks"
    ] = total_checks

    # Keep an explicit list showing exactly
    # what contributes to Structural Score.
    corrected[
        "structural_checks"
    ] = structural_checks

    return corrected


def successful_cases(
    cases: list[dict],
) -> list[dict]:

    return [
        case
        for case in cases
        if case.get("status")
        == "success"
    ]


def structural_average(
    cases: list[dict],
) -> float | None:

    values = [
        case["structural_score"]
        for case in cases
        if case.get("status")
        == "success"
        and case.get(
            "structural_score"
        ) is not None
    ]

    return mean(
        values
    )


def update_group_summary(
    report: dict,
    corrected_cases: list[dict],
    report_key: str,
    case_key: str,
) -> None:

    groups = report.get(
        report_key
    )

    if not isinstance(
        groups,
        dict,
    ):
        return

    for group_name, group_data in (
        groups.items()
    ):

        matching_cases = [
            case
            for case
            in corrected_cases
            if case.get(
                case_key
            )
            == group_name
            and case.get(
                "status"
            )
            == "success"
        ]

        if not matching_cases:
            continue

        group_data[
            "average_structural_score"
        ] = structural_average(
            matching_cases
        )


def print_comparison(
    original: dict,
    corrected: dict,
) -> None:

    old_overall = (
        original
        .get("overall", {})
        .get(
            "average_structural_score"
        )
    )

    new_overall = (
        corrected
        .get("overall", {})
        .get(
            "average_structural_score"
        )
    )

    print(
        "\n"
        + "=" * 70
    )

    print(
        "STRUCTURAL SCORE "
        "METHODOLOGY CORRECTION"
    )

    print("=" * 70)

    print(
        f"Prompt version: "
        f"{corrected.get('prompt_version')}"
    )

    print(
        f"Old overall structural: "
        f"{old_overall}"
    )

    print(
        f"New overall structural: "
        f"{new_overall}"
    )

    print(
        "\nBy language"
    )

    for language, data in (
        corrected.get(
            "by_language",
            {}
        ).items()
    ):

        old_value = (
            original
            .get(
                "by_language",
                {}
            )
            .get(
                language,
                {}
            )
            .get(
                "average_structural_score"
            )
        )

        new_value = data.get(
            "average_structural_score"
        )

        print(
            f"  {language}: "
            f"{old_value} -> "
            f"{new_value}"
        )

    print(
        "\nBy difficulty"
    )

    for difficulty, data in (
        corrected.get(
            "by_difficulty",
            {}
        ).items()
    ):

        old_value = (
            original
            .get(
                "by_difficulty",
                {}
            )
            .get(
                difficulty,
                {}
            )
            .get(
                "average_structural_score"
            )
        )

        new_value = data.get(
            "average_structural_score"
        )

        print(
            f"  {difficulty}: "
            f"{old_value} -> "
            f"{new_value}"
        )


def recompute_report(
    report: dict,
) -> dict:

    corrected = deepcopy(
        report
    )

    cases = report.get(
        "cases"
    )

    if not isinstance(
        cases,
        list,
    ):
        raise ValueError(
            "Report does not contain "
            "a valid 'cases' list."
        )

    corrected_cases = [
        recompute_case(
            case
        )
        for case in cases
    ]

    corrected[
        "cases"
    ] = corrected_cases

    successful = (
        successful_cases(
            corrected_cases
        )
    )

    if "overall" not in corrected:
        corrected[
            "overall"
        ] = {}

    corrected[
        "overall"
    ][
        "average_structural_score"
    ] = structural_average(
        successful
    )

    update_group_summary(
        corrected,
        corrected_cases,
        report_key="by_language",
        case_key="language",
    )

    update_group_summary(
        corrected,
        corrected_cases,
        report_key="by_difficulty",
        case_key="difficulty",
    )

    corrected[
        "methodology_note"
    ] = (
        "Structural Score excludes "
        "Evidence Traceability. "
        "Evidence is reported as a "
        "separate metric. Historical "
        "Structural values in the "
        "source report included the "
        "evidence pass/fail check in "
        "the Structural denominator."
    )

    corrected[
        "structural_methodology"
    ] = {
        "evidence_in_structural":
            False,

        "structural_check_filter":
            (
                "check.category "
                "!= 'evidence'"
            ),

        "evidence_reported_separately":
            True,

        "model_inference_rerun":
            False,
    }

    return corrected


def main() -> None:

    parser = argparse.ArgumentParser(
        description=(
            "Recompute benchmark "
            "Structural Score while "
            "excluding Evidence "
            "Traceability."
        )
    )

    parser.add_argument(
        "input_report",
        type=Path,
        help=(
            "Existing objective "
            "benchmark report JSON."
        ),
    )

    parser.add_argument(
        "output_report",
        type=Path,
        nargs="?",
        help=(
            "Corrected report path. "
            "If omitted, writes beside "
            "the input report with "
            "'_structural_corrected'."
        ),
    )

    args = parser.parse_args()

    input_path = (
        args.input_report
    )

    if not input_path.exists():
        raise FileNotFoundError(
            f"Input report not found: "
            f"{input_path}"
        )

    if args.output_report:
        output_path = (
            args.output_report
        )
    else:
        output_path = (
            input_path.parent
            / (
                input_path.stem
                + "_structural_corrected"
                + input_path.suffix
            )
        )

    # Never overwrite the source report.
    if (
        output_path.resolve()
        == input_path.resolve()
    ):
        raise ValueError(
            "Output path must be "
            "different from input path."
        )

    original = load_json(
        input_path
    )

    corrected = (
        recompute_report(
            original
        )
    )

    save_json(
        output_path,
        corrected,
    )

    print_comparison(
        original,
        corrected,
    )

    print(
        "\nSaved corrected report:"
    )

    print(
        output_path
    )


if __name__ == "__main__":
    main()