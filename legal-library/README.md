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
| First-receiver and interposition | 15, 38, 42 | New purchasing power or a title wedge at a designated desk; street lag; man-made distribution |
| Franchise inversion | 18, 22, 33 | Belief, aid, or technique recoded as an institution's owned license |

The [relational analysis skill](../relational/SKILL.md) is a complementary diagnostic: it asks whether a mechanism keeps pairwise relations mutual and generative or converts them into extraction, exclusion, or hierarchy. These entries supply the legal mechanisms that skill would classify.

---

## Disclaimer

This library is documentation of observed legal patterns. It is not legal advice, not a determination of liability in any dispute, and not a claim that every cited actor is guilty of a crime. Facts in entries can be incomplete or disputed. Read them as documented routing patterns, not as verdicts.

The parent repository is released under [CC0 1.0](../LICENSE). These files inherit that dedication.

---

## Library map

Six arcs, pla-001 through pla-072. Full catalog and domain browse: [index.md](index.md).

| Arc | IDs | Inversion |
| --- | --- | --------- |
| Track-switching | pla-001–012 | Same taking; civil for the institution, crime for the analog person |
| Technique enclosure | pla-013–024 | You have the tools; the license or secret is the wall |
| Earth and money | pla-025–036 | First-receiver issue and title sit between people and land, minerals, and water |
| Protected complexes | pla-037–048 | Compulsion outside, immunity inside (purity, Drug War, health/MIC) |
| Institutional religion | pla-049–060 | Belief, expression, and receipt vs the church-as-franchise |
| Institutional charity | pla-061–072 | Local aid vs deducted corpus; controllers act through the 501(c)(3) |

Waves 4–6 share the `protected-complexes` domain token. Browse **Protected complexes** for pla-037–048 only; religion and charity have their own headings.

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

`labor`, `property`, `personal-property`, `intellectual-property`, `technology-access`, `monetary`, `resources`, `protected-complexes`, `religion`, `charity`, `capital-access`, `debt`, `regulatory-control`, `land-use`, `policing-revenue`, `platforms`, `speech`, `financial`, `commercial`

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

## Second wave: technology access

Restriction of **use of, or awareness of, a technique** despite sufficient machines, copies, labs, skill, or public funding. Not inability to pay for the device, the drug, or the factory. See [index.md](index.md) for catalog grouping.

| ID | File | Outcome | Primary instruments | Domains |
| -- | ---- | ------- | ------------------- | ------- |
| pla-013 | [digital-license-not-sale.md](digital-license-not-sale.md) | Vendor retains control of a paid-for digital copy | 17 U.S.C. § 109; *Vernor*; *ReDigi* | intellectual-property, technology-access, personal-property |
| pla-014 | [cfaa-tos-authorized-access.md](cfaa-tos-authorized-access.md) | ToS or "authorized access" as a crime around reachable systems | 18 U.S.C. § 1030; *Van Buren*; *hiQ* | technology-access, platforms, speech |
| pla-015 | [security-research-knowledge-ban.md](security-research-knowledge-ban.md) | Independent research and publication about locks is legally risky | 17 U.S.C. § 1201(a)(2); CFAA | intellectual-property, technology-access |
| pla-016 | [technical-data-export-controls.md](technical-data-export-controls.md) | License wall on publishing or transferring crypto and AI technical data | EAR/ITAR; *Bernstein*; ECCN 3A090 / 4E091 | technology-access, regulatory-control |
| pla-017 | [ai-corpus-and-evaluation-enclosure.md](ai-corpus-and-evaluation-enclosure.md) | Incumbents keep corpora and evaluation; later parties are fenced | Copyright; ToS; CFAA; anti-benchmark clauses | intellectual-property, technology-access, platforms |
| pla-018 | [seed-patent-reuse-ban.md](seed-patent-reuse-ban.md) | Bought seed cannot be saved, replanted, or independently bred | Utility patents; PVPA; *Bowman v. Monsanto* | intellectual-property, technology-access, property |
| pla-019 | [bayh-dole-exclusive-license.md](bayh-dole-exclusive-license.md) | Publicly funded inventions exclusively licensed away from other equipped firms | 35 U.S.C. §§ 200–212 | intellectual-property, technology-access, regulatory-control |
| pla-020 | [blocking-patents-nonuse.md](blocking-patents-nonuse.md) | Exclusive rights used to prevent practice, including by non-working owners | 35 U.S.C. § 271; *Continental Paper Bag* | intellectual-property, technology-access |
| pla-021 | [historical-technique-privilege.md](historical-technique-privilege.md) | Sovereign or incumbent reserves who may print, export a machine, or attach a device | Stationers; machinery-export bans; *Carterfone* | intellectual-property, technology-access, regulatory-control |
| pla-022 | [gene-method-patents.md](gene-method-patents.md) | Equipped labs blocked from running known tests by gene and method patents | 35 U.S.C. § 101; *Myriad*; *Mayo* | intellectual-property, technology-access |
| pla-023 | [born-secret-restricted-data.md](born-secret-restricted-data.md) | Independently derived nuclear technique still illegal to communicate | 42 U.S.C. §§ 2014(y), 2274; *Progressive* | technology-access, regulatory-control |
| pla-024 | [constrained-open-licenses.md](constrained-open-licenses.md) | Source-available and field-of-use terms that look open while reserving commercial use | Copyright licenses; BSL, SSPL, Commons Clause, Llama AUP, dual-license | intellectual-property, technology-access |

## Third wave: resource access and money issue

Legal standing between mortal people and the earth's means of staying alive — land, minerals, water, and the **monetary claim-ticket** that mediates almost all of that access. New purchasing power enters at legally designated points; street prices and wages adjust later. First receivers spend at pre-dilution prices. See [index.md](index.md).

| ID | File | Outcome | Primary instruments | Domains |
| -- | ---- | ------- | ------------------- | ------- |
| pla-025 | [national-banking-reserve-pyramid.md](national-banking-reserve-pyramid.md) | Note-issue and reserve privilege in chartered banks and NY correspondents | National Bank Acts; Coinage Act 1873; Aldrich-Vreeland | monetary, capital-access, financial |
| pla-026 | [federal-reserve-act-1913.md](federal-reserve-act-1913.md) | Elastic currency and discount window for member banks | Federal Reserve Act; 12 U.S.C. ch. 3 | monetary, financial, regulatory-control |
| pla-027 | [legal-tender-forced-acceptance.md](legal-tender-forced-acceptance.md) | Debts and taxes must be payable in US coins and Fed notes | 31 U.S.C. § 5103 | monetary, property |
| pla-028 | [gold-withdrawal-1933.md](gold-withdrawal-1933.md) | Private gold called in; dollar gold content cut | EO 6102; Gold Reserve Act 1934 | monetary, property, regulatory-control |
| pla-029 | [fiat-first-receiver-impulse.md](fiat-first-receiver-impulse.md) | New balances appear first at dealers, banks, and Treasury counterparties | 12 U.S.C. §§ 343, 355, 461; primary dealers | monetary, capital-access, financial |
| pla-030 | [deposit-insurance-emergency-liquidity.md](deposit-insurance-emergency-liquidity.md) | Insured deposits and emergency facilities keep funding inside designated institutions | FDIC; 12 U.S.C. § 343 (13(3)); BTFP | monetary, financial, regulatory-control |
| pla-031 | [genius-act-permitted-issuance.md](genius-act-permitted-issuance.md) | Payment-stablecoin issue confined to permitted issuers; T-bill/reserve backing | GENIUS Act; 12 U.S.C. § 5902 | monetary, financial, regulatory-control |
| pla-032 | [hardrock-mining-patent-1872.md](hardrock-mining-patent-1872.md) | Locatable public-domain minerals to the claimant at statutory patent prices | General Mining Law of 1872 | resources, property, land-use |
| pla-033 | [public-land-mineral-leasing.md](public-land-mineral-leasing.md) | Exclusive extraction of leasable federal minerals | Mineral Leasing Act 1920; OCSLA | resources, regulatory-control |
| pla-034 | [water-prior-appropriation-reclamation.md](water-prior-appropriation-reclamation.md) | First beneficial use plus Reclamation storage sits between later users and the stream | State prior-appropriation; Reclamation Act 1902 | resources, property, land-use |
| pla-035 | [eminent-domain-to-consolidators.md](eminent-domain-to-consolidators.md) | Condemnation transfers land to a designated taker, including private carriers | *Kelo*; 15 U.S.C. § 717f(h) | resources, property, land-use |
| pla-036 | [land-grants-and-tariff-incidence.md](land-grants-and-tariff-incidence.md) | Public-domain grants to franchisees; tariff wedge to protected first receivers | Railroad land-grant acts; 19 U.S.C. §§ 1862, 2411; IEEPA/§ 122 as dated | resources, land-use, regulatory-control, monetary |

## Fourth wave: protected complexes

Compulsion for the outside, immunity and exemption for designated institutions. The spine is legalistic purity control — alcohol prohibition, then the Drug War, then health-emergency product shields and mandates — applied as **enabler types** across overlapping US industrial complexes (health, carceral, military, intelligence, professional). COVID entries cite PREP, EUA, mandates, and speech routing. They do not decide virology. Institutional religion and institutional charity (waves 5–6) reuse this token; they are listed separately.

| ID | File | Outcome | Primary instruments | Domains |
| -- | ---- | ------- | ------------------- | ------- |
| pla-037 | [constitutional-purity-prohibition.md](constitutional-purity-prohibition.md) | Personal consumption criminalized by constitutional amendment and Volstead | 18th Amendment; Volstead Act; 21st Amendment | protected-complexes, regulatory-control |
| pla-038 | [tax-schedule-as-crime.md](tax-schedule-as-crime.md) | Administrative schedule or tax stamp makes the analog a crime | Harrison Act; CSA 21 U.S.C. §§ 811–813 | protected-complexes, regulatory-control |
| pla-039 | [mandatory-minimum-quantity-disparity.md](mandatory-minimum-quantity-disparity.md) | Same molecule, different quantity trigger by form and class | Anti-Drug Abuse Act 1986; 21 U.S.C. § 841 | protected-complexes |
| pla-040 | [militarized-local-enforcement.md](militarized-local-enforcement.md) | Surplus military gear and federal grants convert local police into a drug-war force | 10 U.S.C. § 2576a; Byrne JAG | protected-complexes, policing-revenue |
| pla-041 | [self-funding-forfeiture-enforcement.md](self-funding-forfeiture-enforcement.md) | Enforcement pays itself from seized property; drug cases as the yield | CCCA 1984; 21 U.S.C. § 881; equitable sharing | protected-complexes, policing-revenue |
| pla-042 | [covered-person-liability-shields.md](covered-person-liability-shields.md) | Designated manufacturers and administrators immune; users lack ordinary product suits | PREP Act 42 U.S.C. § 247d-6d; EUA 21 U.S.C. § 360bbb-3 | protected-complexes, financial |
| pla-043 | [funding-conditioned-mandates.md](funding-conditioned-mandates.md) | Federal money or workplace rules compel a health or abstinence product | 23 U.S.C. § 158; OSHA ETS; CMS mandate | protected-complexes, labor |
| pla-044 | [licensing-monopoly-on-the-analog.md](licensing-monopoly-on-the-analog.md) | Same substance: registered professional track vs street crime | 21 U.S.C. § 822; medical boards | protected-complexes, labor |
| pla-045 | [qualified-immunity.md](qualified-immunity.md) | Officials shielded unless a nearly identical right was already clearly established | *Harlow*; 42 U.S.C. § 1983 | protected-complexes |
| pla-046 | [captured-evidence-associations.md](captured-evidence-associations.md) | User-fee and association gates on what counts as official evidence | PDUFA; professional-association standards | protected-complexes |
| pla-047 | [government-platform-speech.md](government-platform-speech.md) | Official pressure plus platform rules close dissent on the complex's product | First Amendment jawboning; pla-012 stack | protected-complexes, speech, platforms |
| pla-048 | [designated-cost-plus-contractor.md](designated-cost-plus-contractor.md) | Designated contractors take cost-plus or OTA work with limited bid competition | BARDA/OWS; 10 U.S.C. OTA; FAR cost-reimbursement | protected-complexes, capital-access |

## Fifth wave: institutional religion

Original religious liberty, with speech, protected **belief, expression, and receipt**. A legal barrier to any of those is a closed analog. The inversion: those protections attach to **favored institutions** (tax, land, labor, discovery, bankruptcy, public money) while the analog person — member, employee, child, dissenting believer, unfavored sect, ordinary charity — loses the suit, the filing, or the practice. Not a verdict that religion is harmful. Named groups are case illustrations. See [index.md](index.md).

| ID | File | Outcome | Primary instruments | Domains |
| -- | ---- | ------- | ------------------- | ------- |
| pla-049 | [church-autonomy-ecclesiastical-abstention.md](church-autonomy-ecclesiastical-abstention.md) | Courts treat internal church discipline as nonjusticiable | *Watson v. Jones*; *Kedroff*; *Serbian Eastern Orthodox* | religion, protected-complexes |
| pla-050 | [disfavored-practice-criminalization.md](disfavored-practice-criminalization.md) | Unfavored sect's analog practice is a crime or costs a benefit | *Reynolds*; Edmunds-Tucker; *Smith* | religion, protected-complexes, regulatory-control |
| pla-051 | [contracted-native-conversion.md](contracted-native-conversion.md) | Federal money and custody to churches to interrupt Native belief and language | Grant Peace Policy; BIA contract schools; Interior boarding-school reports | religion, protected-complexes, speech |
| pla-052 | [church-tax-opacity.md](church-tax-opacity.md) | Automatic 501(c)(3), no Form 990, special IRS inquiry wall | 26 U.S.C. §§ 508(c)(1)(A), 6033(a)(3)(A), 7611 | religion, protected-complexes, financial |
| pla-053 | [clergy-tax-preferences.md](clergy-tax-preferences.md) | Minister housing excluded from income; analog worker is taxed | 26 U.S.C. § 107 | religion, protected-complexes, financial |
| pla-054 | [ministerial-exception.md](ministerial-exception.md) | "Minister" employees cannot maintain Title VII or ADA claims | *Hosanna-Tabor*; *Our Lady of Guadalupe* | religion, protected-complexes, labor |
| pla-055 | [clergy-privilege-discovery-walls.md](clergy-privilege-discovery-walls.md) | Privilege and autonomy keep personnel files out of discovery | State clergy-penitent codes; First Amendment autonomy | religion, protected-complexes |
| pla-056 | [religious-mass-tort-bankruptcy.md](religious-mass-tort-bankruptcy.md) | Dioceses and similar entities route mass torts into Chapter 11 | 11 U.S.C. ch. 11; charitable-immunity remnants | religion, protected-complexes, financial |
| pla-057 | [faith-healing-child-exemptions.md](faith-healing-child-exemptions.md) | Faith-based medical neglect exempt from ordinary child-protection crime | State faith-healing exemptions; *Yoder* overlay | religion, protected-complexes |
| pla-058 | [rfra-commercial-overlay.md](rfra-commercial-overlay.md) | RFRA heightens the test; closely held for-profits count as persons | RFRA; *Boerne*; *Hobby Lobby* | religion, protected-complexes, commercial |
| pla-059 | [rluipa-property-tax-franchise.md](rluipa-property-tax-franchise.md) | Land-use and property-tax track for religious landowners | RLUIPA; state worship exemptions | religion, protected-complexes, land-use |
| pla-060 | [faith-based-public-money.md](faith-based-public-money.md) | Designated religious providers take social-service and school money | Charitable Choice; *Trinity Lutheran*; *Espinoza*; *Carson* | religion, protected-complexes, speech |

## Sixth wave: institutional charity

Local, personal aid is the analog. The inversion: deduction, corpus, standing, and allocation protect **the institution and its controllers** (banks, employers, family offices, DAF sponsors, hospital systems) while the claimed beneficiary often cannot sue, cannot see the fund, and does not receive the money. Not a verdict that giving is harmful. See [index.md](index.md).

| ID | File | Outcome | Primary instruments | Domains |
| -- | ---- | ------- | ------------------- | ------- |
| pla-061 | [charitable-deduction-first-receiver.md](charitable-deduction-first-receiver.md) | Itemizers deduct gifts to qualifying orgs; analog neighbor gift is not deductible | 26 U.S.C. § 170; §§ 2055, 2522 | charity, protected-complexes, financial |
| pla-062 | [501c3-franchise-vs-mutual-aid.md](501c3-franchise-vs-mutual-aid.md) | Legal "charity" is an org that passes IRS tests; mutual aid is outside the franchise | 26 U.S.C. §§ 501(c)(3), 509 | charity, protected-complexes, financial |
| pla-063 | [cypres-institutional-preservation.md](cypres-institutional-preservation.md) | Failed purpose keeps corpus in charitable title, rewritten as near as possible | Cy-près; UTC §§ 413–414; UPMIFA modification | charity, protected-complexes, property |
| pla-064 | [ag-only-charitable-standing.md](ag-only-charitable-standing.md) | Indefinite beneficiaries generally cannot sue; AG is the protector | Parens patriae; Uniform Supervision of Trustees | charity, protected-complexes |
| pla-065 | [federated-workplace-capture.md](federated-workplace-capture.md) | Exclusive payroll deduction steers gifts to a federation allocator | Employer deduction contracts; CFC 5 C.F.R. Part 950 | charity, protected-complexes, labor |
| pla-066 | [community-foundation-bank-trustee.md](community-foundation-bank-trustee.md) | Perpetual funds at a bank trustee; a committee allocates | Cleveland Foundation 1914; UPMIFA | charity, protected-complexes, financial |
| pla-067 | [private-foundation-perpetual-control.md](private-foundation-perpetual-control.md) | 1969 rules lock in perpetual family-control vehicles with a 5% payout | TRA 1969; 26 U.S.C. §§ 4940–4945 | charity, protected-complexes, financial |
| pla-068 | [donor-advised-funds-no-payout.md](donor-advised-funds-no-payout.md) | Complete deduction at contribution; no mandatory 5% payout | 26 U.S.C. §§ 4966, 4967, 170(f)(18) | charity, protected-complexes, financial |
| pla-069 | [upmifa-endowment-lock.md](upmifa-endowment-lock.md) | Prudent spending preserves endowment purchasing power as default | UMIFA 1972; UPMIFA 2006 | charity, protected-complexes, capital-access |
| pla-070 | [operating-charity-capital-pool.md](operating-charity-capital-pool.md) | Hospitals and universities hold exempt capital; charity-care tests are residual | 26 U.S.C. § 501(r); Form 990 Sch. H | charity, protected-complexes, financial |
| pla-071 | [supporting-org-control-without-ownership.md](supporting-org-control-without-ownership.md) | Supporting orgs let a principal steer capital without owning it | 26 U.S.C. §§ 509(a)(3), 4943(f) | charity, protected-complexes, commercial |
| pla-072 | [scientific-charity-means-test-gate.md](scientific-charity-means-test-gate.md) | COS investigation and "deserving poor" gate replace direct aid | COS charters 1877–; associated-charity form | charity, protected-complexes, regulatory-control |

Adjacent domains still open: housing, healthcare billing as price (hospital 501(r) here is exemption-vs-duty only), environmental permitting, education credentialing.

To add an entry, follow the inclusion rule and this spec, then add it to [index.md](index.md).
