# Validation session notes

Fictional company, people and numbers.

**Screen:** Daily list with agent proposals, mockup v3 | **Date:** 2026-04-14 | **Duration:** 30 min
**Participants:** two field sales reps, the sales manager (not technical, decider), one engineer
**Facilitator:** product manager

## Opening (the job, not the screen)

Prompt used: "You just finished the Northwind meeting and you have Harbor Foods in forty minutes. Show me what you do next."
What they did before seeing the screen: the first rep opened the CRM on her phone, scrolled to the deal, gave up on the stage field and wrote a note instead. The manager said she would have called the rep that evening to ask what happened.

## Hesitations observed

| Where | Who | What happened |
|---|---|---|
| Proposal column, first row | Rep 1 | Read the proposal twice to check whether it was already in the CRM |
| "Save to CRM" button | Rep 2 | Asked whether it sends the email too |
| Stale deals block | Manager | Asked why Meridian Clinics was there if a meeting happened today |

## The questions

| Question | Rep 1 | Rep 2 | Manager |
|---|---|---|---|
| What is this screen for? | "What I owe the CRM today" | "My meetings and what to do after" | "Whether my team updated after their meetings" |
| What would you do first? | Approve Northwind | Open Harbor Foods | Look at the stale deals |
| What is missing to do your job? | The email draft next to the proposal | Nothing | A view per rep |
| What here would you not trust? | A stage I did not choose | An amount that is not in the CRM | Any number without a date |
| What would you remove? | The contact title column | Nothing | The stale block from the rep's screen; it is mine |
| What did the agent do, and would you let it do that without asking you? | "It suggested moving Northwind to Negotiation. Yes, for stages. Not for amounts." | "Yes for the next step. Not for emails to the customer." | "No. Not yet. Show me a month first." |

## Decisions (read back and confirmed)

| # | Decision | Becomes spec line in |
|---|---|---|
| D1 | Proposals appear in their own column with the words "Agent proposes" and the evidence quote; never in the same cell as a recorded fact | Feature "Propose the CRM update", acceptance |
| D2 | The approve button is labeled "Save to CRM"; it writes only the CRM fields shown, never sends the email; the result line offers Undo for ten seconds | User Story "Approve a proposed update", acceptance and never list |
| D3 | The list is sorted by meeting time; the stale-deals block moves to the manager's weekly summary | Feature "Rep daily list", scope; Feature "Manager weekly summary", scope |

## Objections

| # | Objection | Owner | Resolve by |
|---|---|---|---|
| O1 | The manager wants to approve proposals on behalf of a rep who is on the road | Sales director | 2026-04-21 |

## Data gaps (into the next snapshot)

| # | Gap | Source to ask |
|---|---|---|
| G1 | Stage names in the CRM ("Proposal", "Negotiation") do not match the names reps use ("quote sent", "haggling"); the next snapshot carries both | CRM administrator |

## Spec lines written (within the day)

- The daily list shows today's meetings in time order with customer, stage and amount as recorded; where the CRM has no value the cell reads "no data"; mockup v3, session 2026-04-14.
- Each proposal is shown in its own column with "Agent proposes", the proposed value and the evidence quote with its timestamp; a proposal is never shown in the same cell as a recorded fact; mockup v3, session 2026-04-14.
- "Save to CRM" writes the proposed fields to the deal, shows "Saved to CRM" with Undo for ten seconds, and never sends the email draft; mockup v3, session 2026-04-14.
- The stale-deals block is removed from the rep's list and added to the manager's weekly summary; mockup v3, session 2026-04-14.

## Next round

2026-04-22, after O1 is resolved and the stage-name mapping is in the snapshot.
