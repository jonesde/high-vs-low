# high-vs-low Evaluation Report Review Checklist

- Execute each validation in order.
- Execute ALL validations unless the report does not include the DETAILED section, then skip the validations of report elements in the DETAILED section.
- If one or more *Statements* is added, removed, or moved during a review pass, then re-execute starting at Section 0 (rebuild inventories first, then re-verify).
- If no iteration or depth limit is specified, limit re-execute iterations to 3

---

## 0. Build Audit Inventories

- [ ] **Automated verification**: For Markdown formatted reports run `python3 scripts/verify_report.py <report.md>` from the skill directory as an initial automated cross-check. This catches various count and score mismatches and outputs info and issues found. If any issues are found, use them to inform the complete review, do *not* use script output alone as a reason to make changes.

Before fixing anything, derive these from the report. These are your source of truth - do not trust generated summaries, headers, or narrative counts.

- [ ] `HL_rows`: actual data rows in the *High Law Aligned* table.
- [ ] `LL_rows`: actual data rows in the *Low Law Aligned* table.
- [ ] `statement_topics`: every topic assigned in each statement's *Key Topics column*.
- [ ] `topic_list`: every topic in the *Key Topics numbered list*.
- [ ] `score_table_topics`: every topic row in the *Key Topic Score Table*.
- [ ] `detail_topics`: every `### N. Topic Name` section in *Key Topic Details*.
- [ ] `narrative_scores`: every score mention outside the *Scoring Summary*.

---

## 1. Source Coverage & Statement Integrity

Validate that every normative claim in the original text was captured and classified correctly.

- [ ] **Re-scan source text for missed stances**: Identify any verse/paragraph with no `Location` reference in the report. Extract and classify all missing normative claims.
- [ ] **Split multi-claim locations**: Any source location represented by a single statement but containing **two or more distinct stances** must be split into separate statements.
- [ ] **Required fields present on every statement**: Confirm each row has `#`, `Location`, `Rules`, `Principle Quote`, `Speaker`, `Stance Quote`, `Key Topics`, and `Decision Notes`.
- [ ] **Rules are exhaustive**: The `Rules` column must list **all** relevant Distinction Rules by **concept**, not vocabulary.
- [ ] **Quote length within limits**: Every `Stance Quote` and `Principle Quote` should be under 40 words (target), with a hard cap of 80 words. Use `...` for omissions; preserve original wording and structure.
- [ ] **Topic count in range**: The numbered `Key Topics` list should contain 7–14 topics. If fewer than 7, check whether distinct themes were merged prematurely. If more than 14, merge similar/related topics.
- [ ] **Alignment 2x2 Map applied to every statement**: Re-verify that `Principle` classification, `Stance` interpretation, and `Speaker` inversion were all evaluated in order before final mapping.
- [ ] **Section placement matches Decision Notes conclusion**: For every statement, if the `Decision Notes` conclude one alignment but the physical table row sits under the opposite section header, trust the `Decision Notes` and move the row.
- [ ] **Decision Notes internal consistency**: For every statement, verify the Decision Notes reasoning actually supports the stated conclusion — the principle type (HL/LL), stance direction (support/oppose), and speaker inversion (if applied) must produce the final alignment via the 2x2 Map. Flag notes where the logic doesn't match the conclusion.
- [ ] **Speaker inversion applied once**: Verify that speaker inversion for villain/evil speakers was applied exactly once (in Step 2.3.3), not double-applied across Steps 2.3.2 and 2.3.3.
- [ ] **Tie-breaking rule applied**: For any statement where HL and LL rule counts are equal, verify there is a tie-breaking justification in Decision Notes.
- [ ] **Negation priority rule applied**: For any statement where both HL and LL negation patterns apply simultaneously, verify the High Law negation took priority.
- [ ] **[TRAP] Divine coercion check**: Search all stance quotes for divine empowerment of violence or coercion (e.g., "Lord strengthened," "slew," "slaughter," "destroy"). Any such outcome is **LL** (Rules 14-LL, 17-LL, 19-LL), never HL. Divine coercion is still coercion.
- [ ] **[TRAP] Rule 3 adversary check**: Verify that external adversaries (nature, sickness, ignorance, devil) are coded **3-HL** and interpersonal adversaries (PvP) are **3-LL**. Do not misclassify defense against external threats as LL.

---

## 2. Statement Quotes Section (HL/LL Tables)

Validate the HL and LL tables against each other and against their headers.

- [ ] **HL header count is exact**: `### High Law Aligned (N statements)` - `N` must equal `HL_rows`. Count rows manually; do not trust the header integer.
- [ ] **LL header count is exact**: `### Low Law Aligned (N statements)` - `N` must equal `LL_rows`. Count rows manually; do not trust the header integer.
- [ ] **Table structure matches template**: Column order and header text (`| # | Location | Rules | Principle Quote | Speaker | Stance Quote | Key Topics | Decision Notes |`) must match the specification exactly.
- [ ] **No empty Decision Notes cells**: Every data row contains a completed decision note. Each note should include the final alignment (HL/LL) and a one-line justification referencing the principle type and stance direction.

---

## 3. Key Topics List

Validate the numbered `Key Topics` list and its closed-loop relationship to statements.

- [ ] **Bidirectional name match (list → statements)**: Every topic string appearing in any statement's `Key Topics` column must appear in the numbered `Key Topics` list.
- [ ] **Bidirectional name match (statements → list)**: Every topic in the numbered `Key Topics` list must appear in at least one statement.
- [ ] **Zero-assignment purge complete**: Any topic with no assigned statements after audit is removed from the list, Score Table, Evaluation Table, and Key Topic Details.
- [ ] **Taxonomy format enforced**: Every topic name follows `RootCategory: SubTopic`.

---

## 4. Scoring Summary & Key Topic Score Table

Validate all numeric summaries and derived scores.

- [ ] **Scoring Summary row counts match tables**: `HL_count` equals `HL_rows`; `LL_count` equals `LL_rows`; `Total` equals their sum.
- [ ] **Scoring Summary percentages are correct**: `HL_pct = 100 × HL / Total`; `LL_pct = 100 × LL / Total`.
- [ ] **Overall Score is correct**: `Score = (HL_pct - LL_pct) / 10`, rounded to 1 decimal place.
- [ ] **Score Table row count equals topic count**: Number of data rows in the Key Topic Score Table must exactly equal the number of topics in the numbered `Key Topics` list.
- [ ] **Score Table per-topic counts match assignments**: For each topic, the HL and LL counts in the Score Table must equal the counts derived from actual statement references.
- [ ] **Score Table per-topic scores are correct**: Recalculate each topic's score using the standard formula and confirm.

---

## 5. Evaluation Highlights (DETAILED)

Validate analytical sections for factual consistency with statement data.

- [ ] **Summary score matches**: Any score mentioned in the Summary paragraph matches the Scoring Summary exactly.
- [ ] **Strongest Alignment topics are accurate**: The topic(s) cited as strongest HL and strongest LL correspond to the highest and lowest per-topic scores in the Key Topic Score Table.
- [ ] **HL-for-LL terminology list is complete**: Every instance of High Law vocabulary packaging a Low Law principle is captured and numbered.
- [ ] **LL-for-HL terminology list is complete**: Every instance of Low Law vocabulary packaging a High Law principle is captured and numbered.
- [ ] **Comparisons table coverage**: Dimensions that appear in statements (Justice, Mercy, Judgment, Consequences, Dominion, Authority, Suffering, Sacrifice, Perfecting, Unity, Fruit, Safeguards, Durability, Production) are populated if present in the text.

---

## 6. Key Topic Evaluation Table & Details (DETAILED)

Validate that detailed-report sections are structurally synchronized with the Key Topics registry.

- [ ] **Evaluation Table row count equals topic count**: One row per topic in the numbered `Key Topics` list, no more and no less.
- [ ] **Evaluation Table bullets cover all statements**: For each topic, the HL and LL bullet points must reference **every** statement assigned to that topic. Use `(none)` only when a side has zero statements.
- [ ] **Key Topic Details count matches list**: The number of `### N. Topic Name` sections equals the number of topics in the numbered `Key Topics` list.
- [ ] **Key Topic Details numbering/order matches list**: Section numbering and topic names must follow the `Key Topics` list exactly (same order, same names).
- [ ] **No orphaned Details sections**: Confirm no section exists for a topic that was removed during review.
- [ ] **Details internal structure complete**: Each Key Topic Details section contains all required subsections: Summary, Primary Alignment Evaluation, Contradictions to Primary Alignment, Key Quotes in Context, and Detailed Evaluation.

---

## 7. Narrative Sections & Global Score Lock (DETAILED)

Validate that all narrative text points to a single, consistent score.

- [ ] **Overview score matches**: Any score or numeric evaluation mentioned in the Overview matches the Scoring Summary exactly.
- [ ] **Conclusions score matches**: The score restated in the Conclusions matches the Scoring Summary exactly.
- [ ] **Full-document score sweep**: Search the entire document for the numeric score value (and plausible stale variants). **Every** mention in narrative text must equal the Scoring Summary score. Fix stale references, which typically survive after statement edits.
- [ ] **Narrative claims are evidence-backed**: Confirm that characterizations in Overview and Conclusions do not contradict the classified statements.

---

## 8. Final Cross-Reference & Structural Lock

Validate global template compliance and holistic consistency.

- [ ] **Template header exactness**: All section headers (`## Statement Quotes`, `### High Law Aligned (N statements)`, `### Low Law Aligned (N statements)`, `## Scoring Summary`, `## Key Topic Score Table`, etc.) match the specification exactly. No invented headers or tables.
- [ ] **Sequential numbering**: All numbered lists in the report are sequential with no gaps.
- [ ] **Holistic re-check triggered**: If any statement was added, removed, moved, split, or reclassified during this review, re-execute Sections 0 through 7 completely (rebuild inventories first) before signing off.

## Common Pitfalls During Review

- **LL header says 30 but table has 32 rows**: Header count can lag behind actual table rows. Always count rows manually.
- **Renumbering regex corrupts table data**: Use `re.sub(r'^(\|\s*)\d+(\s*\|)', rf'\g<1>{i}\2', row)` per data row, NOT a broad `re.sub(r'\|\s*(\d+)\s*\|', ...)` that matches all pipe-delimited numbers.
- **Per-topic scores go stale after moves**: Moving a statement changes topic-level HL/LL counts AND scores. Recalculate ALL affected topics.
- **Evaluation Table bullets diverge from Score Table**: After statement changes, update both Score Table numbers AND Evaluation Table bullet points.
- **Narrative score mentions survive edits**: Search for old score value across entire document after any count change.
