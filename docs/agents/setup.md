# Setup: install before you build

The Claude Code setup for anyone who builds, and for any team member who wants to try an agent. Target time: 10 minutes.

## 1. Model access

| Who calls | Through | Setup |
|---|---|---|
| Claude Code (building) | the event's Claude access on the cloud VM | `claude`, then `/status` shows the account or the Foundry resource. Settings for Foundry: `CLAUDE_CODE_USE_FOUNDRY=1`, `ANTHROPIC_FOUNDRY_RESOURCE`, pinned `ANTHROPIC_DEFAULT_*_MODEL` deployments ([foundry-models.md](../research/foundry-models.md)) |
| The app's LLM egress (Request Parser, Reply Drafter, pipeline drafting) | Claude on Azure Foundry, through the `foundry` egress adapter | the Foundry endpoint and key as environment variables, never in the repo. Tests run on the `replay` adapter and need no model |
| Page selection in the Rule Card pipeline | TypeSafe Jev, `https://api.typesafe.ai`, model `jev-latest` | `export TYPESAFE_API_KEY=…`. If Jev is not allowed at the bank, the keyword fallback in [tech-choices.md](../tech-choices.md#rule-card-pipeline) applies |

The data rules are the same on every adapter ([ADR 0004](../adr/0004-two-runtimes-one-llm-egress.md)): only Privacy Gate output reaches an LLM.

## 2. Clone and trust the repo

```bash
git clone <repo url> && cd <repo>
claude          # accept the trust prompt
```

Trusting the folder loads `.claude/settings.json`: the plugins (`frontend-design`, `playwright`, `pr-review-toolkit`, `jdtls-lsp`, `typescript-lsp`), the gate agents in `.claude/agents/` and the skills in `.claude/skills/`. The language plugins need their servers on the `PATH`: `brew install jdtls` (JDK 17+) and `npm install -g typescript-language-server typescript`. Playwright needs its browser once: `npx playwright install chromium`.

Check: `/plugin` lists the plugins as enabled; `/agents` lists `privacy-gate-auditor`, `engine-purity-reviewer`, `demo-flow-verifier` and the stack reviewers; typing `/` shows `wayfinder`, `to-tickets`, `tdd` and `implement`.

## 3. Angular CLI MCP

Gives the agent `ng` targets, the Angular docs and the best-practices guide:

```bash
claude mcp add angular-cli -- npx -y @angular/cli mcp
```

## 4. Look at the screens before building them

Open `docs/ux/mockups/dealer.html` and `docs/ux/mockups/validation.html` in a browser; the switcher in the bottom-left corner walks through every state. These pages are the target of every screen ticket ([ux/README.md](../ux/README.md)).

## 5. Run the executable specification

`specs/` holds the team's scenarios in Gherkin ([specs/README.md](../../specs/README.md)). Cucumber is wired in the skeleton (spine S1):
- a `@Suite` runner, `SpecificationSuite`, with `@SelectDirectories("../specs")` relative to `backend/`. Not the `cucumber.features` property: under the JUnit 6 Suite engine it finds nothing;
- an undefined step is an error, so `./mvnw test` runs `SpecificationRunsTest` instead, which fails only on a scenario that really fails. One module's scenarios: `./mvnw test -Dtest=SpecificationSuite -Dcucumber.filter.tags="<tags>"`;
- default filter `not @live-llm`, with the egress in replay mode, so a run makes no model call;
- one step-definition package per module. An undefined step is that module's to-do list.

`@assumed` scenarios still run. A failing `@answer-key` row blocks the rehearsal.

## 6. Daily moves

| When | Do |
|---|---|
| Two modules at once | `claude --worktree <module>`, one worktree per agent |
| API changed | regenerate the Angular client, commit both sides together |
| Build broken | `java-build-resolver` (Spring Boot) or `ts-build-resolver` (Angular) |
| Before merging | the module's tests; the stack reviewer agent; `privacy-gate-auditor` if an LLM call or client field is touched; `engine-purity-reviewer` for the engine; for a screen, its Playwright screenshots |
| Integration, freeze, rehearsal | the `demo-flow-verifier` agent |
