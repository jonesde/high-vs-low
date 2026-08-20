---
id: pla-003
title: Manufacturer post-sale control of repair markets
slug: manufacturer-repair-control
outcome: Manufacturer post-sale control of repair markets and parts
jurisdiction: [US-federal, US-state]
domains: [intellectual-property, personal-property, technology-access]
routing:
  enabled: [civil, contractual, regulatory]
  closed: [civil]
instruments:
  - 17 U.S.C. § 1201
  - 35 U.S.C. design patents
  - 35 U.S.C. patent exhaustion
status: initial
related:
  - dmca-takedown-content-id
  - noncompete-trade-secrets
  - platform-safe-harbors
  - digital-license-not-sale
  - security-research-knowledge-ban
  - historical-technique-privilege
updated: 2026-08-20
---

# Manufacturer post-sale control of repair markets

Once a machine is sold, the buyer's ordinary right to repair it collides with copyright anti-circumvention rules, embedded software, design patents, and parts-pairing. Circumventing a digital lock to repair a device you own can be a freestanding violation even when the repair would not infringe copyright. Independent repair is the closed analog.

## Outcome / Goal

The practical result is manufacturer control of post-sale repair, parts, diagnostics, and software authorization. The parties who obtain it are original-equipment manufacturers and their authorized service networks. Independent repair shops, owners, and secondary parts markets face legal risk, unavailable parts, or paired components that refuse to function without manufacturer cryptographic approval.

## Contrast / Parallel Track

Repair of purchased chattel is ordinary personal-property use. Independent repair of a purely mechanical good is not a copyright event. After software, TPMs, and design-patented replacement parts enter the product, the same act (open, diagnose, replace, close) can trigger DMCA § 1201, patent threats, and contract/warranty voiding. State right-to-repair statutes try to reopen that analog; manufacturers answer with federal-preemption arguments and technical work-arounds.

## Formal Legal Instruments

| Instrument | Role in the outcome | Citation |
| ---------- | ------------------- | -------- |
| DMCA anti-circumvention | Makes circumvention of an access-control TPM unlawful as such; trafficking in circumvention tools is separately banned | [17 U.S.C. § 1201(a)–(b)](https://www.law.cornell.edu/uscode/text/17/1201) |
| Triennial exemptions | Temporary, class-specific permission to circumvent for named uses (including some repair); must be renewed | [17 U.S.C. § 1201(a)(1)(B)–(D)](https://www.law.cornell.edu/uscode/text/17/1201); 37 C.F.R. § 201.40 |
| Copyright in embedded software | Supplies the "work protected under this title" that the TPM is said to protect | Title 17 generally |
| Design patents on parts | Exclusive rights in ornamental designs of replacement parts (collision parts, device shells) | 35 U.S.C. Chapter 16 |
| Contract, warranty, and parts-pairing | Private restrictions plus cryptographic pairing that makes third-party parts fail | Manufacturer terms and firmware |
| Patent claims on cartridges and chips | Post-sale control of refill/remanufacture until exhaustion doctrine cuts them back | 35 U.S.C. § 271; *Impression Products v. Lexmark*, 581 U.S. 318 (2017) |
| State right-to-repair laws | Attempted restoration of owner/independent repair; often limited by preemption claims and OEM design choices | State statutes |

Section 1201(c)(1) says the section does not affect fair use or other infringement defenses. Circumvention liability is still a separate count. An owner who bypasses a lock to perform a noninfringing repair can violate § 1201 even if no copyright is infringed.

## Routing

Enabled: civil DMCA claims, design-patent claims, contract/warranty leverage, and the regulatory exemption process as a pressure valve. Closed: a stable property right of the owner to repair, and a stable privilege of independent shops to do the same work.

Procedural features:

- Exemptions last three years, cover named classes of works, and do not legalize trafficking in tools under § 1201(a)(2)/(b).
- The tenth triennial proceeding is underway; renewed exemptions would run October 2027–October 2030. Repair-related exemptions have expanded (2024 final rule) but remain temporary and bounded.
- Federal copyright and patent arguments are used to cabin state repair mandates.

## Application Evidence

This entry is stronger on mechanism than on a single national dollar figure.

The mechanism is the freestanding circumvention ban. Repair of a tractor, phone, or medical device that requires bypassing a TPM is legally unlike repair of a hammer. Independent repair advocacy (iFixit, PIRG, state bills) and OEM opposition (copyright, safety, cybersecurity, trade secret) are the public record of that split.

Copyright Office practice treats repair as an exemption category, not as outside § 1201. That is evidence that ordinary owner repair is the exception that must be pleaded every three years, not the baseline.

Design-patent assertion against crash parts and consumer-device shells, and manufacturer parts-pairing (phones, cars, appliances, **printer cartridges**), are the non-copyright complements: even when § 1201 is not the pleaded count, the repair market remains closed.

**Printer cartridges as a worked example.** Lexmark encoded toner cartridges so that a microchip handshake with the printer firmware would refuse third-party or refilled cartridges. Static Control Components sold replacement chips. Lexmark sued under DMCA § 1201 (circumvention of an access control on the "Printer Engine Program") and copyright. The Sixth Circuit in *Lexmark International, Inc. v. Static Control Components, Inc.*, 387 F.3d 522 (6th Cir. 2004), rejected the § 1201 theory: the authentication sequence did not effectively control *access to a copyrighted work* in the statutory sense; it controlled whether the printer would accept a cartridge. A buyer who already had the printer could read the firmware. The authentication lock was a parts-pairing gate, not a copyright lock.

Lexmark also used patent claims and a "Prebate" single-use contract (discount if the buyer agreed to return the empty cartridge) against remanufacturers. In *Impression Products, Inc. v. Lexmark International, Inc.*, 581 U.S. 318 (2017), the Supreme Court held that Lexmark exhausted its U.S. patent rights in cartridges it sold, including sales abroad and sales under the return program. A patentee's decision to sell exhausts the patent; post-sale restrictions do not preserve a patent infringement theory against refillers.

Together the two Lexmark cases show the stack and the remaining hole. Patent exhaustion closed one post-sale patent path. DMCA § 1201, as pleaded, failed when the TPM was really a parts authenticator. Firmware pairing, chip cryptography, and contract/warranty terms remain available, which is why cartridge aftermarkets still fight authentication rather than a live patent-exhaustion theory. The buyer has the printer and the money for toner. Use of a third-party cartridge is the restricted technique.

## Domain Tags

intellectual-property, personal-property, technology-access

## Sources

1. 17 U.S.C. § 1201 (Circumvention of copyright protection systems). <https://www.law.cornell.edu/uscode/text/17/1201>
2. U.S. Copyright Office, Section 1201 rulemaking (tenth triennial; 2024 final rule). <https://www.copyright.gov/1201/>
3. 37 C.F.R. § 201.40 (current temporary exemptions). <https://www.ecfr.gov/current/title-37/chapter-II/subchapter-A/part-201/section-201.40>
4. Federal Register, "Exemption to Prohibition on Circumvention of Copyright Protection Systems for Access Control Technologies," 89 Fed. Reg. 84470 (Oct. 28, 2024). <https://www.govinfo.gov/content/pkg/FR-2024-10-28/pdf/2024-24563.pdf>
5. *Lexmark International, Inc. v. Static Control Components, Inc.*, 387 F.3d 522 (6th Cir. 2004).
6. *Impression Products, Inc. v. Lexmark International, Inc.*, 581 U.S. 318 (2017). <https://supreme.justia.com/cases/federal/us/581/15-1189/>
7. EFF, Lexmark v. Static Control case archive. <https://www.eff.org/cases/lexmark-v-static-control-case-archive>

## Related Entries

- [DMCA takedown and Content ID](dmca-takedown-content-id.md) (pla-005) — another DMCA title used to control downstream use.
- [Non-competes and trade secrets](noncompete-trade-secrets.md) (pla-011) — IP-adjacent tools that restrict post-relationship economic activity.
- [Platform safe harbors](platform-safe-harbors.md) (pla-012) — statutory safe harbor plus private terms as a control stack.
- [Digital license-not-sale](digital-license-not-sale.md) (pla-013) — the same post-transfer control, aimed at the copy rather than the spare part.
- [Security research knowledge ban](security-research-knowledge-ban.md) (pla-015) — § 1201 trafficking in how the lock works, not just using a spare part.
- [Historical technique privilege](historical-technique-privilege.md) (pla-021) — Carterfone-era attachment bans as the analog network version of parts-pairing.

## Expansion notes

Specific 2024 repair exemption classes; preemption litigation on state right-to-repair; quantified independent-repair market share by sector (auto, electronics, agriculture, medical, printer supplies).

## Framework notes

Relevant distinction rules from [SKILL.md](../SKILL.md):

- **Rule 6 (Individual autonomy).** The owner's "no" to manufacturer-only repair is met with legal and technical penalty, not with a respected alternative.
- **Rule 22 (Legalism as Idol; hedge-as-law).** A copyright anti-circumvention rule, written for access controls on works, is elevated into a repair ban. The hedge becomes the law.
- **Rule 33 (Dominion: stewardship or ownership).** The manufacturer continues to act as owner after sale. The buyer is a licensee of function.
- **Rule 40 (Safeguards: principled or procedural).** The triennial exemption is a procedural safeguard. It does not establish a principled owner-repair right.
- **Rule 42 (Production: distributed or centralized).** Independent, local, open repair is the distributed pattern. TPM-plus-pairing is centralized, proprietary, and fragile by design.

Do not score this entry. The rules name the pattern; they do not replace the instruments or the evidence.
