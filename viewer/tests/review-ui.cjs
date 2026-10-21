const {chromium}=require('/opt/checks/node_modules/playwright');
const assert=require('node:assert/strict');
(async()=>{
 const b=await chromium.launch({args:['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 const p=await b.newPage({viewport:{width:1440,height:1100}});p.setDefaultTimeout(60000);const errors=[];p.on('pageerror',e=>errors.push(e.message));
 let note={model:{id:'portable-pinball',name:'Cabinet'},part:{id:'cad:front_button_panel',name:'Panel'},text:'Check this panel',revision:1,history:[]};
 await p.route('**/api/part-notes**',async route=>{
  if(route.request().method()==='POST'){
   const body=route.request().postDataJSON();
   if(body.expectedRevision!==note.revision)return route.fulfill({status:409,json:{error:'Revision conflict',current:note}});
   const history=[...note.history];if(note.reviewed)history.push({...note,history:undefined});
   note={...body,history,reviewed:false,revision:note.revision+1,updatedAt:new Date().toISOString()};
   return route.fulfill({json:{note}});
  }
  return route.fulfill({json:{notes:[note]}});
 });
 await p.route('**/*',route=>route.request().resourceType()==='image'?route.abort():route.fallback());
 await p.goto('http://intel3d-review-web/#portable-pinball');await p.waitForSelector('#viewport[data-state=ready]');await p.selectOption('#cad-part','front_button_panel');
 const c=p.locator('#viewport canvas');await c.scrollIntoViewIfNeeded();await p.waitForTimeout(500);const r=await c.boundingBox(),x=r.x+r.width/2,y=r.y+r.height/2;
 await p.mouse.click(x,y);assert.equal(await p.locator('#part-popup').isVisible(),false);await p.mouse.click(x,y,{button:'right'});await p.waitForSelector('#part-popup:not([hidden])');
 await p.waitForFunction(()=>document.querySelector('#part-note').value==='Check this panel');assert.equal(await p.locator('#review-rows tr').count(),0);
 note={...note,reviewed:true,revision:2,reviewedAt:new Date().toISOString(),reviewResponse:'Checked, no change needed.'};
 await p.waitForFunction(()=>document.querySelector('#part-note').value==='',{},{timeout:10000});assert.match(await p.locator('#review-rows').textContent(),/Check this panel/);assert.match(await p.locator('#review-rows').textContent(),/Checked, no change needed/);
 await p.fill('#part-note','Follow-up');await p.click('#save-note');await p.waitForFunction(()=>document.querySelector('#note-status').textContent.startsWith('Saved on Mini'));assert.equal(note.reviewed,false);assert.equal(note.history.length,1);
 // Agent reviews saved version while a new local edit is pending: never clear that draft.
 await p.fill('#part-note','Do not erase my newer edit');note={...note,reviewed:true,revision:note.revision+1,reviewedAt:new Date().toISOString(),reviewResponse:'Answered follow-up'};
 await p.waitForFunction(()=>document.querySelector('#note-status').textContent.includes('Revision conflict'));assert.equal(await p.inputValue('#part-note'),'Do not erase my newer edit');
 assert.equal(await p.locator('#reload-note').isVisible(),true);await p.click('#reload-note');await p.waitForFunction(()=>document.querySelector('#note-status').textContent==='Loaded saved note.');assert.equal(await p.inputValue('#part-note'),'');assert.equal(await p.locator('#review-rows tr').count(),2);
 await p.setViewportSize({width:390,height:844});assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));assert.deepEqual(errors,[]);
 console.log('PASS: pending-only editor; automatic reviewed history; new note preserves history; newer local draft survives agent review; reload; right-click selection; mobile width');await b.close();
})().catch(e=>{console.error(e);process.exit(1)});
