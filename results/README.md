# Result Artifacts

- `smoke_v02` … `smoke_v05`: early 5-case prompt iterations.
- `benchmark_v1`: 30-case development benchmark. `comparison/` contains the clean recalculated v0.5 vs v0.6 comparison.
- `holdout_v1`: frozen 20-case local qwen3:8b holdout, objective evaluation, and completed semantic-review artifacts.
- `model_comparison_v1/gemini_3_8_flash`: final 20 canonical Gemini outputs, objective evaluation, and completed semantic-review artifacts.

Historical Gemini quota-error files under `attempts/` are intentionally excluded. They are operational diagnostics, not quality results.