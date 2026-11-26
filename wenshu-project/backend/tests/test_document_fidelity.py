from app.pipeline.parser import DocumentParser,ParsedDocument,Block
from app.pipeline.chunker import Chunker

def test_markdown_fenced_headers_are_not_document_headings(tmp_path):
 p=tmp_path/'x.md';p.write_text('# 条款\n\n```python\n# 注释不能变标题\nprint(1)\n```\n\n真实正文')
 d=DocumentParser().parse(p)
 assert [x.text for x in d.blocks if x.type=='heading']==['条款']
 assert any(x.type=='code'and '# 注释' in x.text for x in d.blocks)

def test_markdown_table_preserved_as_one_structural_block(tmp_path):
 p=tmp_path/'x.md';p.write_text('# 标准\n\n| 类型 | 金额 |\n|---|---|\n| 学生 | 100 |\n| 教师 | 200 |\n')
 d=DocumentParser().parse(p);assert any(b.type=='table'and '学生' in b.text and '教师' in b.text for b in d.blocks)

def test_large_atomic_table_not_sliced_mid_row():
 table='| 类型 | 内容 |\n'+'\n'.join(f'| 第{i}项 | '+'详细说明'*20+' |'for i in range(20))
 d=ParsedDocument('规则',[Block('heading',1,'第一章 申请'),Block('table',0,table)])
 chunks=Chunker().chunk(d)
 assert any(table in c['content']for c in chunks)
 assert any(c['metadata'].get('oversized_atomic')for c in chunks)

def test_html_ignores_script_and_nested_duplicate_paragraphs(tmp_path):
 p=tmp_path/'x.html';p.write_text('<h1>规则</h1><script>不要执行</script><table><tr><td><p>唯一表格值</p></td></tr></table>')
 d=DocumentParser().parse(p)
 assert sum(b.text.count('唯一表格值')for b in d.blocks)==1

def test_blank_pdf_page_uses_local_ocr(tmp_path,monkeypatch):
 from pypdf import PdfWriter
 import app.pipeline.ocr as ocr
 p=tmp_path/'scan.pdf';writer=PdfWriter();writer.add_blank_page(width=300,height=300)
 with p.open('wb')as f:writer.write(f)
 monkeypatch.setattr(ocr,'ocr_page',lambda path,index:'第一条 申请材料须于第八周提交。')
 d=DocumentParser().parse(p)
 assert '第八周'in d.text and d.meta['ocr_pages']==[1]

def test_new_chunk_uses_its_own_page_not_previous_buffer_page():
 blocks=[Block('paragraph',0,'甲'*300,page=1),Block('paragraph',0,'乙'*300,page=2)]
 c=Chunker(min_chars=200,max_chars=400).chunk(ParsedDocument('规则',blocks))
 assert [x['metadata']['page']for x in c]==[1,2]

def test_code_indentation_and_large_atomic_block_preserved():
 from app.pipeline.cleaner import TextCleaner
 from app.pipeline.chunker import Chunker
 from app.pipeline.parser import ParsedDocument,Block
 code='def example():\n    return "１２３"\n'+'    # comment\n'*100
 doc=ParsedDocument(title='code',blocks=[Block(type='code',level=0,text=code)])
 doc=TextCleaner().clean(doc)
 chunks=Chunker().chunk(doc)
 assert len(chunks)==1 and '    return "１２３"'in chunks[0]['content']
 assert chunks[0]['metadata']['has_code']and chunks[0]['metadata']['oversized_atomic']

def test_cleaning_preserves_security_marks_and_short_facts():
 from app.pipeline.cleaner import TextCleaner
 from app.pipeline.parser import ParsedDocument,Block
 doc=ParsedDocument(title='text',blocks=[Block(type='paragraph',level=0,text=t)for t in ['内部资料','严禁外传','无','10']])
 assert len(TextCleaner().clean(doc).blocks)==4

def test_heading_sentence_is_present_in_retrievable_body():
 from app.pipeline.chunker import Chunker
 from app.pipeline.parser import ParsedDocument,Block
 doc=ParsedDocument(title='t',blocks=[Block(type='heading',level=1,text='二、非必要不外出，杜绝涉水拍照。'),Block(type='paragraph',level=0,text='注意避险。')])
 assert '杜绝涉水拍照' in '\n'.join(c['content']for c in Chunker().chunk(doc))
