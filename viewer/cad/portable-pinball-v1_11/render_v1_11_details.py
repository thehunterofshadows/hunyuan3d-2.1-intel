
"""Render exact V1.11 front-corner geometry and print-test pieces."""
from pathlib import Path
import json, math, struct
import numpy as np
from PIL import Image, ImageDraw, ImageFont
R=Path(__file__).resolve().parent
O=R/'exports'
P=json.loads((R/'parameters.json').read_text())
M=json.loads((O/'front_corner_preview_meshes.json').read_text())
B=json.loads((O/'front_corner_before_meshes.json').read_text())
BG=np.array([244,247,250],dtype=np.uint8)
COLORS={'wall':(.45,.56,.63),'lid':(.25,.60,.64),'joint':(.87,.59,.27)}
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'

def render(items,size=(1050,560),direction=(-1,-1.4,1.0),frame_items=None):
    forward=-np.array(direction,dtype=float);forward/=np.linalg.norm(forward)
    right=np.cross(forward,[0,0,1]);right/=np.linalg.norm(right)
    up=np.cross(right,forward);basis=np.array([right,up,forward]).T
    allp=np.concatenate([np.asarray(v)@basis for v,f,c in (frame_items or items)])
    mn=allp.min(axis=0);mx=allp.max(axis=0);center=(mn+mx)/2
    width,height=size;scale=min((width-80)/max(mx[0]-mn[0],1),(height-70)/max(mx[1]-mn[1],1))
    canvas=np.full((height,width,3),BG,dtype=np.uint8);depth=np.full((height,width),np.inf)
    light=np.array([-.7,-.5,1.0]);light/=np.linalg.norm(light)
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
            shade=.52+.48*abs(float(n@light/length)) if length else .8
            rgb=np.clip(np.array(color)*255*shade,0,255).astype(np.uint8)
            buf[mask]=zz[mask];canvas[lo[1]:hi[1]+1,lo[0]:hi[0]+1][mask]=rgb
    return Image.fromarray(canvas)

def items(meshes,explode=False):
    out=[]
    for m in meshes:
        v=np.asarray(m['v'],dtype=float).copy()
        name=m['name']
        kind=m.get('kind','wall')
        color=COLORS.get(kind,COLORS['wall'])
        if 'panel' in name:color=(.57,.67,.73)
        if 'lid' in name:color=COLORS['lid']
        if 'corner_left' in name or 'top_block' in name:color=COLORS['joint']
        if explode:
            if 'lid' in name:v[:,2]+=9
            elif 'panel' in name:v[:,1]-=6
            elif 'wall' in name:v[:,0]-=6
        out.append((v,m['f'],color))
    return out

def stl_mesh(path):
    data=path.read_bytes();n=struct.unpack_from('<I',data,80)[0]
    assert len(data)==84+50*n
    v=np.array([struct.unpack_from('<12fH',data,84+j*50)[3:12] for j in range(n)]).reshape(-1,3)
    return v,np.arange(len(v)).reshape(-1,3)

def text(draw,x,y,s,size=24,strong=False,fill='#183449'):
    draw.text((x,y),s,font=ImageFont.truetype(BOLD if strong else FONT,size),fill=fill)

def section():
    img=Image.new('RGB',(1100,500),tuple(BG));d=ImageDraw.Draw(img)
    extent=P['front_edge_depth_mm'];radius=P['front_edge_blend_radius_mm']
    start=extent+radius-math.sqrt(2)*radius
    join=(extent-radius/math.sqrt(2),radius-radius/math.sqrt(2))
    arc=[(extent+radius*math.cos(a),radius+radius*math.sin(a)) for a in np.linspace(5*math.pi/4,3*math.pi/2,65)]
    profile=[(0,start),join,*arc[1:]]
    def pt(u,v):return (85+v*170,415-u*170)
    old=[pt(0,0),pt(2.1,0),pt(2.1,3.1),pt(0,3.1)]
    d.polygon(old,fill='#e0e7ed')
    d.polygon([pt(*p) for p in [*profile,(2.1,0),(2.1,3.1),(0,3.1)]],fill='#829ba8')
    d.line([pt(*p) for p in profile],fill='#c48a29',width=5)
    d.line([(45,420),(645,420)],fill='#294b60',width=3)
    text(d,650,80,'45° starting bevel',25,True)
    text(d,650,145,'1.0 mm curved blend',25,True)
    text(d,650,210,'1.5 mm maximum',25,True)
    text(d,650,245,'inward treatment',25,True)
    text(d,650,325,'Flat show face stays',23,False,'#526a7a')
    text(d,650,357,'on the print bed.',23,False,'#526a7a')
    text(d,55,450,'Magnified profile; both axes use the same scale.',22,False,'#526a7a')
    return img

def panel(base,draw,x,y,title,subtitle,img):
    text(draw,x+20,y,title,28,True)
    text(draw,x+20,y+43,subtitle,22,False,'#526a7a')
    base.paste(img,(x,y+80))

new=items(M);old=items(B);frame=old+new
base=Image.new('RGB',(2300,1640),tuple(BG));d=ImageDraw.Draw(base)
text(d,65,35,'PORTABLE PINBALL  /  V1.11',45,True)
text(d,65,98,'Softened front corners  •  Matching part interfaces  •  Small assembled corner test kit',25,False,'#526a7a')
panel(base,d,35,170,'BEFORE — V1.10','Original front-left corner; exact cropped CAD.',render(old,(1100,550),(-1,-1.4,.85),frame))
panel(base,d,1160,170,'AFTER — V1.11','Up to 1.5 mm edge treatment; same camera and scale.',render(new,(1100,550),(-1,-1.4,.85),frame))
panel(base,d,35,870,'SIDE-WALL CORNER PROFILE','A short bevel flows into the curved transition.',section())
panel(base,d,1160,870,'SMALL CORNER TEST KIT','Three sample panels plus two existing mounting pieces.',render(items(M,True),(1100,500),(1,-1.2,1.1)))
text(d,65,1530,'The existing 1 mm lid clearance remains. Test feel, seam alignment and print finish before the full panels.',23,False,'#526a7a')
text(d,65,1570,'Kit pieces are separated in the lower-right view for visibility. Actual CAD geometry.',22,False,'#526a7a')
base.save(O/'cad_preview.png');base.save(O/'changes_preview.png')

manifest=json.loads((O/'parts_manifest.json').read_text())
coupons=[t for t in manifest['tests'] if t['name'].startswith('front_corner_')]
assert len(coupons)==3
base=Image.new('RGB',(2100,900),tuple(BG));d=ImageDraw.Draw(base)
text(d,55,35,'V1.11  /  FRONT CORNER TEST PANELS',39,True)
text(d,55,98,'Exact cropped sections of the finished parts. Use the supplied print orientations.',25,False,'#526a7a')
for i,t in enumerate(coupons):
    x=20+700*i
    label='A1 — SIDE WALL' if 'wall' in t['name'] else 'A2 — FRONT PANEL' if 'panel' in t['name'] else 'A3 — FRONT LID'
    text(d,x+32,185,label,28,True)
    text(d,x+32,232,' × '.join(f'{b:g}' for b in t['bounds'])+' mm',23,False,'#526a7a')
    v,f=stl_mesh(O/'print_first_tests'/(t['name']+'.stl'))
    color=COLORS['lid'] if 'lid' in t['name'] else COLORS['wall']
    base.paste(render([(v,f,color)],(660,440),(.45,-.7,-1.4)),(x+20,290))
text(d,55,790,'The kit also includes the original corner bracket and top block. Assemble with the cabinet hardware.',23,False,'#526a7a')
text(d,55,833,'These three panels are not a self-locking assembly; the mounting pieces reproduce the correct lid spacing.',23,False,'#526a7a')
base.save(O/'fit_test_preview.png')
base=Image.new('RGB',(1800,1200),tuple(BG));d=ImageDraw.Draw(base)
text(d,55,35,'SMALL FRONT CORNER TEST  /  V1.11',40,True)
text(d,55,98,'Three exact panel samples + original mounting pieces',26,False,'#526a7a')
base.paste(render(items(M,True),(1690,850),(1,-1.2,1.1)),(55,165))
text(d,55,1070,'Exploded view for visibility. Assembled lid clearance remains 1 mm.',25,False,'#526a7a')
text(d,55,1118,'Check the softened edges and seam alignment before printing the full cabinet parts.',24,False,'#526a7a')
base.save(O/'front_corner_test_preview.png')
print(json.dumps({'preview':str(O/'cad_preview.png'),'fitTestPreview':str(O/'front_corner_test_preview.png')}))
