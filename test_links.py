"""
链接可用性测试脚本
异步并发测试所有书签链接，标记状态：
  alive       - 可访问（HTTP 2xx/3xx）
  alive_block - 服务器有响应但拒绝请求（HTTP 4xx，通常是反爬/需登录，网站本身没问题）
  blocked_gfw - 被墙/无法从国内访问（已知被墙域名超时）
  dead        - 真正失效（DNS 解析失败、连接被拒、服务器无响应且非被墙站点）
  skipped     - 特殊协议
  suspicious  - 可疑域名
"""

import asyncio
import json
import os
import sys
import time
from urllib.parse import urlparse

import aiohttp

INPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "merged_bookmarks.json")
OUTPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_results.json")

# 代理设置（本地代理端口）
PROXY = "http://127.0.0.1:7897"

# 并发连接数
CONCURRENCY = 50
# 超时秒数
TIMEOUT = 15
# 跳过测试的协议
SKIP_SCHEMES = {"edge", "chrome", "javascript", "about", "file", "data", "mailto", "tel", "ftp",
                "chrome-extension"}
# 可疑域名
SUSPICIOUS_DOMAINS = {"favo.gengnie.com"}

# 已知被墙/国内无法直接访问的域名关键词
GFW_BLOCKED_DOMAINS = {
    "google.com", "google.co", "googleapis.com", "googleusercontent.com",
    "youtube.com", "youtu.be", "ytimg.com",
    "facebook.com", "instagram.com", "twitter.com", "x.com",
    "chatgpt.com", "openai.com",
    "wikipedia.org", "wikimedia.org",
    "github.io",  # 部分不稳定
    "reddit.com",
    "stackoverflow.com", "stackexchange.com",
    "medium.com",
    "notion.so",
    "hackingcpp.com",
    "gitbook.io",
    "readthedocs.io",
    "pytorch.org",
    "unsplash.com", "pexels.com",
    "apkpure.com",
    "wallhaven.cc",
    "emojixd.com",
}


def _get_domain(url: str) -> str:
    try:
        return urlparse(url).netloc.lower()
    except Exception:
        return ""


def should_skip(url: str) -> bool:
    """判断是否跳过测试。"""
    try:
        parsed = urlparse(url)
        return parsed.scheme.lower().replace(":", "") in SKIP_SCHEMES
    except Exception:
        return True


def is_suspicious(url: str) -> bool:
    """判断是否为可疑域名。"""
    domain = _get_domain(url)
    for s in SUSPICIOUS_DOMAINS:
        if domain.endswith(s):
            return True
    return False


def is_gfw_blocked(url: str) -> bool:
    """判断是否为已知被墙域名。"""
    domain = _get_domain(url)
    for blocked in GFW_BLOCKED_DOMAINS:
        if domain == blocked or domain.endswith("." + blocked):
            return True
    return False


async def test_url(session: aiohttp.ClientSession, url: str, semaphore: asyncio.Semaphore) -> dict:
    """测试单个 URL 的可用性。"""
    result = {"url": url, "status": "unknown", "http_code": None, "error": None}

    if should_skip(url):
        result["status"] = "skipped"
        result["error"] = "特殊协议，跳过测试"
        return result

    if is_suspicious(url):
        result["status"] = "suspicious"
        result["error"] = "可疑域名"
        return result

    async with semaphore:
        try:
            # 先尝试 HEAD 请求（通过代理）
            async with session.head(url, timeout=aiohttp.ClientTimeout(total=TIMEOUT),
                                    allow_redirects=True, ssl=False,
                                    proxy=PROXY) as resp:
                result["http_code"] = resp.status
                if resp.status < 400:
                    result["status"] = "alive"
                elif resp.status < 500:
                    # 4xx: 服务器在线，只是拒绝了自动请求（反爬/需登录）
                    result["status"] = "alive_block"
                    result["error"] = f"HTTP {resp.status} (服务器在线，拒绝自动请求)"
                else:
                    # 5xx: 再用 GET 试一次
                    try:
                        async with session.get(url, timeout=aiohttp.ClientTimeout(total=TIMEOUT),
                                               allow_redirects=True, ssl=False,
                                               proxy=PROXY) as resp2:
                            result["http_code"] = resp2.status
                            if resp2.status < 400:
                                result["status"] = "alive"
                            elif resp2.status < 500:
                                result["status"] = "alive_block"
                                result["error"] = f"HTTP {resp2.status} (服务器在线)"
                            else:
                                result["status"] = "dead"
                                result["error"] = f"HTTP {resp2.status}"
                    except Exception:
                        result["status"] = "dead"
                        result["error"] = f"HTTP {resp.status}"
        except (aiohttp.ClientError, asyncio.TimeoutError, OSError) as e:
            err_msg = str(e)[:100] if str(e) else type(e).__name__
            if isinstance(e, asyncio.TimeoutError):
                # 超时，再用 GET 试一次
                try:
                    async with session.get(url, timeout=aiohttp.ClientTimeout(total=TIMEOUT),
                                           allow_redirects=True, ssl=False,
                                           proxy=PROXY) as resp3:
                        result["http_code"] = resp3.status
                        if resp3.status < 500:
                            result["status"] = "alive" if resp3.status < 400 else "alive_block"
                        else:
                            result["status"] = "dead"
                        result["error"] = f"HEAD超时但GET成功 HTTP {resp3.status}" if result["status"] != "dead" else f"HTTP {resp3.status}"
                except Exception:
                    result["status"] = "dead"
                    result["error"] = "超时"
            else:
                result["status"] = "dead"
                result["error"] = err_msg
        except Exception as e:
            result["status"] = "dead"
            result["error"] = str(e)[:100]

    return result


async def run_tests(bookmarks: list[dict]) -> list[dict]:
    """并发测试所有链接。"""
    semaphore = asyncio.Semaphore(CONCURRENCY)
    total = len(bookmarks)

    # 自定义 headers 模拟浏览器
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    connector = aiohttp.TCPConnector(limit=CONCURRENCY, limit_per_host=5, enable_cleanup_closed=True)
    async with aiohttp.ClientSession(headers=headers, connector=connector) as session:
        tasks = []
        for bm in bookmarks:
            tasks.append(test_url(session, bm["url"], semaphore))

        # 实时显示进度
        results = []
        completed = 0
        start_time = time.time()

        for coro in asyncio.as_completed(tasks):
            result = await coro
            results.append(result)
            completed += 1
            if completed % 20 == 0 or completed == total:
                elapsed = time.time() - start_time
                pct = completed / total * 100
                print(f"\r  进度: {completed}/{total} ({pct:.1f}%) - 耗时 {elapsed:.1f}s", end="", flush=True)

        print()  # 换行

    # 按原始顺序排列结果
    url_to_result = {r["url"]: r for r in results}
    ordered = []
    for bm in bookmarks:
        r = url_to_result.get(bm["url"], {"url": bm["url"], "status": "unknown"})
        ordered.append(r)

    return ordered


def main():
    print("=" * 60)
    print("链接可用性测试工具")
    print("=" * 60)

    if not os.path.exists(INPUT_FILE):
        print(f"错误: 未找到输入文件 {INPUT_FILE}")
        print("请先运行 parse_bookmarks.py")
        sys.exit(1)

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    bookmarks = data["bookmarks"]
    total = len(bookmarks)
    print(f"\n共 {total} 个书签待测试")

    print("\n开始测试链接...")
    start = time.time()
    results = asyncio.run(run_tests(bookmarks))
    elapsed = time.time() - start

    # 统计结果
    stats = {"alive": 0, "alive_block": 0, "blocked_gfw": 0,
             "dead": 0, "skipped": 0, "suspicious": 0, "unknown": 0}
    for r in results:
        s = r.get("status", "unknown")
        stats[s] = stats.get(s, 0) + 1

    print(f"\n测试完成！耗时 {elapsed:.1f} 秒")
    print(f"  可访问 (alive):           {stats['alive']}")
    print(f"  在线但拒绝请求 (alive_block): {stats['alive_block']}")
    print(f"  被墙 (blocked_gfw):       {stats['blocked_gfw']}")
    print(f"  真正失效 (dead):          {stats['dead']}")
    print(f"  跳过 (skipped):           {stats['skipped']}")
    print(f"  可疑 (suspicious):        {stats['suspicious']}")

    # 合并到书签数据
    for bm, result in zip(bookmarks, results):
        bm["test_status"] = result.get("status", "unknown")
        bm["http_code"] = result.get("http_code")
        bm["test_error"] = result.get("error")

    output = {
        "stats": {
            **data["stats"],
            "test_stats": stats,
            "test_duration_seconds": round(elapsed, 1),
        },
        "bookmarks": bookmarks,
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n结果已输出到: {OUTPUT_FILE}")
    print("完成!")


if __name__ == "__main__":
    main()
