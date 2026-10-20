# AI Program Review Assistant

A bilingual LLM application that converts Korean or English project updates into structured TPM findings while keeping evidence, uncertainty, and evaluation explicit.

The project was intentionally designed as a **small, controlled LLM system** before adding RAG or agents. Its goal is to make model behavior measurable: prompting, structured output, grounding, classification, evidence traceability, failure analysis, and model-choice trade-offs.

## What it produces

The output schema separates:

- summary
- issues
- risks
- dependencies
- requirement changes
- schedule impacts
- actions
- uncertainties
- source evidence for supported findings

The application uses Pydantic-backed structured output instead of free-form prose so outputs can be validated and compared programmatically.

## Architecture

```text
Project Update (KO/EN)
        |
        v
Versioned System Prompt
        |
        v
LLM
  | local: Ollama + qwen3:8b
  | hosted comparison: Gemini 3.8 Flash
        |
        v
Pydantic Structured Output
        |
        +--> Objective Structural Evaluation
        +--> Strict Evidence Traceability
        +--> Human Semantic Review
```

This implementation deliberately excludes RAG, vector databases, autonomous agents, and fine-tuning so the core generation behavior can be evaluated in isolation. Retrieval and cross-document grounding are natural future extensions rather than part of the current scope.

## Final frozen comparison

Both models were evaluated on the same frozen 20-case bilingual holdout with the same prompt semantics, Golden Expectations, output schema, and semantic-review rubric. No Gemini-specific prompt tuning was applied before the comparison.

| Metric | qwen3:8b | Gemini 3.8 Flash |
|---|---:|---:|
| Execution reliability | 20 / 20 | 20 / 20 |
| Objective Structural | 86.0 | 93.6 |
| Strict Evidence Traceability | 97.5% | 100.0% |
| Human Semantic | 85.0 | 94.0 |
| English Semantic | 84.0 | 96.0 |
| Korean Semantic | 86.0 | 92.0 |
| Average latency | 16.861 s | 19.257 s |
| Total tokens | 26,958 | 29,999 |

These results are **task-specific**. They are not intended as a universal model ranking. In this task Gemini produced stronger quality across the three evaluation dimensions, while qwen3:8b retained advantages in local execution, lower average latency, privacy, and independence from hosted API quotas.

Latency and token counts are descriptive rather than directly comparable benchmarks: qwen ran locally through Ollama, Gemini ran through a hosted API, and providers use different tokenization/accounting.

## Why the evaluation is split into three metrics

**Structural** checks deterministic behavior such as expected category counts and selected field assertions.

**Strict Evidence Traceability** checks whether cited evidence appears directly in the supplied input using normalized exact/substring matching. It does not claim that lexical overlap alone proves semantic correctness.

**Human Semantic** uses a five-dimension 0–2 rubric: factual correctness, completeness, unsupported-claim control, classification accuracy, and meaning preservation.

These metrics are intentionally **not merged into one score**.

## Prompt evolution

The project used failure-driven prompt iteration rather than continuously adding rules.

- baseline: minimal structured extraction
- grounded prompts: stronger evidence and unsupported-information rules
- targeted rules: refined known failure patterns
- `fewshot-v0.5`: targeted semantic examples; selected final prompt
- `fewshot-boundary-v0.6`: improved some classifications but missed the predeclared semantic adoption gate and was rejected

The corrected 30-case development benchmark produced:

| Version | Structural | Strict Evidence | Human Semantic |
|---|---:|---:|---:|
| fewshot-v0.5 | 82.2 | 88.6% | 77.3 |
| fewshot-boundary-v0.6 | 85.2 | 96.7% | 79.7 |

v0.6 was not adopted because its human semantic score missed the predefined 80.0 gate and completeness regressed.

## Key design decisions

1. **No RAG in the initial scope** — isolate generation behavior before adding retrieval complexity.
2. **Structured output** — make findings machine-readable, testable, and reusable.
3. **One controlled local baseline first** — stabilize prompt/schema/evaluation before comparing providers.
4. **Low-randomness settings** — the task is structured analysis, not creative generation.
5. **Few-shot only after measured failures** — semantic boundary examples were more useful than adding more rules.
6. **Evidence-first schema** — require traceable support for material findings and avoid unsupported confidence/severity scoring.
7. **Human-in-the-loop** — the model supports TPM decisions; it does not make final risk, schedule, priority, or client-commitment decisions.

See [`docs/design-decisions.md`](docs/design-decisions.md) for the rationale and trade-offs.

## Repository structure

```text
.
├── src/                         # application, prompts, datasets, runners, evaluators
├── results/
│   ├── smoke_v02..v05/         # early prompt experiments
│   ├── benchmark_v1/           # 30-case development benchmark
│   ├── holdout_v1/             # frozen qwen3:8b final holdout
│   └── model_comparison_v1/    # frozen Gemini comparison, including 20 raw outputs
├── docs/
│   ├── architecture.md
│   ├── design-decisions.md
│   ├── evaluation-methodology.md
│   └── experiment-history.md
├── .env.example
├── .gitignore
├── requirements.txt
└── pyproject.toml
```

Historical Gemini quota-error artifacts are intentionally excluded from the repository; the canonical final 20 successful outputs are retained.

## Setup

Tested during development with Python 3.12.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

For the local model, install Ollama and make `qwen3:8b` available locally.

For Gemini comparison runs:

```bash
export GEMINI_API_KEY="your_key"
```

Never commit a real API key.

## Reproduce evaluations from saved outputs

These commands do **not** call an LLM API and can recompute the objective metrics from saved outputs:

```bash
python -m src.evaluate_smoke
python -m src.benchmark_evaluator_v1
python -m src.benchmark_compare
python -m src.holdout_evaluator_v1
python -m src.model_comparison_evaluator_v1
```

To run new inference, the corresponding local model or API access is required:

```bash
python -m src.holdout_runner_v1
python -m src.gemini_comparison_runner_v1
```

## Operational lessons

The hosted comparison also surfaced production concerns beyond model quality. During the experiment, active Free Tier limits were observed around 5 RPM / 250K TPM / 20 RPD, so the 20-case comparison required multiple quota windows. Infrastructure rate-limit failures were kept separate from model-quality evaluation, and successful outputs were not regenerated for quality reasons.

## Data and privacy

All benchmark and holdout scenarios are synthetic. No employer, client, NDA, personal, or production data is required by this repository.

## Current limitations

- no retrieval or cross-document grounding
- no autonomous action execution
- strict evidence is lexical traceability, not semantic entailment
- some inferred-risk classification errors remain
- hosted-model execution depends on provider quotas and API availability
- semantic review is manual and rubric-based, not an independent human-subject study
- some frozen v0.5/v0.6 few-shot example snippets omit evidence fields even though the Pydantic schema requires evidence; they were not retroactively edited because that would invalidate the frozen benchmark/comparison history

## Possible extension

A natural next step is to extend the same evaluation discipline into a bilingual RAG-based Technical Program Copilot, where retrieval quality, multi-document conflicts, and answer grounding become first-class evaluation targets.