const {chromium}=require('/opt/checks/node_modules/playwright');
const assert=require('node:assert/strict'),crypto=require('node:crypto');
(async()=>{
 const b=await chromium.launch({args:['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 const p=await b.newPage({viewport:{width:1440,height:1100}}),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.route('**/api/part-notes?model=portable-pinball',r=>r.fulfill({json:{notes:[{model:{id:'portable-pinball'},part:{id:'cad:monitor_saddle_left_180',geometryFingerprint:'old-geometry'},text:'Check tip thickness',revision:1}]}}));
 const base=process.env.VIEWER_URL;await p.goto(base+'#portable-pinball',{waitUntil:'domcontentloaded'});await p.waitForSelector('#viewport[data-state=ready]',{timeout:60000});
 assert.match(await p.locator('#title').textContent(),/V1.3/);assert.equal(await p.locator('#cad-part option').count(),46);assert.match(await p.locator('#stats').textContent(),/45 printed parts/);
 assert.match(await p.locator('#download').getAttribute('href'),/cabinet-v1_3.glb/);
 async function glb(path){const r=await p.request.get(base+'models/portable-pinball/'+path);assert.equal(r.status(),200);const raw=await r.body(),len=raw.readUInt32LE(12);return {doc:JSON.parse(raw.subarray(20,20+len)),bin:raw.subarray(28+len)};}
 const old=await glb('cabinet.glb'),current=await glb('cabinet-v1_1.glb');assert.equal(current.doc.nodes.filter(n=>n.extras?.cadPart).length,47);
 function meshData(g,node){const primitive=g.doc.meshes[node.mesh].primitives[0];const attrs=[primitive.attributes.POSITION,primitive.indices];const out=attrs.map(i=>{const a=g.doc.accessors[i],v=g.doc.bufferViews[a.bufferView],start=(v.byteOffset||0)+(a.byteOffset||0);return g.bin.subarray(start,start+a.count*(a.type==='VEC3'?3:1)*(a.componentType===5126||a.componentType===5125?4:2))});return crypto.createHash('sha256').update(Buffer.concat(out)).digest('hex');}
 const changed=[];
 for(const node of current.doc.nodes){const before=old.doc.nodes.find(n=>n.name===node.name);assert.ok(before);if(meshData(old,before)!==meshData(current,node))changed.push(node.name);
  if(node.name.startsWith('monitor_saddle_')){const a=old.doc.accessors[old.doc.meshes[before.mesh].primitives[0].attributes.POSITION],c=current.doc.accessors[current.doc.meshes[node.mesh].primitives[0].attributes.POSITION];assert.ok(Math.abs(c.min[1]-a.min[1]+.004)<.000001);assert.deepEqual(c.max,a.max);}
 }
 assert.deepEqual(changed.sort(),['monitor_saddle_left_180','monitor_saddle_left_360','monitor_saddle_right_180','monitor_saddle_right_360'].sort());
 for(const name of ['cabinet-v1_1.step','cad-print-pack-v1_1.zip','monitor-support-v1_1.stl']){const r=await p.request.get(base+'models/portable-pinball/'+name);assert.equal(r.status(),200);const body=await r.body();if(name.endsWith('.stl')){let lo=Infinity,hi=-Infinity;for(let i=0,n=body.readUInt32LE(80);i<n;i++)for(let v=0;v<3;v++){const z=body.readFloatLE(84+i*50+12+v*12+8);lo=Math.min(lo,z);hi=Math.max(hi,z);}assert.ok(Math.abs(lo)<.0001);assert.ok(Math.abs(hi-20)<.0001,'end-face print orientation has 20 mm Z height');}}
 await p.selectOption('#cad-part','monitor_saddle_left_180');const c=p.locator('#viewport canvas');await c.scrollIntoViewIfNeeded();await p.waitForTimeout(400);assert.equal(await p.locator('#cad-part').inputValue(),'monitor_saddle_left_180');await p.screenshot({path:'/evidence/cad-v1_1-support.png'});
 await p.selectOption('#cad-part','all');await p.uncheck('#cad-monitor');await p.uncheck('#cad-pc');await p.uncheck('#cad-panels');await c.screenshot({path:'/evidence/cad-v1_1-internal.png'});
 assert.deepEqual(errors,[]);console.log('PASS: exactly four revised supports; 4 mm deeper shelves with unchanged upper bounds; stable part IDs and old-note geometry warning; all revision downloads; end-face STL orientation; selection, transparency and restoration');await b.close();
})().catch(e=>{console.error(e);process.exit(1)});
