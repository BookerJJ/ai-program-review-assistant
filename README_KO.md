# AI Program Review Assistant — 한국어 요약

본 LLM 애플리케이션은 프로젝트 업데이트와 관련해 한국어/영어 프로젝트 업데이트를 Issue, Risk, Dependency, Requirement Change, Schedule Impact, Action, Uncertainty와 같은 구조화된 TPM Finding으로 변환하는 것을 목적으로 합니다.

이번 시도는 초기 프로젝트로 복잡한 RAG/Agent 시스템을 한 번에 만드는 것보다, **Prompting → Structured Output → Grounding → Evidence → Evaluation → Failure Analysis**의 기본 흐름을 통제된 환경에서 직접 설계하고 검증을 시도하는 것을 목표로 프로젝트를 수행했습니다.

## 최종 결과

| Metric | qwen3:8b | Gemini 3.8 Flash |
|---|---:|---:|
| Execution | 20 / 20 | 20 / 20 |
| Structural | 86.0 | 93.6 |
| Strict Evidence | 97.5% | 100.0% |
| Human Semantic | 85.0 | 94.0 |
| 평균 Latency | 16.861 s | 19.257 s |

이 표는 **해당 Frozen TPM Extraction Task에 한정된 비교**이며 일반적인 Model Ranking을 의미하지 않습니다.

평가에서는 Structural, Strict Evidence, Human Semantic을 하나의 Accuracy Score로 합치지 않았습니다. 각각 다른 실패 유형을 측정했습니다.

세부 내용은 영문 [`README.md`](README.md)와 `docs/`를 참고해 주세요.