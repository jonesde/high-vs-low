-- high-vs-low table definitions (for SQLite)

-- Eval/Draft Status Workflows
-- 1. Evaluate (default)
--    - eval_status: 0 -> 1 (eval begin), 1 -> 2 (eval end), 2 -> 8 (eval review begin), 8 -> 9 (eval review end)
--    - in each thread iteratively query (and work on): search for eval_status 2 first (begin review, set to 8; at end set to 9), if none found then search for NULL/0 next (begin eval, set to 1; at end set to 2), if none found then done; also warn about 1,8 in progress?
-- 2. Merge
--    - eval_status: 2/5/7/9 -> 3 (plan merge: set status on all planned to track); 3 -> 4 (merge begin), 4 -> 5 (merge end), 5 -> 8 (merge review begin), 8 -> 9 (merge review end)
--    - pre-step: find all 2/5/7/9 with matching IDs in the merge-from file, set eval_status to 3
--    - query (work): search for eval_status 5 first (set to 8, begin review; at end set to 9), if none then search for 3 (set to 4, begin merge; at end set to 5)
-- 3. Drafts
--    - eval_status: 0 -> 6 (begin drafts), 6 -> 7 (drafts end; ie all merged, status 6), 7 -> 8 (review begin), 8 -> 9 (review end)
--    - draft_status: 0 -> 1 (draft begin), 1 -> 2 (draft end), 2 -> 3 (draft review begin), 3 -> 4 (draft review end), 4 -> 5 (merge begin, by main/merge endpoint not draft endpoint), 5 -> 6 (merge end)
--    - pre-step: create doc_eval_draft records for all planned drafts (one for each draft endpoint specified)
--    - draft query (work), for each draft endpoint, ie N (draft_seq) threads: search for draft_status 2 first (set to 3, begin review; at end set to 4; if draft-reviews is 0 then skip review and set to 4), if none found then search for draft_status NULL/0 (set to 1, begin draft evel; at end set to 2), if none found then done
--    - merge/main query (work) thread: search for eval_status 7 (); if none then search for eval drafts in 4 (set to 5, begin merge; at end set to 6); if none then search for eval drafts where draft_status is null or draft_status <> 6, if any found wait 5s then continue loop (repeat searches from beginning); if none found done (set eval_status to 7)

CREATE TABLE IF NOT EXISTS documents (  
    id INTEGER PRIMARY KEY AUTOINCREMENT, -- reference id, no meaning
    doc_text TEXT,
    count_hl INTEGER DEFAULT NULL,
    count_ll INTEGER DEFAULT NULL,
    score REAL DEFAULT NULL,
    evaluation TEXT DEFAULT NULL,
    -- eval_status: NULL/0=planned, 1=eval-in-progress, 2=eval-complete, 3=merge-planned, 4=merge-in-progress, 5=merge-complete, 6=drafts-in-progress, 7=drafts-complete, 8=review-in-progress, 9=review-complete
    eval_status INTEGER,
    type TEXT, -- book, scripture, speech, article, whitepaper, etc
    author_name TEXT,
    author_title TEXT DEFAULT NULL,
    series TEXT DEFAULT NULL, -- Bible, Book of Mormon, LDS General Conference, etc
    volume TEXT DEFAULT NULL, -- Isaiah, 2 Nephi, April 1977, etc; if more than one populate series
    doc_title TEXT, -- always populate, if more than one chapter populate volume
    doc_num INTEGER DEFAULT NULL, -- document (chapter) number within a volume
    year INTEGER DEFAULT NULL,
    source_name TEXT DEFAULT NULL,
    source_url TEXT DEFAULT NULL
);
-- if needed, newer col: ALTER TABLE documents ADD COLUMN eval_status INTEGER;

CREATE TABLE IF NOT EXISTS doc_eval_draft (
    doc_id INTEGER,
    draft_seq INTEGER,
    -- draft_status: NULL/0=planned, 1=draft-in-progress, 2=draft-complete, 3=review-in-progress, 4=review-complete, 5=merge-in-progress, 6=merge-complete
    draft_status INTEGER DEFAULT 0,
    evaluation TEXT DEFAULT NULL,
    count_hl INTEGER DEFAULT NULL,
    count_ll INTEGER DEFAULT NULL,
    score REAL DEFAULT NULL,

    PRIMARY KEY (doc_id, draft_seq),
    FOREIGN KEY (doc_id) REFERENCES documents(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS statement (
    statement_id INTEGER PRIMARY KEY AUTOINCREMENT,
    doc_id INTEGER,
    law_group INTEGER, -- HL=1 / LL=0
    doc_group_seq INTEGER,
    rules TEXT,
    decision_notes TEXT,
    key_topics TEXT,
    speaker TEXT,
    stance_quote TEXT,
    principle_quote TEXT,
    FOREIGN KEY (doc_id) REFERENCES documents(id) ON DELETE RESTRICT
);

-- join table between statement and rule (no rule table or FK for now, to add later if/when needed)
CREATE TABLE IF NOT EXISTS statement_rule (
    statement_id INTEGER,
    rule_id INTEGER,
    law_align INTEGER, -- HL=1 / LL=0
    comments TEXT,
    PRIMARY KEY (statement_id, rule_id),
    FOREIGN KEY (statement_id) REFERENCES statement(statement_id) ON DELETE RESTRICT
);

