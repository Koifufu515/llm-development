from docx import Document
from quarry.ingest.parsers.markdown import MarkdownParser
from quarry.ingest.parsers.docx import DocxParser

def test_markdown_fenced_code_heading_does_not_become_section(tmp_path):
    text='# 文档\n\n## 示例\n\n下面代码应保留完整。\n\n```python\n# 内部注释\nprint(1)\n```\n\n## 后续\n\n正文。\n';p=tmp_path/'a.md';p.write_text(text)
    sections=MarkdownParser().parse(p)
    assert len(sections)==2
    assert '# 内部注释' in sections[0].content
    assert sections[0].content.count('```')==2
    assert all(text[s.char_start:s.char_end]==s.content for s in sections)

def test_docx_without_headings_keeps_body(tmp_path):
    p=tmp_path/'a.docx';doc=Document();doc.add_paragraph('没有标题也必须保留。');doc.save(p)
    sections=DocxParser().parse(p)
    assert len(sections)==1
    assert sections[0].content=='没有标题也必须保留。'
