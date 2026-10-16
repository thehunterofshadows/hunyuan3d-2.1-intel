const {chromium}=require('/opt/checks/node_modules/playwright');
const fs=require('node:fs');
const assert=require('node:assert/strict');
const slugs=['flipper','plunger','slingshot','target','pop-bumper'];
(async()=>{
 const browser=await chromium.launch({args:['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 const page=await browser.newPage({viewport:{width:1440,height:900},deviceScaleFactor:1});
 const issues=[];
 page.on('pageerror',e=>issues.push(e.message));
 const origin=process.env.VIEWER_URL||'http://intel-3d-studio-prod-web/';
 for (const slug of slugs){
   const id='trellis-pinball-'+slug;
   await page.goto(origin+'?model='+slug+'#'+id,{waitUntil:'domcontentloaded'});
   await page.waitForSelector('#viewport[data-state=ready]',{timeout:90000});
   assert.equal(await page.locator('#viewport').getAttribute('data-model'),id);
   const txt=await page.locator('#stats').innerText();
   assert.match(txt,/[0-9,]+ triangles · 2048px textures/);
   const tris=Number(txt.match(/[\d,]+/)[0].replaceAll(',',''));
   assert(tris>50000&&tris<500000,id+' triangles expected evaluation range');
   const href=await page.locator('#download').getAttribute('href');
   const response=await page.request.get(new URL(href,page.url()).href);
   assert.equal(response.status(),200,id+' download');
   assert.equal((await response.body()).subarray(0,4).toString(),'glTF');
   await page.waitForTimeout(350);
   const outfile='/assets/'+id+'/preview.png';
   await page.locator('#viewport canvas').screenshot({path:outfile});
   assert(fs.statSync(outfile).size>5000,id+' screenshot size');
   console.log('PASS '+slug+' triangles='+tris+' preview='+outfile);
 }
 assert.deepEqual(issues,[]);
 await page.setViewportSize({width:390,height:844});
 await page.goto(origin+'#trellis-pinball-flipper');
 await page.waitForSelector('#viewport[data-state=ready]',{timeout:90000});
 assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'mobile overflows');
 console.log('PASS mobile layout and 5 independent source GLBs');
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
