English | [简体中文](README_CN.md)

# Bookmark Organize

> Merge bookmarks locally, deduplicate and check links, then optionally let ChatGPT / Claude / Gemini / Codex review the final structure.

Important clarification:

- browsers do **not** really provide a strong built-in AI bookmark classification workflow
- this project is not meant to force an LLM API
- the default workflow is local, deterministic, and review-friendly

AI is optional here.
The real value is:

1. merge bookmark sources
2. normalize and deduplicate URLs
3. check broken or suspicious links
4. produce an importable result
5. optionally let a strong model review the final tree

## Do I need an API key?

No.

This project works without any LLM API key.
If you want, you can still send the final Markdown report to ChatGPT / Claude / Gemini / Codex for structural review.

## Zero-to-first-result workflow

### Step 1. Install dependency

```bash
pip install aiohttp
```

### Step 2. Merge bookmarks

```bash
python parse_bookmarks.py
```

You should then get:

- `merged_bookmarks.json`

### Step 3. Optionally check links

```bash
python test_links.py
```

You should then get:

- `test_results.json`

### Step 4. Organize bookmarks

```bash
python organize_bookmarks.py
```

You should then get:

- `bookmarks_organized.html`
- `bookmarks_organized.md`
- `report.md`

## Screenshot-style beginner walkthrough

### What you run first

```bash
python parse_bookmarks.py
```

Think of the first “result screen” as:

- your Chrome, Edge, and HTML exports are merged
- duplicates are already normalized and collapsed
- no browser import has happened yet

### What you run second

```bash
python test_links.py
```

This is optional but recommended if your bookmarks are old or messy.

### What you run third

```bash
python organize_bookmarks.py
```

Now you have:

- an importable HTML file
- a readable Markdown tree
- a report for review

### What you optionally send to AI

If you want better category refinement, send:

- `bookmarks_organized.md`
- or `report.md`

Good questions:

- which categories are too broad?
- which bookmarks look misplaced?
- which suspicious links should be removed?
- how should I simplify the tree?

### What you import back to the browser

The file to import is:

- `bookmarks_organized.html`

That is the final browser-ready output.

## Why this is not API-first

This repo is intentionally conservative:

- local scripts do the important work
- AI is a refinement layer
- you do not need a provider key just to get value

## Important files

| File | Purpose |
| --- | --- |
| `parse_bookmarks.py` | merge and deduplicate sources |
| `test_links.py` | check link availability and suspicious sites |
| `organize_bookmarks.py` | final organization and export |
| `merged_bookmarks.json` | merged bookmark data |
| `test_results.json` | link-check result |
| `bookmarks_organized.html` | browser-importable output |
| `bookmarks_organized.md` | readable review output |
| `report.md` | summary report |

## License

MIT
