"""
书签解析与合并脚本
解析 Chrome JSON、Edge JSON、HTML 导出书签文件，按 URL 去重，清理名称，输出合并后的 JSON。
"""

import json
import os
import re
from html.parser import HTMLParser
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

# 输入文件路径
CHROME_BOOKMARKS = os.path.expandvars(
    r"%LOCALAPPDATA%\Google\Chrome\User Data\Default\Bookmarks"
)
EDGE_BOOKMARKS = os.path.expandvars(
    r"%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Bookmarks"
)
HTML_BOOKMARKS = os.path.expandvars(
    r"%USERPROFILE%\Desktop\favorites_2026_2_2.html"
)

OUTPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "merged_bookmarks.json")

# 需要去除的 URL 追踪参数
TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "spm", "from", "isappinstalled", "bxsign", "ali_trackid", "union_lens",
    "ops_request_misc", "request_id", "biz_id", "scm",
}

# 需要清理的书签名称前缀模式
NAME_NOISE_PATTERNS = [
    re.compile(r"^\(\d+\s*封私信\s*/?\s*\d*\s*条?消息?\)\s*"),  # (1 封私信 / 10 条消息)
    re.compile(r"^\(\d+\s*条消息\)\s*"),                         # (83条消息)
    re.compile(r"^\(\d+\s*封私信\)\s*"),                         # (5封私信)
]

# 可疑域名
SUSPICIOUS_DOMAINS = {"favo.gengnie.com"}


def normalize_url(url: str) -> str:
    """规范化 URL：去除追踪参数、统一 scheme。"""
    try:
        parsed = urlparse(url)
    except Exception:
        return url

    # 特殊协议不处理
    if parsed.scheme in ("edge", "chrome", "javascript", "about", "file", "data"):
        return url

    # 去除追踪参数
    query_params = parse_qs(parsed.query, keep_blank_values=True)
    filtered = {k: v for k, v in query_params.items() if k.lower() not in TRACKING_PARAMS}
    new_query = urlencode(filtered, doseq=True)

    # 去除末尾 fragment 如果为空
    fragment = parsed.fragment

    normalized = urlunparse((
        parsed.scheme,
        parsed.netloc.lower(),
        parsed.path.rstrip("/") if parsed.path != "/" else "/",
        parsed.params,
        new_query,
        fragment,
    ))
    return normalized


def clean_name(name: str) -> str:
    """清理书签名称中的噪音前缀。"""
    for pattern in NAME_NOISE_PATTERNS:
        name = pattern.sub("", name)
    return name.strip()


def is_suspicious_url(url: str) -> bool:
    """检查是否为可疑域名。"""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        for suspicious in SUSPICIOUS_DOMAINS:
            if domain.endswith(suspicious):
                return True
    except Exception:
        pass
    return False


def parse_chromium_json(filepath: str, source: str) -> list[dict]:
    """解析 Chromium 系 (Chrome/Edge) JSON 书签文件。"""
    bookmarks = []

    if not os.path.exists(filepath):
        print(f"  警告: 文件不存在 - {filepath}")
        return bookmarks

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    roots = data.get("roots", {})

    def walk(node, folder_path=""):
        if node.get("type") == "url":
            url = node.get("url", "")
            name = node.get("name", "")
            bookmarks.append({
                "name": name,
                "url": url,
                "folder": folder_path,
                "source": source,
                "date_added": node.get("date_added", ""),
            })
        elif node.get("type") == "folder":
            folder_name = node.get("name", "")
            new_path = f"{folder_path}/{folder_name}" if folder_path else folder_name
            for child in node.get("children", []):
                walk(child, new_path)

    for root_name, root_node in roots.items():
        if isinstance(root_node, dict) and root_node.get("type") == "folder":
            walk(root_node, "")

    print(f"  从 {source} 解析到 {len(bookmarks)} 个书签")
    return bookmarks


class BookmarkHTMLParser(HTMLParser):
    """解析 NETSCAPE-Bookmark-file HTML 格式。"""

    def __init__(self):
        super().__init__()
        self.bookmarks = []
        self.folder_stack = []
        self.current_href = None
        self.current_text = ""
        self.in_a = False
        self.in_h3 = False
        self.h3_text = ""
        self.dl_depth = 0

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        attrs_dict = dict(attrs)
        if tag == "a":
            self.in_a = True
            self.current_href = attrs_dict.get("href", "")
            self.current_text = ""
        elif tag == "h3":
            self.in_h3 = True
            self.h3_text = ""
        elif tag == "dl":
            self.dl_depth += 1

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag == "a" and self.in_a:
            self.in_a = False
            folder_path = "/".join(self.folder_stack)
            self.bookmarks.append({
                "name": self.current_text.strip(),
                "url": self.current_href or "",
                "folder": folder_path,
                "source": "HTML导出",
                "date_added": "",
            })
            self.current_href = None
            self.current_text = ""
        elif tag == "h3" and self.in_h3:
            self.in_h3 = False
            self.folder_stack.append(self.h3_text.strip())
        elif tag == "dl":
            self.dl_depth -= 1
            if self.folder_stack:
                self.folder_stack.pop()

    def handle_data(self, data):
        if self.in_a:
            self.current_text += data
        elif self.in_h3:
            self.h3_text += data


def parse_html_bookmarks(filepath: str) -> list[dict]:
    """解析 HTML 书签文件。"""
    if not os.path.exists(filepath):
        print(f"  警告: 文件不存在 - {filepath}")
        return []

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    parser = BookmarkHTMLParser()
    parser.feed(content)
    print(f"  从 HTML导出 解析到 {len(parser.bookmarks)} 个书签")
    return parser.bookmarks


def merge_and_deduplicate(all_bookmarks: list[dict]) -> list[dict]:
    """按规范化 URL 去重，保留首次出现的书签信息。"""
    seen_urls = {}
    merged = []

    for bm in all_bookmarks:
        url = bm["url"]
        if not url:
            continue

        norm_url = normalize_url(url)

        if norm_url not in seen_urls:
            cleaned = {
                "name": clean_name(bm["name"]),
                "url": url,
                "normalized_url": norm_url,
                "folder": bm["folder"],
                "source": bm["source"],
                "suspicious": is_suspicious_url(url),
            }
            seen_urls[norm_url] = len(merged)
            merged.append(cleaned)
        else:
            # URL 已存在，记录来源
            idx = seen_urls[norm_url]
            existing = merged[idx]
            if bm["source"] not in existing.get("also_in", ""):
                existing["also_in"] = existing.get("also_in", "") + \
                    (", " if existing.get("also_in") else "") + bm["source"]

    return merged


def main():
    print("=" * 60)
    print("书签解析与合并工具")
    print("=" * 60)

    all_bookmarks = []

    # 1. 解析 Chrome 书签
    print("\n[1/3] 解析 Chrome 书签...")
    chrome_bms = parse_chromium_json(CHROME_BOOKMARKS, "Chrome")
    all_bookmarks.extend(chrome_bms)

    # 2. 解析 Edge 书签
    print("\n[2/3] 解析 Edge 书签...")
    edge_bms = parse_chromium_json(EDGE_BOOKMARKS, "Edge")
    all_bookmarks.extend(edge_bms)

    # 3. 解析 HTML 书签
    print("\n[3/3] 解析 HTML 导出书签...")
    html_bms = parse_html_bookmarks(HTML_BOOKMARKS)
    all_bookmarks.extend(html_bms)

    total_raw = len(all_bookmarks)
    print(f"\n原始书签总数: {total_raw}")

    # 4. 合并去重
    print("\n正在去重...")
    merged = merge_and_deduplicate(all_bookmarks)
    print(f"去重后书签数: {len(merged)}")
    print(f"去除重复: {total_raw - len(merged)} 个")

    suspicious_count = sum(1 for bm in merged if bm.get("suspicious"))
    print(f"可疑链接: {suspicious_count} 个")

    # 5. 输出 JSON
    output = {
        "stats": {
            "total_raw": total_raw,
            "chrome_count": len(chrome_bms),
            "edge_count": len(edge_bms),
            "html_count": len(html_bms),
            "merged_count": len(merged),
            "duplicates_removed": total_raw - len(merged),
            "suspicious_count": suspicious_count,
        },
        "bookmarks": merged,
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n已输出到: {OUTPUT_FILE}")
    print("完成!")


if __name__ == "__main__":
    main()
