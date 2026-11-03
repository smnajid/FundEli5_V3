# Design system

The few parts both screens are built from. Tokens live in [tokens.css](tokens.css), which the skeleton copies into `frontend/src/styles.css`. The reference look of each component is in [mockups/components.css](mockups/components.css) and the [screenshots](screens/). Build each component once in `frontend/src/app/ui/` and compose screens from them.

## Tokens

| Group | Tokens | Use |
|---|---|---|
| Brand | `--brand-900` … `--brand-50` | top bar (900), primary buttons (700), links, citation markers, selection (50/100) |
| Ink and surfaces | `--ink-900/700/500/400`, `--line`, `--surface`, `--ground`, `--sunken` | text in three strengths; white cards on a light grey ground; sunken insets for quotes and code |
| Verdict | `--eligible-*`, `--not-eligible-*`, `--review-*` (700 text, 600 solid, 100 chip, 50 banner) | **only** Verdicts, rule outcomes and their banners. Never decoration |
| AI | `--ai-*` | everything an LLM wrote: the reply, Advisory Suggestions, their labels |
| Evidence | `--quote-bg`, `--quote-line` | the highlighted passage, on the rail and on the document page |
| Type | `--font-sans` (Inter), `--font-mono` (JetBrains Mono), `--text-xs` 12 … `--text-2xl` 24 | body is `--text-md` 15 px; Verdict headlines `--text-lg`; Portfolio References and ISINs in mono |
| Space | `--space-1` 4 px … `--space-10` 40 px | cards pad `--space-5`/`--space-6`; gaps between cards `--space-4` |
| Shape | `--radius-sm/md/lg/pill`, `--shadow-card/raised/drawer` | cards `--radius-lg` and `--shadow-card`; the selected evidence card `--shadow-raised` |
| Layout | `--topbar-height` 56, `--page-max` 1320, `--rail-width` 380 | the page grid of both screens |

Colour carries meaning, so it must not be the only carrier: every Verdict chip also has an icon (✓ ✕ !) and a word.

## Components

| Component | What it shows | Inputs | States |
|---|---|---|---|
| `app-shell` | Top bar: wordmark, the two screens as tabs (validation shows the count of Draft cards), role and name | current route, role | — |
| `status-chip` | A Verdict or a status as icon + word | kind: eligible, not-eligible, review, ai, neutral, safe; label | — |
| `verdict-line` | One check: chip, headline sentence, reason with citation markers, metadata, **Why?** | check view (from the API), alternative flag | folded, unfolded (rule outcomes) |
| `citation-marker` | `[n]` linking to an evidence card | number | normal, highlighted (hover or focus on either side) |
| `evidence-card` | Rule kind, outcome, Share Class, quote, document title and page, "quote found on page" | citation view | normal, highlighted |
| `reply-card` | The drafted reply: AI label, language, editable text, Copy reply, footer | reply view | waiting for suggestions, drafting, drafted, edited, copied |
| `suggestion-list` | Advisory Suggestions in two groups, Accept / Dismiss with note | suggestions | undecided, accepted, dismissed |
| `banner` | A message with an icon, title and body | tone: danger, warning, success, ai, neutral | — |
| `progress-steps` | The steps of a running check, ticking as they finish | steps with status and note | — |
| `drawer` | A right-hand panel over a scrim, focus trapped, Esc closes | title, open | open, closed |
| `empty-state` | Title, one sentence, the main action | — | — |
| `rule-list` | Rules grouped by scope, with status, label, value, pages | rules, selection | per row: open, accepted, corrected, contradiction |
| `document-page` | Page text with running head and highlighted quotes, tabs per Citation | pages, quotes | loading, page text, page missing |
| `decision-panel` | The selected rule's value, summary, signals, decision controls | rule, its signals | open, contradiction, unmodelled, decided |

## Words on screen

- **One label map.** `ui/labels.ts` turns every API enum into words, in English and French: rule kinds (`INVESTOR_CATEGORY` → "Investor category"), outcomes (`FAIL` → "FAIL" on the rail, "failed" in counts), Verdicts (`NOT_ELIGIBLE` → "Not eligible" / "cannot buy"), condition values (`reg_s` → "Reg S definition", `full_loss` → "possible total loss"). An enum missing from the map fails a unit test; it never falls through to the screen.
- **One date formatter.** "today 09:42" for today, "1 Nov 2026, 14:10" otherwise. Never ISO strings.
- **Documents by title.** "Nordea 1 prospectus · p.123", "BI-EUR KID · p.1"; the document id stays in the data.
- **Share Classes by name, then ISIN.** "Nordea 1 Global Climate BI-EUR" in sentences, the ISIN in the metadata line.
- **Counts, not lists, when something is missing.** "5 rules and 2 contradictions left", not one line per rule.
- **Errors say what to do.** "Could not reach the rules service. Your email is still here: try Answer it again." Never an internal id or a stack trace.
- **Product words come from [GLOSSARY.md](../../GLOSSARY.md)**: Verdict, Needs Review, Rule Card, Portfolio Reference, Privacy Gate. Buttons are verbs: Answer it, Copy reply, Draft reply, Accept and next, Validate card.

## Motion and feedback

- 160 ms transitions on hover and highlight only (`--motion`); none when the user prefers reduced motion.
- A toast confirms copy actions; a banner confirms a validation.
- A busy button keeps its width and shows a spinner; the rest of the screen stays readable.
