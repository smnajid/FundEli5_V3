# Task 1: Chart the map

**Why.** The map is the team's plan: what the demo shows, which decisions are still open, and in what order the work happens. Every content ticket comes from it, so the team owns what gets built. Without it, the agents build the wrong thing quickly.

**Time box.** 60 minutes. **Who:** the whole team in one Claude Code session on a shared screen. One person types; everyone speaks for themselves. **Tool:** the `/wayfinder` skill.

**Output.**
- One issue labelled `wayfinder:map`, with the **destination** written in the team's words.
- Its child tickets, labelled by type (`grilling`, `prototype`, `research`, `task`), with blocking edges. The first two are tasks 2 and 3 of this folder.
- The platform's build tickets (spine S1–S3 and waves A–C from [build-workflow.md](../build-workflow.md)), labelled `ready-for-agent` or `ready-for-human`, so the builder can start right after the session.

## Before the session (builder, 15 minutes)

1. The repo is on the tracker the team will use, and everyone can open it.
2. `docs/agents/issue-tracker.md` describes that tracker. It is written for GitHub. If the bank's repo is on Azure DevOps or GitLab, ask Claude to rewrite it for that tracker and test one issue create, label, child link and close before the session.
3. The labels exist: `wayfinder:map`, `wayfinder:grilling`, `wayfinder:prototype`, `wayfinder:research`, `wayfinder:task`, plus the five triage labels of [triage-labels.md](../agents/triage-labels.md).
4. `claude` starts at the repo root, and `/wayfinder` appears when you type `/` ([setup.md](../agents/setup.md)).

## Steps

| Minutes | Step | What happens |
|---|---|---|
| 0–5 | **Open** | Run `claude` at the repo root on the shared screen. Type `/wayfinder` and paste the prompt below. |
| 5–20 | **Destination** | Claude asks what the 5-minute jury demo shows and what must work for it (the Must tier). Answer in the desk's words: who sends what, what the dealer sees, what the jury should remember. Push back until the destination fits in two lines. |
| 20–45 | **Breadth first** | Claude walks the open questions (who uses FundEli5 and for which steps of their work, which funds, which clients and cases, which rules decide, what the answer key must prove, what each organiser capability looks like). Don't answer them now. For each one, agree on **what kind of ticket** it is and **what blocks it**. Claude creates the tickets. |
| 45–55 | **Check the frontier** | Ask Claude: "List the frontier." Tasks 2 and 3 must be on it, unblocked. The platform build tickets must be published from build-workflow.md's spine and waves. |
| 55–60 | **Split** | Decide who takes which frontier ticket. Tasks 2 and 3 go to different people, so they run in parallel. The builder takes S1. |

## The prompt

Paste after `/wayfinder`:

```
Chart the map for FundEli5 at the hackathon, with the whole team present.
Every person in the session speaks for themselves: ask the team, never answer for them.

Destination to grill first: what the 5-minute demo to the jury shows, and the Must tier
behind it.

Fixed frame, not up for decision (ask only how to use it):
- The four promises (docs/adr): no LLM decides a Verdict; no client data reaches an LLM;
  every rule outcome cites its source; a person validates every rule before it decides.
- The organisers ask for: explain eligibility like I'm five, guide the subscription form,
  alert on deadlines, answer questions about eligibility.
- The repo holds no code. The platform is rebuilt from docs/architecture.md,
  docs/tech-choices.md and docs/ux/ (screens, design system, mockups). Its build tickets
  come from docs/build-workflow.md (spine S1-S3, waves A-C) and need no grilling:
  publish them with /to-tickets, labelled ready-for-agent or ready-for-human, with
  blocking edges as the workflow says.
- The content is the team's: demo story, cast, funds, rule kinds and readings, answer
  key, emails, wording. docs/contracts/fixtures/ is disposable seed data.
- About 20 build hours.

Out of scope: regimes other than CH/LU, suitability, the reverse lookup.

The first two tickets of the map, unblocked:
- "Walk the screens" (prototype), as docs/tasks/02-walk-the-screens.md describes.
- "Write the demo story and the answer key" (grilling), as
  docs/tasks/03-write-the-demo-story-and-answer-key.md describes.

Breadth-first after that, surface at least: who uses FundEli5 and for which steps of
their work; which funds; which clients and cases; which rules decide eligibility; what
the answer key must prove; what each organiser capability looks like for the desk.

Each grilling ticket closes by creating its build ticket(s) with /to-tickets, linked to
it and using the build-ticket template of docs/build-workflow.md.
Who takes which ticket is decided by the team once the map is ready.
Use GLOSSARY.md vocabulary; the team may change it.
```

## Done when

- [ ] The map issue exists, and its destination is two lines the whole team agrees with.
- [ ] "Walk the screens" and "Write the demo story and the answer key" are open, unblocked and assigned.
- [ ] S1 is published as a build ticket and assigned to the builder.
- [ ] Every open question raised in the session is either a ticket or under "Not yet specified" or "Out of scope" on the map.

## Pitfalls

- **Claude answering for the team.** If Claude proposes an answer to a business question, say "ask us" and move on. A grilling agent that answers its own questions has broken the skill.
- **Solving tickets during the charting.** The hour is for naming the questions, not answering them. Park the discussion in the ticket.
- **Re-deciding the platform.** The stack, the four promises and the screens' layout are decided. A real objection becomes a ticket, not a debate in the session.
