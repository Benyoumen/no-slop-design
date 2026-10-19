---
name: visual-validation-session
description: Runs a thirty-minute validation of a mockup with the people who will use it or decide about it, at least one of them not technical. Opens on the job rather than the screen, asks five questions plus one about the agent, records every statement as a decision, an objection with an owner, or a data gap, and turns decisions into spec lines with a link to the mockup and the date. Use before any production code, after each round of changes, and whenever a sponsor asks "can we see it first".
license: MIT
metadata:
  version: "1.0"
  author: Benjamin Tayar
  method: no-slop-design
---

# Visual validation session

> Thirty minutes with the right people and a screen that looks real settles more than a month of documents.

## When to use

- A mockup passed the audit and nothing has been built yet.
- A sponsor wants to see it before committing time or money.
- A round of changes needs to be checked with the same people.
- An agentic screen needs to be trusted: people must say whether they would let the agent do what it proposes.

Not a demo. Not a presentation. A working session in which the participants use the screen.

## Inputs

1. The mockup, passing the audit, on a device the participants would use (a phone for a phone screen).
2. Three to five participants: people who will use the screen, and the person who decides about it. At least one not technical.
3. The brief, for the job and the number.
4. The notes template ([`templates/validation-session-notes.md`](../../templates/validation-session-notes.md)).

## Procedure

1. **Open on the job, not on the screen.** "You just finished a meeting with a customer. Show me what you do next." Then show the screen doing that step.
2. **Let them use it.** Hand over the mouse or the phone. Watch where they hesitate. Do not explain. Note the hesitation and where it happened.
3. **Ask the five questions**, in this order, to each participant: What is this screen for? What would you do first? What is missing to do your job? What here would you not trust? What would you remove?
4. **For an agent screen, ask the sixth**: What did the agent do, and would you let it do that without asking you?
5. **Record every statement as one of three things.** A decision: something the screen will do, which goes into the spec. An objection: a disagreement with an owner and a date to resolve it. A data gap: something the snapshot did not have, which goes into the next snapshot.
6. **Close in the last five minutes** by reading the decisions back. A decision nobody repeats is not a decision.
7. **Within the day, write the spec lines.** Each decision becomes a line a developer and a coding agent can build from: what the screen shows, what the person can do, what the system writes, what it must never do, with a link to the mockup version and the session date.
8. **Regenerate the mockup** from the decisions and the new data, and schedule the next round if an objection is open.

## Rules

- Thirty minutes. A session that needs more has too much on the screen.
- At least one participant is not technical. If they cannot say what the screen is for, the screen is not ready, whatever the engineers think.
- The facilitator does not explain the screen. An explanation in the room is a defect in the design.
- Every statement is recorded as a decision, an objection or a data gap. Nothing stays as "feedback".
- A decision is read back and confirmed before it is written.
- Spec lines link to the mockup version and the date. The mockup stays the visual reference and keeps being regenerated.
- Real data on the screen. A session on invented data validates nothing.

## Checklist

- [ ] Participants: users plus the decider, one of them not technical.
- [ ] Opened on the job; the participants used the screen themselves.
- [ ] Five questions asked to each; the sixth for an agent screen.
- [ ] Hesitations noted with their location.
- [ ] Every statement classified: decision, objection with owner and date, data gap.
- [ ] Decisions read back at the end.
- [ ] Spec lines written within the day, with mockup version and date.
- [ ] Next snapshot includes the data gaps; next round scheduled if an objection is open.

## Example

Acme Field Sales Assistant, the rep's daily list, session of 2026-04-14 with two reps, the sales manager and one engineer.

Weak: a forty-five-minute walkthrough of the screen by the product manager, ending with "any feedback?" and a list of eleven comments nobody classified. Three weeks later the engineer builds the comment he understood.

Corrected: the manager was asked to show what she does after a meeting; she opened the CRM. The screen was then shown doing that step. Decisions: proposals appear in their own column, never mixed with recorded facts; the approve button is labeled "Save to CRM" and shows a result line with Undo for ten seconds; the list is sorted by meeting time, not by amount. Objection: the manager wants managers to approve on behalf of reps; owner the sales director, by 2026-04-21. Data gap: the stage names in the CRM do not match the ones the reps use; next snapshot carries both. Full notes in [`examples/acme-sales-assistant/session-notes.md`](../../examples/acme-sales-assistant/session-notes.md).

## Definition of done

The session ran in thirty minutes with the right people, every statement is classified, the decisions were read back, and the spec lines exist with a link to the mockup version and the date.

## Related

- [`html-mockup`](../html-mockup/SKILL.md): the mockup the session needs.
- [`visual-slop-audit`](../visual-slop-audit/SKILL.md): the gate before the session.
- [backlog-writing-system](https://github.com/Benyoumen/backlog-writing-system): where spec lines become Features and User Stories (`write-prd`, `user-story-writing`).
- [agentic-ux](https://github.com/Benyoumen/agent-design-principles/tree/main/skills/agentic-ux): what an agent screen must show for the sixth question to have a good answer.
- Template: [`templates/validation-session-notes.md`](../../templates/validation-session-notes.md).
