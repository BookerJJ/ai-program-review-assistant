# AI Program Review Assistant

A bilingual LLM application that turns Korean and English project updates into **structured, evidence-linked TPM findings**. The project examines how well a model can extract issues, risks, dependencies, requirement changes, schedule impacts, actions, and uncertainties without inventing missing project facts.

The implementation deliberately uses **directly supplied context** rather than RAG or agents. Its focus is a controlled, measurable sequence: **prompting → structured output → grounding → evidence → evaluation → failure analysis**.

## At a glance

- **Input:** synthetic Korean or English technical-program updates.
- **Output:** a strict Pydantic `ProgramReview` object with `summary`, `issues`, `risks`, `dependencies`, `requirement_changes`, `schedule_impacts`, `actions`, and `uncertainties`. Material findings include supporting source evidence.
- **Models:** Ollama `qwen3:8b` for local prompt development; hosted `gemini-3.8-flash` for a comparison after the task and local holdout were frozen.
- **Evaluation:** execution success, deterministic Structural score, lexical Strict Evidence Traceability, and separately scored semantic review. **No combined accuracy score.**
- **Scope:** no document retrieval, external tools, agentic actions, fine-tuning, or automatic program decisions.

## Evaluation results

Both models were evaluated on the same frozen **20-case bilingual holdout** (10 English and 10 Korean cases), with the same task definitions, golden expectations, output schema, and semantic-review rubric. Gemini did not receive task-specific prompt tuning.

| Metric | qwen3:8b (local) | Gemini 3.8 Flash (hosted) |
|---|---:|---:|
| Successful structured executions | 20/20 | 20/20 |
| Objective Structural | 86.0 | 93.6 |
| Strict Evidence Traceability | 97.5% | 100.0% |
| Human Semantic (rubric-based)* | 85.0 | 94.0 |
| English semantic | 84.0 | 96.0 |
| Korean semantic | 86.0 | 92.0 |
| Average observed latency | 16.861 s | 19.257 s |
| Total reported tokens | 26,958 | 29,999 |

**Interpretation:** These are results for **this frozen TPM extraction task**, not a general model ranking. Gemini scored higher on the three assessed quality dimensions. qwen supports local execution and avoids hosted quota dependence; observed latency was lower on this specific setup. Latency and token totals are descriptive, **not controlled hardware- or tokenizer-equivalent benchmarks**.

\* **Review provenance:** “Human Semantic” is the historical metric name. Case-level rubric scores are saved as CSV. The Gemini scores were prepared through a manual rubric review conducted by an AI assistant and **have not been independently validated by a separate human rater**. Treat the 94.0 value as a provisional, rubric-based assessment—not a blinded or independently adjudicated human benchmark. Reviewer independence for the older qwen scores cannot be established from the archived CSV alone. See [evaluation methodology](docs/evaluation-methodology.md).

### What the metrics do—and do not—measure

- **Execution:** a completed call that returned JSON accepted by the strict output schema; not evidence of semantic accuracy.
- **Structural:** expected category counts and selected field assertions; **excludes** evidence checks.
- **Strict Evidence:** normalized exact/substring match between quoted evidence and the input. It checks **textual traceability, not semantic entailment**.
- **Semantic review:** five 0–2 rubric dimensions—factual correctness, completeness, unsupported-claim control, classification, and meaning preservation.

These dimensions are **not merged into a single accuracy number**.

## Design and architecture

```text
Korean / English project update
            |
            v
   Versioned system prompt
            |
            v
       LLM adapter
      /           \
 Ollama/qwen3:8b   Gemini hosted comparison
      \           /
            v
  Pydantic ProgramReview
            |
            v
    Saved JSON outputs
       |       |       |
       v       v       v
  Structural  Evidence  Rubric-scored
  evaluation traceability semantic review
```

The LLM's role is **decision support**. It may identify and explain findings, evidence, and uncertainty; it does **not** autonomously accept risks, commit dates, change priorities, or approve customer-facing plans.

Prompt iterations moved from baseline extraction to stronger grounding rules and, after observed classification failures, targeted few-shot examples. The frozen prompt is `fewshot-v0.5`. The later v0.6 improved objective measures but was not adopted because its development semantic score (**79.7**) missed the predeclared **80.0** adoption threshold and completeness regressed.

| Development prompt | Structural | Strict Evidence | Human Semantic* |
|---|---:|---:|---:|
| `fewshot-v0.5` | 82.2 | 88.6% | 77.3 |
| `fewshot-boundary-v0.6` | 85.2 | 96.7% | 79.7 |

The 30-case benchmark is a **development set**, not a final unseen test. The frozen 20-case holdout was used for final evaluation; it was subsequently reused for the provider comparison. Scores should not be interpreted as estimates of general production reliability.

## Explore the repository

| Where | What to look for |
|---|---|
| [`src/schemas.py`](src/schemas.py) | Pydantic output contract and evidence requirements |
| [`src/prompts.py`](src/prompts.py) | Prompt evolution and frozen v0.5 instructions |
| [`src/analyzer.py`](src/analyzer.py), [`src/gemini_client.py`](src/gemini_client.py) | Local and hosted model adapters |
| [`src/benchmark_*`](src) | Development cases, expectations, runners, and evaluators |
| [`src/holdout_*`](src) | Frozen holdout data and evaluation logic |
| [`src/model_comparison_*`](src) | Cross-model objective evaluation and semantic review preparation |
| [`results/`](results/README.md) | Frozen model outputs, scored CSVs, objective reports |
| [`docs/architecture.md`](docs/architecture.md) | Architecture and module responsibilities |
| [`docs/design-decisions.md`](docs/design-decisions.md) | Design rationale and trade-offs |
| [`docs/evaluation-methodology.md`](docs/evaluation-methodology.md) | Metrics, review provenance, threats to validity |
| [`docs/experiment-history.md`](docs/experiment-history.md) | Prompt iterations, failure patterns, measured results |
| [`docs/reproducing-results.md`](docs/reproducing-results.md) | Exact offline commands and limitations |

## Quick start

Run commands from the **repository root** with Python 3.12.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
```

The tests inspect **saved synthetic artifacts** and do not invoke an LLM. To regenerate the reported objective metrics from the same saved outputs:

```bash
python -m src.evaluate_smoke
python -m src.benchmark_evaluator_v1
python -m src.benchmark_compare
python -m src.holdout_evaluator_v1
python -m src.model_comparison_evaluator_v1
```

Those scripts recompute **Structural / Strict Evidence**, not manual semantic-review scores; the latter are stored in completed CSVs. The scripts write derived evaluation reports. See [reproduction guide](docs/reproducing-results.md).

### Live inference (optional)

For the local baseline, install [Ollama](https://ollama.com/) and run `ollama pull qwen3:8b`. Then:

```bash
python -m src.run_baseline
```

For Gemini comparison experiments, set `GEMINI_API_KEY` in your environment; do not commit it. **Do not rerun the frozen holdout/comparison runners in the published result directory.** Those scripts are historical experiment entry points with saved canonical outputs and may be quota-limited. Use a separate copy and an independently defined new experiment if further inference is needed.

## Limitations and safety

- **Synthetic data only.** Do not submit actual employer/client/NDA, personal, or sensitive project details to a hosted free-tier service.
- No RAG, cross-document search, autonomous actions, production authorization logic, or deployment UI.
- Strict evidence matching cannot verify whether a cited passage logically supports the conclusion.
- Inferred-risk classification and some cross-category reasoning remain failure modes.
- The two providers have different execution environments, inference settings, token accounting, and quotas.
- The semantic review is rubric-based and not independent expert evaluation; see the reviewer-provenance caveat above.
- Frozen v0.5/v0.6 prompt examples include some snippets without `evidence` fields even though the actual Pydantic output requires evidence. The frozen prompt was **not retroactively modified**, preserving evaluation comparability.

A possible extension would add bilingual retrieval and multi-document grounding, with retrieval failures evaluated separately from extraction failures.

[한국어 요약 / Korean summary](README_KO.md)
