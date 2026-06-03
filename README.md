# high-vs-low - High Law vs Low Law Alignment Evaluation Agent Skill

Evaluate and score articles, emails, speeches, web pages, books (by chapter), etc for alignment against a High Law vs Low Law framework.

**Easy Install** agent prompt:
```text
Install the latest version of the skill at github.com/jonesde/high-vs-low
```

**Use Cases**
- Why do I feel funny when I read this, but can't quite place it?
- Am I being controlled (manipulated or coerced) in some way? If so, which patterns are they using?
- Why is the world the way it is?
- What is the answer to Life, the Universe, and Everything?

One thing this does NOT try to answer is what **God** is like, or what the ultimate definition of **good** is. In fact, consistency and accuracy improved dramatically with the various instructions to interpret statements about God and good (or the inverse) as indicators of the stance or perspective of the speaker, and *not* use them to distinguish between High Law and Low Law.

This is also NOT about **truth**, LLMs are pure GIGO when it comes to the truth (garbage in => garbage out), but they are pretty good at recognizing patterns, interpreting actions, and picking out intent. The truth of the output depends on the truth of the input.

**The distinction** between High and Low Law can be broken down with two distinct sets of correlated but opposite principles. There is a single line separating the two and it is a straight line, but it is not a single point (it is represented as 42 points in this skill). The principles and behaviors in the High Law set tend to lead to outcomes as well as other principles and behaviors within the High Law set, and not to those in the Low Law set (and vice-versa).

That the core definition, with disinctions for various topics and questions taken from a wide variety of sources. Some language or jargon from those sources is present in the wording and this may be *expanded* over time rather than reduced in order to engage more concept spaces as LLMs operate.

**The score** is on a scale of -10 (low law aligned) to +10 (high law aligned). A score of 0.0 means there are an equal number of statements where the author expresses High Law and Low Law alignments. In other words, the further from 0 the stonger the alignment, and because of how subtracted percentages are used to normalize scores it takes a strong majority to get close to 10, making high numbers strong outliers.

To combine scores (especially rounded to 1 decimal) the best approach is to sum the HL and LL counts that the score is based on (across chapters of a book, all works by an author, etc).

**Evaluations** are based on 42 distinction rules with a High Law and Low Law definition for each. The evaluation process involves identifying **speaker**, **stance**, and **principle** for on each normative claim found in a text. Factors are considered like the speaker being described as a villain by the author, where opinions of the speaker should be inverted.

The 42 rules came from a contest among a bunch of LLMs to consolidate a much longer list of rules from various sources. For the fun of it given the number it landed on, and to keep the list to a reasonable size that hopefully LLMs can navigate effectively, I'll try to keep the number of rules at 42 over time. As more testing results in additional distinctions being needed that means combining existing rules to make room for new ones. The current rule list has some conceptual room for this.

**LLM quality makes a difference.** No level of breaking things down into step-by-step instructions can replace the requirements to understand language and concepts and to make all sorts of judgment calls along the way.

## Skip This Section To Stay Out of Trouble

For some fun, try it on things other people have written or said, especially important and powerful poeple! For even more fun, try it on your OWN stuff. Where do you align more, with High Law or Low Law? Find out based on an evaluation of your communication (like email, articles, speeches, etc), and if you're really brave do that before you read the list of distinction rules

Which would you describe as "good"? My bias is clear, I named it "high-vs-low" after all. Whether my communication is consistent with that, is another question! As the instructions say in the skill, interpret that as a signal of my stance on the topic and NOT as a way to distinguish between High Law vs Low Law principles.

Or, if you're into Joker style fun, try running this on something you must abide by but that you have little influence over, like your corporate handbook or local legal code or even what your preacher says, and share the results with the people who are in charge of such things. Evaluations like these from LLMs are often blunt and brutally honest. This is the sort of fire that gets people talking and reframing, so I apologize for the Joker reference who used fire to destroy. Be prepared to ask unsafe questions like: what sort of community do we have, and is what I want as important as what you want? Said another way, and to paraphrase Animal Farm: who are the "most equal" among the equal animals, and how do the "more equal" animals treat the "less equal"?

For a really trippy vibe, try having it evaluate stuff in other languages... even ancient languages. Some are strongly high law or low law aligned, it's Plum Wild (to quote a wise weatherman).

## Recommendations

- This is an AI Agent Skill, built and tested primarily with Hermes Agent
- Easiest install, prompt your agent:
    ```text
    Install the latest version of the skill at github.com/jonesde/high-vs-low
    ```
- To manually install the skill go to your `skills` directory (like `/opt/data/skills/`) and either:
    - clone the repo:
    ```bash
    git clone https://github.com/jonesde/high-vs-low.git
    ```
    - OR download & unzip the archive:
    ```bash
    wget https://github.com/jonesde/high-vs-low/archive/refs/heads/master.zip && unzip master.zip && mv high-vs-low-master high-vs-low && rm master.zip
    ```
- To use it outside an AI Agent, like in a chat interface, upload or include the SKILL.md file and use a prompt like:
    - `Follow the instructions in the SKILL.md file to evaluate the text below and generate a DETAILED report:` (or "basic/score report" if that's what you're up to)
- LLMs have limited context, and you have limited patience, so do analysis one chapter/article/whatever at a time instead of trying to run this on a whole book or magazine; you will also get VERY different results, even if the full book fits in your fancy 1M token context window, or maybe not if the model is WAY more thorough than even the best LLMs available now (June 2026)
- In the `references/batch-handling.md` file there are additional instructions for handling batches of documents in a database such as SQLite, which is a good option for this sort of work due to common availability and ease of handling sets of documents with a single-file DB, CLI, python libs, GUIs (ie DB Browser), etc
- In the `references/report-review.md` file there is a checklist for reviewing evaluation documents that have already been generated, and this is used by default in the batch-handling instructions (if you don't want it to review after writing, ask it not to); this uses the `script/verify_report.py` Python3 script to do automated verification, but can be used without it (LLM does all validations)

## Sample Database Batch Prompt

This prompt is for Hermes Agent running in a Docker Container with a SQLite db file containing document records with no evaluations; replace the technical details as needed, or pull them all out and let your agent figure it out if you're more patient than I am; also note the instruction to run one delegated task at a time, if you have a good setup for concurrency change that:

```
/high-vs-low
Use the Database Delegation Workflow (db has recommended schema): evaluate and
write a DETAILED report for each record in the `documents` table in the
`/opt/data/home/docs/documents.db` sqlite3 database where `id` is between 598 and 602.
Note that sqlite3 cli is not available, use a python script with import sqlite3.
Run each delegated task one at a time and check its output before continuing to the next one.
```

To create a database file from other sources, ask your agent to do it using the schema in the `high-vs-low/references/batch-handling.md` file. Even using current local models like Qwen3.6 (35B or 27B), I've had little trouble when asking them to do this from CSV files, large HTML documents over a thousand sections (ie the Bible in one big HTML page), web scraping results, and other databases.

## AI Usage Notes

This file is all me, I both apologize and say you're welcome. The beginning intro paragraphs are all me. The wording in the distinction rule table is all mine from things I've written and notes I've taken over the last few years, but I used a LOT of AI help from a number of different LLMs to consolidate a huge pile of text into that list. The instructions and the report template are all AI generated, manually edited, AI reviewed and tested, AI suggestions added, and manually edited more.

The batch-handling instructions are mostly manually written and taken from progressively more complex prompts from testing over time, and also AI reviewed/tested/edited. The report-review.md file and the verify_report.py file were initially AI generated but have been both AI and manually edited... a significant number of times, because many of the validations are based on actual AI caught evaluation errors with AI generated suggestions for what to validate. I no longer find reading AI generated evaluation reports and suggested patches on complex topics and tasks to be enjoyable. :)

## Status Notes

- **Evaluations Quality**
  - LLM quality matters quite a bit; better LLMs produce more insightful, accurate, and consistent results
  - Thinking models, on XHIGH or SUPERULTRAMAXIMAX or whatever, do better and don't need the report review step as much
  - Qwen3.6 27B Q8 running locally is the primary LLM I used to test this skill and work on improvements; the 35Ba3B variant was not as thorough or consistent, I stopped using it after a few rounds of tests
  - Qwen3.6 27B Q8 is the one I've tested with the most, it is very insightful but has certain limitations:
    - preplanning during thinking is not always adequate, and this requires a LOT of thinking before generating the report, so it will realize things in the middle of generating the report output and just say whoops and carry on; it's funny, but also not funny; adding the report-review step and the detailed file and script for that helped a lot with this, pretty much solved (for Qwen3.6 27B anyway... which is a pretty smart model)
    - it is not always thorough in picking out stances (normative claims) in text, probably the biggest issue for consistency as this point, ie different sets of locations referenced from run to run; this may be solvable...
- **Result Consistency** across runs on the same text is difficult but is a high priority for this skill
  - Better LLMs are more consistent, in a significant way; the limitations of Qwen3.6 27B above get worse with lower quality models
  - **TODO** Try a process of two separate evals on the same text, both auto-reviewed, then auto-merged; this could significantly improve quality and consistency, maybe as much as adding an explicit review process helped...
- **Best and Worst LLMs**
  - heckifino, this needs a lot of testing...
  - **TODO** Would this be an interesting **LLM Benchmark**? These are all the rage these days... I don't know if this would make sufficiently useful or interesting comparisons between LLMs, like how well it might correlate with other tasks, but for being thorough and moral reasoning, it's quite the test; would require some test cases, **thoroughly reviewed**, both **AI and manual** reviews...
