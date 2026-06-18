#!/usr/bin/env python3
"""
run-sqlite.py

Threaded, status-based evaluation workflow for High Law vs Low Law.
Based on batch-sqlite.py with multi-thread support and YAML config.

Usage:
  python3 run-sqlite.py <db_path|config.yml> [options]

If first positional argument is a .yml/.yaml file, it is loaded as config.
Otherwise, treated as db_path and CLI args are used.

Options mirror batch-sqlite.py plus:
  --parallel N       Number of threads for main endpoint (default: 1)
  --reviews N        Number of review iterations (default: 3; 0 = skip)
  --name NAME        Human-readable name for this endpoint (for progress lines)

YAML config supports all CLI options plus 'db' for database filename,
and a 'drafts' list with per-endpoint config including 'parallel'.
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
from typing import Any, Callable, Dict, List, NamedTuple, Optional

try:
    import yaml
except ImportError:
    yaml = None

logger = logging.getLogger("run-sqlite")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_ENDPOINT = "http://127.0.0.1:1234/v1"
DEFAULT_EP_NO_URL_PREFIX = "http://"
DEFAULT_EP_NO_URL_SUFFIX = ":1234/v1"
DEFAULT_DOCUMENTS_TABLE = "documents"
DEFAULT_DOCUMENT_COLUMN = "doc_text"
DEFAULT_ID_COLUMN = "id"
DEFAULT_EVALUTION_COL = "evaluation"
DEFAULT_COUNT_HL_COLUMN = "count_hl"
DEFAULT_COUNT_LL_COLUMN = "count_ll"
DEFAULT_SCORE_COLUMN = "score"

_REPORT_TITLE_PREFIX = "# High Law vs Low Law Alignment Evaluation"
_REPORT_LATE_HEADER = "## Key Topic Score Table"
EVAL_REPORT_END_MARKER = "_END_OF_UPDATED_REPORT_"

# Status constants
STATUS_PLANNED = 0
STATUS_EVAL_IN_PROGRESS = 1
STATUS_EVAL_COMPLETE = 2
STATUS_MERGE_PLANNED = 3
STATUS_MERGE_IN_PROGRESS = 4
STATUS_MERGE_COMPLETE = 5
STATUS_DRAFTS_IN_PROGRESS = 6
STATUS_DRAFTS_COMPLETE = 7
STATUS_REVIEW_IN_PROGRESS = 8
STATUS_REVIEW_COMPLETE = 9

# Draft status constants
DRAFT_PLANNED = 0
DRAFT_IN_PROGRESS = 1
DRAFT_COMPLETE = 2
DRAFT_REVIEW_IN_PROGRESS = 3
DRAFT_REVIEW_COMPLETE = 4
DRAFT_MERGE_IN_PROGRESS = 5
DRAFT_MERGE_COMPLETE = 6

# Directories for other files used (SKILL.md, report-review.md, verify-report.py, etc), relative to script file (use dir structure from git repo)
_BATCH_DIR = os.path.dirname(os.path.abspath(__file__))
_SCRIPTS_DIR = os.path.dirname(_SCRIPTS_DIR)
_SKILL_DIR = os.path.dirname(_SCRIPTS_DIR)

# ---------------------------------------------------------------------------
# Stubs
# ---------------------------------------------------------------------------

_STUB_EVAL_PATH = os.path.join(_BATCH_DIR, "test-report.md")
def _load_stub_evaluation() -> str:
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
# Multi-thread progress display
# ---------------------------------------------------------------------------

class MultiProgressDisplay:
    """Manages N static progress lines at the bottom of the terminal."""

    def __init__(self, num_lines: int):
        self.num_lines = num_lines
        self._lock = threading.Lock()
        self._lines: List[str] = [""] * num_lines
        self._last_refresh: float = 0
        self._dirty = False
        self._term_width = shutil.get_terminal_size(fallback=(180, 24)).columns
        # Start background refresh thread
        self._stop_event = threading.Event()
        self._bg_thread = threading.Thread(target=self._refresh_loop, daemon=True)
        self._bg_thread.start()

    def _refresh_loop(self):
        while not self._stop_event.is_set():
            self._stop_event.wait(0.5)
            self._render()

    def _render(self):
        with self._lock:
            if not self._dirty:
                return
            self._dirty = False
            now = time.monotonic()
            if now - self._last_refresh < 0.3:
                return
            self._last_refresh = now

        # Save cursor, move to bottom N lines, draw, restore
        lines_to_draw = []
        with self._lock:
            for i in range(self.num_lines):
                lines_to_draw.append(self._lines[i] if i < len(self._lines) else "")

        sys.stdout.write("\033[?25l")  # hide cursor
        sys.stdout.write("\033[s")  # save cursor position
        sys.stdout.write(f"\033[{self.num_lines}A")  # move up N lines
        for line in lines_to_draw:
            padded = line.ljust(self._term_width)
            sys.stdout.write(f"\033[2K\r{padded}\n")
        sys.stdout.write(f"\033[{self.num_lines}A")  # move back up
        sys.stdout.write("\033[u")  # restore cursor
        sys.stdout.write("\033[?25h")  # show cursor
        sys.stdout.flush()

    def update_line(self, line_idx: int, text: str):
        with self._lock:
            if 0 <= line_idx < self.num_lines:
                if self._lines[line_idx] != text:
                    self._lines[line_idx] = text[:self._term_width]
                    self._dirty = True

    def finalize(self):
        """Stop background thread and do final render."""
        self._stop_event.set()
        self._bg_thread.join(timeout=2)
        self._render()
        # Clear the progress lines
        sys.stdout.write("\033[?25l")
        sys.stdout.write("\033[s")
        sys.stdout.write(f"\033[{self.num_lines}A")
        for _ in range(self.num_lines):
            sys.stdout.write("\033[2K\r" + " " * self._term_width + "\n")
        sys.stdout.write(f"\033[{self.num_lines}A")
        sys.stdout.write("\033[u")
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()

    def newline_after(self):
        """Move cursor past the progress lines."""
        sys.stdout.write(f"\033[{self.num_lines}B\n")
        sys.stdout.flush()


def make_thread_progress_cb(display: MultiProgressDisplay, line_idx: int) -> Callable:
    """Create a progress callback for a specific thread line."""
    start_times: Dict[int, float] = {}
    last_print: Dict[int, float] = {}

    def cb(char_count: int, content_so_far: str, start_time: float) -> None:
        if line_idx not in start_times:
            start_times[line_idx] = start_time
        elapsed = time.monotonic() - start_times.get(line_idx, start_time)
        now = time.monotonic()
        if last_print.get(line_idx, 0) > now - 0.5:
            return
        last_print[line_idx] = now
        mins = int(elapsed) // 60
        secs = int(elapsed) % 60
        if char_count == 0:
            left = f" {mins:02d}:{secs:02d} (reading & reasoning...) | "
        else:
            left = f" {mins:02d}:{secs:02d} chars {char_count} | "
        tw = display._term_width
        text_width = max(10, tw - len(left) - 1)
        flat = content_so_far.replace("\r", "").replace("\n", " ")
        recent = flat[-(text_width + 20):]
        recent = recent[-text_width:]
        display.update_line(line_idx, left + recent)

    return cb


# ---------------------------------------------------------------------------
# OpenAI-compatible client
# ---------------------------------------------------------------------------

class ChatResult(NamedTuple):
    content: str
    elapsed: float = 0.0
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    reasoning_tokens: Optional[int] = None
    first_token_elapsed: Optional[float] = None


class OpenAIClient:
    """Minimal OpenAI-compatible chat completions client using urllib."""

    def __init__(self, endpoint: str, api_key: str, model: str = ""):
        self.endpoint = endpoint.rstrip("/")
        self.api_key = api_key
        self.model = model

    def _build_payload(self, system_prompt: str, user_prompt: str, stream: bool = False) -> dict:
        return {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "reasoning_effort": "high",
            "reasoning": "on",
            "stream": stream,
            "stream_options": {"include_usage": True} if stream else None,
            "max_completion_tokens": 40000,
            "max_tokens": 40000,
        }

    def chat(self, system_prompt: str, user_prompt: str) -> ChatResult:
        url = f"{self.endpoint}/chat/completions"
        payload = self._build_payload(system_prompt, user_prompt, stream=False)
        if payload.get("stream_options") is None:
            payload.pop("stream_options", None)
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }, method="POST")
        start = time.monotonic()
        try:
            with urllib.request.urlopen(req, timeout=1800) as resp:
                body = json.loads(resp.read().decode("utf-8"))
            elapsed = time.monotonic() - start
            content = body["choices"][0]["message"]["content"]
            usage = body.get("usage", {})
            usage_details = usage.get("completion_tokens_details", {})
            return ChatResult(content=content, elapsed=elapsed, prompt_tokens=usage.get("prompt_tokens"),
                completion_tokens=usage.get("completion_tokens"), total_tokens=usage.get("total_tokens"),
                reasoning_tokens=usage_details.get("reasoning_tokens"))
        except urllib.error.HTTPError as exc:
            elapsed = time.monotonic() - start
            error_body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"HTTP {exc.code} from {url} ({elapsed:.1f}s): {error_body}") from exc

    def chat_stream(self, system_prompt: str, user_prompt: str,
                     progress_cb: Optional[Callable] = None) -> ChatResult:
        url = f"{self.endpoint}/chat/completions"
        payload = self._build_payload(system_prompt, user_prompt, stream=True)
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={ "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}" }, method="POST")
        start = time.monotonic()
        try:
            with urllib.request.urlopen(req, timeout=1800) as resp:
                full_content: List[str] = []
                prompt_tokens = None
                completion_tokens = None
                total_tokens = None
                reasoning_tokens = None
                char_count = 0
                first_token_time = None

                for raw_line in resp:
                    line = raw_line.decode("utf-8").rstrip("\n")
                    if not line or not line.startswith("data: "):
                        continue
                    data_str = line[6:]
                    if data_str == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data_str)
                    except json.JSONDecodeError:
                        continue

                    choices = chunk.get("choices", [])
                    for choice in choices:
                        delta = choice.get("delta", {})
                        delta_content = delta.get("content")
                        if delta_content:
                            if first_token_time is None:
                                first_token_time = time.monotonic() - start
                            full_content.append(delta_content)
                            if progress_cb:
                                char_count = len("".join(full_content).split())
                                progress_cb(char_count, "".join(full_content), start)

                    usage = chunk.get("usage")
                    if usage:
                        prompt_tokens = usage.get("prompt_tokens")
                        completion_tokens = usage.get("completion_tokens")
                        total_tokens = usage.get("total_tokens")
                        cd = usage.get("completion_tokens_details", {})
                        reasoning_tokens = cd.get("reasoning_tokens")

                elapsed = time.monotonic() - start
                content = "".join(full_content)
                if completion_tokens is None:
                    completion_tokens = char_count
                return ChatResult(content=content, elapsed=elapsed, prompt_tokens=prompt_tokens, completion_tokens=completion_tokens,
                    total_tokens=total_tokens, reasoning_tokens=reasoning_tokens, first_token_elapsed=first_token_time)
        except urllib.error.HTTPError as exc:
            elapsed = time.monotonic() - start
            error_body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"HTTP {exc.code} from {url} ({elapsed:.1f}s): {error_body}") from exc


class StubClient:
    """Stub that returns constant responses for testing."""

    def __init__(self):
        self.call_count = 0
        self.review_call_count = 0
        self.merge_call_count = 0
        self._lock = threading.Lock()

    def chat(self, system_prompt: str, user_prompt: str) -> ChatResult:
        return self._stub_response(system_prompt, user_prompt)

    def chat_stream(self, system_prompt: str, user_prompt: str, progress_cb: Optional[Callable] = None) -> ChatResult:
        result = self._stub_response(system_prompt, user_prompt)
        content = result.content
        chunk_size = 50
        start = time.monotonic()
        for i in range(0, len(content), chunk_size):
            chunk = content[i:i + chunk_size]
            if progress_cb:
                char_count = len(content[:i + len(chunk)].split())
                progress_cb(char_count, content[:i + len(chunk)], start)
            time.sleep(0.001)
        return result._replace(elapsed=time.monotonic() - start, first_token_elapsed=0.005)

    def _stub_response(self, system_prompt: str, user_prompt: str) -> ChatResult:
        with self._lock:
            self.call_count += 1
            if user_prompt.lower().startswith("merge"):
                self.merge_call_count += 1
                content = STUB_REVIEW_WITH_CHANGES
            elif user_prompt.lower().startswith("review"):
                self.review_call_count += 1
                if self.review_call_count == 1:
                    content = STUB_REVIEW_WITH_CHANGES
                else:
                    content = STUB_REVIEW
            else:
                content = _load_stub_evaluation()
        return ChatResult(content=content, elapsed=0.01, prompt_tokens=100, completion_tokens=200, total_tokens=300, reasoning_tokens=0)


# ---------------------------------------------------------------------------
# Prompt builders
# ---------------------------------------------------------------------------

def _read_skill_file(relative_path: str) -> str:
    path = os.path.join(_SKILL_DIR, relative_path)
    if not os.path.exists(path):
        logger.warning("Skill file not found: %s", path)
        return ""
    with open(path, "r", encoding="utf-8") as fl:
        return fl.read()


def build_evaluation_system_prompt(is_detailed: bool) -> str:
    skill_md = _read_skill_file("SKILL.md")
    if is_detailed:
        extra = ("\n\n## Report Type: DETAILED\n\n"
                 "Produce a **DETAILED** evaluation report. Include ALL sections from the Report Specification.")
    else:
        extra = ("\n\n## Report Type: BASIC\n\n"
                 "Produce a **basic/score** evaluation report. Do *not* include the detailed sections. "
                 "Stop after the *Key Topic Score Table* section.")
    instructions = (
        "\n\n# Task\n\n"
        "You are a High Law vs Low Law alignment evaluator.\n\n"
        "Evaluate the provided document text by following the Evaluation Protocol "
        "and Report Specification from the skill file above.\n"
        f"{extra}\n\n"
        "Execute the Self-Verification and Post-Report Self-Check before emitting the final report.")
    return skill_md + instructions


def build_evaluation_user_prompt(doc_text: str, doc_title: Optional[str]) -> str:
    title_part = f' titled "{doc_title}"' if doc_title else ""
    return f"""Evaluate the following document{title_part} for High Law vs Low Law Alignment.
--- BEGIN Document Text ---
{doc_text}
--- END Document Text ---

Produce the evaluation report by following the instructions in the **high-vs-low** skill.
"""


def build_review_system_prompt() -> str:
    skill_md = _read_skill_file("SKILL.md")
    review_md = _read_skill_file("references/report-review.md")
    instructions = (
        "\n\n# Task\n\n"
        "You are a High Law vs Low Law evaluation report reviewer.\n\n"
        "Review the provided evaluation report against the original document text by executing the following **in order**:\n"
        "1. Execute the Report Review Checklist from the reference file above, all included instructions in exact order.\n"
        "2. Do NOT verify the DETAILED sections if they are not present, and do NOT generate the DETAILED sections if they are not present.\n"
        "3. If changes are needed, describe them clearly with original and updated counts. If no changes are needed, state that explicitly.\n"
        "4. If any changes are needed, **FIRST** regenerate the entire updated evaluation report.\n"
        "5. If you regenerated an updated evaluation report, **ALWAYS** emit the following **EXACT** marker on its own line after the report:\n"
        f"```\n{EVAL_REPORT_END_MARKER}\n```\n"
        "This marker tells the parser where the report ends and the summary begins.\n"
        "6. After the marker, include a CHANGES SUMMARY section:\n"
        "- Original counts: HL=N, LL=N, Score=X.X\n"
        "- Updated counts: HL=N, LL=N, Score=X.X (same if no changes)\n"
        "- If and **ONLY** if you added any statements then emit the EXACT text marker 'STATEMENTS_ADDED'\n"
        "- If and **ONLY** if you moved any statements between high/low categories then emit the EXACT text marker 'STATEMENTS_MOVED'\n"
        "- If and **ONLY** if you removed any statements then emit the EXACT text marker 'STATEMENTS_REMOVED'\n"
        "- Bulleted list of short descriptions of each change made")
    return skill_md + "\n" + review_md + instructions


def build_merge_system_prompt() -> str:
    skill_md = _read_skill_file("SKILL.md")
    instructions = (
        "\n\n# Task\n\n"
        "You are a High Law vs Low Law alignment evaluator performing a **merge** of two "
        "existing evaluation reports for the same document.\n\n"
        "You will receive:\n"
        "1. The original document text\n"
        "2. Evaluation A (from the source database, merge from)\n"
        "3. Evaluation B (from the target database, merge into)\n\n"
        "Your job is to produce a single **merged evaluation report** that:\n\n"
        "- Adds all valid statements from Evaluation A to Evaluation B, combining statements with the same stance and location\n"
        "- Combines all valid distinction rules for each combined statement to make a single distinct list containing all rules from both statements\n"
        "- Removes duplicate statements (same Stance Quote AND same Location)\n"
        "- Sides with Evaluation B (target) over Evaluation A (source) when evals cover the same statement but have opposite HL/LL alignment, AND\n"
        "  uses your judgment based on the Distinction Rules and Decision Notes to verify decisions\n"
        "- Merges all Key Topics from Evaluation A into Evaluation B, normalizing names as needed\n"
        "- Recalculates all counts, percentages, and scores from the merged HL and LL statement sets\n"
        "- Follows the full Report Specification and template from the skill file above\n\n"
        "- Does NOT include the DETAILED sections unless they are present in one or both evaluations\n"
        "Execute the Self-Verification and Post-Report Self-Check before emitting the final report.\n")
    return skill_md + instructions


def build_merge_user_prompt(doc_text: str, doc_title: Optional[str], eval_a: str, eval_b: str, source_a: str, source_b: str) -> str:
    title_part = f', titled "{doc_title}"' if doc_title else ""
    return f"""Merge the following two evaluation reports for the same document{title_part}:

--- BEGIN Original Document Text ---
{doc_text}
--- END Original Document Text ---

--- BEGIN Evaluation A ({source_a}) ---
{eval_a}
--- END Evaluation A ---

--- BEGIN Evaluation B ({source_b}) ---
{eval_b}
--- END Evaluation B ---

Produce a single merged evaluation report by following the instructions above.
Include ALL valid statements from both evaluations, removing duplicates and resolving
any classification conflicts using the Distinction Rules.
"""


def build_review_user_prompt(doc_text: str, evaluation: str, doc_title: Optional[str], verify_output: Optional[str] = None,
                              prev_llm_notes: Optional[str] = None) -> str:
    verify_section = ""
    if verify_output is not None:
        verify_section = f"""
Check and correct all issues in this verify report from a script:
--- BEGIN Automated Evaluation Verify Report ---
{verify_output}
--- END Automated Evaluation Verify Report ---

"""
    if prev_llm_notes is not None:
        prev_llm_section = f"""
The Changes Summary from the previous LLM Review is work already done, make sure all changes were actually needed and actually done:
--- BEGIN Previous LLM Review Changes Summary ---
{prev_llm_notes}
--- END Previous LLM Review Changes Summary ---

"""
        verify_section += prev_llm_section
    title_part = f', titled "{doc_title}"' if doc_title else ""
    return f"""Review the following evaluation report for this original document{title_part}:
--- BEGIN Original Document Text ---
{doc_text}
--- END Original Document Text ---

--- BEGIN Evaluation Report ---
{evaluation}
--- END Evaluation Report ---

{verify_section}
Review the Evaluation Report of the Original Document Text by following the instructions in "high-vs-low Evaluation Report Review Checklist".
"""


def run_verify_report(evaluation_text: str) -> Optional[str]:
    verify_script = os.path.join(_SCRIPTS_DIR, "verify-report.py")
    if not os.path.exists(verify_script):
        logger.info("    [script] Script not found: %s — skipping", verify_script)
        return None
    try:
        fd, tmp_path = tempfile.mkstemp(suffix=".md", text=True)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(evaluation_text)
            result = subprocess.run([sys.executable, verify_script, tmp_path], capture_output=True, text=True, timeout=30)
            output = result.stdout
            if result.stderr:
                output += result.stderr
            return output.strip()
        finally:
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

def parse_evaluation_report(report_text: Optional[str]):
    if not report_text:
        return None, None, None
    hl_match = re.search(r"High Law Aligned\s+\|?\s+(\d+)", report_text)
    ll_match = re.search(r"Low Law Aligned\s+\|?\s+(\d+)", report_text)
    if not hl_match:
        hl_match = re.search(r"### High Law Aligned \((\d+) statements?\)", report_text)
    if not ll_match:
        ll_match = re.search(r"### Low Law Aligned \((\d+) statements?\)", report_text)
    count_hl = int(hl_match.group(1)) if hl_match else 0
    count_ll = int(ll_match.group(1)) if ll_match else 0
    score = None
    score_match = re.search(r"\*\*Score\*\*.*?=\s*\*\*([+-]?\d+\.?\d*)\*\*", report_text)
    if score_match:
        score = float(score_match.group(1))
    else:
        total = count_hl + count_ll
        if total > 0:
            hl_pct = 100 * count_hl / total
            ll_pct = 100 * count_ll / total
            score = round((hl_pct - ll_pct) / 10, 1)
    return count_hl, count_ll, score


def parse_review_has_changes(changes_text: str) -> bool:
    return ("STATEMENTS_ADDED" in changes_text or "STATEMENTS_MOVED" in changes_text or "STATEMENTS_REMOVED" in changes_text)


def _is_valid_report(text: Optional[str]) -> bool:
    if not text:
        return False
    text_stripped = text.lstrip()
    if not text_stripped.startswith(_REPORT_TITLE_PREFIX):
        return False
    if _REPORT_LATE_HEADER not in text:
        return False
    return True


def parse_review_updated_eval(review_text: str) -> Optional[str]:
    title_pos = review_text.find(_REPORT_TITLE_PREFIX)
    if title_pos == -1:
        return None
    candidate = review_text[title_pos:].strip()
    marker_pos = candidate.find(EVAL_REPORT_END_MARKER)
    if marker_pos == -1:
        if _REPORT_LATE_HEADER in candidate:
            return candidate
        return None
    return candidate[:marker_pos]


def parse_review_changes_section(review_text: str) -> str:
    marker_pos = review_text.find(EVAL_REPORT_END_MARKER)
    if marker_pos == -1:
        return review_text
    return review_text[marker_pos + len(EVAL_REPORT_END_MARKER):].strip()


# ---------------------------------------------------------------------------
# Database helpers (thread-safe: each caller uses own connection)
# ---------------------------------------------------------------------------

def _get_conn(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, timeout=30)
    # TODO: is WAL a good idea? necessary for the multi-threads? gets set permanently on file once used...
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def _get_write_conn(db_path: str) -> sqlite3.Connection:
    """Get a connection with BEGIN IMMEDIATE for atomic claim operations."""
    conn = sqlite3.connect(db_path, timeout=30, isolation_level=None)
    # TODO: is WAL a good idea? necessary for the multi-threads? gets set permanently on file once used...
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("BEGIN IMMEDIATE")
    return conn


def _claim_record_for_eval(db_path: str, table: str, doc_col: str, start_id: Optional[int], where: Optional[str],
                             limit: Optional[int], max_id: Optional[int] = None) -> Optional[tuple]:
    """Atomically find and claim a record for evaluation using BEGIN IMMEDIATE.
    Returns (id, doc_title, doc_text) or None.
    max_id: if set, only claim records with id <= max_id (enforces limit)."""
    conditions = []
    params: List[Any] = []
    conditions.append("eval_status IS NULL OR eval_status = 0")
    if where:
        conditions.append(where)
    if start_id is not None:
        conditions.append("id >= ?")
        params.append(start_id)
    if max_id is not None:
        conditions.append("id <= ?")
        params.append(max_id)
    query = f"SELECT id, doc_title, {doc_col} FROM {table} WHERE {' AND '.join(conditions)} ORDER BY id LIMIT 1"
    conn = _get_write_conn(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        row = cursor.fetchone()
        if not row:
            conn.rollback()
            return None
        doc_id = row[0]
        conn.execute(f"UPDATE {table} SET eval_status = ? WHERE id = ?", (STATUS_EVAL_IN_PROGRESS, doc_id))
        conn.commit()
        return (doc_id, row[1], row[2])
    except Exception:
        conn.rollback()
        raise


def _claim_record_for_review(db_path: str, table: str, doc_col: str, start_id: Optional[int], where: Optional[str],
                               limit: Optional[int], max_id: Optional[int] = None) -> Optional[tuple]:
    """Atomically find and claim a record for review (status 2 -> 8) using BEGIN IMMEDIATE.
    Returns (id, doc_title, doc_text, evaluation) or None."""
    conditions = []
    params: List[Any] = []
    conditions.append("eval_status = 2")
    if where:
        conditions.append(where)
    if start_id is not None:
        conditions.append("id >= ?")
        params.append(start_id)
    if max_id is not None:
        conditions.append("id <= ?")
        params.append(max_id)
    query = f"SELECT id, doc_title, {doc_col}, evaluation FROM {table} WHERE {' AND '.join(conditions)} ORDER BY id LIMIT 1"
    conn = _get_write_conn(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        row = cursor.fetchone()
        if not row:
            conn.rollback()
            return None
        doc_id = row[0]
        conn.execute(f"UPDATE {table} SET eval_status = ? WHERE id = ?", (STATUS_REVIEW_IN_PROGRESS, doc_id))
        conn.commit()
        return (doc_id, row[1], row[2], row[3])
    except Exception:
        conn.rollback()
        raise


def _claim_record_for_merge_review(db_path: str, table: str, doc_col: str, start_id: Optional[int], where: Optional[str],
                                      limit: Optional[int], max_id: Optional[int] = None) -> Optional[tuple]:
    """Claim a record with status 5 for review (5 -> 8) using BEGIN IMMEDIATE."""
    conditions = ["eval_status = 5"]
    params: List[Any] = []
    if where:
        conditions.append(where)
    if start_id is not None:
        conditions.append("id >= ?")
        params.append(start_id)
    if max_id is not None:
        conditions.append("id <= ?")
        params.append(max_id)
    query = f"SELECT id, doc_title, {doc_col}, evaluation FROM {table} WHERE {' AND '.join(conditions)} ORDER BY id LIMIT 1"
    conn = _get_write_conn(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        row = cursor.fetchone()
        if not row:
            conn.rollback()
            return None
        doc_id = row[0]
        conn.execute(f"UPDATE {table} SET eval_status = ? WHERE id = ?", (STATUS_REVIEW_IN_PROGRESS, doc_id))
        conn.commit()
        return (doc_id, row[1], row[2], row[3])
    except Exception:
        conn.rollback()
        raise


def _claim_record_for_merge(db_path: str, table: str, doc_col: str, start_id: Optional[int], where: Optional[str],
                               limit: Optional[int], max_id: Optional[int] = None) -> Optional[tuple]:
    """Claim a record with status 3 for merge (3 -> 4) using BEGIN IMMEDIATE."""
    conditions = ["eval_status = 3"]
    params: List[Any] = []
    if where:
        conditions.append(where)
    if start_id is not None:
        conditions.append("id >= ?")
        params.append(start_id)
    if max_id is not None:
        conditions.append("id <= ?")
        params.append(max_id)
    query = f"SELECT id, doc_title, {doc_col}, evaluation FROM {table} WHERE {' AND '.join(conditions)} ORDER BY id LIMIT 1"
    conn = _get_write_conn(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        row = cursor.fetchone()
        if not row:
            conn.rollback()
            return None
        doc_id = row[0]
        conn.execute(f"UPDATE {table} SET eval_status = ? WHERE id = ?", (STATUS_MERGE_IN_PROGRESS, doc_id))
        conn.commit()
        return (doc_id, row[1], row[2], row[3])
    except Exception:
        conn.rollback()
        raise


def _claim_draft_for_review(conn: sqlite3.Connection, doc_id: int, draft_seq: int) -> Optional[tuple]:
    """Claim a draft record with status 2 for review (2 -> 3).
    Returns (draft_status, evaluation, count_hl, count_ll, score) or None.
    Uses conditional UPDATE to prevent race conditions."""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT draft_status, evaluation, count_hl, count_ll, score FROM doc_eval_draft WHERE doc_id = ? AND draft_seq = ? AND draft_status = ?",
        (doc_id, draft_seq, DRAFT_COMPLETE))
    row = cursor.fetchone()
    if not row:
        return None
    cursor.execute(
        "UPDATE doc_eval_draft SET draft_status = ? WHERE doc_id = ? AND draft_seq = ? AND draft_status = ?",
        (DRAFT_REVIEW_IN_PROGRESS, doc_id, draft_seq, DRAFT_COMPLETE))
    conn.commit()
    if cursor.rowcount == 0:
        return None  # Another thread claimed it first
    return row


def _claim_draft_for_eval(conn: sqlite3.Connection, doc_id: int, draft_seq: int) -> bool:
    """Claim a draft record for evaluation (0/NULL -> 1). Returns True if claimed.
    Uses conditional UPDATE to prevent race conditions."""
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE doc_eval_draft SET draft_status = ? WHERE doc_id = ? AND draft_seq = ? AND (draft_status IS NULL OR draft_status = 0)",
        (DRAFT_IN_PROGRESS, doc_id, draft_seq))
    conn.commit()
    return cursor.rowcount > 0


def _get_draft_doc_text(conn: sqlite3.Connection, table: str, doc_col: str,
                         doc_id: int) -> Optional[tuple]:
    """Get doc_text and doc_title for a draft's doc_id."""
    cursor = conn.cursor()
    cursor.execute(f"SELECT id, doc_title, {doc_col} FROM {table} WHERE id = ?", (doc_id,))
    row = cursor.fetchone()
    return row


def _save_eval_to_table(conn: sqlite3.Connection, table: str, doc_id: int, evaluation: Optional[str], count_hl: Optional[int],
                         count_ll: Optional[int], score: Optional[float]):

    assignments = []
    params: List[Any] = []
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
        return
    params.append(doc_id)
    conn.execute(f"UPDATE {table} SET {', '.join(assignments)} WHERE id = ?", params)
    conn.commit()


def _save_draft_eval(conn: sqlite3.Connection, doc_id: int, draft_seq: int, evaluation: Optional[str], count_hl: Optional[int],
                      count_ll: Optional[int], score: Optional[float]):
    assignments = []
    params: List[Any] = []
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
        return
    params.extend([doc_id, draft_seq])
    conn.execute(
        f"UPDATE doc_eval_draft SET {', '.join(assignments)} WHERE doc_id = ? AND draft_seq = ?",
        params)
    conn.commit()


def _count_status(conn: sqlite3.Connection, table: str, status: int) -> int:
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE eval_status = ?", (status,))
    return cursor.fetchone()[0]


def _count_draft_status(conn: sqlite3.Connection, draft_seq: int, status: int) -> int:
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM doc_eval_draft WHERE draft_seq = ? AND draft_status = ?",
        (draft_seq, status))
    return cursor.fetchone()[0]


def _compute_max_id_for_limit(conn: sqlite3.Connection, table: str, doc_col: str, start_id: Optional[int],
                              where: Optional[str], limit: int) -> Optional[int]:
    """Find the max ID that should be processed given a limit.
    Returns the ID of the Nth eligible record (1-indexed), or None if fewer than N exist."""
    conditions = []
    params: List[Any] = []
    conditions.append("eval_status IS NULL OR eval_status = 0")
    if where:
        conditions.append(where)
    if start_id is not None:
        conditions.append("id >= ?")
        params.append(start_id)
    query = (f"SELECT id FROM {table} WHERE {' AND '.join(conditions)} "
             f"ORDER BY id LIMIT 1 OFFSET ?")
    params.append(limit - 1)  # 0-indexed offset
    cursor = conn.cursor()
    cursor.execute(query, params)
    row = cursor.fetchone()
    return row[0] if row else None


# ---------------------------------------------------------------------------
# Workflow step functions
# ---------------------------------------------------------------------------

def _accumulate_stats(stats: dict, result: ChatResult):
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


def _empty_stats() -> dict:
    return {
        "phase_start": time.monotonic(), "total_elapsed": 0.0,
        "total_generation_time": 0.0, "total_prompt_tokens": 0,
        "total_completion_tokens": 0, "total_tokens": 0,
        "total_reasoning_tokens": 0, "total_output_tokens": 0,
    }


def _do_eval(client, doc_id: int, doc_title: Optional[str], doc_text: str, dry_run: bool, detailed: bool,
             conn_or_path, table: str, progress_cb) -> tuple:
    """Evaluate a single record. Returns (doc_id, doc_title, hl, ll, score, eval_text, error, chat_result).
    conn_or_path: either a sqlite3.Connection or a db_path string."""
    system_prompt = build_evaluation_system_prompt(detailed)
    user_prompt = build_evaluation_user_prompt(doc_text, doc_title)
    start_time = time.monotonic()

    try:
        result = client.chat_stream(system_prompt, user_prompt, progress_cb=progress_cb)
    except RuntimeError as exc:
        logger.error("    [eval] %s", exc)
        return (doc_id, doc_title, None, None, None, None, str(exc), None)

    output_tokens = (result.completion_tokens or 0) - (result.reasoning_tokens or 0)
    logger.info("    [eval] LLM: %.1fs | prompt %s reasoning %s output %s",
                result.elapsed, result.prompt_tokens, result.reasoning_tokens, output_tokens)

    eval_report = result.content.lstrip() if result.content else None
    if not eval_report:
        logger.warning("    [eval] Empty response")
        return (doc_id, doc_title, None, None, None, None, "Empty Response", result)

    count_hl, count_ll, score = parse_evaluation_report(eval_report)
    logger.info("    [eval] Result: HL=%s, LL=%s, Score=%s", count_hl, count_ll, score)

    if not dry_run:
        if isinstance(conn_or_path, sqlite3.Connection):
            _save_eval_to_table(conn_or_path, table, doc_id, eval_report, count_hl, count_ll, score)
        else:
            conn = _get_conn(conn_or_path)
            try:
                _save_eval_to_table(conn, table, doc_id, eval_report, count_hl, count_ll, score)
            finally:
                conn.close()
        logger.info("    [eval] Saved to DB (%s chars)", len(eval_report))

    return (doc_id, doc_title, count_hl, count_ll, score, eval_report, None, result)


def _do_review(client, doc_id: int, doc_title: Optional[str], doc_text: str,
               eval_text: str, dry_run: bool, conn_or_path, table: str,
               max_reviews: int, progress_cb) -> tuple:
    """Review a single record with re-execution loop.
    conn_or_path: either a sqlite3.Connection or a db_path string.
    Returns (doc_id, doc_title, orig_hl, orig_ll, orig_score, final_hl, final_ll, final_score, error, chat_result)."""
    orig_hl, orig_ll, orig_score = parse_evaluation_report(eval_text)
    final_hl, final_ll, final_score = orig_hl, orig_ll, orig_score
    final_error = None
    previous_changes_text = None
    current_eval = eval_text
    last_result = None

    for iteration in range(1, max_reviews + 1):
        logger.info("    [review pass %d]", iteration)
        verify_output = run_verify_report(current_eval)

        system_prompt = build_review_system_prompt()
        user_prompt = build_review_user_prompt(doc_text, current_eval, doc_title, verify_output, previous_changes_text)
        start_time = time.monotonic()

        try:
            result = client.chat_stream(system_prompt, user_prompt, progress_cb=progress_cb)
        except RuntimeError as exc:
            logger.error("    [review] %s", exc)
            final_error = str(exc)
            break

        last_result = result
        changes_text = parse_review_changes_section(result.content)
        previous_changes_text = changes_text
        has_changes = changes_text and parse_review_has_changes(changes_text)

        updated_eval = parse_review_updated_eval(result.content)
        updated_valid = updated_eval and _is_valid_report(updated_eval)

        if updated_valid:
            new_hl, new_ll, new_score = parse_evaluation_report(updated_eval)
        else:
            new_hl, new_ll, new_score = None, None, None

        logger.info("    [review] Valid report? %s | Changes? %s | HL %s->%s, LL %s->%s, Score %s->%s",
                     "YES" if updated_valid else "NO", "YES" if has_changes else "NO",
                     orig_hl, new_hl, orig_ll, new_ll, orig_score, new_score)

        if updated_valid:
            if not dry_run:
                if isinstance(conn_or_path, sqlite3.Connection):
                    _save_eval_to_table(conn_or_path, table, doc_id, updated_eval, new_hl, new_ll, new_score)
                else:
                    conn = _get_conn(conn_or_path)
                    try:
                        _save_eval_to_table(conn, table, doc_id, updated_eval, new_hl, new_ll, new_score)
                    finally:
                        conn.close()
            current_eval = updated_eval
            final_hl, final_ll, final_score = new_hl, new_ll, new_score

        if has_changes and updated_valid and iteration < max_reviews:
            orig_hl, orig_ll, orig_score = new_hl, new_ll, new_score
            continue

        if not updated_valid:
            final_hl, final_ll, final_score = orig_hl, orig_ll, orig_score
        break

    return (doc_id, doc_title, orig_hl, orig_ll, orig_score,
            final_hl, final_ll, final_score, final_error, last_result)


def _do_merge(client, doc_id: int, doc_title: Optional[str], doc_text: str, eval_source: str, eval_target: Optional[str], source_name: str,
              target_name: str, dry_run: bool, conn_or_path, table: str, progress_cb) -> tuple:
    """Merge two evaluations. Returns (doc_id, hl, ll, score, merged_eval, error, chat_result).
    conn_or_path: either a sqlite3.Connection or a db_path string."""
    if eval_target is None:
        logger.info("    [merge] Target has no eval — copying from source")
        count_hl, count_ll, score = parse_evaluation_report(eval_source)
        if not dry_run:
            if isinstance(conn_or_path, sqlite3.Connection):
                _save_eval_to_table(conn_or_path, table, doc_id, eval_source, count_hl, count_ll, score)
            else:
                conn = _get_conn(conn_or_path)
                try:
                    _save_eval_to_table(conn, table, doc_id, eval_source, count_hl, count_ll, score)
                finally:
                    conn.close()
        return (doc_id, count_hl, count_ll, score, eval_source, None, None)

    logger.info("    [merge] Both have evals — AI merge")
    system_prompt = build_merge_system_prompt()
    user_prompt = build_merge_user_prompt(doc_text, doc_title, eval_source, eval_target,
                                          source_name, target_name)
    start_time = time.monotonic()

    try:
        result = client.chat_stream(system_prompt, user_prompt, progress_cb=progress_cb)
    except RuntimeError as exc:
        logger.error("    [merge] %s", exc)
        return (doc_id, None, None, None, None, str(exc), None)

    merged_eval = result.content.lstrip() if result.content else None
    if not merged_eval or not _is_valid_report(merged_eval):
        logger.warning("    [merge] Invalid merged report — keeping target")
        count_hl, count_ll, score = parse_evaluation_report(eval_target)
        return (doc_id, count_hl, count_ll, score, eval_target, "Invalid merged report", result)

    count_hl, count_ll, score = parse_evaluation_report(merged_eval)
    logger.info("    [merge] Result: HL=%s, LL=%s, Score=%s", count_hl, count_ll, score)

    if not dry_run:
        if isinstance(conn_or_path, sqlite3.Connection):
            _save_eval_to_table(conn_or_path, table, doc_id, merged_eval, count_hl, count_ll, score)
        else:
            conn = _get_conn(conn_or_path)
            try:
                _save_eval_to_table(conn, table, doc_id, merged_eval, count_hl, count_ll, score)
            finally:
                conn.close()

    return (doc_id, count_hl, count_ll, score, merged_eval, None, result)


def _do_draft_merge(client, doc_id: int, doc_title: Optional[str], doc_text: str, main_eval: Optional[str], draft_eval: str, draft_name: str,
                    dry_run: bool, conn_or_path, table: str, progress_cb) -> tuple:
    """Merge a draft evaluation into the main evaluation.
    conn_or_path: either a sqlite3.Connection or a db_path string.
    Returns (hl, ll, score, merged_eval, error, chat_result)."""
    if main_eval is None:
        logger.info("    [draft-merge] No main eval — copying draft")
        count_hl, count_ll, score = parse_evaluation_report(draft_eval)
        if not dry_run:
            if isinstance(conn_or_path, sqlite3.Connection):
                _save_eval_to_table(conn_or_path, table, doc_id, draft_eval, count_hl, count_ll, score)
            else:
                conn = _get_conn(conn_or_path)
                try:
                    _save_eval_to_table(conn, table, doc_id, draft_eval, count_hl, count_ll, score)
                finally:
                    conn.close()
        return (count_hl, count_ll, score, draft_eval, None, None)

    logger.info("    [draft-merge] Merging draft '%s' into main eval", draft_name)
    system_prompt = build_merge_system_prompt()
    user_prompt = build_merge_user_prompt(doc_text, doc_title, draft_eval, main_eval,
                                          draft_name, "main")
    start_time = time.monotonic()

    try:
        result = client.chat_stream(system_prompt, user_prompt, progress_cb=progress_cb)
    except RuntimeError as exc:
        logger.error("    [draft-merge] %s", exc)
        return (None, None, None, None, str(exc), None)

    merged_eval = result.content.lstrip() if result.content else None
    if not merged_eval or not _is_valid_report(merged_eval):
        logger.warning("    [draft-merge] Invalid merged report — keeping main")
        count_hl, count_ll, score = parse_evaluation_report(main_eval)
        return (count_hl, count_ll, score, main_eval, "Invalid merged report", result)

    count_hl, count_ll, score = parse_evaluation_report(merged_eval)
    logger.info("    [draft-merge] Result: HL=%s, LL=%s, Score=%s", count_hl, count_ll, score)

    if not dry_run:
        if isinstance(conn_or_path, sqlite3.Connection):
            _save_eval_to_table(conn_or_path, table, doc_id, merged_eval, count_hl, count_ll, score)
        else:
            conn = _get_conn(conn_or_path)
            try:
                _save_eval_to_table(conn, table, doc_id, merged_eval, count_hl, count_ll, score)
            finally:
                conn.close()

    return (count_hl, count_ll, score, merged_eval, None, result)


# ---------------------------------------------------------------------------
# Thread worker functions
# ---------------------------------------------------------------------------

class ThreadStats:
    """Thread-safe stats accumulator."""
    def __init__(self):
        self._lock = threading.Lock()
        self.eval_count = 0
        self.review_count = 0
        self.merge_count = 0
        self.error_count = 0
        self.stats = _empty_stats()

    def add(self, result: ChatResult):
        with self._lock:
            _accumulate_stats(self.stats, result)

    def inc_eval(self):
        with self._lock:
            self.eval_count += 1

    def inc_review(self):
        with self._lock:
            self.review_count += 1

    def inc_merge(self):
        with self._lock:
            self.merge_count += 1

    def inc_error(self):
        with self._lock:
            self.error_count += 1

    def summary(self, name: str) -> str:
        with self._lock:
            s = self.stats
            return (f"[{name}] evals={self.eval_count} reviews={self.review_count} merges={self.merge_count} errors={self.error_count} "
                    f"time={s['total_elapsed']:.0f}s tokens=prompt={s['total_prompt_tokens']} "
                    f"reasoning={s['total_reasoning_tokens']} output={s['total_output_tokens']}")


def _update_status(db_path: str, table: str, doc_id: int, status: int):
    """Update eval_status for a record."""
    conn = _get_conn(db_path)
    try:
        conn.execute(f"UPDATE {table} SET eval_status = ? WHERE id = ?", (status, doc_id))
        conn.commit()
    finally:
        conn.close()


def worker_main_eval(client, db_path: str, table: str, doc_col: str, name: str, line_idx: int, display: MultiProgressDisplay,
                       dry_run: bool, detailed: bool, reviews: int, start_id: Optional[int], where: Optional[str],
                       limit: Optional[int], max_id: Optional[int], stats: ThreadStats, stop_event: threading.Event,
                       results_lock: threading.Lock, results: list):
    """Main endpoint worker: evaluate and review based on eval_status."""
    progress_cb = make_thread_progress_cb(display, line_idx)
    prefix = f"[{name}]"

    while not stop_event.is_set():
        try:
            # Phase 1: Try to find records ready for review (status 2 -> 8)
            row = _claim_record_for_review(db_path, table, doc_col, start_id, where, limit, max_id)
            if row:
                doc_id, doc_title, doc_text, evaluation = row
                logger.info("%s [review] ID=%s: %s", prefix, doc_id, (doc_title or "N/A")[:50])
                display.update_line(line_idx, f"{prefix} reviewing ID={doc_id} ...")

                if reviews > 0:
                    _, _, _, _, _, fhl, fll, fscore, err, chat_res = _do_review(
                        client, doc_id, doc_title, doc_text, evaluation, dry_run, db_path, table, reviews, progress_cb)
                    if chat_res:
                        stats.add(chat_res)
                    stats.inc_review()
                    if err:
                        stats.inc_error()
                        with results_lock:
                            results.append({ "doc_id": doc_id, "doc_title": doc_title, "phase": "review", "error": err,
                                "orig_hl": None, "orig_ll": None, "orig_score": None, "final_hl": fhl, "final_ll": fll, "final_score": fscore })
                        _update_status(db_path, table, doc_id, STATUS_REVIEW_IN_PROGRESS)
                        break
                    else:
                        _update_status(db_path, table, doc_id, STATUS_REVIEW_COMPLETE)
                        with results_lock:
                            results.append({ "doc_id": doc_id, "doc_title": doc_title, "phase": "review", "error": None,
                                "orig_hl": None, "orig_ll": None, "orig_score": None, "final_hl": fhl, "final_ll": fll, "final_score": fscore })
                else:
                    _update_status(db_path, table, doc_id, STATUS_REVIEW_COMPLETE)
                    logger.info("%s [review] ID=%s: SKIPPED (reviews=0)", prefix, doc_id)
                display.update_line(line_idx, f"{prefix} review done ID={doc_id}")
                continue

            # Phase 2: Try to find records to evaluate (NULL/0 -> 1 -> 2)
            row = _claim_record_for_eval(db_path, table, doc_col, start_id, where, limit, max_id)
            if row:
                doc_id, doc_title, doc_text = row
                logger.info("%s [eval] ID=%s: %s", prefix, doc_id, (doc_title or "N/A")[:50])
                display.update_line(line_idx, f"{prefix} evaluating ID={doc_id} ...")

                _, _, hl, ll, score, eval_text, err, chat_res = _do_eval(
                    client, doc_id, doc_title, doc_text, dry_run, detailed, db_path, table, progress_cb)
                if chat_res:
                    stats.add(chat_res)
                stats.inc_eval()
                if err:
                    stats.inc_error()
                    with results_lock:
                        results.append({ "doc_id": doc_id, "doc_title": doc_title, "phase": "eval", "error": err,
                            "final_hl": hl, "final_ll": ll, "final_score": score })
                    _update_status(db_path, table, doc_id, STATUS_EVAL_IN_PROGRESS)
                    break
                else:
                    _update_status(db_path, table, doc_id, STATUS_EVAL_COMPLETE)
                    with results_lock:
                        results.append({ "doc_id": doc_id, "doc_title": doc_title, "phase": "eval", "error": None,
                            "final_hl": hl, "final_ll": ll, "final_score": score })
                display.update_line(line_idx, f"{prefix} eval done ID={doc_id}")
                continue

            # No work found
            display.update_line(line_idx, f"{prefix} idle")
            # Brief sleep before retry
            for _ in range(10):
                if stop_event.is_set():
                    return
                time.sleep(0.5)
            return

        except Exception as exc:
            logger.error("%s worker error: %s", prefix, exc)
            stats.inc_error()
            time.sleep(1)


def worker_main_merge(client, source_db_path: str, db_path: str, table: str, doc_col: str, source_table: str, name: str, line_idx: int,
                        display: MultiProgressDisplay, dry_run: bool, reviews: int, start_id: Optional[int], where: Optional[str],
                        limit: Optional[int], max_id: Optional[int], stats: ThreadStats, stop_event: threading.Event,
                        results_lock: threading.Lock, results: list):
    """Main endpoint worker for merge mode: merge then review based on eval_status."""
    progress_cb = make_thread_progress_cb(display, line_idx)
    prefix = f"[{name}]"

    # Pre-step: plan merges (find status 2/5/7/9 with matching IDs in source)
    # Only thread 0 runs the merge-plan step to avoid concurrent updates
    if line_idx == 0:
        logger.info("%s [merge-plan] Planning merges from %s", prefix, source_db_path)
        src_conn = _get_conn(source_db_path)
        tgt_conn = _get_conn(db_path)
        try:
            src_cursor = src_conn.cursor()
            src_conditions = ["evaluation IS NOT NULL"]
            src_params: List[Any] = []
            if where:
                src_conditions.append(where)
            if start_id is not None:
                src_conditions.append("id >= ?")
                src_params.append(start_id)
            if max_id is not None:
                src_conditions.append("id <= ?")
                src_params.append(max_id)
            src_query = f"SELECT id FROM {source_table} WHERE {' AND '.join(src_conditions)} ORDER BY id"
            if limit:
                src_query += " LIMIT ?"
                src_params.append(limit)
            src_cursor.execute(src_query, src_params)
            source_ids = {row[0] for row in src_cursor.fetchall()}
            logger.info("[merge-plan] %d source records with evals", len(source_ids))

            if source_ids:
                placeholders = ",".join("?" for _ in source_ids)
                tgt_where = f"id IN ({placeholders}) AND eval_status IN (2, 5, 7, 9)"
                if max_id is not None:
                    tgt_where += " AND id <= ?"
                    tgt_params = [STATUS_MERGE_PLANNED] + list(source_ids) + [max_id]
                else:
                    tgt_params = [STATUS_MERGE_PLANNED] + list(source_ids)
                tgt_cursor = tgt_conn.cursor()
                tgt_cursor.execute(f"UPDATE {table} SET eval_status = ? WHERE {tgt_where}", tgt_params)
                tgt_conn.commit()
                logger.info("[merge-plan] Planned %d merges", tgt_cursor.rowcount)
        finally:
            src_conn.close()
            tgt_conn.close()

    while not stop_event.is_set():
        try:
            # Phase 1: Review merge-complete records (5 -> 8 -> 9)
            row = _claim_record_for_merge_review(db_path, table, doc_col, start_id, where, limit, max_id)
            if row:
                doc_id, doc_title, doc_text, evaluation = row
                logger.info("%s [merge-review] ID=%s: %s", prefix, doc_id, (doc_title or "N/A")[:50])
                display.update_line(line_idx, f"{prefix} merge-review ID={doc_id} ...")

                if reviews > 0:
                    _, _, _, _, _, fhl, fll, fscore, err, chat_res = _do_review(
                        client, doc_id, doc_title, doc_text, evaluation, dry_run, db_path, table, reviews, progress_cb)
                    if chat_res:
                        stats.add(chat_res)
                    stats.inc_review()
                    if err:
                        stats.inc_error()
                        _update_status(db_path, table, doc_id, STATUS_REVIEW_IN_PROGRESS)
                        break
                    else:
                        _update_status(db_path, table, doc_id, STATUS_REVIEW_COMPLETE)
                else:
                    _update_status(db_path, table, doc_id, STATUS_REVIEW_COMPLETE)
                display.update_line(line_idx, f"{prefix} merge-review done ID={doc_id}")
                continue

            # Phase 2: Merge planned records (3 -> 4 -> 5)
            row = _claim_record_for_merge(db_path, table, doc_col, start_id, where, limit, max_id)
            if row:
                doc_id, doc_title, doc_text, eval_target = row
                logger.info("%s [merge] ID=%s: %s", prefix, doc_id, (doc_title or "N/A")[:50])
                display.update_line(line_idx, f"{prefix} merging ID={doc_id} ...")

                src_conn = _get_conn(source_db_path)
                try:
                    src_cursor = src_conn.cursor()
                    src_cursor.execute(f"SELECT evaluation FROM {source_table} WHERE id = ?", (doc_id,))
                    src_row = src_cursor.fetchone()
                    eval_source = src_row[0] if src_row else None
                finally:
                    src_conn.close()

                if eval_source:
                    _, hl, ll, score, merged, err, chat_res = _do_merge(client, doc_id, doc_title, doc_text, eval_source, eval_target,
                        os.path.basename(source_db_path), os.path.basename(db_path), dry_run, db_path, table, progress_cb)
                    if chat_res:
                        stats.add(chat_res)
                    stats.inc_merge()
                    if err:
                        stats.inc_error()
                        _update_status(db_path, table, doc_id, STATUS_MERGE_IN_PROGRESS)
                        break
                    else:
                        _update_status(db_path, table, doc_id, STATUS_MERGE_COMPLETE)
                else:
                    logger.info("%s [merge] ID=%s: no source eval, skipping", prefix, doc_id)
                    _update_status(db_path, table, doc_id, STATUS_EVAL_COMPLETE)

                display.update_line(line_idx, f"{prefix} merge done ID={doc_id}")
                continue

            display.update_line(line_idx, f"{prefix} idle")
            for _ in range(10):
                if stop_event.is_set():
                    return
                time.sleep(0.5)
            return

        except Exception as exc:
            logger.error("%s worker error: %s", prefix, exc)
            stats.inc_error()
            time.sleep(1)


def worker_draft_eval(client, db_path: str, table: str, doc_col: str, name: str, line_idx: int, display: MultiProgressDisplay,
                        dry_run: bool, detailed: bool, reviews: int, draft_seq: int, stats: ThreadStats,
                        stop_event: threading.Event, results_lock: threading.Lock, results: list):
    """Draft endpoint worker: evaluate and review drafts based on draft_status."""
    progress_cb = make_thread_progress_cb(display, line_idx)
    prefix = f"[{name}]"

    while not stop_event.is_set():
        # Phase 1: Find drafts ready for review (status 2 -> 3)
        doc_id = None
        doc_title = None
        doc_text = None
        draft_eval = None
        claimed = False
        conn = _get_conn(db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT doc_id FROM doc_eval_draft WHERE draft_seq = ? AND draft_status = ?", (draft_seq, DRAFT_COMPLETE))
            rows = cursor.fetchall()
            if rows:
                doc_id = rows[0][0]
                draft_row = _claim_draft_for_review(conn, doc_id, draft_seq)
                if draft_row:
                    claimed = True
                    _, draft_eval, _, _, _ = draft_row
                    doc_row = _get_draft_doc_text(conn, table, doc_col, doc_id)
                    if not doc_row:
                        logger.error("%s [draft-review] ID=%s: doc not found", prefix, doc_id)
                        conn.execute("UPDATE doc_eval_draft SET draft_status = ? WHERE doc_id = ? AND draft_seq = ?",
                            (DRAFT_REVIEW_IN_PROGRESS, doc_id, draft_seq))
                        conn.commit()
                        doc_id = None  # prevent double-close
                        break
                    _, doc_title, doc_text = doc_row
        finally:
            conn.close()

        if claimed and doc_id is not None:
            logger.info("%s [draft-review] doc_id=%s draft_seq=%d: %s", prefix, doc_id, draft_seq, (doc_title or "N/A")[:50])
            display.update_line(line_idx, f"{prefix} draft-review doc={doc_id} ...")

            # Close conn before LLM call; pass db_path instead
            if reviews > 0:
                _, _, _, _, _, fhl, fll, fscore, err, chat_res = _do_review(
                    client, doc_id, doc_title, doc_text, draft_eval, dry_run, db_path, table, reviews, progress_cb)
                if chat_res:
                    stats.add(chat_res)
                stats.inc_review()
                if err:
                    stats.inc_error()
                    conn2 = _get_conn(db_path)
                    try:
                        conn2.execute(
                            "UPDATE doc_eval_draft SET draft_status = ? WHERE doc_id = ? AND draft_seq = ?",
                            (DRAFT_REVIEW_IN_PROGRESS, doc_id, draft_seq))
                        conn2.commit()
                    finally:
                        conn2.close()
                    break
                else:
                    conn2 = _get_conn(db_path)
                    try:
                        if not dry_run:
                            _save_draft_eval(conn2, doc_id, draft_seq, None, fhl, fll, fscore)
                        conn2.execute(
                            "UPDATE doc_eval_draft SET draft_status = ? WHERE doc_id = ? AND draft_seq = ?",
                            (DRAFT_REVIEW_COMPLETE, doc_id, draft_seq))
                        conn2.commit()
                    finally:
                        conn2.close()
            else:
                conn2 = _get_conn(db_path)
                try:
                    conn2.execute(
                        "UPDATE doc_eval_draft SET draft_status = ? WHERE doc_id = ? AND draft_seq = ?",
                        (DRAFT_REVIEW_COMPLETE, doc_id, draft_seq))
                    conn2.commit()
                finally:
                    conn2.close()

            display.update_line(line_idx, f"{prefix} draft-review done doc={doc_id}")
            continue

        # Phase 2: Find drafts to evaluate (0/NULL -> 1 -> 2)
        if not claimed:
            doc_id = None
            doc_title = None
            doc_text = None
            conn = _get_conn(db_path)
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT doc_id FROM doc_eval_draft WHERE draft_seq = ? "
                    "AND (draft_status IS NULL OR draft_status = 0) ORDER BY doc_id",
                    (draft_seq,))
                rows = cursor.fetchall()
                if rows:
                    doc_id = rows[0][0]
                    if _claim_draft_for_eval(conn, doc_id, draft_seq):
                        doc_row = _get_draft_doc_text(conn, table, doc_col, doc_id)
                        if not doc_row:
                            logger.error("%s [draft-eval] ID=%s: doc not found", prefix, doc_id)
                            doc_id = None
                            break
                        _, doc_title, doc_text = doc_row
                    else:
                        # Lost race to another thread — break and retry from loop top
                        break
            finally:
                conn.close()

            if doc_id is not None:
                logger.info("%s [draft-eval] doc_id=%s draft_seq=%d: %s",
                            prefix, doc_id, draft_seq, (doc_title or "N/A")[:50])
                display.update_line(line_idx, f"{prefix} draft-eval doc={doc_id} ...")

                # Close conn before LLM call; pass db_path instead
                _, _, hl, ll, score, eval_text, err, chat_res = _do_eval(
                    client, doc_id, doc_title, doc_text, dry_run, detailed, db_path, table, progress_cb)
                if chat_res:
                    stats.add(chat_res)
                stats.inc_eval()
                if err:
                    stats.inc_error()
                    conn2 = _get_conn(db_path)
                    try:
                        conn2.execute(
                            "UPDATE doc_eval_draft SET draft_status = ? WHERE doc_id = ? AND draft_seq = ?",
                            (DRAFT_IN_PROGRESS, doc_id, draft_seq))
                        conn2.commit()
                    finally:
                        conn2.close()
                    break
                else:
                    conn2 = _get_conn(db_path)
                    try:
                        if not dry_run:
                            _save_draft_eval(conn2, doc_id, draft_seq,
                                              eval_text, hl, ll, score)
                        conn2.execute(
                            "UPDATE doc_eval_draft SET draft_status = ? WHERE doc_id = ? AND draft_seq = ?",
                            (DRAFT_COMPLETE, doc_id, draft_seq))
                        conn2.commit()
                    finally:
                        conn2.close()

                display.update_line(line_idx, f"{prefix} draft-eval done doc={doc_id}")
                continue

        display.update_line(line_idx, f"{prefix} idle")
        for _ in range(10):
            if stop_event.is_set():
                return
            time.sleep(0.5)
        return


def worker_draft_merge(client, db_path: str, table: str, doc_col: str, name: str, line_idx: int, display: MultiProgressDisplay,
                        dry_run: bool, reviews: int, all_draft_seqs: List[int], stats: ThreadStats, stop_event: threading.Event,
                        results_lock: threading.Lock, results: list, num_draft_threads: int):
    """Merge/main thread for drafts: merge draft evals into main, then review."""
    progress_cb = make_thread_progress_cb(display, line_idx)
    prefix = f"[{name}-merge]"
    max_idle_iterations = 30  # ~25 seconds max wait before giving up
    idle_iterations = 0

    while not stop_event.is_set():
        # Phase 0: Check if any docs are in drafts-in-progress
        conn = _get_conn(db_path)
        try:
            in_progress = conn.execute(f"SELECT COUNT(*) FROM {table} WHERE eval_status = ?", (STATUS_DRAFTS_IN_PROGRESS,)).fetchone()[0]
        finally:
            conn.close()

        if in_progress == 0:
            display.update_line(line_idx, f"{prefix} idle (no drafts in progress)")
            for _ in range(10):
                if stop_event.is_set():
                    return
                time.sleep(0.5)
            return

        # Phase 1: Find docs where all drafts are review-complete and need merge
        # Collect all needed data, then close conn before LLM calls
        found_merge = False
        work_item = None  # (doc_id, doc_title, doc_text, main_eval, draft_evals, is_retry)
        for draft_seq in all_draft_seqs:
            conn = _get_conn(db_path)
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT DISTINCT d.doc_id FROM doc_eval_draft d JOIN documents doc ON d.doc_id = doc.id "
                    "WHERE d.draft_seq = ? AND d.draft_status = ? AND doc.eval_status = ?",
                    (draft_seq, DRAFT_REVIEW_COMPLETE, STATUS_DRAFTS_IN_PROGRESS))
                rows = cursor.fetchall()
            finally:
                conn.close()

            for row in rows:
                doc_id = row[0]
                # Collect data needed for merge/review
                conn = _get_conn(db_path)
                try:
                    cursor = conn.cursor()
                    # Skip if already merged (all drafts at status 6)
                    already_merged = cursor.execute(
                        "SELECT COUNT(*) FROM doc_eval_draft WHERE doc_id = ? AND draft_status = ?",
                        (doc_id, DRAFT_MERGE_COMPLETE)).fetchone()[0]
                    if already_merged == len(all_draft_seqs):
                        doc_status = cursor.execute(f"SELECT eval_status FROM {table} WHERE id = ?", (doc_id,)).fetchone()[0]
                        if doc_status in (STATUS_REVIEW_COMPLETE, STATUS_DRAFTS_COMPLETE):
                            continue
                        elif doc_status == STATUS_REVIEW_IN_PROGRESS:
                            doc_row = _get_draft_doc_text(conn, table, doc_col, doc_id)
                            if not doc_row:
                                continue
                            _, doc_title, doc_text = doc_row
                            main_eval = cursor.execute(f"SELECT evaluation FROM {table} WHERE id = ?", (doc_id,)).fetchone()
                            main_eval = main_eval[0] if main_eval else None
                            work_item = (doc_id, doc_title, doc_text, main_eval, None, True)
                            found_merge = True
                            break
                    else:
                        pending = cursor.execute(
                            "SELECT COUNT(*) FROM doc_eval_draft WHERE doc_id = ? AND draft_status != ?",
                            (doc_id, DRAFT_REVIEW_COMPLETE)).fetchone()[0]
                        if pending == 0:
                            doc_row = _get_draft_doc_text(conn, table, doc_col, doc_id)
                            if not doc_row:
                                continue
                            _, doc_title, doc_text = doc_row
                            main_eval = cursor.execute(f"SELECT evaluation FROM {table} WHERE id = ?", (doc_id,)).fetchone()
                            main_eval = main_eval[0] if main_eval else None
                            # Collect draft evals
                            draft_evals = {}
                            for ds in all_draft_seqs:
                                de = cursor.execute("SELECT evaluation FROM doc_eval_draft WHERE doc_id = ? AND draft_seq = ?", (doc_id, ds)).fetchone()
                                draft_evals[ds] = de[0] if de else None
                            work_item = (doc_id, doc_title, doc_text, main_eval, draft_evals, False)
                            found_merge = True
                            break
                finally:
                    conn.close()

                if found_merge:
                    break
            if found_merge:
                break

        if found_merge and work_item:
            doc_id, doc_title, doc_text, main_eval, draft_evals, is_retry = work_item
            if is_retry:
                logger.info("%s [draft-review-retry] doc_id=%s: retrying post-draft review", prefix, doc_id)
                display.update_line(line_idx, f"{prefix} retry review doc={doc_id} ...")

                if reviews > 0:
                    _, _, _, _, _, fhl, fll, fscore, err, chat_res = _do_review(
                        client, doc_id, doc_title, doc_text, main_eval, dry_run,
                        db_path, table, reviews, progress_cb)
                    if chat_res:
                        stats.add(chat_res)
                    stats.inc_review()
                    if err:
                        stats.inc_error()
                        display.update_line(line_idx, f"{prefix} review retry failed doc={doc_id}")
                        time.sleep(2)
                        continue
                    else:
                        conn = _get_conn(db_path)
                        try:
                            _save_eval_to_table(conn, table, doc_id, main_eval, fhl, fll, fscore)
                            conn.execute(f"UPDATE {table} SET eval_status = ? WHERE id = ?", (STATUS_REVIEW_COMPLETE, doc_id))
                            conn.commit()
                        finally:
                            conn.close()
                        display.update_line(line_idx, f"{prefix} retry review done doc={doc_id}")
                        idle_iterations = 0
                        continue
                else:
                    conn = _get_conn(db_path)
                    try:
                        conn.execute(f"UPDATE {table} SET eval_status = ? WHERE id = ?", (STATUS_DRAFTS_COMPLETE, doc_id))
                        conn.commit()
                    finally:
                        conn.close()
                    display.update_line(line_idx, f"{prefix} done (no review) doc={doc_id}")
                    idle_iterations = 0
                    continue

            # New merge
            logger.info("%s [draft-merge] doc_id=%s: merging %d drafts", prefix, doc_id, len(all_draft_seqs))
            display.update_line(line_idx, f"{prefix} merging doc={doc_id} ...")

            current_eval = main_eval
            for ds in all_draft_seqs:
                de = draft_evals.get(ds)
                if de:
                    dn = f"draft-{ds}"
                    hl, ll, score, merged, err, chat_res = _do_draft_merge(client, doc_id, doc_title, doc_text,
                        current_eval, de, dn, dry_run, db_path, table, progress_cb)
                    if chat_res:
                        stats.add(chat_res)
                    stats.inc_merge()
                    if err:
                        stats.inc_error()
                    current_eval = merged
                    if not dry_run:
                        conn = _get_conn(db_path)
                        try:
                            _save_eval_to_table(conn, table, doc_id, merged, hl, ll, score)
                        finally:
                            conn.close()

            # Mark all drafts as merge-complete
            conn = _get_conn(db_path)
            try:
                for ds in all_draft_seqs:
                    conn.execute("UPDATE doc_eval_draft SET draft_status = ? WHERE doc_id = ? AND draft_seq = ?", (DRAFT_MERGE_COMPLETE, doc_id, ds))
                conn.commit()
            finally:
                conn.close()

            if reviews > 0:
                conn = _get_conn(db_path)
                try:
                    conn.execute(f"UPDATE {table} SET eval_status = ? WHERE id = ?", (STATUS_REVIEW_IN_PROGRESS, doc_id))
                    conn.commit()
                finally:
                    conn.close()

                logger.info("%s [draft-review] doc_id=%s: post-draft review", prefix, doc_id)
                display.update_line(line_idx, f"{prefix} post-draft review doc={doc_id} ...")

                _, _, _, _, _, fhl, fll, fscore, err, chat_res = _do_review(
                    client, doc_id, doc_title, doc_text, current_eval, dry_run, db_path, table, reviews, progress_cb)
                if chat_res:
                    stats.add(chat_res)
                stats.inc_review()
                if err:
                    stats.inc_error()
                    conn = _get_conn(db_path)
                    try:
                        conn.execute(f"UPDATE {table} SET eval_status = ? WHERE id = ?", (STATUS_REVIEW_IN_PROGRESS, doc_id))
                        conn.commit()
                    finally:
                        conn.close()
                else:
                    conn = _get_conn(db_path)
                    try:
                        conn.execute(f"UPDATE {table} SET eval_status = ? WHERE id = ?", (STATUS_REVIEW_COMPLETE, doc_id))
                        conn.commit()
                    finally:
                        conn.close()
            else:
                conn = _get_conn(db_path)
                try:
                    conn.execute(f"UPDATE {table} SET eval_status = ? WHERE id = ?", (STATUS_DRAFTS_COMPLETE, doc_id))
                    conn.commit()
                finally:
                    conn.close()

            display.update_line(line_idx, f"{prefix} merge+review done doc={doc_id}")
            idle_iterations = 0
            continue

        # Phase 2: Check if any drafts are still in progress
        conn = _get_conn(db_path)
        try:
            pending = conn.execute(
                "SELECT COUNT(*) FROM doc_eval_draft d JOIN documents doc ON d.doc_id = doc.id WHERE doc.eval_status = ? AND d.draft_status < 4",
                (STATUS_DRAFTS_IN_PROGRESS,)).fetchone()[0]
        finally:
            conn.close()

        if pending > 0:
            idle_iterations += 1
            if idle_iterations >= max_idle_iterations:
                logger.warning("%s drafts stuck for %d iterations, aborting",
                               prefix, idle_iterations)
                conn = _get_conn(db_path)
                try:
                    conn.execute(
                        "UPDATE doc_eval_draft SET draft_status = ? "
                        "WHERE draft_status IN (1, 2) AND doc_id IN ("
                        f"SELECT id FROM {table} WHERE eval_status = ?)",
                        (DRAFT_REVIEW_COMPLETE, STATUS_DRAFTS_IN_PROGRESS))
                    conn.commit()
                finally:
                    conn.close()
                display.update_line(line_idx, f"{prefix} drafts timed out, marking complete")
                continue
            display.update_line(line_idx, f"{prefix} waiting for {pending} pending drafts...")
            time.sleep(5)
            continue
        else:
            display.update_line(line_idx, f"{prefix} all drafts done, no merge needed")
            for _ in range(10):
                if stop_event.is_set():
                    return
                time.sleep(0.5)
            return


# ---------------------------------------------------------------------------
# Config loading
# ---------------------------------------------------------------------------

def normalize_endpoint(endpoint: str) -> str:
    """If endpoint is just an IP/host, build a full URL."""
    if "://" not in endpoint:
        return f"{DEFAULT_EP_NO_URL_PREFIX}{endpoint}{DEFAULT_EP_NO_URL_SUFFIX}"
    return endpoint


def load_yaml_config(path: str) -> dict:
    """Load configuration from a YAML file."""
    if yaml is None:
        logger.error("PyYAML is required to load .yml config files. Install with: pip install pyyaml")
        sys.exit(1)
    with open(path, "r") as f:
        config = yaml.safe_load(f)
    return config or {}


def build_args_from_config(config: dict) -> argparse.Namespace:
    """Build argparse.Namespace from YAML config dict."""
    defaults = {
        "db_path": config.get("db"),
        "limit": config.get("limit"),
        "start_id": config.get("start-id"),
        "endpoint": config.get("endpoint", os.environ.get("OPENAI_ENDPOINT", DEFAULT_ENDPOINT)),
        "api_key": config.get("api-key", os.environ.get("OPENAI_API_KEY", "")),
        "model": config.get("model", ""),
        "stub": config.get("stub", False),
        "skip_review": config.get("skip-review", False),
        "skip_evaluation": config.get("skip-evaluation", False),
        "merge_from": config.get("merge-from"),
        "dry_run": config.get("dry-run", False),
        "reset": config.get("reset", False),
        "reset_only": config.get("reset-only", False),
        "where": config.get("where"),
        "table": config.get("table"),
        "document_column": config.get("document-column", DEFAULT_DOCUMENT_COLUMN),
        "detailed": config.get("detailed", False),
        "parallel": config.get("parallel", 1),
        "reviews": config.get("reviews", 3),
        "name": config.get("name", "main"),
        "drafts": config.get("drafts", []),
    }
    return argparse.Namespace(**defaults)


def parse_cli_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Threaded Database Delegation Workflow for High Law vs Low Law evaluation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("db_path", nargs="?", help="Path to SQLite database or .yml config file")
    parser.add_argument("--limit", type=int, default=None, help="Process only first N records")
    parser.add_argument("--start-id", type=int, default=None, help="Start from this record ID")
    parser.add_argument("--endpoint", default=os.environ.get("OPENAI_ENDPOINT", DEFAULT_ENDPOINT), help="OpenAI-compatible endpoint URL")
    parser.add_argument("--api-key", default=os.environ.get("OPENAI_API_KEY", ""), help="API key")
    parser.add_argument("--model", default="", help="Model name")
    parser.add_argument("--name", default="main", help="Human-readable name for this endpoint")
    parser.add_argument("--stub", action="store_true", help="Use stub AI client")
    parser.add_argument("--skip-review", action="store_true", help="Skip the review phase")
    parser.add_argument("--skip-evaluation", action="store_true", help="Skip the evaluation phase")
    parser.add_argument("--merge-from", default=None, metavar="DB", help="Merge evaluations from another database")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without modifying DB")
    parser.add_argument("--reset", action="store_true", help="Reset evaluation data before processing")
    parser.add_argument("--reset-only", action="store_true", help="Only reset evaluation data and exit")
    parser.add_argument("--where", default=None, help="SQL WHERE clause (without 'WHERE')")
    parser.add_argument("--table", default=None, help="Table name to use")
    parser.add_argument("--document-column", default=DEFAULT_DOCUMENT_COLUMN, help=f"Column containing document text (default: {DEFAULT_DOCUMENT_COLUMN})")
    parser.add_argument("--detailed", action="store_true", help="Produce detailed evaluation reports")
    parser.add_argument("--parallel", type=int, default=1, help="Number of threads for main endpoint (default: 1)")
    parser.add_argument("--reviews", type=int, default=3, help="Number of review iterations (default: 3; 0 = skip reviews)")
    return parser.parse_args(argv)


def merge_cli_over_yaml(yaml_args: argparse.Namespace, cli_args: argparse.Namespace) -> argparse.Namespace:
    """Override YAML config with explicit CLI args (non-default values)."""
    # If CLI has non-default values, override YAML
    overrides = {
        "db_path": cli_args.db_path if cli_args.db_path and not cli_args.db_path.endswith((".yml", ".yaml")) else yaml_args.db_path,
        "limit": cli_args.limit if cli_args.limit is not None else yaml_args.limit,
        "start_id": cli_args.start_id if cli_args.start_id is not None else yaml_args.start_id,
        "endpoint": cli_args.endpoint if cli_args.endpoint != os.environ.get("OPENAI_ENDPOINT", DEFAULT_ENDPOINT) else yaml_args.endpoint,
        "api_key": cli_args.api_key if cli_args.api_key != os.environ.get("OPENAI_API_KEY", "") else yaml_args.api_key,
        "model": cli_args.model if cli_args.model else yaml_args.model,
        "name": cli_args.name if cli_args.name != "main" else yaml_args.name,
        "stub": cli_args.stub or yaml_args.stub,
        "skip_review": cli_args.skip_review or yaml_args.skip_review,
        "skip_evaluation": cli_args.skip_evaluation or yaml_args.skip_evaluation,
        "merge_from": cli_args.merge_from or yaml_args.merge_from,
        "dry_run": cli_args.dry_run or yaml_args.dry_run,
        "reset": cli_args.reset or yaml_args.reset,
        "reset_only": cli_args.reset_only or yaml_args.reset_only,
        "where": cli_args.where or yaml_args.where,
        "table": cli_args.table or yaml_args.table,
        "document_column": cli_args.document_column if cli_args.document_column != DEFAULT_DOCUMENT_COLUMN else yaml_args.document_column,
        "detailed": cli_args.detailed or yaml_args.detailed,
        "parallel": cli_args.parallel if cli_args.parallel != 1 else yaml_args.parallel,
        "reviews": cli_args.reviews if cli_args.reviews != 3 else yaml_args.reviews,
    }
    # drafts only from YAML
    overrides["drafts"] = yaml_args.drafts
    return argparse.Namespace(**overrides)


# ---------------------------------------------------------------------------
# Schema / DB initialization
# ---------------------------------------------------------------------------

def discover_schema(conn: sqlite3.Connection, table: str, doc_col: str):
    """Verify required columns exist."""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table,))
    row = cursor.fetchone()
    if not row:
        logger.error("Table '%s' not found in the database.", table)
        sys.exit(1)
    schema = row[0]
    logger.info("[db-init] Schema: %s", schema)

    required = {"id", doc_col, "evaluation", "count_hl", "count_ll", "score"}
    found = {m[0] for m in re.findall(r"(\w+)\s+(TEXT|INTEGER|REAL)", schema, re.IGNORECASE)}
    missing = required - found
    if missing:
        logger.error("[db-init] Missing required columns: %s", missing)
        sys.exit(1)

    # Check for eval_status column
    if "eval_status" not in found:
        logger.warning("[db-init] eval_status column not found, adding it...")
        conn.execute(f"ALTER TABLE {table} ADD COLUMN eval_status INTEGER")
        conn.commit()
        logger.info("[db-init] Added eval_status column")

    logger.info("[db-init] All required columns present")


def preview_records(conn: sqlite3.Connection, table: str, doc_col: str, start_id: Optional[int], where: Optional[str], limit: Optional[int]):
    """Preview record counts and ranges."""
    cursor = conn.cursor()
    cursor.execute(f"SELECT MIN(id), MAX(id), COUNT(*) FROM {table}")
    min_id, max_id, total = cursor.fetchone()

    cursor.execute(
        f"SELECT AVG(LENGTH({doc_col})), MIN(LENGTH({doc_col})), MAX(LENGTH({doc_col})) FROM {table}")
    avg_len, min_len, max_len = cursor.fetchone()

    cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE evaluation IS NOT NULL")
    evaluated = cursor.fetchone()[0]

    cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE evaluation IS NULL")
    unevaluated = cursor.fetchone()[0]

    # Count by status
    statuses = {}
    cursor.execute(
        f"SELECT eval_status, COUNT(*) FROM {table} GROUP BY eval_status")
    for status, count in cursor.fetchall():
        statuses[status] = count

    logger.info("Record preview:")
    logger.info("  ID range: %s - %s", min_id, max_id)
    logger.info("  Total records: %s", total)
    logger.info("  Text lengths: avg=%.0f, min=%s, max=%s", avg_len, min_len, max_len)
    logger.info("  Already evaluated: %s", evaluated)
    logger.info("  Unevaluated: %s", unevaluated)
    logger.info("  Status distribution: %s", statuses)

    # Count eligible
    conditions = []
    params: List[Any] = []
    conditions.append("evaluation IS NULL")
    if where:
        conditions.append(where)
    if start_id is not None:
        conditions.append("id >= ?")
        params.append(start_id)
    cursor.execute(
        f"SELECT COUNT(*) FROM {table} WHERE {' AND '.join(conditions)}", params)
    eligible = cursor.fetchone()[0]
    if limit and limit < eligible:
        eligible = limit
    logger.info("  Records to process: %s", eligible)


def reset_evaluations(conn: sqlite3.Connection, table: str, where: Optional[str], dry_run: bool):
    """Reset evaluation columns."""
    if dry_run:
        logger.info("[Dry-run] Would reset evaluations.")
        return
    query = f"UPDATE {table} SET evaluation = NULL, count_hl = NULL, count_ll = NULL, score = NULL, eval_status = NULL"
    if where:
        query += f" WHERE {where}"
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    logger.info("[Reset] Cleared evaluations for %s records.", cursor.rowcount)


# ---------------------------------------------------------------------------
# Draft preparation
# ---------------------------------------------------------------------------

def prepare_drafts(conn: sqlite3.Connection, table: str, doc_col: str, drafts_config: List[dict], start_id: Optional[int],
                    where: Optional[str], limit: Optional[int]):
    """Create doc_eval_draft records and set eval_status for draft workflow."""
    if not drafts_config:
        return

    cursor = conn.cursor()

    # Get doc IDs to process
    conditions = []
    params: List[Any] = []
    conditions.append("evaluation IS NULL")
    if where:
        conditions.append(where)
    if start_id is not None:
        conditions.append("id >= ?")
        params.append(start_id)
    query = f"SELECT id FROM {table} WHERE {' AND '.join(conditions)} ORDER BY id"
    if limit:
        query += " LIMIT ?"
        params.append(limit)
    cursor.execute(query, params)
    doc_ids = [row[0] for row in cursor.fetchall()]
    logger.info("[drafts] %d documents to draft-evaluate", len(doc_ids))

    if not doc_ids:
        return

    # Create draft records
    for i, draft_cfg in enumerate(drafts_config):
        draft_seq = i
        for doc_id in doc_ids:
            cursor.execute("INSERT OR IGNORE INTO doc_eval_draft (doc_id, draft_seq, draft_status) VALUES (?, ?, ?)",
                (doc_id, draft_seq, DRAFT_PLANNED))
        conn.commit()
        logger.info("[drafts] Created draft_seq=%d records for '%s'", draft_seq, draft_cfg.get("name", f"draft-{draft_seq}"))

    # Set eval_status to 6 (drafts-in-progress) for these docs
    placeholders = ",".join("?" for _ in doc_ids)
    conn.execute(f"UPDATE {table} SET eval_status = ? WHERE id IN ({placeholders})", [STATUS_DRAFTS_IN_PROGRESS] + doc_ids)
    conn.commit()
    logger.info("[drafts] Set eval_status=6 for %d documents", len(doc_ids))


# ---------------------------------------------------------------------------
# Summary reporting
# ---------------------------------------------------------------------------

def print_summary(results: list, thread_stats: List[tuple], db_path: str, table: str):
    """Print final summary report."""
    logger.info("=" * 80)
    logger.info("Summary Report")
    logger.info("=" * 80)

    # Per-thread stats
    for name, stats in thread_stats:
        logger.info("%s", stats.summary(name))

    # Results by doc
    logger.info("")
    logger.info("RESULTS BY DOCUMENT:")
    logger.info("  %6s  %-45s  %-10s  %6s  %6s  %8s  %s", "ID", "Title", "Phase", "HL", "LL", "Score", "Error")
    logger.info("  " + "-" * 100)

    # Group by doc_id
    by_doc: Dict[int, dict] = {}
    for r in results:
        doc_id = r.get("doc_id")
        if doc_id is None:
            continue
        if doc_id not in by_doc:
            by_doc[doc_id] = {"title": r.get("doc_title", ""), "entries": []}
        by_doc[doc_id]["entries"].append(r)

    for doc_id in sorted(by_doc.keys()):
        info = by_doc[doc_id]
        title = (info["title"] or "N/A")[:43]
        for entry in info["entries"]:
            phase = entry.get("phase", "")
            hl = entry.get("final_hl")
            ll = entry.get("final_ll")
            score = entry.get("final_score")
            err = entry.get("error", "")
            hl_s = str(hl) if hl is not None else "N/A"
            ll_s = str(ll) if ll is not None else "N/A"
            score_s = f"{score:.1f}" if score is not None else "N/A"
            err_s = (err or "")[:15]
            logger.info("  %6d  %-45s  %-10s  %6s  %6s  %8s  %s",
                        doc_id, title, phase, hl_s, ll_s, score_s, err_s)

    logger.info("")
    logger.info("Workflow complete.")


def print_final_status(db_path: str, table: str):
    """Print final status distribution."""
    conn = _get_conn(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT eval_status, COUNT(*) FROM {table} GROUP BY eval_status ORDER BY eval_status")
        logger.info("Final status distribution:")
        status_names = {
            None: "planned/null", 0: "planned", 1: "eval-ing", 2: "eval-done",
            3: "merge-planned", 4: "merge-ing", 5: "merge-done",
            6: "drafts-ing", 7: "drafts-done", 8: "review-ing", 9: "review-done",
        }
        for status, count in cursor.fetchall():
            label = status_names.get(status, f"unknown({status})")
            logger.info("  status %s (%s): %d", status, label, count)

        # Draft status
        cursor.execute(
            "SELECT draft_status, COUNT(*) FROM doc_eval_draft GROUP BY draft_status ORDER BY draft_status")
        draft_names = {
            None: "planned/null", 0: "planned", 1: "draft-ing", 2: "draft-done",
            3: "review-ing", 4: "review-done", 5: "merge-ing", 6: "merge-done",
        }
        draft_rows = cursor.fetchall()
        if draft_rows:
            logger.info("Draft status distribution:")
            for status, count in draft_rows:
                label = draft_names.get(status, f"unknown({status})")
                logger.info("  status %s (%s): %d", status, label, count)
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    # Check if first arg is a YAML file
    argv = sys.argv[1:]
    yaml_config = {}
    use_yaml = False

    if argv and argv[0].endswith((".yml", ".yaml")):
        use_yaml = True
        yaml_config = load_yaml_config(argv[0])
        yaml_args = build_args_from_config(yaml_config)
        # Parse remaining CLI args (skip the yaml file path)
        cli_args = parse_cli_args(argv[1:])
        args = merge_cli_over_yaml(yaml_args, cli_args)
    else:
        args = parse_cli_args(argv)
        args.drafts = []
        args.parallel = getattr(args, "parallel", 1)
        args.reviews = getattr(args, "reviews", 3)
        args.name = getattr(args, "name", "main")

    # Handle --skip-review -> reviews=0
    if args.skip_review:
        args.reviews = 0

    # Normalize endpoint
    args.endpoint = normalize_endpoint(args.endpoint)

    # Setup logging
    db_path = args.db_path
    if not db_path:
        logger.error("Database path or YAML config file is required")
        sys.exit(1)

    setup_logging(db_path)

    # Validate database
    if not os.path.exists(db_path):
        logger.error("Database not found: %s", db_path)
        sys.exit(1)

    conn = _get_conn(db_path)
    try:
        # Resolve table name
        if not args.table:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            tables = [row[0] for row in cursor.fetchall()]
            if len(tables) == 1:
                args.table = tables[0]
            elif DEFAULT_DOCUMENTS_TABLE in tables:
                args.table = DEFAULT_DOCUMENTS_TABLE
            else:
                logger.error("Database has %d tables. Specify --table.", len(tables))
                if tables:
                    logger.error("  Available: %s", ", ".join(tables))
                sys.exit(1)
        logger.info("[db-init] Table: %s, Doc column: %s", args.table, args.document_column)

        discover_schema(conn, args.table, args.document_column)
        preview_records(conn, args.table, args.document_column, args.start_id, args.where, args.limit)

        # Reset if requested
        if args.reset or args.reset_only:
            reset_evaluations(conn, args.table, args.where, args.dry_run)
            if args.reset_only:
                logger.info("Reset complete. Exiting.")
                return

        # Handle drafts
        drafts_config = args.drafts if hasattr(args, "drafts") else []
        has_drafts = bool(drafts_config)

        if has_drafts:
            prepare_drafts(conn, args.table, args.document_column, drafts_config, args.start_id, args.where, args.limit)

    finally:
        conn.close()

    # Determine mode
    is_merge_mode = bool(args.merge_from)
    is_draft_mode = has_drafts

    # Compute max_id for limit enforcement (not for draft mode since drafts handle their own limit)
    max_id: Optional[int] = None
    if args.limit and not is_draft_mode:
        conn = _get_conn(db_path)
        try:
            max_id = _compute_max_id_for_limit(conn, args.table, args.document_column, args.start_id, args.where, args.limit)
            if max_id:
                logger.info("[limit] Will process records with id <= %s (limit %d)", max_id, args.limit)
        finally:
            conn.close()

    # Normalize draft endpoints
    for i, draft_cfg in enumerate(drafts_config):
        if isinstance(draft_cfg, dict):
            ep = draft_cfg.get("endpoint", "")
            draft_cfg["endpoint"] = normalize_endpoint(ep)
            draft_cfg.setdefault("api_key", draft_cfg.get("api-key",
                os.environ.get("OPENAI_API_KEY", "")))
            draft_cfg.setdefault("model", "")
            draft_cfg.setdefault("name", f"draft-{i}")
            draft_cfg.setdefault("parallel", 1)
            draft_cfg.setdefault("reviews", 1)
            draft_cfg["draft_seq"] = i
            # Handle skip-review for drafts
            if draft_cfg.get("skip-review", False):
                draft_cfg["reviews"] = 0

    # Initialize clients
    main_client = None
    if not (args.skip_evaluation and args.skip_review and not is_merge_mode):
        if args.stub:
            main_client = StubClient()
            logger.info("[llm] Main: STUB client (%s)", args.name)
        else:
            main_client = OpenAIClient(args.endpoint, args.api_key, args.model)
            logger.info("[llm] Main: %s (%s)", args.endpoint, args.name)

    draft_clients = []
    if is_draft_mode:
        for draft_cfg in drafts_config:
            if args.stub:
                c = StubClient()
            else:
                c = OpenAIClient(draft_cfg["endpoint"], draft_cfg.get("api_key", ""), draft_cfg.get("model", ""))
            draft_clients.append(c)
            logger.info("[llm] Draft '%s': %s", draft_cfg.get("name", ""), draft_cfg["endpoint"])

    # Calculate total threads and set up progress display
    total_threads = 0
    if not is_draft_mode:
        total_threads += args.parallel
    if is_draft_mode:
        total_threads += sum(d.get("parallel", 1) for d in drafts_config)
        total_threads += 1  # merge thread

    if total_threads <= 1:
        display = MultiProgressDisplay(1)
    else:
        display = MultiProgressDisplay(total_threads)

    # Start workers
    stop_event = threading.Event()
    results_lock = threading.Lock()
    results: list = []
    threads: List[threading.Thread] = []
    thread_stats_list: List[tuple] = []

    try:
        if is_merge_mode:
            # Merge mode
            if not os.path.exists(args.merge_from):
                logger.error("Source database not found: %s", args.merge_from)
                sys.exit(1)

            # Resolve source table
            src_conn = _get_conn(args.merge_from)
            src_cursor = src_conn.cursor()
            src_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            src_tables = [row[0] for row in src_cursor.fetchall()]
            if len(src_tables) == 1:
                source_table = src_tables[0]
            elif DEFAULT_DOCUMENTS_TABLE in src_tables:
                source_table = DEFAULT_DOCUMENTS_TABLE
            else:
                source_table = args.table
            src_conn.close()

            logger.info("Merge mode: %s -> %s (%d threads)",
                         args.merge_from, db_path, args.parallel)

            for i in range(args.parallel):
                name = f"{args.name}-{i}" if args.parallel > 1 else args.name
                stats = ThreadStats()
                thread_stats_list.append((name, stats))
                t = threading.Thread(
                    target=worker_main_merge,
                    args=(main_client, args.merge_from, db_path, args.table, args.document_column, source_table, name, i,
                          display, args.dry_run, args.reviews, args.start_id, args.where, args.limit, max_id,
                          stats, stop_event, results_lock, results),
                    daemon=True,
                )
                threads.append(t)
                t.start()

        elif is_draft_mode:
            # Draft mode
            logger.info("Draft mode: %d draft endpoints, %d total threads",
                         len(drafts_config), total_threads)

            line_offset = 0
            # Start draft eval threads
            for di, draft_cfg in enumerate(drafts_config):
                parallel = draft_cfg.get("parallel", 1)
                client = draft_clients[di]
                for p in range(parallel):
                    name = f"{draft_cfg.get('name', f'draft-{di}')}-{p}" if parallel > 1 else draft_cfg.get("name", f"draft-{di}")
                    stats = ThreadStats()
                    thread_stats_list.append((name, stats))
                    t = threading.Thread(
                        target=worker_draft_eval,
                        args=(client, db_path, args.table, args.document_column, name, line_offset, display, args.dry_run, args.detailed,
                              draft_cfg.get("reviews", 1), di, stats, stop_event, results_lock, results),
                        daemon=True,
                    )
                    threads.append(t)
                    t.start()
                    line_offset += 1

            # Start draft merge thread
            merge_name = f"{args.name}-merge"
            merge_stats = ThreadStats()
            thread_stats_list.append((merge_name, merge_stats))
            num_draft_threads = sum(d.get("parallel", 1) for d in drafts_config)
            merge_t = threading.Thread(
                target=worker_draft_merge,
                args=(main_client, db_path, args.table, args.document_column, args.name, line_offset, display, args.dry_run,
                      args.reviews, list(range(len(drafts_config))), merge_stats, stop_event, results_lock, results, num_draft_threads),
                daemon=True,
            )
            threads.append(merge_t)
            merge_t.start()
            line_offset += 1

        else:
            # Normal eval mode
            logger.info("Eval mode: %d threads", args.parallel)

            for i in range(args.parallel):
                name = f"{args.name}-{i}" if args.parallel > 1 else args.name
                stats = ThreadStats()
                thread_stats_list.append((name, stats))
                t = threading.Thread(
                    target=worker_main_eval,
                    args=(main_client, db_path, args.table, args.document_column, name, i, display, args.dry_run, args.detailed,
                          args.reviews, args.start_id, args.where, args.limit, max_id, stats, stop_event, results_lock, results),
                    daemon=True,
                )
                threads.append(t)
                t.start()

        # Wait for all threads
        for t in threads:
            t.join()

    except KeyboardInterrupt:
        logger.info("Interrupted, stopping workers...")
        stop_event.set()
        for t in threads:
            t.join(timeout=5)

    finally:
        if display:
            display.finalize()
            display.newline_after()

    # Print summary
    print_summary(results, thread_stats_list, db_path, args.table)
    print_final_status(db_path, args.table)


def setup_logging(db_path: str):
    """Configure logging."""
    base, _ = os.path.splitext(db_path)
    ts = datetime.now().strftime("%Y-%m-%d-%H-%M")
    log_file = base + f".eval.{ts}.log"

    root = logging.getLogger("run-sqlite")
    root.setLevel(logging.DEBUG)
    if root.handlers:
        return

    fmt = logging.Formatter("%(asctime)s  %(levelname)-7s  %(message)s", datefmt="%H:%M:%S")

    sh = logging.StreamHandler(sys.stdout)
    sh.setLevel(logging.INFO)
    sh.setFormatter(fmt)
    root.addHandler(sh)

    fh = logging.FileHandler(log_file, mode="a", encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)
    root.addHandler(fh)


if __name__ == "__main__":
    main()
