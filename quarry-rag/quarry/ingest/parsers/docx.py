"""B 档：docx 解析。用 python-docx 抽出标题与段落。"""
from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.text.paragraph import Paragraph
from docx.table import Table

from quarry.ingest.parsers.base import Section

class DocxParser:
    tier = "B"

    def can_parse(self, source_uri: str) -> bool:
        return source_uri.lower().endswith(".docx")

    def parse(self, path: Path) -> list[Section]:
        doc = Document(str(path))

        # 先把整份文档拍平成一条文本流，同时记下每个段落在流里的位置。
        # 这样 char_start / char_end 有一个明确的参照系，而且两次解析结果相同。
        flat: list[str] = []
        items: list[tuple[int, int, int, str]] = []   # (层级, 起, 止, 文字)
        cursor = 0
        for para in doc.iter_inner_content():
            # 表格必须按文档顺序保留；后续切分器将连续Markdown表格行作为原子块。
            text = _table_text(para) if isinstance(para, Table) else para.text.strip()
            if not text:
                continue
            start = cursor
            flat.append(text)
            cursor += len(text) + 1                  # +1 是拼接时的换行
            items.append((0 if isinstance(para, Table) else _heading_level(para), start, start + len(text), text))

        full = "\n".join(flat)

        sections: list[Section] = []
        stack: list[tuple[int, str]] = []
        body_start: int | None = None
        body_end = 0

        def flush() -> None:
            nonlocal body_start
            if body_start is not None and body_end > body_start:
                sections.append(Section(
                    heading_path=[t for _, t in stack],
                    content=full[body_start:body_end],
                    char_start=body_start,
                    char_end=body_end,
                ))
            body_start = None

        for level, start, end, text in items:
            if level > 0:
                flush()
                while stack and stack[-1][0] >= level:
                    stack.pop()
                stack.append((level, text))
            else:
                if body_start is None:
                    body_start = start
                body_end = end

        flush()
        return sections

def _heading_level(para: Paragraph) -> int:
    """从段落样式判断标题层级，0 表示不是标题。"""
    style = para.style.name if para.style else ""
    if style.startswith("Heading "):
        try:
            return int(style.split()[1])
        except (IndexError, ValueError):
            return 0
    return 0


def _table_text(table: Table) -> str:
    rows = [[cell.text.strip().replace("|", "\\|").replace("\n", "<br>") for cell in row.cells] for row in table.rows]
    if not rows:
        return ""
    width = max(len(row) for row in rows)
    lines = ["| " + " | ".join(row + [""] * (width - len(row))) + " |" for row in rows]
    lines.insert(1, "| " + " | ".join(["---"] * width) + " |")
    return "\n".join(lines)
