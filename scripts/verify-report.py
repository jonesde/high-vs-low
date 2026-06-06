#!/usr/bin/env python3
"""
Verify a high-vs-low evaluation report for internal consistency.
Usage: python3 verify_report.py <report.md>
NOTE: this does not verify the DETAILED sections of the report, those are less important and intentionally skipped.
"""
import sys, re

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 verify_report.py <report.md>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        text = f.read()

    issues = []

    # Parse HL/LL rows
    hl_section = text.split('### High Law Aligned')[1].split('### Low Law Aligned')[0] if '### High Law Aligned' in text else ''
    ll_section = text.split('### Low Law Aligned')[1].split('## Scoring Summary')[0] if '### Low Law Aligned' in text else ''
    hl_rows = [l for l in hl_section.split('\n') if re.match(r'\|\s*\d+\s*\|', l) and '---' not in l]
    ll_rows = [l for l in ll_section.split('\n') if re.match(r'\|\s*\d+\s*\|', l) and '---' not in l]

    hl_count = len(hl_rows)
    ll_count = len(ll_rows)
    total = hl_count + ll_count
    hl_pct = round(100 * hl_count / total, 1) if total > 0 else 0
    ll_pct = round(100 * ll_count / total, 1) if total > 0 else 0
    score = round((hl_pct - ll_pct) / 10, 1) if total > 0 else 0

    print(f"HL={hl_count}, LL={ll_count}, Total={total}, HL%={hl_pct}, LL%={ll_pct}, Score={score}")

    # 1. Header counts
    hl_h = re.search(r'### High Law Aligned \((\d+) statements\)', text)
    ll_h = re.search(r'### Low Law Aligned \((\d+) statements\)', text)
    if hl_h and int(hl_h.group(1)) != hl_count:
        issues.append(f"HL header {hl_h.group(1)} != actual {hl_count}")
    if ll_h and int(ll_h.group(1)) != ll_count:
        issues.append(f"LL header {ll_h.group(1)} != actual {ll_count}")

    # 2. Required fields
    for i, row in enumerate(hl_rows + ll_rows):
        parts = [p.strip() for p in row.split('|') if p.strip()]
        if len(parts) < 8:
            issues.append(f"Row {i+1}: only {len(parts)} columns (need 8)")
        elif not parts[-1].strip():
            issues.append(f"Row {i+1}: empty Decision Notes")

    # 2b. Quote length limits (hard cap 80)
    for i, row in enumerate(hl_rows + ll_rows):
        parts = [p.strip() for p in row.split('|') if p.strip()]
        if len(parts) >= 8:
            principle_quote = parts[3]
            stance_quote = parts[5]
            for label, quote in [("Principle Quote", principle_quote), ("Stance Quote", stance_quote)]:
                # Strip surrounding quotes if present
                q = quote.strip('"').strip("'")
                word_count = len(q.split())
                if word_count > 80:
                    issues.append(f"Row {i+1}: {label} exceeds hard cap ({word_count} words > 80)")

    # 3. Key Topics
    kt_list = []
    kt_section = text.split('## Key Topics\n\n')[1].split('\n\n---\n')[0] if '## Key Topics' in text else ''
    for line in kt_section.split('\n'):
        m = re.match(r'\d+\.\s+\*\*(.+?)\*\*', line)
        if m:
            kt_list.append(m.group(1))

    all_topic_refs = set()
    for row in hl_rows + ll_rows:
        parts = [p.strip() for p in row.split('|') if p.strip()]
        if len(parts) >= 7:
            for t in parts[6].split(','):
                t = t.strip()
                if t:
                    all_topic_refs.add(t)

    if all_topic_refs - set(kt_list):
        issues.append(f"Topics in statements not in list: {all_topic_refs - set(kt_list)}")
    if set(kt_list) - all_topic_refs:
        issues.append(f"Topics in list not in statements: {set(kt_list) - all_topic_refs}")
    if not (7 <= len(kt_list) <= 14):
        issues.append(f"Topic count {len(kt_list)} outside 7-14 range")

    # 4. Scoring Summary
    scoring = text.split('## Scoring Summary\n\n')[1].split('\n\n---\n')[0] if '## Scoring Summary' in text else ''
    if scoring:
        ss_hl = re.search(r'High Law Aligned\s*\|\s*(\d+)', scoring)
        ss_ll = re.search(r'Low Law Aligned\s*\|\s*(\d+)', scoring)
        ss_total = re.search(r'Total.*?\*\*(\d+)\*\*', scoring)
        ss_score = re.search(r'Score.*?=\s+\*\*(-?\d+\.?\d*)\*\*', scoring)
        if ss_hl and int(ss_hl.group(1)) != hl_count:
            issues.append(f"Scoring Summary HL {ss_hl.group(1)} != {hl_count}")
        if ss_ll and int(ss_ll.group(1)) != ll_count:
            issues.append(f"Scoring Summary LL {ss_ll.group(1)} != {ll_count}")
        if ss_total and int(ss_total.group(1)) != total:
            issues.append(f"Scoring Summary Total {ss_total.group(1)} != {total}")
        if ss_score and float(ss_score.group(1)) != score:
            issues.append(f"Scoring Summary Score {ss_score.group(1)} != {score}")

    # 5. Score Table
    score_section = text.split('## Key Topic Score Table\n\n')[1].split('\n\n---\n')[0] if '## Key Topic Score Table' in text else ''
    score_rows = [l for l in score_section.split('\n') if re.match(r'\|', l) and 'Key Topic' not in l and '---' not in l and l.strip()]
    if score_rows and len(score_rows) != len(kt_list):
        issues.append(f"Score Table rows ({len(score_rows)}) != Key Topics ({len(kt_list)})")

    # Per-topic counts
    topic_actual = {}
    for row in hl_rows:
        parts = [p.strip() for p in row.split('|') if p.strip()]
        if len(parts) >= 7:
            for t in parts[6].split(','):
                t = t.strip()
                if t:
                    topic_actual.setdefault(t, {'HL': 0, 'LL': 0})
                    topic_actual[t]['HL'] += 1
    for row in ll_rows:
        parts = [p.strip() for p in row.split('|') if p.strip()]
        if len(parts) >= 7:
            for t in parts[6].split(','):
                t = t.strip()
                if t:
                    topic_actual.setdefault(t, {'HL': 0, 'LL': 0})
                    topic_actual[t]['LL'] += 1

    for line in score_rows:
        parts = [p.strip() for p in line.split('|') if p]
        if len(parts) >= 4:
            topic = parts[0]
            hl_s, ll_s, score_s = int(parts[1]), int(parts[2]), float(parts[3])
            actual = topic_actual.get(topic, {'HL': 0, 'LL': 0})
            if hl_s != actual['HL']:
                issues.append(f"Score Table '{topic}': HL {hl_s} != actual {actual['HL']}")
            if ll_s != actual['LL']:
                issues.append(f"Score Table '{topic}': LL {ll_s} != actual {actual['LL']}")
            total_t = hl_s + ll_s
            calc = round((100*hl_s/total_t - 100*ll_s/total_t)/10, 1) if total_t > 0 else 0.0
            if score_s != calc:
                issues.append(f"Score Table '{topic}': score {score_s} != calculated {calc}")

    # Report
    if issues:
        print(f"\nISSUES FOUND ({len(issues)}):")
        for i in issues:
            print(f"  - {i}")
        sys.exit(1)
    else:
        print("\nALL CHECKS PASSED!")
        sys.exit(0)

if __name__ == '__main__':
    main()
