// Real HTTP GLB modified timestamps and sorting, keeping folder navigation intact.
const {chromium}=require('/opt/checks/node_modules/playwright');
const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({args:['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 const origin=process.env.VIEWER_URL||'http://intel-3d-studio-prod-web/';
 const page=await browser.newPage({viewport:{width:1440,height:900}});
 const errors=[];page.on('pageerror',error=>errors.push(error.message));
 await page.goto(origin+'#railgun-detail-v2',{waitUntil:'domcontentloaded'});
 await page.waitForSelector('#viewport[data-state=ready][data-model=railgun-detail-v2]',{timeout:120000});
 await page.waitForFunction(()=>Array.from(document.querySelectorAll('.model time')).every(t=>!t.textContent.includes('Loading')),null,{timeout:30000});
 assert.equal(await page.locator('.model time').count(),17);
 assert.equal(await page.locator('#model-sort').inputValue(),'newest');
 assert.equal(await page.locator('[data-folder=instagib] .model').count(),9);
 assert.equal(await page.locator('[data-folder=pinball] .model').count(),8);
 assert.equal(await page.locator('[data-folder=instagib] .model').first().getAttribute('data-model'),'railgun-detail-v2');
 assert.match(await page.locator('#model-modified').textContent(),/Modified .*2026/);
 const dates=await page.locator('.model time').evaluateAll(nodes=>nodes.map(n=>[n.closest('.model').dataset.model,n.dateTime,n.textContent]));
 assert(dates.every(([,date,label])=>Boolean(date)&&label.includes('Modified')),'Every model needs a real modified date');
 assert.equal(dates.find(([id])=>id==='portable-pinball')[1],'2026-10-16T20:42:03Z','reproducible CAD timestamp fallback');
 const sorted=async (folder,ascending)=>{
  const values=await page.locator('[data-folder='+folder+'] .model time').evaluateAll(nodes=>nodes.map(n=>Date.parse(n.dateTime)));
  assert(values.every(Number.isFinite));
  const expectation=[...values].sort((a,b)=>ascending?a-b:b-a);
  assert.deepEqual(values,expectation,folder+' date order');
 };
 await sorted('instagib',false);await sorted('pinball',false);
 await page.selectOption('#model-sort','oldest');
 await sorted('instagib',true);await sorted('pinball',true);
 await page.selectOption('#model-sort','name');
 for(const folder of ['instagib','pinball']){
  const names=await page.locator('[data-folder='+folder+'] .model strong').allTextContents();
  assert.deepEqual(names,[...names].sort((a,b)=>a.localeCompare(b)),'alphabetical sort '+folder);
 }
 await page.selectOption('#model-sort','newest');
 await page.locator('#model-search').fill('ultra');
 assert.equal(await page.locator('.model:visible').count(),2);
 await page.locator('#model-search').fill('');
 await page.locator('[data-folder=pinball] summary').click();
 await page.locator('.model[data-model=portable-pinball]').click();
 await page.waitForSelector('#viewport[data-state=ready][data-model=portable-pinball]',{timeout:120000});
 assert.match(await page.locator('#model-modified').textContent(),/Oct 16, 2026/);
 await page.setViewportSize({width:390,height:844});
 assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'mobile has no overflow');
 assert.deepEqual(errors,[]);
 await browser.close();
 console.log('PASS: 17 model file dates, CAD fallback, newest/oldest/name sorting inside folders, details, search, mobile viewport');
})().catch(error=>{console.error(error);process.exit(1)});
