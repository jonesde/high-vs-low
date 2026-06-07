#!/usr/bin/env python3
"""
batch-sqlite.py

Implements the "Database Delegation Workflow" from
skills/high-vs-low/references/batch-handling.md.

Follows the exact steps:
  1. Discover schema
  2. Preview records
  3. Delegate evaluation per-record (calls AI endpoint)
  4. Delegate review per-record (calls AI endpoint)
  5. Report summary

Usage:
  python3 batch-sqlite.py <db_path> [options]

Options:
  --limit N          Process only the first N records (default: all)
  --start-id ID      Start from this record ID (default: minimum ID)
  --endpoint URL     OpenAI-compatible endpoint URL (default: env OPENAI_ENDPOINT or http://127.0.0.1:1234/v1)
  --api-key KEY      API key (default: env OPENAI_API_KEY)
  --model MODEL      Model name (default: qwen3.6-27b-mtp)
  --stub             Use a stub AI that returns a constant response
  --skip-review      Skip the review phase
  --skip-evaluation  Skip the evaluation phase
  --dry-run          Print what would be done without modifying the database
  --reset            Clean out evaluation/count/score columns before processing
  --reset-only       Only clean out evaluation/count/score columns and exit
  --where CLAUSE     SQL WHERE clause (without 'WHERE') to filter records
  --table TABLE_NAME Table name to use (default: auto-detect if DB has exactly one table)
  --document-column COLUMN_NAME Column containing the document text (default: doc_text)
  --detailed           produce detailed evaluation reports (default: basic)
"""

import argparse
from datetime import datetime
import json
import logging
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request
from typing import Callable, NamedTuple, Optional

logger = logging.getLogger("batch-sqlite")

def setup_logging(db_path: str) -> None:
    """Configure logging to write to both stdout and a file derived from db_path.

    The log file is named by replacing the .db extension with .eval.%Y-%m-%d-%H-%M.log.
    """
    # Build log file path
    base, _ = os.path.splitext(db_path)
    ts = datetime.now().strftime("%Y-%m-%d-%H-%M")
    log_file = base + f".eval.{ts}.log"

    root = logging.getLogger("batch-sqlite")
    root.setLevel(logging.DEBUG)

    # Prevent duplicate handlers on repeated calls
    if root.handlers:
        return

    fmt = logging.Formatter("%(asctime)s  %(levelname)-7s  %(message)s", datefmt="%H:%M:%S")

    # stdout handler — INFO and above
    sh = logging.StreamHandler(sys.stdout)
    sh.setLevel(logging.INFO)
    sh.setFormatter(fmt)
    root.addHandler(sh)

    # file handler — DEBUG and above
    fh = logging.FileHandler(log_file, mode="a", encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)
    root.addHandler(fh)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEFAULT_ENDPOINT = "http://127.0.0.1:1234/v1"
# Not a URL in --endpoint? add the prefix and suffix to make a URL (NOTE: defaults to local friendly settings for LM Studio)
DEFAULT_EP_NO_URL_PREFIX = "http://"
DEFAULT_EP_NO_URL_SUFFIX = ":1234/v1"

DEFAULT_DOCUMENTS_TABLE = "documents"
DEFAULT_DOCUMENT_COLUMN = "doc_text"
# TODO: use these in parser.add_argument() calls to add options, then use those from args like args.document_column
DEFAULT_ID_COLUMN = "id"
DEFAULT_EVALUTION_COL = "evaluation"
DEFAULT_COUNT_HL_COLUMN = "count_hl"
DEFAULT_COUNT_LL_COLUMN = "count_ll"
DEFAULT_SCORE_COLUMN = "score"

_REPORT_TITLE_PREFIX = "# High Law vs Low Law Alignment Evaluation"

# ---------------------------------------------------------------------------
# Stubs for --stubs
# ---------------------------------------------------------------------------

_STUB_EVAL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test-report.md")
def _load_stub_evaluation() -> str:
    """Load the stub evaluation report from test-report.md in the same directory."""
    with open(_STUB_EVAL_PATH, "r") as f:
        return f.read()

STUB_REVIEW = """# Review Result: STUB_REVIEW_RESPONSE

## CHANGES SUMMARY

**Original counts**: HL=13, LL=0, Score=10.0
**Updated counts**: HL=3, LL=3, Score=0.0

- STATEMENTS_ADDED
- STATEMENTS_REMOVED
- Moved 3 statements from HL to LL
- Removed 7 invalid HL statements
"""

# Unique divider the LLM emits after a regenerated evaluation report.
# Used by parse_review_updated_eval to reliably extract the full report.
EVAL_REPORT_END_MARKER = "--- END OF UPDATED EVALUATION REPORT ---"

STUB_REVIEW_WITH_CHANGES = f"""# High Law vs Low Law Alignment Evaluation: STUB_DOCUMENT

## Overview

Updated stub evaluation.

---

## Key Topics

1. **Authority and Power: Obedience**
2. **Justice and Punishment: Divine Justice**
3. **Mercy and Compassion: Forgiveness**
4. **Autonomy and Consent: Free Will**
5. **Community and Belonging: Unity**

---

## Statement Quotes

### High Law Aligned (3 statements)

| # | Location | Rules | Decision Notes | Key Topics | Speaker | Stance Quote | Principle Quote |
|---| -------- | ----- | -------------- | ---------- | ------- | ------------ | --------------- |
| 1 | L5 | 6-HL,37-HL | HL | Authority and Power: Obedience | Author | "each person must choose for themselves" | "individual agency and choice" |
| 2 | L12 | 26-HL,5-HL | HL | Mercy and Compassion: Forgiveness | Author | "we must show mercy to all" | "compassion for the suffering" |
| 3 | L25 | 6-HL | HL (added during review) | Autonomy and Consent: Free Will | Author | "this was missed before" | "newly added statement" |

### Low Law Aligned (3 statements)

| # | Location | Rules | Decision Notes | Key Topics | Speaker | Stance Quote | Principle Quote |
|---| -------- | ----- | -------------- | ---------- | ------- | ------------ | --------------- |
| 1 | L8 | 17-LL,19-LL | LL | Authority and Power: Obedience | Author | "you must obey or face consequences" | "obey under threat of punishment" |
| 2 | L15 | 25-LL,27-LL | LL | Justice and Punishment: Divine Justice | Author | "the wicked shall be punished" | "punishment for transgression" |
| 3 | L20 | 34-LL,35-LL | LL | Community and Belonging: Unity | Author | "those who do not conform will be cast out" | "conformity to the standard" |

---

## Scoring Summary

| Category | Count | Percentage |
| -------- | ----- | ---------- |
| High Law Aligned | 3 | 50.0% |
| Low Law Aligned | 3 | 50.0% |
| **Total** | **6** | **100%** |

**Score**: ((50.0 - 50.0) / 10) = **0.0**

---

## Key Topic Score Table

| Key Topic | High # | Low # | Score |
| --------- | ------ | ----- | ----- |
| Authority and Power: Obedience | 1 | 1 | 0.0 |
| Justice and Punishment: Divine Justice | 0 | 1 | -10.0 |
| Mercy and Compassion: Forgiveness | 1 | 0 | 10.0 |
| Autonomy and Consent: Free Will | 1 | 0 | 10.0 |
| Community and Belonging: Unity | 0 | 1 | -10.0 |

{EVAL_REPORT_END_MARKER}

## CHANGES SUMMARY

**Original counts**: HL=13, LL=0, Score=10.0
**Updated counts**: HL=3, LL=3, Score=0.0

- STATEMENTS_ADDED
- STATEMENTS_REMOVED
- Moved 3 statements from HL to LL
- Removed 7 invalid HL statements
"""


# ---------------------------------------------------------------------------
# OpenAI-compatible client
# ---------------------------------------------------------------------------

class ChatResult(NamedTuple):
    """Result from an AI chat call with content and usage metadata."""
    content: str
    elapsed: float = 0.0
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    reasoning_tokens: Optional[int] = None
    first_token_elapsed: Optional[float] = None

ProgressCallback = Callable[[int, str, float], None]


def print_progress(char_count: int, content_so_far: str, start_time: float) -> None:
    """Print a single-line progress indicator with token count, elapsed time, and recent text.
    Refreshes at most once per second.
    """
    global _LAST_PROGRESS_TIME
    now = time.monotonic()
    # Skip if less than 1 second since last refresh
    if now - _LAST_PROGRESS_TIME < 1.0:
        return
    _LAST_PROGRESS_TIME = now

    term_width = _term_width()
    # Elapsed time as MM:SS
    elapsed = now - start_time
    mins = int(elapsed) // 60
    secs = int(elapsed) % 60
    # Left side: "MM:SS thinking..." while waiting, then "MM:SS NNN tokens | "
    if char_count == 0:
        left = f" {mins:02d}:{secs:02d} (reading & reasoning...) | "
    else:
        left = f" {mins:02d}:{secs:02d} chars {char_count} | "
    # Available space for text (leave 1 char margin)
    text_width = max(10, term_width - len(left) - 1)
    # Collapse newlines so embedded \n don't break the single-line display
    flat = content_so_far.replace("\r", "").replace("\n", " ")
    # Take the most recent characters that fit
    recent = flat[-(text_width + 20):]
    recent = recent[-text_width:]
    # Clear the line and print
    sys.stdout.write("\r" + " " * term_width + "\r" + left + recent)
    sys.stdout.flush()


_TERM_WIDTH: int = 0
_LAST_PROGRESS_TIME: float = 0.0
_WAIT_THREAD: Optional[threading.Thread] = None
_WAIT_THREAD_STOP: threading.Event = threading.Event()


def _wait_timer_loop(start_time: float) -> None:
    """Background thread that keeps the progress line visible while waiting for tokens."""
    while not _WAIT_THREAD_STOP.is_set():
        print_progress(0, "", start_time)
        # Sleep in small increments so we stop quickly when first token arrives
        for _ in range(10):
            if _WAIT_THREAD_STOP.is_set():
                break
            time.sleep(0.1)


def start_wait_timer(start_time: float) -> None:
    """Start a background thread that keeps the progress line ticking while waiting."""
    global _WAIT_THREAD, _WAIT_THREAD_STOP
    _WAIT_THREAD_STOP.clear()
    _WAIT_THREAD = threading.Thread(target=_wait_timer_loop, args=(start_time,), daemon=True)
    _WAIT_THREAD.start()


def stop_wait_timer() -> None:
    """Stop the background wait timer thread."""
    global _WAIT_THREAD
    _WAIT_THREAD_STOP.set()
    if _WAIT_THREAD is not None:
        _WAIT_THREAD.join(timeout=2.0)
        _WAIT_THREAD = None


def make_streaming_callback(progress_cb: ProgressCallback) -> tuple:
    """Create a callback wrapper that starts the wait timer and stops it on first token.

    Returns (start_fn, wrapped_callback) where:
      - start_fn(start_time) kicks off the background timer thread
      - wrapped_callback replaces the original progress_cb; stops the timer on first call
    """
    first = [True]  # mutable flag

    def start_fn(start_time: float) -> None:
        # Reset _LAST_PROGRESS_TIME so the timer prints immediately
        global _LAST_PROGRESS_TIME
        _LAST_PROGRESS_TIME = 0.0
        start_wait_timer(start_time)

    def wrapped(char_count: int, content_so_far: str, start_time: float) -> None:
        if first[0]:
            first[0] = False
            stop_wait_timer()
            # Reset so the first real callback prints immediately
            global _LAST_PROGRESS_TIME
            _LAST_PROGRESS_TIME = 0.0
        progress_cb(char_count, content_so_far, start_time)

    return start_fn, wrapped


def _term_width() -> int:
    """Cached terminal width to avoid repeated syscalls."""
    global _TERM_WIDTH
    if _TERM_WIDTH == 0:
        _TERM_WIDTH = shutil.get_terminal_size(fallback=(180, 24)).columns
    return _TERM_WIDTH


def print_progress_done() -> None:
    """Clear the progress line and move to next line."""
    sys.stdout.write("\r" + " " * _term_width() + "\r\n")
    sys.stdout.flush()


class OpenAIClient:
    """Minimal OpenAI-compatible chat completions client using urllib."""

    def __init__(self, endpoint, api_key, model=""):
        self.endpoint = endpoint.rstrip("/")
        self.api_key = api_key
        self.model = model

    def chat(self, system_prompt, user_prompt):
        """Send a chat completion request and return ChatResult(content, usage)."""
        url = f"{self.endpoint}/chat/completions"
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "reasoning_effort": "high",
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )
        start = time.monotonic()
        try:
            with urllib.request.urlopen(req, timeout=1800) as resp:
                body = json.loads(resp.read().decode("utf-8"))
            elapsed = time.monotonic() - start
            content = body["choices"][0]["message"]["content"]
            usage = body.get("usage", {})
            usage_details = usage.get("completion_tokens_details", {})
            return ChatResult(
                content=content,
                elapsed=elapsed,
                prompt_tokens=usage.get("prompt_tokens"),
                completion_tokens=usage.get("completion_tokens"),
                total_tokens=usage.get("total_tokens"),
                reasoning_tokens=usage_details.get("reasoning_tokens"),
            )
        except urllib.error.HTTPError as exc:
            elapsed = time.monotonic() - start
            error_body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"HTTP {exc.code} from {url} ({elapsed:.1f}s): {error_body}"
            ) from exc


    def chat_stream(self, system_prompt, user_prompt, progress_cb=None):
        """Send a streaming chat completion request.

        Uses SSE streaming to show progress as tokens arrive.
        progress_cb(char_count, content_so_far) is called per chunk.
        Returns ChatResult with full content and usage.
        """
        url = f"{self.endpoint}/chat/completions"
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "reasoning_effort": "high",
            "stream": True,
            "stream_options": {"include_usage": True},
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )
        start = time.monotonic()
        try:
            with urllib.request.urlopen(req, timeout=1800) as resp:
                full_content = []
                prompt_tokens = None
                completion_tokens = None
                total_tokens = None
                reasoning_tokens = None
                char_count = 0
                first_token_time = None

                # Read SSE stream line by line
                for raw_line in resp:
                    line = raw_line.decode("utf-8").rstrip("\n")
                    if not line or not line.startswith("data: "):
                        continue
                    data_str = line[6:]  # strip "data: "
                    if data_str == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data_str)
                    except json.JSONDecodeError:
                        continue

                    # Extract delta content
                    choices = chunk.get("choices", [])
                    for choice in choices:
                        delta = choice.get("delta", {})
                        delta_content = delta.get("content")
                        if delta_content:
                            if first_token_time is None:
                                first_token_time = time.monotonic() - start
                            full_content.append(delta_content)
                            if progress_cb:
                                # Count actual words in accumulated content as token proxy
                                char_count = len("".join(full_content).split())
                                progress_cb(char_count, "".join(full_content), start)

                    # Extract usage from final chunk (has content = None)
                    usage = chunk.get("usage")
                    if usage:
                        prompt_tokens = usage.get("prompt_tokens")
                        completion_tokens = usage.get("completion_tokens")
                        total_tokens = usage.get("total_tokens")
                        cd = usage.get("completion_tokens_details", {})
                        reasoning_tokens = cd.get("reasoning_tokens")

                elapsed = time.monotonic() - start
                content = "".join(full_content)

                # If no usage in stream, try to get it (some endpoints don't send it)
                if completion_tokens is None:
                    completion_tokens = char_count

                # NOTE: remember to comment this out after using to debug or whatever
                # print(f"API response in {elapsed:.1f}s\nUSAGE: {usage}\nCHUNK: {chunk}\nCONTENT: {content}")

                return ChatResult(content=content, elapsed=elapsed, prompt_tokens=prompt_tokens, completion_tokens=completion_tokens,
                    total_tokens=total_tokens, reasoning_tokens=reasoning_tokens, first_token_elapsed=first_token_time)
        except urllib.error.HTTPError as exc:
            elapsed = time.monotonic() - start
            error_body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"HTTP {exc.code} from {url} ({elapsed:.1f}s): {error_body}"
            ) from exc


class StubClient:
    """Stub that returns constant responses for testing."""

    def __init__(self):
        self.call_count = 0
        self.review_call_count = 0

    def chat(self, system_prompt, user_prompt):
        self.call_count += 1
        # Distinguish by user prompt — system prompts now both contain SKILL.md
        if user_prompt.lower().startswith("review"):
            self.review_call_count += 1
            # First review call: report changes (triggers re-execution loop)
            # Subsequent review calls: no changes (exits loop)
            if self.review_call_count == 1:
                content = STUB_REVIEW_WITH_CHANGES
            else:
                content = STUB_REVIEW
        else:
            content = _load_stub_evaluation()
        return ChatResult(
            content=content,
            elapsed=0.01,
            prompt_tokens=100,
            completion_tokens=200,
            total_tokens=300,
            reasoning_tokens=0,
        )

    def chat_stream(self, system_prompt, user_prompt, progress_cb=None):
        self.call_count += 1
        if user_prompt.lower().startswith("review"):
            self.review_call_count += 1
            if self.review_call_count == 1:
                content = STUB_REVIEW_WITH_CHANGES
            else:
                content = STUB_REVIEW
        else:
            content = _load_stub_evaluation()
        # Simulate streaming in chunks
        chunk_size = 50
        start = time.monotonic()
        for i in range(0, len(content), chunk_size):
            chunk = content[i:i + chunk_size]
            if progress_cb:
                char_count = len(content[:i + len(chunk)].split())
                progress_cb(char_count, content[:i + len(chunk)], start)
            time.sleep(0.001)
        return ChatResult(
            content=content,
            elapsed=0.01,
            prompt_tokens=100,
            completion_tokens=200,
            total_tokens=300,
            reasoning_tokens=0,
            first_token_elapsed=0.005,
        )

# ---------------------------------------------------------------------------
# Prompt builders
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Prompt builders — load skill files dynamically
# ---------------------------------------------------------------------------

_SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def _read_skill_file(relative_path):
    """Read a file from the skill directory."""
    path = os.path.join(_SKILL_DIR, relative_path)
    if not os.path.exists(path):
        logger.warning("Skill file not found: %s", path)
        return ""
    with open(path, "r", encoding="utf-8") as fl:
        return fl.read()


def build_evaluation_system_prompt(is_detailed):
    """Build evaluation system prompt: SKILL.md + minimal instructions."""
    skill_md = _read_skill_file("SKILL.md")

    if is_detailed:
        extra = (
            "\n\n## Report Type: DETAILED\n\n"
            "Produce a **DETAILED** evaluation report. Include ALL sections from the Report Specification."
        )
    else:
        extra = (
            "\n\n## Report Type: BASIC\n\n"
            "Produce a **basic/score** evaluation report. Do *not* include the detailed sections. Stop after the *Key Topic Score Table* section."
        )

    instructions = (
        "\n\n# Task\n\n"
        "You are a High Law vs Low Law alignment evaluator.\n\n"
        "Evaluate the provided document text by following the Evaluation Protocol "
        "and Report Specification from the skill file above.\n"
        f"{extra}\n\n"
        "Execute the Self-Verification and Post-Report Self-Check before emitting the final report."
    )

    return skill_md + instructions


def build_evaluation_user_prompt(doc_text, doc_title):
    return f"""Evaluate the following document{" titled \"" + doc_title + "\"" if doc_title else ""} for High Law vs Low Law Alignment.
--- BEGIN Document Text ---
{doc_text}
--- END Document Text ---

Produce the evaluation report by following the instructions in the **high-vs-low** skill.
"""


def build_review_system_prompt():
    """Build review system prompt: SKILL.md + review checklist + minimal instructions."""
    skill_md = _read_skill_file("SKILL.md")
    review_md = _read_skill_file("references/report-review.md")

    instructions = (
        "\n\n# Task\n\n"
        "You are a High Law vs Low Law evaluation report reviewer.\n\n"
        "Review the provided evaluation report against the original document text.\n"
        "1. Execute the Report Review Checklist from the reference file above, all included instructions in exact order.\n"
        "2. Do NOT verify the DETAILED sections if they are not present, and do NOT generate the DETAILED sections if they are not present.\n"
        "3. If changes are needed, describe them clearly with original and updated counts. If no changes are needed, state that explicitly.\n"
        "4. If you made any changes, regenerate the entire updated evaluation report.\n"
        "5. If you regenerated an updated evaluation report, **ALWAYS** emit the following marker **EXACTLY** on its own line:\n"
        f"```\n{EVAL_REPORT_END_MARKER}\n```\n"
        "This marker tells the parser where the report ends and the summary begins.\n"
        "6. After the marker, include a CHANGES SUMMARY section:\n"
        "- Original counts: HL=N, LL=N, Score=X.X\n"
        "- Updated counts: HL=N, LL=N, Score=X.X (same if no changes)\n"
        "- If and **ONLY** if you added any statements then emit the EXACT text marker 'STATEMENTS_ADDED'\n"
        "- If and **ONLY** if you moved any statements between high/low categories then emit the EXACT text marker 'STATEMENTS_MOVED'\n"
        "- If and **ONLY** if you removed any statements then emit the EXACT text marker 'STATEMENTS_REMOVED'\n"
        "- Bulleted list of short descriptions of each change made"
    )

    return skill_md + "\n" + review_md + instructions


def build_review_user_prompt(doc_text, evaluation, doc_title, verify_output=None):
    verify_section = ""
    if verify_output is not None:
        verify_section = f"""
--- BEGIN Automated Evaluation Verify Report ---
{verify_output}
--- END Automated Evaluation Verify Report ---

"""
    return f"""Review the following evaluation report for this original document{", titled \"" + doc_title + "\"" if doc_title else ""}:
--- BEGIN Original Document Text ---
{doc_text}
--- END Original Document Text ---

--- BEGIN Evaluation Report ---
{evaluation}
--- END Evaluation Report ---

{verify_section}
Review the Evaluation Report of the Original Document Text by following the instructions in "high-vs-low Evaluation Report Review Checklist".
"""


def run_verify_report(evaluation_text):
    """Run verify-report.py on the given evaluation text and return its stdout.

    Writes the evaluation to a temp file, runs the script, and cleans up.
    Returns the combined stdout+stderr output, or None if the script is not
    found or fails to run.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    verify_script = os.path.join(script_dir, "verify-report.py")

    if not os.path.exists(verify_script):
        logger.info("    [script] Script not found: %s — skipping", verify_script)
        return None

    try:
        # Write evaluation to a temporary file
        fd, tmp_path = tempfile.mkstemp(suffix=".md", text=True)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(evaluation_text)

            result = subprocess.run(
                [sys.executable, verify_script, tmp_path],
                capture_output=True,
                text=True,
                timeout=30,
            )
            output = result.stdout
            if result.stderr:
                output += result.stderr
            return output.strip()
        finally:
            # Clean up temp file
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
    except subprocess.TimeoutExpired:
        logger.warning("    [script] verify-report.py timed out — skipping")
        return None
    except Exception as exc:
        logger.warning("    [script] Error running verify-report.py: %s — skipping", exc)
        return None


# ---------------------------------------------------------------------------
# Report parsing
# ---------------------------------------------------------------------------

def parse_evaluation_report(report_text):
    """Extract count_hl, count_ll, and score from an evaluation report."""
    # Try to get counts from the Scoring Summary table

    if not report_text:
        return None, None, None

    hl_match = re.search(r"High Law Aligned\s+\|?\s+(\d+)", report_text)
    ll_match = re.search(r"Low Law Aligned\s+\|?\s+(\d+)", report_text)

    # Also try header counts as fallback
    if not hl_match:
        hl_match = re.search(r"### High Law Aligned \((\d+) statements?\)", report_text)
    if not ll_match:
        ll_match = re.search(r"### Low Law Aligned \((\d+) statements?\)", report_text)

    count_hl = int(hl_match.group(1)) if hl_match else 0
    count_ll = int(ll_match.group(1)) if ll_match else 0

    # Try to get score from the report
    score = None
    score_match = re.search(
        r"\*\*Score\*\*.*?=\s*\*\*([+-]?\d+\.?\d*)\*\*", report_text
    )
    if score_match:
        score = float(score_match.group(1))
    else:
        # Calculate from counts
        total = count_hl + count_ll
        if total > 0:
            hl_pct = 100 * count_hl / total
            ll_pct = 100 * count_ll / total
            score = round((hl_pct - ll_pct) / 10, 1)

    return count_hl, count_ll, score


def parse_review_has_changes(changes_text):
    """Check if the LLM self-reported adding, moving, or removing statements."""
    return ("STATEMENTS_ADDED" in changes_text or "STATEMENTS_MOVED" in changes_text or "STATEMENTS_REMOVED" in changes_text)


def _is_valid_report(text):
    """Check if text looks like a real evaluation report.

    Verifies two mandatory section headers from the report template:
      1. The text contains "# High Law vs Low Law Alignment Evaluation"
         (after stripping leading whitespace the first line must start with it)
      2. Somewhere in the text "## Scoring Summary" is present
    """
    if not text:
        return False
    first_line = text.lstrip().split("\n")[0]
    if not first_line.startswith(_REPORT_TITLE_PREFIX):
        return False
    if "## Scoring Summary" not in text:
        return False
    return True


def parse_review_updated_eval(review_text):
    """Extract the full updated evaluation report text from the review response.

    Looks for the EVAL_REPORT_END_MARKER emitted by the LLM after the regenerated
    report.  Everything between the evaluation title line and that marker is the
    updated report.
    """
    # Find the marker
    marker_pos = review_text.find(EVAL_REPORT_END_MARKER)
    if marker_pos == -1:
        return None

    # Everything before the marker is the candidate report text (possibly with
    # preamble).  Trim to the report title header so "#" is the first character,
    # enforcing the template spec.
    before_marker = review_text[:marker_pos]

    # Strip all characters before the report title header, if found
    idx = before_marker.find(_REPORT_TITLE_PREFIX)
    if idx == -1:
        return before_marker
    return before_marker[idx:].strip()


def parse_review_changes_section(review_text):
    """Extract everything after the EVAL_REPORT_END_MARKER.

    The LLM emits the marker to separate the regenerated evaluation report from
    the CHANGES SUMMARY / review notes.  This function returns the text after
    the marker (stripped), or an empty string if the marker is not found.
    """
    marker_pos = review_text.find(EVAL_REPORT_END_MARKER)
    if marker_pos == -1:
        return review_text
    return review_text[marker_pos + len(EVAL_REPORT_END_MARKER):].strip()


# ---------------------------------------------------------------------------
# Database operations
# ---------------------------------------------------------------------------

def discover_schema(conn, args):
    """Step 1: Discover schema by querying sqlite_master."""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (args.table,)
    )
    row = cursor.fetchone()
    if not row:
        logger.error("Table '%s' not found in the database.", args.table)
        sys.exit(1)
    schema = row[0]
    logger.info("[db-init] Schema discovered:")
    logger.info(schema)

    # Verify required columns exist
    required = {"id", args.document_column, "evaluation", "count_hl", "count_ll", "score"}
    found = {m[0] for m in re.findall(r"(\w+)\s+(TEXT|INTEGER|REAL)", schema, re.IGNORECASE)}
    missing = required - found
    if missing:
        logger.error("[db-init] Missing required columns: %s", missing)
        sys.exit(1)
    logger.info("[db-init] All required columns present: %s", required)
    return schema


def preview_records(conn, args, limit=None, start_id=None, where_clause=None):
    """Step 2: Preview records - check id range, text lengths, evaluation state."""
    cursor = conn.cursor()

    cursor.execute(f"SELECT MIN(id), MAX(id), COUNT(*) FROM {args.table}")
    min_id, max_id, total = cursor.fetchone()

    cursor.execute(f"SELECT AVG(LENGTH({args.document_column})), MIN(LENGTH({args.document_column})), MAX(LENGTH({args.document_column})) FROM {args.table}")
    avg_len, min_len, max_len = cursor.fetchone()

    cursor.execute(f"SELECT COUNT(*) FROM {args.table} WHERE evaluation IS NOT NULL")
    evaluated = cursor.fetchone()[0]

    cursor.execute(f"SELECT COUNT(*) FROM {args.table} WHERE evaluation IS NULL")
    unevaluated = cursor.fetchone()[0]

    logger.info("Record preview:")
    logger.info("  ID range: %s - %s", min_id, max_id)
    logger.info("  Total records: %s", total)
    logger.info("  Text lengths: avg=%.0f, min=%s, max=%s", avg_len, min_len, max_len)
    logger.info("  Already evaluated: %s", evaluated)
    logger.info("  Unevaluated: %s", unevaluated)

    # Determine which records to process
    conditions = []
    params = []
    if where_clause is not None:
        conditions.append(where_clause)
    if start_id is not None:
        conditions.append("id >= ?")
        params.append(start_id)

    if conditions:
        cursor.execute(
            f"SELECT COUNT(*) FROM {args.table} WHERE " + " AND ".join(conditions), params
        )
    else:
        cursor.execute(f"SELECT COUNT(*) FROM {args.table}")
    eligible = cursor.fetchone()[0]

    if limit and limit < eligible:
        eligible = limit

    logger.info("  Records to process: %s", eligible)

    return min_id, max_id, total


def reset_evaluations(conn, args, where_clause=None):
    """Clean out evaluation, count_hl, count_ll, and score columns."""
    cursor = conn.cursor()
    query = f"UPDATE {args.table} SET evaluation = NULL, count_hl = NULL, count_ll = NULL, score = NULL"
    if where_clause is not None:
        query += f" WHERE {where_clause}"
    cursor.execute(query)
    conn.commit()
    logger.info("[Reset] Cleared evaluations for %s records.", cursor.rowcount)


def get_records_to_process(conn, args):
    """Get the list of (id, doc_title, doc_text) to process."""
    limit = args.limit
    start_id = args.start_id
    where_clause = args.where

    # Build WHERE clause from all filters
    conditions = []
    params = []

    # never overwrite existing evaluations, if doing (not skipping) the evaluation phase, make this a hard constraint
    if not args.skip_evaluation:
        conditions.append("evaluation IS NULL")
    # add conditions from args
    if where_clause is not None:
        conditions.append(where_clause)
    if start_id is not None:
        conditions.append("id >= ?")
        params.append(start_id)

    query = f"SELECT id, doc_title, {args.document_column} FROM {args.table}"

    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY id"
    if limit:
        query += " LIMIT ?"
        params.append(limit)

    cursor = conn.cursor()
    cursor.execute(query, params)
    return cursor.fetchall()


def save_evaluation(args, doc_id, evaluation, count_hl, count_ll, score):
    """Save evaluation results to the database. Safe partial update — only columns whose corresponding parameter is not None"""

    # Connect to database
    conn = sqlite3.connect(args.db_path)
    logger.info("[db-save] Connected to: %s", args.db_path)

    try:
        cursor = conn.cursor()
        assignments = []
        params = []
        if evaluation is not None:
            assignments.append("evaluation = ?")
            params.append(evaluation)
        if count_hl is not None:
            assignments.append("count_hl = ?")
            params.append(count_hl)
        if count_ll is not None:
            assignments.append("count_ll = ?")
            params.append(count_ll)
        if score is not None:
            assignments.append("score = ?")
            params.append(score)
        if not assignments:
            return  # nothing to update
        params.append(doc_id)
        query = f"UPDATE {args.table} SET {', '.join(assignments)} WHERE id = ?"
        cursor.execute(query, params)
        conn.commit()
    finally:
        conn.close()
        logger.info("[db-save] Connection closed")


def load_record(args, doc_id):
    """Load a single record's doc_text, doc_title, and evaluation."""

    # Connect to database
    conn = sqlite3.connect(args.db_path)
    logger.info("[db-load] Connected to: %s", args.db_path)

    try:
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT id, doc_title, {args.document_column}, evaluation FROM {args.table} WHERE id = ?",
            (doc_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return {"id": row[0], "doc_title": row[1], "doc_text": row[2], "evaluation": row[3]}
    finally:
        conn.close()
        logger.info("[db-load] Connection closed")


# ---------------------------------------------------------------------------
# Workflow steps
# ---------------------------------------------------------------------------

def _accumulate_stats(stats, result):
    """Accumulate token/time stats from a ChatResult into a stats dict."""
    stats["total_elapsed"] += result.elapsed
    if result.first_token_elapsed is not None:
        stats["total_generation_time"] += result.elapsed - result.first_token_elapsed
    if result.prompt_tokens is not None:
        stats["total_prompt_tokens"] += result.prompt_tokens
    if result.completion_tokens is not None:
        stats["total_completion_tokens"] += result.completion_tokens
    if result.total_tokens is not None:
        stats["total_tokens"] += result.total_tokens
    if result.reasoning_tokens is not None:
        stats["total_reasoning_tokens"] += result.reasoning_tokens
    output_tokens = (result.completion_tokens or 0) - (result.reasoning_tokens or 0)
    stats["total_output_tokens"] += output_tokens


def _stats_summary(name, stats, record_count):
    """Print a phase summary from accumulated stats."""
    logger.info("[%s] %s Complete", name, name)
    logger.info("  Records processed: %s", record_count)
    logger.info("  Total time:        %.1fs", time.monotonic() - stats['phase_start'])
    logger.info("  %s time:   %.1fs", name, stats['total_elapsed'])
    if record_count > 1:
        logger.info("  Avg time/rec:      %.1fs", stats['total_elapsed'] / record_count)
    # completion {stats['total_completion_tokens']} total {stats['total_tokens']}
    logger.info("  Tokens:            prompt %s reasoning %s output %s",
                stats['total_prompt_tokens'], stats['total_reasoning_tokens'], stats['total_output_tokens'])
    if stats["total_generation_time"]:
        logger.info("  Tokens/Second:     output: %.1f (in %.1fs)",
                     stats['total_output_tokens'] / stats['total_generation_time'],
                     stats['total_generation_time'])


def _empty_stats():
    """Return a fresh stats dict."""
    return { "phase_start": time.monotonic(), "total_elapsed": 0.0, "total_generation_time": 0.0, "total_prompt_tokens": 0,
        "total_completion_tokens": 0, "total_tokens": 0, "total_reasoning_tokens": 0, "total_output_tokens": 0 }


def _evaluate_record(client, doc_id, doc_title, doc_text, dry_run, detailed, args):
    """Evaluate a single record. Returns (doc_id, doc_title, hl, ll, score, response, error, chat_result)."""

    system_prompt = build_evaluation_system_prompt(detailed)
    user_prompt = build_evaluation_user_prompt(doc_text, doc_title)

    # Start progress display immediately — timer ticks while waiting for first token
    _start_time = time.monotonic()
    start_fn, wrapped_cb = make_streaming_callback(print_progress)
    start_fn(_start_time)

    try:
        result = client.chat_stream(system_prompt, user_prompt, progress_cb=wrapped_cb)
    except RuntimeError as exc:
        stop_wait_timer()
        print_progress_done()
        logger.error("    %s", exc)
        return (doc_id, doc_title, None, None, None, None, str(exc), None)

    stop_wait_timer()
    print_progress_done()

    output_tokens = (result.completion_tokens or 0) - (result.reasoning_tokens or 0)
    logger.info("    [eval] LLM API Call: %.1fs | prompt tokens: %s reasoning: %s output: %s completion: %s total: %s",
                result.elapsed, result.prompt_tokens, result.reasoning_tokens,
                output_tokens, result.completion_tokens, result.total_tokens)

    eval_report = result.content.lstrip() if result.content else None
    if not eval_report:
        logger.warning("    No evaluation report returned")
        return (doc_id, doc_title, None, None, None, None, "Empty Response", None)

    count_hl, count_ll, score = parse_evaluation_report(eval_report)
    logger.info("    [eval] Result: HL=%s, LL=%s, Score=%s", count_hl, count_ll, score)

    if dry_run:
        return (doc_id, doc_title, count_hl, count_ll, score, eval_report, None, result)

    # Save
    save_evaluation(args, doc_id, eval_report, count_hl, count_ll, score)
    logger.info("    [eval] Saved evaluation, counts, and score to database (%s chars)", len(eval_report))

    # Verify
    record = load_record(args, doc_id)
    if record and record["evaluation"] is not None:
        logger.info("    [eval] Verified: evaluation populated (%s chars)", len(record['evaluation']))
    else:
        logger.warning("    [eval] evaluation not found in database after save")

    return (doc_id, doc_title, count_hl, count_ll, score, eval_report, None, result)


def _review_record(client, doc_id, doc_title, orig_hl, orig_ll, orig_score, dry_run, args, eval_text=None):
    """Review a single record with re-execution loop.

    eval_text: optional pre-loaded evaluation text (used in dry-run mode or when
                the evaluation was just generated and not yet persisted).
    Returns (doc_id, doc_title, orig_hl, orig_ll, orig_score, final_hl, final_ll, final_score, final_error, result).
    """
    MAX_REVIEW_ITERATIONS = 3

    final_hl, final_ll, final_score = orig_hl, orig_ll, orig_score
    final_error = None

    for iteration in range(1, MAX_REVIEW_ITERATIONS + 1):
        iter_label = f"Review Pass {iteration}"
        logger.info("    [%s]", iter_label)

        # In dry-run mode or when eval_text is provided, use it directly;
        # otherwise reload from DB (may have been updated by previous iteration)
        if eval_text is not None:
            current_eval = eval_text
            current_doc_text = None  # will be loaded below if needed
        else:
            record = load_record(args, doc_id)
            if not record or record["evaluation"] is None:
                logger.error("      evaluation lost during re-review")
                final_error = "Evaluation lost during re-review"
                break
            current_eval = record["evaluation"]
            current_doc_text = record["doc_text"]

        if current_doc_text is None:
            rec = load_record(args, doc_id)
            current_doc_text = rec["doc_text"] if rec else ""

        # Run automated verification on the current evaluation
        logger.info("    [script] Running verify-report.py...")
        verify_output = run_verify_report(current_eval)
        if verify_output:
            logger.info("    [script] Verify Output:\n      %s", "\n      ".join(verify_output.split("\n")))
        else:
            logger.info("    [script] Verify Output: (none)")

        system_prompt = build_review_system_prompt()
        user_prompt = build_review_user_prompt(
            current_doc_text, current_eval, doc_title, verify_output=verify_output
        )

        # Start progress display immediately
        _rev_start = time.monotonic()
        rev_start_fn, rev_wrapped_cb = make_streaming_callback(print_progress)
        rev_start_fn(_rev_start)

        try:
            result = client.chat_stream(system_prompt, user_prompt, progress_cb=rev_wrapped_cb)
        except RuntimeError as exc:
            stop_wait_timer()
            print_progress_done()
            logger.error("      %s", exc)
            final_error = str(exc)
            break

        stop_wait_timer()
        print_progress_done()

        # Extract the post-marker section (CHANGES SUMMARY / review notes).
        changes_text = parse_review_changes_section(result.content)

        # has_changes defined as presence of LLM self-reported text about
        # STATEMENT changes in the CHANGES SUMMARY section only.
        has_changes = changes_text and parse_review_has_changes(changes_text)

        # Log the changes section for debugging
        if changes_text:
            logger.info("    [review] LLM Review Notes:\n      %s", "\n      ".join(changes_text.split("\n")))

        # Extract the regenerated report (between title and marker) for saving.
        # If no regenerated report was emitted, the LLM reported no changes and
        # we keep the original counts.
        updated_eval = parse_review_updated_eval(result.content)
        updated_is_valid_report = updated_eval and _is_valid_report(updated_eval)

        # Parse counts the same way as the evaluation step — directly from the raw LLM output.
        if updated_is_valid_report:
            new_hl, new_ll, new_score = parse_evaluation_report(updated_eval)
        else:
            new_hl, new_ll, new_score = None, None, None

        logger.info("    [review] Valid New Report Generated? %s. Statement Changes Reported? %s.",
                     "YES" if updated_is_valid_report else "NO",
                     "YES" if has_changes else "NO")
        logger.info("    [review] Original: HL %s, LL %s, Score %s", orig_hl, orig_ll, orig_score)
        logger.info("    [review] Updated:  HL %s, LL %s, Score %s", new_hl, new_ll, new_score)
        output_tokens = (result.completion_tokens or 0) - (result.reasoning_tokens or 0)
        logger.info("    [review] LLM API Call: %.1fs | prompt tokens: %s reasoning: %s output: %s completion: %s total: %s",
                     result.elapsed, result.prompt_tokens, result.reasoning_tokens,
                     output_tokens, result.completion_tokens, result.total_tokens)

        if updated_is_valid_report:
            # save the valid report
            if not dry_run:
                save_evaluation(args, doc_id, updated_eval, new_hl, new_ll, new_score)
                logger.info("    [review] Saved updated evaluation + counts/score to database. Evaluation length: %d chars", len(updated_eval) if updated_eval else 0)
            else:
                logger.info("    [DRY RUN] Would save updated evaluation + counts/score.")
        else:
            if not dry_run:
                # Quick check to see if counts/score need to be corrected or filled in
                new_hl, new_ll, new_score = parse_evaluation_report(current_eval)
                if ((new_hl and new_hl != orig_hl) or (new_ll and new_ll != orig_ll) or (new_score and new_score != orig_score)):
                    # NOTE: this relies on save_evalution() remaining "safe" and not nulling columns with None value
                    save_evaluation(args, doc_id, None, new_hl, new_ll, new_score)
                    logger.info("      Skipped evaluation update (no valid eval text extracted).")
                    logger.info("      NOTE: Saved corrected counts/score from current report text, DB values were not correct: DB HL=%s, LL=%s, Score=%s REPORT HL=%s, LL=%s, Score=%s",
                                orig_hl, orig_ll, orig_score, new_hl, new_ll, new_score)
                else:
                    logger.info("      Skipped evaluation + counts/score update (no valid eval text extracted).")
            else:
                logger.info("      [DRY RUN] Would skip evaluation + counts/score update (no valid eval text extracted).")

        if has_changes and iteration < MAX_REVIEW_ITERATIONS:
            orig_hl, orig_ll, orig_score = new_hl, new_ll, new_score
            final_hl, final_ll, final_score = new_hl, new_ll, new_score
            if updated_is_valid_report:
                # use updated text for next iteration
                eval_text = updated_eval
                logger.info("      -> Re-reviewing with updated evaluation report...")
            else:
                logger.info("      -> Re-reviewing with the SAME evaluation text (no valid report found)...")
            continue

        # No changes reported or last iteration — finalize
        final_hl, final_ll, final_score = new_hl, new_ll, new_score
        changed = (new_hl != orig_hl) or (new_ll != orig_ll) or (new_score != orig_score)
        if changed:
            logger.warning("    [review] Final: WARNING - Last run still had different counts or score")
        else:
            logger.info("    [review] Final: No statement changes made")

        # Verify
        if dry_run:
            logger.info("      [DRY RUN] Would verify evaluation in database.")
        else:
            record = load_record(args, doc_id)
            if record and record["evaluation"] is not None:
                logger.info("    [review] Verified: evaluation present (%s chars)", len(record['evaluation']))
            else:
                logger.warning("    [review] evaluation missing after review!")

        break

    return (doc_id, doc_title, orig_hl, orig_ll, orig_score, final_hl, final_ll, final_score, final_error, result)


def process_records_interleaved(client, records, args):
    """Process records: evaluate then review for each record before moving to the next.

    Returns (eval_results, review_results) tuples compatible with step5_report.
    eval_results: (doc_id, doc_title, hl, ll, score, response, error)
    review_results: (doc_id, doc_title, orig_hl, orig_ll, orig_score, final_hl, final_ll, final_score, error)
    """

    dry_run = args.dry_run
    detailed = args.detailed
    skip_evaluation = args.skip_evaluation
    skip_review = args.skip_review
    eval_results = []
    review_results = []

    eval_stats = _empty_stats()
    review_stats = _empty_stats()

    logger.info("=" * 60)
    logger.info("Interleaved Evaluation + Review")
    logger.info("=" * 60)
    logger.info("  Records: %s", len(records))
    logger.info("  Report type: %s", "detailed" if detailed else "basic")
    logger.info("  Skip evaluation: %s", skip_evaluation)
    logger.info("  Skip review: %s", skip_review)
    logger.info("")

    for idx, (doc_id, doc_title, doc_text) in enumerate(records, 1):
        logger.info("[%s/%s] ID=%s: %s", idx, len(records), doc_id, doc_title)

        response = None  # set by eval step, used by review step

        # --- Step 3: Evaluate (unless skipped) ---
        if skip_evaluation:
            logger.info("  [eval] SKIPPED (--skip-evaluation)")
        else:
            logger.info("  [eval] Evaluating...")
            er = _evaluate_record(client, doc_id, doc_title, doc_text, dry_run, detailed, args)
            _, _, count_hl, count_ll, score, response, error, chat_result = er
            if chat_result:
                _accumulate_stats(eval_stats, chat_result)
            eval_results.append((doc_id, doc_title, count_hl, count_ll, score, response, error))

        logger.info("")

        # --- Step 4: Review (unless skipped) ---
        if skip_review:
            logger.info("  [review] SKIPPED (--skip-review)")
            review_results.append((doc_id, doc_title, count_hl, count_ll, score, count_hl, count_ll, score, None))
        else:
            logger.info("  [review] Reviewing...")
            # If we skipped evaluation, parse counts from DB
            rev_orig_hl = count_hl
            rev_orig_ll = count_ll
            rev_orig_score = score
            if rev_orig_hl is None:
                record = load_record(args, doc_id)
                if record and record["evaluation"] is not None:
                    rev_orig_hl, rev_orig_ll, rev_orig_score = parse_evaluation_report(record["evaluation"])

            if rev_orig_hl is None:
                logger.info("    SKIPPED: No evaluation found for ID=%s", doc_id)
                review_results.append((doc_id, doc_title, None, None, None, None, None, None, "No evaluation"))
            else:
                # Pass evaluation text directly to review (avoids DB round-trip)
                if not skip_evaluation and response is not None:
                    rev_eval_text = response
                else:
                    rec = load_record(args, doc_id)
                    rev_eval_text = rec["evaluation"] if rec else None
                rr = _review_record(client, doc_id, doc_title, rev_orig_hl, rev_orig_ll, rev_orig_score, dry_run, args, rev_eval_text)
                _, _, orig_hl, orig_ll, orig_score, final_hl, final_ll, final_score, final_error, chat_result = rr
                if chat_result:
                    _accumulate_stats(review_stats, chat_result)
                review_results.append((doc_id, doc_title, orig_hl, orig_ll, orig_score, final_hl, final_ll, final_score, final_error))

        logger.info("")

    # Print summaries
    logger.info("=" * 60)
    if not skip_evaluation:
        _stats_summary("Evaluation", eval_stats, len([r for r in eval_results if r[6] is None]))
        logger.info("=" * 60)
    if not skip_review:
        _stats_summary("Review", review_stats, len([r for r in review_results if r[8] is None]))
        logger.info("=" * 60)

    return eval_results, review_results


def step5_report(eval_results, review_results):
    """Step 5: Report summary."""
    logger.info("=" * 60)
    logger.info("Summary Report")
    logger.info("=" * 60)
    logger.info("")

    logger.info("EVALUATION RESULTS:")
    logger.info("  %6s  %-50s  %3s  %3s  %6s  %s", "ID", "Title", "HL", "LL", "Score", "Error")
    logger.info("  " + "-" * 100)
    for r in eval_results:
        doc_id, doc_title, hl, ll, score, _, error = r[0], r[1], r[2], r[3], r[4], r[5], r[6]
        title_display = doc_title[:48] if doc_title else "N/A"
        hl_str = str(hl) if hl is not None else "N/A"
        ll_str = str(ll) if ll is not None else "N/A"
        score_str = f"{score:.1f}" if score is not None else "N/A"
        error_str = error[:20] if error else ""
        logger.info("  %6s  %-50s  %3s  %3s  %6s  %s", doc_id, title_display, hl_str, ll_str, score_str, error_str)

    if review_results:
        logger.info("")
        logger.info("REVIEW RESULTS:")
        logger.info("  %6s  %-50s  %7s  %7s  %10s  %6s  %6s  %9s  %s",
                     "ID", "Title", "Orig HL", "Orig LL", "Orig Score", "New HL", "New LL", "New Score", "Error")
        logger.info("  " + "-" * 130)
        for r in review_results:
            doc_id = r[0]
            doc_title = r[1] if len(r) > 1 else ""
            title_display = doc_title[:45] if doc_title else "N/A"
            orig_hl = str(r[2]) if r[2] is not None else "N/A"
            orig_ll = str(r[3]) if r[3] is not None else "N/A"
            orig_score = f"{r[4]:.1f}" if r[4] is not None else "N/A"
            new_hl = str(r[5]) if r[5] is not None else "N/A"
            new_ll = str(r[6]) if r[6] is not None else "N/A"
            new_score = f"{r[7]:.1f}" if r[7] is not None else "N/A"
            error = r[8] if len(r) > 8 and r[8] else ""
            error_str = error[:15] if error else ""
            logger.info("  %6s  %-50s  %7s  %7s  %10s  %6s  %6s  %9s  %s",
                         doc_id, title_display, orig_hl, orig_ll, orig_score, new_hl, new_ll, new_score, error_str)

    logger.info("")
    logger.info("Workflow complete.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Database Delegation Workflow for High Law vs Low Law evaluation"
    )
    parser.add_argument("db_path", help="Path to SQLite database")
    parser.add_argument("--limit", type=int, default=None, help="Process only first N records")
    parser.add_argument("--start-id", type=int, default=None, help="Start from this record ID")
    parser.add_argument("--endpoint", default=os.environ.get("OPENAI_ENDPOINT", "http://127.0.0.1:1234/v1"), help="OpenAI-compatible endpoint URL")
    parser.add_argument("--api-key", default=os.environ.get("OPENAI_API_KEY", ""), help="API key")
    parser.add_argument("--model", default="", help="Model name (default: empty, let endpoint decide)")
    parser.add_argument("--stub", action="store_true", help="Use stub AI client (constant response)")
    parser.add_argument("--skip-review", action="store_true", help="Skip the review phase")
    parser.add_argument("--skip-evaluation", action="store_true", help="Skip the evaluation phase")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without modifying database")
    parser.add_argument("--reset", action="store_true", help="Reset evaluation data before processing")
    parser.add_argument("--reset-only", action="store_true", help="Only reset evaluation data and exit (no eval)")
    parser.add_argument("--where", default=None, help="SQL WHERE clause (without 'WHERE') to filter records")
    parser.add_argument("--table", default=None, help=f"Table name to use (default: exactly one table, '{DEFAULT_DOCUMENTS_TABLE}' if found, or must specify)")
    parser.add_argument("--document-column", default=DEFAULT_DOCUMENT_COLUMN, help=f"Column containing the document text (default: {DEFAULT_DOCUMENT_COLUMN})")
    parser.add_argument("--detailed", action="store_true", help="Produce detailed evaluation reports (default: basic)")

    args = parser.parse_args()

    # Setup logging before any output
    setup_logging(args.db_path)

    # Normalize --endpoint: if it's just an IP/host, build a full URL
    if "://" not in args.endpoint:
        args.endpoint = f"{DEFAULT_EP_NO_URL_PREFIX}{args.endpoint}{DEFAULT_EP_NO_URL_SUFFIX}"
        logger.info("Normalized endpoint to: %s", args.endpoint)

    # Validate database path
    if not os.path.exists(args.db_path):
        logger.error("Database not found: %s", args.db_path)
        sys.exit(1)

    # Connect to database
    conn = sqlite3.connect(args.db_path)
    logger.info("[db-init] Connected to: %s", args.db_path)

    try:
        # Resolve table name
        if not args.table:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            tables = [row[0] for row in cursor.fetchall()]
            if len(tables) == 1:
                args.table = tables[0]
                logger.info("[db-init] Auto-detected single table: %s", args.table)
            else:
                # if one of the tables is DEFAULT_DOCUMENTS_TABLE then use that one
                if tables and DEFAULT_DOCUMENTS_TABLE in tables:
                    args.table = DEFAULT_DOCUMENTS_TABLE
                    logger.info("[db-init] Using default table name, was found in DB: %s", args.table)
                else:
                    logger.error("Database has %d tables. Please specify one with --table.", len(tables))
                    if tables:
                        logger.error("  Available tables: %s", ", ".join(tables))
                    sys.exit(1)

        logger.info("[db-init] Document column: %s", args.document_column)

        # Step 1: Discover schema
        discover_schema(conn, args)

        # Step 2: Preview records
        preview_records(conn, args, limit=args.limit, start_id=args.start_id, where_clause=args.where)

        # Reset evaluations (if --reset or --reset-only is passed)
        if args.reset or args.reset_only:
            if not args.dry_run:
                reset_evaluations(conn, args, where_clause=args.where)
            else:
                logger.info("[Dry-run] Would reset evaluations.")

            if args.reset_only:
                logger.info("Reset complete. Exiting.")
                return

        # Get records to process
        records = get_records_to_process(conn, args)
        if not records:
            logger.info("No records to process.")
            return
    finally:
        conn.close()
        logger.info("[db-init] Connection closed")

    # From here use a DB connection per operation so file isn't left open for long periods
    # Initialize client (only needed if not skipping both phases)
    if args.skip_evaluation and args.skip_review:
        client = None
        logger.info("[llm] Skipping both evaluation and review — no client needed")
    elif args.stub:
        client = StubClient()
        logger.info("[llm] Using STUB client (constant responses)")
    else:
        if not args.endpoint:
            logger.error("--endpoint is required")
            sys.exit(1)
        client = OpenAIClient(args.endpoint, args.api_key, args.model)
        logger.info("[llm] Endpoint: %s, Model: %s", args.endpoint, args.model if args.model else "(whatever is loaded or default...)")

    logger.info("")
    logger.info("Processing %s records...", len(records))

    # Step 3/4: Interleaved evaluation + review per record
    eval_results, review_results = process_records_interleaved(client, records, args)

    # Step 5: Report
    step5_report(eval_results, review_results)


if __name__ == "__main__":
    main()
