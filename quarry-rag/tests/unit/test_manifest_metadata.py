import json
from quarry.scripts import ingest_corpus

def test_macos_metadata_not_parsed_as_a_manifest(tmp_path,monkeypatch):
 folder=tmp_path/'_manifest';folder.mkdir()
 (folder/'wiki.jsonl').write_text(json.dumps({'source_uri':'travel-guide/a.md','title':'城市'}))
 (folder/'._wiki.jsonl').write_bytes(b'\x00\x05\x16\x07\xa3metadata')
 monkeypatch.setattr(ingest_corpus,'CORPUS_ROOT',tmp_path)
 assert ingest_corpus.load_manifest()['travel-guide/a.md']['title']=='城市'
