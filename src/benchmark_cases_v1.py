BENCHMARK_CASES = [
    # =========================================================
    # SIMPLE — 10 cases
    # =========================================================

    {
        "id": "TC-001",
        "language": "English",
        "difficulty": "Simple",
        "primary_target": "Issue + action; no invented schedule impact",
        "input": """
During today's integration test, the authentication service returned 401 errors for all test accounts. QA could not complete the planned test cycle. Backend Engineering is investigating the authentication configuration and will provide an update by Wednesday. No change to the release date has been discussed.
""".strip(),
    },

    {
        "id": "TC-006",
        "language": "English",
        "difficulty": "Simple",
        "primary_target": "Issue + explicit action + null schedule impact",
        "input": """
The nightly build failed because the deployment configuration file was missing from the build package. DevOps restored the file and will rerun the build by 3 PM today. No release milestone has been changed.
""".strip(),
    },

    {
        "id": "TC-007",
        "language": "Korean",
        "difficulty": "Simple",
        "primary_target": "Issue + vendor action",
        "input": """
한국어 Localization 파일에 일부 문자열이 누락되어 QA 검수가 중단되었습니다. Localization Vendor는 수정된 파일을 금요일까지 다시 전달하기로 했습니다. 현재 Release 일정 변경은 논의되지 않았습니다.
""".strip(),
    },

    {
        "id": "TC-008",
        "language": "English",
        "difficulty": "Simple",
        "primary_target": "Negative case; avoid creating findings",
        "input": """
The client reviewed the current feature scope and confirmed that no requirement changes are needed. Engineering reported that implementation is proceeding according to the existing plan. No new issues, risks, or schedule changes were identified.
""".strip(),
    },

    {
        "id": "TC-009",
        "language": "Korean",
        "difficulty": "Simple",
        "primary_target": "Existing issue + explicit action",
        "input": """
테스트 서버의 SSL 인증서가 만료되어 QA가 접속할 수 없습니다. Infrastructure Team이 인증서를 갱신하고 오늘 오후까지 서버 접속 상태를 확인할 예정입니다.
""".strip(),
    },

    {
        "id": "TC-010",
        "language": "English",
        "difficulty": "Simple",
        "primary_target": "Completed activity; avoid false issue",
        "input": """
The database backup completed successfully overnight. The Operations Team verified the backup file this morning, and no errors were reported. No follow-up action is required.
""".strip(),
    },

    {
        "id": "TC-011",
        "language": "Korean",
        "difficulty": "Simple",
        "primary_target": "Future commitment without invented risk",
        "input": """
UI Team은 신규 아이콘 Asset을 금요일까지 전달할 예정입니다. 현재 개발 작업은 기존 Asset으로 계속 진행 중이며 일정 영향은 보고되지 않았습니다.
""".strip(),
    },

    {
        "id": "TC-012",
        "language": "English",
        "difficulty": "Simple",
        "primary_target": "Issue + action deadline",
        "input": """
The staging environment became unavailable this morning, so QA paused regression testing. Infrastructure is restarting the environment and will confirm service availability by 2 PM.
""".strip(),
    },

    {
        "id": "TC-013",
        "language": "Korean",
        "difficulty": "Simple",
        "primary_target": "Issue + explicit remediation action",
        "input": """
Accessibility Review에서 두 개의 버튼에 Screen Reader Label이 없는 것이 확인되었습니다. UI Engineering이 해당 Label을 추가하고 수요일까지 수정 내용을 QA에 전달하기로 했습니다.
""".strip(),
    },

    {
        "id": "TC-014",
        "language": "Korean",
        "difficulty": "Simple",
        "primary_target": "Confirmed requirement change",
        "input": """
기존 세션 Timeout 요구사항은 20분이었습니다. 고객이 이를 30분으로 변경하는 안을 최종 승인했습니다. 변경에 따른 일정 영향은 없습니다.
""".strip(),
    },

    # =========================================================
    # MEDIUM — 10 cases
    # =========================================================

    {
        "id": "TC-002",
        "language": "Korean",
        "difficulty": "Medium",
        "primary_target": "Risk vs issue + dependency + missing duration",
        "input": """
최종 API 명세서는 월요일까지 전달될 예정이었지만 아직 고객으로부터 전달되지 않았습니다. 최종 명세서를 받기 전에는 Integration Module 개발을 시작할 수 없습니다. 고객은 목요일까지 명세서를 전달할 계획이라고 했습니다. System Test는 다음 주 월요일로 예정되어 있지만, 현재까지 수정된 일정은 합의되지 않았습니다.
""".strip(),
    },

    {
        "id": "TC-003",
        "language": "English",
        "difficulty": "Medium",
        "primary_target": "Proposed requirement + supported effort impact",
        "input": """
The current security requirement specifies encryption key rotation every 90 days. The client proposed changing the interval to every 30 days. The Security Lead said the change would require configuration redesign and approximately two additional engineering days. The Architecture Team will review the proposal on Friday, and the change has not yet been approved.
""".strip(),
    },

    {
        "id": "TC-015",
        "language": "English",
        "difficulty": "Medium",
        "primary_target": "Dependency + future milestone risk",
        "input": """
Production deployment cannot begin until the security scan is completed. The Security Team expects to finish the scan on Tuesday, while production deployment is planned for Wednesday morning. No revised deployment schedule has been agreed.
""".strip(),
    },

    {
        "id": "TC-016",
        "language": "Korean",
        "difficulty": "Medium",
        "primary_target": "Proposed requirement + effort",
        "input": """
현재 시스템 Log 보관 기간은 7일입니다. 고객은 보관 기간을 30일로 늘리는 방안을 제안했습니다. Engineering은 변경 시 Storage 설정 작업에 약 하루가 추가로 필요하다고 설명했습니다. 변경안은 아직 승인되지 않았습니다.
""".strip(),
    },

    {
        "id": "TC-017",
        "language": "English",
        "difficulty": "Medium",
        "primary_target": "Issue + dependency + potential test impact",
        "input": """
The Data Team reported that approximately 40% of the required test records are still missing. Integration testing requires the complete dataset and is scheduled for Friday. The Data Team has not provided a completion date, and no revised test schedule has been approved.
""".strip(),
    },

    {
        "id": "TC-018",
        "language": "Korean",
        "difficulty": "Medium",
        "primary_target": "Vendor delay + explicit recovery commitment",
        "input": """
외부 Vendor가 화요일까지 전달하기로 한 Character Animation 파일을 아직 전달하지 않았습니다. Animation Team은 해당 파일이 있어야 최종 Integration을 진행할 수 있습니다. Vendor는 목요일 오전까지 파일을 전달하겠다고 했습니다.
""".strip(),
    },

    {
        "id": "TC-019",
        "language": "English",
        "difficulty": "Medium",
        "primary_target": "Multiple actions with different deadlines",
        "input": """
Engineering is investigating the crash and will provide an initial analysis by Tuesday. QA will prepare a reproduction package by Wednesday. A fix date has not been committed.
""".strip(),
    },

    {
        "id": "TC-020",
        "language": "Korean",
        "difficulty": "Medium",
        "primary_target": "Conflicting requirement information",
        "input": """
기존 Requirements 문서에는 최대 Upload Size가 100MB로 정의되어 있습니다. 오늘 고객 이메일에서는 200MB가 필요하다고 언급했지만 공식 변경 승인은 아직 없습니다. Engineering은 현재 100MB 기준으로 개발 중입니다.
""".strip(),
    },

    {
        "id": "TC-021",
        "language": "English",
        "difficulty": "Medium",
        "primary_target": "Technical issue with unknown impact",
        "input": """
Load testing showed CPU utilization above the internal target on two application servers. Engineering will perform additional profiling, but no owner or completion date has been assigned. The release plan remains unchanged pending the profiling results.
""".strip(),
    },

    {
        "id": "TC-022",
        "language": "Korean",
        "difficulty": "Medium",
        "primary_target": "Confirmed requirement change without schedule impact",
        "input": """
API Timeout은 기존 30초에서 60초로 변경하는 것으로 고객 승인이 완료되었습니다. Backend Team은 다음 Build부터 변경된 값을 적용할 예정입니다. 이 변경으로 인한 추가 일정 영향은 없다고 확인되었습니다.
""".strip(),
    },

    # =========================================================
    # DIFFICULT — 10 cases
    # =========================================================

    {
        "id": "TC-004",
        "language": "Korean",
        "difficulty": "Difficult",
        "primary_target": "Null handling + conservative analysis",
        "input": """
이번 Load Test에서 메모리 사용량이 내부 기준치를 초과했습니다. 다음 Performance Review 전에 추가 Memory Profiling이 필요합니다. 아직 담당자는 지정되지 않았고 Profiling 완료 일정도 결정되지 않았습니다. 분석 결과가 나오기 전까지 Release Plan은 변경하지 않기로 했습니다.
""".strip(),
    },

    {
        "id": "TC-005",
        "language": "English",
        "difficulty": "Difficult",
        "primary_target": "Conflicting criteria + proposed change",
        "input": """
Earlier meeting notes state that client acceptance requires a 95% test pass rate. In today's update, the Product Manager said that 90% would be acceptable for the pilot, but client approval has not been obtained. QA is still using 95% in the acceptance checklist. No schedule impact was discussed.
""".strip(),
    },

    {
        "id": "TC-023",
        "language": "English",
        "difficulty": "Difficult",
        "primary_target": "Conflicting dates without selecting a winner",
        "input": """
The current project plan lists API delivery on Thursday. In today's engineering meeting, the Backend Lead said Friday is more realistic, but the Project Manager stated that the official plan has not been changed. No final delivery date was agreed during the meeting.
""".strip(),
    },

    {
        "id": "TC-024",
        "language": "Korean",
        "difficulty": "Difficult",
        "primary_target": "Multi-clause action/deadline binding",
        "input": """
Engineering은 Login Crash를 조사 중이며 화요일까지 조사 결과를 공유하기로 했습니다. 수정 사항이 준비되면 QA가 재테스트를 수행할 예정이지만 수정 완료일과 재테스트 일정은 아직 정해지지 않았습니다.
""".strip(),
    },

    {
        "id": "TC-025",
        "language": "English",
        "difficulty": "Difficult",
        "primary_target": "Conditional change + explicit effort + no milestone",
        "input": """
The client proposed enabling audit logging for all administrator actions. Engineering estimated that the proposal would require approximately three additional development days if approved. The client has not yet confirmed the change, and no release milestone was referenced in the discussion.
""".strip(),
    },

    {
        "id": "TC-026",
        "language": "Korean",
        "difficulty": "Difficult",
        "primary_target": "Dependency chain",
        "input": """
Security Review가 완료되어야 Production Access 승인을 받을 수 있습니다. Production Access 승인이 완료된 이후에만 Deployment Validation을 시작할 수 있습니다. Security Review 담당자는 아직 정해지지 않았으며 현재 Release 일정 변경은 없습니다.
""".strip(),
    },

    {
        "id": "TC-027",
        "language": "English",
        "difficulty": "Difficult",
        "primary_target": "Existing issue with explicitly ruled-out schedule impact",
        "input": """
Performance testing found a 12% response-time regression in the reporting service. Engineering is investigating the regression. The Release Manager confirmed that the current release date will not change because of this finding. No remediation deadline has been set.
""".strip(),
    },

    {
        "id": "TC-028",
        "language": "Korean",
        "difficulty": "Difficult",
        "primary_target": "Proposed scope removal with current state preserved",
        "input": """
고객은 Pilot 버전에서 Export 기능을 제외하는 방안을 제안했습니다. Product Lead는 고객의 최종 확인 전까지 기존 Scope를 유지하겠다고 했습니다. 현재 개발팀은 Export 기능을 포함한 기존 Scope 기준으로 작업 중입니다.
""".strip(),
    },

    {
        "id": "TC-029",
        "language": "English",
        "difficulty": "Difficult",
        "primary_target": "Conflicting criteria + explicit clarification action",
        "input": """
The signed acceptance document specifies a minimum throughput of 1,000 requests per second. A recent client message mentioned that 900 requests per second may be sufficient for the pilot. The client has not approved a formal change. The Account Team will request written confirmation by Friday. No schedule change has been discussed.
""".strip(),
    },

    {
        "id": "TC-030",
        "language": "Korean",
        "difficulty": "Difficult",
        "primary_target": "Bilingual technical terms + unresolved requirement",
        "input": """
현재 Production 기준에서는 Feature Flag가 기본적으로 Disabled 상태입니다. 고객은 다음 Pilot Build에서 Default를 Enabled로 변경할 수 있는지 요청했습니다. Engineering은 기술적으로 가능하다고 확인했지만 변경 승인은 아직 없습니다. Product Team은 다음 주 화요일 Review에서 최종 결정을 논의할 예정입니다.
""".strip(),
    },
]

def validate_benchmark_distribution() -> None:
    assert len(BENCHMARK_CASES) == 30

    ids = [case["id"] for case in BENCHMARK_CASES]
    assert len(ids) == len(set(ids))

    english = sum(
        case["language"] == "English"
        for case in BENCHMARK_CASES
    )

    korean = sum(
        case["language"] == "Korean"
        for case in BENCHMARK_CASES
    )

    simple = sum(
        case["difficulty"] == "Simple"
        for case in BENCHMARK_CASES
    )

    medium = sum(
        case["difficulty"] == "Medium"
        for case in BENCHMARK_CASES
    )

    difficult = sum(
        case["difficulty"] == "Difficult"
        for case in BENCHMARK_CASES
    )

    assert english == 15
    assert korean == 15

    assert simple == 10
    assert medium == 10
    assert difficult == 10


if __name__ == "__main__":
    validate_benchmark_distribution()
    print("Benchmark distribution OK")