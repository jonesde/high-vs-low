# Preferential Legal Application Library

This directory is a structured collection of documented instances of **preferential legal application**. Each entry captures a specific outcome that the formal legal system enables or facilitates for some parties while closing or criminalizing analogous conduct for others.

The formal code is treated as a partial confession of the underlying social tension. The observed routing into civil, criminal, regulatory, administrative, contractual, or non-action tracks completes the picture. Entries prioritize concrete, citable mechanisms over abstract claims.

This library lives inside the [high-vs-low](../README.md) project. It is a knowledge base of real-world legal routing, not an evaluation corpus and not a source of High Law / Low Law scores.

**Browse the wiki catalog:** [index.md](index.md)

---

## How this library is used

Read it on its own as a catalog of legal instruments and enforcement patterns.

Use it with the High Law vs. Low Law skill when a text, policy, or institution needs concrete legal examples rather than only distinction-rule language. The skill's [Distinction Rule Table](../SKILL.md) is the conceptual layer; these entries are the applied layer. Each entry's **Framework notes** section names the relevant distinction rules by number and topic. It does not score the entry, assign an alignment percentage, or run the evaluation protocol.

Typical rule clusters for this library:

| Cluster | Rules | What they pick up in these entries |
| ------- | ----- | ---------------------------------- |
| Status and hierarchy | 1, 2 | Some parties treated as above others; hierarchy presented as the natural legal order |
| Domain and taking | 7, 13, 15 | Taking or damaging another party's domain; treating the counterpart as an object; expanding rather than restoring |
| Legalism and punishment | 21, 22, 25, 28 | Compulsion beyond preservation; law as idol; punitive vs restorative justice; fairness as equal suffering for the lower-status party only |
| Artificial process | 38, 40 | Man-made, status-dependent consequences; procedural safeguards that function as loopholes |
| Enclosure and centralization | 6, 8, 33, 36, 42 | Restricted autonomy; "no" with cost; ownership over stewardship; sacrifice of the least; centralized proprietary control |

The [relational analysis skill](../relational/SKILL.md) is a complementary diagnostic: it asks whether a mechanism keeps pairwise relations mutual and generative or converts them into extraction, exclusion, or hierarchy. These entries supply the legal mechanisms that skill would classify.

---

## Disclaimer

This library is documentation of observed legal patterns. It is not legal advice, not a determination of liability in any dispute, and not a claim that every cited actor is guilty of a crime. Facts in entries can be incomplete or disputed. Read them as documented routing patterns, not as verdicts.

The parent repository is released under [CC0 1.0](../LICENSE). These files inherit that dedication.

---

## Document specification

Every entry is a Markdown file with YAML frontmatter and a fixed body. New entries must follow this spec so [index.md](index.md) can catalog them.

### Filename and identity

- Filename is the `slug` plus `.md`, in this directory, kebab-case.
- `id` is `pla-NNN` (preferential legal application, zero-padded). Assign the next unused number.
- `status` is `initial` for first-pass starter entries, `expanded` after a later deepening pass, or `stub` only if an entry is intentionally incomplete (the starter set is not stubs).

### Frontmatter (required)

```yaml
---
id: pla-001
title: Employer retention of unpaid wages on the civil track
slug: unpaid-wages-civil-track
outcome: Retention of unpaid wages with minimal criminal exposure
jurisdiction: [US-federal, US-state]
domains: [labor, property]
routing:
  enabled: [civil, administrative, non-action]
  closed: [criminal]
instruments:
  - 29 U.S.C. §§ 201–219
status: initial
related:
  - employee-theft-criminal-track
updated: 2026-08-20
---
```

`title` must match the `#` heading. `slug` must match the filename. `related` lists other slugs, not titles. `updated` is ISO date.

### Controlled vocabularies

**`domains`** (one or more):

`labor`, `property`, `personal-property`, `intellectual-property`, `capital-access`, `debt`, `regulatory-control`, `land-use`, `policing-revenue`, `platforms`, `speech`, `financial`, `commercial`

**`routing` values** (under `enabled` and `closed`):

`civil`, `criminal`, `regulatory`, `administrative`, `contractual`, `non-action`

**`jurisdiction`:**

`US-federal`, `US-state`, `local`

The starter set is United States law. Other jurisdictions may be added later using the same keys plus an explicit country or system tag in `jurisdiction`.

Do not invent new domain or routing tokens without updating this README and `index.md`.

### Body sections (required, in this order)

1. **Title** (`#`) matching `title` in frontmatter.
2. **Lead** — one paragraph, no heading. State the outcome and the preferential pattern in one or two sentences.
3. **Outcome / Goal** — the practical result, and who obtains it.
4. **Contrast / Parallel Track** — the analogous conduct, and how it is closed, criminalized, or made impractical for others. Required because the library definition depends on it.
5. **Formal Legal Instruments** — a table:

   `| Instrument | Role in the outcome | Citation |`

   Multiple instruments in parallel or sequence are the normal case.
6. **Routing** — which track is enabled, which is closed, and which procedural features produce the split (burden of proof, cost-shifting, bond, private right of action, prosecutor discretion, safe harbor, choice of law, and so on).
7. **Application Evidence** — statistics, enforcement data, studies, or observed patterns. Inline citations. At least one quantitative claim where data exists. If the evidence is qualitative or structural, say so. Label the scope of every statistic (what it measures, for which years, for which jurisdictions).
8. **Domain Tags** — short list matching frontmatter.
9. **Sources** — numbered bibliography with titles, authors or publishers, years, and URLs.
10. **Related Entries** — relative Markdown links to other files in this directory.
11. **Framework notes** — required. Name the relevant distinction rules from [SKILL.md](../SKILL.md) by number and topic (for example, "Rule 22, Legalism as Idol"). Explain how this routing pattern illustrates those rules. Do not assign a High Law / Low Law score, do not run the evaluation protocol, and do not treat this section as a substitute for the four core elements.

### Optional body sections

Place these after Related Entries and before Framework notes, or after Framework notes if they are expansion-only:

- **Case illustrations** — named disputes used as routing illustrations. Label alleged and disputed facts as such.
- **Expansion notes** — what would deepen the entry (more statutes, better data, additional jurisdictions).

### Four core elements

The library definition requires four elements in every entry. They map onto the body as follows:

| Core element | Where it lives |
| ------------ | -------------- |
| Outcome / Goal | Frontmatter `outcome` + **Outcome / Goal** section |
| Formal legal instruments | Frontmatter `instruments` + **Formal Legal Instruments** table |
| Application evidence | **Application Evidence** + **Sources** |
| Domain tags | Frontmatter `domains` + **Domain Tags** |

Contrast, Routing, and Framework notes are additional required sections. They make the preferential pattern, the track split, and the link to the distinction rules explicit.

### Inclusion rule

An entry belongs in this library only if all four are true:

1. A concrete outcome can be named.
2. Specific legal instruments can be cited.
3. There is evidence of differential use by status, resources, institutional position, or network connection.
4. An analogous course of conduct is closed, criminalized, or practically unavailable to another class of parties.

Abstract complaints without a citable mechanism are out of scope.

### Evidence rules

- Prefer primary sources: U.S. Code, agency data, court opinions, and established research organizations.
- Do not conflate distinct statistics (for example, a minimum-wage-violation estimate and an all-forms wage-theft estimate).
- Do not invent recovery rates, conviction counts, or dollar figures. If the evidence is the structure of the code itself, say that.
- Ongoing disputes are illustrations of routing, not findings of liability.

---

## Starter set

Twelve initial entries. Each is `status: initial`: a complete first-pass page, not a stub, and not a finished treatise. They can be expanded with more statutory text, quantitative studies, and case illustrations.

| ID | File | Outcome | Primary instruments | Domains |
| -- | ---- | ------- | ------------------- | ------- |
| pla-001 | [unpaid-wages-civil-track.md](unpaid-wages-civil-track.md) | Retention of unpaid wages with minimal criminal exposure | FLSA 29 U.S.C. §§ 201–219; state payday statutes | labor, property |
| pla-002 | [civil-asset-forfeiture.md](civil-asset-forfeiture.md) | Seizure of cash, vehicles, or other property from low-resource owners with low contestation | 18 U.S.C. §§ 981, 983; 21 U.S.C. § 881 | property, policing-revenue |
| pla-003 | [manufacturer-repair-control.md](manufacturer-repair-control.md) | Manufacturer post-sale control of repair markets and parts | 17 U.S.C. § 1201; design patents; TPM / parts-pairing | intellectual-property, personal-property |
| pla-004 | [patent-assertion-entities.md](patent-assertion-entities.md) | Licensing revenue or settlements by PAEs against operating companies | 35 U.S.C. infringement remedies; venue and joinder | intellectual-property, capital-access |
| pla-005 | [dmca-takedown-content-id.md](dmca-takedown-content-id.md) | Rapid removal or monetization control of user-generated content | 17 U.S.C. § 512; platform Content ID | intellectual-property, platforms |
| pla-006 | [consignment-civil-conversion.md](consignment-civil-conversion.md) | Retention of high-value consigned inventory routed as a civil dispute | Conversion/replevin; UCC Art. 9; franchise/contract | property, commercial |
| pla-007 | [employee-theft-criminal-track.md](employee-theft-criminal-track.md) | Criminal exposure for employee theft of modest value | State larceny/embezzlement; low felony thresholds | labor, property |
| pla-008 | [secured-credit-foreclosure.md](secured-credit-foreclosure.md) | Preferential retention of capital through secured credit and foreclosure | UCC Art. 9; mortgage/foreclosure; 11 U.S.C. priority | capital-access, debt |
| pla-009 | [zoning-incumbent-protection.md](zoning-incumbent-protection.md) | Zoning and code barriers that protect incumbents | Local zoning; variance; nonconforming use; nuisance | land-use, regulatory-control |
| pla-010 | [white-collar-civil-routing.md](white-collar-civil-routing.md) | Large-scale financial wrongdoing routed civil/regulatory | Securities Acts; SEC civil; DPAs/NPAs | financial, regulatory-control |
| pla-011 | [noncompete-trade-secrets.md](noncompete-trade-secrets.md) | Restriction of worker mobility via non-competes and trade secrets | State non-compete doctrine; 18 U.S.C. § 1836 | labor, intellectual-property |
| pla-012 | [platform-safe-harbors.md](platform-safe-harbors.md) | Platform control of speech and economic access via ToS plus safe harbors | 47 U.S.C. § 230; 17 U.S.C. § 512; terms of service | platforms, speech, capital-access |

Adjacent domains for later growth (no stub files yet): housing, healthcare billing, environmental permitting, education credentialing.

To add an entry, follow the inclusion rule and this spec, then add it to [index.md](index.md).
