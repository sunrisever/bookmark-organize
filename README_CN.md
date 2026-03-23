[English](README.md) | 简体中文

# Bookmark Organize

> 导出浏览器书签，先在本地完成合并、去重、检查与整理，再可选地交给 ChatGPT / Claude / Gemini / Codex 等通用大模型优化分类方案。

这个项目适合那些书签来源很多、已经积累得很乱的人。它**不是**一个必须绑定 LLM API 才能工作的仓库。默认工作流是本地、确定性的。AI 只是一个可选增强层，最适合拿来做分类方案优化、可疑项复核、或者帮助你重新梳理目录结构。

## 这个项目本质上是做什么的

它帮你完成这几件事：

1. 把 Chrome、Edge、HTML 导出里的书签合并起来
2. 用 URL 标准化做去重
3. 检查死链、可疑链接和被墙链接
4. 重新整理分类结构
5. 输出浏览器可以重新导入的结果

所以和另外几个项目相比，它其实更偏“本地确定性整理工具”而不是“AI 主导项目”：

- 核心工作由本地脚本完成
- AI 只是额外增强层
- 正常使用不需要 API Key

## 要不要 API Key？

**不需要。**

这个项目完全可以在没有任何 LLM API Key 的情况下正常使用。

如果你想进一步优化结果，也可以把导出的 Markdown 报告交给：

- ChatGPT
- Claude
- Gemini
- Codex
- Claude Code
- OpenCode

让它帮你看分类是否合理、哪些链接可疑、目录结构还能怎么优化。但这一步是可选增强，不是前置条件。

## 适合谁用

如果你有这些需求，这个项目就很适合：

- Chrome、Edge、旧 HTML 导出里都有书签
- 想得到一个更干净、可重新导入浏览器的书签树
- 不想把死链和垃圾书签一直堆着不管
- 想要比“手工拖文件夹”更强的整理工作流

## 小白使用流程

### 1. 安装依赖

```bash
pip install aiohttp
```

只有 `test_links.py` 依赖 `aiohttp`，其他步骤大多是标准库。

### 2. 合并书签

```bash
python parse_bookmarks.py
```

它会从这些来源读取：

- Chrome 默认配置文件
- Edge 默认配置文件
- 你手动指定的 HTML 导出文件

主要输出：

- `merged_bookmarks.json`

### 3. 可选：检测链接

```bash
python test_links.py
```

它会检查链接是正常、被拒绝、已失效、可疑，还是特殊协议。

主要输出：

- `test_results.json`

### 4. 整理书签

```bash
python organize_bookmarks.py
```

主要输出：

- `bookmarks_organized.html` —— 可重新导入浏览器
- `bookmarks_organized.md` —— 可读性更好的 Markdown 结果
- `report.md` —— 统计和复核报告

## 推荐的 AI 复核方式

这个仓库本身不依赖 AI，但在“最后复核”阶段很适合配合强模型一起用。

实用流程是：

1. 先跑本地脚本
2. 打开 `bookmarks_organized.md` 或 `report.md`
3. 把它交给 ChatGPT / Claude / Gemini / Codex / Claude Code / OpenCode
4. 问它：
   - 哪些分类太宽了？
   - 哪些书签可能放错了？
   - 哪些可疑链接应该删掉？
   - 目录树还能怎么简化？

然后你再回到本地脚本规则或人工结果里做调整。

## 为什么它比“纯 AI 书签整理”更稳

纯 AI 整理经常有这些问题：

- 不会认真处理死链
- 识别不出只是带追踪参数的重复 URL
- 看起来分类挺漂亮，但导入结构不好用
- 下次再整理时很难复现

这个项目的优势在于，它先把基础层做成确定性的：

- 合并
- 标准化
- 去重
- 链接检测
- 导出

然后 AI 只作为附加增强层，而不是唯一依据。

## 重要文件

| 文件 | 作用 |
| --- | --- |
| `parse_bookmarks.py` | 合并并去重多个书签来源 |
| `test_links.py` | 检测链接状态与可疑站点 |
| `organize_bookmarks.py` | 最终分类整理与导出 |
| `merged_bookmarks.json` | 合并后的书签数据 |
| `test_results.json` | 链接检测结果 |
| `bookmarks_organized.html` | 可重新导入浏览器的输出 |
| `bookmarks_organized.md` | 可读性更好的 Markdown 输出 |
| `report.md` | 汇总与复核报告 |

## 注意事项

- `parse_bookmarks.py` 里 HTML 导入路径可能需要根据你自己的电脑修改
- `test_links.py` 最好在 Clash Verge 或其他代理可用时运行，这样被墙站点的判断更准确
- 分类本身仍然是启发式的，所以最好做一次复核
- 这个工具很适合定期整理，比如每月或每季度跑一次

## AI 编程助手支持

仓库内包含：

- `AGENTS.md`
- `CLAUDE.md`

所以很适合接入 Codex、Claude Code、OpenCode、OpenClaw 这类 agent 工作流。

## 开源协议

MIT
