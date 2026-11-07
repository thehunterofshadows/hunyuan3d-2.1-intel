"""Independent read-only audit of the exported V1.9 flipper pedestal revision.

Run with the existing CAD virtualenv's Python. No builder is imported or executed.
Checks production STL bytes/topology, assembly meshes, and re-imported STEP solids.
The only written artifact is this script itself; the audit prints JSON to stdout.
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
NEW = CAD / 'portable-pinball-v1_9' / 'exports'
OLD = CAD / 'portable-pinball-v1_8' / 'exports'
EXPECTED = {'left_front_wall', 'right_front_wall', 'bottom_front'}
manifest = json.loads((NEW / 'parts_manifest.json').read_text())
old_manifest = json.loads((OLD / 'parts_manifest.json').read_text())
meshes = {m['name']: m for m in json.loads((NEW / 'preview_meshes.json').read_text())}
old_meshes = {m['name']: m for m in json.loads((OLD / 'preview_meshes.json').read_text())}
names = [p['name'] for p in manifest['parts']]
assert len(names) == 45 and set(names) == set(meshes) == set(old_meshes)
assert len(manifest['tests']) == 17
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
stl_changed = [n for n in names if sha(NEW / 'enclosure_stl' / (n + '.stl')) != sha(OLD / 'enclosure_stl' / (n + '.stl'))]
mesh_changed = [n for n in names if meshes[n] != old_meshes[n]]
assert set(stl_changed) == set(mesh_changed) == EXPECTED, (stl_changed, mesh_changed)
old_parts = {p['name']: p for p in old_manifest['parts']}
for p in manifest['parts']:
    if p['name'] not in EXPECTED:
        assert p == old_parts[p['name']], p['name']

def near(a, b, tolerance=1e-4):
    assert abs(float(a) - float(b)) <= tolerance, (a, b, tolerance)

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
    assert all(len(e) == 2 for e in edges.values()), (path, 'nonmanifold or open edge')
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
    assert len({root(i) for i in range(len(faces))}) == 1, (path, 'disconnected triangle shells')
    volume = float(np.einsum('ij,ij->i', tri[:, 0], np.cross(tri[:, 1], tri[:, 2])).sum() / 6)
    assert volume > 0, (path, 'nonpositive signed volume')
    lo, hi = tri.min(axis=(0, 1)), tri.max(axis=(0, 1))
    dims = hi - lo
    assert lo[2] >= -1e-5, (path, 'below print bed')
    assert dims[0] + 16 < 325.001 and dims[1] + 16 < 325.001 and dims[2] < 315.001, (path, 'printer bounds')
    return tri, {'name': path.stem, 'triangles': len(tri), 'volume_mm3': round(volume, 6), 'print_size_mm': np.round(dims, 6).tolist()}

files = sorted((NEW / 'enclosure_stl').glob('*.stl')) + sorted((NEW / 'print_first_tests').glob('*.stl'))
assert len(files) == 62
triangles, mesh_rows = {}, []
for path in files:
    tri, row = topology(path)
    triangles[path.stem] = tri
    mesh_rows.append(row)

old_tests = {p.stem: p for p in (OLD / 'print_first_tests').glob('*.stl')}
new_tests = {p.stem: p for p in (NEW / 'print_first_tests').glob('*.stl')}
assert set(new_tests) - set(old_tests) == {'flipper_floor_notch_sample'}
assert not set(old_tests) - set(new_tests)
changed_tests = sorted(n for n in old_tests if sha(old_tests[n]) != sha(new_tests[n]))
def canonical_triangles(tri):
    return sorted(tuple(sorted(tuple(np.round(v, 6)) for v in face)) for face in tri)
changed_test_geometry = sorted(n for n in changed_tests if canonical_triangles(stl(old_tests[n])) != canonical_triangles(stl(new_tests[n])))
assert changed_test_geometry == ['flipper_nudge_wall_sample'], changed_test_geometry

def flat_area(tri, axis, level):
    mask = np.all(abs(tri[:, :, axis] - level) < 1e-5, axis=1)
    return float(np.linalg.norm(np.cross(tri[mask, 1] - tri[mask, 0], tri[mask, 2] - tri[mask, 0]), axis=1).sum() / 2)

def box(x, y, z, dx, dy, dz):
    return cq.Workplane('XY').box(dx, dy, dz, centered=False).translate((x, y, z)).val()

def volume(shape):
    return sum(s.Volume() for s in shape.Solids())

def imported_parts(folder, meta, mesh):
    solids = cq.importers.importStep(str(folder / 'mini_vpin_assembly.step')).solids().vals()
    assert len(solids) == 64
    parts = {}
    for i, p in enumerate(meta['parts']):
        s = solids[i]
        assert s.isValid() and len(s.Solids()) == 1, p['name']
        near(s.Volume(), p['volume'], .001)
        b = s.BoundingBox()
        verts = np.array(mesh[p['name']]['v'])
        got = np.array([b.xmin, b.ymin, b.zmin, b.xmax, b.ymax, b.zmax])
        expected = np.r_[verts.min(axis=0), verts.max(axis=0)]
        assert np.max(abs(got - expected)) < .1, (p['name'], 'STEP/mesh bounds mismatch')
        parts[p['name']] = s
    return parts

parts = imported_parts(NEW, manifest, meshes)
prior = imported_parts(OLD, old_manifest, old_meshes)

def thickness(shape, y, z):
    w = .02
    return volume(shape.intersect(box(-1, y - w / 2, z - w / 2, 262, w, w))) / (w * w)

def planar_area(shape, axis, level):
    area = 0
    for face in shape.Faces():
        b = face.BoundingBox()
        bounds = [(b.xmin, b.xmax), (b.ymin, b.ymax), (b.zmin, b.zmax)][axis]
        if max(abs(v - level) for v in bounds) < 1e-5:
            area += face.Area()
    return area

walls = []
floor = parts['bottom_front']
upper_region = box(-1, -1, 30.001, 262, 472, 160)
for name in ['left_front_wall', 'right_front_wall']:
    wall, old_wall = parts[name], prior[name]
    verts = np.array(meshes[name]['v'])
    exterior = 0 if name.startswith('left') else 260
    direction = 1 if exterior == 0 else -1
    depth = (verts[:, 0] - exterior) * direction
    near(depth.min(), 0)
    near(depth.max(), 8)
    near(verts[:, 2].min(), 0)
    near(planar_area(wall, 0, exterior), planar_area(old_wall, 0, exterior), 1e-4)
    assert volume(old_wall.cut(wall)) < .001, (name, 'existing wall material removed')
    upper_new, upper_old = wall.intersect(upper_region), old_wall.intersect(upper_region)
    assert volume(upper_new.cut(upper_old)) + volume(upper_old.cut(upper_new)) < .001, (name, 'upper collar/wall changed')
    added = wall.cut(old_wall)
    b = added.BoundingBox()
    assert b.zmin >= -1e-5 and b.zmax <= 30.00001
    assert b.ymin >= 79.99999 and b.ymax <= 126.00001
    assert volume(added) > 2000

    # Recover circular bore center/radius and nudge opening directly from mesh coordinates.
    yz = verts[:, 1:]
    circle = yz[(abs(depth) < 1e-6) & (abs(np.linalg.norm(yz - [103, 30], axis=1) - 14) < .001)]
    fit = np.linalg.lstsq(np.c_[2 * circle, np.ones(len(circle))], np.einsum('ij,ij->i', circle, circle), rcond=None)[0]
    cy, cz = fit[:2]
    radius = math.sqrt(fit[2] + cy * cy + cz * cz)
    near(cy, 103); near(cz, 30); near(radius, 14)
    opening = np.unique(np.round(yz[(abs(depth) < 1e-6) & (abs(yz[:, 0] - 136) < 10) & (abs(yz[:, 1] - 30) < 10)], 6), axis=0)
    assert len(opening) == 4
    center = (opening.min(axis=0) + opening.max(axis=0)) / 2
    dims = np.ptp(opening, axis=0)
    near(center[0], 136); near(center[1], 30)
    near(dims[0], 14.1); near(dims[1], 14.1)
    near(center[0] - cy, 33); near(center[1] - cz, 0)
    near(thickness(wall, 143.75, 30), 1.5)
    near(thickness(wall, 150, 30), 4)
    near(thickness(wall, 136, 30), 0)
    # The full added thickness must continue to the bottom under/across the bore.
    measured = []
    for y in [83, 103, 123]:
        for z in [.1, 2, 4.1, 8, 12]:
            t = thickness(wall, y, z)
            near(t, 8, .0001)
            measured.append(t)
    tri = triangles[name]
    near(tri[:, :, 2].min(), 0)
    near(tri[:, :, 2].max(), 8)
    near(flat_area(tri, 2, 0), flat_area(stl(OLD / 'enclosure_stl' / (name + '.stl')), 2, 0), .05)
    expected_inner_face = 44 * 30 + math.pi * 22**2 / 2 - math.pi * 14**2
    near(planar_area(wall, 0, exterior + direction * 8), expected_inner_face, .001)
    near(flat_area(tri, 2, 8), expected_inner_face, 2)  # Tessellated circular edges approximate exact CAD area.
    near(flat_area(tri, 2, 1.5), 16.6**2 - 14.1**2, .005)
    foot_x = 4.0001 if direction == 1 else 251.9
    pedestal_at_floor = wall.intersect(box(foot_x, 79, 0, 4.1, 48, 4))
    assert volume(pedestal_at_floor) > 700
    overlap = volume(wall.intersect(floor))
    near(overlap, 0, .00001)
    clearance = pedestal_at_floor.distance(floor)
    near(clearance, .3, .00001)
    whole_wall_floor_distance = wall.distance(floor)
    near(whole_wall_floor_distance, .3, .00001)
    walls.append({
        'name': name,
        'flipper_center_yz_mm': [round(cy, 6), round(cz, 6)],
        'flipper_bore_diameter_mm': round(radius * 2, 6),
        'nudge_center_yz_mm': center.tolist(),
        'nudge_opening_mm': dims.tolist(),
        'center_spacing_mm': round(center[0] - cy, 6),
        'bottom_pedestal_total_thickness_mm': round(min(measured), 6),
        'bottom_pedestal_z_mm': round(b.zmin, 6),
        'new_material_volume_mm3': round(volume(added), 6),
        'new_material_above_centerline_mm3': round(volume(added.intersect(upper_region)), 6),
        'added_bottom_bearing_area_mm2': round(planar_area(wall, 2, 0) - planar_area(old_wall, 2, 0), 6),
        'actual_pedestal_to_floor_clearance_mm': round(clearance, 6),
        'floor_overlap_mm3': round(overlap, 6),
        'print_exterior_z_mm': 0,
        'print_pedestal_face_z_mm': 8,
    })

# Independently reconstruct only the requested floor relief, not the cabinet.
left_cut = box(0, 79.7, -1, 8.3, 46.6, 6)
right_cut = box(251.7, 79.7, -1, 8.3, 46.6, 6)
expected_floor = prior['bottom_front'].cut(left_cut).cut(right_cut)
difference = volume(expected_floor.cut(floor)) + volume(floor.cut(expected_floor))
near(difference, 0, .00001)
removed_volume = prior['bottom_front'].Volume() - floor.Volume()
near(removed_volume, 2 * 4 * 46.6 * 4, .001)
near(volume(floor.cut(prior['bottom_front'])), 0, .00001)
assert floor.isValid() and len(floor.Solids()) == 1

# Exact wall sample now includes the bottom; the floor sample mates to that region.
tri = triangles['flipper_nudge_wall_sample']
dims = tri.max(axis=(0, 1)) - tri.min(axis=(0, 1))
for a, b in zip(dims, [57, 78, 8]):
    near(a, b)
near(tri[:, :, 2].min(), 0)
near(flat_area(tri, 2, 1.5), 16.6**2 - 14.1**2, .005)
near(flat_area(tri, 2, 0) - flat_area(stl(old_tests['flipper_nudge_wall_sample']), 2, 0), 78 * 3, .05)
root_width_at_x4 = 2 * (23 - (4 - 3.98) / (8 - 3.98))
expected_bottom_area = 4 * 78 + 4 * (root_width_at_x4 + 44) / 2
near(flat_area(tri, 0, 57), expected_bottom_area, .01)

floor_tri = triangles['flipper_floor_notch_sample']
dims = floor_tri.max(axis=(0, 1)) - floor_tri.min(axis=(0, 1))
for a, b in zip(dims, [20, 78, 4]):
    near(a, b)
near(floor_tri[:, :, 2].min(), 0)
floor_sample_area = 20 * 78 - 4 * 46.6
near(flat_area(floor_tri, 2, 0), floor_sample_area, .005)
near(flat_area(floor_tri, 2, 4), floor_sample_area, .005)
top_vertices = floor_tri.reshape(-1, 3)
for x, y in [(0, 0), (20, 0), (20, 78), (0, 78), (0, 3.7), (4, 3.7), (4, 50.3), (0, 50.3)]:
    assert np.any(np.max(abs(top_vertices - [x, y, 4]), axis=1) < 1e-4), (x, y, 'sample notch vertex missing')

report = {
    'status': 'PASS',
    'evidence': 'Independent audit of exported STL bytes/topology, assembly meshes and re-imported STEP; no builder imported or executed.',
    'printed_parts': 45,
    'fit_samples': 17,
    'only_changed_enclosure_parts': stl_changed,
    'unchanged_enclosure_stl_bytes_preview_geometry_and_manifest_records': 42,
    'only_changed_existing_fit_sample_geometry': changed_test_geometry,
    'existing_fit_sample_byte_changes': changed_tests,
    'sample_reordering_only': sorted(set(changed_tests) - set(changed_test_geometry)),
    'new_fit_sample': 'flipper_floor_notch_sample',
    'mesh_topology': {
        'checked': 62,
        'closed_edge_manifold': 62,
        'consistent_winding': 62,
        'single_connected_triangle_shell': 62,
        'positive_volume': 62,
        'nondegenerate_triangles': 62,
        'within_printer_envelope_with_8mm_brim': 62,
    },
    'front_walls': walls,
    'front_floor': {
        'only_changes_are_two_local_notches': True,
        'notch_y_mm': [79.7, 126.3],
        'left_notch_x_mm': [4.3, 8.3],
        'right_notch_x_mm': [251.7, 255.7],
        'removed_volume_mm3': round(removed_volume, 6),
        'connected_valid_solid': True,
    },
    'samples': {
        'wall_print_size_mm': [57, 78, 8],
        'wall_bottom_bearing_area_mm2': round(expected_bottom_area, 6),
        'wall_exterior_print_z_mm': 0,
        'floor_print_size_mm': [20, 78, 4],
        'floor_notch_depth_mm': 4,
        'floor_notch_width_mm': 46.6,
    },
    'physical_limit': 'Geometry verifies added support and fit clearance; actual flipper stiffness, fastener tightness and print/hardware fit have not been physically measured.',
}
print(json.dumps(report, indent=2))
