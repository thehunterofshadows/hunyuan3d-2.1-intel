const {chromium}=require('/opt/checks/node_modules/playwright');
const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 const page=await browser.newPage({viewport:{width:1360,height:920},deviceScaleFactor:1});
 const base=process.env.VIEWER_URL||'http://intel-3d-studio-prod-web/';
 const errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 await page.goto(base+'#m18-usb-charger-v1',{waitUntil:'domcontentloaded'});
 await page.waitForSelector('#viewport[data-state=ready][data-model=m18-usb-charger-v1]',{timeout:90000});
 assert.match(await page.locator('#title').textContent(),/M18/);
 await page.locator('[data-panel=info-panel]').click();
 assert.equal(await page.locator('#cad-downloads a').count(),5);
 const files=['m18-usb-charger-v1.glb','m18-usb-charger-v1-print-pack.zip','m18-usb-socket-housing-v1.step','stl/M18_USB_Socket_Housing_v1.stl','README.md','preview.png'];
 for(const file of files){
  const r=await page.request.get(new URL('/models/m18-usb-charger-v1/'+file,base).href);
  assert.equal(r.status(),200,file+' '+r.status());
  if(file.endsWith('.glb'))assert.equal((await r.body()).subarray(0,4).toString(),'glTF');
 }
 if(process.env.SCREENSHOT_PATH)await page.locator('#viewport').screenshot({path:process.env.SCREENSHOT_PATH});
 await page.setViewportSize({width:390,height:844});
 assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
 assert.deepEqual(errors,[]);
 console.log('M18 USB PASS: rendered model, 5 downloads, 6 files HTTP200, mobile layout, no page errors');
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
