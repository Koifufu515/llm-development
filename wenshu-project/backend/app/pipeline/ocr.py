"""本机扫描页OCR：PDFium渲染+Tesseract；原文档不会发送外部OCR服务。"""
from __future__ import annotations
import os,shutil,subprocess,tempfile
from pathlib import Path

def ocr_page(path:Path,page_index:int)->str:
 import pypdfium2 as pdfium
 if not shutil.which('tesseract'):raise RuntimeError('扫描页需要本机Tesseract OCR；禁止把空文本标为入库成功')
 with tempfile.TemporaryDirectory(prefix='wenshu-ocr-')as tmp:
  pdf=pdfium.PdfDocument(str(path));page=pdf[page_index];bitmap=page.render(scale=2.5)
  image=Path(tmp)/'page.png';bitmap.to_pil().save(image)
  bitmap.close();page.close();pdf.close()
  command=['tesseract',str(image),'stdout','-l',os.getenv('OCR_LANGUAGES','chi_sim+eng'),'--psm','3']
  if os.getenv('TESSDATA_PREFIX'):command+=['--tessdata-dir',os.environ['TESSDATA_PREFIX']]
  result=subprocess.run(command,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=120)
  if result.returncode:raise RuntimeError('本机OCR失败：'+result.stderr[:200])
  return result.stdout.strip()
