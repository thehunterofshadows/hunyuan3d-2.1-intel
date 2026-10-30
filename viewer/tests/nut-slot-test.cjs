const {chromium}=require('/opt/checks/node_modules/playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
(async()=>{
 const browser=await chromium.launch({args:['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 const page=await browser.newPage({viewport:{width:1440,height:900}});
 const errors=[]; page.on('pageerror',e=>errors.push(e.message));
 const origin=process.env.VIEWER_URL||'http://intel-3d-studio-nut-candidate';
 await page.goto(origin+'/#pinball-nut-slot-test');
 await page.waitForSelector('#viewport[data-state=ready]',{timeout:90000});
 assert.equal(await page.locator('#viewport').getAttribute('data-model'),'pinball-nut-slot-test');
 assert.match(await page.locator('#title').innerText(),/side-entry nut block TEST/);
 assert.match(await page.locator('#stats').innerText(),/2,002 triangles/);
 assert.equal(await page.locator('#download').getAttribute('href'),'/models/pinball-nut-slot-test/top_block_left_140_side_slot.stl');
 const response=await page.request.get(origin+'/models/pinball-nut-slot-test/top_block_left_140_side_slot.stl');
 assert.equal(response.status(),200);
 const stl=await response.body(); assert.equal(stl.length,84+50*stl.readUInt32LE(80));
 for(const f of ['nut-slot-v1.glb','top_block_left_140_side_slot.step','validation.json'])assert.equal((await page.request.get(origin+'/models/pinball-nut-slot-test/'+f)).status(),200);
 // Exercise views and capture actual CAD, including side entry.
 await page.locator('#viewport canvas').screenshot({path:'/evidence/nut-slot-home.png'});
 await page.locator('#viewport canvas').screenshot({path:'/assets/pinball-nut-slot-test/preview.png'});
 await page.locator('[data-view=right]').click();
 await page.waitForTimeout(200);
 await page.locator('#viewport canvas').screenshot({path:'/evidence/nut-slot-inside.png'});
 await page.locator('[data-view=top]').click();
 await page.locator('#viewport canvas').screenshot({path:'/evidence/nut-slot-top.png'});
 // Existing cabinet must still be the V1.3 assembly.
 await page.goto(origin+'/#portable-pinball');
 await page.waitForSelector('#viewport[data-state=ready]',{timeout:90000});
 assert.match(await page.locator('#title').innerText(),/CAD V1.3/);
 assert.match(await page.locator('#stats').innerText(),/45 printed parts/);
 await page.setViewportSize({width:390,height:844});
 await page.goto(origin+'/#pinball-nut-slot-test');
 await page.waitForSelector('#viewport[data-state=ready]',{timeout:90000});
 assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'mobile overflow');
 assert.deepEqual(errors,[]);
 console.log('PASS: exact-CAD test renders; print STL/STEP/GLB available; view controls and mobile work; cabinet remains V1.3.');
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
