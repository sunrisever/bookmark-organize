"""
分类整理与输出脚本
读取测试结果，智能分类，生成 HTML 书签文件、Markdown 文档和整理报告。
"""

import json
import os
import re
import sys
from datetime import datetime
from urllib.parse import urlparse

INPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_results.json")
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))


# ============================================================
# 分类规则
# ============================================================

CATEGORY_RULES = [
    # (分类名, 匹配函数)
    # 优先级从高到低，第一个匹配的分类生效
]


def _domain(url: str) -> str:
    try:
        return urlparse(url).netloc.lower()
    except Exception:
        return ""


def _path(url: str) -> str:
    try:
        return urlparse(url).path.lower()
    except Exception:
        return ""


def classify_bookmark(bm: dict) -> str:
    """根据 URL 域名、原始文件夹、名称智能分类。"""
    url = bm.get("url", "")
    name = bm.get("name", "")
    folder = bm.get("folder", "")
    domain = _domain(url)
    path = _path(url)
    folder_lower = folder.lower()
    name_lower = name.lower()

    # CDCL 大作业
    if "cdcl" in folder_lower or "cdcl" in name_lower or "cdcl" in url.lower():
        return "CDCL 大作业"

    # SJTU 校园（含交大域名下的课程页面）
    if "sjtu.edu.cn" in domain or "sjtu.plus" in domain or "sjtu" in folder_lower:
        return "SJTU 校园"
    if "share.dyweb.sjtu.cn" in domain:
        return "SJTU 校园"
    if "202.120." in domain or "202.120." in url:
        return "SJTU 校园"
    if "sjtu" in name_lower or "交大" in name_lower:
        return "SJTU 校园"

    # 数学分类：文件夹+名称双重验证
    # 数学分析
    _math_analysis_name = any(kw in name_lower for kw in [
        "数学分析", "数分", "实数", "连续统", "完备", "阿基米德",
        "希尔伯特", "无理数", "域", "环与域", "除环", "运算封闭",
        "保序同构", "稠密", "内积空间", "度量空间", "一致空间",
        "常微分", "格林公式", "高斯公式", "斯托克斯",
    ])
    if any(kw in folder_lower for kw in ["数学分析", "数分"]) and _math_analysis_name:
        return "数学/数学分析"
    if any(kw in name_lower for kw in ["数学分析", "数分"]):
        return "数学/数学分析"
    if _math_analysis_name and ("数学" in folder_lower or "math" in folder_lower):
        return "数学/数学分析"

    # 线性代数 → 数学/其他
    if any(kw in name_lower for kw in ["线性代数", "线代", "linear algebra"]):
        return "数学/其他"

    # 离散数学 → 数学/其他
    if any(kw in name_lower for kw in ["离散数学"]):
        return "数学/其他"
    if "hongfeifu" in url:
        return "数学/其他"

    # 数学通用（文件夹标记）
    if "数学" in folder_lower or "math" in folder_lower:
        _any_math = any(kw in name_lower for kw in [
            "数学", "math", "代数", "微积分", "矩阵", "概率",
            "统计", "拓扑", "数论", "最优化", "mooc", "课程",
        ])
        if _any_math:
            return "数学/其他"

    # 数学通用关键词
    if any(kw in name_lower for kw in ["最优化", "图论", "graph theory", "统计",
                                        "statistics", "随机过程", "概率论",
                                        "代数", "algebra", "微积分", "拓扑",
                                        "矩阵", "数论", "metamath",
                                        "常微分", "微分方程"]):
        return "数学/其他"
    if any(kw in url for kw in ["optbook", "metamath.org", "bimsa.cn"]):
        return "数学/其他"
    if "zyhwtc.com" in domain:
        return "数学/其他"

    # 大学课程攻略/资源 → 编程学习
    if any(kw in name_lower for kw in ["课程攻略", "课程资源", "课目", "learning_resource",
                                        "icicles", "pkucourse", "ustc-course"]):
        return "编程学习/编程与开发"
    if "计算机公开课" in name_lower or "免费的计算机" in name_lower:
        return "编程学习/编程与开发"

    # C++
    if "c++" in folder_lower or "c++" in name_lower or "cpp" in folder_lower:
        return "编程学习/C++"
    if "educoder.net" in domain:
        return "编程学习/C++"

    # GitHub 项目（按内容分配到具体类目）
    if "github.com" in domain or "github.io" in domain:
        if any(kw in name_lower for kw in ["草榴", "1024app", "porn"]):
            return "NSFW"
        if any(kw in name_lower for kw in ["clash", "shadowsocks", "v2ray", "trojan", "proxy"]):
            return "代理与VPN"
        if any(kw in name_lower for kw in ["课程攻略", "课程资源", "course", "课目",
                                            "learning_resource", "icicles", "大作业"]):
            return "编程学习/编程与开发"
        if any(kw in name_lower for kw in ["deep learning", "深度学习"]):
            return "编程学习/编程与开发"
        if "linear-algebra" in name_lower or "线性代数" in name_lower:
            return "数学/其他"
        if any(kw in name_lower for kw in ["statistics", "统计", "math"]):
            return "数学/其他"
        if any(kw in name_lower for kw in ["c++", "cpp", "cppcoreguide"]):
            return "编程学习/C++"
        return "编程学习/编程与开发"

    # CSDN 博客
    if "csdn.net" in domain:
        if any(kw in name_lower for kw in ["格林公式", "高斯公式", "斯托克斯", "微积分",
                                            "数学", "矩阵", "代数"]):
            return "数学/数学分析"
        return "编程学习/编程与开发"

    # ====== NSFW ======
    nsfw_domains = {
        "spankbanglive.com", "eporner.com", "missav.ws", "missav.live",
        "njav.tv", "jable.tv", "123av.com", "simpcity.su", "javtrailers.com",
        "javevil.com", "javlikes.com", "jav.pub", "my622.com",
        "erodouga-beam.com", "51bl.cool",
        "g64w.com", "yourdesignagency.com", "leqqz.cn",
    }
    if any(domain.endswith(d) for d in nsfw_domains):
        return "NSFW"

    # ====== AI 工具 ======
    ai_domains = {
        "chatgpt.com", "claude.ai", "chat.qwenlm.ai", "chat.deepseek.com",
        "chat.zju.edu.cn", "yuanbao.tencent.com", "app.grammarly.com",
        "tingwu.aliyun.com", "chatpdf.com", "livebench.ai",
        "vmake.ai", "x-design.com", "ai-bot.cn",
        "chat-with-geogebra.com",
    }
    if any(domain.endswith(d) for d in ai_domains):
        return "AI 工具"

    # ====== 代理/VPN ======
    proxy_domains = {
        "duyaoss.com", "fbvipaffa05.cc", "flyingbirds.pro",
        "ttyun168.com", "amytele.net", "sms-activate.org",
        "glados.space", "ttgongbu.xyz", "sockboom.id", "iskrbt.top",
    }
    if any(domain.endswith(d) for d in proxy_domains):
        return "代理与VPN"

    # ====== 图书与文献 ======
    lib_domains = {
        "z-library.sk", "annas-archive.org", "llhlf.com",
        "cnki.net", "cnki.com",
        "book.douban.com", "e-m.jd.com",
        "reserves.lib.tsinghua.edu.cn",
    }
    if any(domain.endswith(d) for d in lib_domains):
        return "图书与文献"
    if "zlibrary" in name_lower or "libgen" in name_lower or "z-lib" in name_lower:
        return "图书与文献"
    if "读书" in name_lower:
        return "图书与文献"
    if any(kw in folder_lower for kw in ["学术", "论文"]):
        return "图书与文献"

    # ====== 壁纸与图片 ======
    wallpaper_domains = {
        "wallhaven.cc", "unsplash.com", "pexels.com", "peapix.com",
        "pidoutv.com", "paper.photos", "wallwiz.com", "bigjpg.com",
        "istockphoto.com", "aiseesoft.com",
    }
    if any(domain.endswith(d) for d in wallpaper_domains):
        return "壁纸与图片"
    if any(kw in name_lower for kw in ["壁纸", "wallpaper", "图片素材"]):
        return "壁纸与图片"

    # ====== 在线工具与资源（合并原在线工具+导航与资源站） ======
    tool_domains = {
        "wolframalpha.com", "geogebra.org", "mathcha.io",
        "convertio.co", "ilovepdf.com", "pic.55.la",
        "text-to-speech.cn", "matrix.reshish.com", "reshish.com",
        "zimujiang.com", "timelessq.com", "y2mate.com",
        "ieee.icu", "overleaf.com",
        "xue8nav.com", "adzhp.xyz", "fanl.top",
        "appledi.com", "ciligoufabuye2.xyz", "jjtui.com",
        "tgdriver.com",
    }
    if "latex" in name_lower:
        return "在线工具与资源"
    if any(domain.endswith(d) for d in tool_domains):
        return "在线工具与资源"

    # ====== 编程学习/编程与开发 ======
    dev_domains = {
        "python.org", "pytorch.org", "runoob.com",
        "stackoverflow.com", "stackexchange.com", "robotics.stackexchange.com",
        "leetcode.cn", "luogu.com.cn", "hdlbits.01xz.net",
        "readthedocs.io", "netlify.app",
        "developer.nvidia.com", "developer.nvidia.cn",
        "intel.com", "riscv.org", "techpowerup.com",
        "ros.org", "openrobotics.org", "guyuehome.com", "autolabor.com.cn",
        "azeria-labs.com", "docs.net9.org", "wchargin.com",
        "csdiy.wiki", "learncs.site", "composingprograms.netlify.app",
        "book.systemsapproach.org", "kaoyansou.cn",
        "gitee.com",
        "icourse163.org", "xuetangx.com", "ocw.mit.edu",
        "udemy.com", "courses.d2l.ai", "zh-v2.d2l.ai", "d2l.ai",
        "rymooc.com",
        "learn.tsinghua.edu.cn",
        "classes.berkeley.edu", "learn.microsoft.com",
        "developers.google.com", "icourse.club",
    }
    if any(domain.endswith(d) for d in dev_domains):
        return "编程学习/编程与开发"
    if any(kw in name_lower for kw in ["算法", "数据结构", "编程", "代码", "开发",
                                        "ros", "机器人", "robotics",
                                        "mooc", "慕课", "操作系统"]):
        return "编程学习/编程与开发"
    if any(kw in folder_lower for kw in ["编程", "程序", "代码", "开发", "coding", "programming"]):
        return "编程学习/编程与开发"

    # ====== B站内容细分 ======
    if "bilibili.com" in domain:
        if "9027520" in url:  # ZY-Eric 数学笔记
            return "数学/其他"
        if "390606417" in url:  # 大语言模型网课
            return "编程学习/编程与开发"
        if any(kw in name_lower for kw in ["数学", "math", "mathematical"]):
            return "数学/其他"
        return "其他"

    # ====== YouTube 内容细分 ======
    if "youtube.com" in domain:
        if any(kw in name_lower for kw in ["mathematical", "discrete math", "数学"]):
            return "数学/其他"
        return "其他"

    # 考研 → 看内容
    if "考研" in name_lower:
        if "数学" in name_lower:
            return "数学/其他"
        return "编程学习/编程与开发"

    # 超星 → 看内容
    if "chaoxing.com" in domain:
        if any(kw in name_lower for kw in ["数学", "微分", "代数", "概率", "统计"]):
            return "数学/其他"
        return "编程学习/编程与开发"

    return "其他"


# ============================================================
# HTML 生成
# ============================================================

def generate_html(categories: dict[str, list[dict]], output_path: str):
    """生成标准 NETSCAPE-Bookmark-file-1 HTML 文件。"""
    lines = [
        "<!DOCTYPE NETSCAPE-Bookmark-file-1>",
        "<!-- This is an automatically generated file.",
        "     It will be read and overwritten.",
        "     DO NOT EDIT! -->",
        '<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">',
        "<TITLE>Bookmarks</TITLE>",
        "<H1>Bookmarks</H1>",
        "<DL><p>",
        '    <DT><H3 PERSONAL_TOOLBAR_FOLDER="true">书签栏</H3>',
        "    <DL><p>",
    ]

    def escape_html(text: str) -> str:
        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

    # 按分类排序
    sorted_cats = sorted(categories.keys())

    for cat in sorted_cats:
        bms = categories[cat]
        if not bms:
            continue

        # 处理子分类（如 "编程学习/C++ 教程与参考"）
        parts = cat.split("/")
        indent = "        "

        if len(parts) == 1:
            lines.append(f'{indent}<DT><H3>{escape_html(cat)}</H3>')
            lines.append(f"{indent}<DL><p>")
            for bm in bms:
                name = escape_html(bm["name"])
                url = escape_html(bm["url"])
                lines.append(f'{indent}    <DT><A HREF="{url}">{name}</A>')
            lines.append(f"{indent}</DL><p>")
        else:
            # 对于子分类，先创建父分类文件夹再嵌套
            pass  # 将在下面统一处理

    # 重新组织：将子分类嵌套到父分类下
    lines = [
        "<!DOCTYPE NETSCAPE-Bookmark-file-1>",
        "<!-- This is an automatically generated file.",
        "     It will be read and overwritten.",
        "     DO NOT EDIT! -->",
        '<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">',
        "<TITLE>Bookmarks</TITLE>",
        "<H1>Bookmarks</H1>",
        "<DL><p>",
        '    <DT><H3 PERSONAL_TOOLBAR_FOLDER="true">书签栏</H3>',
        "    <DL><p>",
    ]

    # 构建层级结构
    tree = {}  # parent -> {subcats, bookmarks}
    for cat in sorted_cats:
        parts = cat.split("/")
        if len(parts) == 1:
            if cat not in tree:
                tree[cat] = {"subcats": {}, "bookmarks": []}
            tree[cat]["bookmarks"] = categories[cat]
        else:
            parent = parts[0]
            sub = parts[1]
            if parent not in tree:
                tree[parent] = {"subcats": {}, "bookmarks": []}
            tree[parent]["subcats"][sub] = categories[cat]

    indent1 = "        "
    indent2 = "            "
    indent3 = "                "

    for parent in sorted(tree.keys()):
        node = tree[parent]
        lines.append(f'{indent1}<DT><H3>{escape_html(parent)}</H3>')
        lines.append(f"{indent1}<DL><p>")

        # 父分类直属书签
        for bm in node["bookmarks"]:
            name = escape_html(bm["name"])
            url = escape_html(bm["url"])
            lines.append(f'{indent2}<DT><A HREF="{url}">{name}</A>')

        # 子分类
        for sub_name in sorted(node["subcats"].keys()):
            sub_bms = node["subcats"][sub_name]
            lines.append(f'{indent2}<DT><H3>{escape_html(sub_name)}</H3>')
            lines.append(f"{indent2}<DL><p>")
            for bm in sub_bms:
                name = escape_html(bm["name"])
                url = escape_html(bm["url"])
                lines.append(f'{indent3}<DT><A HREF="{url}">{name}</A>')
            lines.append(f"{indent2}</DL><p>")

        lines.append(f"{indent1}</DL><p>")

    lines.append("    </DL><p>")
    lines.append("</DL><p>")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"  HTML 书签文件: {output_path}")


# ============================================================
# Markdown 生成
# ============================================================

STATUS_EMOJI = {
    "alive": "[OK]",
    "alive_block": "[OK-反爬]",
    "blocked_gfw": "[被墙]",
    "dead": "[失效]",
    "skipped": "[跳过]",
    "suspicious": "[可疑]",
    "unknown": "[?]",
}


def generate_markdown(categories: dict[str, list[dict]], stats: dict, output_path: str):
    """生成 Markdown 文档。"""
    lines = [
        "# 浏览器书签整理",
        "",
        f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## 统计信息",
        "",
        f"- 原始书签总数: {stats.get('total_raw', 'N/A')}",
        f"- 去重后数量: {stats.get('merged_count', 'N/A')}",
        f"- 去除重复: {stats.get('duplicates_removed', 'N/A')} 个",
        "",
    ]

    test_stats = stats.get("test_stats", {})
    if test_stats:
        lines.extend([
            "### 链接测试结果",
            "",
            f"- 可访问: {test_stats.get('alive', 0)}",
            f"- 在线但拒绝自动请求 (反爬/需登录): {test_stats.get('alive_block', 0)}",
            f"- 被墙/国内无法访问: {test_stats.get('blocked_gfw', 0)}",
            f"- 真正失效: {test_stats.get('dead', 0)}",
            f"- 跳过: {test_stats.get('skipped', 0)}",
            f"- 可疑: {test_stats.get('suspicious', 0)}",
            "",
        ])

    lines.append("---")
    lines.append("")

    # 构建层级结构
    tree = {}
    sorted_cats = sorted(categories.keys())
    for cat in sorted_cats:
        parts = cat.split("/")
        if len(parts) == 1:
            if cat not in tree:
                tree[cat] = {"subcats": {}, "bookmarks": []}
            tree[cat]["bookmarks"] = categories[cat]
        else:
            parent = parts[0]
            sub = parts[1]
            if parent not in tree:
                tree[parent] = {"subcats": {}, "bookmarks": []}
            tree[parent]["subcats"][sub] = categories[cat]

    for parent in sorted(tree.keys()):
        node = tree[parent]
        total_in_cat = len(node["bookmarks"]) + sum(len(v) for v in node["subcats"].values())
        lines.append(f"## {parent} ({total_in_cat})")
        lines.append("")

        for bm in node["bookmarks"]:
            status = STATUS_EMOJI.get(bm.get("test_status", "unknown"), "[?]")
            lines.append(f"- {status} [{bm['name']}]({bm['url']})")

        for sub_name in sorted(node["subcats"].keys()):
            sub_bms = node["subcats"][sub_name]
            lines.append(f"### {sub_name} ({len(sub_bms)})")
            lines.append("")
            for bm in sub_bms:
                status = STATUS_EMOJI.get(bm.get("test_status", "unknown"), "[?]")
                lines.append(f"- {status} [{bm['name']}]({bm['url']})")
            lines.append("")

        lines.append("")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"  Markdown 文档: {output_path}")


# ============================================================
# 报告生成
# ============================================================

def generate_report(categories: dict[str, list[dict]], stats: dict, output_path: str):
    """生成整理报告。"""
    lines = [
        "# 书签整理报告",
        "",
        f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## 一、汇总统计",
        "",
        f"| 项目 | 数量 |",
        f"|------|------|",
        f"| Chrome 书签 | {stats.get('chrome_count', 'N/A')} |",
        f"| Edge 书签 | {stats.get('edge_count', 'N/A')} |",
        f"| HTML 导出书签 | {stats.get('html_count', 'N/A')} |",
        f"| 原始书签总数 | {stats.get('total_raw', 'N/A')} |",
        f"| **去重后数量** | **{stats.get('merged_count', 'N/A')}** |",
        f"| 去除重复 | {stats.get('duplicates_removed', 'N/A')} |",
        "",
    ]

    test_stats = stats.get("test_stats", {})
    if test_stats:
        lines.extend([
            "### 链接测试结果",
            "",
            f"| 状态 | 数量 |",
            f"|------|------|",
            f"| 可访问 (alive) | {test_stats.get('alive', 0)} |",
            f"| 在线但拒绝请求 (alive_block) | {test_stats.get('alive_block', 0)} |",
            f"| 被墙/国内无法访问 (blocked_gfw) | {test_stats.get('blocked_gfw', 0)} |",
            f"| 真正失效 (dead) | {test_stats.get('dead', 0)} |",
            f"| 跳过 (skipped) | {test_stats.get('skipped', 0)} |",
            f"| 可疑 (suspicious) | {test_stats.get('suspicious', 0)} |",
            "",
            f"测试耗时: {stats.get('test_duration_seconds', 'N/A')} 秒",
            "",
        ])

    # 分类统计
    lines.extend([
        "## 二、分类统计",
        "",
        "| 分类 | 书签数 |",
        "|------|--------|",
    ])

    tree = {}
    sorted_cats = sorted(categories.keys())
    for cat in sorted_cats:
        parts = cat.split("/")
        if len(parts) == 1:
            if cat not in tree:
                tree[cat] = {"subcats": {}, "bookmarks": []}
            tree[cat]["bookmarks"] = categories[cat]
        else:
            parent = parts[0]
            sub = parts[1]
            if parent not in tree:
                tree[parent] = {"subcats": {}, "bookmarks": []}
            tree[parent]["subcats"][sub] = categories[cat]

    for parent in sorted(tree.keys()):
        node = tree[parent]
        total = len(node["bookmarks"]) + sum(len(v) for v in node["subcats"].values())
        lines.append(f"| **{parent}** | **{total}** |")
        for sub_name in sorted(node["subcats"].keys()):
            lines.append(f"| &nbsp;&nbsp;{sub_name} | {len(node['subcats'][sub_name])} |")

    lines.append("")

    # 被墙链接列表
    gfw_links = []
    for cat, bms in categories.items():
        for bm in bms:
            if bm.get("test_status") == "blocked_gfw":
                gfw_links.append(bm)

    if gfw_links:
        lines.extend([
            "## 三、被墙/国内无法访问的链接",
            "",
            f"共 {len(gfw_links)} 个（网站本身正常，需翻墙访问）：",
            "",
            "| 名称 | URL |",
            "|------|-----|",
        ])
        for bm in gfw_links:
            name = bm["name"][:50] + "..." if len(bm["name"]) > 50 else bm["name"]
            url = bm["url"][:70] + "..." if len(bm["url"]) > 70 else bm["url"]
            name = name.replace("|", "\\|")
            url = url.replace("|", "\\|")
            lines.append(f"| {name} | {url} |")
        lines.append("")

    # 失效链接列表
    dead_links = []
    for cat, bms in categories.items():
        for bm in bms:
            if bm.get("test_status") == "dead":
                dead_links.append(bm)

    if dead_links:
        lines.extend([
            "## 四、真正失效的链接",
            "",
            f"共 {len(dead_links)} 个失效链接：",
            "",
            "| 名称 | URL | 错误 |",
            "|------|-----|------|",
        ])
        for bm in dead_links:
            name = bm["name"][:40] + "..." if len(bm["name"]) > 40 else bm["name"]
            url = bm["url"][:60] + "..." if len(bm["url"]) > 60 else bm["url"]
            error = (bm.get("test_error") or str(bm.get("http_code", "")))[:30]
            # Escape pipes in markdown table
            name = name.replace("|", "\\|")
            url = url.replace("|", "\\|")
            error = error.replace("|", "\\|")
            lines.append(f"| {name} | {url} | {error} |")
        lines.append("")

    # 可疑链接列表
    suspicious_links = []
    for cat, bms in categories.items():
        for bm in bms:
            if bm.get("test_status") == "suspicious" or bm.get("suspicious"):
                suspicious_links.append(bm)

    if suspicious_links:
        lines.extend([
            "## 五、可疑链接",
            "",
            f"共 {len(suspicious_links)} 个可疑链接（域名指向非预期网站）：",
            "",
            "| 名称 | URL |",
            "|------|-----|",
        ])
        for bm in suspicious_links:
            name = bm["name"].replace("|", "\\|")
            url = bm["url"].replace("|", "\\|")
            lines.append(f"| {name} | {url} |")
        lines.append("")

    lines.append("---")
    lines.append("*本报告由书签整理工具自动生成*")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"  整理报告: {output_path}")


# ============================================================
# 主函数
# ============================================================

def main():
    print("=" * 60)
    print("书签分类整理与输出工具")
    print("=" * 60)

    if not os.path.exists(INPUT_FILE):
        print(f"错误: 未找到输入文件 {INPUT_FILE}")
        print("请先运行 test_links.py")
        sys.exit(1)

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    bookmarks = data["bookmarks"]
    stats = data["stats"]
    total = len(bookmarks)
    print(f"\n共 {total} 个书签待分类")

    # 分类
    print("\n正在分类...")
    categories: dict[str, list[dict]] = {}
    for bm in bookmarks:
        cat = classify_bookmark(bm)
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(bm)

    # 显示分类结果
    print("\n分类结果:")
    for cat in sorted(categories.keys()):
        print(f"  {cat}: {len(categories[cat])} 个")

    # 生成输出
    print("\n正在生成输出文件...")

    html_path = os.path.join(OUTPUT_DIR, "bookmarks_organized.html")
    generate_html(categories, html_path)

    md_path = os.path.join(OUTPUT_DIR, "bookmarks_organized.md")
    generate_markdown(categories, stats, md_path)

    report_path = os.path.join(OUTPUT_DIR, "report.md")
    generate_report(categories, stats, report_path)

    print("\n完成！")
    print(f"  可将 bookmarks_organized.html 导入浏览器")


if __name__ == "__main__":
    main()
