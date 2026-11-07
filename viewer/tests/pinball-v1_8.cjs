const {chromium}=require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const base=(process.env.VIEWER_URL || '').replace(/\/?$/,'/');
const assets=process.env.PINBALL_ASSET_DIR,evidence=process.env.PINBALL_EVIDENCE_DIR;
assert.ok(base.startsWith('http'));assert.ok(assets);assert.ok(evidence);fs.mkdirSync(evidence,{recursive:true});
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:process.env.PINBALL_BROWSER_EXECUTABLE,args:['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 const page=await browser.newPage({viewport:{width:1440,height:1100},acceptDownloads:true}),errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 await page.route('**/api/part-notes**',route=>route.fulfill({json:{notes:[]}}));
 async function openModel(id){
  await page.goto(base+'#'+id,{waitUntil:'domcontentloaded'});
  await page.waitForSelector('#viewport[data-model="'+id+'"][data-state="ready"]',{timeout:120000});
 }
 await openModel('portable-pinball-v1_8');
 assert.match(await page.locator('#title').textContent(),/V1.8/);
 assert.match(await page.locator('#description').textContent(),/33 mm/);
 const names=await page.locator('#cad-part option').evaluateAll(opts=>opts.map(o=>o.value).filter(v=>v!=='all'));
 assert.equal(names.length,45);
 for(const name of ['left_front_wall','right_front_wall','rear_vent_panel'])assert.ok(names.includes(name));
 await page.locator('#viewport canvas').screenshot({path:path.join(evidence,'v1_8-assembly.png')});
 await Promise.all(names.map(async name=>{
  const response=await page.request.get(base+'models/portable-pinball-v1_8/stl-v1_8/'+name+'.stl');
  assert.equal(response.status(),200,name);assert.equal(hash(await response.body()),hash(fs.readFileSync(path.join(assets,'stl-v1_8',name+'.stl'))),name);
 }));
 const links=await page.locator('#cad-downloads a').evaluateAll(as=>as.map(a=>({text:a.textContent,href:a.getAttribute('href')})));
 assert.equal(links.length,7);
 for(const link of links){
  assert.ok(link.href.startsWith('/models/portable-pinball-v1_8/'));
  const response=await page.request.get(new URL(link.href,base).href);assert.equal(response.status(),200,link.href);
  const rel=link.href.replace('/models/portable-pinball-v1_8/','');
  assert.equal(hash(await response.body()),hash(fs.readFileSync(path.join(assets,rel))),rel);
 }
 for(const name of ['left_front_wall','right_front_wall','rear_vent_panel']){
  await page.selectOption('#cad-part',name);
  await page.click('[data-view="'+(name==='rear_vent_panel'?'back':name.startsWith('left')?'left':'right')+'"]');
  const pending=page.waitForEvent('download');await page.click('#export-cad-stl');const download=await pending;
  assert.equal(await download.failure(),null);assert.equal(download.suggestedFilename(),name+'.stl');
  assert.equal(hash(fs.readFileSync(await download.path())),hash(fs.readFileSync(path.join(assets,'stl-v1_8',name+'.stl'))));
  await page.locator('#viewport canvas').screenshot({path:path.join(evidence,'v1_8-'+name+'.png')});
 }
 for(const [id,version] of [['portable-pinball-v1_7','V1.7'],['portable-pinball-v1_6','V1.6']]){
  await openModel(id);assert.ok((await page.locator('#title').textContent()).includes(version));
  const href=await page.locator('#cad-downloads a').nth(1).getAttribute('href');
  const response=await page.request.get(new URL(href,base).href);assert.equal(response.status(),200,version);
 }
 await page.setViewportSize({width:390,height:844});await openModel('portable-pinball-v1_8');
 await page.selectOption('#cad-part','rear_vent_panel');
 assert.ok(await page.locator('#export-cad-stl').isEnabled());
 await page.screenshot({path:path.join(evidence,'v1_8-mobile.png'),fullPage:true});
 assert.deepEqual(errors,[]);
 const report={result:'PASS',model:'portable-pinball-v1_8',printedParts:45,stlHashesVerified:45,versionDownloadLinksVerified:7,changedPartUiDownloadsVerified:3,priorVersionsLoaded:['V1.7','V1.6'],mobileReady:true,pageErrors:errors};
 fs.writeFileSync(path.join(evidence,'browser-checks.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
 await browser.close();
})().catch(error=>{console.error(error);process.exit(1)});
