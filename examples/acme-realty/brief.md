# Mockup brief: the broker's portfolio, explore view

Fictional brokerage, people and numbers.

**Product:** Acme Realty broker assistant | **Screen:** Portfolio, explore view (`#/portfolio/explore`) | **Date:** 2026-04-13 | **Owner:** Product manager

## The job

A broker at Acme Realty sells developers' launches and resale apartments in Alder Bay. Between two visits, on a laptop in the car or at the desk late in the afternoon, she needs to answer one question in under two minutes: who in my portfolio is waiting on me, and what exactly do they wait for? Today the answer lives in three places: the CRM, the visit notes on her phone, and the portal inboxes.

## Who opens it, and how often

Marina Costa, broker, 14 people in her portfolio (12 buyers, 2 owners), 9 listings, 3 to 5 visits a week. Opens the screen three to six times a day, for one to two minutes each time. Not technical; reads numbers fast, distrusts any number without a date.

## The number this screen must move

Buyers with a visit and no next step within 48 hours: from about half today (measured in the visit log of March) to under one in five. Secondary: portal leads answered within two hours.

## What the screen shows

- The portfolio as a dense list: person, stage, what they are looking for, budget as recorded, last contact with its date, the next step, and the assistant's proposal where there is one, with the evidence it rests on.
- Filters by stage, district, days since contact and source, with counts.
- An explore box: a question in plain words, answered only from the snapshot, with the source of every fact.
- A number strip for the whole portfolio: people, listings, open proposals, visits today, and the number that asks for action (people without contact for 14 days or more).

## What the screen must never do

- Write to the CRM without the broker's approval. The assistant proposes; the broker approves; every write shows "Undo".
- Show a number without its source and date. Where the CRM has no value, the cell reads "no data".
- Estimate a budget, a price or a decision date the source does not have.
- Send anything to a buyer, a developer or an owner.

## Autonomy tier of the assistant on this screen

Propose. It drafts tasks and notes with their evidence; nothing reaches the CRM until Marina approves. Acting with review is the next tier, after a month of shadow comparison.

## Data

Frozen snapshot of 13 April 2026, 16:10: 14 people, 9 listings, 12 visits in the last eight days, 5 open proposals, 4 portal leads, 7 open tasks. Three fields are empty in the source (two budgets, one phone) and one listing has no price yet; the screen says so. File: `data-snapshot.json`.

## Out of scope for version 1

Writing proposals, portal replies, a map, and anything a manager would see. Owners appear as people in the list, with their listings, and nothing else.

## Done when

Three brokers and the sales manager run the validation session on the live mockup, every decision is written as a spec line, and no "would you not trust" answer points at a number without a source.
