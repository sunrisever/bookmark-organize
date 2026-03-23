English | [简体中文](README_CN.md)

# Bookmark Organize

> Export bookmarks, clean and deduplicate them locally, and optionally use ChatGPT / Claude / Gemini / Codex or another frontier LLM to improve the final category plan.

This project is a bookmark cleanup and organization workflow for people who have accumulated bookmarks from multiple browsers and exports. It is **not** a repo that depends on an LLM API to work. The default workflow is local and deterministic. AI is optional and is most useful for reviewing the final structure, improving category design, or spotting suspicious classifications.

## What this project actually does

It helps you:

1. merge bookmarks from Chrome, Edge, and HTML exports
2. deduplicate them with URL normalization
3. check for dead or suspicious links
4. classify them into a cleaner structure
5. export browser-importable results

So compared with the other projects, this one is even more conservative:

- local scripts do the heavy lifting
- AI is an optional refinement layer
- no API key is required for normal use

## Do I need an API key?

No.

This project works perfectly fine without any LLM API key.

If you want, you can still take the exported Markdown report and ask:

- ChatGPT
- Claude
- Gemini
- Codex
- Claude Code
- OpenCode

for better category design, suspicious-link review, or manual reorganization suggestions. But that is optional.

## Who this is for

This project is useful if you:

- have bookmarks spread across Chrome, Edge, and old HTML exports
- want a cleaner and importable bookmark tree
- want dead-link detection before keeping old junk forever
- want a workflow stronger than random manual folder dragging in the browser

## Beginner workflow

### 1. Install dependency

```bash
pip install aiohttp
```

Only `test_links.py` needs `aiohttp`. The rest is mostly standard library.

### 2. Merge bookmarks

```bash
python parse_bookmarks.py
```

This reads bookmarks from:

- Chrome default profile
- Edge default profile
- a manually specified HTML export path

Main output:

- `merged_bookmarks.json`

### 3. Optionally test links

```bash
python test_links.py
```

This checks whether links are alive, blocked, dead, or suspicious.

Main output:

- `test_results.json`

### 4. Organize bookmarks

```bash
python organize_bookmarks.py
```

Main outputs:

- `bookmarks_organized.html` — browser-importable bookmarks file
- `bookmarks_organized.md` — readable Markdown version
- `report.md` — statistics and review report

## Recommended AI-assisted review

This repo does not require AI, but it can benefit from strong general-purpose models at the review stage.

A practical workflow is:

1. Run the local scripts
2. Open `bookmarks_organized.md` or `report.md`
3. Send it to ChatGPT / Claude / Gemini / Codex / Claude Code / OpenCode
4. Ask questions like:
   - which categories look too broad?
   - which bookmarks may belong elsewhere?
   - which suspicious links should be removed?
   - how should the tree be simplified?

Then you adjust the script rules or manually edit the result.

## Why this can be better than naive AI-only bookmark sorting

Pure AI-only sorting often has problems:

- it may ignore dead links
- it may miss duplicate URLs with different tracking params
- it may produce nice-looking categories but poor importable structure
- it may be hard to reproduce later

This project keeps the foundation deterministic:

- merge
- normalize
- deduplicate
- link-check
- export

Then AI becomes an optional improvement layer instead of the only source of truth.

## Important files

| File | Purpose |
| --- | --- |
| `parse_bookmarks.py` | merge and deduplicate bookmark sources |
| `test_links.py` | link availability and suspicious-site checks |
| `organize_bookmarks.py` | final category organization and export |
| `merged_bookmarks.json` | merged bookmark data |
| `test_results.json` | link-check result |
| `bookmarks_organized.html` | browser-importable output |
| `bookmarks_organized.md` | readable Markdown export |
| `report.md` | summary and review report |

## Notes

- The HTML import path in `parse_bookmarks.py` may need to be edited for your own machine.
- `test_links.py` works best when Clash Verge or another proxy is available for blocked domains.
- Classification is heuristic, so you should still review the result.
- This is a good tool for periodic cleanup, such as monthly or quarterly bookmark maintenance.

## AI coding assistant support

The repository includes:

- `AGENTS.md`
- `CLAUDE.md`

so it fits well into Codex, Claude Code, OpenCode, and OpenClaw workflows.

## License

MIT
