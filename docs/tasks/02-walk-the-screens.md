# Task 2: Walk the screens

**Why.** The screens are what the jury sees and what the desk would use. The last build got working screens nobody wanted to look at, because the people who know the desk's work saw them only at the end. This task puts the business in front of the screens **before** any screen code exists. A change now costs an edit to a mockup; a change after the build costs a ticket.

**Time box.** 45 minutes. **Who:** the business members, and a desk adviser if one is free. One person drives Claude; the others react. **Tool:** a browser, Claude Code with the `prototype` skill.

**Output.**
- The decisions of the session at the end of [ux/README.md](../ux/README.md#what-the-team-decides-task-2), one line each.
- The mockups in `docs/ux/mockups/` changed to match, and their screenshots in `docs/ux/screens/` taken again.
- A wording table, `docs/ux/wording.md`: every fixed text on screen (titles, buttons, banners, empty and error states) in English and French.

## Steps

1. **Open the mockups** (2 min). Open [`dealer.html`](../ux/mockups/dealer.html) in a browser, full screen on the shared display. The switcher in the bottom-left corner walks through the states.
2. **Play the dealer** (15 min). One person reads a request email aloud, the way a relationship manager would send it. Walk the states in order: Paste → Working → Answered → Needs review → Privacy Gate → Check Record. At each state, answer the questions below and say them aloud; the driver writes them down in the Claude session.
3. **Play the validator** (10 min). Open [`validation.html`](../ux/mockups/validation.html). Walk Queue → Draft card → Validated, asking the same questions.
4. **Decide the open points** (10 min). Go through the list in [What the team decides](../ux/README.md#what-the-team-decides-task-2): Advisory Suggestions in or out, where the organisers' capabilities go (form guidance, deadlines, eligibility questions), and anything the walk-through raised. One decision per line.
5. **Apply** (8 min, the driver with Claude). Paste the prompt below. Claude updates the mockups, `ux/README.md` and `wording.md`, and takes the screenshots again. Look at the new screenshots together before closing.

### Questions at each state

- **Would a dealer trust this?** What is missing before they would send the reply?
- **Is the first thing you read the right thing?** What do you read first, second, third?
- **Is any word wrong?** Desk words, not IT words. Is it the word the relationship manager uses?
- **What would you click next?** If the answer differs between people, the screen is unclear.
- **What would the jury remember?** If nothing, what should change?

## The prompt

Paste in Claude Code at the repo root after the walk-through, with the notes taken during it:

```
/prototype

We walked the FundEli5 mockups (docs/ux/mockups/dealer.html and validation.html) with the
business. Apply our decisions below to the mockups, docs/ux/README.md (record each
decision as one line under "What the team decides") and a new docs/ux/wording.md (every
fixed text on screen, English and French). Keep the design tokens and the components of
docs/ux/design-system.md; add a state to a mockup if a decision needs one. Then take a
1440 x 900 screenshot of every state with the Playwright tool and replace the files in
docs/ux/screens/. Show us the changed screenshots. Ask before inventing any wording
we did not give you.

Our notes:
<paste the notes here>
```

## Done when

- [ ] Every state of both mockups was walked with the questions above.
- [ ] Each decision is one line in `docs/ux/README.md`, and the open points listed there are settled.
- [ ] The mockups and screenshots show the decisions, and the team looked at the new screenshots.
- [ ] `docs/ux/wording.md` exists, in English and French.
- [ ] The ticket "Walk the screens" is closed with a link to the commit.

## Pitfalls

- **Redesigning the colours.** The design system is fixed: green, red and amber mean Verdicts, purple means AI. Change what the screens say and show, not the palette.
- **Adding features.** A new capability is a ticket on the map, not a box added to a mockup during the session. Add it to the mockup only once the map has it in the Must tier.
- **Wording for the Verdict sentences.** The sentence under each Verdict ("BI-EUR is for institutional investors…") depends on the rule kinds, so it is written in task 3, not here.
