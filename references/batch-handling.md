# Batch & Scale Operations

When evaluating multiple documents, use tools to handle the scale:
1. Use a to-do list with one entry per document
2. Use a delegated task for each document; instruct subagent to load this skill (/high-vs-low); only do one document in each delegated task
3. If the resource is a file, database, URL or other location that the subagent can access directly, instruct each delegation subagent to read and/or write directly

## Database Batches (SQLite or similar)

**Recommended Schema (documents table)**

| Column | Type | Purpose |
|--------|------|---------|
| *basic* | | *required input fields* |
| id | INTEGER PRIMARY KEY | Record identifier |
| doc_text | TEXT | Full source text |
| *eval/score* | | *populated by high-vs-low skill* |
| count_hl | INTEGER | High Law aligned statement count |
| count_ll | INTEGER | Low Law aligned statement count |
| score | REAL | Score on -10 to +10 scale |
| evaluation | TEXT | Full markdown evaluation report |
| *metadata* | | *organization, analysis dimensions* |
| type | TEXT | book, scripture, speech, article, etc |
| author_name | TEXT | Full name of author |
| author_title | TEXT | Title of author at the time of writing or publication |
| series | TEXT | Serial publications, conferences, 'Bible', 'Book of Mormon', etc |
| volume | TEXT | Book volumes, magazine editions, 'Isaiah', '2 John', etc |
| doc_title | TEXT | Chapter/article/speech/etc title |
| doc_num | TEXT | Document (chapter) number within a volume |
| year | INTEGER | Year written or published, + for AD, - for BC |
| source_name | TEXT | Easily referenceable name of source |
| source_url | TEXT | URL for web page and other URL addressable sources |

**Database Delegation Workflow**

Follow these steps *in order*:
1. **Discover schema**: Confirm columns (query `sqlite_master`)
2. **Preview records**: Check `id` range, text lengths, and existing evaluation state; DO NOT read full document text or include it in instructions (instruct subagent to read)
3. **Delegate evaluation per-record**
   - *ALWAYS* use one task per one record; delegate one task at a time sequentially and verify results before starting the next
   - Send *these exact* instructions to subagent (replace locations and column names as needed):
      1. Read the `high-vs-low` skill (via skill like `skill_view(name='high-vs-low')` or path like `/opt/data/skills/high-vs-low/SKILL.md`)
      2. Read `doc_text` for the designated `id` from the `documents` table in the specified *database* (include database location and access details)
      3. Evaluate the text: follow skill instructions and reason through the full text as an AI
      4. Generate the full evaluation report as per specification in the high-vs-low skill and any additional user instructions (default to basic report unless user requests detailed); use a temporary file for initial output, and use patches to modify as needed before finalizing (to avoid regenerating entire report)
      5. Write the markdown report into the `evaluation` column
      6. Populate `count_hl`, `count_ll`, and `score` using values from the report
      7. Return `id` and final counts for verification
   - **Verify after each**: Confirm counts, score, and evaluation are populated; remember these to report at the end
4. **Delegate review per-record**
   - *ALWAYS* do this review unless the user has asked to skip the review
   - *ALWAYS* use one task per one record; delegate one task at a time sequentially and verify results before starting the next
   - Send *these exact* instructions to subagent (replace locations and column names as needed):
      1. Read the `high-vs-low` skill (via skill like `skill_view(name='high-vs-low')` or path like `/opt/data/skills/high-vs-low/SKILL.md`)
      2. Read the `references/report-review.md` skill reference file (Evaluation Report Review Checklist) via skill like `skill_view(name='high-vs-low', file_path='references/report-review.md')` or path like `/opt/data/skills/high-vs-low/references/report-review.md`
      3. Read `doc_text` and `evaluation` for the designated `id` from the `documents` table in the specified *database* (include database location and access details)
      4. Review the *evaluation* by verifying all applicable entries in the *Evaluation Report Review Checklist* (from the `report-review.md` file)
      5. Update `evaluation`, `count_hl`, `count_ll`, and `score` if changed
      6. Return `id` and both original and updated counts for verification
   - **Verify after each**: Confirm counts, score, and evaluation are populated and have been updated as needed; remember these to report at the end
5. **Report**: Describe what was done, if there were any issues and what was done about them, and a summary of the scores per record from before and after the review
