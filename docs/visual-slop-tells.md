# Visual slop: the tells, and what to do instead

Slop is not ugliness. Most of it is pleasant. It is the look of a screen nobody decided: the defaults a generator reaches for when the brief did not say otherwise. People read it in seconds, and what they read is "nobody owns this". Each tell below gives what it looks like, why it reads as slop, and the replacement. The replacements are cheap. None of them needs a designer; all of them need a decision.

| # | The tell | Why it reads as slop | Do this instead |
|---|---|---|---|
| 1 | A purple-to-blue gradient hero with glowing blobs | It is the single most generated composition of the decade | A plain background, one accent color, the product's own data in the first screen |
| 2 | Three columns of icon, title, sentence | The grid says "features" without saying which, and the icons are the same six everywhere | One capability per section with a real screen or a real number next to it. Cut the icons |
| 3 | Rounded cards with drop shadows on everything | Shadow on every element means hierarchy on none | Elevation for the one thing that floats, if anything. Borders and spacing do the rest |
| 4 | Headlines that could sit on any product ("Unlock the power of…", "Smarter, faster, better") | They are not about this product, so the reader learns nothing | A headline that names the job and the result: "Follow-up email drafted before you leave the parking lot" |
| 5 | Emoji as bullets, sparkles on anything "AI" | Decoration standing in for structure | Numbered steps, bold lead-ins, a real label such as "proposed by the agent" |
| 6 | Everything centered | Centering avoids the decision about reading order | Left-aligned text in a measure of 60 to 75 characters; center only a title or a single call to action |
| 7 | Invented data: round numbers, "John Doe", "Lorem ipsum" | Stakeholders approve a screen that does not exist | A frozen, anonymized snapshot of real data. Where there is none, show "no data", not zero |
| 8 | Five font weights, three families, random sizes | No type scale means no hierarchy | One family (two at most), a scale of five sizes, two weights |
| 9 | Spacing that changes from block to block | The eye reads inconsistency as carelessness | A spacing scale (4, 8, 12, 16, 24, 32, 48) used everywhere, including inside components |
| 10 | Color used for decoration: a different pastel per card, status in six hues | Color stops meaning anything, so warnings stop working | Color only for state and for the one accent. Gray for structure. Measure contrast at 4.5:1 |
| 11 | No empty, loading, error or success states | The happy path is the only path, which is never true in production | Every list has an empty state with a next action, every action has a result message, every fetch has a loading state |
| 12 | Cards of equal height with truncated text and "…" | The layout won over the content | Let content set height, or shorten the content at the source |
| 13 | A screen you cannot operate with a keyboard | It will fail its first accessibility review and its first power user | Focus order, visible focus, Escape closes, Enter confirms. Test it before the demo |
| 14 | Stock illustration people, isometric 3D, confetti | The art says "template" louder than the words say "product" | No illustration, or a real screenshot, or a diagram that explains something |
| 15 | Generic empty copy ("Welcome back!", "Get started", "Something went wrong") | The words were not written for this person | Copy that names the thing: "No meetings yet this week. Connect your calendar to see them here." |
| 16 | A hero image that does not load, a logo wall of brands you do not work with | Both destroy credibility in one glance | Only images that load from your own path, only logos with a written agreement behind them |

## The five-second test

Open the screen cold and answer four questions without scrolling: What is this for? Who is it for? What is the one thing I would do here? Does it look like somebody decided? If any answer is missing, the screen is not ready for a stakeholder.

## What a mockup must show for an agentic system

Agent screens produce a slop of their own: a chat box in the corner and a sparkle icon. Replace them with the four things a person needs to trust an agent:

1. **Presence.** What the agent is doing now, in one line, with a timestamp.
2. **Proposals, separate from facts.** A proposed CRM change looks different from a recorded one, and says what it is based on.
3. **Approval and undo.** Where the person says yes, and how they take it back.
4. **The trail.** What the agent did, when, on whose approval. Readable by someone who was not there.

The UX model behind these four is in [agent-design-principles](https://github.com/Benyoumen/agent-design-principles).

## Measured, not squinted

Checks that return a number, run at two widths (for example 1280 and 390):

- Contrast of every text and background pair, threshold 4.5:1 (3:1 for large text).
- Clipping: no element's bounding box exceeds its container without an intended scroll.
- Alignment: left edges of text in a column within 1px (padding plus border, not margin).
- Click targets: at least 40px on the small side for anything a hand will touch.
- Keyboard: every interactive element reachable, focus visible, dialogs closable.
- Ids unique, headings in order, images with alt text, forms with labels.

A defect found by eye becomes a check. The check is run without the fix first, to prove it fails. A check that never fails protects nothing.
