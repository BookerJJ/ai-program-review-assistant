from .holdout_cases_v1 import HOLDOUT_CASES


CATEGORIES = [
    "issues",
    "risks",
    "dependencies",
    "requirement_changes",
    "schedule_impacts",
    "actions",
    "uncertainties",
]


TEST_INPUTS = {
    case["id"]: case["input"]
    for case in HOLDOUT_CASES
}


def counts(
    issues=0,
    risks=0,
    dependencies=0,
    requirement_changes=0,
    schedule_impacts=0,
    actions=0,
    uncertainties=0,
):
    return {
        "issues": issues,
        "risks": risks,
        "dependencies": dependencies,
        "requirement_changes": requirement_changes,
        "schedule_impacts": schedule_impacts,
        "actions": actions,
        "uncertainties": uncertainties,
    }


GOLDEN_EXPECTATIONS = {

    # =========================================================
    # 1. OPERATIONAL INCIDENT
    # =========================================================

    "H-001": {
        "expected_counts": counts(
            issues=1,
            actions=1,
            uncertainties=1,
        ),
        "assertions": [
            {
                "path": "actions.0.owner",
                "op": "equals",
                "value": "Platform Team",
            },
            {
                "path": "actions.0.due_date",
                "op": "contains",
                "value": "4 PM",
            },
        ],
        "manual_review": [
            "The 503 authentication/payment gateway failure is an existing issue.",
            "QA stopping the checkout validation cycle is the supported impact.",
            "4 PM applies to providing the status update, not necessarily completing the investigation.",
            "Do not create a release-delay risk or schedule impact.",
            "The release-date impact remains unresolved because it has not been reviewed yet.",
        ],
    },

    "H-002": {
        "expected_counts": counts(
            issues=1,
            actions=1,
        ),
        "assertions": [
            {
                "path": "actions.0.owner",
                "op": "contains",
                "value": "Art Tech Team",
            },
        ],
        "manual_review": [
            "Missing Mip Levels are the current issue.",
            "The Art Tech Team commitment to regenerate and deliver the assets is an action.",
            "The delivery deadline is tomorrow at noon.",
            "Do not create a schedule impact because no milestone impact has been identified.",
            "Do not invent a delivery-failure risk.",
        ],
    },

    "H-003": {
        "expected_counts": counts(),
        "assertions": [],
        "manual_review": [
            "This is a completed-success negative case.",
            "The export and QA spot check both completed successfully.",
            "Do not create an issue, risk, action, schedule impact, or uncertainty.",
        ],
    },

    "H-004": {
        "expected_counts": counts(
            issues=1,
            actions=1,
        ),
        "assertions": [
            {
                "path": "actions.0.owner",
                "op": "contains",
                "value": "Database Team",
            },
        ],
        "manual_review": [
            "The Read-Only Staging Database is an existing issue.",
            "Integration testing being blocked is the directly supported impact.",
            "The Database Team restoration / access confirmation is an explicit action.",
            "11 AM applies to confirming access availability, not necessarily the restoration completion time.",
            "Do not invent a release or milestone delay.",
        ],
    },

    # =========================================================
    # 2. REQUIREMENT CHANGE
    # =========================================================

    "H-005": {
        "expected_counts": counts(
            requirement_changes=1,
            actions=1,
            uncertainties=1,
        ),
        "assertions": [
            {
                "path": "requirement_changes.0.previous_state",
                "op": "contains",
                "value": "14",
            },
            {
                "path": "requirement_changes.0.new_state",
                "op": "contains",
                "value": "45",
            },
            {
                "path": "requirement_changes.0.change_status",
                "op": "equals",
                "value": "proposed",
            },
            {
                "path": "actions.0.owner",
                "op": "contains",
                "value": "Security Team",
            },
            {
                "path": "actions.0.due_date",
                "op": "contains",
                "value": "Tuesday",
            },
        ],
        "manual_review": [
            "The 45-day retention value is proposed, not approved.",
            "The Security Team Tuesday review is an explicit action.",
            "No implementation effort estimate exists.",
            "Do not invent a schedule impact or implementation risk.",
            "Final approval remains uncertain.",
        ],
    },

    "H-006": {
        "expected_counts": counts(
            requirement_changes=1,
            actions=1,
        ),
        "assertions": [
            {
                "path": "requirement_changes.0.previous_state",
                "op": "contains",
                "value": "5",
            },
            {
                "path": "requirement_changes.0.new_state",
                "op": "contains",
                "value": "3",
            },
            {
                "path": "requirement_changes.0.change_status",
                "op": "equals",
                "value": "confirmed",
            },
            {
                "path": "actions.0.owner",
                "op": "contains",
                "value": "Backend Team",
            },
            {
                "path": "actions.0.due_date",
                "op": "contains",
                "value": "Sprint",
            },
        ],
        "manual_review": [
            "The retry-limit change from 5 to 3 is confirmed.",
            "Applying the value from the next Sprint is an explicit Backend Team action.",
            "No schedule impact should be generated.",
        ],
    },

    "H-007": {
        "expected_counts": counts(
            dependencies=1,
            requirement_changes=1,
            uncertainties=1,
        ),
        "assertions": [
            {
                "path": "dependencies.0.basis",
                "op": "equals",
                "value": "explicit",
            },
            {
                "path": "requirement_changes.0.previous_state",
                "op": "contains",
                "value": "disabled",
            },
            {
                "path": "requirement_changes.0.new_state",
                "op": "contains",
                "value": "enabled",
            },
            {
                "path": "requirement_changes.0.change_status",
                "op": "equals",
                "value": "proposed",
            },
        ],
        "manual_review": [
            "Telemetry remains disabled by default.",
            "Enabling telemetry for Beta is proposed, not approved.",
            "Client consent explicitly gates Legal approval.",
            "The final decision remains unresolved.",
            "Do not invent a schedule impact.",
        ],
    },

    "H-008": {
        "expected_counts": counts(
            risks=1,
            requirement_changes=1,
            schedule_impacts=1,
            uncertainties=1,
        ),
        "assertions": [
            {
                "path": "risks.0.basis",
                "op": "equals",
                "value": "inferred",
            },
            {
                "path": "requirement_changes.0.previous_state",
                "op": "is_null",
            },
            {
                "path": "requirement_changes.0.change_status",
                "op": "equals",
                "value": "proposed",
            },
            {
                "path": "schedule_impacts.0.affected_milestone",
                "op": "is_null",
            },
            {
                "path": "schedule_impacts.0.impact_status",
                "op": "equals",
                "value": "potential",
            },
        ],
        "manual_review": [
            "High-Resolution Texture support is proposed, not approved.",
            "Approximately two additional work days are explicitly supported if approved.",
            "The additional effort supports an inferred risk / potential schedule impact.",
            "No release milestone should be invented.",
        ],
    },

    # =========================================================
    # 3. DEPENDENCY AND SCHEDULE
    # =========================================================

    "H-009": {
        "expected_counts": counts(
            risks=1,
            dependencies=1,
            schedule_impacts=1,
            actions=1,
            uncertainties=1,
        ),
        "assertions": [
            {
                "path": "risks.0.basis",
                "op": "equals",
                "value": "inferred",
            },
            {
                "path": "dependencies.0.basis",
                "op": "equals",
                "value": "explicit",
            },
            {
                "path": "schedule_impacts.0.affected_milestone",
                "op": "contains",
                "value": "Certification",
            },
            {
                "path": "schedule_impacts.0.duration_change",
                "op": "is_null",
            },
            {
                "path": "schedule_impacts.0.impact_status",
                "op": "equals",
                "value": "potential",
            },
            {
                "path": "actions.0.owner",
                "op": "contains",
                "value": "Security Team",
            },
            {
                "path": "actions.0.due_date",
                "op": "contains",
                "value": "Wednesday",
            },
        ],
        "manual_review": [
            "The signed firmware package explicitly gates Certification testing.",
            "The Wednesday package delivery followed by Thursday testing supports a future timing risk.",
            "Do not invent a specific delay duration.",
            "The Security Team package delivery is an explicit action.",
            "The revised test schedule remains unresolved.",
        ],
    },

    "H-010": {
        "expected_counts": counts(
            issues=1,
            risks=1,
            dependencies=1,
            schedule_impacts=1,
            uncertainties=1,
        ),
        "assertions": [
            {
                "path": "risks.0.basis",
                "op": "equals",
                "value": "inferred",
            },
            {
                "path": "dependencies.0.basis",
                "op": "equals",
                "value": "explicit",
            },
            {
                "path": "schedule_impacts.0.affected_milestone",
                "op": "contains",
                "value": "Build Validation",
            },
            {
                "path": "schedule_impacts.0.duration_change",
                "op": "is_null",
            },
            {
                "path": "schedule_impacts.0.impact_status",
                "op": "equals",
                "value": "potential",
            },
        ],
        "manual_review": [
            "The missing Whitelist is an existing issue.",
            "Whitelist activation explicitly gates Build Validation.",
            "The unknown Whitelist completion time creates a supported risk to Friday Build Validation.",
            "Do not invent a specific delay duration.",
            "The unresolved item is the Whitelist completion timing.",
        ],
    },

    "H-011": {
        "expected_counts": counts(
            dependencies=1,
            actions=1,
        ),
        "assertions": [
            {
                "path": "dependencies.0.basis",
                "op": "equals",
                "value": "explicit",
            },
            {
                "path": "actions.0.owner",
                "op": "contains",
                "value": "Localization Team",
            },
            {
                "path": "actions.0.due_date",
                "op": "contains",
                "value": "Monday",
            },
        ],
        "manual_review": [
            "Localization signoff explicitly gates store submission.",
            "The Monday signoff is an explicit Localization Team action.",
            "Do not create a risk solely because store submission is Wednesday.",
            "No schedule concern has been reported.",
        ],
    },

    "H-012": {
        "expected_counts": counts(
            dependencies=2,
            uncertainties=1,
        ),
        "assertions": [
            {
                "path": "dependencies.0.basis",
                "op": "equals",
                "value": "explicit",
            },
            {
                "path": "dependencies.1.basis",
                "op": "equals",
                "value": "explicit",
            },
        ],
        "manual_review": [
            "Security Review completion gates Privacy Approval.",
            "Privacy Approval gates Pilot Access activation.",
            "Both dependencies are explicit.",
            "The missing Security Review owner is the unresolved item.",
            "Do not invent a schedule delay.",
        ],
    },

    # =========================================================
    # 4. ACTION AND DEADLINE
    # =========================================================

    "H-013": {
        "expected_counts": counts(
            issues=1,
            actions=2,
            uncertainties=1,
        ),
        "assertions": [
            {
                "path": "actions.0.owner",
                "op": "contains",
                "value": "Support",
            },
            {
                "path": "actions.0.due_date",
                "op": "contains",
                "value": "Tuesday",
            },
            {
                "path": "actions.1.owner",
                "op": "contains",
                "value": "Engineering",
            },
            {
                "path": "actions.1.due_date",
                "op": "contains",
                "value": "Thursday",
            },
        ],
        "manual_review": [
            "The intermittent connection drop is the existing issue.",
            "Tuesday belongs to Support log collection.",
            "Thursday belongs to Engineering log review.",
            "Do not bind either date to remediation.",
            "The remediation date remains uncertain.",
        ],
    },

    "H-014": {
        "expected_counts": counts(
            issues=1,
            actions=2,
            uncertainties=1,
        ),
        "assertions": [
            {
                "path": "actions.0.owner",
                "op": "contains",
                "value": "고객",
            },
            {
                "path": "actions.1.owner",
                "op": "contains",
                "value": "QA",
            },
        ],
        "manual_review": [
            "The intermittent Mobile Client crash is an existing issue.",
            "The customer Device-list delivery and QA reproduction are separate actions.",
            "Monday belongs to the customer Device-list action.",
            "Wednesday belongs to QA crash reproduction.",
            "The fix completion date remains unresolved.",
        ],
    },

    "H-015": {
        "expected_counts": counts(
            actions=1,
        ),
        "assertions": [
            {
                "path": "actions.0.owner",
                "op": "contains",
                "value": "audio vendor",
            },
            {
                "path": "actions.0.due_date",
                "op": "contains",
                "value": "Friday",
            },
        ],
        "manual_review": [
            "The Friday final-mix delivery is an explicit action.",
            "The internal team can continue with the temporary mix.",
            "Do not invent a risk that the vendor may miss Friday.",
            "No schedule impact has been identified.",
        ],
    },

    "H-016": {
        "expected_counts": counts(
            actions=2,
            uncertainties=1,
        ),
        "assertions": [
            {
                "path": "actions.0.owner",
                "op": "contains",
                "value": "Analytics Team",
            },
            {
                "path": "actions.1.owner",
                "op": "contains",
                "value": "Product Team",
            },
        ],
        "manual_review": [
            "The Analytics Team cost estimate and Product Team review are two separate actions.",
            "Tuesday belongs to the cost-estimate action.",
            "Wednesday belongs to the Product Team review.",
            "Whether the feature will actually be added remains unresolved.",
            "Do not invent a requirement change approval or schedule impact.",
        ],
    },

    # =========================================================
    # 5. CONFLICT AND NEGATIVE
    # =========================================================

    "H-017": {
        "expected_counts": counts(
            risks=1,
            requirement_changes=1,
            uncertainties=1,
        ),
        "assertions": [
            {
                "path": "risks.0.basis",
                "op": "equals",
                "value": "inferred",
            },
            {
                "path": "requirement_changes.0.previous_state",
                "op": "contains",
                "value": "7",
            },
            {
                "path": "requirement_changes.0.new_state",
                "op": "contains",
                "value": "30",
            },
            {
                "path": "requirement_changes.0.change_status",
                "op": "equals",
                "value": "proposed",
            },
        ],
        "manual_review": [
            "Seven days remains the signed/current requirement.",
            "Thirty days is only a proposed value.",
            "The conflicting current and proposed values support an inferred consistency/readiness risk.",
            "Do not invent a schedule impact.",
            "The final retention requirement remains unresolved.",
        ],
    },

    "H-018": {
        "expected_counts": counts(
            risks=1,
            uncertainties=1,
        ),
        "assertions": [
            {
                "path": "risks.0.basis",
                "op": "equals",
                "value": "inferred",
            },
        ],
        "manual_review": [
            "October 10 remains the official Launch Date.",
            "October 12 is an Engineering Lead opinion, not an approved schedule change.",
            "Do not select October 12 as the final schedule.",
            "Do not create a confirmed schedule impact.",
            "The unresolved item is the final schedule-change decision.",
        ],
    },

    "H-019": {
        "expected_counts": counts(),
        "assertions": [],
        "manual_review": [
            "The rollout completed successfully.",
            "Monitoring remained normal and no incidents were reported.",
            "No follow-up work is required.",
            "Do not create any findings.",
        ],
    },

    "H-020": {
        "expected_counts": counts(),
        "assertions": [],
        "manual_review": [
            "This is a clean status-update negative case.",
            "No scope change, blocker, risk, or action exists.",
            "Do not create findings or uncertainties.",
        ],
    },
}


def validate_golden_expectations() -> None:
    holdout_ids = {
        case["id"]
        for case in HOLDOUT_CASES
    }

    golden_ids = set(
        GOLDEN_EXPECTATIONS.keys()
    )

    assert holdout_ids == golden_ids, (
        "Holdout cases and golden expectations "
        "do not contain the same case IDs."
    )

    assert len(
        GOLDEN_EXPECTATIONS
    ) == 20

    for test_id, expectation in (
        GOLDEN_EXPECTATIONS.items()
    ):
        expected_counts = expectation[
            "expected_counts"
        ]

        assert set(
            expected_counts.keys()
        ) == set(CATEGORIES), (
            f"{test_id}: invalid category set"
        )

        for category, value in (
            expected_counts.items()
        ):
            assert isinstance(value, int), (
                f"{test_id}: "
                f"{category} count must be int"
            )

            assert value >= 0, (
                f"{test_id}: "
                f"{category} count cannot be negative"
            )

        assert isinstance(
            expectation["assertions"],
            list,
        )

        assert isinstance(
            expectation["manual_review"],
            list,
        )


if __name__ == "__main__":
    validate_golden_expectations()
    print("Holdout golden expectations OK")