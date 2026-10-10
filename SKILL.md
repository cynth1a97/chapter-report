---
name: chapter-report
description: Turn one book chapter or paper (PDF, often a scanned one) plus an optional Critical Form (.docx) into a class reading-report package — a 16:9 HTML slide deck for presenting, a one-page "detail" web page with two tabs (full report / Critical Form), and an index page — optionally deployed to Cloudflare Pages with in-page editing the whole group can use. Use when someone says things like "幫我做第 X 章的讀書報告", "把這章做成簡報跟詳細版", "chapter report", "reading report slides", "Critical Form 做成網頁", or hands over a chapter PDF and a Critical Form for a class presentation. Requires the frontend-slides skill for style discovery.
---

# Chapter Report

Make a reading-report package for one chapter: **slides** for the talk, a **detail page** people can read on their own, and an **index page** that links both. Everything is plain HTML/CSS/JS — no build tools.

```
<chapter-folder>/
├── build_slides.py        # slide generator (content lives here)
├── <name>-上台版.html      # generated slides
├── <name>-詳細版.html      # detail page (report tab + Critical Form tab)
└── site/                  # what gets deployed
    ├── index.html  slides.html  detail.html
```

Talk to the user in their language (default 繁體中文). They are usually design students, not engineers: explain in plain words, no jargon.

## Step 0 — Gather inputs (ask everything in one message)

1. The chapter **PDF** (required) and page range if it is part of a bigger file
2. The **Critical Form** `.docx` (optional — without it, skip the Critical Form tab)
3. **Presenters**: names and student IDs exactly as they should appear
4. Talk length (default ~10 minutes → ~10–13 slides)
5. Whether they want it **online** (Cloudflare Pages) and **group editing** — default: local files only

Do not ask about visual style here; Step 3 shows options instead.

## Step 1 — Read the source

**PDF.** Try text first. If the text layer is empty (common for scanned course readers), extract the page images and read them visually:

```bash
python3 <skill>/scripts/pdf_pages.py "<chapter.pdf>" <out_dir>     # writes p01.png, p02.png …
```

Read every page. Scanned Chinese books are often vertical text, right-to-left — read carefully and keep the book's own translated names for people and terms.

**Critical Form.** `python3 <skill>/scripts/read_docx.py "<form.docx>"` prints the text and tables. Keep the student's wording; it is their graded work.

Then write a short outline for yourself: the author's question, method, key examples (who said what, with page numbers), conclusion.

## Step 2 — Plan the slide outline (low density, one idea per slide)

Default order — adapt to the chapter, but keep the shape:

1. Cover (title, English title, chapter + pages, presenters)
2. The author's question
3. Background / preconditions
4. Core concept
5–7. The main content (lists, comparisons, timelines — split long lists across slides, 3–4 items per slide)
8. Conclusion
9. Meaning for design research / for us
10. Does it hold in Taiwan / Asia? (holds / needs revision, two columns)
11. One discussion question for the class

Rules that came from real use:
- **Check every fact against the book.** If the user pastes an AI summary, compare it with the original and tell them what was wrong or missing before using it.
- Separate what the book says from what you added (e.g. outside research). Say so in your reply so the user can decide.
- If the Critical Form has its own discussion question and it differs from the slides, ask which to use.
- Don't put personal profile details (personality tests, a member's own thesis) on a group deck without asking.

## Step 3 — Style discovery (use frontend-slides)

Follow the **frontend-slides** skill's Phase 2: generate 3 one-slide previews from the real cover content — 1 safe preset, 1 bold template, 1 custom wildcard designed around the chapter's own idea (e.g. "strata of civilisations" for a chapter about culture). Open them and let the user pick. Never show template names on the slides themselves.

## Step 4 — Build the slides

Copy `templates/build_slides.py` into the chapter folder and edit:

- `THEME` — colours and fonts from the chosen style (keep CJK font: Noto Serif TC / Noto Sans TC)
- `META` — title, chapter, pages, presenters
- `SLIDES` — the outline, written with the layout helpers already in the file (`cover`, `statement`, `cols`, `ledger`, `discussion`)

```bash
python3 build_slides.py . <frontend-slides>/viewport-base.css
```

The generator inlines `deck.js` (navigation: ← → space, swipe, wheel, page numbers), a hover-only **← 回首頁** button (top-right) and the cloud editor. Then verify **every** slide in a browser at 1280×720: no text overflow, no overlap, nothing hidden behind decorations. Fix and rebuild until clean.

## Step 5 — Build the detail page

Start from `templates/detail.html`. It is a normal scrolling page (works on phones), not slides:

- Sticky top bar: **← 回首頁** and **編輯** buttons on the left (always visible — users could not find hover-only buttons), two tabs on the right: **報告內容** / **Critical Form**
- 報告內容: the full version of the slides — numbered sections, tables become cards on phones
- Critical Form: the docx text verbatim, split into its sections with an in-page table of contents; `#form` in the URL opens this tab
- Reuse the slide theme's colours and fonts so the two feel like one set

## Step 6 — Index page and delivery

Copy `templates/index.html` (two cards: slides / detail, plus presenters). Put the three files in `site/` as `index.html`, `slides.html`, `detail.html` (ASCII names keep URLs clean) and stamp them:

```bash
python3 <skill>/scripts/stamp.py site/slides.html site/detail.html
```

Open everything for the user and summarise: file locations, how to navigate, what to check.

## Step 7 (optional) — Online + group editing on Cloudflare Pages

Only when the user wants a public URL. They need a free Cloudflare account and must log in themselves:

```bash
wrangler login                                   # the user approves in the browser
wrangler kv namespace create <project>-edits     # copy the id
```

In the chapter folder add `wrangler.toml` (from `templates/wrangler.toml.example`, fill in name + KV id) and copy `templates/functions/` next to it. Deploy:

```bash
wrangler pages project create <project> --production-branch main
wrangler pages deploy --branch main
```

Verify `/`, `/slides`, `/detail` and `/api/edits?page=slides` with curl.

How editing works (tell the user): press **E** (or 編輯) on the live site, click any text; it saves 5 s after typing stops (or when you click elsewhere) and everyone sees it. A backup of the previous version is kept once per editing session (per browser, at most every 30 min; last 30 backups) for rollback. Edits are unlimited; the only cap is Cloudflare's free KV quota (~1,000 writes/day per account, ≈ one write per save). Edits are stored by position ("slide N : element M") on top of the HTML.

**Before ANY layout change** (adding/removing slides, columns or sections):
1. `curl <site>/api/edits?page=slides` (and `detail`) — read the online edits and map each key to its element on the live page
2. Write those edits into the source files, rebuild, `stamp.py`, deploy
3. Fetch the edits again; only if `savedAt` is unchanged, back them up and delete the key: `wrangler kv key delete slides --namespace-id <id> --remote`
4. Tell the user to refresh open tabs (stale tabs are blocked from saving by the build stamp)

Skipping this puts people's edits on the wrong slide.

## Files in this skill

| File | What it is |
|---|---|
| `scripts/pdf_pages.py` | PDF → page PNGs (for scanned PDFs) |
| `scripts/read_docx.py` | .docx → plain text with tables |
| `scripts/stamp.py` | writes `<meta name="build">` so edits stay tied to one page version |
| `templates/build_slides.py` | slide generator with layout helpers and a placeholder outline |
| `templates/deck.js` | slide navigation controller |
| `templates/edit-sync.js` | in-page cloud editor (used by slides and detail page) |
| `templates/detail.html` | detail page template (tabs, Critical Form, mobile cards) |
| `templates/index.html` | index page template |
| `templates/functions/api/edits.js` | Cloudflare Pages Function storing edits in KV |
| `templates/wrangler.toml.example` | deploy config |
