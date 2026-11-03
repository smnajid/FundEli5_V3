# Working hypotheses

A business question the build needs answered before the team or the desk can answer it gets a **working hypothesis** here, so the build can go on and the change later is cheap. The team owns this file; agents never edit it ([build-workflow.md](build-workflow.md), rule 2).

## How to add one

1. An agent stops on a missing business answer and says what it needs.
2. The team writes the row below: the question, the working choice, and the `@assumed` scenario that encodes it.
3. The ticket restarts.

## How to change one

1. Record the answer (from the desk or the team) on the question's ticket and close it.
2. Edit the scenarios listed under **Encoded in**: remove `@assumed` from a confirmed one, change the example of a corrected one.
3. Run the module's tag. The failing scenarios show the code to change.
4. Strike the row here.

A hypothesis written only in this file, with no scenario, is hidden from the build.

## Business hypotheses

| Question | Working choice | Encoded in | Confirmed by |
|---|---|---|---|

## Technical choices taken while the business answers wait

| Question | Working choice | Encoded in |
|---|---|---|
| What does the validation screen show instead of the extractor's self-rated confidence? | Only signals the code checks: quote found on its page, a value with no supporting quote, a contradiction between documents. The confidence stays in the Draft card, off screen | [ux/README.md](ux/README.md#rule-card-validation-screen-the-document-beside-the-rules) |
