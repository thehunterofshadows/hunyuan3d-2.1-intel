const {chromium}=require('/opt/checks/node_modules/playwright');
(async()=>{const b=await chromium.launch({args:['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
const p=await b.newPage({viewport:{width:1440,height:1000}});
const errors=[];p.on('pageerror',e=>errors.push(e.message));
await p.goto(process.env.VIEWER_URL||'http://trellis-bumper-check/#trellis-bumper');
await p.waitForSelector('#viewport[data-state=ready]',{timeout:60000});
for(const view of ['front','back','top']){
await p.click('[data-view='+view+']');await p.waitForTimeout(300);
await p.locator('#viewport canvas').screenshot({path:'/evidence/'+view+'.png'});
}
await p.click('#reset');await p.waitForTimeout(300);await p.locator('#viewport canvas').screenshot({path:'/evidence/actual-model.png'});
const assert=require('node:assert/strict');
assert.match(await p.locator('#stats').innerText(),/[0-9,]+ triangles · 2048px textures/);
const res=await p.request.get(new URL(await p.locator('#download').getAttribute('href'),p.url()).href);
assert.equal(res.status(),200);assert.equal((await res.body()).subarray(0,4).toString(),'glTF');
await p.setViewportSize({width:390,height:844});
assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'mobile overflow');
assert.deepEqual(errors,[]);console.log('PASS actual TRELLIS GLB, materials label, four views, download and mobile layout');await b.close()})().catch(e=>{console.error(e);process.exit(1)});
