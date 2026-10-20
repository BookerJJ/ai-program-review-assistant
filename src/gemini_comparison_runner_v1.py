import json
import re
import time
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path

from .gemini_client import GeminiClient
from .holdout_cases_v1 import (
    HOLDOUT_CASES,
    validate_holdout_distribution,
)
from .holdout_golden_v1 import (
    validate_golden_expectations,
)
from .prompts import FEWSHOT_SYSTEM_PROMPT_V05
from .schemas import ProgramReview


# ============================================================
# Experiment configuration
# ============================================================

COMPARISON_VERSION = "model-comparison-v1"
HOLDOUT_VERSION = "holdout-v1"
PROMPT_VERSION = "fewshot-v0.5"

PROVIDER = "google"
MODEL = "gemini-3.8-flash"

THINKING_LEVEL = "low"
TEMPERATURE = 0.0

RESULTS_DIR = (
    Path("results")
    / "model_comparison_v1"
    / "gemini_3_8_flash"
)

ATTEMPTS_DIR = (
    RESULTS_DIR
    / "attempts"
)


# Existing successful model outputs are NEVER overwritten.
#
# This is important for evaluation integrity:
# once Gemini has successfully generated an answer for a
# holdout case, that answer becomes the official artifact.
SKIP_EXISTING = True


# ============================================================
# Free Tier rate-limit handling
# ============================================================

# Observed Free Tier limits for the project on 2026-09-13:
# - RPM: 5
# - TPM: 250K
# - RPD: 20
#
# These are experiment-time observations, not permanent Google
# guarantees. Re-check AI Studio before a future rerun.
OBSERVED_FREE_TIER_RPD_LIMIT = 20

# 15 seconds between API calls keeps the run below roughly
# 4 requests/minute and gives some safety margin under 5 RPM.
REQUEST_INTERVAL_SECONDS = 15.0


# If Google does not provide an explicit retry duration,
# use this fallback.
DEFAULT_RATE_LIMIT_WAIT_SECONDS = 30.0


# Add a small buffer on top of Google's requested retry delay.
RATE_LIMIT_BUFFER_SECONDS = 2.0


# Maximum number of API attempts for one case during one run.
#
# Example:
# attempt 1 -> 429
# attempt 2 -> 429
# attempt 3 -> success
MAX_ATTEMPTS_PER_CASE = 4


RETRYABLE_ERROR_TYPES = {
    "RateLimitError",
}

PACIFIC_TZ = ZoneInfo(
    "America/Los_Angeles"
)


# ============================================================
# Runtime state
# ============================================================

# Used to avoid sending API requests too close together.
last_api_call_monotonic: float | None = None


# ============================================================
# Utility functions
# ============================================================

def timestamp() -> str:
    return datetime.now().astimezone().isoformat(
        timespec="seconds"
    )


def result_path_for(
    test_id: str,
) -> Path:

    filename = (
        test_id
        .lower()
        .replace("-", "")
        + ".json"
    )

    return RESULTS_DIR / filename


def load_existing_result(
    path: Path,
) -> dict:

    return json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )


def create_client() -> GeminiClient:

    return GeminiClient(
        model=MODEL,
        thinking_level=THINKING_LEVEL,
        temperature=TEMPERATURE,
    )


# ============================================================
# Rate-limit helpers
# ============================================================

def extract_retry_seconds(
    error_message: str | None,
) -> float:

    """
    Extract Google's suggested retry duration from an error.

    Example:
        "Please retry in 25.079516739s."

    Returns the configured fallback if no duration is found.
    """

    if not error_message:
        return DEFAULT_RATE_LIMIT_WAIT_SECONDS

    match = re.search(
        r"retry in\s+([0-9]+(?:\.[0-9]+)?)s",
        error_message,
        flags=re.IGNORECASE,
    )

    if not match:
        return DEFAULT_RATE_LIMIT_WAIT_SECONDS

    try:
        return float(
            match.group(1)
        )

    except ValueError:
        return DEFAULT_RATE_LIMIT_WAIT_SECONDS


def extract_quota_limit(
    error_message: str | None,
) -> int | None:

    if not error_message:
        return None

    match = re.search(
        r"limit:\s*([0-9]+)",
        error_message,
        flags=re.IGNORECASE,
    )

    if not match:
        return None

    try:
        return int(
            match.group(1)
        )

    except ValueError:
        return None


def is_daily_quota_exhausted(
    error_message: str | None,
) -> bool:
    """
    Detect the experiment's observed Free Tier RPD exhaustion.

    The 2026-09-13 project showed RPD=20 in AI Studio.
    A RateLimitError reporting the same request metric and
    limit=20 is therefore treated as daily quota exhaustion
    for this frozen experiment.
    """

    if not error_message:
        return False

    metric_present = (
        "generate_content_free_tier_requests"
        in error_message
    )

    return (
        metric_present
        and extract_quota_limit(
            error_message
        )
        == OBSERVED_FREE_TIER_RPD_LIMIT
    )


def occurred_on_current_pacific_day(
    timestamp_value: str | None,
) -> bool:

    if not timestamp_value:
        return False

    try:
        event_time = datetime.fromisoformat(
            timestamp_value
        )
    except ValueError:
        return False

    if event_time.tzinfo is None:
        return False

    event_day = (
        event_time
        .astimezone(PACIFIC_TZ)
        .date()
    )

    current_day = (
        datetime.now(PACIFIC_TZ)
        .date()
    )

    return event_day == current_day


def wait_for_request_interval() -> None:

    """
    Ensure API calls are spaced apart.

    Existing saved results do not count as API calls.
    """

    global last_api_call_monotonic

    if last_api_call_monotonic is None:
        return

    elapsed = (
        time.monotonic()
        - last_api_call_monotonic
    )

    remaining = (
        REQUEST_INTERVAL_SECONDS
        - elapsed
    )

    if remaining <= 0:
        return

    print(
        "\nFree Tier pacing: "
        f"waiting {remaining:.1f} seconds "
        "before next API call..."
    )

    time.sleep(
        remaining
    )


def mark_api_call_started() -> None:

    global last_api_call_monotonic

    last_api_call_monotonic = (
        time.monotonic()
    )


# ============================================================
# Attempt archive
# ============================================================

def next_attempt_archive_path(
    test_id: str,
) -> Path:

    ATTEMPTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    base_name = (
        test_id
        .lower()
        .replace("-", "")
    )

    attempt_number = 1

    while True:

        archive_path = (
            ATTEMPTS_DIR
            / (
                f"{base_name}"
                f"_attempt{attempt_number}"
                "_error.json"
            )
        )

        if not archive_path.exists():
            return archive_path

        attempt_number += 1


def archive_error_output(
    output: dict,
) -> Path:

    """
    Save an API/infrastructure failure separately.

    These attempts are retained for operational evidence,
    but they are NOT treated as model-quality outputs.
    """

    archive_path = (
        next_attempt_archive_path(
            output["test_case"]
        )
    )

    archive_path.write_text(
        json.dumps(
            output,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    return archive_path


def archive_existing_retryable_result(
    path: Path,
    existing: dict,
) -> Path:

    """
    Move a previously saved retryable error out of the
    canonical result location.

    This allows the case to be retried while preserving
    the original infrastructure failure.
    """

    archive_path = (
        next_attempt_archive_path(
            existing["test_case"]
        )
    )

    path.replace(
        archive_path
    )

    return archive_path


# ============================================================
# Case execution
# ============================================================

def run_case_once(
    client: GeminiClient,
    test_case: dict,
    case_number: int,
    total_cases: int,
    attempt_number: int,
) -> dict:

    test_id = test_case["id"]

    print("\n" + "=" * 70)

    print(
        f"[{case_number}/{total_cases}] "
        f"{test_id} | "
        f"{test_case['language']} | "
        f"{test_case['scenario_type']}"
    )

    print(
        f"Target: "
        f"{test_case['primary_target']}"
    )

    print(
        f"API attempt: "
        f"{attempt_number}"
    )

    print("=" * 70)

    started_at = timestamp()

    wait_for_request_interval()

    mark_api_call_started()

    try:

        result, metadata = (
            client.generate_structured(
                input_text=test_case[
                    "input"
                ],
                system_prompt=(
                    FEWSHOT_SYSTEM_PROMPT_V05
                ),
                response_model=ProgramReview,
            )
        )

        output = {
            "comparison_version":
                COMPARISON_VERSION,

            "holdout_version":
                HOLDOUT_VERSION,

            "prompt_version":
                PROMPT_VERSION,

            "provider":
                PROVIDER,

            "model":
                MODEL,

            "test_case":
                test_id,

            "language":
                test_case[
                    "language"
                ],

            "scenario_type":
                test_case[
                    "scenario_type"
                ],

            "primary_target":
                test_case[
                    "primary_target"
                ],

            "status":
                "success",

            "api_attempt":
                attempt_number,

            "started_at":
                started_at,

            "completed_at":
                timestamp(),

            "metadata":
                metadata,

            "result":
                result.model_dump(),
        }

    except Exception as error:

        output = {
            "comparison_version":
                COMPARISON_VERSION,

            "holdout_version":
                HOLDOUT_VERSION,

            "prompt_version":
                PROMPT_VERSION,

            "provider":
                PROVIDER,

            "model":
                MODEL,

            "test_case":
                test_id,

            "language":
                test_case[
                    "language"
                ],

            "scenario_type":
                test_case[
                    "scenario_type"
                ],

            "primary_target":
                test_case[
                    "primary_target"
                ],

            "status":
                "error",

            "api_attempt":
                attempt_number,

            "started_at":
                started_at,

            "completed_at":
                timestamp(),

            "error_type":
                type(error).__name__,

            "error_message":
                str(error),
        }

    return output


def run_case_with_retry(
    client: GeminiClient,
    test_case: dict,
    case_number: int,
    total_cases: int,
) -> dict:

    """
    Retry only recoverable infrastructure rate-limit failures.

    A successfully generated model answer is never regenerated.
    Daily Free Tier quota exhaustion is not retried in-process.
    """

    for attempt_number in range(
        1,
        MAX_ATTEMPTS_PER_CASE + 1,
    ):

        output = run_case_once(
            client=client,
            test_case=test_case,
            case_number=case_number,
            total_cases=total_cases,
            attempt_number=attempt_number,
        )

        if (
            output.get("status")
            == "success"
        ):
            return output

        error_type = (
            output.get(
                "error_type"
            )
        )

        if (
            error_type
            not in RETRYABLE_ERROR_TYPES
        ):

            print(
                "\nNon-retryable error."
            )

            print(
                f"{error_type}: "
                f"{output.get('error_message')}"
            )

            return output

        error_message = (
            output.get(
                "error_message"
            )
        )

        # Daily RPD exhaustion cannot be repaired by sleeping for
        # a few seconds. Preserve this failure as the canonical
        # infrastructure artifact and stop the run in main().
        if is_daily_quota_exhausted(
            error_message
        ):
            output["quota_scope"] = (
                "daily_rpd"
            )

            print(
                "\nDaily Free Tier quota "
                "exhausted. No in-process retry "
                "will be attempted."
            )

            return output

        # The final failed attempt is returned as the canonical
        # error artifact. Only attempts that will actually be
        # followed by another API call are archived here. This
        # avoids duplicating the last failure in both attempts/
        # and the canonical case file.
        if (
            attempt_number
            >= MAX_ATTEMPTS_PER_CASE
        ):

            print(
                "Maximum attempts reached."
            )

            return output

        archive_path = (
            archive_error_output(
                output
            )
        )

        print(
            "\nRate limit encountered."
        )

        print(
            f"Archived infrastructure failure: "
            f"{archive_path}"
        )

        retry_seconds = (
            extract_retry_seconds(
                error_message
            )
        )

        wait_seconds = (
            retry_seconds
            + RATE_LIMIT_BUFFER_SECONDS
        )

        print(
            "Google requested retry after "
            f"{retry_seconds:.1f} seconds."
        )

        print(
            "Waiting "
            f"{wait_seconds:.1f} seconds "
            "before retry..."
        )

        time.sleep(
            wait_seconds
        )

        global last_api_call_monotonic

        last_api_call_monotonic = None

    raise RuntimeError(
        "Unexpected retry-loop exit."
    )


# ============================================================
# Canonical result storage
# ============================================================

def save_result(
    output: dict,
) -> Path:

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        result_path_for(
            output["test_case"]
        )
    )

    if output_path.exists():

        raise FileExistsError(
            "Refusing to overwrite existing "
            "Gemini comparison result: "
            f"{output_path}"
        )

    output_path.write_text(
        json.dumps(
            output,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    return output_path


def collect_canonical_results() -> list[dict]:
    """
    Load the current canonical artifact for every holdout case
    that has one. This makes partial summaries reflect disk state
    rather than only the current Python process.
    """

    results = []

    for case in HOLDOUT_CASES:
        path = result_path_for(
            case["id"]
        )

        if not path.exists():
            continue

        results.append(
            load_existing_result(
                path
            )
        )

    return results


def archived_error_artifact_counts() -> dict:
    """
    Count preserved error artifacts by case.

    Historical artifacts created before this audit may contain
    duplicate copies of a final failed attempt, so these counts
    are diagnostic artifact counts, not guaranteed API-call counts.
    """

    counts: dict[str, int] = {}

    if not ATTEMPTS_DIR.exists():
        return counts

    for path in ATTEMPTS_DIR.glob(
        "h*_attempt*_error.json"
    ):
        match = re.match(
            r"(h\d+)_attempt",
            path.name,
            flags=re.IGNORECASE,
        )

        if not match:
            continue

        raw_id = match.group(1)
        test_id = (
            raw_id[0].upper()
            + "-"
            + raw_id[1:]
        )

        counts[test_id] = (
            counts.get(
                test_id,
                0,
            )
            + 1
        )

    return dict(
        sorted(
            counts.items()
        )
    )


# ============================================================
# Summary construction
# ============================================================

def build_summary(
    all_results: list[dict],
    comparison_started_at: str,
) -> dict:

    successful = [
        result
        for result in all_results
        if result.get("status")
        == "success"
    ]

    failed = [
        result
        for result in all_results
        if result.get("status")
        != "success"
    ]

    latencies = [
        result["metadata"][
            "latency_seconds"
        ]
        for result in successful
        if result.get("metadata")
        and result["metadata"].get(
            "latency_seconds"
        ) is not None
    ]

    total_input_tokens = sum(
        (
            result["metadata"].get(
                "input_tokens",
                0,
            )
            or 0
        )
        for result in successful
    )

    total_output_tokens = sum(
        (
            result["metadata"].get(
                "output_tokens",
                0,
            )
            or 0
        )
        for result in successful
    )

    total_thinking_tokens = sum(
        (
            result["metadata"].get(
                "thinking_tokens",
                0,
            )
            or 0
        )
        for result in successful
    )

    total_tokens = sum(
        (
            result["metadata"].get(
                "total_tokens",
                0,
            )
            or 0
        )
        for result in successful
    )

    same_run_retry_counts = {
        result["test_case"]:
            max(
                (
                    result.get(
                        "api_attempt",
                        1,
                    )
                    - 1
                ),
                0,
            )
        for result in successful
        if result.get(
            "api_attempt",
            1,
        ) > 1
    }

    present_case_ids = {
        result.get("test_case")
        for result in all_results
        if result.get("test_case")
    }

    pending_case_ids = [
        case["id"]
        for case in HOLDOUT_CASES
        if case["id"]
        not in present_case_ids
    ]

    by_language = {}

    languages = sorted(
        {
            case["language"]
            for case in HOLDOUT_CASES
        }
    )

    for language in languages:

        expected_ids = {
            case["id"]
            for case in HOLDOUT_CASES
            if case["language"]
            == language
        }

        language_results = [
            result
            for result in all_results
            if result.get(
                "test_case"
            )
            in expected_ids
        ]

        language_success = sum(
            1
            for result in language_results
            if result.get("status")
            == "success"
        )

        language_failed = sum(
            1
            for result in language_results
            if result.get("status")
            != "success"
        )

        by_language[
            language
        ] = {
            "total":
                len(expected_ids),

            "artifacts_present":
                len(language_results),

            "success":
                language_success,

            "failed":