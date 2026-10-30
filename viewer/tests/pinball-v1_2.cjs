// V1.2 regression: two right-side bezel CAD components become one printable solid.
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../..'),asset=path.join(root,'assets/portable-pinball');
function glb(file){const raw=fs.readFileSync(path.join(asset,file));assert.equal(raw.toString('utf8',0,4),'glTF');const n=raw.readUInt32LE(12);return {json:JSON.parse(raw.subarray(20,20+n)),bin:raw.subarray(28+n)};}
function nodes(g){return g.json.nodes.filter(n=>n.extras?.cadPart)}
function fingerprint(g,n){const mesh=g.json.meshes[n.mesh].primitives[0];const buffer=[];for(const idx of [mesh.attributes.POSITION,mesh.indices]){const a=g.json.accessors[idx],v=g.json.bufferViews[a.bufferView],start=(v.byteOffset||0)+(a.byteOffset||0);buffer.push(g.bin.subarray(start,start+a.count*(a.type==='VEC3'?3:1)*4));}return crypto.createHash('sha256').update(Buffer.concat(buffer)).digest('hex');}
const old=glb('cabinet-v1_1.glb'),now=glb('cabinet-v1_2.glb');const before=nodes(old),after=nodes(now),names=new Set(after.map(n=>n.name));
assert.equal(before.length,47);assert.equal(after.length,46);assert.equal(now.json.nodes.filter(n=>n.extras?.cadReference).length,3);
assert.ok(names.has('bezel_right_a1_a2'));
assert.ok(!names.has('bezel_right_front')&&!names.has('bezel_right_rear'));
for(const n of before.filter(n=>!['bezel_right_front','bezel_right_rear'].includes(n.name))){const replacement=after.find(a=>a.name===n.name);assert.ok(replacement,'missing unchanged CAD part: '+n.name);assert.equal(fingerprint(old,n),fingerprint(now,replacement),'modified unrelated CAD part: '+n.name);}
const dataDir=path.join(root,'viewer/cad/portable-pinball-v1_2/validation');const manifest=JSON.parse(fs.readFileSync(path.join(dataDir,'parts_manifest.json')));
const rail=manifest.parts.find(p=>p.name==='bezel_right_a1_a2');assert.ok(rail);assert.equal(rail.mode,'top_diagonal');
assert.ok(Math.abs(rail.bounds[0]-265.78)<0.05 && Math.abs(rail.bounds[1]-265.78)<0.05,'diagonal fit');
assert.ok(rail.bounds[0]+16<=325&&rail.bounds[1]+16<=325&&rail.bounds[2]<=315,'8 mm brim margin on each side');
const check=JSON.parse(fs.readFileSync(path.join(dataDir,'geometry_checks.json')));assert.ok(check.all_parts_valid&&check.all_parts_single_solid&&check.all_parts_fit_with_8mm_brim);assert.deepEqual(check.interferences,[]);assert.deepEqual(check.reserved_space_interferences,[]);
assert.equal(manifest.parts.length,46);const checks=JSON.parse(fs.readFileSync(path.join(dataDir,'stl_mesh_checks.json')));assert.equal(checks.length,56);assert.ok(checks.every(c=>c.nonmanifold_edges===0&&c.degenerate_facets===0));
for(const file of ['bezel_right_a1_a2-v1_2.stl','cad-print-pack-v1_2.zip','cabinet-v1_2.step','preview-v1_2.png'])assert.ok(fs.statSync(path.join(asset,file)).size>1000,file);
const source=fs.readFileSync(path.join(root,'viewer/cad/portable-pinball-v1_2/build_cabinet.py'),'utf8');assert.match(source,/for yy in \[140,330\]:sh=sh\.cut\(topbore\(W-10,yy\)\)/);
console.log('PASS V1.2: 46 CAD parts; A1 + A2 continuous single rail; all 45 other solids bit-identical to V1.1; 265.78 mm diagonal footprint; preserved mounting holes; manifold STLs; no interference; versioned downloads');
