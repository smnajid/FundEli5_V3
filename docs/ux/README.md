# Screens: what the dealer and the validator see

Two screens, both Angular ([ADR 0006](../adr/0006-spring-boot-and-angular-python-only-for-real-added-value.md)), inside one shell: the **dealer screen**, which answers a subscription request, and the **Rule Card validation screen**, which turns a Draft card into a Validated one. Vocabulary: [GLOSSARY.md](../../GLOSSARY.md). Look and parts: [design-system.md](design-system.md). Tokens: [tokens.css](tokens.css).

**The mockups are the visual oracle.** Open [`mockups/dealer.html`](mockups/dealer.html) and [`mockups/validation.html`](mockups/validation.html) in a browser. The switcher in the bottom-left corner walks through every state. Their screenshots are in [`screens/`](screens/). Reproduce the look, the layout and the wording; do not copy the mockup HTML. The example data is the seed cast, so the team's story will change the content but not the layout.

| State | Mockup | Screenshot |
|---|---|---|
| Dealer: paste | `dealer.html#paste` | [dealer-1-paste.png](screens/dealer-1-paste.png) |
| Dealer: working | `dealer.html#working` | [dealer-2-working.png](screens/dealer-2-working.png) |
| Dealer: answered | `dealer.html#answered` | [dealer-3-answered.png](screens/dealer-3-answered.png) |
| Dealer: Needs Review with suggestions | `dealer.html#review` | [dealer-4-review.png](screens/dealer-4-review.png) |
| Dealer: Privacy Gate refusal | `dealer.html#refused` | [dealer-5-refused.png](screens/dealer-5-refused.png) |
| Dealer: what the AI saw | `dealer.html#record` | [dealer-6-record.png](screens/dealer-6-record.png) |
| Validation: queue | `validation.html#queue` | [validation-1-queue.png](screens/validation-1-queue.png) |
| Validation: Draft card | `validation.html#draft` | [validation-2-draft.png](screens/validation-2-draft.png) |
| Validation: Validated | `validation.html#validated` | [validation-3-validated.png](screens/validation-3-validated.png) |

## Five principles

1. **Answer first, evidence one click away.** The dealer reads the Verdicts in five seconds. Every claim has its source a hover away, never a page away.
2. **Say it like a person.** A Verdict is a sentence ("`LOC90000101` **cannot buy** BI-EUR. BI-EUR is for institutional investors; this portfolio is retail"). That sentence is the "explain it like I'm five" capability. No enums, codes, array indexes or ISO timestamps on screen.
3. **Show what the AI did, and only that.** Everything an LLM wrote is purple and labelled (reply, suggestions). Everything the Rule Engine decided carries a Verdict colour. The two never mix. "The AI saw Portfolio Ids only" is always visible.
4. **Every state is designed.** Paste, working, answered, needs review, refused and error each have a mockup. The screen is never blank, never stuck, and never shows a raw error.
5. **The next action is obvious.** One primary button per state: Answer it, Copy reply, Draft reply, Accept and next, Validate card. A disabled button says what is left, in one short line.

## What went wrong last time

The rebuild of 1–3 Nov produced screens that passed their tests and failed in front of a person ([screenshots](v2-lessons/)). Each item below became a rule in [design-system.md](design-system.md) or [tech-choices.md](../tech-choices.md#frontend-how-the-screens-are-built).

| Seen | Rule now |
|---|---|
| The dealer screen showed an error and an empty card after **Answer it**: it diffed two Check Record lists to guess the record id | The API returns what the screen needs, including the record id; the screen derives nothing |
| Replay mode answered only a byte-exact email; one changed line gave "The AI could not read this email" | Demo emails are one click away (sample buttons); an unknown email in replay mode says so in words, not as a refusal |
| The validation header listed "rule 0 is not reviewed" … "rule 21 is not reviewed" | A disabled button shows one count line: "5 rules and 2 contradictions left" |
| `drafted 2026-11-02T12:10:18.702369228Z`, `reg_s true`, `client_type retail`, `loss_bearing full_loss` | Dates go through one formatter ("1 Nov 2026, 14:10"); enums go through `labels.ts` |
| Tab labels were file ids (`bnp-ch-bonds-chf-prospectus-2026-06-29 p.5`) | Documents show their title and type ("Prospectus · p.123", "BI-EUR KID · p.1") |
| 22 rules in one flat list, Target Market split into 5 lines per class, ISINs as group names | Rules grouped by "All classes", then by Share Class name; the 5 Target Market dimensions are one row |
| No contradiction banner, though it is the strongest moment of the validation demo | The banner is the first thing under the card header |
| A free-text "Validator" field and a dropdown of cards | The role and name sit in the top bar; cards are a queue with their status |
| One 900-line component per screen; the styling ticket came last and took 7 minutes | Tokens in the skeleton; small shared components; a Playwright screenshot per state in every screen ticket |

## Dealer screen: the answer sheet

Layout: one main column and an **evidence rail** on the right (`--rail-width`), which stays in view while scrolling (sticky). Below 1100 px the rail moves under the reply.

1. **Paste** (empty state). A title, one sentence on what happens, a large text area (or a dropped `.eml`), **Answer it** (⌘↵), the privacy promise in one line, and the **demo email** buttons that fill the text area. Under it, three cards explain the flow (Privacy Gate, Rule Engine, Reply), so a jury member who sees the first screen understands the product.
2. **Working.** The request summary, then a short list of steps that tick as the backend reports them: Privacy Gate, Reading the request, Checking the rules, Drafting the reply. Each tick shows what it found ("2 Portfolio References swapped"). Skeleton lines hold the place of the Verdicts. A check takes seconds, and these steps are the architecture shown live.
3. **Request summary.** One line: "Request from Marc Aebi · today 09:42", the subject, the green **"The AI saw Portfolio Ids only"** chip with each swap (`LOC90000101 → 3f6c…a4c3`), and "Show email and parsed requests", which unfolds the email and the editable request form.
4. **Summary strip.** "3 checks", then one chip per Verdict with its count.
5. **One Verdict line per check.** A Verdict chip, a headline sentence (Portfolio Reference in mono, the verb in the Verdict colour, the Share Class name), the plain-language reason with citation markers, and a metadata line (ISIN, amount, "7 rules checked · 1 failed"). **Why?** unfolds that check's rule outcomes. An alternative the reply suggests is tagged "alternative".
6. **Advisory Suggestions** (Needs Review only), in the AI style, grouped **Ask the Requester** and **Dealer to-do**, each with Accept and Dismiss (with an optional note). The line "They never change a Verdict" stays visible ([ADR 0007](../adr/0007-advisory-suggestions-never-change-the-verdict.md)). They sit above the reply because the dealer decides on them first.
7. **The reply**, the largest element: "Drafted by AI · edit before sending", the language chip, editable text, **Copy reply** (a "Reply copied" toast follows). Numbered markers `[1]` link to the rail: hovering a marker highlights its evidence card. On a check with suggestions the reply waits for **Draft reply**, and a line counts the undecided suggestions. A changed decision offers **Redraft**, which never overwrites the dealer's edits.
8. **Evidence rail.** One card per marker: number, rule kind, outcome (PASS, FAIL, REVIEW), Share Class, the quoted passage highlighted, document title and page, and "✓ quote found on page".
9. **What the AI saw** (link in the reply footer) opens the Check Record in a drawer: one row per check with its Rule Card version and Verdict; the engine and Scale Mapping versions; the Client Profile fields read, which stay in the bank; then one block per LLM call with model, provider, duration, the client fields sent as tags, and the gated prompt with the Portfolio Ids highlighted.
10. **Full Justification**, folded: every rule of every check, with its outcome and Citation.

**Privacy Gate refusal.** A red banner replaces everything below the paste step: "No AI was used for this email", what was found and where, and what happens next. The hand-entry form follows. The check runs as usual, and a template reply replaces the drafted one.

### The request form: what the dealer can edit

What the AI read is editable; what code found is not.

| Field | Editable | Source |
|---|---|---|
| Portfolio Reference | no (yes on the hand-entry form after a refusal) | Privacy Gate: a fixed pattern match plus a CRM lookup, no AI |
| Share Class | yes, a dropdown of catalog classes ("Nordea 1 Global Climate BP-EUR · LU0348926287") | the AI's mention, matched by the Share Class catalog |
| Amount, Currency | yes | AI. Currency matters: EUR 80,000 passes a EUR 75,000 minimum, and CHF 80,000 may not |
| Client initiated | yes | AI |

An edit shows **Re-check**, which reruns the engine. The Check Record keeps both the AI's parse and the dealer's correction.

## Rule Card validation screen: the document beside the rules

1. **Queue.** One row per fund's card: fund and regime, Share Classes, version, what it was drafted from, and a status chip (contradictions, rules left, Validated by whom and when). **Review** opens a Draft card.
2. **Card header.** Breadcrumb, fund name, each Share Class with its ISIN, "Draft v1 · drafted 1 Nov 2026, 14:10", what was read ("the prospectus (25 of 944 pages) and 2 KIDs"), "✓ all 21 quotes found on their page". On the right: "9 of 14 rules reviewed", a progress bar, **Validate card** (disabled until every rule is reviewed and every contradiction settled), and one line saying what is left.
3. **Contradiction banner** (amber), first under the header: which rules, and what each source says.
4. **"Possibly missed" banner** (neutral): a core rule kind with no rule for a Share Class, the pages not read, and a link to open them. Until the validator adds the rule or confirms there is none, that Share Class gives Needs Review.
5. **Three columns.**
   - **Rules**, grouped by "All classes" then by Share Class name. Each row has a status (open ○, accepted ✓, corrected ✎, contradiction !), the rule kind's label, its value in words, and its pages. The five Target Market dimensions are one row; selecting it shows all five in the decision panel.
   - **Document**: tabs per Citation, labelled by document type and page; the page text with a running head ("Nordea 1, SICAV · Prospectus · June 2026 · page 123 of 944") and every quote of the selected rule highlighted. The rendered PDF page with the highlight drawn on it is an upgrade if time allows.
   - **Decision**: the rule kind and Share Class, the value in large type, the extractor's summary, the **signals** the code checks (quote found on its page, definition found, contradiction with another source, value with no supporting quote), then the decision. A contradiction asks "Which source governs?" with one card per source. An Unmodelled Restriction asks Blocking or Noted ([ADR 0003](../adr/0003-validator-marks-unmodelled-restrictions-noted.md)). The value is editable with the right control (a select for a category, a number and currency for a minimum). **Accept and next** or **Save correction** then moves to the next open rule, and a "Then:" line names it.
6. **Validated.** The header chip turns green ("Validated v1 by J. Keller, 3 Nov 2026, 11:24 · in force for Eligibility Checks"), a green banner sums up what was done, every rule shows its final status, and the decision panel shows the version history.

The model's self-rated confidence is not shown: the signals the code can check replace it.

## What the team decides (task 2)

The layout above is a strawman, built for the reference story. In [task 2](../tasks/02-walk-the-screens.md) the team walks through the mockups and decides, among other things:
- the wording of every Verdict sentence, banner and button, in English and French;
- whether the **Advisory Suggestions** stay. The mockup shows them; the reference build cut them to a production slide to save build time;
- whether the organisers' other capabilities get a place on the dealer screen, and where: **guide the subscription form** (a checklist under an Eligible Verdict?), **alert on deadlines** (a dealing cut-off chip on the Verdict line? The reference build left it out, agreed with the sponsor), **answer questions about eligibility** (a "What would make it eligible?" link on a Not Eligible line?);
- what a dealer needs that the mockups do not show.

Changes go into the mockups and this page before the first screen ticket starts.

## Definition of done for a screen

A screen ticket is done when all of these hold on the started app with the seed data:
- [ ] A Playwright test per state of the mockup passes and saves a screenshot at 1440 × 900; the layout matches the mockup screenshot side by side.
- [ ] No raw enum, ISO timestamp, array index, file id or `undefined` appears on screen (the e2e test asserts it on the page text).
- [ ] Loading, empty and error states exist. Every error says what to do next.
- [ ] Only the design tokens are used: no hex colour, `px` font size or spacing outside `styles.css`.
- [ ] Keyboard: every action reachable by Tab, a visible focus ring, ⌘↵ on Answer it, Esc closes the drawer.
- [ ] Contrast: text at least 4.5:1 (the tokens meet it; don't put muted text on tinted backgrounds).
- [ ] The `typescript-reviewer` agent reports nothing; components stay under 250 lines.
