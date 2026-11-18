const {chromium}=require('/opt/checks/node_modules/playwright');
const assert=require('node:assert/strict');
(async()=>{
  const browser=await chromium.launch({headless:true,args:['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
  const page=await browser.newPage({viewport:{width:1200,height:900}});
  const errors=[];
  page.on('pageerror',e=>errors.push(String(e)));
  await page.goto('http://intel-3d-studio-prod-web/#chico-volume-buttons-v3',{waitUntil:'domcontentloaded'});
  await page.waitForSelector('#viewport[data-state=ready][data-model=chico-volume-buttons-v3]',{timeout:90000});
  const canvases=await page.locator('canvas').count();
  assert(canvases>0,'canvas not found');
  await page.locator('[data-panel=info-panel]').click();
  const title=await page.locator('#title').innerText();
  assert(title.includes('Volume Buttons V3'),title);
  const links=await page.locator('#cad-downloads a').evaluateAll(as=>as.map(a=>({label:a.textContent,href:a.href})));
  assert.equal(links.length,13,'missing volume STL/STEP downloads');
  for(const l of links){
    const response=await page.request.get(l.href);
    assert.equal(response.status(),200,l.href);
    assert((await response.body()).length>200,l.href);
  }
  const pack=links.find(l=>l.href.endsWith('print-pack.zip'));
  assert(pack,'print pack missing');
  await page.locator('[data-panel=info-panel]').click();
  await page.locator('#viewport').screenshot({path:'/out/chico-volume-v3-viewer.png'});
  await page.setViewportSize({width:390,height:844});
  await page.waitForTimeout(400);
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'mobile horizontal overflow');
  assert.deepEqual(errors,[],'JS errors');
  await browser.close();
  console.log(JSON.stringify({PASS:true,title,links:links.length,canvas:canvases,pack:pack.href,mobile:'ok',pageErrors:errors.length}));
})().catch(e=>{console.error(e);process.exit(1)});

