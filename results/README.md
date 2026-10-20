# Result Artifacts

- `smoke_v02` … `smoke_v05`: early 5-case prompt iterations.
- `benchmark_v1`: 30-case development benchmark. `comparison/` contains the clean recalculated v0.5 vs v0.6 comparison.
- `holdout_v1`: frozen 20-case local qwen3:8b holdout, objective evaluation, and completed semantic-review artifacts.
- `model_comparison_v1/gemini_3_8_flash`: final 20 canonical Gemini outputs, objective evaluation, and completed semantic-review artifacts.

Historical Gemini quota-error files under `attempts/` are intentionally excluded. They are operational diagnostics, not quality results.

## Reading the artifacts

Each canonical case JSON stores the source case identifier, prompt/model version, execution status, generation metadata, and structured `result`. The three final objective report paths are:

- `benchmark_v1/evaluation/benchmark_objective_report.json` — 30-case v0.5 development benchmark;
- `holdout_v1/evaluation/holdout_objective_report.json` — 20-case frozen local holdout;
- `model_comparison_v1/gemini_3_8_flash/evaluation/gemini_objective_report.json` — 20-case hosted comparison.

The `human_review/` folders contain the individual semantic ratings and notes. The label **Human Semantic** denotes the original rubric's name; the Gemini scores were assigned through an assistant-led manual rubric review, **not** an independently verified human panel.

**Do not** combine Structural and Strict Evidence, assume 20/20 execution means perfect accuracy, or interpret strict substring evidence as semantic proof. The original result JSONs should remain frozen; offline evaluators may recreate derived CSV/JSON files.

See [`../docs/reproducing-results.md`](../docs/reproducing-results.md) for steps and caveats.
