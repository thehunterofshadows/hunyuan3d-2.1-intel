from pathlib import Path
from collections import Counter
import struct,json,math
root=Path(__file__).resolve().parent/'exports'
rows=[]
for p in sorted(root.rglob('*.stl')):
 data=p.read_bytes();n=struct.unpack_from('<I',data,80)[0]
 assert len(data)==84+50*n,(p,'unexpected STL format')
 edges=Counter();directions=Counter();degenerate=0;volume=0;parent={};coords=[]
 def find(a):
  parent.setdefault(a,a)
  while parent[a]!=a:
   parent[a]=parent[parent[a]];a=parent[a]
  return a
 def join(a,b):
  a=find(a);b=find(b)
  if a!=b:parent[b]=a
 for i in range(n):
  f=struct.unpack_from('<12fH',data,84+i*50)
  raw=[tuple(f[j:j+3]) for j in [3,6,9]]
  coords.extend(raw);v=[tuple(round(c,5) for c in a) for a in raw]
  a,b,c=raw
  u=[b[j]-a[j] for j in range(3)];w=[c[j]-a[j] for j in range(3)]
  cross=[u[1]*w[2]-u[2]*w[1],u[2]*w[0]-u[0]*w[2],u[0]*w[1]-u[1]*w[0]]
  if len(set(v))<3 or sum(x*x for x in cross)<1e-18:degenerate+=1
  volume+=(a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6
  for a,b in [(v[0],v[1]),(v[1],v[2]),(v[2],v[0])]:
   edge=tuple(sorted((a,b)));edges[edge]+=1;directions[edge]+=1 if a<=b else -1;join(a,b)
 bad=sum(c!=2 for c in edges.values());winding=sum(c!=0 for c in directions.values())
 components=len({find(v) for v in parent})
 minimum=[min(v[j] for v in coords) for j in range(3)];maximum=[max(v[j] for v in coords) for j in range(3)]
 bed_ok=abs(minimum[2])<=1e-5 and all(x>=-1e-5 for x in minimum)
 rows.append({'file':str(p.relative_to(root)),'triangles':n,'nonmanifold_edges':bad,'inconsistent_winding_edges':winding,'degenerate_facets':degenerate,'connected_shells':components,'signed_volume_mm3':round(volume,6),'vertex_min_mm':minimum,'vertex_max_mm':maximum,'print_bed_placement_passed':bed_ok})
assert len(rows)==101,len(rows)
assert all(r['nonmanifold_edges']==0 and r['degenerate_facets']==0 and r['inconsistent_winding_edges']==0 and r['connected_shells']==1 and r['signed_volume_mm3']>0 and r['print_bed_placement_passed'] for r in rows),[r for r in rows if r['nonmanifold_edges'] or r['degenerate_facets'] or r['inconsistent_winding_edges'] or r['connected_shells']!=1 or r['signed_volume_mm3']<=0 or not r['print_bed_placement_passed']]
(root/'stl_mesh_checks.json').write_text(json.dumps(rows,indent=2))
print(f'{len(rows)} STL meshes: closed manifold edges, consistent winding, one positive-volume shell, no degenerate facets, and print-bed placement verified.')
