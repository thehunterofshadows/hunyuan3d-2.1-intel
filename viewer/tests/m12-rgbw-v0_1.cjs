const {chromium}=require('/opt/checks/node_modules/playwright');
const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 const page=await browser.newPage({viewport:{width:1360,height:920},deviceScaleFactor:1});
 const base=process.env.VIEWER_URL||'http://intel-3d-studio-prod-web/';
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(base+'#m12-rgbw-v0_1',{waitUntil:'domcontentloaded'});
 await page.waitForSelector('#viewport[data-state=ready][data-model=m12-rgbw-v0_1]',{timeout:120000});
 assert.match(await page.locator('#title').textContent(),/M12/);
 await page.locator('[data-panel=info-panel]').click();
 assert.equal(await page.locator('#cad-downloads a').count(),7);
 for(const p of ['m12-rgbw-lantern-v0_1.glb','m12-rgbw-v0_1-print-pack.zip','m12-accessories-v0_1.step','stl/rocker-slot_two-button_bezel.stl','stl/esp32_cutoff_electronics_spine.stl','README.md']){
  const r=await page.request.get(new URL('/models/m12-rgbw-v0_1/'+p,base).href);
  assert.equal(r.status(),200,p+' '+r.status());
  if(p.endsWith('.glb'))assert.equal((await r.body()).subarray(0,4).toString(),'glTF');
 }
 await page.locator('[data-panel=info-panel]').click();
 if(process.env.SCREENSHOT_PATH){await page.locator('#viewport').screenshot({path:process.env.SCREENSHOT_PATH});}
 await page.setViewportSize({width:390,height:844});
 assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'Mobile page overflow');
 assert.deepEqual(errors,[]);
 console.log('M12 RGBW PASS: GLB visible, source files HTTP200, CAD downloads, no page errors, mobile fits');
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
