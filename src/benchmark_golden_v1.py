from .benchmark_cases_v1 import BENCHMARK_CASES


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
    for case in BENCHMARK_CASES
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
    # SIMPLE
    # =========================================================

    "TC-001": {
        "expected_counts": counts(
            issues=1,
            actions=1,
            uncertainties=1,
        ),
        "assertions": [
            {
                "path": "actions.0.owner",
                "op": "equals",
                "value": "Backend Engineering",
            },
            {
                "path": "actions.0.due_date",
                "op": "equals",
                "value": "Wednesday",
            },
        ],
        "manual_review": [
            "Wednesday applies to providing the update, not completing the investigation.",
            "Do not create a release-delay risk.",
            "No schedule impact should be created.",
        ],
    },

    "TC-006": {
        "expected_counts": counts(
            issues=1,
            actions=1,
        ),
        "assertions": [
            {
                "path": "actions.0.owner",
                "op": "equals",
                "value": "DevOps",
            },
            {
                "path": "actions.0.due_date",
                "op": "contains",
                "value": "3 PM",
            },
        ],
        "manual_review": [
            "The failed nightly build is the issue.",
            "The missing configuration file is explicitly identified as the cause.",
            "No release schedule impact should be invented.",
        ],
    },

    "TC-007": {
        "expected_counts": counts(
            issues=1,
            actions=1,
            uncertainties=1,
        ),
        "assertions": [
            {
                "path": "actions.0.owner",
                "op": "contains",
                "value": "Localization Vendor",
            },
            {
                "path": "actions.0.due_date",
                "op": "equals",
                "value": "금요일",
            },
        ],
        "manual_review": [
            "The missing localization strings are an existing issue.",
            "Friday is the corrected-file delivery date.",
            "Do not convert 'release schedule change has not been discussed' into a delay risk.",
            "Korean input should normally produce Korean analysis.",
        ],
    },

    "TC-008": {
        "expected_counts": counts(),
        "assertions": [],
        "manual_review": [
            "This is a negative case.",
            "Do not invent issues, risks, requirement changes, schedule impacts, actions, or uncertainties.",
        ],
    },

    "TC-009": {
        "expected_counts": counts(
            issues=1,
            actions=1,
        ),
        "assertions": [
            {
                "path": "actions.0.owner",
                "op": "contains",
                "value": "Infrastructure",
            },
            {
                "path": "actions.0.due_date",
                "op": "contains",
                "value": "오늘 오후",
            },
        ],
        "manual_review": [
            "Expired SSL certificate is an existing issue.",
            "QA access failure is the directly supported impact.",
            "Do not invent a release delay.",
        ],
    },

    "TC-010": {
        "expected_counts": counts(),
        "assertions": [],
        "manual_review": [
            "The backup completed successfully.",
            "Verification was also completed successfully.",
            "No follow-up action should be created.",
        ],
    },

    "TC-011": {
        "expected_counts": counts(
            actions=1,
        ),
        "assertions": [
            {
                "path": "actions.0.owner",
                "op": "contains",
                "value": "UI Team",
            },
            {
                "path": "actions.0.due_date",
                "op": "equals",
                "value": "금요일",
            },
        ],
        "manual_review": [
            "The planned Friday asset delivery is an action, not a risk.",
            "Development is continuing with existing assets.",
            "No schedule impact is supported.",
        ],
    },

    "TC-012": {
        "expected_counts": counts(
            issues=1,
            actions=1,
        ),
        "assertions": [
            {
                "path": "actions.0.owner",
                "op": "contains",
                "value": "Infrastructure",
            },
            {
                "path": "actions.0.due_date",
                "op": "contains",
                "value": "2 PM",
            },
        ],
        "manual_review": [
            "Staging unavailability is the issue.",
            "QA regression testing was paused as the direct impact.",
            "2 PM applies to confirming service availability.",
        ],
    },

    "TC-013": {
        "expected_counts": counts(
            issues=1,
            actions=1,
        ),
        "assertions": [
            {
                "path": "actions.0.owner",
                "op": "contains",
                "value": "UI Engineering",
            },
            {
                "path": "actions.0.due_date",
                "op": "equals",
                "value": "수요일",
            },
        ],
        "manual_review": [
            "Missing Screen Reader Labels are the existing issue.",
            "The action is to add the labels and provide the correction to QA.",
        ],
    },

    "TC-014": {
        "expected_counts": counts(
            requirement_changes=1,
        ),
        "assertions": [
            {
                "path": "requirement_changes.0.previous_state",
                "op": "contains",
                "value": "20",
            },
            {
                "path": "requirement_changes.0.new_state",
                "op": "contains",
                "value": "30",
            },
            {
                "path": "requirement_changes.0.change_status",
                "op": "equals",
                "value": "confirmed",
            },
        ],
        "manual_review": [
            "The timeout change is confirmed, not proposed.",
            "No schedule impact should be created.",
        ],
    },

    # =========================================================
    # MEDIUM
    # =========================================================

    "TC-002": {
        "expected_counts": counts(
            issues=1,
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
                "value": "System Test",
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
                "op": "equals",
                "value": "고객",
            },
            {
                "path": "actions.0.due_date",
                "op": "equals",
                "value": "목요일",
            },
        ],
        "manual_review": [
            "Do not invent a risk that the customer may miss Thursday merely because Thursday is a plan.",
            "The supported risk concerns the upcoming System Test.",
            "The explicit customer delivery commitment should be extracted as the action.",
        ],
    },

    "TC-003": {
        "expected_counts": counts(
            risks=1,
            requirement_changes=1,
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
                "path": "requirement_changes.0.previous_state",
                "op": "contains",
                "value": "90",
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
            {
                "path": "schedule_impacts.0.affected_milestone",
                "op": "is_null",
            },
            {
                "path": "schedule_impacts.0.duration_change",
                "op": "contains",
                "value": "two additional engineering days",
            },
            {
                "path": "schedule_impacts.0.impact_status",
                "op": "equals",
                "value": "potential",
            },
            {
                "path": "actions.0.owner",
                "op": "equals",
                "value": "Architecture Team",
            },
            {
                "path": "actions.0.due_date",
                "op": "equals",
                "value": "Friday",
            },
        ],
        "manual_review": [
            "The 30-day requirement is proposed, not confirmed.",
            "Approximately two engineering days are explicitly supported.",
            "Do not invent a release milestone.",
        ],
    },

    "TC-015": {
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
                "value": "Production deployment",
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
                "value": "Tuesday",
            },
        ],
        "manual_review": [
            "Security scan completion explicitly gates production deployment.",
            "Tuesday scan completion and Wednesday deployment create a supported future timing risk.",
            "Do not invent a specific delay duration.",
        ],
    },

    "TC-016": {
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
            {
                "path": "schedule_impacts.0.affected_milestone",
                "op": "is_null",
            },
            {
                "path": "schedule_impacts.0.duration_change",
                "op": "contains",
                "value": "하루",
            },
            {
                "path": "schedule_impacts.0.impact_status",
                "op": "equals",
                "value": "potential",
            },
        ],
        "manual_review": [
            "The 30-day retention period remains unapproved.",
            "Approximately one additional day is explicitly supported.",
        ],
    },

    "TC-017": {
        "expected_counts": counts(
            issues=1,
            risks=1,
            dependencies=1,
            schedule_impacts=1,
            uncertainties=2,
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
                "value": "Integration testing",
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
            "Missing test data is the current issue.",
            "Complete dataset is an explicit prerequisite for Integration testing.",
            "Friday Integration testing is the supported future risk.",
            "Do not invent a dataset completion date.",
        ],
    },

    "TC-018": {
        "expected_counts": counts(
            issues=1,
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
                "value": "Vendor",
            },
            {
                "path": "actions.0.due_date",
                "op": "contains",
                "value": "목요일 오전",
            },
        ],
        "manual_review": [
            "The Tuesday vendor delivery has already been missed and is an issue.",
            "Final Integration depends on the Character Animation file.",
            "Do not invent a release delay when no release milestone is supplied.",
        ],
    },

    "TC-019": {
        "expected_counts": counts(
            issues=1,
            actions=2,
            uncertainties=1,
        ),
        "assertions": [
            {
                "path": "actions.0.owner",
                "op": "contains",
                "value": "Engineering",
            },
            {
                "path": "actions.0.due_date",
                "op": "contains",
                "value": "Tuesday",
            },
            {
                "path": "actions.1.owner",
                "op": "contains",
                "value": "QA",
            },
            {
                "path": "actions.1.due_date",
                "op": "contains",
                "value": "Wednesday",
            },
        ],
        "manual_review": [
            "Tuesday belongs to the initial analysis.",
            "Wednesday belongs to the QA reproduction package.",
            "No fix date should be invented.",
        ],
    },

    "TC-020": {
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
                "value": "100MB",
            },
            {
                "path": "requirement_changes.0.new_state",
                "op": "contains",
                "value": "200MB",
            },
            {
                "path": "requirement_changes.0.change_status",
                "op": "equals",
                "value": "proposed",
            },
        ],
        "manual_review": [
            "The current approved value remains 100MB.",
            "200MB is proposed but not formally approved.",
            "Do not invent a schedule impact.",
        ],
    },

    "TC-021": {
        "expected_counts": counts(
            issues=1,
            actions=1,
            uncertainties=2,
        ),
        "assertions": [
            {
                "path": "issues.0.impact",
                "op": "is_null",
            },
            {
                "path": "actions.0.owner",
                "op": "is_null",
            },
            {
                "path": "actions.0.due_date",
                "op": "is_null",
            },
        ],
        "manual_review": [
            "High CPU utilization is an existing finding.",
            "No owner or completion date has been assigned for profiling.",
            "Do not create a release delay.",
        ],
    },

    "TC-022": {
        "expected_counts": counts(
            requirement_changes=1,
            actions=1,
        ),
        "assertions": [
            {
                "path": "requirement_changes.0.previous_state",
                "op": "contains",
                "value": "30",
            },
            {
                "path": "requirement_changes.0.new_state",
                "op": "contains",
                "value": "60",
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
                "value": "다음 Build",
            },
        ],
        "manual_review": [
            "The timeout change is approved.",
            "No additional schedule impact should be generated.",
        ],
    },

    # =========================================================
    # DIFFICULT
    # =========================================================

    "TC-004": {
        "expected_counts": counts(
            issues=1,
            dependencies=1,
            actions=1,
            uncertainties=2,
        ),
        "assertions": [
            {
                "path": "issues.0.impact",
                "op": "is_null",
            },
            {
                "path": "dependencies.0.basis",
                "op": "equals",
                "value": "explicit",
            },
            {
                "path": "actions.0.owner",
                "op": "is_null",
            },
            {
                "path": "actions.0.due_date",
                "op": "is_null",
            },
        ],
        "manual_review": [
            "Memory Profiling is required before the next Performance Review.",
            "No release delay should be invented.",
            "Missing profiling date is not itself a schedule impact.",
        ],
    },

    "TC-005": {
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
                "path": "risks.0.impact",
                "op": "is_null",
            },
            {
                "path": "requirement_changes.0.previous_state",
                "op": "contains",
                "value": "95%",
            },
            {
                "path": "requirement_changes.0.new_state",
                "op": "contains",
                "value": "90%",
            },
            {
                "path": "requirement_changes.0.change_status",
                "op": "equals",
                "value": "proposed",
            },
        ],
        "manual_review": [
            "90% is proposed, not approved.",
            "95% remains the current criterion.",
            "Do not invent pilot rejection or delay.",
        ],
    },

    "TC-023": {
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
            "Thursday remains the official plan.",
            "Friday is a statement from the Backend Lead, not an approved schedule change.",
            "Do not select either date as the final agreed delivery date.",
            "No confirmed schedule impact exists.",
        ],
    },

    "TC-024": {
        "expected_counts": counts(
            issues=1,
            dependencies=1,
            actions=2,
            uncertainties=2,
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
                "value": "Engineering",
            },
            {
                "path": "actions.0.due_date",
                "op": "contains",
                "value": "화요일",
            },
            {
                "path": "actions.1.owner",
                "op": "contains",
                "value": "QA",
            },
            {
                "path": "actions.1.due_date",
                "op": "is_null",
            },
        ],
        "manual_review": [
            "Tuesday applies to sharing investigation results.",
            "It is not the crash-fix deadline.",
            "QA retesting depends on the fix becoming available.",
        ],
    },

    "TC-025": {
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
                "path": "schedule_impacts.0.duration_change",
                "op": "contains",
                "value": "three additional development days",
            },
            {
                "path": "schedule_impacts.0.impact_status",
                "op": "equals",
                "value": "potential",
            },
        ],
        "manual_review": [
            "Audit logging is proposed, not confirmed.",
            "Approximately three additional development days are explicitly supported.",
            "No release milestone should be invented.",
        ],
    },

    "TC-026": {
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
            "Security Review completion gates Production Access approval.",
            "Production Access approval gates Deployment Validation.",
            "Do not invent a release delay.",
            "The missing Security Review owner should remain unresolved.",
        ],
    },

    "TC-027": {
        "expected_counts": counts(
            issues=1,
            actions=1,
            uncertainties=1,
        ),
        "assertions": [
            {
                "path": "issues.0.impact",
                "op": "is_null",
            },
            {
                "path": "actions.0.owner",
                "op": "contains",
                "value": "Engineering",
            },
            {
                "path": "actions.0.due_date",
                "op": "is_null",
            },
        ],
        "manual_review": [
            "The 12% response-time regression is the existing issue.",
            "The Release Manager explicitly ruled out a release-date impact.",
            "Do not create a release-delay risk.",
            "Remediation deadline remains unknown.",
        ],
    },

    "TC-028": {
        "expected_counts": counts(
            requirement_changes=1,
            uncertainties=1,
        ),
        "assertions": [
            {
                "path": "requirement_changes.0.previous_state",
                "op": "contains",
                "value": "Export",
            },
            {
                "path": "requirement_changes.0.new_state",
                "op": "contains",
                "value": "Export",
            },
            {
                "path": "requirement_changes.0.change_status",
                "op": "equals",
                "value": "proposed",
            },
        ],
        "manual_review": [
            "The existing scope still includes Export.",
            "Removing Export from the Pilot is only proposed.",
            "Do not treat the proposed removal as confirmed.",
        ],
    },

    "TC-029": {
        "expected_counts": counts(
            risks=1,
            requirement_changes=1,
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
                "path": "requirement_changes.0.previous_state",
                "op": "contains",
                "value": "1,000",
            },
            {
                "path": "requirement_changes.0.new_state",
                "op": "contains",
                "value": "900",
            },
            {
                "path": "requirement_changes.0.change_status",
                "op": "equals",
                "value": "proposed",
            },
            {
                "path": "actions.0.owner",
                "op": "contains",
                "value": "Account Team",
            },
            {
                "path": "actions.0.due_date",
                "op": "contains",
                "value": "Friday",
            },
        ],
        "manual_review": [
            "1,000 requests per second remains the signed criterion.",
            "900 is proposed but not formally approved.",
            "Friday applies to requesting written confirmation.",
            "No schedule delay should be invented.",
        ],
    },

    "TC-030": {
        "expected_counts": counts(
            requirement_changes=1,
            actions=1,
            uncertainties=1,