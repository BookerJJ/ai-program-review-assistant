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