---
id: pla-024
title: Constrained "open" licenses and exploitable open-license patterns
slug: constrained-open-licenses
outcome: Source looks shared; commercial use, fields of endeavor, or competing services remain reserved to the originator
jurisdiction: [US-federal]
domains: [intellectual-property, technology-access]
routing:
  enabled: [civil, contractual]
  closed: [civil]
instruments:
  - Copyright licenses (BSL, SSPL, Commons Clause, Llama AUP, dual-license)
status: initial
related:
  - digital-license-not-sale
  - ai-corpus-and-evaluation-enclosure
  - bayh-dole-exclusive-license
  - platform-safe-harbors
updated: 2026-08-20
---

# Constrained "open" licenses and exploitable open-license patterns

Copyright is a property right that can be licensed on any terms the owner writes. Some terms look like open source — source is visible, forks appear on GitHub — while reserving production use, competing SaaS, or entire fields of endeavor to the originator. Other terms **are** OSI-open (GPL, AGPL) and are still used preferentially through dual-licensing and CLA capture. Equipped implementers have the code and the machines. The reserved use is the restriction.

## Outcome / Goal

The practical result is a two-track grant: community and non-competing users get source; the originator (and chosen cloud or commercial partners) keep the field that makes money. The parties who obtain it are vendors who relicense from OSI-open to source-available, model providers with acceptable-use policies, and dual-license shops. Later implementers who would offer the same service are the closed class.

## Contrast / Parallel Track

OSI Open Source Definition, especially OSD 6 (no discrimination against fields of endeavor) and OSD 5 (no discrimination against persons or groups). MIT/BSD/Apache: anyone with the copy may use it for anything, including competing with the author. The closed analog is that same equipped user offering a hosted product, training a commercial model, or operating in a banned field.

## Formal Legal Instruments

| Instrument | Role in the outcome | Citation |
| ---------- | ------------------- | -------- |
| Copyright exclusive rights | The lever; all of these are copyright licenses | 17 U.S.C. § 106 |
| Commons Clause | Bolt-on: the grant "will not include the right to Sell" (including hosted service whose value is the software) | commonsclause.com |
| Server Side Public License (SSPL) | AGPL-shaped; § 13 requires releasing the entire service stack if you offer the software as a service — not OSI-approved | MongoDB SSPL (2018) |
| Business Source License (BSL) | Production use restricted (often plus "additional use grant" that excludes competing products); converts to an OSI license after a delay (capped at four years in MariaDB's form) | MariaDB BSL; HashiCorp BSL (2023) |
| Llama community license + acceptable use | Weights visible; commercial terms if MAU exceeds a threshold; AUP field bans | Meta Llama 3 license / use policy |
| RAIL and similar AI use licenses | Use-based restrictions (no specified harms, no specified fields) on otherwise published models | RAIL family |
| Dual-licensing | GPL/AGPL for the commons; a paid proprietary license for those who cannot or will not comply — originator, not a random fork, can sell the exception | MySQL, historically MongoDB, others |
| CLA / copyright assignment | Contributors assign; only the originator can relicense or dual-license | Contributor agreements |
| Trademarks on "open" names | Remaining gate after copyright is actually open | Common vendor practice |

## Routing

Enabled: copyright infringement and contract against competing production use, competing SaaS, or AUP-banned fields. Closed: OSI-style freedom to use the published technique in any field, including against the author.

Procedural features:

- GitHub visibility is treated by users as "open." OSI and distros (Debian, Fedora, etc.) reject SSPL/BSL as not open source. The gap is the preferential surface.
- Additional use grants are written by the vendor and aimed at "you may produce, unless you compete with us."
- Dual-license only works for the party who holds enough copyright to relicense — usually via CLA.

## Application Evidence

**Relicensing wave.** MongoDB (SSPL, 2018), Elastic (Elastic License), HashiCorp (BSL, 2023), and others moved from OSI licenses to source-available terms after cloud providers productized the software. The originator still has the trademark and the CLA-controlled copyright. Equipped competitors (including those clouds) have the old OSI versions, or must take a commercial deal.

**Llama-class model licenses.** Weights are published. The community license plus acceptable-use policy still restrict fields of use and, above a monthly-active-user threshold (Llama 2/3 used a 700 million MAU commercial-use trigger), require a separate grant. A lab with GPUs can download the weights and still not have OSI-open rights.

**Dual-license.** The GPL is OSD-compliant. Combined with CLA, it becomes a preferential instrument: the community cannot use the code in a proprietary product; the originator can sell that use. That is an exploitable constraint **inside** otherwise open licensing, not a fake-open license.

Do not claim every copyleft term is a dodge. Copyleft that applies equally, including to the author without a CLA, is a different pattern (reciprocal sharing). The preferential use is the one-sided exception.

## Domain Tags

intellectual-property, technology-access

## Sources

1. 17 U.S.C. § 106. <https://www.law.cornell.edu/uscode/text/17/106>
2. Open Source Definition (especially OSD 5 and 6). <https://opensource.org/osd>
3. Commons Clause. <https://commonsclause.com/>
4. MongoDB, Server Side Public License. <https://www.mongodb.com/legal/licensing/server-side-public-license>
5. FOSSA, source-available / BSL overview (2023). <https://fossa.com/blog/comprehensive-guide-source-available-software-licenses/>
6. Meta Llama 3 community license and acceptable use policy. <https://www.llama.com/llama3/license/>

## Related Entries

- [Digital license-not-sale](digital-license-not-sale.md) (pla-013) — copyright terms that take back ordinary use of a paid copy.
- [AI corpus and evaluation enclosure](ai-corpus-and-evaluation-enclosure.md) (pla-017) — field and evaluation limits on models and data.
- [Bayh-Dole exclusive license](bayh-dole-exclusive-license.md) (pla-019) — reserved exclusive practice, public funding analog.
- [Platform safe harbors](platform-safe-harbors.md) (pla-012) — contract plus statute as the control stack.

## Expansion notes

Distro and cloud-vendor responses to SSPL; Redis trademark/fork history; systematic comparison of RAIL vs Llama AUP field bans.

## Framework notes

Relevant distinction rules from [SKILL.md](../SKILL.md):

- **Rule 8 (Response to "No").** Using the published technique to compete is met with copyright, not a fork.
- **Rule 22 (Legalism as Idol).** "Open" in the README is the hedge. The additional use grant is the law.
- **Rule 33 (Dominion: stewardship or ownership).** Stewardship language (community, commons) over an ownership reservation.
- **Rule 42 (Production: distributed or centralized).** Visible source looks distributed. Field-of-use and dual-license exceptions centralize who may produce at scale.

Do not score this entry. The rules name the pattern; they do not replace the instruments or the evidence.
