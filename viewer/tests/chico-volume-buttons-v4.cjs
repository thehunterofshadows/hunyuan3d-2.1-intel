const {chromium}=require('/opt/checks/node_modules/playwright');
const assert=require('node:assert/strict');
const base=(process.env.VIEWER_URL||'http://intel-3d-studio-prod-web').replace(/\/$/,'');
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 try{
  const page=await browser.newPage({viewport:{width:1200,height:900}});
  const errors=[];page.on('pageerror',e=>errors.push(String(e)));
  await page.goto(base,{waitUntil:'domcontentloaded'});
  await page.waitForSelector('.model[data-model="chico-volume-buttons-v4"]',{state:'visible'});
  for(const n of [1,2,3])assert.equal(await page.locator(`.model[data-model="chico-volume-buttons-v${n}"]`).isHidden(),true,`V${n} appears separately`);
  assert.equal(await page.locator('.model[data-model="chico-volume-buttons-v4"]').getAttribute('aria-pressed'),'false');
  assert.match(await page.locator('.model[data-model="chico-volume-buttons-v4"]').innerText(),/4 versions/);
  assert.equal(await page.locator('.model[data-model^="portable-pinball"]').filter({visible:true}).count(),1,'cabinet version grouping regressed');
  await page.locator('.model[data-model="chico-volume-buttons-v4"]').click();
  await page.waitForSelector('#viewport[data-state="ready"][data-model="chico-volume-buttons-v4"]',{timeout:90000});
  assert.equal(await page.locator('#model-version').isVisible(),true);
  assert.equal(await page.locator('#model-version option').count(),4);
  assert.equal(await page.locator('#model-version').inputValue(),'chico-volume-buttons-v4');
  await page.locator('[data-panel="info-panel"]').click();
  const links=await page.locator('#cad-downloads a').evaluateAll(as=>as.map(a=>({label:a.textContent,href:a.getAttribute('href')})));
  assert.equal(links.length,13);
  for(const l of links){assert(l.href.startsWith('/models/chico-volume-buttons-v4/'),l.href);const response=await page.request.get(base+l.href);assert.equal(response.status(),200,l.href);assert((await response.body()).length>200,l.href);}
  await page.locator('[data-panel="info-panel"]').click();
  for(const n of [3,2,1,4]){
   await page.locator('#model-version').selectOption(`chico-volume-buttons-v${n}`);
   await page.waitForSelector(`#viewport[data-state="ready"][data-model="chico-volume-buttons-v${n}"]`,{timeout:90000});
   assert.equal(await page.locator('#model-version').inputValue(),`chico-volume-buttons-v${n}`);
  }
  await page.locator('#back-library').click();
  await page.waitForSelector('body.library-mode');
  assert.equal(await page.locator('.model[data-model="chico-volume-buttons-v4"]').isVisible(),true);
  for(const n of [1,2,3])assert.equal(await page.locator(`.model[data-model="chico-volume-buttons-v${n}"]`).isHidden(),true);
  await page.setViewportSize({width:390,height:844});
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth+1),'mobile overflow');
  assert.deepEqual(errors,[],'JS errors');
  console.log(JSON.stringify({PASS:true,model:'chico-volume-buttons-v4',downloadLinks:links.length,versions:4,olderVersionsAccessible:true,oneCard:true,mobile:true,pageErrors:0}));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
