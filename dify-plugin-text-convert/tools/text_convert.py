from __future__ import annotations

from collections.abc import Generator
from typing import Any

import anydoc
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


def _file_extension(file: Any) -> str:
    extension = getattr(file, "extension", None) or ""
    extension = str(extension).lstrip(".").lower()
    if extension:
        return extension

    filename = getattr(file, "filename", None) or ""
    if "." in filename:
        return filename.rsplit(".", 1)[-1].lower()
    return ""


def _resolve_format(data: bytes, extension: str) -> str | None:
    detected = anydoc.format_from_bytes(data)
    if detected:
        return detected
    if extension:
        return anydoc.format_from_extension(extension)
    return None


def _read_blob(file: Any) -> bytes:
    blob = getattr(file, "blob", None)
    if blob is None:
        raise ValueError("file content is empty or unavailable")
    if isinstance(blob, memoryview):
        return blob.tobytes()
    if isinstance(blob, bytearray):
        return bytes(blob)
    if isinstance(blob, bytes):
        return blob
    raise ValueError("unsupported file blob type")


def _friendly_error(exc: BaseException, *, fmt: str | None, extension: str) -> str:
    message = str(exc)
    is_pdf = (fmt == "pdf") or (extension == "pdf")
    lowered = message.lower()
    if is_pdf and any(
        token in lowered
        for token in ("unsupported", "ocr", "image", "scan", "no text", "empty")
    ):
        return (
            f"{message}. "
            "Scanned or image-only PDFs are not supported (this tool has no OCR)."
        )
    return message


class TextConvertTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        files = tool_parameters.get("files") or []
        if not isinstance(files, list):
            files = [files]

        if not files:
            yield self.create_text_message("No files provided")
            yield self.create_json_message(
                {
                    "status": "error",
                    "total_files": 0,
                    "successful_conversions": 0,
                    "results": [],
                    "message": "No files provided",
                }
            )
            yield self.create_variable_message("status", "error")
            yield self.create_variable_message("total_files", 0)
            yield self.create_variable_message("successful_conversions", 0)
            yield self.create_variable_message("results", [])
            return

        successes: list[dict[str, Any]] = []
        results: list[dict[str, Any]] = []

        for file in files:
            filename = getattr(file, "filename", None) or "unnamed"
            extension = _file_extension(file)
            fmt: str | None = None

            try:
                data = _read_blob(file)
                fmt = _resolve_format(data, extension)
                if fmt is None:
                    raise ValueError(
                        "unrecognized file format; supported extensions include "
                        "doc/docx/ppt/pptx/xls/xlsx/odt/ods/odp/rtf/epub/csv/pdf"
                    )

                markdown = anydoc.to_markdown_bytes(data, fmt)
                item = {
                    "filename": filename,
                    "format": fmt,
                    "markdown": markdown,
                    "status": "success",
                }
                successes.append(item)
                results.append(item)

                yield self.create_blob_message(
                    markdown.encode("utf-8"),
                    meta={
                        "mime_type": "text/markdown",
                        "filename": f"{filename.rsplit('.', 1)[0]}.md"
                        if "." in filename
                        else f"{filename}.md",
                    },
                )
            except Exception as exc:  # noqa: BLE001 - surface conversion failures to Dify
                detail = _friendly_error(exc, fmt=fmt, extension=extension)
                error_msg = f"Error converting {filename}: {detail}"
                yield self.create_text_message(error_msg)
                results.append(
                    {
                        "filename": filename,
                        "format": fmt or extension or "",
                        "status": "error",
                        "error": detail,
                    }
                )

        status = "success" if successes else "error"
        payload = {
            "status": status,
            "total_files": len(files),
            "successful_conversions": len(successes),
            "results": results,
        }
        yield self.create_json_message(payload)
        yield self.create_variable_message("status", status)
        yield self.create_variable_message("total_files", len(files))
        yield self.create_variable_message("successful_conversions", len(successes))
        yield self.create_variable_message("results", results)

        if not successes:
            yield self.create_text_message("No files were successfully converted")
        elif len(successes) == 1:
            yield self.create_text_message(successes[0]["markdown"])
        else:
            parts: list[str] = []
            for index, item in enumerate(successes, start=1):
                parts.append("=" * 50)
                parts.append(f"File {index}: {item['filename']}")
                parts.append("=" * 50)
                parts.append("")
                parts.append(item["markdown"])
                parts.append("")
            yield self.create_text_message("\n".join(parts).strip())
