TEST_CASES = [
    {
        "id": "TC-001",
        "language": "English",
        "difficulty": "Simple",
        "input": """
During today's integration test, the authentication service returned 401 errors for all test accounts. QA could not complete the planned test cycle. Backend Engineering is investigating the authentication configuration and will provide an update by Wednesday. No change to the release date has been discussed.
""".strip(),
    },
    {
        "id": "TC-002",
        "language": "Korean",
        "difficulty": "Medium",
        "input": """
최종 API 명세서는 월요일까지 전달될 예정이었지만 아직 고객으로부터 전달되지 않았습니다. 최종 명세서를 받기 전에는 Integration Module 개발을 시작할 수 없습니다. 고객은 목요일까지 명세서를 전달할 계획이라고 했습니다. System Test는 다음 주 월요일로 예정되어 있지만, 현재까지 수정된 일정은 합의되지 않았습니다.
""".strip(),
    },
    {
        "id": "TC-003",
        "language": "English",
        "difficulty": "Medium",
        "input": """
The current security requirement specifies encryption key rotation every 90 days. The client proposed changing the interval to every 30 days. The Security Lead said the change would require configuration redesign and approximately two additional engineering days. The Architecture Team will review the proposal on Friday, and the change has not yet been approved.
""".strip(),
    },
    {
        "id": "TC-004",
        "language": "Korean",
        "difficulty": "Difficult",
        "input": """
이번 Load Test에서 메모리 사용량이 내부 기준치를 초과했습니다. 다음 Performance Review 전에 추가 Memory Profiling이 필요합니다. 아직 담당자는 지정되지 않았고 Profiling 완료 일정도 결정되지 않았습니다. 분석 결과가 나오기 전까지 Release Plan은 변경하지 않기로 했습니다.
""".strip(),
    },
    {
        "id": "TC-005",
        "language": "English",
        "difficulty": "Difficult",
        "input": """
Earlier meeting notes state that client acceptance requires a 95% test pass rate. In today's update, the Product Manager said that 90% would be acceptable for the pilot, but client approval has not been obtained. QA is still using 95% in the acceptance checklist. No schedule impact was discussed.
""".strip(),
    },
]