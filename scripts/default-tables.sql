-- high-vs-low table definitions (for SQLite)

CREATE TABLE IF NOT EXISTS documents (  
    id INTEGER PRIMARY KEY AUTOINCREMENT, -- reference id, no meaning
    doc_text TEXT,
    count_hl INTEGER DEFAULT NULL,
    count_ll INTEGER DEFAULT NULL,
    score REAL DEFAULT NULL,
    evaluation TEXT DEFAULT NULL,
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

