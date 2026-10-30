import * as THREE from 'three';
import { STLExporter } from 'three/addons/exporters/STLExporter.js';
const $=id=>document.getElementById(id);
const API='/api/part-notes';
const safeStore={get(k){try{return localStorage.getItem(k);}catch{return null;}},set(k,v){try{localStorage.setItem(k,v);}catch{}},remove(k){try{localStorage.removeItem(k);}catch{}}};
export function sha256(bytes){
 const k=[0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2];
 const h=[0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19],pad=new Uint8Array(Math.ceil((bytes.length+9)/64)*64);pad.set(bytes);pad[bytes.length]=128;
 const dv=new DataView(pad.buffer);dv.setUint32(pad.length-8,Math.floor(bytes.length/0x20000000));dv.setUint32(pad.length-4,(bytes.length*8)>>>0);
 const rr=(x,n)=>(x>>>n)|(x<<(32-n)),w=new Uint32Array(64);
 for(let o=0;o<pad.length;o+=64){
  for(let i=0;i<16;i++)w[i]=dv.getUint32(o+i*4);
  for(let i=16;i<64;i++){const a=w[i-15],b=w[i-2];w[i]=(w[i-16]+(rr(a,7)^rr(a,18)^(a>>>3))+w[i-7]+(rr(b,17)^rr(b,19)^(b>>>10)))>>>0;}
  let[a,b,c,d,e,f,g,j]=h;
  for(let i=0;i<64;i++){const t1=(j+(rr(e,6)^rr(e,11)^rr(e,25))+((e&f)^(~e&g))+k[i]+w[i])>>>0,t2=((rr(a,2)^rr(a,13)^rr(a,22))+((a&b)^(a&c)^(b&c)))>>>0;j=g;g=f;f=e;e=(d+t1)>>>0;d=c;c=b;b=a;a=(t1+t2)>>>0;}
  [a,b,c,d,e,f,g,j].forEach((v,i)=>h[i]=(h[i]+v)>>>0);
 }
 return h.map(n=>n.toString(16).padStart(8,'0')).join('');
}
export function createPartInspector({context,render,appearance,restoreAssembly}){
 const panel=$('part-popup'),menu=$('parts-menu'),ray=new THREE.Raycaster(),ndc=new THREE.Vector2();
 let selected=null,helper=null,overrides=new Map(),records=new Map(),ready=Promise.resolve(),generation=0,timer=0,pointer=null,pointers=new Set();
 const draftKey=(model,part)=>'intel3d-note-draft:'+JSON.stringify([model,part]);
 const storageKey=()=> 'intel3d-part-visibility:'+context().entry.id;
 function path(mesh){const names=[];let node=mesh;while(node&&node!==context().model){const i=node.parent?.children.indexOf(node)??0;names.unshift((node.name||node.type)+'['+i+']');node=node.parent;}return names.join('/');}
 function id(mesh){return mesh.userData.partNoteId;}
 function updateExport(){
  const mesh=selected?.mesh,button=$('export-selected-stl');
  button.disabled=!mesh||!!mesh.userData.cadReference;
  button.title=mesh?.userData.cadReference?'Reference envelope: not a printable part':mesh?'Export '+(mesh.name||'selected mesh')+' as STL':'Select a part first';
  $('export-part-stl').disabled=button.disabled;
 }
 async function exportMesh(mesh){
  const c=context(),message=$('stl-export-status');
  if(!mesh||!c.meshes.includes(mesh)||mesh.userData.cadReference)return;
  const name=(mesh.name||'part').replace(/[^a-zA-Z0-9._-]/g,'_');
  let geometry,url;
  try{
   if(c.entry.printStl){
    const a=document.createElement('a');a.href=c.entry.printStl;a.download=c.entry.printStl.split('/').pop();a.click();
    message.textContent='Original oriented print STL: '+name;return;
   }
   if(c.entry.cad){
    if(!mesh.userData.cadPart||!c.entry.stlDirectory)throw Error('Print STL unavailable for this part.');
    const a=document.createElement('a');a.href=c.entry.stlDirectory+encodeURIComponent(mesh.name)+'.stl';a.download=name+'.stl';a.click();
    message.textContent='Original print STL: '+name;return;
   }
   // Remove viewer centering/front rotation, retain authored node transforms.
   c.model.updateMatrixWorld(true);
   const transform=new THREE.Matrix4().copy(c.model.matrixWorld).invert().multiply(mesh.matrixWorld);
   geometry=mesh.geometry.clone().applyMatrix4(transform);
   geometry.rotateX(Math.PI/2);geometry.scale(1000,1000,1000);geometry.computeBoundingBox();
   const box=geometry.boundingBox;if(box.isEmpty())throw Error('No geometry to export.');
   const center=box.getCenter(new THREE.Vector3());geometry.translate(-center.x,-center.y,-box.min.z);
   const output=new STLExporter().parse(new THREE.Mesh(geometry),{binary:true});
   url=URL.createObjectURL(new Blob([output],{type:'model/stl'}));
   const a=document.createElement('a');a.href=url;a.download=c.entry.id+'-'+name+'.stl';a.click();
   message.textContent='Exported '+name+' · mm';
  }catch(error){message.textContent='STL export failed: '+error.message;}
  finally{geometry?.dispose();if(url)setTimeout(()=>URL.revokeObjectURL(url),1000);}
 }
 $('export-selected-stl').onclick=$('export-part-stl').onclick=()=>exportMesh(selected?.mesh);
 function looks(){appearance();render();}
 function remember(){safeStore.set(storageKey(),JSON.stringify([...overrides]));}
 function applyVisibility(){for(const mesh of context().meshes)mesh.visible=mesh.userData.baseVisible!==false&&overrides.get(id(mesh))!==0;updateCount();if(helper&&selected?.mesh.visible)helper.update();if(helper)helper.visible=!!selected?.mesh.visible;}
 function applyAppearance(mesh){
  const alpha=overrides.get(id(mesh));
  for(const material of Array.isArray(mesh.material)?mesh.material:[mesh.material]){
   if(!material.userData.partBaseline)material.userData.partBaseline={opacity:material.opacity,transparent:material.transparent,depthWrite:material.depthWrite};
   const base=material.userData.partBaseline;material.opacity=alpha===undefined?base.opacity:alpha===0?base.opacity:alpha;material.transparent=alpha===undefined?base.transparent:alpha===.5;material.depthWrite=alpha===undefined?base.depthWrite:alpha!==.5;material.needsUpdate=true;
  }
 }
 function updateCount(){const n=context().meshes.filter(m=>overrides.get(id(m))===0).length;$('hidden-parts').textContent='Unhide Objects ('+n+')';}
 function close(){panel.hidden=true;menu.hidden=true;if(helper){context().scene.remove(helper);helper.dispose();helper=null;}render();}
 function position(element,x,y){element.hidden=false;element.style.left=Math.max(8,Math.min(x+12,innerWidth-element.offsetWidth-8))+'px';element.style.top=Math.max(8,Math.min(y+12,innerHeight-element.offsetHeight-8))+'px';}
 function pick(e){const c=context(),r=c.renderer.domElement.getBoundingClientRect();ndc.set((e.clientX-r.left)/r.width*2-1,-(e.clientY-r.top)/r.height*2+1);c.model?.updateMatrixWorld(true);ray.setFromCamera(ndc,c.camera);return ray.intersectObjects(c.meshes.filter(m=>m.visible),false)[0]||null;}
 function snapshot(){const c=context();return {cameraPositionM:c.camera.position.toArray(),cameraTargetM:c.controls.target.toArray(),modelMatrixWorld:c.model.matrixWorld.toArray(),exploded:c.entry.cad?Number($('explode').value):0,partOpacities:[...overrides],cadFilters:c.entry.cad?Object.fromEntries(['monitor','pc','cover','panels'].map(n=>[n,$('cad-'+n).checked])):null};}
 function metadata(mesh,anchor){
  const c=context(),geometry=mesh.geometry,pos=geometry.getAttribute('position'),index=geometry.index;
  const a=new Uint8Array(pos.array.buffer,pos.array.byteOffset,pos.array.byteLength),b=index?new Uint8Array(index.array.buffer,index.array.byteOffset,index.array.byteLength):new Uint8Array();const bytes=new Uint8Array(a.length+b.length);bytes.set(a);bytes.set(b,a.length);
  geometry.computeBoundingBox();const box=geometry.boundingBox,mm=v=>v.toArray().map(n=>Number((n*1000).toFixed(5)));
  const part={id:id(mesh),name:mesh.name||'Mesh',cadName:mesh.userData.cadPart?mesh.name:null,nodePath:path(mesh),meshIndex:c.meshes.indexOf(mesh),geometryFingerprint:sha256(bytes),triangleCount:(index?.count||pos.count)/3,boundsLocalMm:{min:mm(box.min),max:mm(box.max)},coordinateSystem:'Geometry-local millimeters in viewer Y-up axes; model matrix and click anchor supplied'};
  if(c.entry.cad)part.sourceCadBoundsMm={min:[box.min.x*1000,-box.max.z*1000,box.min.y*1000],max:[box.max.x*1000,-box.min.z*1000,box.max.y*1000]};
  return {model:{id:c.entry.id,name:c.entry.name,assetPath:c.entry.local?null:'/models/'+c.entry.id+'/'+c.entry.file,localFile:!!c.entry.local,localFilename:c.entry.local?c.entry.name:null},part,anchor,view:snapshot()};
 }
 function status(record,message){if(selected?.record===record)$('note-status').textContent=message;}
 const pendingText=note=>note?.reviewed?'':note?.text||'';
 function showHistory(record){
  if(selected?.record!==record)return;
  const note=record.saved,history=[...(note?.history||[])];if(note?.reviewed)history.push(note);
  const rows=$('review-rows');rows.replaceChildren();
  for(const entry of history.reverse()){
   const row=document.createElement('tr');
   for(const value of [entry.text,entry.reviewResponse||'—',entry.reviewedAt?new Date(entry.reviewedAt).toLocaleString():'Reviewed']){const cell=document.createElement('td');cell.textContent=value;row.append(cell);}
   rows.append(row);
  }
  $('review-empty').hidden=history.length>0;$('review-table').hidden=!history.length;
 }
 async function refreshSelected(){
  const record=selected?.record,version=generation;if(!record||record.dirty||record.conflict)return;
  try{
   const response=await fetch(API+'?model='+encodeURIComponent(record.payload.model.id));if(!response.ok)return;
   const data=await response.json();if(version!==generation||selected?.record!==record||record.dirty||record.conflict)return;
   const note=data.notes.find(n=>n.part.id===record.payload.part.id);
   // An older GET must never roll back a just-completed save.
   if(!note||note.revision<record.revision)return;
   record.saved=note;record.revision=note.revision;record.text=pendingText(note);$('part-note').value=record.text;showHistory(record);
   status(record,note.reviewed?'Reviewed · add a new note above.':'Not reviewed · saved on Mini');
  }catch{/* Keep local edits and the last loaded history available offline. */}
 }
 setInterval(()=>{if(!document.hidden&&!panel.hidden)refreshSelected();},5000);
 window.addEventListener('focus',()=>{if(!panel.hidden)refreshSelected();});
 async function persist(record){
  await ready;if(!record.dirty)return;
  const text=record.text,version=record.revision;
  status(record,'Saving…');
  try{
   const r=await fetch(API,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({...record.payload,text,expectedRevision:version})});const body=await r.json();
   if(!r.ok){if(r.status===409){record.conflict=true;if(selected?.record===record)$('reload-note').hidden=false;}throw new Error(body.error||'Save failed');}
   record.revision=body.note.revision;record.saved=body.note;showHistory(record);if(record.text===text){record.dirty=false;safeStore.remove(draftKey(record.payload.model.id,record.payload.part.id));status(record,'Saved on Mini · '+new Date(body.note.updatedAt).toLocaleTimeString());}
  }catch(error){status(record,error.message+' — browser draft retained.');throw error;}
 }
 function queue(record){if(!record||record.conflict)return Promise.resolve();record.queue=(record.queue||Promise.resolve()).catch(()=>{}).then(()=>persist(record));return record.queue;}
 function flush(){clearTimeout(timer);if(selected?.record?.dirty){selected.record.payload.view=snapshot();return queue(selected.record).catch(()=>{});}return Promise.resolve();}
 function setModel(){
  generation++;close();selected=null;updateExport();$('stl-export-status').textContent='';records=new Map();const c=context(),version=generation;
  try{overrides=new Map(JSON.parse(safeStore.get(storageKey())||'[]').filter(([k,v])=>typeof k==='string'&&[0,.5,1].includes(v)));}catch{overrides=new Map();}
  for(const mesh of c.meshes){mesh.userData.partNoteId=c.entry.local?'local:'+sha256(new Uint8Array(mesh.geometry.attributes.position.array.buffer)):(mesh.userData.cadPart?'cad:'+mesh.name:'mesh:'+path(mesh));if(mesh.userData.baseVisible===undefined)mesh.userData.baseVisible=mesh.visible;}
  ready=fetch(API+'?model='+encodeURIComponent(c.entry.id)).then(r=>{if(!r.ok)throw Error('Notes service unavailable');return r.json();}).then(data=>{if(version!==generation)return;for(const note of data.notes||[]){const record=records.get(note.part.id);if(record){record.saved=note;record.revision=note.revision;}else records.set(note.part.id,{saved:note,revision:note.revision,text:pendingText(note),dirty:false});}}).catch(error=>{if(version===generation&&selected)$('note-status').textContent=error.message+'; drafts stay in this browser.';});
  applyVisibility();looks();
 }
 async function select(hit,e,openPanel=true){
  flush();close();const c=context(),mesh=hit.object,key=id(mesh),version=generation;
  const local=mesh.worldToLocal(hit.point.clone()),anchor={pointInPartM:local.toArray(),pointInViewerWorldM:hit.point.toArray(),faceIndex:hit.faceIndex};
  if(c.entry.cad)anchor.sourceCadPointMm=[local.x*1000,-local.z*1000,local.y*1000];
  let record=records.get(key);if(!record){record={revision:0,text:'',dirty:false};records.set(key,record);}
  record.payload=metadata(mesh,anchor);
  const draft=safeStore.get(draftKey(c.entry.id,key));if(draft!==null){record.text=draft;record.dirty=true;}
  selected={mesh,record};updateExport();$('stl-export-status').textContent='';panel.dataset.partId=key;$('part-title').textContent=(mesh.name||'Mesh').replaceAll('_',' ');$('part-model').textContent=c.entry.name;$('part-note').value=record.text;$('reload-note').hidden=true;
  $('part-opacity').value=String(overrides.get(key)??1);$('note-status').textContent='Loading saved note…';
  helper=new THREE.BoxHelper(mesh,0x72e3d0);helper.raycast=()=>{};c.scene.add(helper);if(openPanel)position(panel,e.clientX,e.clientY);render();
  await ready;if(version!==generation||selected?.record!==record)return;
  if(!record.dirty){record.text=pendingText(record.saved);$('part-note').value=record.text;}
  const changed=record.saved&&record.saved.part.geometryFingerprint!==record.payload.part.geometryFingerprint;
  status(record,changed?'Geometry changed since this note; review its location.':record.dirty?'Browser draft recovered — press Save.':record.saved?.reviewed?'Reviewed · add a new note above.':record.saved?'Not reviewed · saved on Mini':'Add a note; it saves automatically.');
  showHistory(record);await refreshSelected();
 }
 function menuAt(x,y){
  const hidden=context().meshes.filter(m=>overrides.get(id(m))===0),list=$('restore-list');list.replaceChildren();
  $('restore-empty').hidden=hidden.length>0;$('restore-all').disabled=!hidden.length;
  for(const mesh of hidden){const button=document.createElement('button');button.type='button';button.textContent='Show '+(mesh.name||'Mesh').replaceAll('_',' ');button.onclick=()=>{overrides.delete(id(mesh));remember();restoreAssembly(mesh);applyVisibility();looks();menuAt(x,y);};list.append(button);}
  position(menu,x,y);
 }
 $('center-object').onclick=()=>{
  if(!selected?.mesh.visible)return;
  const c=context();c.model.updateMatrixWorld(true);
  const bounds=new THREE.Box3().setFromObject(selected.mesh);
  if(bounds.isEmpty())return;
  const target=bounds.getCenter(new THREE.Vector3());
  // Move camera and pivot together, preserving the current angle and zoom.
  const offset=c.camera.position.clone().sub(c.controls.target);
  const damping=c.controls.enableDamping,rotating=c.controls.autoRotate;
  c.controls.enableDamping=false;c.controls.autoRotate=false;c.controls.update();
  c.controls.target.copy(target);c.camera.position.copy(target).add(offset);
  c.controls.update();c.controls.enableDamping=damping;c.controls.autoRotate=rotating;
  flush();close();render();
 };
 $('part-close').onclick=()=>{flush();close();};$('menu-close').onclick=()=>menu.hidden=true;
 $('part-note').oninput=()=>{if(!selected)return;const r=selected.record;r.text=$('part-note').value;r.dirty=true;safeStore.set(draftKey(r.payload.model.id,r.payload.part.id),r.text);status(r,'Unsaved browser draft…');clearTimeout(timer);timer=setTimeout(()=>{r.payload.view=snapshot();queue(r).catch(()=>{});},700);};
 $('save-note').onclick=()=>{clearTimeout(timer);if(selected){selected.record.payload.view=snapshot();queue(selected.record).catch(()=>{});}};
 $('reload-note').onclick=async()=>{const r=selected?.record;if(!r)return;try{const data=await fetch(API+'?model='+encodeURIComponent(r.payload.model.id)).then(x=>x.json());const n=data.notes.find(n=>n.part.id===r.payload.part.id);r.saved=n;r.revision=n?.revision||0;r.text=pendingText(n);r.dirty=false;r.conflict=false;safeStore.remove(draftKey(r.payload.model.id,r.payload.part.id));$('part-note').value=r.text;$('reload-note').hidden=true;showHistory(r);status(r,'Loaded saved note.');}catch{status(r,'Could not reload note; browser draft retained.');}};
 $('part-opacity').onchange=()=>{if(!selected)return;const mesh=selected.mesh;overrides.set(id(mesh),Number($('part-opacity').value));remember();applyVisibility();looks();};
 $('restore-all').onclick=()=>{for(const mesh of context().meshes)if(overrides.get(id(mesh))===0)overrides.delete(id(mesh));remember();restoreAssembly();applyVisibility();looks();menu.hidden=true;};
 $('hidden-parts').onclick=e=>menuAt(e.clientX||e.target.getBoundingClientRect().left,e.clientY||e.target.getBoundingClientRect().bottom);
 $('export-notes').onclick=async()=>{await flush();try{const response=await fetch(API+'/export');if(!response.ok)throw Error('Export unavailable');const data=await response.json(),url=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='intel3d-part-notes.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}catch{if(selected)status(selected.record,'Could not export; browser drafts are retained.');}};
 const canvas=context().renderer.domElement;
 canvas.addEventListener('pointerdown',e=>{pointers.add(e.pointerId);if(pointers.size===1)pointer={x:e.clientX,y:e.clientY,id:e.pointerId,button:e.button,moved:false};else if(pointer)pointer.moved=true;menu.hidden=true;});
 canvas.addEventListener('pointermove',e=>{if(pointer&&Math.hypot(e.clientX-pointer.x,e.clientY-pointer.y)>6){pointer.moved=true;if(pointer.button===2)panel.hidden=true;}});
 canvas.addEventListener('pointerup',e=>{pointers.delete(e.pointerId);if(pointer?.id===e.pointerId&&!pointer.moved&&pointer.button===0){const hit=pick(e);if(hit)select(hit,e,e.pointerType==='touch');else{flush();close();selected=null;updateExport();}}if(!pointers.size)pointer=null;});
 canvas.addEventListener('pointercancel',e=>{pointers.delete(e.pointerId);pointer=null;});
 canvas.addEventListener('contextmenu',e=>{e.preventDefault();menu.hidden=true;const hit=pick(e);if(hit&&hit.object===selected?.mesh&&!pointer?.moved)select(hit,e);});
 document.addEventListener('keydown',e=>{if(e.key==='Escape'){flush();close();}});
 document.addEventListener('pointerdown',e=>{if(!menu.hidden&&!menu.contains(e.target)&&e.target!==$('hidden-parts')&&e.target!==canvas)menu.hidden=true;});
 return {setModel,exportMesh,beforeModelChange:flush,applyVisibility,applyAppearance,getOpacity:mesh=>overrides.get(id(mesh)),close};
}
