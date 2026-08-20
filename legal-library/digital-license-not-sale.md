---
id: pla-013
title: License-not-sale of software and digital copies
slug: digital-license-not-sale
outcome: Vendor retains control of a paid-for copy (no resale, no perpetual use, no TDM, revocation at will)
jurisdiction: [US-federal]
domains: [intellectual-property, technology-access, personal-property]
routing:
  enabled: [civil, contractual]
  closed: [civil]
instruments:
  - 17 U.S.C. § 109
  - Software license agreements
status: initial
related:
  - manufacturer-repair-control
  - constrained-open-licenses
  - ai-corpus-and-evaluation-enclosure
  - historical-technique-privilege
updated: 2026-08-20
---

# License-not-sale of software and digital copies

A buyer who pays for software, an ebook, or a download often receives a license, not title to a copy. First sale (the right to resell, lend, or keep using the copy you bought) is closed by that label. The vendor keeps post-transfer control. The analog is a book or a wrench: you paid, you own the chattel.

## Outcome / Goal

The practical result is continuing vendor control of a copy the user already paid for: no lawful used market, no lending of the file, no text-and-data mining of a subscribed corpus without a second permission, and revocation or always-online authentication that can kill the copy. The parties who obtain it are software publishers, ebook and music platforms, and database vendors. Libraries and universities that spend large sums still do not own the copies they license.

## Contrast / Parallel Track

17 U.S.C. § 109(a) lets the **owner** of a lawfully made copy sell or otherwise dispose of that copy without the copyright owner's permission. That is how used bookstores, libraries, and garage sales work. Section 109(d) withholds those privileges from someone who has only a license. Calling the transfer a "license" is the switch. The same dollars that would buy a first-sale copy buy a revocable permission.

## Formal Legal Instruments

| Instrument | Role in the outcome | Citation |
| ---------- | ------------------- | -------- |
| First-sale statute | Privileges run only to owners of copies, not licensees | [17 U.S.C. § 109](https://www.law.cornell.edu/uscode/text/17/109) |
| Ninth Circuit license test | A transfer is a license, not a sale, when the copyright owner specifies it is licensed, significantly restricts transfer, and imposes notable use restrictions | *Vernor v. Autodesk, Inc.*, 621 F.3d 1102 (9th Cir. 2010) |
| Digital resale as reproduction | Moving a lawfully purchased file to a new medium is treated as making a new copy, so § 109 does not apply | *Capitol Records, LLC v. ReDigi Inc.*, 910 F.3d 649 (2d Cir. 2018) |
| Shrinkwrap / clickwrap | Terms that forbid reverse engineering, resale, benchmarking, and TDM; often held enforceable as contract | *ProCD, Inc. v. Zeidenberg*, 86 F.3d 1447 (7th Cir. 1996) |
| Subscription and university licenses | Paid access without ownership; TDM and sharing carved out | Publisher and aggregator licenses |

## Routing

Enabled: copyright infringement plus contract for anyone who resells, lends, or mines the paid copy. Closed: first sale as it still applies to a physical book.

Procedural features:

- DMCA takedown against used-software listings (*Vernor* began with Autodesk using § 512 to knock Vernor's eBay sales offline).
- Always-online license checks convert a paid copy into a service.
- Library "controlled digital lending" and interlibrary supply sit on the same hinge: if the library does not own a copy, § 109 never starts.

## Application Evidence

**Software.** In *Vernor*, Autodesk's AutoCAD SLA specified a license, banned transfer, and restricted use. The Ninth Circuit held CTA (the original "purchaser") was a licensee, so Vernor, who bought used copies, had no first-sale right. The buyer had paid. Resale was still infringement.

**Digital music.** ReDigi built a marketplace for "used" iTunes files and deleted the seller's copy. The Second Circuit held that the transfer reproduced the work on a new phonorecord, so § 109 (which limits the distribution right, not the reproduction right) did not apply. A paid download is not a resalable chattel.

**Paid institutions.** Research libraries spend large subscription budgets and still cannot, under typical licenses, TDM the corpus, keep perpetual local copies, or lend as they would a print volume. The restriction is use of knowledge they already paid to house, not lack of money. That is the same license-not-sale switch at institutional scale.

The code is structural: § 109(d) is the confession. *Vernor* and *ReDigi* are how it is applied to software and files.

## Domain Tags

intellectual-property, technology-access, personal-property

## Sources

1. 17 U.S.C. § 109 (Limitations on exclusive rights: Effect of transfer of particular copy or phonorecord). <https://www.law.cornell.edu/uscode/text/17/109>
2. *Vernor v. Autodesk, Inc.*, 621 F.3d 1102 (9th Cir. 2010). EFF case page: <https://www.eff.org/cases/vernor-v-autodesk>
3. *Capitol Records, LLC v. ReDigi Inc.*, 910 F.3d 649 (2d Cir. 2018). <https://law.justia.com/cases/federal/appellate-courts/ca2/16-2321/16-2321-2018-12-12.html>
4. *ProCD, Inc. v. Zeidenberg*, 86 F.3d 1447 (7th Cir. 1996).

## Related Entries

- [Manufacturer repair control](manufacturer-repair-control.md) (pla-003) — post-sale control of the machine and spare part; this page is post-sale control of the copy.
- [Constrained open licenses](constrained-open-licenses.md) (pla-024) — copyright terms that look like a grant and still reserve use.
- [AI corpus and evaluation enclosure](ai-corpus-and-evaluation-enclosure.md) (pla-017) — TDM and training as the use that licenses strip out.
- [Historical technique privilege](historical-technique-privilege.md) (pla-021) — older privileges over who may traffic in copies.

## Expansion notes

Kirtsaeng international exhaustion contrast; EU used-software *UsedSoft* (CJEU) as a working analog; library CDL litigation (Internet Archive).

## Framework notes

Relevant distinction rules from [SKILL.md](../SKILL.md):

- **Rule 6 (Individual autonomy).** The buyer's use of a paid copy is subordinated to a form license.
- **Rule 22 (Legalism as Idol).** "License" as a word in a EULA becomes the law that empties § 109.
- **Rule 33 (Dominion: stewardship or ownership).** The vendor remains owner after the money has moved.
- **Rule 42 (Production: distributed or centralized).** Used markets and local copies are distributed. Authentication servers and subscription stacks are centralized.

Do not score this entry. The rules name the pattern; they do not replace the instruments or the evidence.
