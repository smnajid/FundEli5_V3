# The team's first three tasks

The repo holds decisions and no code. Before anyone builds content, the team does three things, in this order. Each page says why the task matters, how long it takes, how to do it step by step, and what "done" looks like.

| # | Task | Time box | Who | Output |
|---|---|---|---|---|
| 1 | [Chart the map](01-chart-the-map.md) | 60 min | the whole team, in one Claude Code session | the map issue, its grilling tickets, and the platform's build tickets |
| 2 | [Walk the screens](02-walk-the-screens.md) | 45 min | the business members, the desk if available; one person drives Claude | decisions and wording in `docs/ux/`, updated mockups |
| 3 | [Write the demo story and the answer key](03-write-the-demo-story-and-answer-key.md) | 2–3 h, in two sittings | the business members; the desk confirms | `specs/00`, `01`, `99`, and the build tickets for the rule kinds |

Tasks 2 and 3 run in parallel once task 1 is done, with different people. Meanwhile the builder starts the platform spine (S1–S3 in [build-workflow.md](../build-workflow.md)), which needs no content. The two tracks meet when task 3 delivers its first answer-key rows: that is when the Rule Engine ticket (S4) can start.

```
 task 1: map ──┬── task 2: screens ──────────┐
   (all)       ├── task 3: story + key ──────┼──► S4 Rule Engine on the team's rows ──► waves ──► demo
               └── builder: S1 → S2 → S3 ────┘
```

## Before task 1 (10 minutes, everyone)

- Read the four promises: [ADR 0001](../adr/0001-llm-extracts-rules-engine-decides.md), [0002](../adr/0002-no-llm-at-check-time.md), [0004](../adr/0004-two-runtimes-one-llm-egress.md), [0007](../adr/0007-advisory-suggestions-never-change-the-verdict.md). In short: no LLM decides a Verdict; no client data reaches an LLM; every rule outcome cites its source; a person validates every rule before it decides.
- Open the two mockups in a browser: [dealer.html](../ux/mockups/dealer.html) and [validation.html](../ux/mockups/validation.html). Click through the states.
- Skim [GLOSSARY.md](../../GLOSSARY.md). These are the words the map, the specs and the code use.
