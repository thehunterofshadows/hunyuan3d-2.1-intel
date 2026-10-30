const {chromium}=require('/opt/checks/node_modules/playwright');
const assert=require('node:assert/strict'),fs=require('node:fs'),crypto=require('node:crypto');
(async()=>{
 const b=await chromium.launch({args:['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 const p=await b.newPage({viewport:{width:1440,height:1100},acceptDownloads:true}),errors=[];
 p.on('pageerror',e=>{errors.push(e.message);console.log('PAGE ERROR',e.message);});
 await p.route('**/api/part-notes**',r=>r.fulfill({json:{notes:[]}}));
 const base=process.env.VIEWER_URL;
 await p.goto(base+'#portable-pinball',{waitUntil:'domcontentloaded'});await p.waitForSelector('#viewport[data-state=ready]',{timeout:120000});
 assert.ok(await p.locator('#export-selected-stl').isDisabled());assert.ok(await p.locator('#export-cad-stl').isDisabled());
 const names=await p.locator('#cad-part option').evaluateAll(opts=>opts.map(o=>o.value).filter(v=>v!=='all'));assert.equal(names.length,45);
 const hash=x=>crypto.createHash('sha256').update(x).digest('hex');
 for(const name of names){const r=await p.request.get(base+'models/portable-pinball/stl-v1_4/'+name+'.stl');assert.equal(r.status(),200);assert.equal(hash(await r.body()),hash(fs.readFileSync('/cad/'+name+'.stl')),name);}
 async function download(button){const pending=p.waitForEvent('download');await p.click(button);const d=await pending;assert.equal(await d.failure(),null);return {name:d.suggestedFilename(),body:fs.readFileSync(await d.path())};}
 await p.selectOption('#cad-part','monitor_saddle_right_180');let d=await download('#export-cad-stl');assert.equal(d.name,'monitor_saddle_right_180.stl');assert.equal(hash(d.body),hash(fs.readFileSync('/cad/monitor_saddle_right_180.stl')));
 await p.selectOption('#cad-part','front_button_panel');
 const canvas=p.locator('#viewport canvas');await canvas.scrollIntoViewIfNeeded();await p.waitForTimeout(400);let r=await canvas.boundingBox();await p.mouse.click(r.x+r.width/2,r.y+r.height/2);assert.ok(await p.locator('#export-selected-stl').isEnabled());
 d=await download('#export-selected-stl');assert.equal(d.name,'front_button_panel.stl');assert.equal(hash(d.body),hash(fs.readFileSync('/cad/front_button_panel.stl')));
 await p.mouse.click(r.x+r.width/2,r.y+r.height/2,{button:'right'});await p.waitForSelector('#part-popup:not([hidden])');d=await download('#export-part-stl');assert.equal(d.name,'front_button_panel.stl');await p.click('#part-close');
 await p.locator('#explode').fill('1');await p.locator('#explode').dispatchEvent('input');d=await download('#export-selected-stl');assert.equal(hash(d.body),hash(fs.readFileSync('/cad/front_button_panel.stl')));
 await p.selectOption('#cad-part','all');assert.ok(await p.locator('#export-cad-stl').isDisabled());
 // A known 10 x 20 x 30 mm tetrahedron verifies local STL scale, Z-up and single-mesh download.
 const stl='solid test\n'+[[[0,0,0],[0,20,0],[10,0,0]],[[0,0,0],[10,0,0],[0,0,30]],[[0,0,0],[0,0,30],[0,20,0]],[[10,0,0],[0,20,0],[0,0,30]]].map(t=>'facet normal 0 0 0\nouter loop\n'+t.map(v=>'vertex '+v.join(' ')).join('\n')+'\nendloop\nendfacet').join('\n')+'\nendsolid test';
 console.log('CAD exports passed; loading local STL');await p.setInputFiles('#stl-file',{name:'known.stl',mimeType:'model/stl',buffer:Buffer.from(stl)});await p.waitForSelector('#viewport[data-model="local-stl"][data-state="ready"]');console.log('Local STL ready');assert.ok(await p.locator('#export-selected-stl').isDisabled());
 await canvas.scrollIntoViewIfNeeded();await p.waitForTimeout(400);r=await canvas.boundingBox();
 for(let y=.2;y<=.8&&await p.locator('#export-selected-stl').isDisabled();y+=.1)for(let x=.2;x<=.8&&await p.locator('#export-selected-stl').isDisabled();x+=.1)await p.mouse.click(r.x+r.width*x,r.y+r.height*y);
 console.log('Local selected',await p.locator('#export-selected-stl').isEnabled());d=await download('#export-selected-stl');assert.equal(d.body.readUInt32LE(80),4);assert.equal(d.body.length,284);
 const lo=[Infinity,Infinity,Infinity],hi=[-Infinity,-Infinity,-Infinity];for(let i=0;i<4;i++)for(let v=0;v<3;v++)for(let a=0;a<3;a++){const n=d.body.readFloatLE(84+i*50+12+v*12+a*4);lo[a]=Math.min(lo[a],n);hi[a]=Math.max(hi[a],n);}for(let a=0;a<3;a++)assert.ok(Math.abs(hi[a]-lo[a]-[10,20,30][a])<.0001);assert.ok(Math.abs(lo[2])<.0001);
 await p.setViewportSize({width:390,height:844});await p.goto(base+'#portable-pinball');await p.reload({waitUntil:'domcontentloaded'});await p.waitForSelector('#viewport[data-model="portable-pinball"][data-state="ready"]',{timeout:120000});await p.selectOption('#cad-part','monitor_saddle_left_180');d=await download('#export-cad-stl');assert.equal(d.name,'monitor_saddle_left_180.stl');assert.deepEqual(errors,[]);
 console.log('PASS: 45 original CAD STL hashes; dropdown, mesh and inspector downloads; explode independence; selection reset; binary STL mm/Z-up geometry; mobile export.');await b.close();
})().catch(e=>{console.error(e);process.exit(1)});
