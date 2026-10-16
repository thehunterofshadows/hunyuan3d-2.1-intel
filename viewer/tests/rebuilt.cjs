const {chromium}=require('/opt/checks/node_modules/playwright');
const fs=require('fs'),assert=require('assert');
(async()=>{
 const browser=await chromium.launch({args:['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 const page=await browser.newPage({viewport:{width:1440,height:1000}});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(process.env.VIEWER_URL||'http://railgun-built-check/');
 await page.waitForSelector('#viewport[data-state=ready][data-model=railgun-built]',{timeout:60000});
 await page.screenshot({path:'/evidence/rebuilt-desktop.png',fullPage:true});
 await page.locator('#viewport canvas').screenshot({path:'/evidence/rebuilt-model.png'});
 for(const view of ['front','back','top']){
  await page.click('[data-view='+view+']');await page.waitForTimeout(500);
  await page.locator('#viewport canvas').screenshot({path:'/evidence/rebuilt-'+view+'.png'});
 }
 await page.click('#reset');
 const url=new URL(await page.locator('#download').getAttribute('href'),page.url()).href;
 const res=await page.request.get(url);assert.equal(res.status(),200);
 const data=await res.body();assert.equal(data.subarray(0,4).toString(),'glTF');
 const doc=JSON.parse(data.subarray(20,20+data.readUInt32LE(12)));
 assert(doc.materials.some(m=>m.emissiveFactor?.some(v=>v>0)));
 assert(doc.nodes.some(n=>n.name==='Muzzle'));
 assert(doc.nodes.some(n=>n.name==='RightHand'));
 assert.deepEqual(errors,[]);
 console.log('PASS actual rebuilt GLB loaded; emissive materials and attachment nodes verified; screenshots saved');
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
