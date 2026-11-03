# specs/: the team's executable specification

This folder starts empty. The team writes it at the event ([task 3](../docs/tasks/03-write-the-demo-story-and-answer-key.md)), in Gherkin, in the words of [GLOSSARY.md](../GLOSSARY.md). Its scenarios are the definition of done for every content ticket ([build-workflow.md](../docs/build-workflow.md)). Agents never edit this folder; only the team does.

## Files

| File | Holds | Written in |
|---|---|---|
| `00-fundeli5.feature` | What FundEli5 does, in one paragraph; the demo story; the reading order; the tags; what is out of the demo | task 3 |
| `01-check-eligibility.feature` | One `Rule:` per rule kind the team keeps, with examples that prove it | task 3, then one rule kind per ticket |
| `02-answer-a-subscription-request.feature` | The demo emails, the Privacy Gate behaviour, the reply | task 3 (emails), then the tickets |
| `99-answer-key.feature` | One row per case the demo data must produce: portfolio, Share Class, amount, expected Verdict and the outcome of every rule | task 3 |

Add others as the map asks (explain a Verdict, validate a Rule Card, audit a check, prepare the subscription form).

## Tags

- Scope tier: `@must` or `@should`. A cut capability has no scenario.
- Unconfirmed reading: `@assumed`, with a sentence saying what is assumed and who confirms it. The desk's confirmation removes the tag; the demo avoids `@assumed` rows.
- The coverage set, rerun before every rehearsal: `@answer-key`.
- Live model: `@live-llm`. Every other scenario runs in replay mode.
- One tag per module: `@rule-engine @privacy-gate @request-parser @reply-drafter @share-class-catalog @rule-card-pipeline @validation @check-record @explanation`.

## The shape of an answer-key row

```gherkin
@answer-key @must
Scenario Outline: Answer key
  When <portfolio> asks to subscribe <amount> <currency> to <share class>
  Then the Verdict is <verdict>
  And the outcomes are investor category <ic>, US Person <us>, minimum <min>, …

  Examples:
    | row | portfolio   | share class | amount | currency | verdict      | ic   | us   | min  |
    | 1   | LOC90000101 | GCE-BI      | 80000  | EUR      | Not Eligible | Fail | Pass | Pass |
```

The columns are the team's rule kinds. Write the expected answers from the fund documents and the desk's practice, **before** looking at what the app returns.
