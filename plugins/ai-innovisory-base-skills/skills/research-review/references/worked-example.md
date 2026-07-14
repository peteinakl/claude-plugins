# Worked example — research review applied to a pricing brief

This example walks through the skill end-to-end on a short, fictional research brief. It's chosen deliberately to show a piece that would score reasonably well on fact-check's original seven criteria, but fails once the argument and insight checks are added — the case this skill exists for.

---

## Input

The user pastes the following 260-word brief:

> **Briefing: Subscription tier expansion for CloudDesk, June 2026**
>
> CloudDesk's user base grew from 40,000 to 95,000 between January 2024 and June 2026. Over the same period, the proportion of users on the free tier fell from 82% to 71%, while paid conversions rose to 29%. Support ticket volume also increased by 60% in the last year, driven mainly by onboarding questions from new free-tier signups.
>
> A survey of 340 paid users found that 64% cited "team collaboration features" as their primary reason for upgrading. Enterprise customers (over 500 seats) grew fastest, from 12 to 47 accounts in eighteen months, mostly through inbound sales rather than self-serve conversion.
>
> Because collaboration features are clearly driving the strongest growth segment, CloudDesk should launch a new "Teams Pro" tier priced above the current top plan, bundling collaboration tools that are currently included in the standard paid tier. This will capture additional revenue from the segment that values collaboration most, without disrupting the self-serve funnel that continues to convert free users steadily.
>
> The broader environment is favourable: competitors have raised prices in the last year, and enterprise software budgets are recovering after two years of tightening.
>
> Organisations should carefully weigh the trade-offs of tier restructuring against the risk of user churn, and monitor customer sentiment closely following launch.

---

## Verification work

**Claims identified** (step 2): six internal-data claims (user growth, tier mix, ticket volume, survey result, enterprise account growth) and two external market claims (competitor pricing, enterprise budget recovery). Interpretive claims: "collaboration features are clearly driving the strongest growth segment", the causal "without disrupting the self-serve funnel" assertion, and the closing recommendation to "carefully weigh… and monitor".

**Argument chain** (step 2, for criterion 8): *Enterprise accounts are the fastest-growing segment → the primary reason paid users upgrade is collaboration features → therefore, gate collaboration features into a new self-serve "Teams Pro" tier → this captures value from the segment that wants collaboration, without disrupting the self-serve funnel.*

The internal figures cannot be checked externally — they're proprietary to CloudDesk — so they're assessed for internal consistency and attribution (is a named source or system given?) rather than verified against a third party. The two external claims can be checked.

- User base, tier mix, ticket volume, survey, enterprise growth — **internal data, unverifiable externally.** No named source (dashboard, analytics platform, survey vendor) is given for any of them, only a description.
- *"Competitors have raised prices in the last year"* — Partial. Several comparable SaaS collaboration tools raised prices in 2025, but at least two held pricing flat over the same period; the claim overstates a mixed picture as uniform.
- *"Enterprise software budgets are recovering after two years of tightening"* — Confirmed, consistent with Gartner's 2026 IT spending forecast showing enterprise software spend growth returning to positive territory after two years of flat-to-declining budgets.

---

## Argument and insight assessment

**Argument quality (step 4):** The chain breaks at the connecting step. The piece's own evidence states that enterprise accounts — the segment it identifies as fastest-growing and most associated with collaboration features — grew "mostly through inbound sales rather than self-serve conversion." The proposed fix is a change to the *self-serve* pricing tier. The recommendation doesn't target the growth driver it just cited; it's a non-sequitur. The piece then asserts "without disrupting the self-serve funnel" with no support — removing features that existing paid self-serve users currently have access to is a well-known trigger for churn and downgrade requests, and the brief neither acknowledges this risk nor explains why it wouldn't apply here. That's an unsupported leap on top of the non-sequitur. **Fail.**

**Insight depth (step 5):** The core recommendation (launch a higher-priced tier gating a popular feature) is specific enough to act on, but it is also the single most predictable lever in SaaS pricing — it doesn't require this research to arrive at. Nothing in the piece names a churn threshold, a specific existing-user segment at risk, or a reason this move succeeds where similar feature-gating moves have caused backlash elsewhere. The closing line — "carefully weigh the trade-offs… and monitor customer sentiment closely" — is generic enough to append to any pricing memo on any product. **Fail.**

---

## Scorecard

# Research review scorecard

**Subject:** Briefing on CloudDesk subscription tier expansion, June 2026
**Input:** pasted text
**Length:** approximately 260 words
**Verification effort:** 2 externally verifiable claims identified, 1 confirmed, 1 partial; 6 internal-data claims noted as unverifiable externally due to no named source

## Overall verdict

**Draft only**

The piece fails Argument quality: its own evidence shows enterprise growth came through inbound sales, not self-serve, yet the recommendation is a self-serve pricing change justified by that same enterprise growth, with the churn risk of gating existing features asserted away rather than addressed. Argument quality is a blocking criterion, so the verdict is Draft only regardless of the piece's other scores — including a properly specific core recommendation, which passes Decision value on its own.

## Rubric

| Criterion | Score | Note |
|---|---|---|
| 1. Source quality | Partial | Internal figures are plausible but no dashboard, analytics platform, or survey vendor is named; the two external claims are checkable and one is a Partial. |
| 2. Evidence separation | Partial | "Because collaboration features are clearly driving the strongest growth segment" states an interpretation as settled fact. |
| 3. Currency | Pass | Data window (Jan 2024–Jun 2026) is current and clearly dated relative to the brief's own date. |
| 4. Coverage | Partial | Doesn't address the risk to existing paid users who already have the features being gated, or consider alternative pricing levers. |
| 5. Traceability | Partial | Figures are specific (340 survey respondents, 12→47 accounts) but none are attributed to a named source a reader could check. |
| 6. Contradictions | Partial | Presents the pricing move as low-risk without engaging the well-documented risk of backlash from gating previously-included features. |
| 7. Decision value | Pass | Ends with a specific, named recommendation (a priced "Teams Pro" tier) — not just general implications. |
| 8. Argument quality | Fail | The recommendation targets the self-serve funnel to capture value from a segment the piece says grew through inbound sales, not self-serve — a non-sequitur — and asserts no funnel disruption with no support. |
| 9. Insight depth | Fail | The recommendation is the most predictable pricing lever available, not a specific insight from this research; the closing guidance is generic boilerplate. |

## Claim verification

### Confirmed
- Enterprise software budgets recovering after two years of tightening — consistent with Gartner's 2026 IT spending forecast.

### Partial
- "Competitors have raised prices in the last year" — several comparable SaaS collaboration tools raised prices in 2025, but at least two held pricing flat; the claim presents a mixed picture as uniform.

### Unverified
- User base growth (40,000 → 95,000), tier mix shift, ticket volume increase, survey result (340 respondents, 64%), enterprise account growth (12 → 47) — all internal data with no named source (dashboard, analytics tool, survey vendor). Not necessarily wrong, but not independently checkable as presented.

## Coverage gaps

- No consideration of how existing paid self-serve users would react to losing access to features they currently have.
- No mention of alternative approaches to monetising the enterprise segment's preference for collaboration tools (e.g., an enterprise-tier add-on rather than gating a feature away from existing paid users).
- No named source for any of the internal figures, so a reader can't judge how current or reliable they are beyond the brief's own assertion.

## Contradictions surfaced or smoothed over

- The brief treats "gate a popular feature into a pricier tier" as a low-risk move without engaging the standard counter-risk — that removing included functionality from paying customers is a well-known driver of churn and downgrade requests in subscription businesses.

## Argument assessment

Chain as stated: enterprise accounts are the fastest-growing segment → collaboration features are the primary reason users upgrade → therefore gate collaboration features into a new self-serve tier → this captures value without disrupting the self-serve funnel.

The chain breaks between steps two and three. The piece's own data shows enterprise growth came "mostly through inbound sales rather than self-serve conversion" — so the segment the recommendation is meant to capture value from isn't reached through the self-serve tier being changed. That's a non-sequitur: the fix doesn't address the growth driver identified. The claim that this happens "without disrupting the self-serve funnel" is then asserted with no evidence, when removing currently-included features from existing paid users is a standard churn trigger the piece never addresses. Two connected failures, not one — this is a Fail, not a Partial.

## Insight assessment

The named recommendation (a "Teams Pro" tier, priced above the current top plan, gating collaboration features) is concrete enough to be actionable — it clears the bar for Decision value. But it isn't a specific insight generated by this research; it's the default move any pricing team would propose on seeing "feature X correlates with upgrades." Nothing in the piece names what churn rate would make the move a bad trade, which existing-user segment is most exposed, or what a successful versus failed launch would look like within a defined window. The closing sentence — "carefully weigh the trade-offs… and monitor customer sentiment closely" — could be pasted unchanged into a memo about any product change at any company. Fail.

## Recommended fixes

1. Re-target the recommendation at how CloudDesk actually reaches the enterprise segment — inbound sales — rather than a self-serve tier change that doesn't touch the growth driver identified.
2. Directly address the churn risk to existing paid users who currently have the features being gated, with a mitigation (e.g., grandfathering existing subscribers) or an explicit acknowledgement of the trade-off.
3. Name a source for the internal figures (analytics dashboard, survey vendor, date the survey was run) so a reader can judge reliability.
4. Replace the closing sentence with a specific success threshold or monitoring metric — e.g., "if 30-day churn among affected self-serve accounts exceeds X%, revert the change" — rather than generic caution.
5. Correct or qualify the competitor pricing claim to reflect the mixed picture rather than presenting it as uniform.

---

## What this example demonstrates

- A piece can Pass Decision value (a specific, named recommendation) and still Fail Insight depth (that recommendation isn't a genuine insight, and the surrounding guidance is boilerplate). The two criteria are independent — score them separately, as `references/rubric.md` notes.
- A piece can have internally consistent, plausible-sounding data and still fail Argument quality if the connective step between evidence and recommendation doesn't hold. Fluent, confident writing is not evidence the underlying chain is sound — write the chain out before scoring.
- Argument quality is a blocking criterion for good reason: no amount of strength elsewhere (here, a specific and well-formed core recommendation) rescues a piece whose central reasoning step doesn't follow from its own evidence.
