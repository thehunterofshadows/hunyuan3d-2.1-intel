"""Independent read-only audit of exported V1.10 nudge recess and fit coupons.

Run with the existing CAD virtualenv Python. No builder is imported or executed.
The audit reads exported STEP/STL/meshes and prints JSON; it never changes exports.
Switch/keycap dimensions are assumptions, not a measurement of installed hardware.
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
NEW = CAD / 'portable-pinball-v1_10' / 'exports'
OLD = CAD / 'portable-pinball-v1_9' / 'exports'
EXPECTED = {'left_front_wall', 'right_front_wall'}

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

def printed(shape):
    shape = shape.rotate((0, 0, 0), (0, 1, 0), -90)
    b = shape.BoundingBox()
    return shape.translate((-b.xmin, -b.ymin, -b.zmin))

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

def flat_area(tri, axis, level):
    mask = np.all(abs(tri[:, :, axis] - level) < 1e-5, axis=1)
    return float(np.linalg.norm(np.cross(tri[mask, 1] - tri[mask, 0], tri[mask, 2] - tri[mask, 0]), axis=1).sum() / 2)

def stl_solid(tri):
    faces = [cq.Face.makeFromWires(cq.Wire.makePolygon([cq.Vector(*p) for p in t] + [cq.Vector(*t[0])])) for t in tri]
    solid = cq.Solid.makeSolid(cq.Shell.makeShell(faces)).clean()
    assert solid.isValid() and len(solid.Solids()) == 1, 'coupon STL did not reconstruct as one valid solid'
    return solid

def thickness(shape, y, z):
    w = .02
    return volume(shape.intersect(box(-1, y-w/2, z-w/2, 262, w, w))) / (w*w)

def planar_area(shape, axis, level):
    area = 0
    for face in shape.Faces():
        b = bounds(face)
        if max(abs(b[axis]-level), abs(b[axis+3]-level)) < 1e-5:
            area += face.Area()
    return area

manifest = json.loads((NEW / 'parts_manifest.json').read_text())
old_manifest = json.loads((OLD / 'parts_manifest.json').read_text())
meshes = {m['name']: m for m in json.loads((NEW / 'preview_meshes.json').read_text())}
old_meshes = {m['name']: m for m in json.loads((OLD / 'preview_meshes.json').read_text())}
names = [p['name'] for p in manifest['parts']]
assert len(names) == 45 and set(names) == set(meshes) == set(old_meshes)
assert len(manifest['tests']) == 17
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
stl_changed = [n for n in names if sha(NEW/'enclosure_stl'/(n+'.stl')) != sha(OLD/'enclosure_stl'/(n+'.stl'))]
mesh_changed = [n for n in names if meshes[n] != old_meshes[n]]
assert set(stl_changed) == set(mesh_changed) == EXPECTED, (stl_changed, mesh_changed)
old_parts = {p['name']: p for p in old_manifest['parts']}
for p in manifest['parts']:
    if p['name'] not in EXPECTED:
        assert p == old_parts[p['name']], p['name']
print('STL bytes, preview meshes and manifest: exactly two changed walls; 43 unchanged parts.', flush=True)

files = sorted((NEW/'enclosure_stl').glob('*.stl')) + sorted((NEW/'print_first_tests').glob('*.stl'))
assert len(files) == 62
triangles, mesh_rows = {}, []
for path in files:
    tri, row = topology(path)
    triangles[path.stem] = tri
    mesh_rows.append(row)
old_tests = {p.stem:p for p in (OLD/'print_first_tests').glob('*.stl')}
new_tests = {p.stem:p for p in (NEW/'print_first_tests').glob('*.stl')}
assert set(new_tests)-set(old_tests) == {'nudge_switch_fit'}
assert set(old_tests)-set(new_tests) == {'nudge_mx_14p1'}
def canonical(tri):
    return sorted(tuple(sorted(tuple(np.round(v, 6)) for v in face)) for face in tri)
test_geometry_changed = sorted(n for n in set(new_tests)&set(old_tests) if canonical(stl(new_tests[n])) != canonical(stl(old_tests[n])))
assert test_geometry_changed == ['flipper_nudge_wall_sample', 'nudge_mx_14p0', 'nudge_mx_14p2'], test_geometry_changed

def imported_parts(folder, meta, mesh):
    solids = cq.importers.importStep(str(folder/'mini_vpin_assembly.step')).solids().vals()
    assert len(solids) >= 64
    parts = {}
    for i, p in enumerate(meta['parts']):
        s = solids[i]
        assert s.isValid() and len(s.Solids()) == 1, p['name']
        near(s.Volume(), p['volume'], .001)
        verts = np.array(mesh[p['name']]['v'])
        expected = np.r_[verts.min(axis=0), verts.max(axis=0)]
        assert np.max(abs(bounds(s)-expected)) < .1, (p['name'], 'STEP/mesh bounds mismatch')
        parts[p['name']] = s
    return parts, solids[len(meta['parts']):]

parts, references = imported_parts(NEW, manifest, meshes)
prior, old_references = imported_parts(OLD, old_manifest, old_meshes)
print('Re-imported both STEP assemblies; checking actual cut surfaces and original pedestal.', flush=True)

# Independently restore the old inner pocket, then subtract only the requested well.
well = cq.Workplane('YZ', origin=(0,136,30)).rect(23,23).workplane(offset=2.5).rect(18,18).loft().val()
restore = box(1.5,127.7,21.7,2.5,16.6,16.6)
through = box(-1,128.95,22.95,10,14.1,14.1)
wall_rows = []
for side in ('left','right'):
    name = side+'_front_wall'
    wall, old_wall = parts[name], prior[name]
    expected = old_wall.fuse(mirror(restore,side)).cut(mirror(well,side)).cut(mirror(through,side))
    near(difference(wall,expected),0,.001)
    # All reinforcement inward of the original 4 mm wall is byte-independent CAD equal.
    inner_region = mirror(box(4,0,-1,5,242,160),side)
    near(difference(wall.intersect(inner_region),old_wall.intersect(inner_region)),0,.001)
    near(old_wall.Volume()-wall.Volume(),366.933333333,.001)
    measured = [thickness(wall,y,z) for y in (83,103,123) for z in (.1,2,4.1,8,12)]
    for t in measured:
        near(t,8)
    near(wall.distance(parts['bottom_front']),.3,.00001)
    near(volume(wall.intersect(parts['bottom_front'])),0,.00001)
    exterior = 0 if side == 'left' else 260
    direction = 1 if side == 'left' else -1
    verts = np.array(meshes[name]['v'])
    depth = (verts[:,0]-exterior)*direction
    yz = verts[:,1:]
    near(depth.min(),0); near(depth.max(),8)
    circle = yz[(abs(depth)<1e-6)&(abs(np.linalg.norm(yz-[103,30],axis=1)-14)<.001)]
    fit = np.linalg.lstsq(np.c_[2*circle,np.ones(len(circle))],np.einsum('ij,ij->i',circle,circle),rcond=None)[0]
    cy,cz = fit[:2]
    radius = math.sqrt(fit[2]+cy*cy+cz*cz)
    near(cy,103); near(cz,30); near(radius,14)
    for plane, half, label in ((0,11.5,'mouth'),(2.5,9,'floor'),(2.5,7.05,'hole')):
        for dy,dz in ((-half,-half),(-half,half),(half,-half),(half,half)):
            point = np.array([exterior+direction*plane,136+dy,30+dz])
            assert np.any(np.max(abs(verts-point),axis=1)<1e-4), (name,label,'missing corner',point.tolist())
    near(thickness(wall,143.75,30),1.5)
    near(thickness(wall,145.5,30),2.0)
    near(thickness(wall,150,30),4)
    near(thickness(wall,136,30),0)
    near(planar_area(wall,0,exterior+direction*2.5),18**2-14.1**2,.001)
    near(planar_area(old_wall,0,exterior)-planar_area(wall,0,exterior),23**2-14.1**2,.001)
    tri = triangles[name]
    near(tri[:,:,2].min(),0); near(tri[:,:,2].max(),8)
    near(flat_area(tri,2,2.5),18**2-14.1**2,.005)
    wall_rows.append({'name':name,'flipper_center_yz_mm':[103,30],'nudge_center_yz_mm':[136,30],
        'center_spacing_mm':33,'recess_depth_mm':2.5,'well_mouth_mm':23,'well_floor_mm':18,
        'through_hole_mm':14.1,'snap_plate_mm':1.5,'surrounding_wall_mm':4,
        'taper_degrees':45,'flipper_bore_to_recess_mouth_web_mm':7.5,
        'pedestal_unchanged':True,'pedestal_bottom_z_mm':0,'pedestal_total_thickness_mm':8,
        'floor_clearance_mm':.3,'only_requested_local_geometry_difference':True,
        'net_removed_material_mm3':round(old_wall.Volume()-wall.Volume(),6)})

# Small sample reproduces the actual 4 mm-thick switch mounting region of the wall.
# It intentionally omits adjacent inward flipper reinforcement beyond that wall.
crop = parts['left_front_wall'].intersect(box(0,121,15,4,30,30))
coupon_rows = []
for name,d in (('nudge_switch_fit',14.1),('nudge_mx_14p0',14.0),('nudge_mx_14p2',14.2)):
    tri = triangles[name]
    for a,b in zip(np.ptp(tri.reshape(-1,3),axis=0),(30,30,4)):
        near(a,b)
    near(flat_area(tri,2,0),30**2-23**2,.005)
    near(flat_area(tri,2,2.5),18**2-d*d,.005)
    near(flat_area(tri,2,4),30**2-d*d,.005)
    solid = stl_solid(tri)
    expected = printed(box(0,121,15,4,30,30).cut(well).cut(box(-1,136-d/2,30-d/2,10,d,d)))
    near(difference(solid,expected),0,.002)
    if name == 'nudge_switch_fit':
        near(difference(solid,printed(crop)),0,.002)
    coupon_rows.append({'name':name,'print_size_mm':[30,30,4],'hole_mm':d,
        'outside_face_down':True,'recess_depth_mm':2.5,'same_switch_mounting_geometry_as_wall':d==14.1})
# The larger existing paired sample must still be the actual wall crop.
combined = parts['left_front_wall'].intersect(box(-.1,76,0,8.2,78,57))
combined_tri = triangles['flipper_nudge_wall_sample']
for a,b in zip(np.ptp(combined_tri.reshape(-1,3),axis=0),(57,78,8)):
    near(a,b)
combined_mesh_volume = float(np.einsum('ij,ij->i',combined_tri[:,0],np.cross(combined_tri[:,1],combined_tri[:,2])).sum()/6)
near(combined_mesh_volume,combined.Volume(),3)
near(flat_area(combined_tri,2,2.5),18**2-14.1**2,.005)

# Check shifted assumed switch envelopes against actual STEP references and every part.
# Distinct hardware groups must also clear one another, not only printed geometry.
clearance_rows = []
for side in ('left','right'):
    stem = mirror(box(2.4,129,23,1.7,14,14),side)
    body = mirror(box(4.1,127.8,21.8,18.4,16.4,16.4),side)
    upper = mirror(box(-3.5,127.8,21.8,6,16.4,16.4),side)
    for label, reserve in (('plate stem',stem),('body clip wiring',body),('upper housing',upper)):
        matches = [r for r in references if np.max(abs(bounds(r)-bounds(reserve)))<1e-4]
        assert any(difference(r,reserve)<.001 for r in matches), (side,label,'updated envelope missing in STEP')
    barrel = mirror(cq.Solid.makeCylinder(13.9,20.1,cq.Vector(-.1,103,30),cq.Vector(1,0,0)),side)
    nut = mirror(cq.Solid.makeCylinder(20,5,cq.Vector(8.2,103,30),cq.Vector(1,0,0)),side)
    rear_body = mirror(box(13.2,83,10,36,40,40),side)
    for label,reserve in (('plate stem',stem),('body clip wiring',body),('upper housing',upper)):
        a = bounds(reserve)
        for part_name,part in parts.items():
            b = bounds(part)
            if np.any(np.minimum(a[3:],b[3:])-np.maximum(a[:3],b[:3])<1e-6):
                continue
            near(volume(reserve.intersect(part)),0,.001)
        for flipper in (barrel,nut,rear_body):
            near(volume(reserve.intersect(flipper)),0,.001)
    gap = min(body.distance(nut),body.distance(rear_body))
    near(gap,4.8,.00001)
    clearance_rows.append({'side':side,'body_inner_depth_mm':22.5,'body_to_flipper_nut_or_body_gap_mm':round(gap,6),
        'assumed_switch_envelopes_clear_every_printed_part':True,'distinct_flipper_and_nudge_envelopes_clear':True})
print(json.dumps({
    'status':'PASS',
    'evidence':'Independent exported STL topology, unchanged-byte comparison, mesh coordinates and re-imported STEP solids; no builder import.',
    'printed_parts':45,'fit_samples':17,
    'only_changed_enclosure_parts':stl_changed,
    'unchanged_enclosure_stl_bytes_preview_geometry_and_manifest_records':43,
    'changed_existing_fit_sample_geometry':test_geometry_changed,
    'renamed_default_sample':{'old':'nudge_mx_14p1','new':'nudge_switch_fit'},
    'all_62_stls_closed_single_shell_manifold_positive_volume_and_print_bounds':True,
    'front_walls':wall_rows,'small_switch_samples':coupon_rows,'assumed_hardware_clearance':clearance_rows,
    'print_limit':'Outside-face-down orientation includes a 1.95 mm horizontal mounting ledge; slicing/physical coupon must establish bridging or local support needs.',
    'physical_limit':'Actual switch, cap skirt, full key travel, clip fit, retained flipper stiffness and printer dimensions have not been physically measured.'
},indent=2))
