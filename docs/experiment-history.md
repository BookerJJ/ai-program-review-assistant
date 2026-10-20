# Experiment History

## Smoke-test progression

| Prompt | Clean Structural | Human Semantic | Strict Evidence | Main learning |
|---|---:|---:|---:|---|
| grounded-v0.2 | 68.0 | 48.0 | 85.8% | Grounding reduced unsupported claims but classification remained weak. |
| grounded-v0.3 | 64.0 | 48.0 | 72.6% | Adding many rules did not improve reasoning. |
| grounded-v0.4 | 66.7 | 56.0 | 71.7% | Targeted rules helped more than broad rule expansion. |
| fewshot-v0.5 | 68.8 | 68.0 | 76.7% | Targeted examples improved semantic boundaries. |

The Structural values above were recomputed with Evidence excluded from the Structural denominator.

## 30-case development benchmark

| Prompt | Structural | Human Semantic | Strict Evidence | Decision |
|---|---:|---:|---:|---|
| fewshot-v0.5 | 82.2 | 77.3 | 88.6% | Retained as the frozen baseline. |
| fewshot-boundary-v0.6 | 85.2 | 79.7 | 96.7% | Rejected: missed the predefined 80.0 semantic gate and completeness regressed. |

## Final 20-case local holdout

- execution: 20 / 20
- Structural: 86.0
- Strict Evidence: 97.5%
- Human Semantic: 85.0
- average latency: 16.861 s
- total tokens: 26,958

## Frozen hosted comparison

Gemini 3.8 Flash was run against the same 20 cases without Gemini-specific prompt tuning.

- execution: 20 / 20
- Structural: 93.6
- Strict Evidence: 100.0%
- Human Semantic: 94.0
- average latency: 19.257 s
- total tokens: 29,999

The remaining Gemini weakness was primarily classification, especially inferred-risk handling, rather than unsupported factual generation.

## Operational learning

The hosted comparison encountered Free Tier quota limits. Infrastructure failures were separated from model-quality evaluation, canonical successful outputs were preserved, and historical quota-error attempts are intentionally omitted from the public package.

## Notes on score provenance

The Structural and Strict Evidence numbers above are recomputable from saved outputs using the offline evaluators. The Semantic numbers come from completed case-level rubric CSVs rather than automated structural scoring. In particular, the Gemini 94.0 rating was prepared by an AI assistant applying the five-dimension rubric and has **not been independently validated by a second human reviewer**. Interpret it as a provisional task-specific rating.

For methods, formulas, and artifact pointers, see [Evaluation Methodology](evaluation-methodology.md) and [Reproducing Results](reproducing-results.md).
