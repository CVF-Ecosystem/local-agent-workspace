# PROJECT CONTEXT & WORKING GUIDANCE

This file holds the stable context of the project. Shared operating rules are in `AGENTS.md`.

## Project details

Fill in only what is useful and stable. Current progress belongs in STATE.

- Project name: [Name]
- Purpose and audience: [What this work is for; who will use it]
- Expected outputs: [Documents, SOPs, forms, reports, other]
- Language and house style: [For example: Vietnamese; use the existing company template]
- Main sources / approved templates: [Paths or entries in the source index]
- Important constraints: [Confirmed business constraints or data-handling limits]
- Data sensitivity: [Public / Internal / Contains personal or confidential data; state how to handle it]

## Purpose of this workspace

This is a file-based workspace for office and operational work: reading documents,
writing procedures and forms, analyzing spreadsheets, and occasional HTML reports.
The local project keeps the working record across agents and sessions.
This does not imply that model processing is offline or that files sync automatically.
It is not a software-development project.

## A useful default

Understand the request, use relevant context, deliver the requested result, then stop.
Choose the approach using your judgment, within the work limits in `AGENTS.md`. The guidance in `AGENTS.md` is shared
across providers and complements, rather than replaces, available native capabilities.

There are no required work modes. Ask only for information that is missing and material to the outcome.

## Sources and outputs

Start from the source the user names. If more context is needed, use the index or
read the relevant part of another source. Reuse already available information when
appropriate; revisit a passage if it may have changed or a conclusion depends on it.

Use the user's template when suitable. Examples bundled with a skill are starting
points, not approved business policy. Keep facts from sources distinct from proposals.

For content review, a draft in the conversation may be enough. When the user asks for
a file, create the file using suitable tools and check the aspects needed for use.
Keep drafts in `working/`, current deliverables in `output/`, and older versions in
`archive/` when retaining them is useful. Existing project paths can also be kept.
Preserve original sources; avoid creating extra versions or outputs without a reason.

## Continuity

STATE is a current snapshot: goal, current output, confirmed decisions, open points,
and next useful action. Overwrite it and keep it to about 60 lines.
Checkpoint when the next session would otherwise miss a meaningful change.

HANDOFF helps another session continue with the necessary files and next action.
It is optional and normally contains `None`. PENDING_LESSONS is also optional:
record a reusable insight only when it is worth keeping. Stable examples or tips
may later become a skill with the user's agreement, not automatically after an error.

## Skills

The skill index is a discovery aid, not a fixed router or a list to load every session.
Select by suitability, including the option of direct work or native capabilities.
A familiar skill does not need to be inventoried again each time it is used.

The user manages additions, removals, and significant rewrites of the library.
`skills/inbox/` remains optional. Provider-specific capability can be noted when
useful, without copying it or assuming it is available to a different provider.

## Completion

A result is done when it satisfies the requested scope and format with the needed
accuracy and usability. A concrete problem is a reason to revisit the relevant part;
spare capacity or the possibility of further polishing is not.
