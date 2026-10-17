"""Merge high-quality railgun accessory meshes by PBR material for browser draw calls."""
import bpy,sys,json,hashlib
from pathlib import Path
import numpy as np
if 'bool' not in np.__dict__:np.bool=np.bool_
src,dst=[Path(s) for s in sys.argv[sys.argv.index('--')+1:]]
assert src.resolve()!=dst.resolve()
dst.parent.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(src))
def obs():return [o for o in bpy.context.scene.objects if o.type=='MESH']
before=len(obs())
tris_before=sum(max(0,len(f.vertices)-2) for o in obs() for f in o.data.polygons)
materials=set(m.name for o in obs() for m in o.data.materials if m)
groups={}
for ob in obs():
 if len(ob.data.materials)!=1: raise RuntimeError('Multi material mesh not supported: '+ob.name)
 mat=ob.data.materials[0]
 key=mat.name if mat else 'none'
 groups.setdefault(key,[]).append(ob)
for name,parts in groups.items():
 bpy.ops.object.select_all(action='DESELECT')
 for ob in parts:ob.select_set(True)
 bpy.context.view_layer.objects.active=parts[0]
 bpy.ops.object.join()
 parts[0].name='MaterialGroup_'+name[:48]
bpy.ops.object.select_all(action='DESELECT')
for ob in obs():ob.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(dst),export_format='GLB',use_selection=True,export_apply=True)
after=len(obs())
tris_after=sum(max(0,len(f.vertices)-2) for o in obs() for f in o.data.polygons)
assert tris_before==tris_after and after<=20,(tris_before,tris_after,after)
print(json.dumps({'source_mesh_count':before,'optimized_mesh_count':after,'triangles':tris_after,'materials':len(materials),'bytes':dst.stat().st_size,'sha256':hashlib.sha256(dst.read_bytes()).hexdigest()}))
