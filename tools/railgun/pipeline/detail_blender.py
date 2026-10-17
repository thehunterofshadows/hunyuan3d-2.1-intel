"""Add authored heat pipes, cooling fins and conduits to the existing real GLB.
Blender 3.4 compatible; never modifies original source asset.
"""
import bpy, math, sys, json, hashlib
from pathlib import Path
from mathutils import Vector
a=sys.argv[sys.argv.index('--')+1:]
src=Path(a[0]);out=Path(a[1]);out.parent.mkdir(parents=True,exist_ok=True)
assert src!=out and src.exists()
import numpy as np
if 'bool' not in np.__dict__:np.bool=np.bool_
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(src))
source_objects=set(bpy.context.scene.objects)
def mat(name,rgb,metal,rough,emit=0):
 m=bpy.data.materials.new(name);m.use_nodes=True
 node=m.node_tree.nodes.get('Principled BSDF')
 node.inputs['Base Color'].default_value=(*rgb,1)
 node.inputs['Metallic'].default_value=metal
 node.inputs['Roughness'].default_value=rough
 if emit:
  node.inputs['Emission'].default_value=(*rgb,1)
  node.inputs['Emission Strength'].default_value=emit
 return m
copper=mat('Polished copper heat exchanger',(.62,.23,.07),.85,.23)
dark=mat('Blackened radiator slots',(.025,.033,.04),.7,.48)
titanium=mat('Machined stainless cooling fins',(.31,.39,.44),.83,.29)
ceramic=mat('Graphite pipe clamps',(.035,.046,.054),.42,.55)
cyan=mat('Induction waveguide emissive',(.015,.48,.83),.20,.22,1.1)
orange=mat('Thermal warning enamel',(.92,.18,.012),.24,.32)
def cube(name,loc,scale,material,bevel=.005):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
 ob=bpy.context.object;ob.name=name
 ob.dimensions=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 ob.data.materials.append(material)
 if bevel:
  mod=ob.modifiers.new('Precision edge radius','BEVEL')
  mod.width=bevel;mod.segments=2
  bpy.context.view_layer.objects.active=ob
  bpy.ops.object.modifier_apply(modifier=mod.name)
 return ob
def tube(name,pts,radius,material):
 curve=bpy.data.curves.new(name,'CURVE');curve.dimensions='3D'
 curve.bevel_depth=radius;curve.bevel_resolution=3
 spline=curve.splines.new('POLY');spline.points.add(len(pts)-1)
 for pt,v in zip(spline.points,pts):
  pt.co=(*v,1)
 ob=bpy.data.objects.new(name,curve);bpy.context.collection.objects.link(ob)
 ob.data.materials.append(material)
 bpy.ops.object.select_all(action='DESELECT')
 ob.select_set(True);bpy.context.view_layer.objects.active=ob
 bpy.ops.object.convert(target='MESH')
 return bpy.context.object
for side in (-1,1):
 # Visible mechanically continuous copper thermal loop, left/right.
 for n,z in enumerate((.46,.12,-.08)):
  outer=side*(.274+(.022 if n==1 else 0))
  pts=[(.65,side*.251,z),(.45,outer,z+.065),(.05,outer,z+.055),
       (-.30,outer,z+.078),(-.58,outer,z+.06),
       (-1.05,outer,z+.035),(-1.70,outer,z+.035),(-2.22,outer,z+.035)]
  tube('Copper heat pipe %s/%s'%(side,n),pts,.018,copper)
  for x in (-1.82,-.89,-.36):
   cube('Machined copper pipe clip',(x,outer+side*.018,z+.045),
        (.085,.04,.045),ceramic,.007)
 # 11 repeating, separated vents below the twin main rails.
 for i in range(11):
  x=-2.28+i*.155
  cube('Radiator fin %s-%02d'%(side,i),(x,side*.221,-.185),
       (.035,.12,.18),titanium,.004)
  cube('Fin slit %s-%02d'%(side,i),(x,side*.285,-.157),
       (.015,.018,.11),dark,.001)
 # Bold spaced receiver cooling shutters and interspersed energy windows.
 for i in range(8):
  x=-.14+i*.132
  cube('Receiver ceramic heat sink %s-%02d'%(side,i),
       (x,side*.280,.63),(.043,.086,.172),ceramic,.007)
  cube('Copper vent edge %s-%02d'%(side,i),
       (x,side*.329,.58),(.018,.013,.10),copper,.002)
  if i%2==0:
   cube('Energy status LED %s-%02d'%(side,i),
        (x,side*.338,.68),(.035,.017,.028),cyan,.002)
 # Metallic collar armor and rear orange warnings
 for j,x in enumerate((-.36,-2.36)):
  cube('Side radiator shield %s-%s'%(side,j),
       (x,side*.275,.33),(.075,.038,.24),titanium,.012)
 cube('Thermal warning chip '+str(side),(.83,side*.315,.60),
      (.11,.015,.025),orange,.003)
# Additional continuous soft-glow barrel spine separated from thermal pipes
tube('Dual accelerator central blue ion line',[(-2.58,0,.225),(-1.9,0,.225),
     (-1.2,0,.225),(-.55,0,.225)],.027,cyan)
# Base model was exported at 25 percent of its authored Blender dimensions.
# Apply the same conversion to all newly authored physical detail parts.
for ob in bpy.context.scene.objects:
 if ob not in source_objects and ob.type=='MESH':
  ob.location *= .25
  ob.scale *= .25
# Copy original parent/mesh hierarchy; accessories are independent named parts.
bpy.ops.object.select_all(action='DESELECT')
objects=[ob for ob in bpy.context.scene.objects if ob.type=='MESH']
for ob in objects:ob.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',export_apply=True,use_selection=True)
def count():return sum(len(p.vertices)-2 for ob in bpy.context.scene.objects if ob.type=='MESH' for p in ob.data.polygons)
manifest={'asset':'railgun-hard-surface-v2','input':str(src),'output':str(out),
    'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
    'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),
    'triangles':count(),'bytes':out.stat().st_size,
    'added_geometry':'copper heat pipes, 22 underrail fins, 16 upper shutters, clamps, ion conduit',
    'source_unchanged':True}
(out.parent/'build.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('BUILT',json.dumps(manifest))
