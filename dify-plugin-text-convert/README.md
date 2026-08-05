# 文本转化（Dify 插件）

在 Dify 插件运行环境内，将办公文档**本地、快速**转换为干净的 GitHub Flavored Markdown。作者：senrylee。

无需 API Key；转换在 plugin-daemon 内完成。

## 能力说明

- **速度快**：常见文档转换耗时通常在数毫秒级，适合工作流里频繁处理上传文件。
- **格式统一**：多种输入格式都会产出结构一致的 Markdown（标题、列表、表格等）。
- **本地处理**：文件不发往外部第三方转换服务。

## 支持格式

| 类型 | 扩展名 |
|------|--------|
| Word | `.doc` `.docx` `.docm` |
| PowerPoint | `.ppt` `.pps` `.pot` `.pptx` `.pptm` `.ppsx` `.ppsm` |
| Excel | `.xls` `.xlsx` `.xlsm` `.xlsb` |
| OpenDocument | `.odt` `.ods` `.odp` |
| 其他 | `.rtf` `.epub` `.csv` |
| PDF | 带文字层的 `.pdf` |

## 限制

- **扫描件 / 纯图片 PDF 不支持**：本工具**无 OCR**，无法识别图片中的文字；这类 PDF 会转换失败。
- 请优先使用带可选中文字的 PDF，或其他上表支持的办公格式。

## 安装

1. 打包插件（在本目录的上一级执行）：

```bash
dify plugin package ./dify-plugin-text-convert
```

得到 `.difypkg` 后，在 Dify：**插件 → 安装插件 → 本地文件**，上传安装。

2. 开发期远程调试：复制 `.env.example` 为 `.env`，填入调试地址与 Key，然后：

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m main
```

安装时 Dify 会按 `requirements.txt` 拉取运行依赖；服务器需能访问 PyPI，或使用已打好依赖的离线包。常见 Linux Docker（amd64 / arm64）即可，无需在服务器上安装 Rust 工具链。

## 在工作流中使用

1. 在 Start 节点开启文件上传，拿到文件变量。
2. 添加 **文本转化** 工具节点。
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
dify-plugin-text-convert/
├── manifest.yaml
├── main.py
├── requirements.txt
├── PRIVACY.md
├── README.md
├── _assets/icon.svg
├── provider/
│   ├── text_convert.yaml
│   └── text_convert.py
└── tools/
    ├── text_convert.yaml
    └── text_convert.py
```
