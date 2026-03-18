English | [简体中文](README_CN.md)

# Bookmark Organize — AI-Assisted Browser Bookmark Organizer

Merge bookmarks from Chrome, Edge, and HTML exports. Use AI-assisted classification together with deterministic cleanup to deduplicate, check dead links, organize categories, and output browser-importable bookmark files.

## Features

- **Multi-source merge**: Combine bookmarks from Chrome + Edge + HTML exports
- **Smart deduplication**: URL normalization (strip utm_/spm tracking params, lowercase domains, remove trailing slashes)
- **Dead link detection**: Async concurrent link testing (50 connections, proxy support for GFW-blocked sites)
- **Heuristic classification**: Domain and keyword-based auto-classification (~20 categories)
- **Multi-format output**: HTML (browser-importable) + Markdown (with status icons) + statistics report
- **AI coding assistant support**: includes `CLAUDE.md` and `AGENTS.md` for Claude Code, Codex, OpenCode, and OpenClaw

## Install

```bash
pip install aiohttp
```

## Workflow

### Step 1: Parse & Merge — parse_bookmarks.py

```bash
python parse_bookmarks.py
```

Reads bookmarks from three sources and merges with deduplication:
- Chrome: `%LOCALAPPDATA%\Google\Chrome\User Data\Default\Bookmarks`
- Edge: `%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Bookmarks`
- HTML export: manually specified file path (edit in source code)

**Dedup logic**: Normalize URLs (strip tracking params, lowercase domain, remove trailing slash) → keep first occurrence.

**Output**: `merged_bookmarks.json`

### Step 2: Link Check — test_links.py (Optional but Recommended)

```bash
python test_links.py
```

Async concurrent testing of all bookmark URLs.

| Status | Meaning |
|--------|---------|
| `alive` | HTTP 2xx/3xx, working |
| `alive_block` | HTTP 4xx, server online but blocked (anti-scraping / login required) |
| `blocked_gfw` | Known GFW-blocked domain timeout |
| `dead` | DNS failure / connection error / 5xx |
| `skipped` | Special protocols (edge:// / chrome:// etc.) |
| `suspicious` | Known malicious domain |

> Requires proxy (Clash Verge at `127.0.0.1:7897`). Without proxy, GFW-blocked sites will all timeout.

**Output**: `test_results.json`

### Step 3: Classify — organize_bookmarks.py

```bash
python organize_bookmarks.py
```

Classifies bookmarks into ~20 categories using domain and keyword heuristics.

**Output**:

| File | Purpose |
|------|---------|
| `bookmarks_organized.html` | NETSCAPE format, **directly importable to Chrome/Edge** |
| `bookmarks_organized.md` | Markdown with status icons |
| `report.md` | Summary: statistics, category distribution, dead link list |

## Example Categories

Campus (SJTU), Math, Programming/C++, Programming/Dev, AI Tools, VPN & Proxy, Books & Literature, Wallpapers, Online Tools, Others...

## Notes

- HTML import path in `parse_bookmarks.py` is hardcoded — modify for your setup
- `test_links.py` requires proxy running (Clash Verge at `127.0.0.1:7897`)
- Classification is heuristic — check `report.md` for edge cases
- Uses only stdlib + aiohttp, no AI API needed
- Good for periodic runs (e.g., monthly bookmark cleanup)

## License

MIT
