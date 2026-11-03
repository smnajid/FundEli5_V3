# Task 3: Write the demo story and the answer key

**Why.** The answer key is the contract between the business and the code. It lists the cases the demo data must produce, with the expected Verdict and the outcome of every rule, written by the people who know the rules **before** the app answers. The Rule Engine is built test-first against it, so a wrong rule fails a row instead of surprising the jury. The story says which of those rows the jury sees.

**Time box.** 2 to 3 hours in two sittings: the story and the rules (sitting 1, 90 min), then the answer key and the Gherkin (sitting 2, 60–90 min). **Who:** the business members; the desk confirms the rows in its daily slot. One person drives Claude. **Tools:** the `grilling` and `domain-modeling` skills (the map's grilling ticket calls them), the fund documents in `fund-documents/`.

**Output.**
- `specs/00-fundeli5.feature`: what FundEli5 does, the demo story, the reading order, the tags, what is out of the demo.
- `specs/01-check-eligibility.feature`: one `Rule:` per rule kind the team keeps, each with its examples.
- `specs/99-answer-key.feature`: the coverage set, one row per case ([format](../../specs/README.md#the-shape-of-an-answer-key-row)).
- One plain-language sentence per rule kind and outcome, in English and French: the "explain it like I'm five" text under each Verdict.
- Rows in [hypotheses.md](../hypotheses.md) for every reading not yet confirmed, and the matching scenarios tagged `@assumed`.
- Build tickets, one per rule kind, from `/to-tickets`.

## Sitting 1: the story and the rules (90 min)

Start the map's ticket "Write the demo story and the answer key". Claude grills; the team answers.

1. **The story** (30 min). Who sends the request, about which client, for which fund, and what the dealer does with the answer? Aim for **three cases** the jury can follow in five minutes: one clear yes and no side by side, one "needs review" that shows the four promises at work, one refusal by the Privacy Gate. Write each as one paragraph.
2. **The funds** (15 min). Pick from the four seed funds (their PDFs are in `fund-documents/`, facts in [sample-funds.md](../research/sample-funds.md)) or from the bank's shelf. A new fund needs its public prospectus and KID downloaded into `fund-documents/` today, so the Rule Card pipeline can draft its card. DEV's document service serves mock PDFs, so it can't be used.
3. **The rules** (45 min). Which rules decide whether a client may subscribe, in Switzerland and Luxembourg? For each rule: its name, what it checks on the client, where the fund document states it (document and page), and what makes it pass, fail or need review. Each kept rule becomes a **rule kind**: one plug-in class in the code, one `Rule:` in `01-check-eligibility.feature`. Common ones: investor category, US Person, minimum subscription, mandate-only class, KID required for retail, Target Market, other restrictions. Keep only those the story needs, plus the ones a dealer would never skip.

## Sitting 2: the answer key and the Gherkin (60–90 min)

4. **The clients** (15 min). For each case, the client facts that matter: investor classification, mandate type, residence, nationality, US Person flags, risk profile, horizon. Start from the seed Client Profiles in [contracts/fixtures](../contracts/fixtures/README.md); change or add what the story needs. Use only the synthetic number range 900001–900099.
5. **The rows** (30 min). One row per case: Portfolio Reference, Share Class, amount and currency, the expected **outcome of every rule kind** (Pass, Fail, Review), and the Verdict. Write them **from the fund documents and the desk's practice, without the app**. Add rows until every rule kind fails at least once and passes at least once. 15 to 25 rows is a good size.
6. **The sentences** (15 min). For every rule kind and outcome, one sentence a relationship manager could forward to a client, with `{placeholders}` for the values: "{class} is for institutional investors; this portfolio is {classification}." English and French.
7. **The Gherkin** (15 min). Paste the prompt below. Claude writes the three feature files. Read **every line**: Claude writes the code's specification, and the team is answerable for it. Tag `@assumed` every row the desk has not confirmed.
8. **Compare with the reference** (15 min, last). Only now, open the reference build's answer key and rules: [fund-gate `specs/`](https://github.com/smnajid/fund-gate/tree/main/specs). Use it as a checklist of edge cases, not as an answer: a US citizen under Reg S, discretionary mandates counted as institutional (art. 174 of the 2010 Law), reverse solicitation, a fund named without a Share Class. For each edge case you missed, decide to add a row or leave it out, on purpose.

## The prompt for step 7

```
Write the team's executable specification in specs/, following specs/README.md and
GLOSSARY.md, from our notes below:
- specs/00-fundeli5.feature: what FundEli5 does in one paragraph, our demo story, the
  reading order, the tags, and what is not in the demo.
- specs/01-check-eligibility.feature: one Rule: per rule kind we kept, with the examples
  that prove it, each citing the fund document and page.
- specs/99-answer-key.feature: one Scenario Outline with one row per case, every rule
  kind's outcome as a column.
Tag @must the rows the demo shows and @assumed every row the desk has not confirmed,
with a sentence saying what is assumed. Use only the facts in our notes: when something
is missing, ask us instead of filling it in. Then add one row to docs/hypotheses.md per
@assumed reading. Show us each file before writing the next.

Our notes:
<paste the story, the rules, the client facts, the rows and the sentences>
```

Then, once the files are committed: `/to-tickets specs/01-check-eligibility.feature`, one build ticket per rule kind, using the build-ticket template of [build-workflow.md](../build-workflow.md), blocked by S4.

## Done when

- [ ] `specs/00`, `01` and `99` are committed, and every team member has read them.
- [ ] Every rule kind has at least one Pass and one Fail row in the answer key.
- [ ] Every row the desk has not confirmed is `@assumed` and has its line in `docs/hypotheses.md`.
- [ ] The sentences exist for every rule kind and outcome, in English and French.
- [ ] The comparison with the reference is done, and each missed edge case is a row or a recorded "left out".
- [ ] One build ticket per rule kind is published, and the builder knows S4 can start.

## Pitfalls

- **Writing the expected answer from what the app says.** The key is written first, from the documents. Otherwise it proves nothing.
- **Too many rule kinds.** Each one costs a plug-in, a prompt line for the pipeline and rows in the key. Keep what the story and the desk need.
- **Copying the reference.** The reference stays closed until step 8. The team's story beats it only if the team wrote it.
- **Real client data.** Never. Synthetic numbers, invented names, and the Privacy Gate's refusal case uses a made-up name.
