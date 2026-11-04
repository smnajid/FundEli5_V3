# The atlas: every document in one page

`index.html` is the whole repo's documentation as a single page you can open in a browser, with no server and no network. Open it directly:

```bash
open docs/atlas/index.html          # macOS
xdg-open docs/atlas/index.html      # Linux
```

It exists because the documents cross-reference each other heavily — 183 links over 62 files — and following one of them in an editor means leaving what you were reading. In the atlas every relative link is resolved into a jump inside the page, and each document shows **what points back at it**.

## What it gives you

| | |
|---|---|
| **Resolved links** | Every `[build-workflow.md](../build-workflow.md)` becomes an in-page jump, section anchors included. A link to a folder opens that folder's README |
| **Backlinks** | "Referenced by" on every document, with the words used to link to it. The rail shows each document's inbound count |
| **Search** | Full text over every document, `⌘K` or `/` |
| **The mockups, live** | `dealer.html` and `validation.html` embedded with all their states, in a shadow root so their styles and the page's stay apart |
| **The screens** | `docs/ux/README.md` renders its nine state screenshots inline |
| **One reference index** | Every link out of the repo, grouped by host, with the documents citing it — the reference build among them |
| **A link check** | A document that links to a file that does not exist is reported instead of failing silently |

Navigation: the **⌂ Atlas home** button on every page, the wordmark top-left, or the browser's Back. Each document has its own address (`#docs-tasks-03-…`, `#references`, `#mockup-dealer`), so you can send someone a link to one.

## Regenerating it

The page is generated from the real files, so it cannot drift from the repo — but it does not update itself. After changing any document:

```bash
python3 docs/atlas/build.py . docs/atlas ../ marked.min.js
```

The four arguments are the repo root, the output folder, the prefix the page uses to reach `docs/ux/` assets, and where it loads `marked` from. It needs Python 3 and nothing else; it writes only `index.html`.

The command prints the document count, the link and backlink totals, and **every unresolved link**. That makes it a cheap documentation check before a merge: if it reports a broken link, a document points at a file that is not there.

## What is vendored here

- `marked.min.js` — marked 12.0.2, MIT, the Markdown renderer, kept next to the page so the atlas works with no internet access. This matters inside the bank, where cdnjs is not reachable.
- Fonts come from Google Fonts when there is a network and fall back to the system stack when there is not. Nothing else is fetched.

Links to files the page cannot show — the PDFs in `fund-documents/`, the fixture JSON — appear as a dashed path chip rather than a dead link. Open those from the repo.
