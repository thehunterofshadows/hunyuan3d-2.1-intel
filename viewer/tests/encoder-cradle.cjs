const {chromium}=require('/opt/checks/node_modules/playwright');
const assert=require('node:assert/strict');
(async()=>{
const browser=await chromium.launch({headless:true,args:['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
const page=await browser.newPage({viewport:{width:1200,height:900}});
const errors=[];page.on('pageerror',e=>errors.push(e.message));
await page.goto('http://intel-3d-studio-prod-web/#encoder-cradle-v1');
await page.waitForSelector('#viewport[data-state=ready][data-model=encoder-cradle-v1]',{timeout:120000});
await page.locator('[data-panel=info-panel]').click();
assert.equal(await page.locator('#cad-downloads a').count(),7);
for(const href of await page.locator('#cad-downloads a').evaluateAll(a=>a.map(x=>x.href))){const r=await page.request.get(href);assert.equal(r.status(),200,href);assert((await r.body()).length>100);}
await page.locator('[data-panel=info-panel]').click();
await page.locator('[data-view=top]').click().catch(()=>{});
await page.locator('#viewport').screenshot({path:'/out/preview.png'});
await page.setViewportSize({width:390,height:844});
assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
assert.deepEqual(errors,[]);
await browser.close();console.log('PASS real GLB render, seven downloads, mobile, no page errors');
})().catch(e=>{console.error(e);process.exit(1)});

