#!/usr/bin/env python3
"""Independent V1.12 assembly/manifest audit without reusing CadQuery builder state."""
from pathlib import Path
import json,struct
ROOT=Path(__file__).resolve().parents[1];C=ROOT/'cad/portable-pinball-v1_12/exports';A=ROOT.parent/'assets/portable-pinball-v1_12'
manifest=json.loads((C/'parts_manifest.json').read_text());parts={p['name']:p for p in manifest['parts']}
meshes={m['name']:m for m in json.loads((C/'preview_meshes.json').read_text())}
checks=json.loads((C/'geometry_checks.json').read_text());vcheck=json.loads((C/'v1_12_feature_checks.json').read_text())
assert len(parts)==63 and len(manifest['tests'])==20
assert checks['interferences']==checks['reserved_space_interferences']==checks['control_hardware_interferences']==[]
assert vcheck['all_feature_checks_passed']
assert len(meshes)==67
heights={}
for side in ('left','right'):
 for region in ('front','rear'):
  key=side+'_'+region
  for prefix in ('foot_receiver_','foot_backing_','foot_terminal_'):
   assert prefix+key in parts
  segs=[p for p in parts if p.startswith('foot_extension_'+key+'_')]
  assert len(segs)==(1 if region=='front' else 2),segs
  assert sum(int(p.split('_')[-1].replace('mm','')) for p in segs)==(20 if region=='front' else 60)
  foot=meshes['REFERENCE_swivel_rubber_pad_'+key]
  heights[key]=min(v[2] for v in foot['v'])
for side in ('left','right'):
 assert abs((heights[side+'_front']-heights[side+'_rear'])-40)<1e-5
for n in ('bottom_front','bottom_rear'):
 assert n in parts and (A/'stl-v1_12'/(n+'.stl')).is_file()
glb=(A/'cabinet-v1_12.glb').read_bytes();magic,version,length=struct.unpack_from('<III',glb)
assert magic==0x46546c67 and version==2 and length==len(glb)
assert len(json.loads(glb[20:20+struct.unpack_from('<I',glb,12)[0]])['nodes'])==70
assert (A/'modular-foot-fit-kit-v1_12.zip').is_file()
print(json.dumps({'status':'PASS','printedParts':len(parts),'fitTests':len(manifest['tests']),'rubberFootReferences':4,'frontExtension_mm':20,'rearExtension_mm':60,'rearLiftRelative_mm':40,'interferenceCount':0,'glbNodes':70},indent=2))
