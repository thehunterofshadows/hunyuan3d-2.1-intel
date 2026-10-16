const {chromium}=require('/opt/checks/node_modules/playwright');
const assert=require('node:assert/strict');
(async()=>{
 const b=await chromium.launch({headless:true,args:['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 const p=await b.newPage({viewport:{width:1440,height:1100}}),errors=[];
 p.on('pageerror',e=>errors.push(e.message));p.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
 const base=process.env.VIEWER_URL||'http://pinball-cad-viewer-check/';
 await p.goto(base+'#portable-pinball');await p.waitForSelector('#viewport[data-state=ready][data-model=portable-pinball]',{timeout:60000});
 assert.equal(await p.locator('#cad-part option').count(),48,'47 printed parts plus All');
 assert.match(await p.locator('#stats').innerText(),/37,364 triangles · 47 printed parts · 3 reference envelopes/);
 assert.match(await p.locator('#reference .caption').textContent(),/CAD assembly/);
 assert.equal(await p.locator('#chrome-control').isVisible(),false);
 const response=await p.request.get(new URL(await p.locator('#download').getAttribute('href'),p.url()).href);
 assert.equal(response.status(),200);const glb=await response.body();assert.equal(glb.subarray(0,4).toString(),'glTF');
 const jsonSize=glb.readUInt32LE(12);const doc=JSON.parse(glb.subarray(20,20+jsonSize).toString());
 assert.equal(doc.nodes.filter(n=>n.extras?.cadPart).length,47);assert.equal(doc.nodes.filter(n=>n.extras?.cadReference).length,3);
 for(const path of ['cad-print-pack.zip','cabinet.step']){
  const r=await p.request.get(new URL('/models/portable-pinball/'+path,p.url()).href);assert.equal(r.status(),200);
  const content=await r.body();assert.ok(path.endsWith('zip')?content.subarray(0,2).toString()==='PK':content.subarray(0,30).toString().includes('ISO-10303-21'));
 }
 const canvas=p.locator('#viewport canvas');await canvas.scrollIntoViewIfNeeded();await p.waitForTimeout(350);
 const assembled=await canvas.screenshot();await canvas.screenshot({path:'/evidence/pinball-assembled.png'});
 await p.locator('#explode').evaluate(e=>{e.value='1';e.dispatchEvent(new Event('input',{bubbles:true}));e.dispatchEvent(new Event('change',{bubbles:true}));});
 await p.waitForTimeout(500);assert.match(await p.locator('#explode-value').innerText(),/100%/);assert.notDeepEqual(await canvas.screenshot(),assembled,'explode changes actual rendering');
 await canvas.screenshot({path:'/evidence/pinball-exploded.png'});
 await p.uncheck('#cad-monitor');await p.uncheck('#cad-pc');await p.uncheck('#cad-panels');await p.check('#cad-cover');
 await p.waitForTimeout(350);const cutaway=await canvas.screenshot();assert.notDeepEqual(cutaway,assembled);await canvas.screenshot({path:'/evidence/pinball-cover-clearance.png'});
 await p.selectOption('#cad-part','left_front_wall');await p.waitForTimeout(400);assert.notDeepEqual(await canvas.screenshot(),cutaway,'isolation changes rendering');
 await canvas.screenshot({path:'/evidence/pinball-part-isolated.png'});
 await p.selectOption('#cad-part','all');await p.check('#cad-panels');await p.check('#cad-monitor');await p.check('#cad-pc');await p.uncheck('#cad-cover');
 for(const view of ['front','back','left','right','top']){await p.click('[data-view='+view+']');await p.waitForTimeout(200);}
 await p.selectOption('#surface','clay');await p.check('#wireframe');await p.selectOption('#surface','normals');await p.uncheck('#wireframe');await p.selectOption('#surface','pbr');
 await p.click('#reset');await p.waitForTimeout(350);await canvas.scrollIntoViewIfNeeded();
 const before=await canvas.screenshot(),box=await canvas.boundingBox();
 await p.mouse.move(box.x+box.width*.5,box.y+box.height*.5);await p.mouse.down();await p.mouse.move(box.x+box.width*.7,box.y+box.height*.6,{steps:10});await p.mouse.up();await p.waitForTimeout(500);
 const rotated=await canvas.screenshot();assert.notDeepEqual(rotated,before);await p.mouse.wheel(0,-250);await p.waitForTimeout(500);assert.notDeepEqual(await canvas.screenshot(),rotated);
 const stl=await p.request.get(new URL('/models/portable-pinball/button_hole_28.stl',p.url()).href);assert.equal(stl.status(),200);
 await p.locator('#stl-file').setInputFiles({name:'button-hole-28.stl',mimeType:'model/stl',buffer:await stl.body()});
 await p.waitForSelector('#viewport[data-state=ready][data-model=local-stl]');assert.equal(await p.locator('#cad-controls').isVisible(),false);assert.match(await p.locator('#stats').innerText(),/STL geometry/);assert.match(await p.locator('#description').innerText(),/not uploaded/);
 await canvas.screenshot({path:'/evidence/pinball-local-stl.png'});
 // ASCII STL path as well as the binary exported coupon.
 const ascii='solid t\nfacet normal 0 0 1\nouter loop\nvertex 0 0 0\nvertex 10 0 0\nvertex 0 10 0\nendloop\nendfacet\nendsolid t';
 await p.locator('#stl-file').setInputFiles({name:'ascii.stl',mimeType:'model/stl',buffer:Buffer.from(ascii)});await p.waitForFunction(()=>document.querySelector('#title').textContent==='ascii.stl'&&document.querySelector('#viewport').dataset.state==='ready');
 await p.click('[data-model=trellis-bumper]');await p.waitForSelector('#viewport[data-state=ready][data-model=trellis-bumper]',{timeout:60000});assert.equal(await p.locator('#chrome-control').isVisible(),true);assert.equal(await p.locator('#cad-controls').isVisible(),false);
 await p.click('[data-model=portable-pinball]');await p.waitForSelector('#viewport[data-state=ready][data-model=portable-pinball]');assert.equal(await p.locator('#explode').inputValue(),'0');assert.equal(await p.locator('#cad-panels').isChecked(),true);
 const mobile=await b.newPage({viewport:{width:390,height:844},isMobile:true,hasTouch:true});await mobile.goto(base+'#portable-pinball');await mobile.waitForSelector('#viewport[data-state=ready]',{timeout:60000});
 assert.ok(await mobile.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'mobile no horizontal overflow');await mobile.locator('#cad-panels').uncheck();await mobile.selectOption('#cad-part','front_button_panel');await mobile.locator('#viewport canvas').screenshot({path:'/evidence/pinball-mobile.png'});
 assert.deepEqual(errors,[]);console.log('PASS: exact 47-part assembly; 3 references; explode, hide and isolate; 5 views; rotation/zoom; materials; GLB/STEP/ZIP; binary + ASCII local STL; bumper regression; mobile.');await b.close();
})().catch(e=>{console.error(e);process.exit(1)});
