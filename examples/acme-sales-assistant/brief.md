# Mockup brief: the rep's daily list

**Screen:** Daily list with agent proposals (Acme Field Sales Assistant)
**Version:** v3 | **Date:** 2026-04-13 | **Owner:** Product manager

Fictional company, people and numbers.

## The job

In the words of a rep: "I come out of a meeting, I have four more today, and the CRM wants ten fields from me. I do it at night or not at all."

## The person

A field sales rep, four to six customer meetings a day, opens this on a laptop between meetings and on a phone in the car, with two minutes at most. Knows the customers well; does not know or care about CRM field names. Afraid of writing something wrong into a record the finance team reads.

## The number

CRM updated within 24 hours of a meeting: from 50% of meetings today to 90% in eight weeks.

## What the screen shows

1. Today's meetings in time order, with customer, stage and amount as recorded in the CRM (source: CRM deals, snapshot 2026-04-13).
2. What the agent proposes after each meeting, visibly separate from recorded facts (source: agent proposals from the meeting notes).
3. How many proposals are waiting and how many meetings are already updated (derived from 1 and 2).
4. Deals with no activity for 14 days or more (CRM last activity).

## What the person can do

Main action: approve a proposal, which writes it to the CRM and shows a result line with Undo for ten seconds. Secondary: edit the proposal before saving. Way back: Undo, or "Not now", which keeps the proposal for tomorrow.

## What the screen must never do

- Never write to the CRM without the rep's approval.
- Never show an amount or a stage the CRM does not have; show "no data".
- Never mix a proposal with a recorded fact in the same cell.
- Never hide a proposal because the rep dismissed it once; it returns tomorrow with a note.

## If an agent acts

Tier 2, propose: the agent drafts the update and the follow-up email; the rep approves each. Presence: one line in the header with the time of the last run. Trail: every saved proposal is listed with who approved it and when.

## Data snapshot

`data-snapshot.json`, 2026-04-13, CRM deals and meeting notes, names and amounts anonymized with a private rule; three deals have no amount in the source, one has no stage.

## States to show in version 1

Empty (no meetings today), loading (sync in progress), error (CRM sync failed at 07:05), success (proposal saved with Undo).

## Audience of the validation session

Two reps, the sales manager (not technical, decider), one engineer.
