import sys,json,hashlib
from pathlib import Path
p=Path(sys.argv[1]);m=json.loads(p.read_text())
assert m['input']!=m['output']
for key,sha in [('input','input_sha256'),('output','output_sha256')]:
 f=Path(m[key]); f=Path(str(f).replace('/work/','',1)) if str(f).startswith('/work/') else f
 assert f.is_file()
 assert hashlib.sha256(f.read_bytes()).hexdigest()==m[sha]
assert Path(m['output'].replace('/work/','',1)).open('rb').read(4)==b'glTF'
assert m['processed']['triangles']==m['reimport']['triangles']>0
for shot in ('side','opposite','top','underside','muzzle','fp'):
 assert (p.parent/(shot+'-actual-model.png')).stat().st_size>1000
print('VALIDATED',m['output'],m['reimport']['triangles'],'triangles')
