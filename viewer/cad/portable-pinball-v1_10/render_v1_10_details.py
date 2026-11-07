"""Render the exact V1.10 CAD and fit samples; no concept imagery."""
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
D=P['nudge_recess_depth_mm']; WELL=P['nudge_well_floor_mm']; MOUTH=P['nudge_well_mouth_mm']
NY=P['flipper_y_mm']+P['nudge_center_spacing_mm']; BZ=P['button_center_z_mm']; T=P['wall']; HOLE=P['nudge_cutout_mm']
def wall_items(p,inside=False):
    feature=[];plain=[]
    for face in p['f']:
        vs=[p['v'][i] for i in face]
        if inside:
            selected=any(v[0]>4.001 for v in vs)
        else:
            selected=all(abs(v[1]-NY)<=MOUTH/2+.001 and abs(v[2]-BZ)<=MOUTH/2+.001 for v in vs) and any(.001<v[0]<=D+.001 for v in vs)
        (feature if selected else plain).append(face)
    return [(p['v'],plain,COLORS['wall']),(p['v'],feature,(.24,.66,.63))]
def frame(x,y,title,subtitle,img):
    text(x+22,y,title,26,True);text(x+22,y+40,subtitle,22,False,'#526a7a');base.paste(img,(x,y+77))
def stl_mesh(path):
    data=path.read_bytes();n=struct.unpack_from('<I',data,80)[0]
    if len(data)!=84+50*n:raise ValueError('Expected binary STL: '+str(path))
    v=np.array([struct.unpack_from('<12fH',data,84+j*50)[3:12] for j in range(n)]).reshape(-1,3)
    return v,np.arange(len(v)).reshape(-1,3)
def section():
    img=Image.new('RGB',(1100,500),tuple(BG));d=ImageDraw.Draw(img)
    f=ImageFont.truetype(font,23);small=ImageFont.truetype(font,21)
    def xy(u,depth):return (450+u*24,120+depth*55)
    left=[(-15,0),(-MOUTH/2,0),(-WELL/2,D),(-HOLE/2,D),(-HOLE/2,T),(-15,T)]
    d.polygon([xy(*p) for p in left],fill='#829ba8')
    d.polygon([xy(-u,v) for u,v in left],fill='#829ba8')
    for a,b in [((-MOUTH/2,0),(-WELL/2,D)),((-WELL/2,D),(-HOLE/2,D)),((MOUTH/2,0),(WELL/2,D)),((WELL/2,D),(HOLE/2,D))]:
        d.line([xy(*a),xy(*b)],fill='#248f88',width=5)
    def arrow(a,b,label,pos):
        d.line([a,b],fill='#274b60',width=2)
        dx=b[0]-a[0];dy=b[1]-a[1];norm=math.hypot(dx,dy);ux=dx/norm;uy=dy/norm
        for p,sign in [(a,1),(b,-1)]:
            q=(p[0]+sign*ux*8,p[1]+sign*uy*8)
            d.polygon([p,(q[0]-uy*4,q[1]+ux*4),(q[0]+uy*4,q[1]-ux*4)],fill='#274b60')
        d.text(pos,label,font=small,fill='#274b60')
    d.text((90,24),'OUTSIDE / BUTTON SIDE',font=f,fill='#526a7a')
    arrow(xy(-MOUTH/2,-.55),xy(MOUTH/2,-.55),f'{MOUTH:g} mm mouth',(382,55))
    arrow((860,120),(860,120+D*55),f'{D:g} mm recess',(880,170))
    arrow((860,120+D*55),(860,120+T*55),f'{T-D:g} mm plate',(880,285))
    arrow(xy(-HOLE/2,T+.5),xy(HOLE/2,T+.5),f'{HOLE:g} mm opening',(350,380))
    d.text((90,410),'INSIDE OF CABINET',font=f,fill='#526a7a')
    d.text((90,455),'Depth exaggerated for clarity; switch and cap are not shown.',font=small,fill='#526a7a')
    return img
wall=next(p for p in M if p['name']=='left_front_wall')
sample=O/'print_first_tests/nudge_switch_fit.stl';v,f=stl_mesh(sample)
text(65,35,'PORTABLE PINBALL  /  V1.10',45,True)
text(65,96,'Recessed nudge switch  •  2.5 mm setback  •  Separate 30 × 30 mm fit sample  •  Actual CAD geometry',24,False,'#526a7a')
frame(35,165,'LEFT WALL — OUTSIDE','The tapered pocket moves the switch mounting face inward.',render(wall_items(wall),(1100,560),(-1,.12,.18)))
frame(1160,165,'SMALL SWITCH-ONLY TEST','30 × 30 × 4 mm. Default 14.1 mm opening.',render([(v,f,(.28,.61,.67))],(1100,560),(.45,-.7,-1.4)))
frame(35,860,'RECESSED MOUNTING — SECTION','A 1.5 mm plate remains for the switch clips.',section())
frame(1160,860,'LEFT WALL — INSIDE','The existing flipper reinforcement continues to the bottom.',render(wall_items(wall,True),(1100,500),(1,.12,.18)))
text(65,1530,'Only the two front walls change from V1.9. Test your actual switch and the full button stroke in the small sample.',22,False,'#526a7a')
text(65,1570,'Print the sample outside-face-down to match the wall. Check the recessed ledge for bridge sag or support cleanup.',22,False,'#526a7a')
base.save(O/'cad_preview.png');base.save(O/'changes_preview.png')
base=Image.new('RGB',(2040,860),tuple(BG));draw=ImageDraw.Draw(base)
text(55,35,'V1.10  /  SMALL RECESSED SWITCH FIT TESTS',38,True)
text(55,94,'Start with the 14.1 mm opening. Each sample is 30 × 30 × 4 mm and has the same 2.5 mm recess.',24,False,'#526a7a')
for i,(name,label) in enumerate([('nudge_mx_14p0.stl','14.0 mm opening'),('nudge_switch_fit.stl','14.1 mm — DEFAULT'),('nudge_mx_14p2.stl','14.2 mm opening')]):
    v,f=stl_mesh(O/'print_first_tests'/name);x=20+i*680
    text(x+30,185,label,26,True)
    base.paste(render([(v,f,(.28,.61,.67))],(650,480),(.45,-.7,-1.4)),(x,235))
text(55,770,'Use the actual switch and cap. Check clip retention, removal and full travel before printing the wall.',23,False,'#526a7a')
base.save(O/'fit_test_preview.png')
base=Image.new('RGB',(1600,1060),tuple(BG));draw=ImageDraw.Draw(base)
text(55,35,'SMALL NUDGE SWITCH FIT TEST  /  V1.10',36,True)
text(55,90,'30 × 30 × 4 mm  •  14.1 mm square opening  •  2.5 mm recessed mounting face',25,False,'#526a7a')
v,f=stl_mesh(sample);base.paste(render([(v,f,(.28,.61,.67))],(1500,780),(.45,-.7,-1.4)),(50,155))
text(55,975,'Exact print geometry. Test the actual switch clips and button travel; hardware is not included.',23,False,'#526a7a')
base.save(O/'nudge_switch_fit_preview.png')
print(json.dumps({'preview':str(O/'cad_preview.png'),'small_sample':str(sample)}))
