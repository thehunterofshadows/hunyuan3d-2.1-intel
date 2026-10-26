#!/usr/bin/env python3
"""Generate named-part, dimensioned VX110 Sport PWC dolly GLB with Python stdlib only.
All dimensions in inches internally. This is a visualization, not a certified load design.
"""
import json, math, struct, pathlib, datetime
ROOT=pathlib.Path(__file__).resolve().parents[2]
OUT=ROOT/'assets'/'vx110-wood-dolly'
OUT.mkdir(parents=True,exist_ok=True)
M=0.0254
parts=[]
materials=[
('Pine frame',[0.65,0.43,0.25,1],0.88),
('Bunk wood',[0.49,0.28,0.13,1],0.9),
('Marine carpet',[0.16,0.25,0.33,1],0.99),
('Steel caster',[0.54,0.59,0.65,1],0.35),
('Polyurethane wheel',[0.07,0.11,0.16,1],0.85),
('Plywood pads and gussets',[0.79,0.61,0.35,1],0.9),
('Bolt heads',[0.82,0.84,0.85,1],0.36),
('Lashing rings',[0.88,0.53,0.17,1],0.48),
('Load braces',[0.57,0.36,0.21,1],0.85)
]
def box(name,center,dims,mat,angle=0):
    x,y,z=center; a,b,c=dims; ca,sa=math.cos(angle),math.sin(angle)
    corners=[(-.5,-.5,-.5),(.5,-.5,-.5),(.5,.5,-.5),(-.5,.5,-.5),
             (-.5,-.5,.5),(.5,-.5,.5),(.5,.5,.5),(-.5,.5,.5)]
    verts=[]
    for px,py,pz in corners:
        u,v,w=px*a,py*b,pz*c
        verts.append((x+u*ca-v*sa,y+u*sa+v*ca,z+w))
    faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(3,7,6,2),(0,4,7,3),(1,2,6,5)]
    # Every face its own vertices for clean flat normals.
    positions=[]; normals=[]; indices=[]
    for quad in faces:
        p=[verts[i] for i in quad]
        ax,ay,az=[p[1][j]-p[0][j] for j in range(3)]
        bx,by,bz=[p[2][j]-p[0][j] for j in range(3)]
        nx,ny,nz=ay*bz-az*by,az*bx-ax*bz,ax*by-ay*bx
        mag=max(math.sqrt(nx*nx+ny*ny+nz*nz),1e-9)
        base=len(positions)
        for v in p: positions.append(v);normals.append((nx/mag,ny/mag,nz/mag))
        indices.extend((base,base+1,base+2,base,base+2,base+3))
    parts.append((name,positions,normals,indices,mat))
def wheel(name,x,y,z,mat=4):
    # Cylinder through X: sidewall discs, segmented tire 5-inch outside diameter.
    p=[];n=[];ix=[];N=20;r=2.5;w=1.6
    for i in range(N):
        t=2*math.pi*i/N;u=2*math.pi*(i+1)/N
        q=[(x-w/2,y+r*math.cos(t),z+r*math.sin(t)),
           (x+w/2,y+r*math.cos(t),z+r*math.sin(t)),
           (x+w/2,y+r*math.cos(u),z+r*math.sin(u)),
           (x-w/2,y+r*math.cos(u),z+r*math.sin(u))]
        base=len(p);p.extend(q)
        n.extend([(0,math.cos(t),math.sin(t))]*4)
        ix.extend([base,base+1,base+2,base,base+2,base+3])
    # capped wheel hubs
    for side,flip in [(-w/2,-1),(w/2,1)]:
        for i in range(N):
            t=2*math.pi*i/N;u=2*math.pi*(i+1)/N
            base=len(p)
            p.extend([(x+side,y,z),(x+side,y+r*math.cos(t),z+r*math.sin(t)),(x+side,y+r*math.cos(u),z+r*math.sin(u))])
            n.extend([(flip,0,0)]*3);ix.extend([base,base+1,base+2] if flip>0 else [base,base+2,base+1])
    parts.append((name,p,n,ix,mat))
def brace(name,x1,y1,x2,y2,z):
    # Inclined 2x4 cross-frame diagonal, run in the X/Y plane.
    dx=x2-x1;dy=y2-y1;length=math.hypot(dx,dy)
    box(name,((x1+x2)/2,(y1+y2)/2,z),(1.5,length,3.5),8,-math.atan2(dx,dy))
# Floor y=0; 5in wheels, 6.3in caster assembly, plywood mounting pads 3/4.
for side in (-1,1):
    x=side*17.25
    box('Base / 2x6 long rail '+('left' if side<0 else 'right'),(x,9.8,0),(1.5,5.5,72),0)
for z,name in [(-35.25,'front'),(-25,'cross A'),(0,'cross middle'),(25,'cross B'),(35.25,'rear')]:
    box('Base / 2x6 '+name,(0,9.8,z),(33,5.5,1.5),0)
# Four reinforced caster bays: a short inner 2x6 runner and two transverse
# 2x6 blocks at the actual caster plate bolt rows. Blocks must be properly
# connected with structural hardware (not screws into end grain alone).
for side in (-1,1):
    for end in (-1,1):
        x=side*9.25
        box('Caster bay / 2x6 inner runner '+str(side)+str(end),(x,9.8,end*30),(1.5,5.5,11),0)
        for dz in (-1.35,1.35):
            box('Caster bay / 2x6 double cross blocking '+str(side)+str(end)+str(dz),
                (side*13.25,9.8,end*32+dz),(7,5.5,1.5),0)
# caster cross-bracing backing plates: ply sits beneath structural framing, bolts pass through.
for side in (-1,1):
    for end in (-1,1):
        x,z=side*14,end*32
        code=('L' if side<0 else 'R')+('F' if end<0 else 'B')
        box('Caster / 3-4in plywood mount '+code,(x,6.675,z),(8,.75,8),5)
        box('Caster / steel top plate '+code,(x,6.24,z),(4.5,.12,4),3)
        box('Caster / swivel fork '+code,(x,4.15,z),(2.4,3.5,1.25),3)
        wheel('Caster / 5in wheel '+code,x,2.5,z)
        box('Caster / brake pedal '+code,(x+1.6,4,z+1.2),(1.3,.24,1.6),7)
        for bx in (-1,1):
            for bz in (-1,1):
                box('Caster / through bolt '+code,(x+bx*1.5,7.25,z+bz*1.35),(.44,.18,.44),6)
# Three riser stations directly over full-width crossmembers; field-cut post heights after trailer measurement.
for side in (-1,1):
    sx='port' if side<0 else 'starboard'
    x=side*11
    for j,z in enumerate((-25,0,25),1):
        box('Support / 2x4 post '+sx+' '+str(j),(x,15.95,z),(3.5,6.8,1.5),1)
        # cross-axis diagonal legs brace each upright to the longitudinal outer base.
        brace('Brace / angled 2x4 '+sx+' '+str(j),side*16.6,12.6,side*11,18.5,z)
        # plywood clamping cheek attaches side of the upright near upper support
        box('Support / 3-4in ply cheek '+sx+' '+str(j),(x-side*2.1,16.7,z),(.75,4.6,5),5)
        box('Support / post cross bolt '+sx+' '+str(j),(x-side*2.5,16.7,z),(.2,.55,.55),6)
    box('Bunk / 2x4 80in '+sx,(x,20.1,0),(3.5,1.5,80),1)
    box('Bunk / marine carpet '+sx,(x,20.93,0),(3.58,.16,80),2)
    for z in (-33,33):
        box('Bunk / recessed stop or tie eye '+sx,(x,20.05,z),(.5,.15,.75),7)
# Four dedicated tie-down plates, mounted to the base rather than the bunks
for side in (-1,1):
    for z in (-27,27):
        box('Tie-down / rated eye plate '+('left' if side<0 else 'right')+str(z),(side*17.25,12.75,z),(1.7,.4,2),7)
# Optional foot chocks are separate removable parts, shown beside aft wheels.
for side in (-1,1):
    box('Safety / removable wheel chock '+('left' if side<0 else 'right'),(side*14,1.1,36),(3.2,2.2,2.4),7)
# GLB writer - y-up meters; each named mesh independent for viewer part selection and notes.
binbuf=bytearray(); meshes=[]; nodes=[]; views=[]; accessors=[]
def append(data,target):
    while len(binbuf)%4:binbuf.append(0)
    off=len(binbuf);binbuf.extend(data)
    v={'buffer':0,'byteOffset':off,'byteLength':len(data),'target':target};views.append(v)
    return len(views)-1
def add_accessor(view,ct,n,kind,mins=None,maxs=None):
    a={'bufferView':view,'componentType':ct,'count':n,'type':kind}
    if mins is not None:a.update(min=mins,max=maxs)
    accessors.append(a);return len(accessors)-1
for name,p,n,ids,material in parts:
    flatp=[v*M for xyz in p for v in xyz]
    pn=append(struct.pack('<%sf'%len(flatp),*flatp),34962)
    nn=append(struct.pack('<%sf'%(3*len(n)),*(v for xyz in n for v in xyz)),34962)
    ind=append(struct.pack('<%sH'%len(ids),*ids),34963)
    mina=[min(pt[j] for pt in p)*M for j in range(3)];maxa=[max(pt[j] for pt in p)*M for j in range(3)]
    a=add_accessor(pn,5126,len(p),'VEC3',mina,maxa)
    b=add_accessor(nn,5126,len(n),'VEC3')
    c=add_accessor(ind,5123,len(ids),'SCALAR')
    meshes.append({'name':name,'primitives':[{'attributes':{'POSITION':a,'NORMAL':b},'indices':c,'material':material}]})
    nodes.append({'name':name,'mesh':len(meshes)-1})
mats=[{'name':n,'pbrMetallicRoughness':{'baseColorFactor':col,'metallicFactor':0.55 if i in (3,6,7) else 0,'roughnessFactor':rough},'doubleSided':False}
      for i,(n,col,rough) in enumerate(materials)]
gltf={'asset':{'version':'2.0','generator':'VX110 wood dolly named parts / standard library'},'scene':0,'scenes':[{'nodes':list(range(len(nodes)))}],
      'nodes':nodes,'meshes':meshes,'materials':mats,'buffers':[{'byteLength':len(binbuf)}],
      'bufferViews':views,'accessors':accessors}
js=json.dumps(gltf,separators=(',',':')).encode('utf-8')
js+=b' ' *((4-len(js)%4)%4);binbuf.extend(b'\0'*((4-len(binbuf)%4)%4))
glb=struct.pack('<4sII',b'glTF',2,12+8+len(js)+8+len(binbuf))+struct.pack('<I4s',len(js),b'JSON')+js+struct.pack('<I4s',len(binbuf),b'BIN\0')+binbuf
(OUT/'vx110-wood-dolly.glb').write_bytes(glb)
print('Generated',OUT/'vx110-wood-dolly.glb',len(glb),'bytes',len(parts),'named parts')
