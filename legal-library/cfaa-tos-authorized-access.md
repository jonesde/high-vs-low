---
id: pla-014
title: CFAA and terms of service as a wall around reachable systems
slug: cfaa-tos-authorized-access
outcome: Civil or criminal exposure for using a computer the party can technically reach, because ToS or authorized access is read as the crime
jurisdiction: [US-federal]
domains: [technology-access, platforms, speech]
routing:
  enabled: [criminal, civil, contractual]
  closed: [civil]
instruments:
  - 18 U.S.C. § 1030
status: initial
related:
  - platform-safe-harbors
  - security-research-knowledge-ban
  - ai-corpus-and-evaluation-enclosure
  - technical-data-export-controls
updated: 2026-08-20
---

# CFAA and terms of service as a wall around reachable systems

The Computer Fraud and Abuse Act makes it a crime to access a protected computer "without authorization" or to "exceed authorized access." For years, platforms and prosecutors read that language as covering ToS violations, scraping, and use of credentials for a disapproved purpose. The person has a computer and a network path. The restriction is legal. The analog is reading a posted page or a platform scraping someone else.

## Outcome / Goal

The practical result is a criminal and civil overlay on ordinary computer use that the operator dislikes: scraping, research, interoperability, and violating a clickwrap. The parties who obtain it are platforms and other computer owners who can send a cease-and-desist and, in some circuits and periods, threaten CFAA. Independent researchers, competing services, and journalists are the usual defendants.

## Contrast / Parallel Track

Reading a public HTML page is not trespass. A dominant platform collecting others' public pages at scale is ordinary business. When a smaller party collects the platform's public pages, the platform has often answered with CFAA, contract, and trespass-to-chattels. After *Van Buren* and the Ninth Circuit's *hiQ* remand, the CFAA path for **public** scraping is narrower. Contract and other civil theories remain. Password-gated and technically fenced systems remain CFAA territory. The preferential pattern is who can police "authorization."

## Formal Legal Instruments

| Instrument | Role in the outcome | Citation |
| ---------- | ------------------- | -------- |
| CFAA access crimes and civil action | Fine, imprisonment, and private suit for access without authorization or exceeding authorized access | [18 U.S.C. § 1030](https://www.law.cornell.edu/uscode/text/18/1030) |
| "Exceeds authorized access" | Defined as accessing a computer with authorization and using that access to obtain information in the computer that the accessor is not entitled so to obtain | § 1030(e)(6) |
| *Van Buren* gates-up-or-down | Improper motive for using access one already has is not a CFAA exceedance; the statute is about permission to enter a place in the system | *Van Buren v. United States*, 593 U.S. 374 (2021) |
| *hiQ* public-web scraping | Public pages have no CFAA "gate"; cease-and-desist plus ToS is not enough, in the Ninth Circuit, to make scraping "without authorization" | *hiQ Labs, Inc. v. LinkedIn Corp.*, 31 F.4th 1180 (9th Cir. 2022) |
| Contract / ToS | Parallel civil path that does not need CFAA | Platform terms |

*Van Buren* noted that reading ToS violations as CFAA crimes "would attach criminal penalties to a breathtaking amount of commonplace computer activity." That sentence is the statute confessing how the broader reading was used.

## Routing

Enabled (historically, and still outside the Ninth Circuit's public-web holding): criminal referral and CFAA civil suits against scrapers, researchers, and ToS violators. Enabled now: contract, state trespass, and CFAA where a technical gate (password, non-public API) is down. Closed: treating ToS breach as a federal computer crime for public pages, at least where *Van Buren*/*hiQ* control.

Procedural features:

- Cease-and-desist letters that purport to lower the gate after the fact.
- Criminal exposure that chills even when a later court would find no CFAA violation.
- Platforms remain free to scrape others while litigating inbound scraping.

## Application Evidence

This entry is doctrinal, with a before/after.

**Before *Van Buren*.** Several circuits treated ToS and purpose limits as "authorization." That reading made CFAA a general-purpose computer-misuse statute. DOJ charged, and platforms sued, on that theory.

**After *Van Buren* (2021).** The Court adopted a gates-up-or-down inquiry. Van Buren, a police officer, had permission to use a license-plate database and used it for a bribe. That was not exceeding authorized access. The Supreme Court then GVR'd *hiQ*. On remand the Ninth Circuit again held that scraping **public** LinkedIn pages is not CFAA "without authorization," because a public website has erected no gate. LinkedIn still had contract and other claims. hiQ later failed as a business; the routing holding is what remains.

The preferential residue: large services write the terms, run their own collection, and still use contract (and CFAA on gated APIs) against smaller collectors. Researchers with machines and skill remain one cease-and-desist from a federal computer-crime letter.

## Domain Tags

technology-access, platforms, speech

## Sources

1. 18 U.S.C. § 1030 (Fraud and related activity in connection with computers). <https://www.law.cornell.edu/uscode/text/18/1030>
2. *Van Buren v. United States*, 593 U.S. 374 (2021). <https://www.supremecourt.gov/opinions/20pdf/19-783_k53l.pdf>
3. *hiQ Labs, Inc. v. LinkedIn Corp.*, 31 F.4th 1180 (9th Cir. 2022). <https://law.justia.com/cases/federal/appellate-courts/ca9/17-16783/17-16783-2022-04-18.html>

## Related Entries

- [Platform safe harbors](platform-safe-harbors.md) (pla-012) — ToS plus § 230 as account control; this page is ToS plus CFAA as access-crime.
- [Security research knowledge ban](security-research-knowledge-ban.md) (pla-015) — CFAA stacked with DMCA 1201 against researchers.
- [AI corpus and evaluation enclosure](ai-corpus-and-evaluation-enclosure.md) (pla-017) — scraping as the collection method now fenced for training.
- [Technical data export controls](technical-data-export-controls.md) (pla-016) — another knowledge wall around people who already have the skill.

## Expansion notes

DOJ charging memos post-*Van Buren*; CFAA civil filings against API scrapers; state computer-crime statutes used as substitutes.

## Framework notes

Relevant distinction rules from [SKILL.md](../SKILL.md):

- **Rule 8 (Response to "No").** Using a reachable system in a disapproved way is met with a federal crime theory, not only a contract dispute.
- **Rule 21 (Compulsion).** CFAA as ToS-enforcer is compulsion beyond stopping a break-in.
- **Rule 22 (Legalism as Idol).** "Authorization" is stretched from a locked door to a clickwrap paragraph.
- **Rule 40 (Safeguards: principled or procedural).** *Van Buren*'s gates metaphor is a judicial hedge. Contract fills the hole.
- **Rule 42 (Production: distributed or centralized).** Independent collection is distributed. The platform's own crawl is the centralized exception.

Do not score this entry. The rules name the pattern; they do not replace the instruments or the evidence.
