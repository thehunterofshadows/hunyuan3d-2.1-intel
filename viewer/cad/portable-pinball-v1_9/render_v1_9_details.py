"""Render the exact V1.9 CAD and fit samples; no concept imagery."""
from pathlib import Path
import json, math, struct
import numpy as np
from PIL import Image, ImageDraw, ImageFont
R=Path(__file__).resolve().parent
O=R/'exports'
M=json.loads((O/'preview_meshes.json').read_text())
P=json.loads((R/'parameters.json').read_text())
COLORS={'wall':(.45,.56,.63),'floor':(.55,.64,.70),'lid':(.40,.55,.64),'bezel':(.12,.20,.27),'support':(.90,.58,.23),'joint':(.28,.67,.53)}
BG=np.array([244,247,250],dtype=np.uint8)
def render(items,size=(1050,580),direction=(-1,-1.4,1.1)):
    forward=-np.array(direction,dtype=float);forward/=np.linalg.norm(forward)
    right=np.cross(forward,[0,0,1]);right/=np.linalg.norm(right)
    up=np.cross(right,forward);basis=np.array([right,up,forward]).T
    allp=np.concatenate([np.asarray(v)@basis for v,f,c in items])
    mn=allp.min(axis=0);mx=allp.max(axis=0);center=(mn+mx)/2
    width,height=size;scale=min((width-70)/(mx[0]-mn[0]),(height-60)/(mx[1]-mn[1]))
    canvas=np.full((height,width,3),BG,dtype=np.uint8);depth=np.full((height,width),np.inf)
    light=np.array([-.5,-.7,1]);light/=np.linalg.norm(light)
    for verts,faces,color in items:
        verts=np.array(verts);p=verts@basis;p[:,:2]-=center[:2]
        p[:,0]=p[:,0]*scale+width/2;p[:,1]=height/2-p[:,1]*scale
        for ids in faces:
            ids=np.array(ids);t=p[ids];a,b,c=t
            lo=np.maximum(np.floor(t[:,:2].min(axis=0)).astype(int),[0,0])
            hi=np.minimum(np.ceil(t[:,:2].max(axis=0)).astype(int),[width-1,height-1])
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
            shade=.60+.40*abs(float(n@light/length)) if length else .8
            rgb=np.clip(np.array(color)*255*shade,0,255).astype(np.uint8)
            buf[mask]=zz[mask];canvas[lo[1]:hi[1]+1,lo[0]:hi[0]+1][mask]=rgb
    return Image.fromarray(canvas)
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
base=Image.new('RGB',(2300,1640),tuple(BG));draw=ImageDraw.Draw(base)
def text(x,y,s,size=24,strong=False,fill='#183449'):
    draw.text((x,y),s,font=ImageFont.truetype(bold if strong else font,size),fill=fill)
def wall_items(p):
    raised=[];plain=[]
    for face in p['f']:
        (raised if any(p['v'][i][0]>4.001 for i in face) else plain).append(face)
    return [(p['v'],plain,COLORS['wall']),(p['v'],raised,(.27,.67,.65))]
def items(names=None):
    result=[]
    for p in M:
        if names is not None and p['name'] not in names:continue
        result.extend(wall_items(p) if p['name']=='left_front_wall' else [(p['v'],p['f'],COLORS[p['kind']])])
    return result
def frame(x,y,title,subtitle,image):
    text(x+22,y,title,26,True)
    text(x+22,y+40,subtitle,22,False,'#526a7a')
    base.paste(image,(x,y+77))
text(65,35,'PORTABLE PINBALL  /  V1.9',45,True)
text(65,96,'Actual CAD comparison  •  Raised reinforcement highlighted  •  8 mm total thickness down to the bottom edge',24,False,'#526a7a')
old=json.loads((R/'comparison_v1_8_left_front_wall.json').read_text())
old_wall=wall_items(next(p for p in old if p['name']=='left_front_wall'))
frame(35,165,'V1.8 — EXISTING INSIDE COLLAR','The circular reinforcement ends above the bottom edge.',render(old_wall,(1100,560),(1,.12,.18)))
frame(1160,165,'V1.9 — REINFORCEMENT TO THE BOTTOM','A broad, continuous pad supports the lower button area.',render(items({'left_front_wall'}),(1100,560),(1,.12,.18)))
frame(35,860,'V1.9 — FRONT FLOOR PANEL','Two shallow edge notches clear the new reinforcement.',render(items({'bottom_front'}),(1100,500),(.12,-.2,1)))
frame(1160,860,'V1.9 — WALL AND FLOOR TOGETHER','Same screw locations; the floor remains removable.',render(items({'left_front_wall','bottom_front'}),(1100,500),(1,-1.3,1.2)))
text(65,1530,'45 printable parts. Only both front walls and the front floor change. Nudge spacing stays 33 mm.',23,False,'#526a7a')
text(65,1570,'Designed to reduce local wall flex. Actual stiffness and hardware fit require a hands-on check after printing.',22,False,'#526a7a')
base.save(O/'cad_preview.png')
base.save(O/'changes_preview.png')
def stl_mesh(path):
    data=path.read_bytes();n=struct.unpack_from('<I',data,80)[0]
    if len(data)!=84+50*n:raise ValueError('Expected binary STL: '+str(path))
    v=np.array([struct.unpack_from('<12fH',data,84+j*50)[3:12] for j in range(n)]).reshape(-1,3)
    return v,np.arange(len(v)).reshape(-1,3)
paths=sorted((O/'print_first_tests').glob('nudge*.stl'))
floor_sample=O/'print_first_tests/flipper_floor_notch_sample.stl'
if floor_sample.exists():paths.insert(0,floor_sample)
sample=O/'print_first_tests/flipper_nudge_wall_sample.stl'
if sample.exists():paths.insert(0,sample)
if not paths:paths=[O/'print_first_tests/button_hole_28.stl']
cols=2;rows=math.ceil(len(paths)/cols)
base=Image.new('RGB',(1800,160+rows*560),tuple(BG));draw=ImageDraw.Draw(base)
text(55,32,'V1.9  /  PRINT THESE FIT SAMPLES FIRST',38,True)
text(55,88,'Check the wall-to-floor clearance, switch clips and flipper nut engagement.',24,False,'#526a7a')
for i,path in enumerate(paths):
    v,f=stl_mesh(path);x=25+(i%cols)*900;y=160+(i//cols)*560
    text(x+25,y,path.stem.replace('_',' '),22,True)
    base.paste(render([(v,f,(.25,.58,.72))],(850,480),(-1,-1.5,1.3)),(x,y+45))
base.save(O/'fit_test_preview.png')
print(json.dumps({'preview':str(O/'cad_preview.png'),'fit_samples':[p.name for p in paths]}))
