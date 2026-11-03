# Build workflow: from an empty repo to the demo

How FundEli5 gets built at the event, with coding agents. The modules come from [architecture.md](architecture.md#modules), the technical decisions from [tech-choices.md](tech-choices.md), the screens from [ux/](ux/README.md).

A timed rehearsal (1–3 Nov 2026) rebuilt every component from a repo like this one: 29 tickets, about 3 hours of agent work in all. Waiting was the real cost: plan limits, and agents stopping on a decision nobody had written down. So this workflow front-loads the decisions and keeps two tracks apart.

## Two tracks

| Track | What | Who decides | Starts |
|---|---|---|---|
| **Platform** | Everything that does not depend on the team's rules: skeleton, shell and design tokens, ports and fixture adapters, LLM egress (replay and Foundry), Privacy Gate, Request Parser, Share Class catalog, Check Record, Rule Card pipeline, validation module, the engine frame (Verdict combination, Citations, Draft vs Validated) | Fixed by the ADRs, [tech-choices.md](tech-choices.md) and [ux/](ux/README.md) | At once, while the team runs [tasks 1–3](tasks/README.md) |
| **Content** | The demo story, cast, funds, rule kinds and their readings, answer key, emails, wording | The team, through its map | After [task 1](tasks/01-chart-the-map.md); its scenarios land in `specs/` |

The tracks meet at the **rule plug-ins** (one class per rule kind, [tech-choices](tech-choices.md#rule-catalog-one-plug-in-per-rule-kind)) and the **answer key**: the engine ticket waits for the team's first answer-key rows.

## The rules

1. **`specs/` is the definition of done.** The team writes it ([specs/README.md](../specs/README.md)). A content ticket is done when its tag passes and `@answer-key` still passes. A platform ticket is done when its JUnit tests and the four promises (`FourPromisesTest`) pass.
2. **Agents never edit `specs/` or [hypotheses.md](hypotheses.md).** An agent that thinks a scenario is wrong stops and says why. Otherwise an agent can make a scenario pass by rewriting it. Before a merge, `git diff main -- specs/ docs/hypotheses.md` must be empty unless the ticket says the change is the point.
3. **A missing business answer becomes a hypothesis, not a guess in code.** The agent stops; the team adds the row to [hypotheses.md](hypotheses.md) with its `@assumed` scenario; the ticket restarts.
4. **Screens are built against the mockups.** A screen ticket's gate includes the [screen definition of done](ux/README.md#definition-of-done-for-a-screen): a Playwright screenshot per state, compared with the mockup.
5. **The API serves the screen.** A ticket that adds a screen state also adds what the API must return for it. No screen derives data by combining calls.

## Order

### Spine: one ticket at a time

| # | Ticket | Done when | Mode |
|---|---|---|---|
| S1 | **Skeleton**: Spring Boot 4 with a `pipeline` profile, devtools, springdoc; ArchUnit rules; Angular shell with `tokens.css` as `styles.css`, the top bar and both routes; the client generated from OpenAPI (one npm script); Cucumber runner on `specs/` with `not @live-llm`; Playwright in `frontend/e2e` with one test that screenshots the shell; `./start.sh` | `./mvnw test` passes; `ng build` passes; the shell screenshot matches the mockups' top bar | HITL |
| S2 | **Schemas and ports**: Rule Card, Subscription Request, Verdict, Check Record types; the out ports with fixture adapters on [contracts/fixtures](contracts/fixtures/); `LlmEgress` with the replay adapter | Fixtures load through each port; replay serves one recorded answer | HITL |
| S3 | **Walking skeleton**: an email runs through every seam with stubs (Privacy Gate → Request Parser on replay → engine with a fixed Verdict → template reply → Check Record), shown on the dealer screen **in the mockup's answered layout** with the shared `ui/` components | The flow runs over HTTP from the screen; the e2e test screenshots `answered` | HITL |
| S4 | **Rule Engine frame and the team's first rule kinds**, `/tdd`, one answer-key row at a time | `@rule-engine` and `@answer-key` pass on the team's rows; `engine-purity-reviewer` reports nothing | HITL |

S1–S3 need no content and start while the team charts its map. S4 starts when the team's first answer-key rows exist (task 3).

### Waves: at most 3 worktrees at once

Each wave's tickets touch disjoint packages. Start each with `claude --worktree <module>`.

| Wave | Tickets | Needs |
|---|---|---|
| A | Privacy Gate with Presidio ([ADR 0009](adr/0009-presidio-detects-personal-data-in-emails.md)) · Share Class catalog · Check Record with its API (the screen gets the record id in the answer) | S2, S3 |
| B | Request Parser and Reply Drafter on the Foundry adapter · explanation templates (the Verdict sentences, from task 2's wording) · validation module | A; the Verdict sentences from task 2 |
| C | Dealer screen, all states of `dealer.html` · validation screen, all states of `validation.html` · Rule Card pipeline (Jev ranking, drafting, quote check) for the team's funds | B for the screens; the team's fund list for the pipeline |
| Integrate | Merge, then `demo-flow-verifier` on `@must` | All of the above |

The rest of the team's rule kinds join as tickets in any wave once their rows are in the answer key: one plug-in class each.

## How much an agent does alone

| Modules | Mode | Gate before the builder reads the diff |
|---|---|---|
| Rule Engine, rule plug-ins, Scale Mapping | HITL: `/tdd`, the builder picks each next example | module tag + `@answer-key`; `engine-purity-reviewer` |
| Privacy Gate, Request Parser, Reply Drafter, LLM egress | HITL | module tests; `privacy-gate-auditor` |
| Share Class catalog, Check Record, validation module, Rule Card pipeline, explanation templates | AFK: `/implement` in a worktree until the gate passes | module tests; `java-reviewer` |
| Angular screens | AFK | the [screen definition of done](ux/README.md#definition-of-done-for-a-screen); `typescript-reviewer` |

An AFK agent that hits a stop condition stops and reports. It never works around it.

## The build ticket

`/to-tickets` publishes one issue per row above, labelled `ready-for-agent` (AFK) or `ready-for-human` (HITL), with blocking edges that follow the spine and the waves. Every body uses this template, so an agent starting cold has what it needs:

```markdown
## Goal
<one sentence in GLOSSARY.md terms: what the module does in the demo story>

## Done when
- <module tests or Cucumber tags> pass, with no undefined step
- `@answer-key` still passes; `FourPromisesTest` passes
- <for a screen> the Playwright test of each listed state passes and its screenshot matches docs/ux/screens/<file>
- <gate agents> report nothing

## Read first
- GLOSSARY.md; ADRs <numbers>; architecture.md row "<module>"
- contract or schema: <path>; screens: docs/ux/README.md section "<section>", mockup state <file#state>
- hypotheses.md rows: <rows>, or "none"

## Seam
May change: <packages / folders>. Calls only: <ports or modules>.
API it must return for the screen: <fields>, or "none"

## Must not
- edit specs/, docs/hypotheses.md, generated client code, or another module's package
- call an LLM except through the egress client (ADR 0004)
- put a raw colour, enum, ISO date or file id on screen

## Stop and ask when
- a scenario looks wrong or contradicts an ADR
- a business answer is needed that hypotheses.md does not give
- a port or schema signature must change
- the mockup has no state for what the screen must show
```

## Day to day

| When | Do |
|---|---|
| Start a ticket | `claude --worktree <module>`, then `/tdd <issue>` (HITL) or `/implement <issue>` (AFK) |
| Before merging | the module's tests and tags, `@answer-key`, the gate agents, the empty `specs/` diff; for a screen, look at its screenshots |
| API changed | regenerate the Angular client, commit both sides together |
| A hypothesis changes | update [hypotheses.md](hypotheses.md); the failing scenarios become the follow-up ticket |
| Integration, freeze, rehearsal | `demo-flow-verifier` on `@must` |
