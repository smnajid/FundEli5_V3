# Technical choices

The hackathon rebuilds every component from this repo, which holds no code. The technical decisions below were paid for by two earlier builds (fund-gate in October, a timed rebuild on 1–3 Nov 2026), together with the traps found along the way. They are decided: reopen one only if it blocks, and say why. Where a decision has an ADR, the ADR wins.

## Stack and versions

| Part | Choice | Version used in fund-gate |
|---|---|---|
| Backend | Spring Boot, Spring MVC (`spring-boot-starter-webmvc`), Maven wrapper | Boot 4.1.1, Java 25 |
| API spec | `springdoc-openapi-starter-webmvc-ui` | 3.1.1 |
| PDF text | Apache PDFBox | 3.0.8 |
| Architecture tests | ArchUnit (`archunit-junit5`) | 1.4.2 |
| Executable specification | `cucumber-java`, `cucumber-spring`, `cucumber-junit-platform-engine` (via `cucumber-bom`), `junit-platform-suite`, `junit-platform-testkit` | Cucumber 8.0.4 |
| Dev loop | `spring-boot-devtools` | from Boot |
| Frontend | Angular standalone components with signals, Vitest + jsdom, Prettier | Angular 21.2, TypeScript 5.9, Vitest 4.1 |
| Generated client | `@openapitools/openapi-generator-cli`, generator `typescript-angular` | 2.41.0 |
| Page selection | TypeSafe Jev over HTTPS (no SDK) | `jev-latest` |
| Personal-data detection | Presidio analyzer (Python service, Docker image `mcr.microsoft.com/presidio-analyzer`) behind the `PersonalDataDetector` port; `fixture` adapter for tests ([ADR 0009](adr/0009-presidio-detects-personal-data-in-emails.md)) | — |
| Python | only for real added value (ADR 0006): the Presidio service | — |

Group id `com.fundgate`, artifact `fundeli5`, base package `com.fundgate.fundeli5`.

## Repository layout

```
backend/            Spring Boot app, both runtimes (Maven runs here; paths below are relative to it)
frontend/           Angular workspace: shell/, ui/ (shared components), dealer-screen/, validation-screen/, generated/api/ (never edited)
specs/              the team's Gherkin, the definition of done (agents never edit it)
docs/contracts/fixtures/   the seed data the fixture adapters read
fund-documents/     the demo funds' public PDFs (prospectus, KIDs)
```

Properties that pointed at these: `fundeli5.fixtures.dir=../docs/contracts/fixtures`, `fundeli5.documents.folder=../fund-documents`, `fundeli5.llm.recordings=src/main/resources/llm-recordings`, `fundeli5.validation.drafts=${fundeli5.fixtures.dir}/draft-rule-cards,target/draft-rule-cards`, `fundeli5.pipeline.out=target/draft-rule-cards`.

## Package per module, ports and adapters

One top-level package per module of [architecture.md](architecture.md#modules), named after it: `answering` (the online flow orchestration), `privacygate`, `requestparser`, `shareclasscatalog`, `ruleengine`, `replydrafter`, `checkrecord`, `validation`, `rulecardpipeline`, `llm`; shared types in `eligibility` (Subscription Request, Verdict, Justification, Rule Outcome), `rulecard` (Rule Card, Rule, Condition, Rule Kind), `citation`, `bankdata` (codes and enums); one package per out port: `clientprofiles`, `shareclasses`, `funddocuments`, `fundregistrations`, `fxrates`.

- A port is a plain Java interface in its package (`ClientProfiles`, `ShareClasses`, `FundDocuments`, `FundRegistrations`, `FxRates`, `RuleCards`, `LlmEgress`, `RuleEngine`, `RequestParser`, `ReplyDrafter`, `PrivacyGate`, `CheckRecords`). Adapters sit in sub-packages: `fixture`, `folder`, `memory`, `replay`, `stub`, `web`.
- **Spring stays in the wiring and the web layer.** One `*Configuration` class per module at the root package or module root builds the objects; `web` sub-packages hold the controllers. Domain and application classes import no Spring, Jackson or PDFBox. An ArchUnit rule enforces it.
- Stubs first: the walking skeleton wires `stub` adapters for Privacy Gate, Request Parser, Rule Engine and Reply Drafter, then each ticket replaces one stub.
- Each port's adapter is chosen by a Spring property, so a bank adapter replaces a fixture adapter port by port (ADR 0008).

## Architecture tests (ArchUnit), written with the skeleton

1. The Rule Engine never depends on the `llm` package (ADR 0002).
2. Only the Privacy Gate constructs a `GatedEmail` (its output type).
3. The Request Parser and Reply Drafter never depend on `PortfolioReference` or `GatedEmail`: they see Portfolio Ids only (ADR 0004).
4. Spring is used only in the root wiring package and `..web..` packages.
5. `rulecard` never depends on `ruleengine`.
6. A rule kind's `Condition` is used only by its plug-in; only the plug-ins name a kind on the card.

Plus `RuntimeProfilesTest`: the dealer app starts a web server and reads Client Profiles, Share Classes and Fund Registrations; the `pipeline` profile starts with no web server, reads Fund Documents and never a Client Profile.

## The four promises in JUnit (not only Gherkin)

`FourPromisesTest` runs on frozen test-only fixtures under `src/test/resources/fixtures`, never the demo content, so the team can rewrite the content without breaking the guards:
- the Privacy Gate fails closed: an unknown portfolio reaches no LLM;
- what reaches an LLM names portfolios by Portfolio Id only;
- every Eligibility Check writes one Check Record with the Verdict shown;
- Verdict combination: any Fail gives Not Eligible, else any Review gives Needs Review, else Eligible;
- only a Validated Rule Card decides (a Draft card gives Needs Review).

## Rule catalog: one plug-in per rule kind

Each rule kind is one class implementing a `RuleKindPlugin<C extends Condition>`: its `RuleKind` constant, its condition type, its line of the drafting prompt, an optional `asDrafted` correction, `evaluate(condition, facts, lookups) → Optional<Finding>`, and `accumulates()` (all rules of the kind are shown and class-level rules add to fund-level ones, versus worst finding decides and class overrides fund). A `RuleCatalog` lists the plug-ins in order. The pipeline's drafting prompt is assembled from the catalog, one line per plug-in. The kinds in the reference: investor category, US Person exclusion, minimum initial subscription, mandate-only class, KID required for retail, Unmodelled Restriction, Target Market. Adding a kind the business asks for costs one class.

Engine frame rules to keep: Verdict combination above; Citations on every outcome; Draft vs Validated; a class-level rule overrides the fund-level one; contradictions between documents are flagged; a Stale card (newer document edition) still decides until the new version is validated.

## LLM egress

- One interface, `LlmEgress.complete(LlmRequest(model, system, prompt)) → LlmResponse`. It is the only code that calls a model (ADR 0004). On the online side the prompt is Privacy Gate output.
- **Replay adapter** (default for tests, `fundeli5.llm.endpoint=replay`): one JSON file per recording, `{"request": …, "response": …}`, matched on the whole request (model included, so changing the model means recording again). Unknown JSON properties fail loudly, because a misspelt key would load as null and never match. An unrecorded request throws `UnrecordedLlmRequest`. The specification records live answers with a recording egress in tests.
- **Claude plan adapter** (rehearsal only, never at the bank): runs `claude -p --output-format json --json-schema <schema>` as a subprocess, prompt on stdin. The spike's `ClaudePlanDrafter` used this and got the same scores as the API (18/18 rules on Nordea). No Citations API on this path: the model writes `{file, page, quote}` itself, and the quote check verifies each quote on its page.
- **Foundry adapter** (the event's live mode: the app's LLM calls go to Claude on Azure Foundry; see [foundry-models.md](research/foundry-models.md)): official Anthropic Java SDK. For the pipeline, pass 1 sends the selected PDF pages with Citations enabled (Opus), pass 2 turns that into the card with structured output (Sonnet). Spring AI 2.0's `ChatModel` flattens citations into one list and loses which passage supports which statement, so pass 1 calls the SDK client directly. Search **every** generation of pass 2 for the card and fail loudly when none parses: the first live run silently saved a 0-rule card.

## Rule Card pipeline

Command-line mode of the same app: profile `pipeline`, `spring.main.web-application-type=none`, an `ApplicationRunner`, writes Draft cards to `fundeli5.pipeline.out`. Steps: PDF to page text (PDFBox, 944 pages in about 5 s) → page selection → drafting through the egress → quote check → Draft Rule Card.

- **Page selection = Jev** behind a `PageRanking` port ([spike README](reference/rule-card-extraction/spike-README.md), issue #39 on fund-gate). Six rule kinds to rank for: the sub-fund's own description, US Person, investor eligibility, minimum, target market, other restriction. **Jev choice** selects: per kind, a choice question whose options are the pages plus "none", about 20 pages (32k tokens) per question, knockout rounds keeping the top 3 per batch. Keep pages 1–5 (front matter), add the page before each top page, round-robin over the six rankings up to a budget of 25 pages. Documents no longer than the budget are sent whole. **Jev per page** then runs as a check: one request per page, one yes/no question per kind; a kind whose best selected page scores under 0.5 is flagged "possibly missed" on the validation screen. Cost about $0.25 per 944-page prospectus. Cache rankings on disk so reruns cost nothing. Pages over 6,000 characters are cut.
- Jev API: `POST https://api.typesafe.ai/v1/systemone`, bearer `TYPESAFE_API_KEY`, body `{state, model, questions: {<id>: {type: choice|noul|score, instructions, criteria}}}`; the response has per-question probabilities and confidence. No streaming. A missing or bad key returns 403, not 401.
- Fallback if Jev is not allowed: keyword selection v2 at 40 pages (72/74 unseen rules), described in the spike README.
- **Quote check**: every cited quote must be found on its cited page. Normalise whitespace with `[\s\p{Z}]`, not `\s` (French no-break spaces); read control characters as a hyphen (the Citations API returns a line-break hyphen as U+0002); ignore soft hyphens.
- PDFs without a text layer (2 of 21 in the unseen set) can't be selected or checked: they need OCR first. None of the demo funds is affected.
- Reference material for drafting: [prompts](reference/rule-card-extraction/prompts/), [Rule Card JSON schema](reference/rule-card-extraction/rule-card.schema.json), gold cards ([Nordea](reference/rule-card-extraction/gold-rule-card.json), [Robeco, BlackRock](reference/rule-card-extraction/gold/)), page-recall keys and the [unseen documents' URLs](reference/rule-card-extraction/unseen-sources.txt).

## Executable specification wiring

As in [setup.md](agents/setup.md#run-the-executable-specification), with the traps:
- `@Suite` runner `SpecificationSuite` with `@SelectDirectories("../specs")`. The `cucumber.features` property finds nothing under the JUnit 6 Suite engine.
- An undefined step is an error, so the default build runs `SpecificationRunsTest` instead (via `junit-platform-testkit`), which fails only on a scenario that really fails.
- Default `cucumber.filter.tags=not @live-llm`; the egress in replay mode.
- One step-definition package per module under `specs/` in test (`ruleengine`, `privacygate`, …) plus a shared `SpecificationContext`.

## Frontend and the API

- `npm run generate-api`: runs an `OpenApiSpecTest` in the backend that writes `target/openapi.json`, deletes `src/app/generated/api`, then regenerates it with `typescript-angular`. Commit both sides together after every API change.
- `app.config.ts` calls `provideApi('')` (same origin); `proxy.conf.json` sends `/api` to `http://localhost:8080` under `ng serve`. Every controller lives under `/api`.
- Two screens as routes, `dealer-screen` and `validation-screen`, inside one shell (top bar, role). Replace the Angular CLI welcome page and its spec in the skeleton.

## Frontend: how the screens are built

The rebuild of 1–3 Nov produced screens that worked in tests and failed in front of a person (see [ux/README.md](ux/README.md#what-went-wrong-last-time)). These choices prevent the same result.

- **The design comes first, in the skeleton.** S1 copies [`docs/ux/tokens.css`](ux/tokens.css) into `frontend/src/styles.css` and builds the shell (top bar, page grid) from it. Screen tickets use the tokens and never write a raw colour, font size or spacing value.
- **The mockups are the visual oracle.** [`docs/ux/mockups/`](ux/mockups/) holds a static HTML page per screen and state; `docs/ux/screens/` holds their screenshots. A screen ticket is done when its Playwright screenshot, taken at 1440 × 900 on the seed data, matches the mockup's layout and the [screen checklist](ux/README.md#definition-of-done-for-a-screen) passes. Reproduce the look; do not copy the mockup's HTML.
- **Small components, one file each.** `ui/` holds the shared pieces of the [design system](ux/design-system.md#components): `verdict-line`, `citation-marker`, `evidence-card`, `banner`, `status-chip`, `drawer`, `empty-state`. A screen is a container that composes them. No component over 250 lines; templates and styles in their own files.
- **Labels come from one place.** `ui/labels.ts` maps every enum the API returns (rule kinds, outcomes, Verdicts, condition fields) to the words on screen, in English and French. A raw enum, ISO timestamp, array index or file id on screen is a bug.
- **The screen owns its states.** Every async call has loading, empty, error and success states, written in the mockups. An error names what the dealer can do next, never an internal id.
- **The API serves the screen.** If a screen needs a value (a record id, a Share Class name, a count of open rules), the backend returns it. The screen never derives it by diffing two calls.
- **Playwright from S1.** `frontend/e2e/` runs on the started app with seed data: one test per screen state of the mockups, each saving a screenshot under `frontend/e2e/screenshots/`. The `playwright` plugin lets the agent look at them.
- **Angular:** standalone components, signals, `@if`/`@for` control flow, OnPush. No component library: the design system is small and a library's look fights the mockups. Angular CDK only for the drawer's focus trap and overlay if needed.

## Check Record

The Check Record module owns the record's shape and exposes one in port to write it; `answering` calls that port. In-memory append-only store (`memory` adapter) is enough for the demo. The engine version recorded is the app's build version, so the `RuleEngine` port stays unchanged.
