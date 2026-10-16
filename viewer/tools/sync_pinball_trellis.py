#!/usr/bin/env python3
"""Sync five real TRELLIS.2 meshes from Skynet and register them in Intel 3D Studio."""
import hashlib,json,struct,subprocess
from pathlib import Path
ROOT=Path('/home/justin/projects/hunyuan3d-2.1-intel')
ASSETS=ROOT/'assets'
SITE=ROOT/'viewer/site/app.js'
DOCKER=ROOT/'viewer/Dockerfile'
ITEMS=[
 ('flipper','Flipper bat','Classic white bat with red rebound rubber'),
 ('plunger','Ball launcher / plunger','Steel spring-loaded launcher with red pull knob'),
 ('slingshot','Slingshot bumper','Triangular rebound bumper and metal guide posts'),
 ('target','Drop target','Yellow stand-up drop target with hinge'),
 ('pop-bumper','Pop bumper','Red-cap pop bumper for the pinball playfield'),
]
def check_model(path):
    with path.open('rb') as f:
        h=f.read(12)
        if len(h)!=12 or h[:4]!=b'glTF':raise ValueError(f'Invalid GLB: {path}')
        _,ver,length=struct.unpack('<4sII',h)
        if ver!=2 or length!=path.stat().st_size:raise ValueError(f'Invalid GLB length: {path}')
        size,kind=struct.unpack('<I4s',f.read(8))
        obj=json.loads(f.read(size))
        tris=0
        for mesh in obj.get('meshes',[]):
            for prim in mesh.get('primitives',[]):
                ids=prim.get('indices')
                if ids is not None:tris+=obj['accessors'][ids]['count']//3
                else:tris+=obj['accessors'][prim['attributes']['POSITION']]['count']//3
        if tris<1000:raise ValueError(f'Unexpectedly small mesh: {path}')
        return tris
def sync():
    for slug,name,description in ITEMS:
        root=ASSETS/f'trellis-pinball-{slug}'
        root.mkdir(parents=True,exist_ok=True)
        src=f'/home/justin/ai/trellis2/output/pinball-{slug}-trellis2-512.glb'
        target=root/(slug+'.glb')
        subprocess.run(['scp','-q','-o','BatchMode=yes',f'justin@skynet:{src}',str(target)],check=True)
        ref=root/'reference.png'
        subprocess.run(['scp','-q','-o','BatchMode=yes',f'justin@skynet:/home/justin/projects/trellis2-intel-lab/inputs/{slug}-reference.png',str(ref)],check=True)
        tris=check_model(target)
        digest=hashlib.sha256(target.read_bytes()).hexdigest()
        (root/'README.md').write_text(f'# {name} · TRELLIS.2 pinball test\n\nActual TRELLIS.2 generated mesh on Skynet, Intel Arc Pro B70, Vulkan, trellis.cpp v0.8.1.\n512 geometry resolution; seed 42; 12 steps; 2048 atlas. Input is original illustrative reference.\n{tris:,} triangles; {target.stat().st_size:,} bytes; SHA256 {digest}.\n\nEvaluation mesh, not print-ready, physics-ready or gameplay-optimized. GLB downloaded from Studio is the original.\n')
        print(slug,format(tris,','),'triangles',target.stat().st_size,'bytes')
    app=SITE.read_text()
    if "id:'trellis-pinball-flipper'" not in app:
        rows=[]
        for slug,name,description in ITEMS:
            rows.append(" {id:'trellis-pinball-"+slug+"',name:'"+name+" · TRELLIS.2',type:'Pinball component · Arc B70 Vulkan',file:'"+slug+".glb',front:0,reference:'/models/trellis-pinball-"+slug+"/reference.png',thumbnail:'/models/trellis-pinball-"+slug+"/reference.png',textureLabel:'2048px textures',note:'Actual TRELLIS.2 mesh reconstructed from an original illustrated "+description.lower()+" reference. 512-resolution exploratory output. Geometry and surfaces may differ from the input; not optimized or mechanically functional.'},")
        app=app.replace(" {id:'trellis-woman',",'\n'.join(rows)+"\n {id:'trellis-woman',",1)
        assert "id:'trellis-pinball-pop-bumper'" in app
    app=app.replace("entry.id==='trellis-bumper'", "['trellis-bumper','trellis-pinball-pop-bumper'].includes(entry.id)")
    app=app.replace("'AI-generated input, not the reconstructed mesh.'", "entry.id.startsWith('trellis-pinball-')?'Illustrated source reference, not the reconstructed model.':'AI-generated input, not the reconstructed mesh.'")
    SITE.write_text(app)
    docker=DOCKER.read_text()
    marker='COPY assets/portable-pinball /usr/share/nginx/html/models/portable-pinball'
    if 'assets/trellis-pinball-flipper' not in docker:
        inserts='\n'.join(f'COPY assets/trellis-pinball-{slug} /usr/share/nginx/html/models/trellis-pinball-{slug}' for slug,_,_ in ITEMS)
        assert marker in docker
        docker=docker.replace(marker,marker+'\n'+inserts)
        DOCKER.write_text(docker)
    print('Five assets registered in viewer source and Dockerfile.')
if __name__=='__main__':sync()
