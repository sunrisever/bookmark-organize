> This file is for AI coding assistants (Claude Code, Codex, OpenCode, OpenClaw, etc.). It is optional and can be safely deleted.

# bookmark-organize

Browser bookmark merge, dedup, link check and classify tool. Combines bookmarks from Chrome, Edge, and HTML exports into a deduplicated, classified collection.

## Key Commands

```bash
python parse_bookmarks.py    # Step 1: Merge & dedup from Chrome/Edge/HTML
python test_links.py         # Step 2: Async link health check (needs proxy)
python organize_bookmarks.py # Step 3: Classify & generate importable HTML
```

## Architecture

- `parse_bookmarks.py`: Read Chrome/Edge JSON + HTML export, normalize URLs (strip utm_/spm, lowercase domain, remove trailing slash), dedup by normalized URL
- `test_links.py`: Async concurrent link testing (50 connections, 15s timeout, via proxy 127.0.0.1:7897). Categorizes as alive/dead/blocked_gfw/suspicious/skipped
- `organize_bookmarks.py`: Heuristic classification by domain + keywords into ~20 categories. Outputs HTML (NETSCAPE format, browser-importable), Markdown (with status icons), and report

## Output Files

- `merged_bookmarks.json`: Deduplicated bookmark data
- `test_results.json`: Link health status added
- `bookmarks_organized.html`: NETSCAPE format, importable to Chrome/Edge
- `bookmarks_organized.md`: Markdown with status icons
- `report.md`: Summary statistics and dead link list

## Important Notes

- `test_links.py` requires a proxy (Clash Verge at 127.0.0.1:7897) for GFW-blocked sites
- HTML import path in `parse_bookmarks.py` is hardcoded, modify if needed
- Classification rules are heuristic, complex cases may misclassify
- All data files contain personal bookmarks and are gitignored
- No AI API needed — pure heuristic approach
