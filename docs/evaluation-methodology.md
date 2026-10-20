# Evaluation Methodology

The evaluation intentionally separates **execution**, **structural correctness**, **evidence traceability**, and **semantic quality**.

## Execution reliability

A case counts as successful when model inference completes and the returned JSON validates against the strict `ProgramReview` schema. Execution success is not treated as semantic accuracy.

## Objective Structural

Structural scoring checks deterministic expectations such as:

- expected category counts
- selected field assertions
- owner/date/status/null handling where a deterministic expectation is defined

Evidence is not included in the Structural denominator.

## Strict Evidence Traceability

For findings that require evidence, each evidence string is normalized and checked as an exact/substring match against the supplied source text.

This is deliberately a **lexical traceability metric**. It does not prove that the cited snippet semantically entails the model's conclusion.

## Human Semantic

Each case is reviewed on five 0–2 dimensions:

1. factual correctness
2. completeness
3. unsupported-claim control
4. classification accuracy
5. meaning preservation

Case semantic score = sum of the five dimensions / 10 × 100.

The semantic review is manual and rubric-based. It is not presented as a statistically independent human-subject benchmark.

## Development vs final evaluation

The 30-case benchmark is a **development benchmark**. Its findings influenced prompt changes and therefore it is not used as an unbiased final test.

The 20-case bilingual holdout was frozen before the final local evaluation and was not used to tune the selected prompt. The same holdout, Golden Expectations, schema, and prompt semantics were then reused for the hosted Gemini comparison.

## Model-comparison caveats

Latency and token counts are descriptive. qwen ran locally through Ollama while Gemini ran through a hosted API, and token accounting differs across providers. Quality scores are comparable only within this frozen task and evaluation design.

## Review provenance and interpretation

The repository preserves the historical label **Human Semantic** for the manually applied five-dimension rubric; this is distinct from an independently controlled human evaluation.

- Completed qwen development and holdout rating CSVs are provided, including per-case reviewer notes. The archived artifacts do not independently establish the reviewer identity, inter-rater agreement, or blinding.
- The Gemini 20-case ratings were prepared by an **AI assistant performing rubric-based manual review**. They have **not been independently approved or re-scored by another human evaluator**. The reported 94.0 is therefore provisional, not an independently validated human benchmark.
- All numeric scores are descriptive for these synthetic scenarios and this rubric. No statistical confidence intervals, significance tests, cross-rater agreement, or production generalization claims are made.

Structural and evidence metrics can be recomputed automatically from saved outputs. Semantic ratings require a reviewer to apply the rubric and record case-level judgments; simply rerunning the objective evaluator will **not** reproduce or independently verify the human-named metric.

## Additional threats to validity

- The development benchmark was inspected during prompt iteration. Only the 20-case holdout was left unseen for selecting the local prompt; that holdout was then **reused** in the hosted comparison.
- The hosted model was not tuned to the holdout, but the models do not have equivalent inference controls or environments. Latency is descriptive, not a controlled performance benchmark.
- Strict Evidence is a normalized exact/substring match; matching an input sentence does not prove it semantically entails a finding. The metric can both accept irrelevant snippets and reject valid paraphrases.
- Frozen few-shot examples sometimes omit `evidence` attributes in illustrative snippets even though actual outputs must pass the full strict schema. These prompts remain unchanged to preserve experiment history.
