from pathlib import Path
import json,struct,math,numpy as np,tarfile,shutil
import argparse
p=argparse.ArgumentParser();p.add_argument('--cad-dir',required=True,type=Path);p.add_argument('--output',required=True,type=Path);p.add_argument('--print-pack',type=Path);args=p.parse_args()
R=args.cad_dir;dest=args.output;dest.mkdir(parents=True,exist_ok=True)
m=json.loads((R/'exports/preview_meshes.json').read_text())
colors={'wall':[.17,.24,.31,1],'floor':[.40,.47,.53,1],'lid':[.36,.48,.57,1],'bezel':[.16,.21,.26,1],'support':[.88,.55,.20,1],'joint':[.25,.66,.55,1]}
g={'asset':{'version':'2.0','generator':'Exact CAD tessellation from Mini VPin V1','extras':{'sourceUnits':'mm','displayUnits':'m'}},'scene':0,'scenes':[{'nodes':[]}],'nodes':[],'meshes':[],'materials':[],'buffers':[{}],'bufferViews':[],'accessors':[]}
buf=bytearray()
def acc(array,component,kind,target):
 while len(buf)%4:buf.append(0)
 offset=len(buf);buf.extend(array.tobytes());view=len(g['bufferViews']);g['bufferViews'].append({'buffer':0,'byteOffset':offset,'byteLength':array.nbytes,'target':target})
 a={'bufferView':view,'componentType':component,'count':len(array),'type':kind}
 if kind=='VEC3':a.update(min=array.min(axis=0).tolist(),max=array.max(axis=0).tolist())
 g['accessors'].append(a);return len(g['accessors'])-1
materialids={}
def material(kind,color):
 if kind in materialids:return materialids[kind]
 v={'name':kind,'pbrMetallicRoughness':{'baseColorFactor':color,'metallicFactor':.0,'roughnessFactor':.7},'doubleSided':False}
 if color[3]<1:v['alphaMode']='BLEND'
 g['materials'].append(v);i=len(g['materials'])-1;materialids[kind]=i;return i
for p in m:
 name=p['name'];off=np.zeros(3)
 if p['kind']=='wall':
  if name.startswith('left'):off[0]=-55
  if name.startswith('right'):off[0]=55
  if name=='front_button_panel':off[1]=-65
  if name=='rear_vent_panel':off[1]=65
 if p['kind']=='floor':off[2]=-60
 if p['kind']=='bezel':off[2]=65
 if p['kind']=='lid':off[2]=110 if name!='control_hatch' else 165
 p['extras']={'cadPart':True,'kind':p['kind'],'explode':[off[0]/1000,off[2]/1000,-off[1]/1000]}
 p['color']=colors[p['kind']]
def box(name,x,y,z,w,l,h,kind,color):
 v=[[x,y,z],[x+w,y,z],[x+w,y+l,z],[x,y+l,z],[x,y,z+h],[x+w,y,z+h],[x+w,y+l,z+h],[x,y+l,z+h]]
 f=[[0,2,1],[0,3,2],[4,5,6],[4,6,7],[0,1,5],[0,5,4],[1,2,6],[1,6,5],[2,3,7],[2,7,6],[3,0,4],[3,4,7]]
 return {'name':name,'v':v,'f':f,'kind':kind,'color':color,'extras':{'cadReference':kind,'explode':[0,0,0]}}
y0=64;y1=64+358.8*math.cos(math.radians(10));z=lambda y:75+y*math.tan(math.radians(10))
monitor=box('REFERENCE_Monitor',18.1,y0,0,223.8,y1-y0,12,'monitor',[.18,.58,.76,1])
for v in monitor['v']:v[2]+=z(v[1])-12
m.append(monitor)
m.append(box('REFERENCE_Dell_3050',35,240,13,190,190,45,'pc',[.22,.72,.48,.5]))
cover=box('REFERENCE_Folded_cover_allowance',23.1,y0,0,213.8,y1-y0,28,'cover',[.9,.55,.18,.3])
for v in cover['v']:v[2]+=z(v[1])-35
m.append(cover)
for p in m:
 v=np.array(p['v']);v=np.stack((v[:,0],v[:,2],-v[:,1]),axis=1).astype('<f4')/1000
 f=np.array(p['f'],dtype='<u4');normals=np.zeros_like(v)
 n=np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]])
 for j in range(3):np.add.at(normals,f[:,j],n)
 norms=np.linalg.norm(normals,axis=1);normals/=np.where(norms>0,norms,1)[:,None]
 va=acc(v.astype('<f4'),5126,'VEC3',34962);na=acc(normals.astype('<f4'),5126,'VEC3',34962);ia=acc(f.flatten(),5125,'SCALAR',34963)
 mesh=len(g['meshes']);g['meshes'].append({'name':p['name'],'primitives':[{'attributes':{'POSITION':va,'NORMAL':na},'indices':ia,'material':material(p['kind'],p['color'])}]})
 idx=len(g['nodes']);g['nodes'].append({'name':p['name'],'mesh':mesh,'extras':p['extras']});g['scenes'][0]['nodes'].append(idx)
g['buffers'][0]['byteLength']=len(buf)
j=json.dumps(g,separators=(',',':')).encode();j+=b' '*((-len(j))%4);buf+=b'\0'*((-len(buf))%4)
out=struct.pack('<III',0x46546c67,2,12+8+len(j)+8+len(buf))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(buf),0x004e4942)+buf
(dest/'cabinet.glb').write_bytes(out)
shutil.copy2(R/'exports/cad_preview.png',dest/'preview.png')
shutil.copy2(R/'exports/fit_test_preview.png',dest/'fit-tests.png')
if args.print_pack:shutil.copy2(args.print_pack,dest/'cad-print-pack.zip')
shutil.copy2(R/'exports/mini_vpin_assembly.step',dest/'cabinet.step')
shutil.copy2(R/'exports/print_first_tests/button_hole_28.stl',dest/'button_hole_28.stl')
(dest/'README.md').write_text('Exact Mini VPin V1 CAD tessellation. 47 printable parts + 3 named reference envelopes. World axes converted from mm Z-up to meters Y-up. Source STEP and print pack included; no AI generation was used for this cabinet. Mesh sources were supplied by the user in this conversation. Prototype; physical fit tests pending.\n')
print(json.dumps({'nodes':len(g['nodes']),'printedParts':47,'triangles':sum(len(p['f']) for p in m),'glbBytes':len(out)}))
