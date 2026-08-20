---
id: pla-016
title: Export control of cryptographic and AI technical data
slug: technical-data-export-controls
outcome: Parties with money, talent, and machines still cannot publish, export, or tell certain people the technique without a license
jurisdiction: [US-federal]
domains: [technology-access, regulatory-control]
routing:
  enabled: [regulatory, criminal, civil]
  closed: [civil]
instruments:
  - Export Administration Regulations
  - International Traffic in Arms Regulations
status: initial
related:
  - security-research-knowledge-ban
  - born-secret-restricted-data
  - cfaa-tos-authorized-access
  - ai-corpus-and-evaluation-enclosure
  - historical-technique-privilege
  - licensing-monopoly-on-the-analog
updated: 2026-08-20
---

# Export control of cryptographic and AI technical data

Encryption mathematics and, later, frontier-model weights and advanced accelerators have been treated as munitions or dual-use items. A researcher or firm can have the skill, the computers, and the money. Transferring the technique — even by posting source, teaching a foreign national (deemed export), or shipping a chip — still requires a license. The analog is ordinary scientific publication of math.

This page is the **license wall**, not the price of a GPU.

## Outcome / Goal

The practical result is state-licensed control of who may know and use a technique. The parties who obtain licenses, exceptions, or open-weight carve-outs practice. Everyone else with equivalent resources waits, redacts, or does not ship. Historical form: crypto source code as an ITAR/EAR munition. Current form: ECCNs on advanced computing ICs and (when in force) closed AI model weights, plus country-tier licensing.

## Contrast / Parallel Track

Publishing an algorithm in a journal, teaching a class, or emailing a colleague is normal science. Under ITAR/EAR encryption rules of the 1990s, those acts involving cryptographic source code were licensed exports. Under deemed-export rules, telling a foreign national in the United States can be an export. Licensed incumbents and, in the 2025 AI-diffusion design, developers of **open** weights below a threshold, sit on the allowed side. Closed-weight frontier developers and their approved destinations sit on another. Independent publishers and non-aligned buyers sit outside.

## Formal Legal Instruments

| Instrument | Role in the outcome | Citation |
| ---------- | ------------------- | -------- |
| Arms Export Control Act / ITAR | Historically listed encryption as a munition; licenses for export of technical data | 22 U.S.C. § 2778; 22 C.F.R. Parts 120–130 |
| EAR / Commerce Control List | Dual-use controls after crypto moved from State to Commerce (1996); current AI and computing ECCNs | 15 C.F.R. Parts 730–774 |
| *Bernstein* | Encryption source code as speech; Ninth Circuit treated EAR licensing of source-code publication as prior restraint (opinion later vacated as moot after regulatory change) | *Bernstein v. U.S. Dep't of Justice*, 176 F.3d 1132 (9th Cir. 1999), withdrawn 192 F.3d 1308 |
| Deemed export | Release of controlled technology to a foreign national in the United States treated as an export | 15 C.F.R. § 734.13 |
| Advanced computing ECCNs | License requirements for specified ICs and computers containing them | ECCN 3A090, 4A090 and .z items |
| Model-weight ECCN (2025 IFR) | New control on closed-weight models above a training-compute threshold; open weights not controlled in that IFR | ECCN 4E091; 90 Fed. Reg. 4544 (Jan. 15, 2025) |

The January 2025 BIS "Framework for Artificial Intelligence Diffusion" interim final rule added 4E091 and expanded 3A090/4A090 licensing. Later in 2025 BIS **rescinded** that diffusion framework while retaining and adjusting chip controls. Cite the IFR as a documented design of a knowledge-and-hardware license wall, and cite the rescission as a reminder that the wall is a policy instrument, not a standing statute. Chip ECCNs remain the live hardware half.

## Routing

Enabled: administrative licensing, denial, deemed-export compliance, criminal export statutes. Closed: unlicensed publication or transfer of the listed technique by a party who could otherwise do the work.

Procedural features:

- License exceptions and country-group lists are the real map of who may know.
- Open-weight carve-outs (in the 2025 IFR: no license for open weights; closed weights above 10^26 training operations licensed worldwide) split "awareness" by the originator's publication choice.
- Deemed export turns hiring and teaching into an export event.

## Application Evidence

**Crypto.** Daniel Bernstein could write Snuffle. ITAR, then EAR, still required a license before he could post the source. District court and a Ninth Circuit panel treated that as unconstitutional prior restraint on scientific speech. The government then liberalized mass-market crypto rules; the appellate opinion was withdrawn as moot. The sequence is the evidence: the technique was in hand; the license was the restriction; litigation plus policy change, not a market, opened it.

**AI compute and weights.** BIS has listed high-TPP accelerators (3A090.a and related) and, in the 2025 IFR, closed model weights of models trained above 10^26 operations (4E091). Open-weight models were not controlled in that IFR. Firms and states with money still needed licenses by destination tier. That is nationality-and-network preference, not a resource shortage. After rescission of the diffusion framework, destination-based chip licensing continues.

Do not treat GPU list price as the mechanism.

## Domain Tags

technology-access, regulatory-control

## Sources

1. 15 C.F.R. Parts 730–774 (Export Administration Regulations).
2. *Bernstein v. U.S. Department of State*, 974 F. Supp. 1288 (N.D. Cal. 1997); *Bernstein v. U.S. Dep't of Justice*, 176 F.3d 1132 (9th Cir. 1999). EFF: <https://www.eff.org/cases/bernstein-v-us-dept-justice>
3. BIS, "Framework for Artificial Intelligence Diffusion," 90 Fed. Reg. 4544 (Jan. 15, 2025). <https://www.federalregister.gov/documents/2025/01/15/2025-00636/framework-for-artificial-intelligence-diffusion>
4. Coverage of later 2025 rescission of the diffusion IFR and continuing chip ECCNs (confirm current 15 C.F.R. CCL before relying on 4E091 as in force).

## Related Entries

- [Security research knowledge ban](security-research-knowledge-ban.md) (pla-015) — civilian IP overlay on telling how a lock works.
- [Born-secret Restricted Data](born-secret-restricted-data.md) (pla-023) — a stricter born-classified knowledge ban.
- [AI corpus and evaluation enclosure](ai-corpus-and-evaluation-enclosure.md) (pla-017) — private-law enclosure of training and measurement.
- [Historical technique privilege](historical-technique-privilege.md) (pla-021) — machinery and artisan export bans as the analog ancestor.
- [Licensing monopoly on the analog](licensing-monopoly-on-the-analog.md) (pla-044) — a clearance or number that makes the same object lawful in one mouth and a crime in another.

## Expansion notes

Current CCL entries at time of next expansion; Wassenaar crypto history; deemed-export enforcement counts.

## Framework notes

Relevant distinction rules from [SKILL.md](../SKILL.md):

- **Rule 2 (Power hierarchy).** License lists present geopolitical hierarchy as the natural order of who may use a technique.
- **Rule 18 (Authority: chosen or imposed?).** Publication and teaching are made licensed events.
- **Rule 22 (Legalism as Idol).** An export-control classification becomes a speech and science rule.
- **Rule 40 (Safeguards: principled or procedural).** Country groups and open-weight carve-outs are procedural maps, not a principle that knowledge is free to those who can do the work.
- **Rule 42 (Production: distributed or centralized).** Independent labs are distributed. Licensed incumbents and listed destinations are the permitted nodes.

Do not score this entry. The rules name the pattern; they do not replace the instruments or the evidence.
