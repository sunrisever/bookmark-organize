[English](README.md) | 简体中文

# Bookmark Organize

> 浏览器书签整理工具

从 Chrome、Edge 和 HTML 导出文件中合并书签，结合 AI 辅助分类与确定性清洗流程，自动去重、检测死链、整理分类，输出可直接导入浏览器的书签文件。

## 功能

- **多源合并**：Chrome + Edge + HTML 导出书签一键合并
- **智能去重**：URL 标准化（去除追踪参数 utm_/spm 等、统一格式）
- **死链检测**：异步并发测试链接可用性（50 并发，支持代理穿墙）
- **智能分类**：基于域名和关键词的启发式分类（约 20 个类别）
- **多格式输出**：HTML（可导入浏览器）+ Markdown（带状态标记）+ 统计报告
- **AI 编程助手支持**：内置 `CLAUDE.md` 和 `AGENTS.md`，兼容 Claude Code、Codex、OpenCode、OpenClaw

## 安装

```bash
pip install aiohttp
```

## 使用流程

### Step 1：解析合并 — parse_bookmarks.py

```bash
python parse_bookmarks.py
```

从三个来源读取书签并合并去重：
- Chrome 书签：`%LOCALAPPDATA%\Google\Chrome\User Data\Default\Bookmarks`
- Edge 书签：`%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Bookmarks`
- HTML 导出：手动指定文件路径（需修改源码中的路径）

**去重逻辑**：URL 标准化（去除追踪参数、小写域名、去除尾部斜杠）→ 同一 URL 保留首次出现

**输出**：`merged_bookmarks.json`

### Step 2：链接检测 — test_links.py（可选但推荐）

```bash
python test_links.py
```

异步并发测试所有书签链接的可用性。

| 状态 | 含义 |
|------|------|
| `alive` | HTTP 2xx/3xx，正常 |
| `alive_block` | HTTP 4xx，服务器在线但拒绝（反爬/需登录） |
| `blocked_gfw` | 已知被墙域名超时 |
| `dead` | DNS 失败 / 连接错误 / 5xx |
| `skipped` | 特殊协议（edge:// / chrome:// 等） |
| `suspicious` | 已知恶意域名 |

> 需要代理（Clash Verge 运行在 `127.0.0.1:7897`），否则被墙网站会全部超时。

**输出**：`test_results.json`

### Step 3：分类整理 — organize_bookmarks.py

```bash
python organize_bookmarks.py
```

基于域名、书签名、文件夹等启发式规则，将书签分类到约 20 个类别。

**输出**：

| 文件 | 用途 |
|------|------|
| `bookmarks_organized.html` | NETSCAPE 格式，**可直接导入 Chrome/Edge** |
| `bookmarks_organized.md` | Markdown 格式，含链接状态标记 |
| `report.md` | 汇总报告：统计表、分类分布、死链列表 |

## 分类类别（示例）

SJTU 校园、数学、编程学习/C++、编程学习/开发、AI 工具、代理与VPN、图书与文献、壁纸与图片、在线工具、其他...

## 注意事项

- `parse_bookmarks.py` 中 HTML 导入路径需要根据实际情况修改
- `test_links.py` 需要 Clash Verge 运行（代理 `127.0.0.1:7897`）
- 分类规则是启发式的，复杂场景可能分错，建议检查 `report.md`
- 全部使用标准库 + aiohttp，无需 AI API
- 适合定期执行（如每月整理一次书签）

## 开源协议

MIT
