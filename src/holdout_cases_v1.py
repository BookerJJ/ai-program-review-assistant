HOLDOUT_CASES = [

    # =========================================================
    # 1. OPERATIONAL INCIDENT
    # =========================================================

    {
        "id": "H-001",
        "language": "English",
        "scenario_type": "Operational Incident",
        "primary_target":
            "Existing issue + action binding + unresolved release impact",
        "input": (
            "During checkout validation, the payment gateway returned "
            "503 errors for all test transactions. QA stopped the "
            "checkout validation cycle. The Platform Team is "
            "investigating the gateway configuration and will provide "
            "a status update by 4 PM today. The release date has not "
            "been reviewed yet."
        ),
    },

    {
        "id": "H-002",
        "language": "Korean",
        "scenario_type": "Operational Incident",
        "primary_target":
            "Existing issue + remediation action + no schedule impact",
        "input": (
            "Texture Streaming 테스트에서 세 개의 Asset에 필요한 "
            "Mip Level이 누락된 것이 확인되었습니다. Art Tech Team은 "
            "해당 Asset을 다시 생성해 내일 정오까지 전달하기로 했습니다. "
            "현재까지 Milestone 영향은 확인되지 않았습니다."
        ),
    },

    {
        "id": "H-003",
        "language": "English",
        "scenario_type": "Operational Incident",
        "primary_target":
            "Completed activity without false findings",
        "input": (
            "The nightly data export completed successfully. "
            "QA performed a spot check on the exported records and "
            "found no errors. No additional investigation or "
            "follow-up work is required."
        ),
    },

    {
        "id": "H-004",
        "language": "Korean",
        "scenario_type": "Operational Incident",
        "primary_target":
            "Current blocking issue + explicit recovery action",
        "input": (
            "Staging Database가 예기치 않게 Read-Only 상태로 전환되어 "
            "Integration 테스트를 진행할 수 없습니다. Database Team이 "
            "정상 상태로 복구 중이며 오전 11시까지 접근 가능 여부를 "
            "확인할 예정입니다."
        ),
    },

    # =========================================================
    # 2. REQUIREMENT / SCOPE CHANGE
    # =========================================================

    {
        "id": "H-005",
        "language": "English",
        "scenario_type": "Requirement Change",
        "primary_target":
            "Proposed requirement + review action + approval uncertainty",
        "input": (
            "The current data retention requirement is 14 days. "
            "The client requested increasing the retention period to "
            "45 days, but the change has not been approved. "
            "The Security Team will review the proposal on Tuesday. "
            "No implementation effort estimate has been provided."
        ),
    },

    {
        "id": "H-006",
        "language": "Korean",
        "scenario_type": "Requirement Change",
        "primary_target":
            "Confirmed requirement change + implementation action",
        "input": (
            "Login Retry Limit을 기존 5회에서 3회로 변경하는 안이 "
            "최종 승인되었습니다. Backend Team은 다음 Sprint부터 "
            "변경된 값을 적용할 예정입니다. 이 변경으로 인한 추가 "
            "일정 영향은 없습니다."
        ),
    },

    {
        "id": "H-007",
        "language": "English",
        "scenario_type": "Requirement Change",
        "primary_target":
            "Proposed setting change + approval dependency",
        "input": (
            "Telemetry collection is currently disabled by default. "
            "Product proposed enabling it by default for the Beta. "
            "Legal stated that the change cannot be approved until "
            "client consent is received. No final decision has been made."
        ),
    },

    {
        "id": "H-008",
        "language": "Korean",
        "scenario_type": "Requirement Change",
        "primary_target":
            "Conditional scope change + explicit additional effort",
        "input": (
            "고객은 High-Resolution Texture 지원을 추가하는 방안을 "
            "제안했습니다. Engineering은 해당 변경이 승인될 경우 "
            "약 이틀의 추가 작업이 필요하다고 설명했습니다. "
            "변경안은 아직 승인되지 않았으며 Release Milestone은 "
            "논의되지 않았습니다."
        ),
    },

    # =========================================================
    # 3. DEPENDENCY / SCHEDULE
    # =========================================================

    {
        "id": "H-009",
        "language": "English",
        "scenario_type": "Dependency and Schedule",
        "primary_target":
            "Explicit dependency + nearby milestone timing risk",
        "input": (
            "Certification testing cannot begin until the signed "
            "firmware package is available. The Security Team will "
            "provide the signed package on Wednesday. Certification "
            "testing is planned for Thursday morning. No revised "
            "test schedule has been agreed."
        ),
    },

    {
        "id": "H-010",
        "language": "Korean",
        "scenario_type": "Dependency and Schedule",
        "primary_target":
            "Missing prerequisite + dependency + unknown ETA",
        "input": (
            "License Server Whitelist가 아직 적용되지 않았습니다. "
            "Whitelist가 활성화되기 전에는 Build Validation을 시작할 "
            "수 없습니다. Build Validation은 금요일로 예정되어 있지만 "
            "Infrastructure Team은 Whitelist 적용 완료 일정을 아직 "
            "제공하지 않았습니다."
        ),
    },

    {
        "id": "H-011",
        "language": "English",
        "scenario_type": "Dependency and Schedule",
        "primary_target":
            "Explicit dependency without invented timing risk",
        "input": (
            "Localization signoff must be completed before the store "
            "submission can begin. The Localization Team will complete "
            "signoff on Monday. Store submission is scheduled for "
            "Wednesday. No schedule concern has been reported."
        ),
    },

    {
        "id": "H-012",
        "language": "Korean",
        "scenario_type": "Dependency and Schedule",
        "primary_target":
            "Multi-step dependency chain + missing owner",
        "input": (
            "Security Review가 완료된 이후에 Privacy Approval을 받을 "
            "수 있습니다. Privacy Approval이 완료되어야 Pilot Access를 "
            "활성화할 수 있습니다. Security Review 담당자는 아직 "
            "지정되지 않았으며 현재 일정 변경은 없습니다."
        ),
    },

    # =========================================================
    # 4. ACTION / DEADLINE BINDING
    # =========================================================

    {
        "id": "H-013",
        "language": "English",
        "scenario_type": "Action and Deadline",
        "primary_target":
            "Two owners + two deadlines + unresolved remediation date",
        "input": (
            "An intermittent connection drop is under investigation. "
            "Support will collect the affected session logs by Tuesday. "
            "Engineering will review the collected logs by Thursday. "
            "No remediation date has been committed."
        ),
    },

    {
        "id": "H-014",
        "language": "Korean",
        "scenario_type": "Action and Deadline",
        "primary_target":
            "Multiple independent actions with separate deadlines",
        "input": (
            "Mobile Client에서 간헐적인 Crash가 보고되었습니다. "
            "고객은 영향을 받은 Device 목록을 월요일까지 전달하기로 "
            "했습니다. QA는 수요일까지 Crash 재현을 완료할 예정입니다. "
            "수정 완료 일정은 아직 정해지지 않았습니다."
        ),
    },

    {
        "id": "H-015",
        "language": "English",
        "scenario_type": "Action and Deadline",
        "primary_target":
            "Future commitment without hypothetical failure risk",
        "input": (
            "The external audio vendor will deliver the final mix on "
            "Friday. The internal team can continue using the temporary "
            "mix until then. No schedule impact has been identified."
        ),
    },

    {
        "id": "H-016",
        "language": "Korean",
        "scenario_type": "Action and Deadline",
        "primary_target":
            "Two future commitments + unresolved decision",
        "input": (
            "Analytics Team은 새로운 기능의 운영 비용 추정치를 "
            "화요일까지 공유할 예정입니다. Product Team은 수요일에 "
            "제안 내용을 검토하기로 했습니다. 해당 기능을 실제로 "
            "추가할지는 아직 결정되지 않았습니다."
        ),
    },

    # =========================================================
    # 5. CONFLICT / NEGATIVE CASE
    # =========================================================

    {
        "id": "H-017",
        "language": "English",
        "scenario_type": "Conflict and Negative",
        "primary_target":
            "Conflicting requirement information without approval",
        "input": (
            "The signed operations requirement specifies seven days "
            "of log retention. During today's meeting, the Product "
            "Manager said that 30 days may be preferable for the "
            "enterprise launch, but the client has not approved a "
            "change. Operations continues to use the seven-day setting."
        ),
    },

    {
        "id": "H-018",
        "language": "Korean",
        "scenario_type": "Conflict and Negative",
        "primary_target":
            "Conflicting schedule statements without final decision",
        "input": (
            "현재 공식 Launch Date는 10월 10일입니다. Engineering "
            "Lead는 오늘 회의에서 10월 12일이 더 현실적이라고 "
            "말했지만 Project Manager는 공식 일정이 변경되지 않았다고 "
            "확인했습니다. 최종 일정 변경 결정은 내려지지 않았습니다."
        ),
    },

    {
        "id": "H-019",
        "language": "English",
        "scenario_type": "Conflict and Negative",
        "primary_target":
            "Successful rollout with no findings",
        "input": (
            "The feature rollout was completed successfully across all "
            "target regions. Monitoring remained within normal ranges "
            "for 24 hours, and no incidents were reported. "
            "No follow-up action is required."
        ),
    },

    {
        "id": "H-020",
        "language": "Korean",
        "scenario_type": "Conflict and Negative",
        "primary_target":
            "Clean status update without fabricated findings",
        "input": (
            "고객은 현재 Scope에 추가 변경이 없다고 확인했습니다. "
            "Development Team은 기존 계획대로 작업 중이며 현재 "
            "Blocker나 새로운 Risk는 보고되지 않았습니다. "
            "추가 Action Item도 없습니다."
        ),
    },
]


SCENARIO_TYPES = [
    "Operational Incident",
    "Requirement Change",
    "Dependency and Schedule",
    "Action and Deadline",
    "Conflict and Negative",
]


def validate_holdout_distribution() -> None:
    assert len(HOLDOUT_CASES) == 20

    ids = [
        case["id"]
        for case in HOLDOUT_CASES
    ]

    assert len(ids) == len(set(ids))

    english = sum(
        case["language"] == "English"
        for case in HOLDOUT_CASES
    )

    korean = sum(
        case["language"] == "Korean"
        for case in HOLDOUT_CASES
    )

    assert english == 10
    assert korean == 10

    for scenario_type in SCENARIO_TYPES:
        count = sum(
            case["scenario_type"]
            == scenario_type
            for case in HOLDOUT_CASES
        )

        assert count == 4

        type_cases = [
            case
            for case in HOLDOUT_CASES
            if case["scenario_type"]
            == scenario_type
        ]

        type_english = sum(
            case["language"]
            == "English"
            for case in type_cases
        )

        type_korean = sum(
            case["language"]
            == "Korean"
            for case in type_cases
        )

        assert type_english == 2
        assert type_korean == 2


if __name__ == "__main__":
    validate_holdout_distribution()
    print("Holdout distribution OK")