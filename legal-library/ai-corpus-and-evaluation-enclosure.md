---
id: pla-017
title: Training-data, scraping, and evaluation enclosure
slug: ai-corpus-and-evaluation-enclosure
outcome: Incumbent labs keep corpora and evaluation access; later parties and independent evaluators are fenced
jurisdiction: [US-federal]
domains: [intellectual-property, technology-access, platforms]
routing:
  enabled: [civil, contractual]
  closed: [civil]
instruments:
  - Copyright Act
  - Platform terms of service
  - 18 U.S.C. § 1030
status: initial
related:
  - dmca-takedown-content-id
  - cfaa-tos-authorized-access
  - digital-license-not-sale
  - constrained-open-licenses
  - technical-data-export-controls
updated: 2026-08-20
---

# Training-data, scraping, and evaluation enclosure

Frontier labs already crawled the public web, licensed some catalogs, and hold evaluation harnesses. Copyright, ToS, CFAA letters, anti-benchmark clauses, and "no training on our outputs" terms then fence later parties who have GPUs and staff. The scarce legal object is **permission to learn from and measure the existing stack**, not money for hardware.

Ongoing suits are routing illustrations, not verdicts.

## Outcome / Goal

The practical result is a one-way corpus: incumbents keep training data and block independent evaluation and competitive training. The parties who obtain it are large model developers and major rights-holders. Later labs, academics, and evaluators with compute still need licenses the first movers did not.

## Contrast / Parallel Track

Incumbent crawl of publicly posted pages, and ordinary product review of a toaster, are the analog. A later lab scraping the same public web, using model outputs as training signal, or publishing a leaderboard the ToS forbids, is the closed analog. [pla-005](dmca-takedown-content-id.md) is takedown of user uploads. This page is enclosure of **learning and measurement**.

## Formal Legal Instruments

| Instrument | Role in the outcome | Citation |
| ---------- | ------------------- | -------- |
| Copyright in training materials | Reproduction and derivative-work theories against training; fair use is the contested defense | 17 U.S.C. §§ 106, 107 |
| Claimed copyright in model outputs | Used to forbid competitive training on generations | 17 U.S.C. § 106; ToS |
| ToS anti-scraping / anti-benchmark / no-training-on-outputs | Contractual fence; historically used by major API vendors against evaluation and competitive distillation | Platform and API terms |
| CFAA | Parallel access theory against collection (narrowed for public pages; live for gated APIs) | [18 U.S.C. § 1030](https://www.law.cornell.edu/uscode/text/18/1030); [pla-014](cfaa-tos-authorized-access.md) |
| License-not-sale of subscribed corpora | TDM carved out of paid library and publisher access | [pla-013](digital-license-not-sale.md) |

## Routing

Enabled: civil copyright and contract against later trainers and evaluators; sometimes CFAA on APIs. Closed: a practical fair-use or first-sale path to train on and measure what incumbents already ingested.

Procedural features:

- Injunction and discovery costs fall on the later party.
- API keys plus ToS convert evaluation into a contract breach even when the evaluator paid for access.
- Rights-holder suits and platform ToS can run in parallel against the same lab.

## Application Evidence

**Asymmetric crawl.** The first generation of large models was trained on broad web crawls. Subsequent ToS and lawsuits treat similar collection by others as infringement or breach. The preferential fact is timing and market position, not a new statute.

**Evaluation bans.** Major providers have at times contractually forbidden benchmarking, competitive evaluation, or using outputs to train other models, while publishing their own scores. Independent evaluation of ordinary goods does not require the seller's license. Independent evaluation of models often does.

**Litigation as routing (not verdicts).** *New York Times v. OpenAI* and related training-data suits (filed 2023, ongoing) are the rights-holder half: copyright as a fence around corpora. They do not, in this library, establish that training is or is not fair use. They establish that well-resourced rights-holders can impose years of process on the training question, while the incumbent corpus remains in place.

**Paid but closed.** University TDM restrictions on subscribed journals are the same enclosure with invoices attached. See pla-013.

## Domain Tags

intellectual-property, technology-access, platforms

## Sources

1. 17 U.S.C. §§ 106–107. <https://www.law.cornell.edu/uscode/text/17/106>
2. 18 U.S.C. § 1030. <https://www.law.cornell.edu/uscode/text/18/1030>
3. *Van Buren* and *hiQ* (scraping/CFAA limit) — see [pla-014](cfaa-tos-authorized-access.md) sources.
4. Complaints and docket in *New York Times Co. v. Microsoft Corp.*, No. 1:23-cv-11195 (S.D.N.Y.) — illustration of routing, not a holding.

## Related Entries

- [DMCA takedown and Content ID](dmca-takedown-content-id.md) (pla-005) — control of posted copies, not of training.
- [CFAA and terms of service](cfaa-tos-authorized-access.md) (pla-014) — the access-crime tool against collection.
- [Digital license-not-sale](digital-license-not-sale.md) (pla-013) — paid corpora that still cannot be mined.
- [Constrained open licenses](constrained-open-licenses.md) (pla-024) — field-of-use terms on weights that look open.
- [Technical data export controls](technical-data-export-controls.md) (pla-016) — state license wall on weights and chips.

## Expansion notes

Fair-use holdings if and when they land; systematic ToS snapshots of anti-benchmark clauses; dataset-license (LAION, Common Crawl) disputes.

## Framework notes

Relevant distinction rules from [SKILL.md](../SKILL.md):

- **Rule 4 (Machiavellianism vs Compassion).** The first crawl is treated as fact; the second is treated as theft.
- **Rule 22 (Legalism as Idol).** ToS paragraphs become the law of measurement.
- **Rule 33 (Dominion: stewardship or ownership).** Incumbents claim the training commons as a private estate.
- **Rule 40 (Safeguards: principled or procedural).** Fair use and *Van Buren* are hedges. Contract fills them.
- **Rule 42 (Production: distributed or centralized).** Independent labs are distributed production. Corpus-plus-ToS centralizes who may learn.

Do not score this entry. The rules name the pattern; they do not replace the instruments or the evidence.
