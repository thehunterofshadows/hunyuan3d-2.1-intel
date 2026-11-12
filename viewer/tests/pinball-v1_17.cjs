const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const base=(process.env.VIEWER_URL||'http://127.0.0.1:18888/').replace(/\/?$/,'/');
const assets=process.env.PINBALL_ASSET_DIR||'/assets';
const evidence=process.env.PINBALL_EVIDENCE_DIR||'/evidence';
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
fs.mkdirSync(evidence,{recursive:true});
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 try{
  const page=await browser.newPage({viewport:{width:1440,height:1000},acceptDownloads:true});let errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  await page.route('**/api/part-notes**',route=>route.fulfill({json:{notes:[]}}));
  await page.goto(base,{waitUntil:'domcontentloaded'});
  await page.waitForSelector('.model[data-model="portable-pinball-v1_17"]',{timeout:30000});
  assert.equal(await page.locator('.model[data-model^="portable-pinball"]:visible').count(),1);
  await page.click('.model[data-model="portable-pinball-v1_17"]');
  await page.waitForSelector('#viewport[data-model="portable-pinball-v1_17"][data-state="ready"]',{timeout:120000});
  assert.match(await page.locator('#title').textContent(),/V1\.17/);
  assert.equal(await page.locator('#model-version').inputValue(),'portable-pinball-v1_17');
  const names=await page.locator('#cad-part option').evaluateAll(xs=>xs.map(x=>x.value).filter(x=>x!=='all'));
  assert.equal(names.length,71,names.length);
  for(const n of ['foot_receiver_left_front','foot_backing_right_rear','foot_twist_core_left_rear_1_45mm','foot_m8_terminal_core_left_rear_55mm','foot_m8_terminal_sleeve_right_front_55mm','foot_m8_terminal_bolt_key_left_front_55mm','bottom_front','bottom_rear'])assert.ok(names.includes(n),n);
  const links=await page.locator('#cad-downloads a').evaluateAll(as=>as.map(a=>a.getAttribute('href')));
  assert.equal(links.length,9);for(const l of links){assert.ok(l.startsWith('/models/portable-pinball-v1_17/'),l);const f=path.join(assets,l.split('/models/portable-pinball-v1_17/')[1]);const r=await page.request.get(base.replace(/\/$/,'')+l);assert.equal(r.status(),200,l);assert.equal(hash(await r.body()),hash(fs.readFileSync(f)),l);}
  await page.locator('#viewport canvas').screenshot({path:path.join(evidence,'v1_17-assembly.png')});
  await page.click('[data-view="left"]');await page.waitForTimeout(400);
  await page.locator('#viewport canvas').screenshot({path:path.join(evidence,'v1_17-side.png')});
  // inspect a foot as independently editable/exportable STL part
  await page.locator('[data-panel="parts-panel"]').click();
  await page.selectOption('#cad-part','foot_receiver_left_front');
  assert.ok(await page.locator('#export-cad-stl').isEnabled());
  await page.locator('[data-panel="parts-panel"]').click();
  await page.locator('#viewport canvas').screenshot({path:path.join(evidence,'v1_17-receiver-isolated.png')});
  await page.locator('[data-panel="parts-panel"]').click();await page.selectOption('#cad-part','all');
  await page.locator('#cad-feet').uncheck(); await page.locator('#cad-feet').check();
  await page.locator('[data-panel="parts-panel"]').click();
  const old=[['portable-pinball-v1_16','V1.16'],['portable-pinball-v1_15','V1.15']];
  for(const [id,version] of old){await page.goto(base+'#'+id,{waitUntil:'domcontentloaded'});await page.waitForSelector('#viewport[data-model="'+id+'"][data-state="ready"]',{timeout:120000});assert.match(await page.locator('#title').textContent(),new RegExp(version.replace('.','\\.')))}
  await page.setViewportSize({width:390,height:844});await page.goto(base+'#portable-pinball-v1_17',{waitUntil:'domcontentloaded'});await page.waitForSelector('#viewport[data-model="portable-pinball-v1_17"][data-state="ready"]',{timeout:120000});assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth),'mobile width overflow');
  await page.screenshot({path:path.join(evidence,'v1_17-mobile.png'),fullPage:true});
  assert.deepEqual(errors,[]);
  console.log(JSON.stringify({result:'PASS',url:base,printableParts:names.length,urlsVerified:links.length,earlierVersionsPreserved:true,footReferenceToggle:true,mobileNoOverflow:true,pageErrors:errors}));
 } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
