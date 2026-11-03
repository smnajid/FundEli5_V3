## Agent skills

### Issue tracker

Issues are tracked in GitHub Issues through the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

Uses the five default labels: needs-triage, needs-info, ready-for-agent, ready-for-human, wontfix. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: one `GLOSSARY.md` plus `docs/adr/` at the repo root. See `docs/agents/domain.md`.

## How this repo is built

The repo starts with decisions and no code (README.md). The platform follows `docs/architecture.md`, `docs/tech-choices.md` and `docs/build-workflow.md`; the content follows the team's `specs/`. Never edit `specs/` or `docs/hypotheses.md`: a scenario that looks wrong or a missing business answer stops the ticket.

## Screens

Every screen matches its mockup in `docs/ux/mockups/` (screenshots in `docs/ux/screens/`) and meets the definition of done in `docs/ux/README.md`: only the tokens of `docs/ux/tokens.css`, the shared components of `docs/ux/design-system.md`, words from `ui/labels.ts` (never a raw enum, ISO date or file id), every state designed, and a Playwright screenshot per state. If the screen needs a value, the API returns it.

## Gates

Before merging, run the `privacy-gate-auditor` agent on changes touching an LLM call or client field, `engine-purity-reviewer` on Rule Engine changes, and `java-reviewer` or `typescript-reviewer` on the stack. Setup: `docs/agents/setup.md`.
