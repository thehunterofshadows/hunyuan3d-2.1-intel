"""Independent read-only audit of V1.11 front-corner rounding and cropped test kit.

Run with the existing CAD virtualenv Python. No builder is imported or executed.
The audit reads exported STEP/STL/meshes and prints JSON; it never changes exports.
Geometric checks do not establish physical fit or surface feel.
"""
from pathlib import Path
from collections import defaultdict
import hashlib
import json
import math
import struct
import numpy as np
import cadquery as cq

CAD = Path(__file__).resolve().parents[1] / 'cad'
NEW = CAD / 'portable-pinball-v1_11' / 'exports'
OLD = CAD / 'portable-pinball-v1_10' / 'exports'
EXPECTED = {'left_front_wall', 'right_front_wall', 'front_button_panel', 'front_cable_lid'}

def near(a, b, tolerance=1e-4):
    assert abs(float(a) - float(b)) <= tolerance, (a, b, tolerance)

def box(x, y, z, dx, dy, dz):
    return cq.Workplane('XY').box(dx, dy, dz, centered=False).translate((x, y, z)).val()

def volume(shape):
    return sum(s.Volume() for s in shape.Solids())

def difference(a, b):
    return volume(a.cut(b)) + volume(b.cut(a))

def mirror(shape, side):
    return shape if side == 'left' else shape.mirror('YZ', (130, 0, 0))

def bounds(shape):
    b = shape.BoundingBox()
    return np.array([b.xmin, b.ymin, b.zmin, b.xmax, b.ymax, b.zmax])

def stl(path):
    data = path.read_bytes()
    count = struct.unpack_from('<I', data, 80)[0]
    assert len(data) == 84 + 50 * count, (path, 'binary STL length')
    return np.array([struct.unpack_from('<12fH', data, 84 + 50 * i)[3:12] for i in range(count)]).reshape(-1, 3, 3)

def topology(path):
    tri = stl(path)
    areas = np.linalg.norm(np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]), axis=1) / 2
    assert areas.min() > 1e-10, (path, 'degenerate triangle')
    verts, indices = np.unique(np.round(tri.reshape(-1, 3), 5), axis=0, return_inverse=True)
    faces = indices.reshape(-1, 3)
    edges = defaultdict(list)
    for i, face in enumerate(faces):
        for a, b in zip(face, np.roll(face, -1)):
            assert a != b, (path, 'collapsed edge')
            edges[tuple(sorted((int(a), int(b))))].append((i, 1 if a < b else -1))
    assert all(len(e) == 2 for e in edges.values()), (path, 'open or nonmanifold edge')
    assert all(e[0][1] + e[1][1] == 0 for e in edges.values()), (path, 'inconsistent winding')
    parent = list(range(len(faces)))
    def root(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    for edge in edges.values():
        a, b = root(edge[0][0]), root(edge[1][0])
        parent[b] = a
    assert len({root(i) for i in range(len(faces))}) == 1, (path, 'disconnected shells')
    vol = float(np.einsum('ij,ij->i', tri[:, 0], np.cross(tri[:, 1], tri[:, 2])).sum() / 6)
    assert vol > 0, (path, 'nonpositive signed volume')
    lo, hi = tri.min(axis=(0, 1)), tri.max(axis=(0, 1))
    dims = hi - lo
    assert lo[2] >= -1e-5, (path, 'below print bed')
    assert dims[0] + 16 < 325.001 and dims[1] + 16 < 325.001 and dims[2] < 315.001, (path, 'printer bounds')
    return tri, {'name': path.stem, 'triangles': len(tri), 'volume_mm3': round(vol, 6), 'print_size_mm': np.round(dims, 6).tolist()}

# Independent V1.11 export, geometry, assembly and print-orientation checks.
manifest = json.loads((NEW / 'parts_manifest.json').read_text())
old_manifest = json.loads((OLD / 'parts_manifest.json').read_text())
params = manifest['parameters']
meshes = {m['name']: m for m in json.loads((NEW/'preview_meshes.json').read_text())}
old_meshes = {m['name']: m for m in json.loads((OLD/'preview_meshes.json').read_text())}
names = [p['name'] for p in manifest['parts']]
assert len(names) == 45 and set(names) == set(meshes) == set(old_meshes)
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
changed = sorted(n for n in names if sha(NEW/'enclosure_stl'/(n+'.stl')) != sha(OLD/'enclosure_stl'/(n+'.stl')))
assert set(changed) == EXPECTED, changed
old_meta = {p['name']: p for p in old_manifest['parts']}
for p in manifest['parts']:
    if p['name'] not in EXPECTED:
        assert p == old_meta[p['name']], (p['name'], 'unchanged part metadata')
        assert meshes[p['name']] == old_meshes[p['name']], (p['name'], 'unchanged preview geometry')
old_tests = {p.stem:p for p in (OLD/'print_first_tests').glob('*.stl')}
new_tests = {p.stem:p for p in (NEW/'print_first_tests').glob('*.stl')}
assert set(old_tests) <= set(new_tests)
assert len(new_tests) == 20
extra_tests = sorted(set(new_tests)-set(old_tests))
assert len(extra_tests) == 3
def canonical(tri):
    return sorted(tuple(sorted(tuple(np.round(v,6)) for v in face)) for face in tri)
for name,path in old_tests.items():
    assert sha(path)==sha(new_tests[name]),(name,'inherited sample bytes changed')
    assert canonical(stl(path)) == canonical(stl(new_tests[name])), (name, 'inherited sample changed')
files = sorted((NEW/'enclosure_stl').glob('*.stl')) + sorted((NEW/'print_first_tests').glob('*.stl'))
assert len(files) == 65
triangles,mesh_rows = {},[]
for path in files:
    tri,row = topology(path)
    near(tri[:,:,2].min(),0,1e-5)
    triangles[path.stem] = tri
    mesh_rows.append(row)
print('Exactly four changed enclosure STLs; 41 enclosure parts and 17 previous samples preserved. All 65 STLs are valid closed shells and start on the bed.',flush=True)
def imported_parts(folder,meta,mesh):
    solids = cq.importers.importStep(str(folder/'mini_vpin_assembly.step')).solids().vals()
    parts = {}
    for i,p in enumerate(meta['parts']):
        s = solids[i]
        assert s.isValid() and len(s.Solids()) == 1,p['name']
        near(s.Volume(),p['volume'],.002)
        vs=np.array(mesh[p['name']]['v'])
        assert np.max(abs(bounds(s)-np.r_[vs.min(axis=0),vs.max(axis=0)]))<.12,(p['name'],'STEP/preview bounds')
        parts[p['name']]=s
    return parts,solids[len(meta['parts']):]
parts,references=imported_parts(NEW,manifest,meshes)
prior,old_references=imported_parts(OLD,old_manifest,old_meshes)
# Every changed solid is strictly subtractive; it cannot invade existing interior clearance.
part_rows=[]
for name in changed:
    old,new=prior[name],parts[name]
    added=volume(new.cut(old))
    removed=volume(old.cut(new))
    near(added,0,.002)
    assert removed>.01,(name,'unchanged exact solid')
    part_rows.append({'name':name,'added_mm3':round(added,6),'removed_mm3':round(removed,6)})
# No changed part collides with any printed component.
for name in changed:
    a=parts[name];ba=bounds(a)
    for other,b in parts.items():
        if name==other:continue
        bb=bounds(b)
        if np.any(np.minimum(ba[3:],bb[3:])-np.maximum(ba[:3],bb[:3])<1e-5):continue
        near(volume(a.intersect(b)),0,.002)
# Confirm every non-exterior addition, screw region, control region and lid support is retained.
protected={}
for side in ['left','right']:
    name=side+'_front_wall'
    # Complete controls, reinforcement and notched-floor interface start far behind front corner.
    probe=mirror(box(-.1,70,-1,8.2,172,162),side)
    protected[name+'_controls_and_floor']=difference(parts[name].intersect(probe),prior[name].intersect(probe))
    # Fastener regions at Y14 (corner),31/56 (top blocks),24 (floor shelf) remain untouched.
    for y,z in [(14,24),(14,56),(31,75+25*math.tan(math.radians(10))-8),(56,75+50*math.tan(math.radians(10))-8),(24,8)]:
        probe=mirror(box(-.1,y-3,z-3,8.2,6,6),side)
        protected[name+f'_mount_{y}_{z:.3f}']=difference(parts[name].intersect(probe),prior[name].intersect(probe))
for x in [14,246]:
    for z in [24,56]:
        probe=box(x-3,-.1,z-3,6,4.2,6)
        protected[f'front_panel_mount_{x}_{z}']=difference(parts['front_button_panel'].intersect(probe),prior['front_button_panel'].intersect(probe))
for x in [110,160,210]:
    probe=box(x-16,-.1,10,32,4.2,32)
    protected[f'front_panel_button_{x}']=difference(parts['front_button_panel'].intersect(probe),prior['front_button_panel'].intersect(probe))
for key,value in protected.items():near(value,0,.002)
print('Exact STEP subset checks, fastener/control regions and changed-part collision checks passed.',flush=True)

def rotation_matrix(mode):
    a=math.radians(180-10 if mode=='top' else -90 if mode=='side_outer_left' else 90)
    c,s=math.cos(a),math.sin(a)
    if mode in ('side','side_outer_left'):
        return np.array([[c,0,s],[0,1,0],[-s,0,c]],float)
    if mode in ('end','top'):
        return np.array([[1,0,0],[0,c,-s],[0,s,c]],float)
    if mode=='flat':return np.eye(3)
    raise ValueError(mode)

def orient_solid(s,mode):
    if mode in ('side','side_outer_left'):
        s=s.rotate((0,0,0),(0,1,0),-90 if mode=='side_outer_left' else 90)
    elif mode in ('end','top'):
        s=s.rotate((0,0,0),(1,0,0),90 if mode=='end' else 170)
    elif mode!='flat':
        raise ValueError(mode)
    b=bounds(s)
    return s.translate(tuple(-b[:3])),b[:3]

# Only new cut surfaces are checked; inherited mounting ledges retain their prior print caveats.
normal_rows=[]
meta={p['name']:p for p in manifest['parts']}
for name in changed:
    mode=meta[name]['mode']
    expected_printed,shift=orient_solid(parts[name],mode)
    tri=triangles[name]
    tri_bounds=np.r_[tri.min(axis=(0,1)),tri.max(axis=(0,1))]
    assert np.max(abs(bounds(expected_printed)-tri_bounds))<.1,(name,'actual STL/CAD print transform')
    R=rotation_matrix(mode)
    centers=tri.mean(axis=1)
    world=(centers+shift)@R
    normals=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0])
    lens=np.linalg.norm(normals,axis=1)
    normals/=lens[:,None]
    shell=prior[name].Shells()[0]
    # Broad-phase first: only downward faces above bed can make a print overhang.
    candidates=np.where((normals[:,2]<-1e-6)&(centers[:,2]>1e-4))[0]
    inspected=[]
    for i in candidates:
        if shell.distance(cq.Vertex.makeVertex(*world[i]))>.003:
            inspected.append(i)
    if inspected:
        normal_z=normals[inspected,2]
        worst=float(np.max(np.arcsin(np.clip(-normal_z,0,1)))*180/math.pi)
        assert worst<=45.02,(name,'new surface overhang beyond 45 degrees',worst)
    else:
        worst=0
    normal_rows.append({'name':name,'new_downward_facets_checked':len(inspected),'maximum_new_downward_surface_angle_from_vertical_degrees':round(worst,6),'actual_stl_print_origin_z_mm':round(float(tri[:,:,2].min()),7)})
print('New exported downward facets stay at or below 45 degrees in each actual print orientation.',flush=True)

# Cross-sections are measured from re-imported STEP, not from the builder functions.
def ray_range(shape,axis,fixed,lo,hi):
    a=list(fixed);b=list(fixed);a[axis]=lo;b[axis]=hi
    line=cq.Edge.makeLine(cq.Vector(*a),cq.Vector(*b))
    vertices=shape.intersect(line).Vertices()
    assert vertices,('empty material ray',axis,fixed,lo,hi)
    values=[v.Center().toTuple()[axis] for v in vertices]
    return min(values),max(values)

def eased_profile(u,depth=1.5,radius=1.0,slope=0.0):
    angle=math.atan(slope)
    cx=depth+radius*math.sin(angle)
    cy=-slope*depth+radius*math.cos(angle)
    join=cx-radius/math.sqrt(2)
    intercept=cx+cy-radius*math.sqrt(2)
    if u<=join:return intercept-u
    if u>=depth:return -slope*u
    return cy-math.sqrt(radius*radius-(u-cx)**2)

slope=math.tan(math.radians(10))
profile_rows=[]
for side in ['left','right']:
    for u in [.05,.4,.75,.9,1.15,1.45,1.6]:
        x=u if side=='left' else 260-u
        measured=ray_range(parts[side+'_front_wall'],1,(x,0,40),-1,6)[0]
        expected=eased_profile(u)
        near(measured,expected,2e-5)
        profile_rows.append({'feature':side+'_vertical_front_corner','inward_mm':u,'measured_setback_mm':round(measured,6),'expected_setback_mm':round(expected,6)})
# The continuous front lip has the same cross-section on both walls and the panel.
for x,name in [(2,'left_front_wall'),(60,'front_button_panel'),(258,'right_front_wall')]:
    for u in [.05,.4,.8,1.0,1.2,1.45,1.7,3]:
        top=ray_range(parts[name],2,(x,u,0),60,90)[1]
        expected=75-eased_profile(u,slope=slope)
        near(top,expected,2e-5)
        profile_rows.append({'feature':name+'_shared_upper_front_lip','depth_y_mm':u,'measured_top_z_mm':round(top,6),'expected_top_z_mm':round(expected,6)})
# Adjacent thin slabs at the butt seam have identical material silhouettes.
seam_rows=[]
for side,x in [('left',4),('right',256)]:
    wall=parts[side+'_front_wall'];panel=parts['front_button_panel'];w=.001
    if side=='left':
        wall_slab=wall.intersect(box(x-w,0,-1,w,4,160))
        panel_slab=panel.intersect(box(x,0,-1,w,4,160)).translate((-w,0,0))
    else:
        wall_slab=wall.intersect(box(x,0,-1,w,4,160))
        panel_slab=panel.intersect(box(x-w,0,-1,w,4,160)).translate((w,0,0))
    delta=difference(wall_slab,panel_slab)
    near(delta,0,1e-5)
    seam_rows.append({'side':side,'join_x_mm':x,'wall_and_panel_seam_profiles_equal':True,'comparison_slab_thickness_mm':w,'difference_mm3':round(delta,8)})
near(difference(parts['left_front_wall'].mirror('YZ',(130,0,0)),parts['right_front_wall']),0,.003)
# Outer treatment must be limited to the chosen front areas.
front_vertical=box(-.01,-.01,-1,1.52,1.52,165)
upper_front=box(-.01,-.01,73,4.02,1.52,8)
for side in ['left','right']:
    removed=prior[side+'_front_wall'].cut(parts[side+'_front_wall'])
    allowed=mirror(front_vertical.fuse(upper_front),side)
    near(volume(removed.cut(allowed)),0,.003)
removed_front=prior['front_button_panel'].cut(parts['front_button_panel'])
near(volume(removed_front.cut(box(3.99,-.01,73,252.02,1.52,8))),0,.003)
# Retained lid seats, rear bezel joint and monitor stop; all checks use assembled geometry.
lid=parts['front_cable_lid'];old_lid=prior['front_cable_lid']
lid_local=lid.translate((0,0,-76)).rotate((0,0,0),(1,0,0),-10)
old_lid_local=old_lid.translate((0,0,-76)).rotate((0,0,0),(1,0,0),-10)
inner_seat=box(2,2,-40,256,70,42.45)
near(difference(lid_local.intersect(inner_seat),old_lid_local.intersect(inner_seat)),0,.003)
rear=box(-1,62,40,262,6,70)
near(difference(lid.intersect(rear),old_lid.intersect(rear)),0,.003)
stop=box(225,58,40,22,8,80)
near(difference(lid.intersect(stop),old_lid.intersect(stop)),0,.003)
for x in [10,250]:
    for y in [25,50]:
        probe=box(x-4,y/math.cos(math.radians(10))-4,-10,8,8,20)
        near(difference(lid_local.intersect(probe),old_lid_local.intersect(probe)),0,.003)
gap_rows=[]
for name,x,y in [('left_front_wall',3,10),('front_button_panel',60,3),('right_front_wall',257,10)]:
    low=ray_range(parts[name],2,(x,y,0),-1,100)[1]
    high=ray_range(lid,2,(x,y,0),50,110)[0]
    near(high-low,1,1e-5)
    gap_rows.append({'part':name,'probe_xy_mm':[x,y],'vertical_gap_mm':round(high-low,6)})
# Lid base outline matches the wall corner with the existing 10-degree plate transform.
for side in ['left','right']:
    for u in [.05,.4,.75,.9,1.15,1.45,1.6]:
        x=u if side=='left' else 260-u
        local_front=ray_range(lid_local,1,(x,0,.5),-1,6)[0]
        near(local_front*math.cos(math.radians(10)),eased_profile(u),2e-5)
# A smaller one-millimeter lid rim avoids intersecting the tiny curved plan corner.
for u in [.05,.2,.4,.65,.9,1.1]:
    measured=ray_range(lid_local,1,(60,0,4-u),-1,6)[0]
    near(measured,eased_profile(u,depth=1),2e-5)
    left=ray_range(lid_local,0,(0,20,4-u),-1,6)[0]
    right=260-ray_range(lid_local,0,(0,20,4-u),254,261)[1]
    near(left,eased_profile(u,depth=1),2e-5)
    near(right,eased_profile(u,depth=1),2e-5)
# Mirrored removal at the front lid corners; the existing right monitor stop is unchanged.
lid_removed=old_lid.cut(lid)
near(difference(lid_removed,lid_removed.mirror('YZ',(130,0,0))),0,.003)
print('Independent wall/lip/lid profile rays, matching butt seams, lid gap and protected lid seats passed.',flush=True)


def distances_to_mesh(points,triangles,chunk=64):
    """Euclidean distances to actual triangle surfaces, using plane and edge projections."""
    a,b,c=triangles[:,0],triangles[:,1],triangles[:,2]
    ab,ac=b-a,c-a
    normal=np.cross(ab,ac)
    n2=np.einsum('ij,ij->i',normal,normal)
    d00=np.einsum('ij,ij->i',ab,ab)
    d01=np.einsum('ij,ij->i',ab,ac)
    d11=np.einsum('ij,ij->i',ac,ac)
    denom=d00*d11-d01*d01
    good=abs(denom)>1e-18
    result=[]
    for start in range(0,len(points),chunk):
        p=points[start:start+chunk,None,:]
        rel=p-a[None,:,:]
        d20=np.einsum('bti,ti->bt',rel,ab)
        d21=np.einsum('bti,ti->bt',rel,ac)
        v=np.divide(d11*d20-d01*d21,denom,out=np.zeros_like(d20),where=good)
        w=np.divide(d00*d21-d01*d20,denom,out=np.zeros_like(d20),where=good)
        inside=good[None,:]&(v>=-1e-10)&(w>=-1e-10)&(v+w<=1+1e-10)
        signed=np.einsum('bti,ti->bt',rel,normal)
        best=np.where(inside,signed*signed/n2,np.inf)
        for e,f in [(a,b),(b,c),(c,a)]:
            direction=f-e
            length2=np.einsum('ij,ij->i',direction,direction)
            q=p-e[None,:,:]
            t=np.clip(np.einsum('bti,ti->bt',q,direction)/length2,0,1)
            error=q-t[:,:,None]*direction[None,:,:]
            best=np.minimum(best,np.einsum('bti,bti->bt',error,error))
        result.extend(np.sqrt(best.min(axis=1)).tolist())
    return np.array(result)

kit=json.loads((NEW/'front_corner_kit.json').read_text())
assert kit['new_sample_count']==3 and kit['kit_stl_count_including_reused_mounts']==5
assert set(kit['reused_mounts'])=={'corner_left_front_56.stl','top_block_left_25.stl'}
near(kit['lid_vertical_clearance_mm'],1)
assert {r['file'][:-4] for r in kit['samples']}==set(extra_tests)
expected_sources={'front_corner_wall_fit':'left_front_wall','front_corner_panel_fit':'front_button_panel','front_corner_lid_fit':'front_cable_lid'}
crop=box(0,-1,40,40,41,60)
sample_rows=[]
assembly_samples={}
for row in kit['samples']:
    name=row['file'][:-4]
    assert row['source_part']==expected_sources[name]
    assert row['crop_min_mm']==[0,-1,40] and row['crop_max_mm']==[40,40,100]
    assert row['print_mode']==meta[row['source_part']]['mode']
    sampled=parts[row['source_part']].intersect(crop)
    assert sampled.isValid() and len(sampled.Solids())==1,name
    assembly_samples[name]=sampled
    expected_printed,_=orient_solid(sampled,row['print_mode'])
    tri=triangles[name]
    # Use direct mesh/surface metrics: Boolean subtraction of nearly coincident
    # faceted STL and analytic CAD can create invalid OCC fragments.
    mesh_volume=float(np.einsum('ij,ij->i',tri[:,0],np.cross(tri[:,1],tri[:,2])).sum()/6)
    delta=abs(mesh_volume-expected_printed.Volume())
    assert delta<.5,(name,'STL volume differs from exact crop',delta)
    actual_bounds=np.r_[tri.min(axis=(0,1)),tri.max(axis=(0,1))]
    assert np.max(abs(actual_bounds-bounds(expected_printed)))<.0002,(name,'STL crop bounds')
    shell=expected_printed.Shells()[0]
    verts=np.unique(tri.reshape(-1,3),axis=0)
    worst=max(shell.distance(cq.Vertex.makeVertex(*point)) for point in verts)
    assert worst<.0002,(name,'STL vertex off exact crop surface',worst)
    cad_vertices,cad_faces=expected_printed.tessellate(.02,.06)
    cad_vertices=np.array([v.toTuple() for v in cad_vertices])
    cad_triangles=cad_vertices[np.array(cad_faces)]
    surface_samples=np.r_[cad_vertices,cad_triangles.mean(axis=1)]
    reverse=float(distances_to_mesh(surface_samples,tri).max())
    assert reverse<.055,(name,'CAD surface missing from actual STL',reverse)
    dims=np.ptp(tri.reshape(-1,3),axis=0)
    near(dims[2],4,1e-5)
    sample_rows.append({'name':name,'source_part':row['source_part'],'actual_print_size_mm':np.round(dims,6).tolist(),'exact_cad_crop_mm':{'min':[0,-1,40],'max':[40,40,100]},'stl_volume_difference_mm3':round(delta,6),'maximum_stl_vertex_distance_from_exact_crop_mm':round(worst,8),'maximum_sampled_cad_surface_distance_from_stl_mm':round(reverse,8),'cad_surface_points_checked':len(surface_samples),'outside_face_down':True})
for name in ['corner_left_front_56','top_block_left_25']:
    near(volume(parts[name].cut(crop)),0,.003)
    assert sha(NEW/'enclosure_stl'/(name+'.stl'))==sha(OLD/'enclosure_stl'/(name+'.stl'))
    assembly_samples[name]=parts[name]
# The five actual kit parts fit together without added sample-only geometry or intersections.
for i,(name,a) in enumerate(assembly_samples.items()):
    for other,b in list(assembly_samples.items())[i+1:]:
        near(volume(a.intersect(b)),0,.002)
contacts=[('front_corner_wall_fit','front_corner_panel_fit'),
          ('front_corner_wall_fit','corner_left_front_56'),
          ('front_corner_panel_fit','corner_left_front_56'),
          ('front_corner_wall_fit','top_block_left_25'),
          ('front_corner_lid_fit','top_block_left_25')]
for a,b in contacts:
    near(assembly_samples[a].distance(assembly_samples[b]),0,1e-5)
# The printed lid sample includes the original retaining hole; the block makes the real 1 mm gap.
for name,x,y in [('front_corner_wall_fit',3,10),('front_corner_panel_fit',30,3)]:
    low=ray_range(assembly_samples[name],2,(x,y,0),39,100)[1]
    high=ray_range(assembly_samples['front_corner_lid_fit'],2,(x,y,0),50,110)[0]
    near(high-low,1,1e-5)
print('Three exact cropped skins assemble with the two unchanged supports, retaining real seams, screw interfaces and the 1 mm lid gap.',flush=True)
report={
    'status':'PASS',
    'evidence':'Independent exported STL topology/normals, immutable V1.10 comparison, re-imported STEP cross-sections, matched seams, exact corner crops and assembled kit.',
    'printed_parts':45,
    'fit_samples':20,
    'changed_enclosure_parts':changed,
    'unchanged_enclosure_part_stl_bytes_preview_meshes_and_manifest_records':41,
    'unchanged_inherited_sample_stl_bytes_and_geometries':17,
    'all_65_stls_closed_consistently_wound_single_shell_positive_volume_in_printer_volume_and_on_bed':True,
    'changed_solids_are_subsets_of_prior_solids':True,
    'changed_part_removed_volume':part_rows,
    'changed_parts_clear_all_other_printed_parts':True,
    'fasteners_controls_flipper_reinforcement_floor_interface_and_lid_seats_preserved':True,
    'wall_and_panel_profile_measures':profile_rows,
    'new_edge_print_angles':normal_rows,
    'matched_front_butt_seams':seam_rows,
    'lid_vertical_clearance':gap_rows,
    'lid_plan_corner_matches_wall_profile':True,
    'lid_top_rim_depth_mm':1.0,
    'wall_and_front_lip_depth_mm':1.5,
    'blend_radius_mm':1.0,
    'lid_rear_bezel_junction_and_monitor_stop_preserved':True,
    'corner_samples':sample_rows,
    'corner_kit_parts':list(assembly_samples),
    'corner_kit_support_contacts':contacts,
    'corner_kit_zero_intersections':True,
    'physical_limit':'Actual printed fit, fastener engagement, surface feel and print quality require the supplied small five-part kit. New easing geometry does not remove inherited print caveats such as the recessed nudge mounting ledge.'
}
print(json.dumps(report,indent=2))
