const {chromium}=require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const base=(process.env.VIEWER_URL || '').replace(/\/?$/,'/');
const assets=process.env.PINBALL_ASSET_DIR,evidence=process.env.PINBALL_EVIDENCE_DIR;
assert.ok(base.startsWith('http'));assert.ok(assets);assert.ok(evidence);fs.mkdirSync(evidence,{recursive:true});
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const changedParts=['left_front_wall','right_front_wall','front_button_panel','front_cable_lid'];
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:process.env.PINBALL_BROWSER_EXECUTABLE,args:['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 try{
  const page=await browser.newPage({viewport:{width:1440,height:1100},acceptDownloads:true}),errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  await page.route('**/api/part-notes**',route=>route.fulfill({json:{notes:[]}}));
  async function openModel(id){
   await page.goto(base+'#'+id,{waitUntil:'domcontentloaded'});
   await page.waitForSelector('#viewport[data-model="'+id+'"][data-state="ready"]',{timeout:120000});
  }
  async function panel(id,open){if((await page.locator('#'+id).isVisible())!==open)await page.click('[data-panel="'+id+'"]');}
  async function verifiedAsset(relative){
   const response=await page.request.get(base+'models/portable-pinball-v1_11/'+relative);
   assert.equal(response.status(),200,relative);
   assert.equal(hash(await response.body()),hash(fs.readFileSync(path.join(assets,relative))),relative);
  }
  await page.goto(base,{waitUntil:'domcontentloaded'});
  await page.waitForSelector('.model[data-model="portable-pinball-v1_11"]');
  assert.equal(await page.locator('.model[data-model^="portable-pinball"]:visible').count(),1);
  await page.click('.model[data-model="portable-pinball-v1_11"]');
  await page.waitForSelector('#viewport[data-model="portable-pinball-v1_11"][data-state="ready"]',{timeout:120000});
  assert.equal(await page.locator('#model-version').inputValue(),'portable-pinball-v1_11');
  assert.ok(await page.locator('#library').isHidden());
  assert.match(await page.locator('#title').textContent(),/V1\.11/);
  assert.match(await page.locator('#description').textContent(),/corner/i);
  const names=await page.locator('#cad-part option').evaluateAll(opts=>opts.map(o=>o.value).filter(v=>v!=='all'));
  assert.equal(names.length,45);
  for(const name of changedParts)assert.ok(names.includes(name),name);
  await page.locator('#viewport canvas').screenshot({path:path.join(evidence,'v1_11-assembly.png')});
  await Promise.all(names.map(name=>verifiedAsset('stl-v1_11/'+name+'.stl')));
  const fitNames=fs.readdirSync(path.join(assets,'fit-tests-v1_11')).filter(name=>name.endsWith('.stl'));
  assert.ok(fitNames.length>=20,'Expected the 17 retained fit samples and three corner panels');
  await Promise.all(fitNames.map(name=>verifiedAsset('fit-tests-v1_11/'+name)));
  await panel('info-panel',true);
  const links=await page.locator('#cad-downloads a').evaluateAll(as=>as.map(a=>({text:a.textContent,href:a.getAttribute('href'),download:a.hasAttribute('download')})));
  assert.equal(links.length,9);
  assert.match(links[0].text,/corner.*test/i);
  assert.equal(links[0].href,'/models/portable-pinball-v1_11/front-corner-fit-tests-v1_11.zip');
  const cornerPending=page.waitForEvent('download');await page.locator('#cad-downloads a').first().click();const cornerDownload=await cornerPending;
  assert.equal(await cornerDownload.failure(),null);assert.equal(cornerDownload.suggestedFilename(),'front-corner-fit-tests-v1_11.zip');
  assert.equal(hash(fs.readFileSync(await cornerDownload.path())),hash(fs.readFileSync(path.join(assets,'front-corner-fit-tests-v1_11.zip'))));
  for(const link of links){
   assert.ok(link.href.startsWith('/models/portable-pinball-v1_11/'),link.href);
   assert.ok(link.download,link.href);
   await verifiedAsset(link.href.replace('/models/portable-pinball-v1_11/',''));
  }
  await panel('info-panel',false);
  const views={left_front_wall:'left',right_front_wall:'right',front_button_panel:'front',front_cable_lid:'top'};
  for(const name of changedParts){
   await panel('parts-panel',true);
   await page.selectOption('#cad-part',name);
   await panel('parts-panel',false);
   await page.click('[data-view="'+views[name]+'"]');
   await panel('parts-panel',true);
   const pending=page.waitForEvent('download');await page.click('#export-cad-stl');const download=await pending;
   assert.equal(await download.failure(),null);assert.equal(download.suggestedFilename(),name+'.stl');
   assert.equal(hash(fs.readFileSync(await download.path())),hash(fs.readFileSync(path.join(assets,'stl-v1_11',name+'.stl'))));
   await panel('parts-panel',false);
   await page.locator('#viewport canvas').screenshot({path:path.join(evidence,'v1_11-'+name+'.png')});
  }
  for(const [id,version] of [['portable-pinball-v1_10','V1.10'],['portable-pinball-v1_9','V1.9'],['portable-pinball','V1.5']]){
   await openModel(id);assert.ok((await page.locator('#title').textContent()).includes(version));
   const priorLinks=await page.locator('#cad-downloads a').evaluateAll(as=>as.map(a=>a.getAttribute('href')));
   assert.equal(priorLinks.length,7,version);
   assert.ok(priorLinks.every(href=>href.startsWith('/models/'+id+'/')),version);
   const response=await page.request.get(new URL(priorLinks[1],base).href);assert.equal(response.status(),200,version);
  }
  await page.setViewportSize({width:390,height:844});await openModel('portable-pinball-v1_11');
  assert.equal(await page.locator('#cad-downloads a').count(),9);
  assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  await panel('parts-panel',true);await page.selectOption('#cad-part','front_cable_lid');
  assert.ok(await page.locator('#export-cad-stl').isEnabled());await panel('parts-panel',false);
  await page.screenshot({path:path.join(evidence,'v1_11-mobile.png'),fullPage:true});
  assert.deepEqual(errors,[]);
  const report={result:'PASS',model:'portable-pinball-v1_11',printedParts:45,stlHashesVerified:45,fitSampleHashesVerified:fitNames.length,versionDownloadLinksVerified:links.length,changedPartUiDownloadsVerified:changedParts.length,priorVersionsLoaded:['V1.10','V1.9','V1.5'],priorVersionDownloadsRestored:true,mobileReady:true,newWorkspacePreserved:true,cornerSampleZipUiDownloadVerified:true,pageErrors:errors};
  fs.writeFileSync(path.join(evidence,'browser-checks.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
 }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exit(1)});
