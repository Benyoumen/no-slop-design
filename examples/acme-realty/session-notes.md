# Validation session notes

Fictional brokerage, people and numbers.

**Screen:** Portfolio, explore view, mockup v2 | **Date:** 2026-04-14 | **Duration:** 30 min
**Participants:** three brokers, the sales manager (not technical, decider), one engineer
**Facilitator:** product manager

## Opening (the job, not the screen)

Prompt used: "You just finished the 10:00 visit at Linden Park and the next one is at 16:30. Show me what you do now."
What they did before seeing the screen: the first broker opened the CRM on her phone, found the buyer, could not find the visit notes, and wrote the follow-up from memory. The second said she keeps the "who is waiting on me" list in a notebook. The manager said he would not know until Friday's call.

## Hesitations observed

| Where | Who | What happened |
|---|---|---|
| Assistant column, first row | Broker 1 | Read the proposal twice to check whether the task already existed in the CRM |
| "Create the task" button | Broker 2 | Asked whether it also sends the email to the buyer |
| Explore answer, finding 5 | Broker 3 | Asked why a buyer who is not on the list is mentioned at all |
| Number strip, "14 days without contact" | Manager | Asked whether owners count as people in that number |

## The questions

| Question | Broker 1 | Broker 2 | Broker 3 | Manager |
|---|---|---|---|---|
| What is this screen for? | "Who is waiting on me" | "My portfolio with what to do next" | "Where the assistant thinks I am late" | "Whether my team follows up after visits" |
| What would you do first? | Approve the Helena task | Open Ingrid, the counter | Filter by 14 days | Look at the number strip |
| What is missing to do your job? | The listing's price next to the budget | Nothing | Portal replies in the same list | A view per broker |
| What here would you not trust? | A budget without a date | A "liked" I did not write | Any count I cannot click to see the people | Any number without a source |
| What would you remove? | The source column | Nothing | The district filter, I know my districts | The explore box from the broker's screen; it is mine |
| What did the assistant do, and would you let it do that without asking you? | "It drafted a task with the two visit notes. Yes for tasks. Not for notes on the buyer." | "Yes for tasks. Never for messages to buyers." | "Yes, if I can undo for a day, not ten seconds." | "No. Show me a month of its proposals first." |

## Decisions (read back and confirmed)

| # | Decision | Becomes spec line in |
|---|---|---|
| D1 | The assistant's proposal is shown in its own column with the words "Assistant proposes", the visit sentence it rests on, and the date of that visit; never in the same cell as a recorded fact | Feature "Propose the next step", acceptance |
| D2 | The approve button is labeled "Create the task"; it writes only the task shown, never a note on the buyer and never a message; the result line offers Undo until the end of the day | User Story "Approve a proposed task", acceptance and never list |
| D3 | The number "without contact for 14 days or more" counts buyers only; owners are counted in their own line | Feature "Portfolio number strip", scope |
| D4 | The explore answer lists only people who match the question; a related person who does not match goes under "What is not settled", not in the findings | Feature "Explore", acceptance |

## Objections

| # | Objection | Owner | Resolve by |
|---|---|---|---|
| O1 | The manager wants the explore box on his own screen and not on the brokers', because the brokers will ask it questions about each other | Sales manager | 2026-04-21 |

## Data gaps (into the next snapshot)

| # | Gap | Source to ask |
|---|---|---|
| G1 | Visit outcomes in the log ("liked", "undecided") are the broker's words; the CRM has a different list ("interested", "cold"). The next snapshot carries both | CRM administrator |

## Spec lines written (within the day)

- The portfolio list shows every person with stage, what they look for, budget as recorded with its date, last contact with its date, and the next step; where the CRM has no value the cell reads "no data"; mockup v2, session 2026-04-14.
- Each assistant proposal is shown in its own column with "Assistant proposes", the proposed task, and the visit sentence with its date; a proposal is never shown in the same cell as a recorded fact; mockup v2, session 2026-04-14.
- "Create the task" writes the task shown to the CRM, shows "Task created" with Undo until the end of the day, and never writes a note or sends a message; mockup v2, session 2026-04-14.
- The "without contact for 14 days or more" number counts buyers only; owners have their own line in the strip; mockup v2, session 2026-04-14.
- The explore answer lists only matching people; related people who do not match appear under "What is not settled"; mockup v2, session 2026-04-14.

## Next round

2026-04-22, after O1 is resolved and the outcome-name mapping is in the snapshot.
