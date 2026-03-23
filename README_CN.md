[English](README.md) | 简体中文

# Bookmark Organize

> 先在本地完成书签合并、去重、链接检查和整理，再可选地交给 ChatGPT / Claude / Gemini / Codex 做最后的分类复核。

这里也先把原理说清楚：

- 浏览器书签本身并没有一套真正成熟、强力的内置 AI 分类工作流
- 这个项目也不是必须依赖 LLM API 才能使用
- 默认工作流是本地、确定性、可复核的

AI 在这里是可选增强层，不是前置条件。

它真正的价值是：

1. 合并多来源书签
2. 标准化 URL 并去重
3. 检查死链和可疑链接
4. 生成可重新导入浏览器的结果
5. 最后可选地交给强模型做结构复核

## 要不要 API Key？

不需要。

这个项目在没有任何 LLM API Key 的情况下也能完整使用。  
如果你想把最终结果再优化一遍，才建议把结果文件交给 ChatGPT / Claude / Gemini / Codex 做辅助复核。

## 零基础最快上手

### Step 1：安装依赖

```bash
pip install aiohttp
```

### Step 2：合并书签

```bash
python parse_bookmarks.py
```

跑完后你会得到：

- `merged_bookmarks.json`

### Step 3：可选检查链接

```bash
python test_links.py
```

跑完后你会得到：

- `test_results.json`

### Step 4：整理书签

```bash
python organize_bookmarks.py
```

跑完后你会得到：

- `bookmarks_organized.html`
- `bookmarks_organized.md`
- `report.md`

## 像看截图一样的使用流程

### 第一步，你先跑什么

```bash
python parse_bookmarks.py
```

你可以把这一阶段理解成“第一张截图应该看到的是”：

- Chrome、Edge、HTML 导出的书签已经合并
- 重复项已经按 URL 标准化逻辑折叠
- 浏览器里还没有真正导入任何新结果

### 第二步，你再跑什么

```bash
python test_links.py
```

这一步不是强制，但如果你的书签积累很久了，很值得跑。

### 第三步，你最后跑什么

```bash
python organize_bookmarks.py
```

这时你会得到三份关键结果：

- 可重新导入浏览器的 HTML
- 可读的 Markdown 树
- 一份汇总报告

### 第四步，如果你想让 AI 帮你复核，交什么给它

建议交：

- `bookmarks_organized.md`
- `report.md`

可以直接问：

- 哪些分类太宽？
- 哪些书签看起来放错地方？
- 哪些可疑链接应该删掉？
- 目录树还能怎么简化？

### 第五步，真正导回浏览器的是哪个文件

真正拿去浏览器导入的是：

- `bookmarks_organized.html`

这才是最终浏览器可用的产物。

## 为什么它不是 API-first

这个仓库的设计取向就是保守和稳定：

- 重要工作由本地脚本完成
- AI 只负责最后的复核和优化
- 你不需要先解决 API 账号、额度、账单问题

## 重要文件

| 文件 | 作用 |
| --- | --- |
| `parse_bookmarks.py` | 合并并去重多个来源 |
| `test_links.py` | 检查链接可用性和可疑站点 |
| `organize_bookmarks.py` | 最终分类整理与导出 |
| `merged_bookmarks.json` | 合并后的书签数据 |
| `test_results.json` | 链接检查结果 |
| `bookmarks_organized.html` | 浏览器可导入结果 |
| `bookmarks_organized.md` | 可读复核结果 |
| `report.md` | 汇总报告 |

## 开源协议

MIT
