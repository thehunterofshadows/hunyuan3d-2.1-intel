// Read-only note smoke test; never writes annotations to production.
const {chromium}=require('/opt/checks/node_modules/playwright');
const assert=require('node:assert/strict');
(async()=>{
 const b=await chromium.launch({args:['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 const p=await b.newPage({viewport:{width:1440,height:1100}}),errors=[];
 p.setDefaultTimeout(120000);await p.route('**/*',route=>route.request().resourceType()==='image'?route.abort():route.continue());p.on('pageerror',e=>errors.push(e.message));
 await p.goto(process.env.VIEWER_URL+'#portable-pinball',{waitUntil:'domcontentloaded',timeout:60000});await p.waitForSelector('#viewport[data-state=ready]',{timeout:120000});
 await p.selectOption('#cad-part','front_button_panel');const canvas=p.locator('#viewport canvas');await canvas.scrollIntoViewIfNeeded();await p.waitForTimeout(400);const r=await canvas.boundingBox();await p.mouse.click(r.x+r.width/2,r.y+r.height/2);await p.waitForSelector('#part-popup:not([hidden])');
 assert.equal(await p.locator('#part-popup').getAttribute('data-part-id'),'cad:front_button_panel');
 await p.selectOption('#part-opacity','0.5');await p.selectOption('#part-opacity','0');await p.click('#part-close');
 await p.mouse.click(r.x+5,r.y+5,{button:'right'});await p.waitForSelector('#parts-menu:not([hidden])');await p.click('#restore-all');
 assert.match(await p.locator('#hidden-parts').textContent(),/\(0\)/);
 const api=await p.request.get(new URL('/api/part-notes',p.url()).href);assert.equal(api.status(),200);assert.match(api.headers()['cache-control'],/no-store/);assert.equal((await api.json()).notes.length,0);
 assert.ok((await p.context().cookies()).some(c=>c.name==='studio_part_notes'&&c.httpOnly&&c.secure&&c.sameSite==='Strict'));
 assert.deepEqual(errors,[]);console.log('PASS: public HTTPS selected CAD part; half and fully transparent; right-click unhide; private uncached API and secure workspace cookie; no production annotations written');await b.close();
})().catch(e=>{console.error(e);process.exit(1)});
