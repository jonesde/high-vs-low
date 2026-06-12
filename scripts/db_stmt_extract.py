#!/usr/bin/env python3
"""Extract statements from markdown evaluation reports in the documents table."""

import re
import os
import sqlite3
import sys

DASH_CHARS = r"[\u2010-\u2015\u2212\-\u2013\u2014\u2015]"
DASH_RE = re.compile(DASH_CHARS)
NON_ALPHANUM_DASH = re.compile(r"[^\w\d" + DASH_CHARS[1:-1] + r"]")

def parse_rules(rules_str):
    """Parse comma-separated rules like '25-HL,23-HL' into (rule_id, law_align) tuples."""
    result = []
    for part in rules_str.split(","):
        cleaned = NON_ALPHANUM_DASH.sub("", part).strip()
        if not cleaned:
            continue
        pieces = DASH_RE.split(cleaned)
        pieces = [p.strip() for p in pieces if p.strip()]
        if len(pieces) != 2:
            continue
        digit_part = [p for p in pieces if any(c.isdigit() for c in p)]
        letter_part = [p for p in pieces if any(c.isalpha() for c in p)]
        if len(digit_part) != 1 or len(letter_part) != 1:
            continue
        rule_id = int(digit_part[0])
        law_align = 1 if letter_part[0].upper() == "HL" else 0
        result.append((rule_id, law_align))
    return result

def extract_statements(evaluation, doc_id):
    """Extract statement records from the markdown evaluation text."""
    statements = []
    sections = {
        "### High Law Aligned": 1,
        "### Low Law Aligned": 0,
    }
    for header, law_group in sections.items():
        idx = evaluation.find(header)
        if idx == -1:
            continue
        rest = evaluation[idx:]
        next_header = rest.find("\n### ", len(header))
        if next_header == -1:
            section = rest
        else:
            section = rest[:next_header]
        lines = section.split("\n")
        seq = 0
        for line in lines:
            line = line.strip()
            if not line.startswith("|") or line.startswith("|---") or line.startswith("| #"):
                continue
            cells = [c.strip() for c in line.split("|")[1:-1]]
            if len(cells) < 8:
                continue
            if not len(cells[0]) or not cells[0][0].isdigit():
                print(f"-- skipping empty/invalid row: {line}")
                continue
            seq += 1
            rules_str = cells[2]
            statements.append((doc_id, law_group, seq, rules_str, cells[3], cells[4], cells[5], cells[6], cells[7]))
    return statements

def main():
    if len(sys.argv) != 2:
        print("Usage: db_stmt_extract.py <database_path>")
        sys.exit(1)

    db_path = sys.argv[1]
    if not os.path.exists(db_path):
        print(f"Database not found: {db_path}")
        sys.exit(1)

    conn = sqlite3.connect(db_path)
    read_cur = conn.cursor()
    write_cur = conn.cursor()

    read_cur.execute("SELECT COUNT(*) FROM documents WHERE evaluation IS NOT NULL AND evaluation != ''")
    total_evals = read_cur.fetchone()[0]
    print(f"Database opened: {db_path} — {total_evals} evaluations to parse")

    eval_count = 0
    stmt_count = 0
    rule_count = 0

    read_cur.execute("SELECT id, evaluation FROM documents WHERE evaluation IS NOT NULL AND evaluation != ''")
    for doc_id, evaluation in read_cur:
        statements = extract_statements(evaluation, doc_id)
        write_cur.execute("BEGIN")
        for doc_id, law_group, seq, rules_str, decision_notes, key_topics, speaker, stance_quote, principle_quote in statements:
            write_cur.execute(
                "INSERT INTO statement (doc_id, law_group, doc_group_seq, rules, decision_notes, key_topics, speaker, stance_quote, principle_quote) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (doc_id, law_group, seq, rules_str, decision_notes, key_topics, speaker, stance_quote, principle_quote)
            )
            statement_id = write_cur.lastrowid
            parsed = parse_rules(rules_str)
            for rule_id, law_align in parsed:
                write_cur.execute(
                    "INSERT OR IGNORE INTO statement_rule (statement_id, rule_id, law_align) VALUES (?, ?, ?)",
                    (statement_id, rule_id, law_align)
                )
            stmt_count += 1
            rule_count += len(parsed)
        conn.commit()
        eval_count += 1
        if eval_count % 100 == 0:
            print(f"  {eval_count} evaluations processed — {stmt_count} statements, {rule_count} statement_rules created")

    print(f"Complete: {eval_count} evaluations processed — {stmt_count} statements, {rule_count} statement_rules created")
    conn.close()

if __name__ == "__main__":
    main()
