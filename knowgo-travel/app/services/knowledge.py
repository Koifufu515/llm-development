"""本地中文BGE + BM25/RRF；父块引用、城市过滤和有界缓存。"""
import hashlib
import json
import re
from collections import OrderedDict
from pathlib import Path
from time import monotonic
import numpy as np
from rank_bm25 import BM25Okapi
from app.config import PROJECT_ROOT


def tokens(text):
    text=re.sub(r'\s+','',text.lower())
    return [text[i:i+2] for i in range(max(1,len(text)-1))]

class KnowledgeBase:
    def __init__(self, root=None):
        self.root=Path(root or PROJECT_ROOT/'data/guides')
        self.parents=[];self.children=[];self.vectors=None;self.model=None;self.cache=OrderedDict()
        self.version='empty'

    def load(self):
        self.parents=[];self.children=[];self.cache.clear()
        for path in sorted(self.root.glob('*.json')):
            doc=json.loads(path.read_text())
            for i,paragraph in enumerate(re.split(r'\n\s*\n',doc['text'])):
                if len(paragraph.strip())<30:continue
                # 父块最多1200字符，子块256字符、重叠64字符。
                for offset in range(0,len(paragraph),1100):
                    parent_id=hashlib.sha256((doc['source_url']+str(i)+str(offset)).encode()).hexdigest()[:16]
                    parent={'parent_id':parent_id,'city':doc['city'],'title':doc['title'],'source_url':doc['source_url'],
                            'text':paragraph[offset:offset+1200],'license':doc.get('license','source terms')}
                    self.parents.append(parent)
                    for start in range(0,len(parent['text']),192):
                        self.children.append({'parent_id':parent_id,'city':doc['city'],'text':parent['text'][start:start+256]})
        self.version=hashlib.sha256(json.dumps(self.children,ensure_ascii=False).encode()).hexdigest()
        if self.children:
            self.bm25=BM25Okapi([tokens(c['text']) for c in self.children])
            target=PROJECT_ROOT/'data/rag_index'
            target.mkdir(parents=True,exist_ok=True)
            vectorfile=target/(self.version+'.npy')
            if vectorfile.exists():self.vectors=np.load(vectorfile,allow_pickle=False)
            else:
                self.vectors=np.asarray(list(self.embed([c['text'] for c in self.children])))
                np.save(vectorfile,self.vectors,allow_pickle=False)
        return {'parents':len(self.parents),'children':len(self.children),'version':self.version}

    def embed(self,texts):
        if self.model is None:
            from fastembed import TextEmbedding
            self.model=TextEmbedding('BAAI/bge-small-zh-v1.5',cache_dir=str(PROJECT_ROOT/'data/models'),threads=2)
        return self.model.embed(texts)

    def search(self,query,city=None,k=5,rerank=True,use_cache=True):
        k=max(1,min(k,10));key=(self.version,query,city,k,rerank)
        if use_cache and key in self.cache:
            timestamp,result=self.cache[key]
            if monotonic()-timestamp<300:
                self.cache.move_to_end(key)
                return {'status':'ok','cache_hit':True,'results':result}
        if not self.children:return {'status':'empty','cache_hit':False,'results':[]}
        allowed={i for i,c in enumerate(self.children) if city is None or city in c['city']}
        if not allowed:return {'status':'empty','cache_hit':False,'results':[]}
        q=np.asarray(list(self.embed(['为这个句子生成表示以用于检索相关文章：'+query])))[0]
        dense=self.vectors@q
        sparse=self.bm25.get_scores(tokens(query))
        rankings=[sorted(allowed,key=lambda i:scores[i],reverse=True)[:30] for scores in (dense,sparse)]
        scores={}
        for ranking in rankings:
            for rank,index in enumerate(ranking):scores[index]=scores.get(index,0)+1/(60+rank+1)
        selected=sorted(scores,key=scores.get,reverse=True)
        # 明确为词项覆盖率重排，不宣称使用cross-encoder。
        if rerank:
            query_terms=set(tokens(query))
            selected.sort(key=lambda i: (len(query_terms & set(tokens(self.children[i]['text'])))/max(1,len(query_terms))*.02+scores[i]),reverse=True)
        lookup={p['parent_id']:p for p in self.parents};seen=set();result=[]
        for i in selected:
            pid=self.children[i]['parent_id']
            if pid in seen:continue
            seen.add(pid);result.append({**lookup[pid],'score':round(scores[i],6)})
            if len(result)>=k:break
        self.cache[key]=(monotonic(),result)
        while len(self.cache)>128:self.cache.popitem(last=False)
        return {'status':'ok','cache_hit':False,'results':result}
