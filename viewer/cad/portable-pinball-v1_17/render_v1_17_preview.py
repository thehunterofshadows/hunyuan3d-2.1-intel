"""Generate a source-geometry preview for V1.17. No fabricated or generated parts."""
from pathlib import Path
import json,math
import numpy as np
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parent; OUT=R/'exports'
P=json.loads((OUT/'preview_meshes.json').read_text())
PALETTE={'wall':(.19,.29,.37),'floor':(.51,.61,.68),'lid':(.33,.49,.59),'bezel':(.17,.23,.30),'support':(.85,.57,.21),'joint':(.20,.63,.54),'feet':(.36,.47,.59),'mount':(.51,.61,.67),'rubber':(.13,.16,.19)}
BG=np.array([244,247,250],dtype=np.uint8)
def render(items,size,direction=(-1,-1.4,1.2)):
 forward=-np.array(direction,dtype=float);forward/=np.linalg.norm(forward)
 right=np.cross(forward,[0,0,1]);right/=np.linalg.norm(right);up=np.cross(right,forward)
 basis=np.array([right,up,forward]).T
 allp=np.concatenate([np.asarray(v)@basis for v,f,c in items]);mn=allp.min(axis=0);mx=allp.max(axis=0);center=(mn+mx)/2
 width,height=size;scale=min((width-60)/max(mx[0]-mn[0],.1),(height-60)/max(mx[1]-mn[1],.1))
 canvas=np.full((height,width,3),BG,dtype=np.uint8);depth=np.full((height,width),np.inf)
 light=np.array([-.5,-.7,1]);light/=np.linalg.norm(light)
 for verts,faces,color in items:
  verts=np.array(verts);p=verts@basis;p[:,:2]-=center[:2];p[:,0]=p[:,0]*scale+width/2;p[:,1]=height/2-p[:,1]*scale
  for ids in faces:
   ids=np.array(ids);t=p[ids];a,b,c=t
   lo=np.maximum(np.floor(t[:,:2].min(axis=0)).astype(int),[0,0]);hi=np.minimum(np.ceil(t[:,:2].max(axis=0)).astype(int),[width-1,height-1])
   if (hi<lo).any():continue
   den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
   if abs(den)<1e-8:continue
   yy,xx=np.mgrid[lo[1]:hi[1]+1,lo[0]:hi[0]+1];xx=xx+.5;yy=yy+.5
   u=((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(yy-c[1]))/den
   v=((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(yy-c[1]))/den;w=1-u-v
   zz=u*a[2]+v*b[2]+w*c[2];buf=depth[lo[1]:hi[1]+1,lo[0]:hi[0]+1]
   mask=(u>=-1e-6)&(v>=-1e-6)&(w>=-1e-6)&(zz<buf)
   if not mask.any():continue
   world=verts[ids];n=np.cross(world[1]-world[0],world[2]-world[0]);length=np.linalg.norm(n)
   shade=.48+.52*max(0,float(n@light/length)) if length else .8
   rgb=np.clip(np.array(color)*255*shade,0,255).astype(np.uint8)
   buf[mask]=zz[mask];canvas[lo[1]:hi[1]+1,lo[0]:hi[0]+1][mask]=rgb
 return Image.fromarray(canvas)
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
image=Image.new('RGB',(1570,920),tuple(BG));draw=ImageDraw.Draw(image)
def txt(x,y,s,sz=22,b=False):draw.text((x,y),s,font=ImageFont.truetype(bold if b else font,sz),fill='#203445')
txt(40,18,'PORTABLE PINBALL  /  CAD V1.17',38,True)
txt(40,71,'M6x30 screw-on modules + M8 rubber-foot terminal  ·  no-tools adjustment',21)
items=[]
for p in P:
 if p['name'].startswith('REFERENCE_'):continue
 items.append((p['v'],p['f'],PALETTE[p['kind']]))
print('Rendering cabinet assembly',flush=True)
image.paste(render(items,(870,730),(-.85,-1.5,1.2)),(0,112))
rear=[]
for p in P:
 name=p['name'];select=('left_rear' in name and (name.startswith('foot_') or name.startswith('REFERENCE_swivel_rubber_pad_')))
 if not select:continue
 offsets={'foot_backing_left_rear':18,'foot_receiver_left_rear':10,'foot_twist_core_left_rear_1_45mm':0,'foot_lock_sleeve_left_rear_1_45mm':-7,'foot_bolt_key_left_rear_1_45mm':-12,'foot_m8_terminal_core_left_rear_55mm':-14,'foot_m8_terminal_sleeve_left_rear_55mm':-20,'foot_m8_terminal_bolt_key_left_rear_55mm':-25,'REFERENCE_swivel_rubber_pad_left_rear':-32}
 verts=np.asarray(p['v']).copy();verts[:,2]+=offsets.get(name,0)
 rear.append((verts,p['f'],PALETTE.get(p['kind'],(.2,.3,.3))))
print('Rendering exploded M6 rear foot',flush=True)
image.paste(render(rear,(650,710),(-1,-1.8,1.0)),(892,125))
txt(950,840,'Rear foot  ·  exploded 45 mm modules',20,True)
txt(60,854,'Assembled cabinet · 71 printed parts',20,True)
txt(50,892,'Exact CAD geometry; actual M6 head / nut fit and strength untested.',17)
image.save(OUT/'cad_preview.png',optimize=True)
print('Saved',OUT/'cad_preview.png',flush=True)
