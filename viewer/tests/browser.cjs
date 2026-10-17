const {chromium}=require('/opt/checks/node_modules/playwright');
const assert=require('node:assert/strict');
(async()=>{
const browser=await chromium.launch({headless:true,args:['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
const page=await browser.newPage({viewport:{width:1440,height:1000}});
const errors=[];page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
await page.goto(process.env.VIEWER_URL||'http://intel-3d-studio-prod-web/');
await page.waitForSelector('#viewport[data-state=ready]',{timeout:60000});
for(const id of ['bumper','woman','railgun']){
 await page.locator('[data-model="'+id+'"]').evaluate(el=>el.closest('details').open=true);
 await page.click('[data-model="'+id+'"]');
 await page.waitForSelector('#viewport[data-state=ready][data-model="'+id+'"]');
 assert.match(await page.locator('#stats').textContent(),/40,000/);
 const response=await page.request.get(new URL(await page.locator('#download').getAttribute('href'),page.url()).href);
 assert.equal(response.status(),200);assert.equal((await response.body()).subarray(0,4).toString(),'glTF');
}
await page.locator('#viewport canvas').screenshot({path:'/evidence/railgun-before.png'});
const before=await page.locator('#viewport canvas').screenshot();
const box=await page.locator('#viewport').boundingBox();
await page.mouse.move(box.x+box.width*.6,box.y+box.height*.5);await page.mouse.down();
await page.mouse.move(box.x+box.width*.8,box.y+box.height*.6,{steps:12});await page.mouse.up();await page.waitForTimeout(700);
assert.notDeepEqual(await page.locator('#viewport canvas').screenshot(),before,'drag should rotate');
const rotated=await page.locator('#viewport canvas').screenshot();await page.mouse.wheel(0,-300);await page.waitForTimeout(700);
assert.notDeepEqual(await page.locator('#viewport canvas').screenshot(),rotated,'wheel should zoom');
await page.selectOption('#surface','clay');await page.check('#wireframe');await page.selectOption('#lighting','soft');await page.selectOption('#background','#dce1e7');
await page.click('[data-view=back]');await page.click('#reset');
await page.uncheck('#wireframe');await page.selectOption('#surface','pbr');await page.selectOption('#background','#161d25');await page.selectOption('#lighting','studio');
await page.screenshot({path:'/evidence/desktop.png',fullPage:true});
await page.locator('[data-model=woman]').evaluate(el=>el.closest('details').open=true);await page.click('[data-model=woman]');await page.waitForSelector('#viewport[data-state=ready][data-model=woman]');
await page.screenshot({path:'/evidence/woman.png',fullPage:true});
const mobile=await browser.newPage({viewport:{width:390,height:844},isMobile:true,hasTouch:true,deviceScaleFactor:1});
await mobile.goto(process.env.VIEWER_URL||'http://intel-3d-studio-prod-web/');await mobile.waitForSelector('#viewport[data-state=ready]',{timeout:60000});
await mobile.locator('[data-model=bumper]').evaluate(el=>el.closest('details').open=true);await mobile.locator('[data-model=bumper]').tap();await mobile.waitForSelector('#viewport[data-state=ready][data-model=bumper]');
assert.ok(await mobile.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'no horizontal overflow');
await mobile.screenshot({path:'/evidence/mobile.png',fullPage:true});
assert.deepEqual(errors,[]);console.log('PASS: three GLBs, desktop rotate/zoom, inspection controls, mobile selection/layout; no browser errors');
await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
