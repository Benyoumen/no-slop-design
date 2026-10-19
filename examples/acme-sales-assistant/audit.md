# Visual slop audit sheet, filled

Fictional company, people and numbers.

**Screen:** Daily list, the generic version ([live](https://benyoumen.github.io/no-slop-design/daily-list-generic.html)) | **Date:** 2026-04-13 | **Auditor:** Product manager
**Widths audited:** 1280 and 390 | **Scheme:** light (the page has no dark scheme)

## Five-second test (cold, no scrolling)

| Question | Answer | OK? |
|---|---|---|
| What is this for? | "Something with AI and sales." The headline says "Unlock smarter selling with AI." | no |
| Who is it for? | "Ana," because the hero says welcome back. Not what Ana does or when. | no |
| What would I do first? | "Get started," which is the only button above the fold, and nobody can say what it starts. | no |
| Does it look like somebody decided? | It looks like a template someone accepted. | no |

## The sixteen tells

| # | Tell | Verdict | Evidence or reason |
|---|---|---|---|
| 1 | Gradient hero with glowing blobs | fail | Hero, violet to blue gradient with two blurred circles |
| 2 | Three columns of icon, title, sentence | fail | "AI Insights, Pipeline Growth, Instant Updates" with a robot, a chart and a bolt |
| 3 | Shadows on everything | fail | Every stat, feature and meeting card carries the same 30px shadow |
| 4 | Headline that fits any product | fail | "Unlock smarter selling with AI"; "supercharge your pipeline" |
| 5 | Emoji bullets, sparkles on "AI" | fail | Sparkle pill in the hero, sparkle badge on every card, check mark on every Approve |
| 6 | Everything centered | fail | Hero, stats, features and the meetings title are centered |
| 7 | Invented data | fail | "100+ meetings analyzed", "$1M pipeline", "98% AI accuracy"; amounts rounded to the nearest 5,000; three deals with no amount in the CRM show $10,000 |
| 8 | Many weights, families, sizes | fail | Weights 400, 600, 700 and 800; sizes 12, 13, 14, 15, 18, 28, 36 and 44 px |
| 9 | Inconsistent spacing | fail | Card padding 20, 24 and 28 px; section gaps 32, 40 and 48 px with no scale |
| 10 | Decorative color | fail | Gradient text on the numbers, violet badge, indigo secondary button; none of it means a state |
| 11 | No empty, loading, error, success states | fail | One state. Approve does nothing. |
| 12 | Equal-height cards with truncated text | fail | Meeting cards at a fixed minimum height, description clamped to two lines |
| 13 | Not operable by keyboard | pass | Buttons are buttons; focus is the browser default |
| 14 | Stock illustration, isometric 3D, confetti | pass | None, which is the one thing the template did not add |
| 15 | Generic copy | fail | "Our AI recommends following up today to maximize your conversion potential" on every card, including the deal that closed |
| 16 | Broken images, borrowed logos | pass | No images |

## Measured checks (number and width for each)

| Check | 1280 | 390 | Threshold | OK? |
|---|---|---|---|---|
| Lowest text contrast (pair) | 2.54:1, gray labels and feature text on white | 2.54:1, same | 4.5:1 (3:1 at 24px+) | no |
| Hero body text on the gradient | 3.39:1 at the blue end, 4.00:1 at 90% opacity on the violet end | same | 4.5:1 | no |
| "Reject" text on its pink fill (proposal page, same kit) | 3.95:1 | same | 4.5:1 | no |
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
| Success | no, Approve has no effect | |

## Verdict

Not ready.

Three changes with the largest effect:
1. Replace the hero and the stat strip with today's meetings in time order, on the real snapshot, with "no data" where the CRM has none.
2. Put the agent's proposal in its own column with the sentence it is based on, and make the button say what it writes: "Save to CRM", with Undo.
3. Add the empty, loading and error states and a result for the main action; then fix the two contrast failures with one ink and one gray from the tokens.

The screen built from these three changes is [daily-list.html](https://benyoumen.github.io/no-slop-design/daily-list.html).

## Allowlist (accepted exceptions)

| Tell or check | Location | Reason | Decided by | Date |
|---|---|---|---|---|
| none | | | | |
