# Architecture

## Goal

Convert a directly supplied Korean or English project update into a validated `ProgramReview` object without retrieval, autonomous tools, or fine-tuning.

```text
Project Update
    |
    v
Versioned System Prompt
    |
    v
LLM Adapter
    |-- Ollama / qwen3:8b
    |-- Gemini 3.8 Flash comparison
    |
    v
Pydantic ProgramReview Schema
    |
    +--> saved raw result
    +--> objective structural evaluator
    +--> strict evidence traceability
    +--> manual semantic review
```

## Main modules

- `schemas.py`: strict Pydantic output contract.
- `prompts.py`: versioned system prompts, including the frozen `fewshot-v0.5` prompt.
- `analyzer.py`: local Ollama adapter.
- `gemini_client.py`: hosted Gemini adapter with the same structured-output schema.
- `benchmark_*`: 30-case development benchmark used for prompt diagnosis and selection.
- `holdout_*`: frozen 20-case unseen evaluation for the selected local prompt.
- `model_comparison_*`: frozen hosted comparison using the same holdout, schema, and goldens.

## Scope boundary

The implementation deliberately omits RAG, vector databases, autonomous action execution, and fine-tuning. The goal is to isolate generation, classification, grounding, evidence behavior, and evaluation before adding retrieval complexity.

## Request and validation flow

1. The caller supplies one Korean or English project update. No file retrieval is performed.
2. `analyzer.py` or `gemini_client.py` combines the input with a versioned system prompt and requests JSON matching `ProgramReview.model_json_schema()`.
3. `schemas.py` uses Pydantic to validate the returned object. `evidence` is required on material categories; missing information is represented as `null`, `unknown`, or a separate uncertainty, depending on the field.
4. Experiment runners save model output and metadata (status, model/prompt version, timing, tokens). Frozen outputs are preserved as canonical artifacts.
5. Offline evaluators compare these outputs with frozen test-case expectations. Structural and lexical Evidence checks are computed separately; scored Semantic CSVs preserve rubric judgments.

The base program itself **does not** automatically take actions, update ticketing systems, or change project plans. Decision approval remains with a human TPM.

## Reproduction boundary

`src/run_baseline.py` provides a small live local example. The frozen holdout and cross-model runner scripts document historical experiments; running them again is not required for [offline reproducibility](reproducing-results.md) and must not be treated as reproducing the same model outputs.
