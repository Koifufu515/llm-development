"""模型出站文本脱敏。原始事实保留本机，映射文件不得进日志或交付包。"""
from __future__ import annotations
import json,re,os
from functools import lru_cache
from pathlib import Path

@lru_cache(maxsize=4)
def _mapping(path: str):
 if not path:return {}
 p=Path(path)
 if not p.is_file():raise RuntimeError('配置的出站脱敏映射不存在，拒绝发送')
 return json.loads(p.read_text())

def redact(text: str, mapping: dict | None = None) -> str:
 from app.config import get_settings
 settings=get_settings()
 if not settings.model_egress_allowed:raise RuntimeError('模型出站未获授权')
 path=os.getenv('PRIVACY_REDACTION_FILE','')or settings.privacy_redaction_file
 replacements=_mapping(path)if mapping is None else mapping
 for source,target in sorted(replacements.items(),key=lambda item:len(item[0]),reverse=True):
  text=text.replace(source,target)
 text=re.sub(r'(?<!\w)[A-Za-z]{1,5}\d{6,12}(?!\w)','【学号】',text)
 text=re.sub(r'(?<!\d)\d{17}[\dXx](?!\d)','【身份证号】',text)
 text=re.sub(r'(?<!\d)1[3-9]\d{9}(?!\d)','【手机号】',text)
 text=re.sub(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}','【邮箱】',text)
 return text
