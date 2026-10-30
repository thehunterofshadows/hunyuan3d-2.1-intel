from pathlib import Path
from collections import Counter
import struct,json
root=Path(__file__).resolve().parent/'exports'
rows=[]
for p in sorted(root.rglob('*.stl')):
 data=p.read_bytes();n=struct.unpack_from('<I',data,80)[0]
 assert len(data)==84+50*n,(p,'unexpected STL format')
 edges=Counter();degenerate=0;volume=0
 for i in range(n):
  f=struct.unpack_from('<12fH',data,84+i*50)
  v=[tuple(round(c,5) for c in f[j:j+3]) for j in [3,6,9]]
  if len(set(v))<3:degenerate+=1
  for a,b in [(v[0],v[1]),(v[1],v[2]),(v[2],v[0])]:edges[tuple(sorted((a,b)))]+=1
 bad=sum(c!=2 for c in edges.values())
 rows.append({'file':str(p.relative_to(root)),'triangles':n,'nonmanifold_edges':bad,'degenerate_facets':degenerate})
assert all(r['nonmanifold_edges']==0 and r['degenerate_facets']==0 for r in rows),[r for r in rows if r['nonmanifold_edges'] or r['degenerate_facets']]
(root/'stl_mesh_checks.json').write_text(json.dumps(rows,indent=2))
print(f'{len(rows)} STL meshes: closed edges, no degenerate facets.')
