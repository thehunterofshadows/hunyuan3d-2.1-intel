"""Orthographic CPU rasterizer for actual CAD meshes; no image generation or GUI required."""
from pathlib import Path
import json,math,struct
import numpy as np
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parent;O=R/'exports';M=json.loads((O/'preview_meshes.json').read_text())
COLORS={'wall':(.21,.30,.37),'floor':(.55,.64,.70),'lid':(.40,.55,.64),'bezel':(.12,.20,.27),'support':(.90,.58,.23),'joint':(.28,.67,.53)}
BG=np.array([244,247,250],dtype=np.uint8)
def render(items,size=(1050,900),direction=(-1,-1.4,1.1)):
 # items: (world vertices, triangle vertex indices, RGB float)
 forward=-np.array(direction,dtype=float);forward/=np.linalg.norm(forward)
 right=np.cross(forward,[0,0,1]);right/=np.linalg.norm(right);up=np.cross(right,forward)
 basis=np.array([right,up,forward]).T
 allp=np.concatenate([np.asarray(v)@basis for v,f,c in items]);mn=allp.min(axis=0);mx=allp.max(axis=0);center=(mn+mx)/2
 width,height=size;scale=min((width-80)/(mx[0]-mn[0]),(height-80)/(mx[1]-mn[1]))
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
base=Image.new('RGB',(2200,1400),tuple(BG));d=ImageDraw.Draw(base)
def text(x,y,s,size=24,strong=False,fill='#183449'):d.text((x,y),s,font=ImageFont.truetype(bold if strong else font,size),fill=fill)
text(80,45,'MINI VPIN  /  ACTUAL CAD PROTOTYPE',44,True);text(2050,45,'V1.2',36,True,'#ba7625')
text(80,110,'260 × 470 mm body  •  10° playfield  •  flat panels + screwed fittings  •  QIDI X-Max 3',26,False,'#526a7a')
for exploded in [False,True]:
 items=[]
 for p in M:
  off=np.zeros(3);name=p['name']
  if exploded:
   if p['kind']=='wall':
    if name.startswith('left'):off[0]=-45
    if name.startswith('right'):off[0]=45
    if name=='front_button_panel':off[1]=-50
    if name=='rear_vent_panel':off[1]=50
   if p['kind']=='floor':off[2]=-48
   if p['kind']=='bezel':off[2]=55
   if p['kind']=='lid':off[2]=95 if name!='control_hatch' else 135
  items.append((np.array(p['v'])+off,p['f'],COLORS[p['kind']]))
 if not exploded:
  y0=64;y1=y0+358.8*math.cos(math.radians(10));z=lambda y:75+y*math.tan(math.radians(10))
  v=[(18.1,y0,z(y0)),(241.9,y0,z(y0)),(241.9,y1,z(y1)),(18.1,y1,z(y1))]
  items.append((v,[(0,1,2),(0,2,3)],(.29,.64,.80)))
 base.paste(render(items),(50 if not exploded else 1100,230))
text(130,183,'ASSEMBLED — BLUE MONITOR REFERENCE',24,True);text(1200,183,'EXPLODED — PRINTED PARTS',24,True)
text(80,1140,'BUTTONS',24,True);text(80,1180,'5 × Ø28 mm holes; 45 mm inward allowances.',23,False,'#526a7a');text(80,1217,'Front row shifted right to clear the left cable channel.',23,False,'#526a7a')
text(1170,1140,'PRINT SMALL FIT TESTS FIRST',24,True);text(1170,1180,'Joint samples • monitor cradle + cap + shim • button coupon.',23,False,'#526a7a');text(1170,1217,'Housing and folded-cover contacts remain provisional.',23,False,'#526a7a')
text(80,1320,'Rendered from supplied CAD solids. Screws, nuts, foam, wiring and speakers are not shown.',22,False,'#6b7e8a')
base.save(O/'cad_preview.png')
names=['joint_front_wall','joint_rear_wall','joint_splice_plate','monitor_edge_cradle_12mm','monitor_retaining_bar','monitor_5mm_shim_for_7mm_housing','button_hole_28','button_hole_28p2','button_hole_28p4']
base=Image.new('RGB',(1800,1500),tuple(BG));d=ImageDraw.Draw(base)
text(60,30,'PRINT-FIRST FIT TESTS  /  ACTUAL STL GEOMETRY',37,True)
for i,name in enumerate(names):
 data=(O/'print_first_tests'/(name+'.stl')).read_bytes();n=struct.unpack_from('<I',data,80)[0]
 verts=np.array([struct.unpack_from('<12fH',data,84+j*50)[3:12] for j in range(n)]).reshape(-1,3);faces=np.arange(len(verts)).reshape(-1,3)
 image=render([(verts,faces,(.25,.64,.77) if i>2 else (.28,.67,.53))],(560,370),(-1,-1.5,1.2))
 x=20+(i%3)*600;y=125+(i//3)*450
 base.paste(image,(x,y+38));text(x+10,y,name.replace('_',' '),20)
base.save(O/'fit_test_preview.png')
print('CAD and fit-test previews rendered from mesh triangles.')
