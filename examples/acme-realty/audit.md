# Visual slop audit sheet, filled

Fictional brokerage, people and numbers.

**Screen:** Portfolio, the generic version ([live](https://benyoumen.github.io/no-slop-design/portfolio-explore-generic.html)) | **Date:** 2026-04-13 | **Auditor:** Product manager
**Widths audited:** 1280 and 390 | **Scheme:** light (the page has no dark scheme)

## Five-second test (cold, no scrolling)

| Question | Answer | OK? |
|---|---|---|
| What is this for? | "Something with AI and real estate." The headline says "Unlock your real estate superpowers." | no |
| Who is it for? | "Marina," because the hero says welcome back. Not what Marina does between two visits. | no |
| What would I do first? | "Get started," the only button above the fold, and nobody can say what it starts. | no |
| Does it look like somebody decided? | It looks like a template someone accepted. | no |

## The sixteen tells

| # | Tell | Verdict | Evidence or reason |
|---|---|---|---|
| 1 | Gradient hero with glowing blobs | fail | Hero, violet to blue gradient with two blurred circles |
| 2 | Three columns of icon, title, sentence | fail | "Smart Matching, Lead Scoring, Instant Insights" with a house, a chart and a bolt |
| 3 | Shadows on everything | fail | Every stat, feature and buyer card carries the same 30px shadow |
| 4 | Headline that fits any product | fail | "Unlock your real estate superpowers"; "supercharge your pipeline" |
| 5 | Emoji bullets, sparkles on "AI" | fail | Sparkle pill in the hero, "AI insight" badge on every card, fire emoji on "Hot lead" |
| 6 | Everything centered | fail | Hero, stats, features and the buyers title are centered |
| 7 | Invented data | fail | "100+ leads", "$5M pipeline", "98% match accuracy"; budgets rounded to the nearest 50,000; the two buyers with no budget in the CRM show $500,000 |
| 8 | Many weights, families, sizes | fail | Weights 400, 600, 700 and 800; sizes 12, 13, 14, 15, 18, 28, 36 and 44 px |
| 9 | Inconsistent spacing | fail | Card padding 20, 24 and 28 px; section gaps 32, 40 and 48 px with no scale |
| 10 | Decorative color | fail | Gradient text on the numbers, violet badge, indigo secondary button; none of it means a state |
| 11 | No empty, loading, error, success states | fail | One state. "Approve" does nothing. |
| 12 | Equal-height cards with truncated text | fail | Buyer cards at a fixed minimum height, description clamped to two lines |
| 13 | Not operable by keyboard | pass | Buttons are buttons; focus is the browser default |
| 14 | Stock illustration, isometric 3D, confetti | pass | None, which is the one thing the template did not add |
| 15 | Generic copy | fail | "Our AI recommends reaching out today to maximize your conversion potential" on every card, including the buyer who signed last week |
| 16 | Broken images, borrowed logos | pass | No images |

## Measured checks (number and width for each)

| Check | 1280 | 390 | Threshold | OK? |
|---|---|---|---|---|
| Lowest text contrast (pair) | 2.54:1, gray labels and feature text on white | 2.54:1, same | 4.5:1 (3:1 at 24px+) | no |
| Hero body text on the gradient | 3.39:1 at the blue end, 4.00:1 at 90% opacity on the violet end | same | 4.5:1 | no |
| "Reject" text on its pink fill (buyer page, same kit) | 3.95:1 | same | 4.5:1 | no |
| Clipping (element, overflow in px) | 0 | 0 | 0 | yes |
| Left-edge alignment per column (px) | not applicable, everything centered | | 1 | n/a |
| Smallest click target (px) | 44 (buttons) | 44 | 40 | yes |
| Keyboard: all controls reachable, focus visible | yes, default focus ring | yes | yes | yes |
| Dialogs close by button, Escape, outside | no dialogs | | yes | n/a |

## States

| State | Reachable? | Says what happened and what to do? |
|---|---|---|
| Empty | no | |
| Loading | no | |
| Error | no | |
| Success | no, "Approve" has no effect | |

## Verdict

Not ready.

Three changes with the largest effect:
1. Replace the hero and the stat strip with the portfolio list on the real snapshot: person, stage, last contact with its date, next step, and "no data" where the CRM has none.
2. Put the assistant's proposal in its own column with the visit sentence it is based on, and make the button say what it writes: "Create the task", with Undo.
3. Add the empty, loading and error states and a result for the main action; then fix the two contrast failures with one ink and one gray from the tokens.

The screen built from these three changes is [portfolio-explore.html](https://benyoumen.github.io/no-slop-design/portfolio-explore.html).

## Allowlist (accepted exceptions)

| Tell or check | Location | Reason | Decided by | Date |
|---|---|---|---|---|
| none | | | | |
