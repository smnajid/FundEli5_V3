#!/usr/bin/env python3
"""Generate a single-page HTML reader for the FundEli5 decision repo.

Reads the real Markdown files, resolves every relative link into in-page
navigation, builds the backlink graph and the external-reference index,
and emits index.html plus the list of assets to publish alongside it.
"""
import json
import os
import re
import sys
from pathlib import Path

REPO = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]).resolve()
OUT.mkdir(parents=True, exist_ok=True)

# Where the page finds the screenshots, and where it finds marked.js.
#   published artifact : assets sit beside the page        -> prefix ""
#   copy in docs/atlas : assets stay in docs/ux            -> prefix "../"
#   offline copy       : marked.js vendored next to it, so the page needs no network
PREFIX = sys.argv[3] if len(sys.argv) > 3 else ""
MARKED = sys.argv[4] if len(sys.argv) > 4 else \
    "https://cdnjs.cloudflare.com/ajax/libs/marked/12.0.2/marked.min.js"

# ---------------------------------------------------------------- collect docs

def md_files():
    seen = []
    for name in ("README.md", "CLAUDE.md", "GLOSSARY.md"):
        if (REPO / name).exists():
            seen.append(name)
    for base in ("docs", "specs", ".claude"):
        for p in sorted((REPO / base).rglob("*.md")):
            seen.append(str(p.relative_to(REPO)))
    return seen

GROUPS = [
    ("start", "Start here"),
    ("vocab", "Vocabulary"),
    ("adr", "Decisions · ADR"),
    ("build", "Architecture & build"),
    ("tasks", "The team's tasks"),
    ("ux", "Screens"),
    ("contracts", "Data contracts"),
    ("specs", "Specification"),
    ("research", "Research & reference"),
    ("agents", "Agent setup"),
    ("gates", "Gate agents"),
    ("skills", "Skills"),
]

def group_of(path):
    if path in ("README.md", "CLAUDE.md", "docs/agents/setup.md"):
        return "start"
    if path.startswith("docs/atlas/"):
        return "start"
    if path in ("GLOSSARY.md", "docs/agents/domain.md"):
        return "vocab"
    if path.startswith("docs/adr/"):
        return "adr"
    if path in ("docs/architecture.md", "docs/tech-choices.md",
                "docs/build-workflow.md", "docs/hypotheses.md"):
        return "build"
    if path.startswith("docs/tasks/"):
        return "tasks"
    if path.startswith("docs/ux/"):
        return "ux"
    if path.startswith("docs/contracts/"):
        return "contracts"
    if path.startswith("specs/"):
        return "specs"
    if path.startswith("docs/research/") or path.startswith("docs/reference/"):
        return "research"
    if path.startswith("docs/agents/"):
        return "agents"
    if path.startswith(".claude/agents/"):
        return "gates"
    if path.startswith(".claude/skills/"):
        return "skills"
    return "research"

def slug(path):
    s = re.sub(r"[^a-z0-9]+", "-", path.lower().replace(".md", ""))
    return re.sub(r"^-+|-+$", "", s)

def title_of(path, text):
    m = re.search(r"^#\s+(.+?)\s*$", text, re.M)
    t = m.group(1) if m else Path(path).stem
    return re.sub(r"[`*]", "", t)

def short_label(path, title):
    """A compact sidebar label."""
    name = Path(path).name
    if path.startswith("docs/adr/"):
        num = name.split("-")[0]
        rest = re.sub(r"^ADR\s*\d+[:.\s-]*", "", title, flags=re.I)
        return f"{num} · {rest}"
    if path.startswith("docs/tasks/") and name != "README.md":
        return re.sub(r"^Task\s*(\d+):\s*", r"\1. ", title)
    if path.startswith(".claude/skills/"):
        parts = path.split("/")
        extra = "" if name == "SKILL.md" else f" · {Path(name).stem}"
        return f"/{parts[2]}{extra}"
    if path.startswith(".claude/agents/"):
        return Path(name).stem
    return title

docs = {}
order = []
for path in md_files():
    text = (REPO / path).read_text(encoding="utf-8")
    t = title_of(path, text)
    docs[path] = {
        "path": path,
        "slug": slug(path),
        "title": t,
        "label": short_label(path, t),
        "group": group_of(path),
        "body": text,
        "bytes": len(text.encode("utf-8")),
    }
    order.append(path)

# ------------------------------------------------------------- publish assets

ASSET_MAP = {}
for src, dest in [("docs/ux/tokens.css", "ux/tokens.css"),
                  ("docs/ux/mockups/components.css", "ux/mockups/components.css"),
                  ("docs/ux/mockups/dealer.html", "ux/mockups/dealer.html"),
                  ("docs/ux/mockups/validation.html", "ux/mockups/validation.html")]:
    if (REPO / src).exists():
        ASSET_MAP[src] = dest
for p in sorted((REPO / "docs/ux/screens").glob("*.png")):
    ASSET_MAP[f"docs/ux/screens/{p.name}"] = f"ux/screens/{p.name}"
for p in sorted((REPO / "docs/ux/v2-lessons").glob("*.png")):
    ASSET_MAP[f"docs/ux/v2-lessons/{p.name}"] = f"ux/v2-lessons/{p.name}"

# ----------------------------------------------------------------- mockups
# The mockups are embedded in a shadow root rather than linked: a sandboxed
# artifact cannot navigate to a relative published file, and their own state
# switcher reads location.hash, which the atlas needs for its routing.

def scope_css(text, drop_import):
    if drop_import:
        text = re.sub(r"@import\s+url\([^)]*\);\s*", "", text)
    # :root never matches inside a shadow root, and the mockup's html/body
    # rules have to land on the host element instead.
    text = re.sub(r":root(?=\s*[,{])", ":host", text)
    text = re.sub(r"(?m)^html,\s*\n\s*body\s*\{", ":host {", text)
    return text

MOCK_CSS = ""
for rel, drop in (("docs/ux/tokens.css", True), ("docs/ux/mockups/components.css", False)):
    if (REPO / rel).exists():
        MOCK_CSS += scope_css((REPO / rel).read_text(encoding="utf-8"), drop) + "\n"
if re.search(r"(?m)^body\s*[,{]", MOCK_CSS):
    print("warning: a bare `body` selector survived scoping", file=sys.stderr)

MOCKUPS = {}
for key, fname in (("dealer", "dealer.html"), ("validation", "validation.html")):
    src = REPO / "docs/ux/mockups" / fname
    if not src.exists():
        continue
    raw = src.read_text(encoding="utf-8")
    body = re.search(r"<body>(.*)</body>", raw, re.S).group(1)
    states = []
    nav = re.search(r'<nav class="mock-switch".*?</nav>', body, re.S)
    if nav:
        for sid, label in re.findall(r'<a href="#([^"]+)">([^<]+)</a>', nav.group(0)):
            states.append({"id": sid, "label": label})
        body = body.replace(nav.group(0), "")
    body = re.sub(r"<script\b.*?</script>", "", body, flags=re.S)
    t = re.search(r"<title>(.*?)</title>", raw, re.S)
    MOCKUPS[key] = {
        "key": key,
        "file": f"docs/ux/mockups/{fname}",
        "title": (t.group(1) if t else fname).replace("FundEli5 · ", ""),
        "states": states,
        "default": states[0]["id"] if states else "",
        "html": body.strip(),
    }

MOCKUP_FILES = {f"docs/ux/mockups/{n}.html": n for n in MOCKUPS}

# ----------------------------------------------------------------- link graph

LINK_RE = re.compile(r"(!?)\[([^\]\[]*(?:\[[^\]]*\][^\]\[]*)*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")

links = {}        # doc -> {raw href -> resolution}
backlinks = {}    # doc -> [{from, label}]
external = {}     # url -> [{doc, label}]
broken = []

for path, d in docs.items():
    here = {}
    base = os.path.dirname(path)
    for bang, label, target in LINK_RE.findall(d["body"]):
        if target in here:
            continue
        label_txt = re.sub(r"[`*]", "", label).strip()
        if target.startswith(("http://", "https://")):
            here[target] = {"kind": "external", "href": target}
            external.setdefault(target, []).append({"doc": path, "label": label_txt})
            continue
        if target.startswith("mailto:"):
            here[target] = {"kind": "external", "href": target}
            continue
        if target.startswith("#"):
            here[target] = {"kind": "anchor", "anchor": target[1:]}
            continue
        raw, _, anchor = target.partition("#")
        resolved = os.path.normpath(os.path.join(base, raw)) if base else os.path.normpath(raw)
        resolved = resolved.replace(os.sep, "/")
        # a link to a directory means its README
        if resolved in docs:
            hit = resolved
        elif f"{resolved}/README.md" in docs:
            hit = f"{resolved}/README.md"
        elif resolved.rstrip("/") + "/README.md" in docs:
            hit = resolved.rstrip("/") + "/README.md"
        else:
            hit = None
        if hit:
            here[target] = {"kind": "doc", "doc": hit, "anchor": anchor}
            if not bang:
                backlinks.setdefault(hit, []).append({"doc": path, "label": label_txt})
            continue
        if resolved in MOCKUP_FILES:
            here[target] = {"kind": "mockup", "which": MOCKUP_FILES[resolved],
                            "anchor": anchor, "path": resolved}
            continue
        if resolved in ASSET_MAP:
            here[target] = {"kind": "asset", "href": PREFIX + ASSET_MAP[resolved],
                            "path": resolved, "anchor": anchor,
                            "image": bool(bang) or resolved.endswith(".png")}
            continue
        if (REPO / resolved).exists():
            here[target] = {"kind": "file", "path": resolved}
            continue
        here[target] = {"kind": "broken", "path": resolved}
        # .claude/skills/ holds vendored skill templates whose example paths
        # (./src/ordering/GLOSSARY.md and the like) are illustrative, not links.
        if not path.startswith(".claude/"):
            broken.append({"doc": path, "target": target, "resolved": resolved, "label": label_txt})
    links[path] = here

# de-duplicate backlinks per source document
for k, v in backlinks.items():
    seen, out = set(), []
    for b in v:
        if b["doc"] in seen:
            continue
        seen.add(b["doc"])
        out.append(b)
    backlinks[k] = out

ext_index = []
for url, uses in sorted(external.items(), key=lambda kv: (-len(kv[1]), kv[0])):
    host = re.sub(r"^https?://([^/]+).*", r"\1", url)
    seen, cites = set(), []
    for u in uses:
        if u["doc"] in seen:
            continue
        seen.add(u["doc"])
        cites.append(u)
    ext_index.append({"url": url, "host": host, "cites": cites})

payload = {
    "groups": GROUPS,
    "docs": [docs[p] for p in order],
    "links": links,
    "backlinks": backlinks,
    "external": ext_index,
    "broken": broken,
    "mockups": MOCKUPS,
    "mockupCss": MOCK_CSS,
    "stats": {
        "docs": len(docs),
        "bytes": sum(d["bytes"] for d in docs.values()),
        "links": sum(len(v) for v in links.values()),
        "external": len(ext_index),
        "adrs": sum(1 for p in docs if p.startswith("docs/adr/")),
    },
}

data = json.dumps(payload, ensure_ascii=False).replace("<", "\\u003c")

# ------------------------------------------------------------------- the page

HTML = r"""<title>FundEli5 Decision Atlas</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap">
<style>
/* Layout: fixed left rail of grouped documents, scrolling reader, right rail of
   outline + backlinks. Palette and type come from docs/ux/tokens.css. */
:root{
  --brand-900:#0f2440; --brand-800:#163257; --brand-700:#1f4373; --brand-600:#2b5a95;
  --brand-100:#e6eef8; --brand-50:#f3f7fc;
  --ink-900:#111827; --ink-700:#374151; --ink-500:#6b7280; --ink-400:#9ca3af;
  --line:#e5e7eb; --line-strong:#d1d5db;
  --surface:#ffffff; --ground:#f4f6f9; --sunken:#f9fafb;
  --eligible-700:#166534; --eligible-100:#dcfce7;
  --not-eligible-700:#991b1b; --not-eligible-100:#fee2e2;
  --review-700:#92400e; --review-100:#fef3c7;
  --ai-700:#5b21b6; --ai-100:#ede9fe;
  --quote-bg:#fef9c3; --quote-line:#eab308;
  --font-sans:"Inter",system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
  --font-mono:"JetBrains Mono",ui-monospace,"SF Mono",Menlo,monospace;
  --radius-sm:6px; --radius-md:10px; --radius-lg:14px; --radius-pill:999px;
  --shadow-card:0 1px 2px rgba(16,24,40,.05),0 1px 3px rgba(16,24,40,.06);
  --focus-ring:0 0 0 3px rgba(43,90,149,.35);
  --rail:252px; --outline:208px;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --brand-900:#cfe0f5; --brand-800:#b9d2ef; --brand-700:#8fb6e2; --brand-600:#7aa8dc;
  --brand-100:#1b2b43; --brand-50:#16202f;
  --ink-900:#e8edf4; --ink-700:#bcc6d4; --ink-500:#8b97a8; --ink-400:#6b7686;
  --line:#26303d; --line-strong:#36424f;
  --surface:#131a23; --ground:#0d1218; --sunken:#1a222c;
  --eligible-700:#86efac; --eligible-100:#14321f;
  --not-eligible-700:#fca5a5; --not-eligible-100:#3a1a1a;
  --review-700:#fcd34d; --review-100:#3a2a10;
  --ai-700:#c4b5fd; --ai-100:#2a1f45;
  --quote-bg:#33300f; --quote-line:#a1860f;
  --shadow-card:0 1px 2px rgba(0,0,0,.4),0 1px 3px rgba(0,0,0,.3);
  --focus-ring:0 0 0 3px rgba(122,168,220,.4);
  color-scheme:dark;
}}
:root[data-theme="dark"]{
  --brand-900:#cfe0f5; --brand-800:#b9d2ef; --brand-700:#8fb6e2; --brand-600:#7aa8dc;
  --brand-100:#1b2b43; --brand-50:#16202f;
  --ink-900:#e8edf4; --ink-700:#bcc6d4; --ink-500:#8b97a8; --ink-400:#6b7686;
  --line:#26303d; --line-strong:#36424f;
  --surface:#131a23; --ground:#0d1218; --sunken:#1a222c;
  --eligible-700:#86efac; --eligible-100:#14321f;
  --not-eligible-700:#fca5a5; --not-eligible-100:#3a1a1a;
  --review-700:#fcd34d; --review-100:#3a2a10;
  --ai-700:#c4b5fd; --ai-100:#2a1f45;
  --quote-bg:#33300f; --quote-line:#a1860f;
  --shadow-card:0 1px 2px rgba(0,0,0,.4),0 1px 3px rgba(0,0,0,.3);
  --focus-ring:0 0 0 3px rgba(122,168,220,.4);
  color-scheme:dark;
}
*,*::before,*::after{box-sizing:border-box}
body{margin:0;background:var(--ground);color:var(--ink-900);font-family:var(--font-sans);
  font-size:15px;line-height:1.55;-webkit-font-smoothing:antialiased}
:focus-visible{outline:none;box-shadow:var(--focus-ring)}
@media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}

/* top bar */
#top{position:sticky;top:env(safe-area-inset-top,0px);z-index:20;background:var(--brand-900);
  color:#fff;border-bottom:1px solid var(--line)}
:root[data-theme="dark"] #top,
:root:not([data-theme="light"]) #top{color:var(--ink-900)}
@media (prefers-color-scheme:light){:root:not([data-theme="dark"]) #top{color:#fff}}
:root[data-theme="light"] #top{color:#fff}
body::before{content:"";position:fixed;inset:0 0 auto;height:env(safe-area-inset-top,0px);
  z-index:21;background:var(--brand-900)}
.topin{display:flex;align-items:center;gap:12px;min-height:52px;
  padding-left:max(16px,env(safe-area-inset-left,0px));
  padding-right:max(16px,env(safe-area-inset-right,0px))}
.mark{display:flex;align-items:center;gap:8px;font-weight:700;letter-spacing:-.01em;
  background:none;border:0;color:inherit;font-family:inherit;font-size:15px;cursor:pointer;padding:0}
.logo{display:grid;place-items:center;width:24px;height:24px;border-radius:var(--radius-sm);
  background:var(--brand-600);color:#fff;font-size:11px;font-weight:700}
:root[data-theme="dark"] .logo,:root:not([data-theme="light"]) .logo{color:#0d1218}
@media (prefers-color-scheme:light){:root:not([data-theme="dark"]) .logo{color:#fff}}
.mark .sub{font-weight:500;opacity:.62;font-size:13px}
.mark:hover{opacity:.82}
.mark:hover .sub{text-decoration:underline;text-underline-offset:2px}
#search{flex:1;min-width:0;max-width:420px;margin-left:auto;font:inherit;font-size:13px;
  padding:7px 11px;border-radius:var(--radius-pill);border:1px solid rgba(255,255,255,.18);
  background:rgba(255,255,255,.10);color:inherit}
#search::placeholder{color:rgba(255,255,255,.55)}
:root[data-theme="dark"] #search::placeholder,
:root:not([data-theme="light"]) #search::placeholder{color:var(--ink-500)}
@media (prefers-color-scheme:light){:root:not([data-theme="dark"]) #search::placeholder{color:rgba(255,255,255,.55)}}
.iconbtn{background:rgba(255,255,255,.10);border:1px solid rgba(255,255,255,.18);color:inherit;
  width:30px;height:30px;border-radius:var(--radius-sm);cursor:pointer;display:grid;place-items:center;
  font-size:13px;flex:none}
#menu{display:none}

/* shell */
#shell{display:grid;grid-template-columns:var(--rail) minmax(0,1fr) var(--outline);gap:22px;
  max-width:1360px;margin:0 auto;
  padding-left:max(16px,env(safe-area-inset-left,0px));
  padding-right:max(16px,env(safe-area-inset-right,0px));
  padding-block:20px 56px;align-items:start}

/* left rail */
#rail{position:sticky;top:calc(env(safe-area-inset-top,0px) + 68px);
  max-height:calc(100vh - 96px);overflow-y:auto;overscroll-behavior:contain;
  background:var(--surface);border:1px solid var(--line);border-radius:var(--radius-lg);
  box-shadow:var(--shadow-card);padding:10px;min-width:0}
#filter{width:100%;font:inherit;font-size:12.5px;padding:6px 9px;margin-bottom:8px;
  border:1px solid var(--line);border-radius:var(--radius-sm);background:var(--sunken);color:inherit}
.gp{margin-bottom:10px}
.gph{font-size:10.5px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;
  color:var(--ink-500);padding:4px 8px}
.rail-a{display:flex;gap:7px;align-items:baseline;width:100%;text-align:left;background:none;border:0;
  font:inherit;font-size:12.8px;color:var(--ink-700);padding:5px 8px;border-radius:var(--radius-sm);
  cursor:pointer;line-height:1.35}
.rail-a:hover{background:var(--brand-50);color:var(--brand-700)}
.rail-a[aria-current="true"]{background:var(--brand-100);color:var(--brand-800);font-weight:600}
.rail-a .n{color:var(--ink-400);font-size:11px;font-variant-numeric:tabular-nums;flex:none}

/* reader */
#main{min-width:0;background:var(--surface);border:1px solid var(--line);
  border-radius:var(--radius-lg);box-shadow:var(--shadow-card);padding:26px 30px 34px;min-height:70vh}
.crumb{display:flex;align-items:center;gap:8px;flex-wrap:wrap;font-size:11.5px;color:var(--ink-500);
  font-family:var(--font-mono);margin-bottom:14px}
.crumb .tag{background:var(--sunken);border:1px solid var(--line);border-radius:var(--radius-pill);
  padding:2px 9px}
.crumb .homeb{font:inherit;font-family:var(--font-mono);font-size:11.5px;cursor:pointer;
  background:var(--brand-50);border:1px solid var(--brand-600);color:var(--brand-700);
  border-radius:var(--radius-pill);padding:2px 11px}
.crumb .homeb:hover{background:var(--brand-100);color:var(--brand-800)}
.md{min-width:0}
.md h1{font-size:25px;line-height:1.25;letter-spacing:-.02em;margin:0 0 14px;text-wrap:balance}
.md h2{font-size:18px;margin:30px 0 10px;padding-bottom:6px;border-bottom:1px solid var(--line);
  letter-spacing:-.01em;text-wrap:balance;scroll-margin-top:110px}
.md h3{font-size:15.5px;margin:22px 0 7px;color:var(--brand-800);scroll-margin-top:110px}
.md h4{font-size:14px;margin:18px 0 6px;color:var(--ink-700);scroll-margin-top:110px}
.md p,.md li{font-size:14.6px}
.md p{margin:0 0 12px}
.md ul,.md ol{margin:0 0 12px;padding-left:22px}
.md li{margin-bottom:5px}
.md li>p{margin:0 0 6px}
.md strong{font-weight:600;color:var(--ink-900)}
.md hr{border:0;border-top:1px solid var(--line);margin:24px 0}
.md blockquote{margin:0 0 14px;padding:10px 14px;background:var(--quote-bg);
  border-left:3px solid var(--quote-line);border-radius:0 var(--radius-sm) var(--radius-sm) 0;color:var(--ink-900)}
.md blockquote p:last-child{margin:0}
.md code{font-family:var(--font-mono);font-size:.88em;background:var(--sunken);
  border:1px solid var(--line);border-radius:4px;padding:1px 5px}
.md pre{margin:0 0 14px;background:var(--sunken);border:1px solid var(--line);
  border-radius:var(--radius-md);padding:13px 15px;overflow-x:auto}
.md pre code{background:none;border:0;padding:0;font-size:12.3px;line-height:1.5;white-space:pre}
.scroller{overflow-x:auto;margin:0 0 16px;border:1px solid var(--line);border-radius:var(--radius-md)}
.md table{border-collapse:collapse;width:100%;font-size:13.2px}
.md th,.md td{text-align:left;vertical-align:top;padding:8px 11px;border-bottom:1px solid var(--line)}
.md th{background:var(--sunken);font-size:11px;letter-spacing:.05em;text-transform:uppercase;
  color:var(--ink-500);font-weight:700;white-space:nowrap}
.md tr:last-child td{border-bottom:0}
.md td code{white-space:nowrap}
.md img{max-width:100%;height:auto;border:1px solid var(--line);border-radius:var(--radius-md);display:block}
.md a{color:var(--brand-700);text-decoration-color:var(--line-strong);text-underline-offset:2px}
.md a:hover{color:var(--brand-600)}
.md a.doc{cursor:pointer}
.md a.ext::after{content:"\2197";font-size:.8em;margin-left:2px;color:var(--ink-400)}
.md .filechip{font-family:var(--font-mono);font-size:12px;background:var(--sunken);
  border:1px dashed var(--line-strong);border-radius:var(--radius-sm);padding:1px 6px;color:var(--ink-500)}
.md input[type="checkbox"]{margin-right:6px}

/* right rail */
#aside{position:sticky;top:calc(env(safe-area-inset-top,0px) + 68px);
  max-height:calc(100vh - 96px);overflow-y:auto;overscroll-behavior:contain;min-width:0;
  display:flex;flex-direction:column;gap:16px}
.asec h4{font-size:10.5px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;
  color:var(--ink-500);margin:0 0 7px}
.toc-a,.back-a{display:block;width:100%;text-align:left;background:none;border:0;font:inherit;
  font-size:12.2px;color:var(--ink-700);padding:3px 0 3px 9px;border-left:2px solid var(--line);
  cursor:pointer;line-height:1.4}
.toc-a:hover,.back-a:hover{color:var(--brand-700);border-left-color:var(--brand-600)}
.toc-a.h3{padding-left:19px;font-size:11.6px;color:var(--ink-500)}
.back-a{border-left:0;padding-left:0;border-bottom:1px solid var(--line);padding-block:5px}
.back-a:last-child{border-bottom:0}
.back-a .bp{display:block;font-family:var(--font-mono);font-size:10.5px;color:var(--ink-400)}
.empty{font-size:12px;color:var(--ink-400);font-style:italic}

/* home */
.hero{margin-bottom:22px}
.hero h1{font-size:28px;letter-spacing:-.025em;margin:0 0 8px;text-wrap:balance}
.hero p{font-size:15.4px;color:var(--ink-700);margin:0;max-width:66ch}
.stats{display:flex;flex-wrap:wrap;gap:8px;margin:18px 0 26px}
.stat{background:var(--sunken);border:1px solid var(--line);border-radius:var(--radius-pill);
  padding:4px 12px;font-size:12px;color:var(--ink-700)}
.stat b{font-variant-numeric:tabular-nums;color:var(--ink-900)}
.flow{display:grid;gap:10px;margin:0 0 8px}
.flowrow{display:grid;grid-template-columns:86px minmax(0,1fr);gap:12px;align-items:start}
.flowlab{font-size:10.5px;font-weight:700;letter-spacing:.07em;text-transform:uppercase;
  color:var(--ink-500);padding-top:9px}
.chips{display:flex;flex-wrap:wrap;gap:7px}
.chip{background:var(--surface);border:1px solid var(--line-strong);border-radius:var(--radius-sm);
  padding:6px 11px;font-size:12.6px;color:var(--ink-700);cursor:pointer;font:inherit;font-size:12.6px;
  text-align:left;line-height:1.3}
.chip:hover{border-color:var(--brand-600);color:var(--brand-700);background:var(--brand-50)}
.chip.k{border-color:var(--brand-600);background:var(--brand-50);color:var(--brand-800);font-weight:600}
.chip.gate{border-color:var(--eligible-700);background:var(--eligible-100);color:var(--eligible-700)}
.chip.done{border-color:var(--review-700);background:var(--review-100);color:var(--review-700)}
.arrowrow{font-size:11px;color:var(--ink-400);padding-left:98px;letter-spacing:.2em}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(215px,1fr));gap:12px;margin:8px 0 0}
.card{background:var(--sunken);border:1px solid var(--line);border-radius:var(--radius-md);
  padding:13px 15px;text-align:left;cursor:pointer;font:inherit}
.card:hover{border-color:var(--brand-600);background:var(--brand-50)}
.card b{display:block;font-size:13.6px;margin-bottom:3px;color:var(--ink-900)}
.card span{font-size:12.2px;color:var(--ink-500);display:block}
.promise{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:10px}
.pr{background:var(--surface);border:1px solid var(--line);border-left:3px solid var(--brand-600);
  border-radius:var(--radius-sm);padding:11px 13px;text-align:left;cursor:pointer;font:inherit}
.pr:hover{background:var(--brand-50);border-color:var(--brand-600)}
.pr b{display:block;font-size:12.8px;margin-bottom:2px}
.pr span{font-size:11.8px;color:var(--ink-500);font-family:var(--font-mono)}

/* embedded mockups: contain:paint makes the box the containing block for the
   mockup's own fixed-position scrim, drawer and toast */
.mockbar{display:flex;flex-wrap:wrap;gap:7px;align-items:center;margin:0 0 12px}
.mockbar .st{font:inherit;font-size:12.4px;padding:5px 11px;cursor:pointer;
  background:var(--surface);border:1px solid var(--line-strong);border-radius:var(--radius-sm);
  color:var(--ink-700)}
.mockbar .st:hover{border-color:var(--brand-600);color:var(--brand-700)}
.mockbar .st[aria-pressed="true"]{background:var(--brand-800);border-color:var(--brand-800);
  color:#fff;font-weight:600}
.mockframe{contain:layout paint;position:relative;overflow:auto;
  height:min(78vh,820px);min-height:420px;resize:vertical;
  border:1px solid var(--line-strong);border-radius:var(--radius-md);background:#f4f6f9}
.mocknote{font-size:12.2px;color:var(--ink-500);margin:9px 0 0}
.mocktabs{display:flex;gap:7px;margin:0 0 14px}
.mocktabs button{font:inherit;font-size:13px;padding:6px 13px;cursor:pointer;
  background:none;border:0;border-bottom:2px solid transparent;color:var(--ink-500)}
.mocktabs button[aria-current="true"]{color:var(--brand-800);border-bottom-color:var(--brand-600);
  font-weight:600}

/* search + refs views */
.hit{display:block;width:100%;text-align:left;background:none;border:0;border-bottom:1px solid var(--line);
  padding:11px 2px;cursor:pointer;font:inherit}
.hit:hover{background:var(--brand-50)}
.hit b{font-size:13.8px;display:block}
.hit .hp{font-family:var(--font-mono);font-size:10.8px;color:var(--ink-400);display:block;margin:1px 0 4px}
.hit .sn{font-size:12.6px;color:var(--ink-700);display:block}
.hit mark{background:var(--review-100);color:var(--review-700);border-radius:3px;padding:0 2px}
.ref{border-bottom:1px solid var(--line);padding:12px 0}
.ref:last-child{border-bottom:0}
.ref a{font-size:13.4px;font-family:var(--font-mono);word-break:break-all;color:var(--brand-700)}
.ref .host{display:inline-block;font-size:10.5px;text-transform:uppercase;letter-spacing:.06em;
  background:var(--sunken);border:1px solid var(--line);border-radius:var(--radius-pill);
  padding:1px 8px;color:var(--ink-500);margin-bottom:5px}
.ref .uses{display:flex;flex-wrap:wrap;gap:6px;margin-top:7px}
.ref .uses button{background:var(--sunken);border:1px solid var(--line);border-radius:var(--radius-sm);
  font:inherit;font-size:11.4px;padding:3px 8px;color:var(--ink-700);cursor:pointer}
.ref .uses button:hover{border-color:var(--brand-600);color:var(--brand-700)}

@media (max-width:1100px){
  #shell{grid-template-columns:var(--rail) minmax(0,1fr)}
  #aside{display:none}
}
@media (max-width:860px){
  #shell{grid-template-columns:minmax(0,1fr);gap:14px}
  #menu{display:grid}
  #rail{position:static;max-height:none;display:none}
  #rail.open{display:block}
  #main{padding:20px 18px 28px}
  .hero h1{font-size:23px}
  .flowrow{grid-template-columns:minmax(0,1fr);gap:5px}
  .flowlab{padding-top:0}
  .arrowrow{display:none}
}
</style>

<header id="top">
  <div class="topin">
    <button class="iconbtn" id="menu" aria-label="Documents" aria-expanded="false">☰</button>
    <button class="mark" id="home-btn" title="Back to the atlas home page"><span class="logo">F5</span>FundEli5 <span class="sub">Decision Atlas</span></button>
    <input id="search" type="search" placeholder="Search 62 documents…  ⌘K" autocomplete="off" aria-label="Search the documents">
    <button class="iconbtn" id="theme" aria-label="Switch theme">◐</button>
  </div>
</header>

<div id="shell">
  <nav id="rail" aria-label="Documents">
    <input id="filter" type="search" placeholder="Filter documents" autocomplete="off" aria-label="Filter documents">
    <div id="tree"></div>
  </nav>
  <main id="main"></main>
  <aside id="aside"></aside>
</div>

<script type="application/json" id="atlas">__DATA__</script>
<script src="__MARKED__"></script>
<script>
(function(){
"use strict";
var A = JSON.parse(document.getElementById('atlas').textContent);
var byPath = {}, bySlug = {};
A.docs.forEach(function(d){ byPath[d.path] = d; bySlug[d.slug] = d; });

var main = document.getElementById('main');
var aside = document.getElementById('aside');
var rail = document.getElementById('rail');
var tree = document.getElementById('tree');
var search = document.getElementById('search');
var filter = document.getElementById('filter');

search.placeholder = 'Search ' + A.stats.docs + ' documents…  ⌘K';

/* ---- theme ---------------------------------------------------------- */
try{ var sv = localStorage.getItem('atlas-theme'); if(sv) document.documentElement.setAttribute('data-theme', sv); }catch(e){}
document.getElementById('theme').addEventListener('click', function(){
  var cur = document.documentElement.getAttribute('data-theme');
  if(!cur) cur = matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  var next = cur === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', next);
  try{ localStorage.setItem('atlas-theme', next); }catch(e){}
});

/* ---- helpers -------------------------------------------------------- */
function slugify(s){
  return String(s).toLowerCase().replace(/[^\w\- ]+/g,'').trim().replace(/\s+/g,'-');
}
function esc(s){ return String(s).replace(/[&<>"]/g, function(c){
  return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); }
function el(tag, cls, text){
  var n = document.createElement(tag);
  if(cls) n.className = cls;
  if(text != null) n.textContent = text;
  return n;
}

/* ---- left rail ------------------------------------------------------ */
var railBtns = [];
function buildTree(){
  tree.textContent = '';
  railBtns = [];
  A.groups.forEach(function(g){
    var key = g[0], name = g[1];
    var items = A.docs.filter(function(d){ return d.group === key; });
    if(!items.length) return;
    var box = el('div','gp');
    box.appendChild(el('div','gph', name));
    if(key === 'ux'){
      Object.keys(A.mockups).forEach(function(k){
        var b = el('button','rail-a');
        b.type = 'button';
        b.appendChild(el('span', null, '▸ ' + A.mockups[k].title));
        b.dataset.path = 'mockup-' + k;
        b.dataset.hay = ('mockup ' + A.mockups[k].title + ' ' + A.mockups[k].file).toLowerCase();
        b.addEventListener('click', function(){ goMockup(k); if(window.innerWidth<=860) closeRail(); });
        box.appendChild(b);
        railBtns.push(b);
      });
    }
    items.forEach(function(d){
      var b = el('button','rail-a');
      b.type = 'button';
      b.appendChild(el('span', null, d.label));
      var n = (A.backlinks[d.path] || []).length;
      if(n) { var s = el('span','n', '←' + n); s.title = n + ' document' + (n>1?'s':'') + ' link here'; b.appendChild(s); }
      b.addEventListener('click', function(){ go(d.path); if(window.innerWidth<=860) closeRail(); });
      b.dataset.path = d.path;
      b.dataset.hay = (d.label + ' ' + d.title + ' ' + d.path).toLowerCase();
      box.appendChild(b);
      railBtns.push(b);
    });
    tree.appendChild(box);
  });
}
filter.addEventListener('input', function(){
  var q = filter.value.trim().toLowerCase();
  railBtns.forEach(function(b){ b.hidden = q && b.dataset.hay.indexOf(q) < 0; });
  Array.prototype.forEach.call(tree.querySelectorAll('.gp'), function(g){
    var any = Array.prototype.some.call(g.querySelectorAll('.rail-a'), function(b){ return !b.hidden; });
    g.hidden = !any;
  });
});
function closeRail(){ rail.classList.remove('open'); document.getElementById('menu').setAttribute('aria-expanded','false'); }
document.getElementById('menu').addEventListener('click', function(){
  var o = rail.classList.toggle('open');
  this.setAttribute('aria-expanded', o ? 'true' : 'false');
});
function markCurrent(path){
  railBtns.forEach(function(b){
    if(b.dataset.path === path) b.setAttribute('aria-current','true');
    else b.removeAttribute('aria-current');
  });
}

/* ---- markdown ------------------------------------------------------- */
marked.setOptions({ gfm:true, breaks:false });

function renderDoc(d){
  var host = el('div','md');
  host.innerHTML = marked.parse(d.body);
  var map = A.links[d.path] || {};

  /* heading ids for in-page anchors */
  Array.prototype.forEach.call(host.querySelectorAll('h1,h2,h3,h4'), function(h){
    if(!h.id) h.id = slugify(h.textContent);
  });
  /* tables and wide blocks get their own scroll container */
  Array.prototype.forEach.call(host.querySelectorAll('table'), function(t){
    var w = el('div','scroller'); t.parentNode.insertBefore(w, t); w.appendChild(t);
  });
  /* resolve every link through the graph built at generation time */
  Array.prototype.forEach.call(host.querySelectorAll('a[href]'), function(a){
    var raw = a.getAttribute('href');
    var r = map[raw];
    if(!r){
      if(/^https?:/.test(raw)){ a.className = 'ext'; a.target = '_blank'; a.rel = 'noopener'; }
      return;
    }
    if(r.kind === 'doc'){
      a.className = 'doc';
      a.href = '#' + byPath[r.doc].slug;
      a.title = r.doc + (r.anchor ? '#' + r.anchor : '');
      a.addEventListener('click', function(ev){ ev.preventDefault(); go(r.doc, r.anchor); });
    } else if(r.kind === 'mockup'){
      a.className = 'doc';
      a.href = '#mockup-' + r.which;
      a.title = r.path + ' — opens in the atlas';
      a.addEventListener('click', function(ev){ ev.preventDefault(); goMockup(r.which, r.anchor); });
    } else if(r.kind === 'external'){
      a.className = 'ext'; a.target = '_blank'; a.rel = 'noopener';
    } else if(r.kind === 'asset'){
      a.href = r.href + (r.anchor ? '#' + r.anchor : '');
      a.target = '_blank'; a.rel = 'noopener'; a.className = 'ext';
      a.title = r.path;
    } else if(r.kind === 'anchor'){
      a.addEventListener('click', function(ev){
        var sel = window.CSS && CSS.escape ? CSS.escape(r.anchor) : r.anchor;
        var t = host.querySelector('#' + sel);
        if(t){ ev.preventDefault(); t.scrollIntoView({block:'start', behavior:'smooth'}); }
      });
    } else {
      /* a file that lives in the repo and cannot be served here */
      var chip = el('code','filechip', r.path || raw);
      chip.title = 'File in the repo — not part of this page';
      a.parentNode.replaceChild(chip, a);
    }
  });
  /* images: point at the published copies */
  Array.prototype.forEach.call(host.querySelectorAll('img[src]'), function(img){
    var r = map[img.getAttribute('src')];
    if(r && r.kind === 'asset') img.src = r.href;
    else if(r && (r.kind === 'file' || r.kind === 'broken')) img.replaceWith(el('code','filechip', r.path));
    img.loading = 'lazy';
  });
  return host;
}

/* ---- navigation ------------------------------------------------------
   Every move goes through the hash, so each one becomes a history entry
   and the browser's own Back gesture walks the trail. route() does the
   rendering; go() only changes the address. */
var pendingAnchor = null;
function go(path, anchor){
  var d = byPath[path];
  if(!d) return goHome();
  pendingAnchor = anchor || null;
  if(location.hash.slice(1) === d.slug) open(path, anchor);
  else location.hash = d.slug;
}
function goHome(){
  if(location.hash.slice(1) === 'start') home();
  else location.hash = 'start';
}
function goRefs(){
  if(location.hash.slice(1) === 'references') refs();
  else location.hash = 'references';
}
var pendingState = null;
function goMockup(which, state){
  if(!A.mockups[which]) return goHome();
  pendingState = state || null;
  var h = 'mockup-' + which;
  if(location.hash.slice(1) === h) mockup(which, state);
  else location.hash = h;
}
function homeCrumb(){
  var b = el('button','homeb','⌂  Atlas home');
  b.type = 'button';
  b.title = 'Back to the atlas home page';
  b.addEventListener('click', goHome);
  return b;
}

/* ---- document view -------------------------------------------------- */
function open(path, anchor){
  var d = byPath[path];
  if(!d) return home();
  if(location.hash.slice(1) !== d.slug) history.replaceState(null,'','#'+d.slug);
  main.textContent = '';

  var crumb = el('div','crumb');
  crumb.appendChild(homeCrumb());
  crumb.appendChild(el('span','tag', d.path));
  var g = A.groups.filter(function(x){ return x[0]===d.group; })[0];
  if(g) crumb.appendChild(el('span', null, g[1]));
  crumb.appendChild(el('span', null, '· ' + (d.bytes/1024).toFixed(1) + ' kB'));
  main.appendChild(crumb);

  var body = renderDoc(d);
  main.appendChild(body);
  markCurrent(path);
  buildAside(d, body);

  if(anchor){
    var t = body.querySelector('#' + (window.CSS && CSS.escape ? CSS.escape(anchor) : anchor));
    if(t){ t.scrollIntoView({block:'start'}); return; }
  }
  window.scrollTo(0,0);
}

function buildAside(d, body){
  aside.textContent = '';
  var hs = body.querySelectorAll('h2,h3');
  if(hs.length){
    var s = el('div','asec');
    s.appendChild(el('h4', null, 'On this page'));
    Array.prototype.forEach.call(hs, function(h){
      var b = el('button','toc-a' + (h.tagName==='H3' ? ' h3' : ''), h.textContent);
      b.type = 'button';
      b.addEventListener('click', function(){ h.scrollIntoView({block:'start', behavior:'smooth'}); });
      s.appendChild(b);
    });
    aside.appendChild(s);
  }
  var bl = A.backlinks[d.path] || [];
  var s2 = el('div','asec');
  s2.appendChild(el('h4', null, 'Referenced by (' + bl.length + ')'));
  if(!bl.length) s2.appendChild(el('p','empty','Nothing links here yet.'));
  bl.forEach(function(b){
    var src = byPath[b.doc];
    var btn = el('button','back-a');
    btn.type = 'button';
    btn.appendChild(el('span', null, src ? src.title : b.doc));
    btn.appendChild(el('span','bp', b.doc + (b.label ? '  “' + b.label + '”' : '')));
    btn.addEventListener('click', function(){ go(b.doc); });
    s2.appendChild(btn);
  });
  aside.appendChild(s2);
}

/* ---- home ----------------------------------------------------------- */
function chip(label, path, cls){
  var b = el('button','chip' + (cls ? ' ' + cls : ''), label);
  b.type = 'button';
  if(path){ b.addEventListener('click', function(){ go(path); }); b.title = path; }
  else b.style.cursor = 'default';
  return b;
}
function row(label, chips){
  var r = el('div','flowrow');
  r.appendChild(el('div','flowlab', label));
  var c = el('div','chips');
  chips.forEach(function(x){ c.appendChild(x); });
  r.appendChild(c);
  return r;
}
function home(){
  history.replaceState(null,'','#start');
  main.textContent = '';
  markCurrent(null);

  var hero = el('div','hero');
  hero.appendChild(el('h1','','The decisions behind FundEli5, one page deep'));
  hero.appendChild(el('p','','Every document in the starting repo, with its links resolved: click a reference instead of hunting for the file. The right rail shows what points back at the page you are reading.'));
  main.appendChild(hero);

  var st = el('div','stats');
  [['Documents', A.stats.docs], ['ADRs', A.stats.adrs],
   ['Cross-links', A.stats.links], ['External refs', A.stats.external],
   ['Words', Math.round(A.stats.bytes/6/100)*100]].forEach(function(p){
    var s = el('span','stat');
    s.innerHTML = '<b>' + p[1] + '</b> ' + esc(p[0].toLowerCase());
    st.appendChild(s);
  });
  main.appendChild(st);

  var h2 = el('h2'); h2.textContent = 'The four promises';
  h2.style.cssText = 'font-size:18px;margin:4px 0 12px;padding-bottom:6px;border-bottom:1px solid var(--line)';
  main.appendChild(h2);
  var pw = el('div','promise');
  [['An LLM never decides a Verdict','docs/adr/0001-llm-extracts-rules-engine-decides.md','ADR 0001'],
   ['No LLM runs at check time','docs/adr/0002-no-llm-at-check-time.md','ADR 0002'],
   ['No client data reaches an LLM','docs/adr/0004-two-runtimes-one-llm-egress.md','ADR 0004'],
   ['Suggestions never change a Verdict','docs/adr/0007-advisory-suggestions-never-change-the-verdict.md','ADR 0007']
  ].forEach(function(p){
    var b = el('button','pr'); b.type='button';
    b.appendChild(el('b', null, p[0]));
    b.appendChild(el('span', null, p[2]));
    b.addEventListener('click', function(){ go(p[1]); });
    pw.appendChild(b);
  });
  main.appendChild(pw);

  var h3 = el('h2'); h3.textContent = 'How the build runs';
  h3.style.cssText = 'font-size:18px;margin:30px 0 14px;padding-bottom:6px;border-bottom:1px solid var(--line)';
  main.appendChild(h3);
  var flow = el('div','flow');
  flow.appendChild(row('Tasks', [
    chip('1 · Chart the map','docs/tasks/01-chart-the-map.md','k'),
    chip('2 · Walk the screens','docs/tasks/02-walk-the-screens.md','k'),
    chip('3 · Story + answer key','docs/tasks/03-write-the-demo-story-and-answer-key.md','k')
  ]));
  flow.appendChild(el('div','arrowrow','↓'));
  flow.appendChild(row('Spine', [
    chip('S1 Skeleton','docs/build-workflow.md'), chip('S2 Schemas & ports','docs/build-workflow.md'),
    chip('S3 Walking skeleton','docs/build-workflow.md'),
    chip('S4 Rule Engine · the team’s rows','docs/build-workflow.md','k')
  ]));
  flow.appendChild(el('div','arrowrow','↓'));
  flow.appendChild(row('Waves', [
    chip('A Privacy Gate · catalog · record','docs/build-workflow.md'),
    chip('B Parser · drafter · validation','docs/build-workflow.md'),
    chip('C Screens · card pipeline','docs/build-workflow.md')
  ]));
  flow.appendChild(el('div','arrowrow','↓'));
  flow.appendChild(row('Gates', [
    chip('privacy-gate-auditor','.claude/agents/privacy-gate-auditor.md','gate'),
    chip('engine-purity-reviewer','.claude/agents/engine-purity-reviewer.md','gate'),
    chip('demo-flow-verifier','.claude/agents/demo-flow-verifier.md','gate')
  ]));
  flow.appendChild(el('div','arrowrow','↓'));
  flow.appendChild(row('Demo', [ chip('@must passes · 5 minutes','specs/README.md','done') ]));
  main.appendChild(flow);

  var h4 = el('h2'); h4.textContent = 'Jump in';
  h4.style.cssText = 'font-size:18px;margin:30px 0 14px;padding-bottom:6px;border-bottom:1px solid var(--line)';
  main.appendChild(h4);
  var cards = el('div','cards');
  [['Click through the screens','Both mockups, every state','mockup:dealer'],
   ['Set up Claude Code','10 minutes, before anything','docs/agents/setup.md'],
   ['The words we use','Glossary of the domain','GLOSSARY.md'],
   ['Modules and the privacy boundary','architecture.md','docs/architecture.md'],
   ['Stack, ports, versions','tech-choices.md','docs/tech-choices.md'],
   ['The screens, state by state','ux/README.md + mockups','docs/ux/README.md'],
   ['Open questions on the record','hypotheses.md','docs/hypotheses.md']
  ].forEach(function(c){
    var b = el('button','card'); b.type='button';
    b.appendChild(el('b', null, c[0]));
    b.appendChild(el('span', null, c[1]));
    b.addEventListener('click', function(){
      if(c[2].indexOf('mockup:') === 0) goMockup(c[2].slice(7));
      else go(c[2]);
    });
    cards.appendChild(b);
  });
  main.appendChild(cards);

  var h5 = el('h2'); h5.textContent = 'Outside the repo';
  h5.style.cssText = 'font-size:18px;margin:30px 0 14px;padding-bottom:6px;border-bottom:1px solid var(--line)';
  main.appendChild(h5);
  var p = el('p');
  p.style.cssText = 'font-size:14.4px;color:var(--ink-700);margin:0 0 12px';
  p.textContent = 'Every link the documents make to something outside this repo — the reference build, the mockups, the fund documents — collected in one list, with the pages that cite each one.';
  main.appendChild(p);
  var open_refs = el('button','chip k','Open the reference index →');
  open_refs.type = 'button';
  open_refs.addEventListener('click', goRefs);
  main.appendChild(open_refs);
  if(A.broken.length){
    var bb = el('button','chip done','Link check: ' + A.broken.length + ' unresolved');
    bb.type = 'button'; bb.style.marginLeft = '8px';
    bb.addEventListener('click', goRefs);
    main.appendChild(bb);
  }

  aside.textContent = '';
  var s = el('div','asec');
  s.appendChild(el('h4', null, 'Most referenced'));
  Object.keys(A.backlinks).map(function(k){ return [k, A.backlinks[k].length]; })
    .sort(function(a,b){ return b[1]-a[1]; }).slice(0,9).forEach(function(p){
    var d = byPath[p[0]];
    if(!d) return;
    var b = el('button','back-a'); b.type='button';
    b.appendChild(el('span', null, d.label));
    b.appendChild(el('span','bp', '← ' + p[1] + ' documents'));
    b.addEventListener('click', function(){ go(p[0]); });
    s.appendChild(b);
  });
  aside.appendChild(s);
  window.scrollTo(0,0);
}

/* ---- the live mockups ------------------------------------------------
   The mockup's markup goes into a shadow root with its own tokens.css and
   components.css, so its styles and the atlas's cannot reach each other.
   Its state script is replaced by setState, which applies the same rule. */
function mockup(which, state){
  var m = A.mockups[which];
  if(!m) return goHome();
  var cur = state || m.default;
  if(!m.states.some(function(s){ return s.id === cur; })) cur = m.default;

  main.textContent = '';
  markCurrent(null);
  var crumb = el('div','crumb');
  crumb.appendChild(homeCrumb());
  crumb.appendChild(el('span','tag', m.file));
  crumb.appendChild(el('span', null, 'live mockup'));
  main.appendChild(crumb);

  var h = el('h1'); h.textContent = m.title;
  h.style.cssText = 'font-size:24px;letter-spacing:-.02em;margin:0 0 12px';
  main.appendChild(h);

  var tabs = el('div','mocktabs');
  Object.keys(A.mockups).forEach(function(k){
    var b = el('button', null, A.mockups[k].title);
    b.type = 'button';
    if(k === which) b.setAttribute('aria-current','true');
    b.addEventListener('click', function(){ goMockup(k); });
    tabs.appendChild(b);
  });
  main.appendChild(tabs);

  var bar = el('div','mockbar');
  main.appendChild(bar);
  var frame = el('div','mockframe');
  main.appendChild(frame);

  var note = el('p','mocknote');
  note.textContent = 'The real mockup from ' + m.file + ', every state. Drag the bottom edge to resize. '
    + 'The matching screenshots live in docs/ux/screens/.';
  main.appendChild(note);

  var sr = frame.attachShadow({mode:'open'});
  var style = document.createElement('style');
  style.textContent = A.mockupCss;
  sr.appendChild(style);
  var holder = document.createElement('div');
  holder.innerHTML = m.html;
  sr.appendChild(holder);

  function apply(s){
    cur = s;
    Array.prototype.forEach.call(sr.querySelectorAll('[data-state]'), function(n){
      var on = (n.getAttribute('data-state') || '').split(' ').indexOf(s) >= 0 && n.id !== 'toast';
      n.style.display = on ? '' : 'none';
    });
    Array.prototype.forEach.call(bar.children, function(b){
      b.setAttribute('aria-pressed', b.dataset.state === s ? 'true' : 'false');
    });
    frame.scrollTop = 0;
  }
  m.states.forEach(function(s){
    var b = el('button','st', s.label);
    b.type = 'button';
    b.dataset.state = s.id;
    b.addEventListener('click', function(){ apply(s.id); });
    bar.appendChild(b);
  });
  /* the mockup's own links: states, the other mockup, nothing else */
  sr.addEventListener('click', function(ev){
    var node = ev.target, a = null;
    while(node && node !== sr){
      if(node.tagName === 'A'){ a = node; break; }
      node = node.parentNode;
    }
    if(!a) return;
    ev.preventDefault();
    var href = a.getAttribute('href') || '';
    if(href.charAt(0) === '#'){ apply(href.slice(1)); return; }
    var other = href.match(/^(dealer|validation)\.html(?:#(.+))?$/);
    if(other) goMockup(other[1], other[2] || '');
  });
  apply(cur);

  aside.textContent = '';
  var s2 = el('div','asec');
  s2.appendChild(el('h4', null, 'States'));
  m.states.forEach(function(s){
    var b = el('button','toc-a', s.label);
    b.type = 'button';
    b.addEventListener('click', function(){ apply(s.id); });
    s2.appendChild(b);
  });
  aside.appendChild(s2);
  var s3 = el('div','asec');
  s3.appendChild(el('h4', null, 'Read with it'));
  [['docs/ux/README.md','The state-by-state spec'],
   ['docs/ux/design-system.md','The shared components'],
   ['docs/tasks/02-walk-the-screens.md','Task 2: walk the screens']].forEach(function(p){
    if(!byPath[p[0]]) return;
    var b = el('button','back-a');
    b.type = 'button';
    b.appendChild(el('span', null, p[1]));
    b.appendChild(el('span','bp', p[0]));
    b.addEventListener('click', function(){ go(p[0]); });
    s3.appendChild(b);
  });
  aside.appendChild(s3);
  window.scrollTo(0,0);
}

/* ---- external reference index --------------------------------------- */
function refs(){
  main.textContent = '';
  markCurrent(null);
  var rc = el('div','crumb');
  rc.appendChild(homeCrumb());
  rc.appendChild(el('span','tag','reference index'));
  main.appendChild(rc);
  var h = el('h1'); h.textContent = 'Every reference out of the repo';
  h.style.cssText = 'font-size:25px;letter-spacing:-.02em;margin:0 0 6px';
  main.appendChild(h);
  var sub = el('p');
  sub.style.cssText = 'font-size:14.4px;color:var(--ink-700);margin:0 0 20px;max-width:66ch';
  sub.textContent = A.external.length + ' external links, grouped by how often the documents cite them. Click a citing document to go to it.';
  main.appendChild(sub);

  A.external.forEach(function(r){
    var box = el('div','ref');
    box.appendChild(el('div','host', r.host));
    var a = el('a', null, r.url);
    a.href = r.url; a.target = '_blank'; a.rel = 'noopener';
    box.appendChild(a);
    var uses = el('div','uses');
    r.cites.forEach(function(c){
      var d = byPath[c.doc];
      var b = el('button', null, d ? d.label : c.doc);
      b.type = 'button'; b.title = c.doc;
      b.addEventListener('click', function(){ go(c.doc); });
      uses.appendChild(b);
    });
    box.appendChild(uses);
    main.appendChild(box);
  });

  if(A.broken.length){
    var h2 = el('h2'); h2.textContent = 'Unresolved links';
    h2.style.cssText = 'font-size:18px;margin:30px 0 12px;padding-bottom:6px;border-bottom:1px solid var(--line)';
    main.appendChild(h2);
    A.broken.forEach(function(b){
      var box = el('div','ref');
      box.appendChild(el('div','host','no such file'));
      box.appendChild(el('a', null, b.resolved)).removeAttribute('href');
      var u = el('div','uses');
      var btn = el('button', null, 'in ' + b.doc);
      btn.type = 'button';
      btn.addEventListener('click', function(){ go(b.doc); });
      u.appendChild(btn);
      box.appendChild(u);
      main.appendChild(box);
    });
  }
  aside.textContent = '';
  window.scrollTo(0,0);
}

/* ---- search --------------------------------------------------------- */
function snippet(body, terms){
  var low = body.toLowerCase(), at = -1;
  for(var i=0;i<terms.length;i++){ at = low.indexOf(terms[i]); if(at >= 0) break; }
  if(at < 0) at = 0;
  var from = Math.max(0, at - 70);
  var raw = body.slice(from, from + 230).replace(/\s+/g,' ').trim();
  var out = esc(raw);
  terms.forEach(function(t){
    out = out.replace(new RegExp('(' + t.replace(/[.*+?^${}()|[\]\\]/g,'\\$&') + ')','gi'), '<mark>$1</mark>');
  });
  return (from > 0 ? '…' : '') + out + '…';
}
function runSearch(q){
  var terms = q.toLowerCase().split(/\s+/).filter(Boolean);
  if(!terms.length) return home();
  var hits = [];
  A.docs.forEach(function(d){
    var low = (d.title + ' ' + d.path + ' ' + d.body).toLowerCase();
    var score = 0, all = true;
    terms.forEach(function(t){
      var n = low.split(t).length - 1;
      if(!n) all = false;
      score += n;
      if(d.title.toLowerCase().indexOf(t) >= 0) score += 25;
      if(d.path.toLowerCase().indexOf(t) >= 0) score += 12;
    });
    if(all && score) hits.push({d:d, score:score});
  });
  hits.sort(function(a,b){ return b.score - a.score; });

  main.textContent = '';
  markCurrent(null);
  var sc = el('div','crumb');
  sc.appendChild(homeCrumb());
  sc.appendChild(el('span','tag','search'));
  sc.appendChild(el('span', null, 'Esc clears'));
  main.appendChild(sc);
  var h = el('h1'); h.textContent = hits.length + ' document' + (hits.length===1?'':'s') + ' for “' + q + '”';
  h.style.cssText = 'font-size:21px;letter-spacing:-.02em;margin:0 0 16px';
  main.appendChild(h);
  if(!hits.length){
    main.appendChild(el('p','empty','Nothing matched. Every term has to appear in the document.'));
    aside.textContent = ''; return;
  }
  hits.slice(0,40).forEach(function(hit){
    var b = el('button','hit'); b.type = 'button';
    b.appendChild(el('b', null, hit.d.title));
    b.appendChild(el('span','hp', hit.d.path));
    var sn = el('span','sn');
    sn.innerHTML = snippet(hit.d.body, terms);
    b.appendChild(sn);
    b.addEventListener('click', function(){ search.value = ''; go(hit.d.path); });
    main.appendChild(b);
  });
  aside.textContent = '';
  window.scrollTo(0,0);
}
var tmr;
search.addEventListener('input', function(){
  clearTimeout(tmr);
  var q = search.value.trim();
  tmr = setTimeout(function(){
    if(q) runSearch(q);
    else route();
  }, 140);
});
search.addEventListener('keydown', function(e){ if(e.key === 'Escape'){ search.value=''; search.blur(); route(); } });
document.addEventListener('keydown', function(e){
  if((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k'){ e.preventDefault(); search.focus(); search.select(); }
  else if(e.key === '/' && document.activeElement !== search && document.activeElement !== filter){
    e.preventDefault(); search.focus();
  }
});

/* ---- routing -------------------------------------------------------- */
function route(){
  var h = location.hash.replace(/^#/,'');
  if(!h || h === 'start') return home();
  if(h === 'references') return refs();
  if(h.indexOf('mockup-') === 0){
    var st = pendingState; pendingState = null;
    return mockup(h.slice(7), st);
  }
  if(bySlug[h]){
    var a = pendingAnchor; pendingAnchor = null;
    return open(bySlug[h].path, a);
  }
  home();
}
document.getElementById('home-btn').addEventListener('click', function(){ search.value=''; goHome(); });
window.addEventListener('hashchange', route);
buildTree();
route();
})();
</script>
"""

(OUT / "index.html").write_text(
    HTML.replace("__DATA__", data).replace("__MARKED__", MARKED), encoding="utf-8")

print(f"docs      {payload['stats']['docs']}")
print(f"links     {payload['stats']['links']}  external {payload['stats']['external']}")
print(f"backlinks {sum(len(v) for v in backlinks.values())} edges over {len(backlinks)} targets")
print(f"broken    {len(broken)}")
for b in broken:
    print(f"   {b['doc']} -> {b['target']}")
print(f"page      {(OUT / 'index.html').stat().st_size/1024:.0f} kB")
print("\nassets:")
for src, dest in ASSET_MAP.items():
    print(f"  {dest} <- {src}")
