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