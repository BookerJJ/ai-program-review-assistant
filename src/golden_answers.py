from .test_cases import TEST_CASES


TEST_INPUTS = {
    test_case["id"]: test_case["input"]
    for test_case in TEST_CASES
}


GOLDEN_EXPECTATIONS = {
    "TC-001": {
        "expected_counts": {
            "issues": 1,
            "risks": 0,
            "dependencies": 0,
            "requirement_changes": 0,
            "schedule_impacts": 0,
            "actions": 1,
            "uncertainties": 1,
        },
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
            "Wednesday must apply to providing the update, not necessarily completing the investigation.",
            "Release schedule impact should remain unresolved rather than becoming a delay risk.",
        ],
    },

    "TC-002": {
        "expected_counts": {
            "issues": 1,
            "risks": 1,
            "dependencies": 1,
            "requirement_changes": 0,
            "schedule_impacts": 1,
            "actions": 1,
            "uncertainties": 1,
        },
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
                "op": "equals",
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
            "Do not invent a risk that the customer may miss Thursday simply because Thursday is a plan.",
            "The explicit customer delivery commitment should be extracted as the action.",
        ],
    },

    "TC-003": {
        "expected_counts": {
            "issues": 0,
            "risks": 1,
            "dependencies": 0,
            "requirement_changes": 1,
            "schedule_impacts": 1,
            "actions": 1,
            "uncertainties": 1,
        },
        "assertions": [
            {
                "path": "risks.0.basis",
                "op": "equals",
                "value": "inferred",
            },
            {
                "path": "requirement_changes.0.previous_state",
                "op": "equals",
                "value": "every 90 days",
            },
            {
                "path": "requirement_changes.0.new_state",
                "op": "equals",
                "value": "every 30 days",
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
            "The additional engineering effort is a supported inferred risk if the proposal is approved.",
            "Configuration redesign is not a milestone unless the input explicitly identifies it as one.",
        ],
    },

    "TC-004": {
        "expected_counts": {
            "issues": 1,
            "risks": 0,
            "dependencies": 1,
            "requirement_changes": 0,
            "schedule_impacts": 0,
            "actions": 1,
            "uncertainties": 2,
        },
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
            "Memory Profiling is an explicit dependency for the next Performance Review.",
            "Do not convert missing profiling schedule information into a schedule impact.",
            "No root cause or release delay should be invented.",
        ],
    },

    "TC-005": {
        "expected_counts": {
            "issues": 0,
            "risks": 1,
            "dependencies": 0,
            "requirement_changes": 1,
            "schedule_impacts": 0,
            "actions": 0,
            "uncertainties": 1,
        },
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
                "op": "equals",
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
            "95% remains the current acceptance criterion.",
            "Do not invent pilot rejection, delay, or another outcome absent from the input.",
        ],
    },
}