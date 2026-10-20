# AI Program Review Assistant — 한국어 요약

이 LLM 애플리케이션은 **한국어/영어 프로젝트 업데이트**를 Issue, Risk, Dependency, Requirement Change, Schedule Impact, Action, Uncertainty 등 구조화된 TPM Finding으로 변환합니다. 중요한 Finding에는 원문 Evidence를 함께 기록하고, 정보가 부족한 부분은 Uncertainty로 남깁니다.

복잡한 RAG/Agent 시스템을 처음부터 결합하기보다, **Prompting → Structured Output → Grounding → Evidence → Evaluation → Failure Analysis**의 기본 흐름을 통제된 환경에서 직접 설계하고 검증하는 데 집중했습니다.

## 최종 모델 비교

| Metric | qwen3:8b | Gemini 3.8 Flash |
|---|---:|---:|
| Execution | 20 / 20 | 20 / 20 |
| Structural | 86.0 | 93.6 |
| Strict Evidence | 97.5% | 100.0% |
| Human Semantic* | 85.0 | 94.0 |
| 평균 Latency | 16.861 s | 19.257 s |

이 표는 **해당 Frozen TPM Extraction Task에 한정된 비교**이며 일반적인 Model Ranking을 의미하지 않습니다. 실행 환경과 Token 계산 방식이 서로 달라 Latency 및 Token 수치 역시 통제된 성능 비교로 해석해서는 안 됩니다.

평가에서는 **Structural, Strict Evidence, Human Semantic을 하나의 Accuracy Score로 합치지 않았습니다.** 각각 구조적 일치도, 입력 원문의 문자열 추적 가능성, 의미적 정확성을 별도로 측정했습니다. 특히 Strict Evidence의 100%는 인용한 문자열을 원문에서 찾을 수 있다는 뜻이지, Finding의 논리적 정당성을 완전히 검증했다는 뜻은 아닙니다.

\* **평가 관련 주의:** `Human Semantic`은 실험 당시의 지표 이름입니다. Gemini의 94.0은 AI 어시스턴트가 정해진 Rubric에 따라 검토·채점한 값이며, **독립적인 사람 평가자가 추가 검증한 점수는 아닙니다.** 해당 점수는 잠정적인 Rubric 평가 결과로 해석해야 합니다.

## 프로젝트 확인 방법

- [영문 README](README.md): 프로젝트 목적, 모델 비교, 설계와 실행 절차
- [아키텍처](docs/architecture.md): 입력부터 평가까지의 처리 흐름
- [설계 의사결정](docs/design-decisions.md): RAG 제외, Schema, Prompt, Evidence 설계 이유
- [평가 방법](docs/evaluation-methodology.md): Structural / Evidence / Semantic의 구분과 한계
- [실험 기록](docs/experiment-history.md): Prompt 변경, 성능 측정, 실패 분석
- [결과 재현](docs/reproducing-results.md): API 호출 없이 저장된 결과를 재평가하는 방법

최종 의사결정은 TPM 또는 담당자가 수행합니다. 이 애플리케이션은 근거가 있는 Finding과 불확실성을 정리하는 **의사결정 지원 도구**입니다.
