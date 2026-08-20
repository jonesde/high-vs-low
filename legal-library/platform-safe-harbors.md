---
id: pla-012
title: Platform control via terms of service and statutory safe harbors
slug: platform-safe-harbors
outcome: Platform or intermediary control over speech and economic activity via terms of service combined with statutory safe harbors
jurisdiction: [US-federal]
domains: [platforms, speech, capital-access]
routing:
  enabled: [contractual, civil]
  closed: [civil]
instruments:
  - 47 U.S.C. § 230
  - 17 U.S.C. § 512
  - Platform terms of service
status: initial
related:
  - dmca-takedown-content-id
  - manufacturer-repair-control
  - zoning-incumbent-protection
updated: 2026-08-20
---

# Platform control via terms of service and statutory safe harbors

Section 230 says a platform is not the publisher of third-party speech, and is not liable for good-faith restriction of material it finds objectionable. Section 512 adds a copyright safe harbor if the platform takes content down on notice. Terms of service then give the same platform contractual power to remove, demonetize, or terminate. Users live under the contract. The platform lives under the statute.

## Outcome / Goal

The practical result is discretionary control of visibility, monetization, and account existence, with broad immunity for third-party content and for many moderation choices. The parties who obtain it are large interactive computer services. Smaller users and creators have internal appeals, and usually not much else. Economic access (reach, payment, identity attached to the account) is inside that stack.

## Contrast / Parallel Track

A newspaper that prints a letter can be sued as publisher. A speaker on a street corner is not subject to a private ToS that extinguishes the corner. A small forum operator has the same § 230 text but not the same market power: users can leave. On a dominant platform, leaving is leaving the audience. The closed analog is a user's ability to force the platform to carry speech, to explain a takedown with process that a court would recognize as due, or to recover the account as a property interest. Courts generally treat those claims as publishing decisions under *Zeran* and its descendants.

## Formal Legal Instruments

| Instrument | Role in the outcome | Citation |
| ---------- | ------------------- | -------- |
| Publisher/speaker immunity | Provider not treated as publisher or speaker of others' information | [47 U.S.C. § 230(c)(1)](https://www.law.cornell.edu/uscode/text/47/230) |
| Good-faith restriction immunity | No civil liability for restricting material the provider considers obscene, violent, harassing, or "otherwise objectionable," whether or not constitutionally protected | § 230(c)(2)(A) |
| DMCA safe harbors | Copyright module of the stack; notice-and-takedown plus repeat-infringer policy | [17 U.S.C. § 512](https://www.law.cornell.edu/uscode/text/17/512) |
| Terms of service | Contractual license to remove, demonetize, suspend; often at will | Private contract |
| *Zeran* line | Editorial functions (publish, withdraw, postpone, alter) are immunized | *Zeran v. America Online, Inc.*, 129 F.3d 327 (4th Cir. 1997) |
| *Barnes*-style promissory exception | Narrow path if the platform made a specific promise to a specific person | *Barnes v. Yahoo!*, 570 F.3d 1096 (9th Cir. 2009) |

§ 230(e) preserves criminal law and intellectual-property law, which is why § 512 sits beside it instead of inside it.

## Routing

Enabled: contractual moderation plus statutory immunity. Closed: treating account termination or demonetization as a reviewable deprivation of speech or livelihood, except in narrow contract-promise cases.

Procedural features:

- Internal appeals are platform-designed. They are not § 1983, not APA, not a hearing as of right.
- General "we enforce our rules" language usually does not defeat § 230. Specific, personal promises sometimes do (*Barnes*); later cases have kept that exception narrow.
- Combined with [pla-005](dmca-takedown-content-id.md), copyright claims add a second, faster removal path that the user must fight on the rights-holder's timetable.

## Application Evidence

This starter entry is doctrinal more than statistical. The doctrine is the application.

CRS and the case law: § 230(c)(1) has been read to bar suits that treat the provider as publisher, including many suits about takedowns and account suspensions. § 230(c)(2) separately protects good-faith restriction. Users who sue for breach of ToS, fraud, or "inconsistent moderation" routinely lose at the motion-to-dismiss stage when the complained-of act is a publishing decision.

Market structure supplies the rest: a few platforms intermediate a large share of public speech and creator income. Immunity plus contract is not preferential because small hosts lack § 230 (they have it). It is preferential because only large hosts combine that immunity with the ability to exclude a user from the relevant audience.

Transparency reports document volume of removals. They do not give users a cause of action.

## Domain Tags

platforms, speech, capital-access

## Sources

1. 47 U.S.C. § 230. <https://www.law.cornell.edu/uscode/text/47/230>
2. 17 U.S.C. § 512. <https://www.law.cornell.edu/uscode/text/17/512>
3. *Zeran v. America Online, Inc.*, 129 F.3d 327 (4th Cir. 1997).
4. *Barnes v. Yahoo!, Inc.*, 570 F.3d 1096 (9th Cir. 2009).
5. Congressional Research Service, "Section 230: An Overview," R46751. <https://www.congress.gov/crs-product/R46751>
6. Electronic Frontier Foundation, Section 230 overview. <https://www.eff.org/issues/cda230>

## Related Entries

- [DMCA takedown and Content ID](dmca-takedown-content-id.md) (pla-005) — the copyright half of the stack.
- [Manufacturer repair control](manufacturer-repair-control.md) (pla-003) — post-sale control via a different statute-plus-contract pair.
- [Zoning incumbent protection](zoning-incumbent-protection.md) (pla-009) — discretionary gatekeeping in physical space.

## Expansion notes

Account-termination case table post-2024; state laws attempting to constrain moderation and their preemption/First Amendment fate; measurement of creator-income dependence on a single platform.

## Framework notes

Relevant distinction rules from [SKILL.md](../SKILL.md):

- **Rule 8 (Response to "No").** The user's "no" to a moderation decision, or to a contract of adhesion, is met with termination. Consent to ToS is not withdrawal-without-cost.
- **Rule 18 (Authority and obedience: chosen or imposed?).** Platform authority is imposed as a condition of reaching other people, not chosen in a setting where exit is cheap.
- **Rule 22 (Legalism as Idol).** § 230 and the ToS become the container. Speech and livelihood exist only inside it.
- **Rule 40 (Safeguards: principled or procedural).** Internal appeals and transparency reports are procedural. They do not give the excluded user a principled hearing.
- **Rule 42 (Production: distributed or centralized).** User speech and creator income are distributed production running across a centralized gate.

Do not score this entry. The rules name the pattern; they do not replace the instruments or the evidence.
