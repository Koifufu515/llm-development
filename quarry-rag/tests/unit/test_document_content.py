from docx import Document
from quarry.ingest.parsers.docx import DocxParser
from quarry.ingest.parsers.markdown import MarkdownParser
from quarry.ingest.parsers.base import Section
from quarry.ingest.splitter import split

def test_docx_table_is_not_silently_dropped(tmp_path):
 p=tmp_path/'x.docx';d=Document();d.add_heading('差旅',level=1);d.add_paragraph('以下是限额。');t=d.add_table(rows=2,cols=2);t.cell(0,0).text='城市';t.cell(0,1).text='限额';t.cell(1,0).text='苏州';t.cell(1,1).text='300元';d.save(p)
 sections=DocxParser().parse(p);text='\n'.join(s.content for s in sections)
 assert '苏州'in text and '300元'in text and '| --- |'in text
 assert sections==DocxParser().parse(p)

def test_markdown_text_before_heading_is_preserved(tmp_path):
 p=tmp_path/'x.md';p.write_text('前置说明不得丢失。\n\n## 正文\n后续内容。')
 ss=MarkdownParser().parse(p);assert ss[0].content=='前置说明不得丢失。'
 assert all(p.read_text()[s.char_start:s.char_end]==s.content for s in ss)

def test_tilde_code_fence_is_atomic_even_with_empty_lines():
 text='~~~python\n'+('print(1)\n\n'*100)+'~~~';_,children=split(Section([],text,0,len(text)))
 assert len(children)==1 and children[0].content==text

def test_four_backtick_fence_contains_three_backticks():
 text='````text\n```\n'+('x\n\n'*400)+'````';_,children=split(Section([],text,0,len(text)))
 assert len(children)==1 and children[0].content==text
