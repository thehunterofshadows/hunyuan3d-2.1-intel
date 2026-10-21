import sys,os,json
from pathlib import Path
sys.path.insert(0,'/app')
from review_note import review
import importlib.util
spec=importlib.util.spec_from_file_location('api','/tests/notes-api.py');api=importlib.util.module_from_spec(spec);spec.loader.exec_module(api)
path=next(Path('/data').glob('workspace-*.json'))
assert api.request('?model=api-check')[1]['notes'][0]['reviewed'] is False
# Legacy note: missing reviewed is treated as not reviewed.
doc=json.loads(path.read_text());doc['notes'][0].pop('reviewed');path.write_text(json.dumps(doc))
review(path,'api-check','cad:test',2,'Checked dimensions; no geometry changes needed.')
n=api.request('?model=api-check')[1]['notes'][0]
assert n['reviewed'] is True and n['revision']==3 and n['text']=='Updated annotation'
assert api.request(body={**api.note,'expectedRevision':2,'text':'Stale browser edit'})[0]==409
try:review(path,'api-check','cad:test',2,'Old review')
except ValueError:pass
else:raise AssertionError('Stale agent revision accepted')
r,new=api.request(body={**api.note,'expectedRevision':3,'text':'Follow-up question'})
assert r==200 and new['note']['reviewed'] is False
assert new['note']['history'][0]['text']=='Updated annotation'
assert new['note']['history'][0]['reviewResponse'].startswith('Checked dimensions')
review(path,'api-check','cad:test',4,'Answered follow-up')
r,new=api.request(body={**api.note,'expectedRevision':5,'text':'Third question'})
assert r==200 and len(new['note']['history'])==2
assert new['note']['history'][1]['text']=='Follow-up question'
assert new['note']['text']=='Third question' and not new['note']['reviewed']
assert 'Answered follow-up' in path.with_suffix('.md').read_text()
print('PASS: legacy defaults; agent review; stale agent/browser conflicts; two review cycles; preserved text, metadata and history; Markdown sync')
