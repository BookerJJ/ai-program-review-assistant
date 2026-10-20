"""Offline smoke checks for immutable synthetic experiment artifacts."""
import csv
import json
import unittest
from pathlib import Path

from src.schemas import ProgramReview

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"


class FrozenArtifactIntegrity(unittest.TestCase):
    def _json(self, relative):
        return json.loads((RESULTS / relative).read_text(encoding="utf-8"))

    def test_frozen_outputs_validate_against_schema(self):
        stages = [
            ("benchmark_v1/fewshot_v05", "tc", 30, "fewshot-v0.5"),
            ("benchmark_v1/fewshot_v06", "tc", 30, "fewshot-boundary-v0.6"),
            ("holdout_v1/fewshot_v05", "h", 20, "fewshot-v0.5"),
            ("model_comparison_v1/gemini_3_8_flash", "h", 20, "fewshot-v0.5"),
        ]
        for directory, prefix, n, prompt in stages:
            for i in range(1, n + 1):
                case = f"{prefix}{i:03d}.json"
                with self.subTest(stage=directory, case=case):
                    record = self._json(f"{directory}/{case}")
                    self.assertEqual(record["status"], "success")
                    self.assertEqual(record["prompt_version"], prompt)
                    ProgramReview.model_validate(record["result"])

    def test_final_objective_reports_match_published_values(self):
        reports = [
            ("benchmark_v1/evaluation/benchmark_objective_report.json", 30, 82.2, 0.886),
            ("holdout_v1/evaluation/holdout_objective_report.json", 20, 86.0, 0.975),
            ("model_comparison_v1/gemini_3_8_flash/evaluation/gemini_objective_report.json", 20, 93.6, 1.0),
        ]
        for path, n, structural, evidence in reports:
            with self.subTest(report=path):
                o = self._json(path)["overall"]
                self.assertEqual(o["cases"], n)
                self.assertAlmostEqual(o["average_structural_score"], structural)
                self.assertAlmostEqual(o["average_evidence_traceability"], evidence)

    def test_completed_semantic_csvs_have_full_case_coverage(self):
        review_csvs = [
            ("benchmark_v1/human_review/benchmark_human_evaluation_completed.csv", 30),
            ("benchmark_v1/human_review_v06/benchmark_human_evaluation_v06_completed.csv", 30),
            ("holdout_v1/human_review/holdout_human_evaluation_completed.csv", 20),
            ("model_comparison_v1/gemini_3_8_flash/human_review/gemini_human_review_scored.csv", 20),
        ]
        for path, count in review_csvs:
            with self.subTest(review_csv=path):
                with (RESULTS / path).open(encoding="utf-8-sig", newline="") as f:
                    rows = list(csv.DictReader(f))
                self.assertEqual(len(rows), count)
                self.assertTrue(all(r["semantic_score"] != "" for r in rows))


if __name__ == "__main__":
    unittest.main()
