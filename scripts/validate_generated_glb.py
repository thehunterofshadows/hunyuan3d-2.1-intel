"""Check exported mesh data and embedded PBR maps, independent of generation."""
import argparse
import json
from pathlib import Path
import numpy as np
import trimesh
p=argparse.ArgumentParser()
p.add_argument("mesh")
p.add_argument("--require-pbr",action="store_true")
p.add_argument("--output",required=True)
a=p.parse_args()
scene=trimesh.load(a.mesh,force="scene",process=False)
assert scene.geometry,"No geometry exported"
report={"file":Path(a.mesh).name,"geometry":[]}
for name,mesh in scene.geometry.items():
 assert len(mesh.vertices)>0 and len(mesh.faces)>0
 assert np.isfinite(mesh.vertices).all(),"Nonfinite vertex positions"
 assert mesh.faces.min()>=0 and mesh.faces.max()<len(mesh.vertices)
 assert np.all(mesh.extents>0),"Degenerate geometry bounds"
 item={"name":name,"vertices":len(mesh.vertices),"triangles":len(mesh.faces),"extents":mesh.extents.tolist(),"watertight":bool(mesh.is_watertight)}
 if a.require_pbr:
  assert mesh.visual.kind=="texture","Missing texture coordinates"
  assert np.isfinite(mesh.visual.uv).all()
  mat=mesh.visual.material
  item["maps"]={}
  for field in ("baseColorTexture","metallicRoughnessTexture"):
   image=getattr(mat,field,None)
   assert image is not None,f"Missing embedded {field}"
   pixels=np.asarray(image)
   assert pixels.ndim==3 and pixels.shape[2]>=3
   item["maps"][field]={"width":image.width,"height":image.height,"rgb_std":pixels[:,:,:3].std(axis=(0,1)).tolist()}
   if field=="baseColorTexture":assert pixels[:,:,:3].std()>1,"Flat/empty base color map"
 report["geometry"].append(item)
report["status"]="passed_structural_checks_not_artistic_quality"
Path(a.output).write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report,indent=2))
