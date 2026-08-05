# anydoc（Dify 插件）

将 Word、PowerPoint、Excel、OpenDocument、RTF、EPUB、CSV、PDF 转换为干净的 GitHub Flavored Markdown。作者：senrylee。

转换在 Dify 的 plugin-daemon 内本地完成，无需额外 API Key。

## 支持格式

| 类型 | 扩展名 |
|------|--------|
| Word | `.doc` `.docx` `.docm` |
| PowerPoint | `.ppt` `.pps` `.pot` `.pptx` `.pptm` `.ppsx` `.ppsm` |
| Excel | `.xls` `.xlsx` `.xlsm` `.xlsb` |
| OpenDocument | `.odt` `.ods` `.odp` |
| 其他 | `.rtf` `.epub` `.csv` `.pdf` |

说明：纯扫描件 / 纯图片 PDF 需要 OCR，本插件不做 OCR，这类文件会转换失败。

## 安装

1. 打包插件（在本目录的上一级执行）：

```bash
dify plugin package ./dify-plugin-anydoc
```

得到 `anydoc.difypkg`（或同名包）后，在 Dify：**插件 → 安装插件 → 本地文件**，上传安装。

2. 也可在开发期用远程调试：复制 `.env.example` 为 `.env`，填入 Dify 插件调试地址与 Key，然后：

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m main
```

安装时 Dify 会按 `requirements.txt` 拉取运行依赖；服务器需能访问 PyPI，或使用已打好依赖的离线包。常见 Linux Docker（amd64 / arm64）即可，无需在服务器上安装 Rust 工具链。

## 在工作流中使用

1. 在 Start 节点开启文件上传，拿到文件变量。
2. 添加 **anydoc → Convert to Markdown** 工具节点。
3. 将文件变量接到 `files` 参数。
4. 下游使用工具输出的 `text`（Markdown 正文）或 `json` / 自定义变量（`results` 等）。

建议优先在 **Workflow / Chatflow** 中使用；Agent 对 `files` 参数的支持较弱。

## 输出

- `text`：转换后的 Markdown（多文件时按文件分段拼接）
- `json`：含 `status`、`total_files`、`successful_conversions`、`results`
- 变量：`status`、`total_files`、`successful_conversions`、`results`
- 同时返回 `text/markdown` 的 blob，便于当作文件继续传递

## 目录结构

```text
dify-plugin-anydoc/
├── manifest.yaml
├── main.py
├── requirements.txt
├── PRIVACY.md
├── README.md
├── _assets/icon.svg
├── provider/
│   ├── anydoc.yaml
│   └── anydoc.py
└── tools/
    ├── convert_to_markdown.yaml
    └── convert_to_markdown.py
```
