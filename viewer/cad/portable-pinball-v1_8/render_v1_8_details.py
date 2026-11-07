"""Render the exact V1.8 CAD and fit samples; no concept imagery."""
from pathlib import Path
import json, math, struct
import numpy as np
from PIL import Image, ImageDraw, ImageFont
R=Path(__file__).resolve().parent
O=R/'exports'
M=json.loads((O/'preview_meshes.json').read_text())
P=json.loads((R/'parameters.json').read_text())
COLORS={'wall':(.21,.30,.37),'floor':(.55,.64,.70),'lid':(.40,.55,.64),'bezel':(.12,.20,.27),'support':(.90,.58,.23),'joint':(.28,.67,.53)}
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
def items(names=None):
    return [(p['v'],p['f'],COLORS[p['kind']]) for p in M if names is None or p['name'] in names]
def frame(x,y,title,subtitle,image):
    text(x+22,y,title,26,True)
    text(x+22,y+40,subtitle,22,False,'#526a7a')
    base.paste(image,(x,y+77))
text(65,35,'PORTABLE PINBALL  /  V1.8',45,True)
text(65,96,'Actual CAD geometry  •  33 mm nudge spacing  •  Direct switch holes  •  Reinforced flippers  •  120 mm fan grille',24,False,'#526a7a')
assembly_items=items()
y0=P['monitor_front_y'];y1=y0+P['monitor_length']*math.cos(math.radians(P['slope_degrees']))
z=lambda y:P['front_height']+y*math.tan(math.radians(P['slope_degrees']))
left=(P['width']-P['monitor_width'])/2;right=left+P['monitor_width']
monitor=[(left,y0,z(y0)),(right,y0,z(y0)),(right,y1,z(y1)),(left,y1,z(y1))]
assembly_items.append((monitor,[(0,1,2),(0,2,3)],(.29,.64,.80)))
frame(35,165,'ASSEMBLED CABINET','Both sides use matching flipper and nudge openings.',render(assembly_items,(1100,560),(-1,-1.4,1.1)))
frame(1160,165,'REAR FAN PANEL','Curved grille, four fan mounting holes and separate cable exit.',render(items({'rear_vent_panel'}),(1100,560),(.15,1,.15)))
frame(35,860,'LEFT WALL — OUTSIDE','Round flipper hole and square nudge hole share the same height.',render(items({'left_front_wall'}),(1100,500),(-1,0,0)))
frame(1160,860,'LEFT WALL — INSIDE','Local flipper reinforcement and recessed switch clip clearance.',render(items({'left_front_wall'}),(1100,500),(1,.12,.18)))
text(65,1530,'Switch opening assumes a conventional MX-style switch. Print the supplied fit samples before the full walls.',23,False,'#526a7a')
text(65,1570,'45 printable parts. Only the two front side walls and rear vent panel change from V1.7. Physical fit remains unverified.',22,False,'#526a7a')
base.save(O/'cad_preview.png')
base.save(O/'changes_preview.png')
def stl_mesh(path):
    data=path.read_bytes();n=struct.unpack_from('<I',data,80)[0]
    if len(data)!=84+50*n:raise ValueError('Expected binary STL: '+str(path))
    v=np.array([struct.unpack_from('<12fH',data,84+j*50)[3:12] for j in range(n)]).reshape(-1,3)
    return v,np.arange(len(v)).reshape(-1,3)
paths=sorted((O/'print_first_tests').glob('nudge*.stl'))
sample=O/'print_first_tests/flipper_nudge_wall_sample.stl'
if sample.exists():paths.insert(0,sample)
if not paths:paths=[O/'print_first_tests/button_hole_28.stl']
cols=2;rows=math.ceil(len(paths)/cols)
base=Image.new('RGB',(1800,160+rows*560),tuple(BG));draw=ImageDraw.Draw(base)
text(55,32,'V1.8  /  PRINT THESE FIT SAMPLES FIRST',38,True)
text(55,88,'Check switch clips, flipper nut engagement and comfortable spacing.',24,False,'#526a7a')
for i,path in enumerate(paths):
    v,f=stl_mesh(path);x=25+(i%cols)*900;y=160+(i//cols)*560
    text(x+25,y,path.stem.replace('_',' '),22,True)
    base.paste(render([(v,f,(.25,.58,.72))],(850,480),(-1,-1.5,1.3)),(x,y+45))
base.save(O/'fit_test_preview.png')
print(json.dumps({'preview':str(O/'cad_preview.png'),'fit_samples':[p.name for p in paths]}))
