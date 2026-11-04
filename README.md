# FundEli5

FundEli5 helps a private bank's fund dealing desk answer "may this client subscribe to this fund?" in seconds, with a cited Verdict and a reply the dealer can send. An LLM drafts Rule Cards from public fund documents, a person validates them, and a deterministic Rule Engine decides. No client data ever reaches an LLM.

This is the starting repo for the hackathon. It holds **decisions, no code**: the platform gets built here at the event from these documents, and the business content (demo story, rules, answer key) is written by the team.

## Start here

1. **Set up** Claude Code: [docs/agents/setup.md](docs/agents/setup.md) (10 minutes).
2. **Open the screens** in a browser: [dealer](docs/ux/mockups/dealer.html), [validation](docs/ux/mockups/validation.html). Use the switcher in the bottom-left corner.
3. **Do the team's first three tasks**: [docs/tasks/](docs/tasks/README.md).

To read these documents without hunting for files, open `docs/atlas/index.html` in a browser: every page here in one searchable page, with its links and backlinks resolved and both mockups embedded ([how it works](docs/atlas/README.md)).

| # | Task | Time |
|---|---|---|
| 1 | [Chart the map](docs/tasks/01-chart-the-map.md): `/wayfinder` with the whole team | 60 min |
| 2 | [Walk the screens](docs/tasks/02-walk-the-screens.md): the business decides on the mockups before any screen code | 45 min |
| 3 | [Write the demo story and the answer key](docs/tasks/03-write-the-demo-story-and-answer-key.md): `specs/`, written before the code | 2–3 h |

While the team runs tasks 2 and 3, the builder starts the platform spine ([build-workflow.md](docs/build-workflow.md)).

## What's here

| Path | What |
|---|---|
| `GLOSSARY.md`, `docs/adr/` | The domain vocabulary and the nine decisions, including the four promises |
| `docs/architecture.md` | Modules, data flow, privacy boundary |
| `docs/tech-choices.md` | Stack and versions, packages and ports, ArchUnit rules, LLM egress, Rule Card pipeline, how the screens are built |
| `docs/build-workflow.md` | The two tracks (platform, content), the spine and waves, the build-ticket template |
| `docs/ux/` | The screens: principles, lessons from the last build, state-by-state spec, design system, tokens, clickable mockups and their screenshots |
| `docs/tasks/` | The team's first three tasks, step by step, with the prompts to paste |
| `docs/contracts/` | The bank data contracts (Client Profile, Share Classes, Fund Documents, Fund Registrations) and the seed fixtures |
| `docs/hypotheses.md` | The register of working answers to open business questions |
| `docs/reference/rule-card-extraction/` | The extraction spike: findings, prompts, Rule Card schema, gold cards |
| `docs/research/` | Sample funds, LLM rule extraction, Claude on Azure Foundry |
| `fund-documents/` | Public prospectuses and KIDs of the four seed funds |
| `specs/` | Empty: the team's executable specification goes here ([specs/README.md](specs/README.md)) |
| `docs/atlas/` | All of the above as one offline HTML page, generated from the files, with a link check ([README](docs/atlas/README.md)) |
| `.claude/` | Settings and plugins, the gate agents, the skills the tasks use |
