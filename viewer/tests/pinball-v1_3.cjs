// CAD V1.3 regression: join LEFT bezel while preserving RIGHT and 43 unrelated solids.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../..'),assets=path.join(root,'assets/portable-pinball');
function glb(name){const b=fs.readFileSync(path.join(assets,name));assert.equal(b.toString('utf8',0,4),'glTF');const n=b.readUInt32LE(12);return {data:JSON.parse(b.subarray(20,20+n)),bin:b.subarray(28+n)};}
function nodes(g){return g.data.nodes.filter(x=>x.extras?.cadPart)}
function hashNode(g,n){const p=g.data.meshes[n.mesh].primitives[0];const parts=[p.attributes.POSITION,p.indices].map(id=>{const a=g.data.accessors[id],v=g.data.bufferViews[a.bufferView],start=(v.byteOffset||0)+(a.byteOffset||0);return g.bin.subarray(start,start+a.count*(a.type==='VEC3'?3:1)*4);});return crypto.createHash('sha256').update(Buffer.concat(parts)).digest('hex');}
const previous=glb('cabinet-v1_2.glb'),current=glb('cabinet-v1_3.glb'),before=nodes(previous),now=nodes(current),names=new Set(now.map(p=>p.name));
assert.equal(before.length,46);assert.equal(now.length,45);assert.equal(current.data.nodes.filter(x=>x.extras?.cadReference).length,3);
assert.ok(names.has('bezel_left_one_piece')&&names.has('bezel_right_a1_a2'));
for(const name of ['bezel_left_front','bezel_left_rear'])assert.ok(!names.has(name));
for(const old of before.filter(p=>!['bezel_left_front','bezel_left_rear'].includes(p.name))){const newer=now.find(p=>p.name===old.name);assert.ok(newer,'missing '+old.name);assert.equal(hashNode(previous,old),hashNode(current,newer),'unexpected change: '+old.name);}
const reports=path.join(root,'viewer/cad/portable-pinball-v1_3/validation');const manifest=JSON.parse(fs.readFileSync(path.join(reports,'parts_manifest.json')));assert.equal(manifest.parts.length,45);assert.equal(manifest.tests.length,10);
for(const name of ['bezel_left_one_piece','bezel_right_a1_a2']){const part=manifest.parts.find(x=>x.name===name);assert.ok(part);assert.equal(part.mode,'top_diagonal');assert.ok(part.bounds[0]+16<=325&&part.bounds[1]+16<=325&&part.bounds[2]<=315);assert.ok(Math.abs(part.bounds[0]-265.78)<0.1&&Math.abs(part.bounds[1]-265.78)<0.1);const stl=fs.readFileSync(path.join(assets,'stl-v1_3',name+'.stl'));assert.ok(stl.length>10000);}
const checks=JSON.parse(fs.readFileSync(path.join(reports,'geometry_checks.json')));assert.ok(checks.all_parts_valid&&checks.all_parts_single_solid&&checks.all_parts_fit_with_8mm_brim);assert.deepEqual(checks.interferences,[]);assert.deepEqual(checks.reserved_space_interferences,[]);
const mesh=JSON.parse(fs.readFileSync(path.join(reports,'stl_mesh_checks.json')));assert.equal(mesh.length,55);assert.ok(mesh.every(x=>!x.nonmanifold_edges&&!x.degenerate_facets));
const source=fs.readFileSync(path.join(root,'viewer/cad/portable-pinball-v1_3/build_cabinet.py'),'utf8');assert.match(source,/\[140,330\]:sh=sh.cut\(topbore\(x\+10 if side=='left' else W-10,yy\)\)/);
for(const file of ['cabinet-v1_3.glb','cabinet-v1_3.step','cad-print-pack-v1_3.zip','preview-v1_3.png','bezel_left_one_piece-v1_3.stl','bezel_right_a1_a2-v1_3.stl'])assert.ok(fs.statSync(path.join(assets,file)).size>1000,file);
console.log('PASS V1.3: BOTH bezels single printable rail; left new/right unchanged; remaining 44 V1.2 parts bit-identical; both fit QIDI with brim; 45 solids, 55 manifold STLs, no interference; download assets exist');
