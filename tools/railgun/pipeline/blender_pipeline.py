import bpy, argparse, json, hashlib, math, sys, time
from pathlib import Path
from mathutils import Vector
# Blender 3.4 glTF importer still uses removed NumPy dtype aliases.
import numpy as np
if "bool" not in np.__dict__: np.bool = np.bool_
a=sys.argv[sys.argv.index('--')+1:]
p=argparse.ArgumentParser()
for k in ('input','output','run-dir'): p.add_argument('--'+k,required=True)
p.add_argument('--ratio',type=float,default=1)
p.add_argument('--texture-limit',type=int,default=2048)
p.add_argument('--size',type=int,default=512)
o=p.parse_args(a)
src,dst,run=map(Path,(o.input,o.output,o.run_dir))
assert 0 < o.ratio <= 1 and src.is_file() and src.resolve()!=dst.resolve()
dst.parent.mkdir(parents=True,exist_ok=True);run.mkdir(parents=True,exist_ok=True)
t=time.monotonic()
def hashfile(f):
 h=hashlib.sha256()
 with open(f,'rb') as stream:
  for chunk in iter(lambda:stream.read(1048576),b''):h.update(chunk)
 return h.hexdigest()
def meshes():return [x for x in bpy.context.scene.objects if x.type=='MESH']
def box():
 cs=[ob.matrix_world @ Vector(v) for ob in meshes() for v in ob.bound_box]
 lo=Vector([min(v[i] for v in cs) for i in range(3)])
 hi=Vector([max(v[i] for v in cs) for i in range(3)])
 return (lo+hi)*.5,max((hi-lo).length,.01),list(hi-lo)
def stats():
 return {'triangles':sum(max(len(f.vertices)-2,0) for ob in meshes() for f in ob.data.polygons),
 'meshes':len(meshes()),'materials':len(set(m.name for ob in meshes() for m in ob.data.materials if m)),
 'textures':{im.name:list(im.size[:]) for im in bpy.data.images if im.has_data and im.size[0]},
 'dimensions':box()[2]}
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(src))
before=stats()
for ob in meshes():
 if o.ratio<1 and len(ob.data.polygons)>500:
  bpy.ops.object.select_all(action='DESELECT');ob.select_set(True)
  bpy.context.view_layer.objects.active=ob
  mod=ob.modifiers.new('Candidate decimate','DECIMATE');mod.ratio=o.ratio
  bpy.ops.object.modifier_apply(modifier=mod.name)
for im in list(bpy.data.images):
 if im.has_data and max(im.size)>o.texture_limit:
  w,h=im.size;s=o.texture_limit/max(w,h)
  im.scale(max(1,int(w*s)),max(1,int(h*s)))
 if im.has_data:
  try:im.pack()
  except Exception:pass
processed=stats()
bpy.ops.object.select_all(action='DESELECT')
for ob in meshes(): ob.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(dst),export_format='GLB',use_selection=True,export_apply=True)
assert dst.stat().st_size>4096
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(dst))
reimport=stats();assert reimport['triangles']>0
assert abs(reimport['triangles']-processed['triangles']) < max(12,int(reimport['triangles']*.001))
center,diameter,_=box();radius=diameter*.65
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=8
scene.cycles.use_denoising=False
for layer in scene.view_layers: layer.cycles.use_denoising=False
scene.render.resolution_x=o.size;scene.render.resolution_y=o.size
scene.render.resolution_percentage=100
scene.render.threads_mode='FIXED';scene.render.threads=6
scene.render.image_settings.file_format='PNG'
scene.view_settings.view_transform='Standard'
world=bpy.data.worlds.new('Studio');world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(.2,.23,.28,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=.9
scene.world=world
def lamp(name,relative,energy,scale):
 d=bpy.data.lights.new(name,'AREA');ob=bpy.data.objects.new(name,d)
 scene.collection.objects.link(ob);ob.location=center+Vector(relative)*radius
 ob.rotation_euler=(center-ob.location).to_track_quat('-Z','Y').to_euler()
 d.energy=energy;d.size=radius*scale
lamp('Key',(0,-2,2.5),650,3)
lamp('Fill',(0,2,1),500,3)
lamp('Rim',(-2,0,1.5),350,2)
cam=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'))
scene.collection.objects.link(cam);scene.camera=cam
cam.data.type='ORTHO';cam.data.ortho_scale=diameter*1.45
views={'side':(0,-2.5,.7),'opposite':(0,2.5,.7),'top':(0,0,3),
'underside':(0,-.4,-3),'muzzle':(-2.5,-.5,.5),'fp':(2,-2,1)}
for name,rel in views.items():
 cam.location=center+Vector(rel)*radius
 cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
 scene.render.filepath=str(run/(name+'-actual-model.png'))
 bpy.ops.render.render(write_still=True)
manifest={'input':str(src),'input_sha256':hashfile(src),'output':str(dst),
'output_sha256':hashfile(dst),'output_bytes':dst.stat().st_size,
'blender':bpy.app.version_string,'source':before,'processed':processed,
'reimport':reimport,'ratio':o.ratio,'texture_limit':o.texture_limit,
'seconds':round(time.monotonic()-t,1),'renders':'real output GLB (not concept image)'}
(run/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('SUCCESS',json.dumps({'source_triangles':before['triangles'],
'output_triangles':reimport['triangles'],'bytes':dst.stat().st_size}))
