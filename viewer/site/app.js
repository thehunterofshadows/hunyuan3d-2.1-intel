import * as THREE from 'three';
import { createPartInspector } from './part-inspector.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { STLLoader } from 'three/addons/loaders/STLLoader.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

const $=id=>document.getElementById(id);
const models=[
 {id:'portable-pinball',name:'Portable Pinball · CAD V1.1',type:'Printable cabinet assembly',file:'cabinet-v1_1.glb',cad:true,front:0,reference:'/models/portable-pinball/preview-v1_1.png',thumbnail:'/models/portable-pinball/preview-v1_1.png',note:'V1.1: all four monitor supports have 6 mm locator lips, reinforced roots and 4 mm thicker shelves underneath. Monitor contact heights and clearances are unchanged. Support STLs print on their end faces. Actual cabinet CAD: 47 printed parts, a monitor envelope, Dell 3050 allowance and folded-cover reserve. HDMI/USB-C front-left; monitor controls rear-left. Front game buttons are shifted right for cable clearance. Physical fit tests are pending. Use the assembly controls to look inside; download STEP/STLs to edit or print.'},
 {id:'trellis-pinball-flipper',name:'Flipper bat · TRELLIS.2',type:'Pinball component · Arc B70 Vulkan',file:'flipper.glb',front:0,reference:'/models/trellis-pinball-flipper/reference.png',thumbnail:'/models/trellis-pinball-flipper/preview.png',textureLabel:'2048px textures',note:'Actual TRELLIS.2 mesh reconstructed from an original illustrated classic white bat with red rebound rubber reference. 512-resolution exploratory output. Geometry and surfaces may differ from the input; not optimized or mechanically functional.'},
 {id:'trellis-pinball-plunger',name:'Ball launcher / plunger · TRELLIS.2',type:'Pinball component · Arc B70 Vulkan',file:'plunger.glb',front:0,reference:'/models/trellis-pinball-plunger/reference.png',thumbnail:'/models/trellis-pinball-plunger/preview.png',textureLabel:'2048px textures',note:'Actual TRELLIS.2 mesh reconstructed from an original illustrated steel spring-loaded launcher with red pull knob reference. 512-resolution exploratory output. Geometry and surfaces may differ from the input; not optimized or mechanically functional.'},
 {id:'trellis-pinball-slingshot',name:'Slingshot bumper · TRELLIS.2',type:'Pinball component · Arc B70 Vulkan',file:'slingshot.glb',front:0,reference:'/models/trellis-pinball-slingshot/reference.png',thumbnail:'/models/trellis-pinball-slingshot/preview.png',textureLabel:'2048px textures',note:'Actual TRELLIS.2 mesh reconstructed from an original illustrated triangular rebound bumper and metal guide posts reference. 512-resolution exploratory output. Geometry and surfaces may differ from the input; not optimized or mechanically functional.'},
 {id:'trellis-pinball-target',name:'Drop target · TRELLIS.2',type:'Pinball component · Arc B70 Vulkan',file:'target.glb',front:0,reference:'/models/trellis-pinball-target/reference.png',thumbnail:'/models/trellis-pinball-target/preview.png',textureLabel:'2048px textures',note:'Actual TRELLIS.2 mesh reconstructed from an original illustrated yellow stand-up drop target with hinge reference. 512-resolution exploratory output. Geometry and surfaces may differ from the input; not optimized or mechanically functional.'},
 {id:'trellis-pinball-pop-bumper',name:'Pop bumper · TRELLIS.2',type:'Pinball component · Arc B70 Vulkan',file:'pop-bumper.glb',front:0,reference:'/models/trellis-pinball-pop-bumper/reference.png',thumbnail:'/models/trellis-pinball-pop-bumper/preview.png',textureLabel:'2048px textures',note:'Actual TRELLIS.2 mesh reconstructed from an original illustrated red-cap pop bumper for the pinball playfield reference. 512-resolution exploratory output. Geometry and surfaces may differ from the input; not optimized or mechanically functional.'},
 {id:'trellis-woman',name:'Woman · TRELLIS.2',type:'B70 Vulkan · 1024 generation',file:'woman.glb',note:'Actual TRELLIS.2 reconstruction of the armored woman reference. Static, unrigged evaluation mesh with generated PBR textures; not yet optimized or animated for Instagib.',front:0,reference:'/models/woman/reference.png',thumbnail:'/models/trellis-woman/preview.png',textureLabel:'2048px textures'},
 {id:'trellis-bumper',name:'Bumper · TRELLIS.2',type:'B70 Vulkan · 1024 generation',file:'bumper.glb',note:'Actual TRELLIS.2 output from the original red-cap bumper reference. Chrome polish is enabled in this viewer: reflective silver, glossy red and matte rubber. Toggle it off to compare the generated materials. Download contains the original GLB. Static evaluation mesh; not yet optimized for pinball.',front:Math.PI,reference:'/models/bumper/reference.png',thumbnail:'/models/trellis-bumper/preview.png',textureLabel:'2048px textures'},
 {id:'trellis-railgun',name:'Railgun · TRELLIS.2',type:'B70 Vulkan · 1024 generation',file:'railgun.glb',note:'Actual TRELLIS.2 output from the original reference, generated on one B70 in 221 seconds. More detail than the 512 test, but surfaces remain imperfect and the cyan glow was not reproduced. Unoptimized evaluation mesh.',front:Math.PI,reference:'/models/railgun/reference.png',thumbnail:'/models/trellis-railgun/preview.png',textureLabel:'2048px textures'},
 {id:'railgun-built',name:'Railgun · rebuilt',type:'Clean hard-surface model',file:'railgun.glb',note:'Modeled mechanical parts, beveled edges, clean metal and rubber materials, and emissive cyan inserts. Static weapon with named attachment points; not yet integrated into Instagib.',front:0,reference:'/models/railgun/reference.png'},
 {id:'railgun',name:'Railgun · AI draft',type:'Weapon',file:'railgun.glb',note:'Long accelerator rails and cyan accents. First-pass geometry with visible texture artifacts.',front:Math.PI},
 {id:'bumper',name:'Pinball bumper',type:'Table component',file:'bumper.glb',note:'Red cap, impact ring and metal pedestal. Generated textures still need cleanup.',front:Math.PI},
 {id:'woman',name:'Woman character',type:'Character study',file:'woman.glb',note:'Static, unrigged character. Face, hands and clothing show significant reconstruction artifacts.',front:Math.PI}
];
document.querySelector('.eyebrow').textContent='COLLECTION / '+String(models.length).padStart(2,'0');
let scene,camera,renderer,controls,model,grid,envRT,key,fill,hemi,inspector;
let ticket=0,active,meshes=[],fitDistance=4,radius=1,frame=0;
const viewport=$('viewport'), status=$('status');
const clay=new THREE.MeshStandardMaterial({color:0xbcc4cc,roughness:0.75,metalness:0});
const normals=new THREE.MeshNormalMaterial();
function dispose(root){
 const geometries=new Set(),materials=new Set(),textures=new Set();
 root.traverse(o=>{if(!o.isMesh)return;geometries.add(o.geometry);if(o.userData.clayMaterial)materials.add(o.userData.clayMaterial);if(o.userData.normalMaterial)materials.add(o.userData.normalMaterial);const orig=o.userData.originalMaterial||o.material;for(const m of (Array.isArray(orig)?orig:[orig])){materials.add(m);for(const v of Object.values(m))if(v?.isTexture)textures.add(v);}});
 for(const t of textures){t.dispose();t.source?.data?.close?.();}
 for(const m of materials)m.dispose();for(const g of geometries)g.dispose();
}
function requestRender(){if(!frame&&!document.hidden)frame=requestAnimationFrame(draw);}
function draw(){frame=0;controls.update();renderer.render(scene,camera);if(controls.autoRotate)requestRender();}
function resize(){
 if(!renderer)return;
 const w=viewport.clientWidth,h=viewport.clientHeight;
 camera.aspect=w/h;camera.updateProjectionMatrix();renderer.setSize(w,h,false);requestRender();
}
function fit(view='home'){
 if(!model)return;
 const vfov=THREE.MathUtils.degToRad(camera.fov);
 const hfov=2*Math.atan(Math.tan(vfov/2)*camera.aspect);
 fitDistance=radius/Math.sin(Math.min(vfov,hfov)/2)*1.12;
 const target=new THREE.Vector3();
 if(active?.cad){const b=visibleBounds();if(!b.isEmpty()){b.getCenter(target);radius=b.getBoundingSphere(new THREE.Sphere()).radius;}fitDistance=radius/Math.sin(Math.min(vfov,hfov)/2)*1.12;}
 const directions={home:active?.cad?[-0.7,0.6,1]:[0.6,0.3,1],front:[0,0,1],back:[0,0,-1],left:[-1,0,0],right:[1,0,0],top:[0,1,0.001]};
 const direction=new THREE.Vector3(...directions[view]).normalize();
 if(active?.id==='railgun-built'||active?.id==='trellis-railgun'||active?.cad){
  const bounds=active?.cad?visibleBounds():new THREE.Box3().setFromObject(model);
  const right=new THREE.Vector3().crossVectors(new THREE.Vector3(0,1,0),direction).normalize();
  const up=new THREE.Vector3().crossVectors(direction,right).normalize();
  fitDistance=0;
  for(const x of [bounds.min.x,bounds.max.x])for(const y of [bounds.min.y,bounds.max.y])for(const z of [bounds.min.z,bounds.max.z]){
   const p=new THREE.Vector3(x,y,z).sub(target);
   fitDistance=Math.max(fitDistance,p.dot(direction)+Math.max(Math.abs(p.dot(right))/Math.tan(hfov/2),Math.abs(p.dot(up))/Math.tan(vfov/2)));
  }
  fitDistance*=1.18;
 }
 controls.target.copy(target);camera.position.copy(direction.multiplyScalar(fitDistance).add(target));
 camera.near=radius/1000;camera.far=radius*100;camera.updateProjectionMatrix();
 controls.minDistance=radius*0.04;controls.maxDistance=radius*20;controls.update();requestRender();
}
// Viewer-only material polish: infer silver/red/rubber from the generated base color.
// Keep the source GLB untouched; expose the original for comparison and download.
const chromeEnabled={value:1};
function polishBumper(material){
 material.onBeforeCompile=shader=>{
  shader.uniforms.bumperChrome=chromeEnabled;
  shader.fragmentShader='uniform float bumperChrome;\n'+shader.fragmentShader;
  shader.fragmentShader=shader.fragmentShader.replace('#include <metalnessmap_fragment>', `
   #include <metalnessmap_fragment>
   if(bumperChrome > 0.5){
    float hi=max(diffuseColor.r,max(diffuseColor.g,diffuseColor.b));
    float lo=min(diffuseColor.r,min(diffuseColor.g,diffuseColor.b));
    float saturation=(hi-lo)/max(hi,0.001);
    float silver=(1.0-smoothstep(0.18,0.42,saturation))*smoothstep(0.055,0.20,hi);
    float red=smoothstep(1.3,2.2,diffuseColor.r/max(max(diffuseColor.g,diffuseColor.b),0.001));
    roughnessFactor=mix(0.72,0.24,red);
    roughnessFactor=mix(roughnessFactor,0.13,silver);
    metalnessFactor=silver;
    diffuseColor.rgb=mix(diffuseColor.rgb,vec3(0.72,0.75,0.78),silver*0.85);
   }
  `);
 };
 material.customProgramCacheKey=()=> 'bumper-chrome-v1';
 material.needsUpdate=true;
}
// Viewer-only correction of TRELLIS's heavily darkened target panel.
// The original exported GLB stays unchanged and downloadable.
function polishTarget(material){
 material.onBeforeCompile=shader=>{
  shader.uniforms.targetColor=chromeEnabled;
  shader.fragmentShader='uniform float targetColor;\n'+shader.fragmentShader;
  shader.fragmentShader=shader.fragmentShader.replace('#include <map_fragment>',`
    #include <map_fragment>
    if(targetColor > 0.5){
      float cmax=max(diffuseColor.r,max(diffuseColor.g,diffuseColor.b));
      float redProtect=smoothstep(0.02,0.09,diffuseColor.r-max(diffuseColor.g,diffuseColor.b));
      float blueProtect=smoothstep(0.01,0.06,diffuseColor.b-max(diffuseColor.r,diffuseColor.g));
      float dark=1.0-smoothstep(0.12,0.27,cmax);
      float panel=dark*(1.0-redProtect)*(1.0-blueProtect);
      diffuseColor.rgb=mix(diffuseColor.rgb,vec3(0.92,0.64,0.09),panel*0.92);
    }
  `);
 };
 material.customProgramCacheKey=()=> 'target-color-v1';
 material.needsUpdate=true;
}
function surface(){
 const mode=$('surface').value,wire=$('wireframe').checked;
 for(const mesh of meshes){
  mesh.material=mode==='clay'?mesh.userData.clayMaterial:mode==='normals'?mesh.userData.normalMaterial:mesh.userData.originalMaterial;
  for(const m of (Array.isArray(mesh.material)?mesh.material:[mesh.material]))m.wireframe=wire;
  inspector?.applyAppearance(mesh);
 }
 requestRender();
}
function lights(){
 const preset=$('lighting').value;
 scene.environment=preset==='dramatic'?null:envRT.texture;
 key.intensity=preset==='dramatic'?4:preset==='soft'?1:2;
 fill.intensity=preset==='dramatic'?0.2:1.2;
 hemi.intensity=preset==='dramatic'?0.3:1;
 scene.environmentIntensity=preset==='soft'?1.5:1;
 requestRender();
}
async function load(entry){
 const current=++ticket;
 status.hidden=false;status.textContent='Loading '+entry.name+'…';
 viewport.dataset.state='loading';
 try {
  let gltf;
  if(entry.format==='stl'){
   const geometry=await new STLLoader().loadAsync(entry.url);
   const pos=geometry.getAttribute('position');
   if(!pos||!pos.count||!Array.from(pos.array).every(Number.isFinite)){geometry.dispose();throw new Error('STL contains no valid geometry');}
   geometry.rotateX(-Math.PI/2);geometry.scale(.001,.001,.001);geometry.computeVertexNormals();
   const root=new THREE.Group();root.add(new THREE.Mesh(geometry,new THREE.MeshStandardMaterial({color:0x8bb8c9,roughness:.72,metalness:0})));
   gltf={scene:root};
  }else gltf=await new GLTFLoader().loadAsync('/models/'+entry.id+'/'+entry.file+'?v=build1');
  if(current!==ticket){dispose(gltf.scene);if(entry.local)URL.revokeObjectURL(entry.url);return;}
  inspector?.beforeModelChange();
  if(model){scene.remove(model);dispose(model);if(active?.local)URL.revokeObjectURL(active.url);}
  model=gltf.scene;active=entry;meshes=[];
  model.rotation.y=entry.front;
  model.updateMatrixWorld(true);
  const box=new THREE.Box3().setFromObject(model),center=box.getCenter(new THREE.Vector3());
  model.position.sub(center);model.updateMatrixWorld(true);
  radius=box.getBoundingSphere(new THREE.Sphere()).radius;
  let triangles=0;
  model.traverse(o=>{if(o.isMesh){o.material=Array.isArray(o.material)?o.material.map(m=>m.clone()):o.material.clone();o.userData.clayMaterial=clay.clone();o.userData.normalMaterial=normals.clone();o.userData.baseVisible=o.visible;if(entry.id==='trellis-pinball-target')for(const m of (Array.isArray(o.material)?o.material:[o.material]))polishTarget(m);if(['trellis-bumper','trellis-pinball-pop-bumper'].includes(entry.id))for(const m of (Array.isArray(o.material)?o.material:[o.material]))polishBumper(m);o.userData.originalMaterial=o.material;meshes.push(o);triangles+=(o.geometry.index?.count||o.geometry.attributes.position.count)/3;}});
  scene.add(model);configureAssembly();inspector?.setModel();
  if(grid){scene.remove(grid);grid.geometry.dispose();for(const m of (Array.isArray(grid.material)?grid.material:[grid.material]))m.dispose();}
  grid=new THREE.GridHelper(radius*5,20,0x425464,0x293947);grid.position.y=box.min.y-center.y-0.015*radius;grid.visible=$('grid').checked;scene.add(grid);
  $('chrome-control').hidden=!['trellis-bumper','trellis-pinball-pop-bumper','trellis-pinball-target'].includes(entry.id);$('polish-label').textContent=entry.id==='trellis-pinball-target'?'Target color correction':'Chrome polish';
  $('download').textContent=entry.format==='stl'?'Download STL ↓':['trellis-bumper','trellis-pinball-pop-bumper'].includes(entry.id)?'Download original GLB ↓':'Download GLB ↓';
  $('title').textContent=entry.name;$('description').textContent=entry.note;
  $('stats').textContent=triangles.toLocaleString()+' triangles · '+(entry.cad?'47 printed parts · 3 reference envelopes':entry.format==='stl'?'STL geometry · '+[box.max.x-box.min.x,box.max.y-box.min.y,box.max.z-box.min.z].map(v=>(v*1000).toFixed(1)).join(' × ')+' mm':(entry.textureLabel||(entry.id==='railgun-built'?'procedural materials':'1024px textures')));
  $('download').href=entry.local?entry.url:'/models/'+entry.id+'/'+entry.file+'?v=build1';
  $('download').download=entry.local?entry.name:entry.file;
  $('cad-downloads').hidden=!entry.cad;
  $('reference').hidden=!!entry.local;
  $('reference').querySelector('summary').textContent=entry.cad?'Actual CAD preview ↗':'Original reference image ↗';
  $('reference').querySelector('.caption').textContent=entry.cad?'Rendered from the CAD assembly. Physical fit tests are pending.':entry.id.startsWith('trellis-pinball-')?'Illustrated source reference, not the reconstructed model.':'AI-generated input, not the reconstructed mesh.';
  if(!entry.local)$('reference-image').src=entry.reference||'/models/'+entry.id+'/reference.png';
  document.querySelector('.pill').textContent=entry.cad?'CAD PROTOTYPE':entry.local?'LOCAL STL':entry.id.startsWith('trellis-')?'TRELLIS.2 OUTPUT':entry.id==='railgun-built'?'MODELED REBUILD':'FIRST-PASS ASSET';
  $('reference-link').href=$('reference-image').src;
  for(const button of document.querySelectorAll('.model'))button.setAttribute('aria-pressed',String(button.dataset.model===entry.id));
  if(!entry.local)history.replaceState(null,'','#'+entry.id);
  surface();fit();status.hidden=true;viewport.dataset.state='ready';viewport.dataset.model=entry.id;
 }catch(error){
  if(current!==ticket)return;
  console.error(error);if(entry.local)URL.revokeObjectURL(entry.url);status.textContent=entry.local?'Could not read this STL. Choose a valid ASCII or binary STL file.':'Could not load this model. Check your connection and select it again to retry.';
  viewport.dataset.state='error';
 }
}
function visibleBounds(){
 const bounds=new THREE.Box3();model.updateMatrixWorld(true);
 for(const mesh of meshes){if(!mesh.visible)continue;mesh.geometry.computeBoundingBox();bounds.union(mesh.geometry.boundingBox.clone().applyMatrix4(mesh.matrixWorld));}
 return bounds.isEmpty()?new THREE.Box3().setFromObject(model):bounds;
}
function configureAssembly(){
 $('cad-controls').hidden=!active?.cad;
 if(!active?.cad)return;
 $('explode').value='0';$('cad-monitor').checked=true;$('cad-pc').checked=true;$('cad-cover').checked=false;$('cad-panels').checked=true;
 const select=$('cad-part');select.replaceChildren(new Option('All printed parts','all'));
 for(const mesh of meshes){
  mesh.userData.assembledPosition=mesh.position.clone();
  if(mesh.userData.cadPart)select.add(new Option(mesh.name.replaceAll('_',' '),mesh.name));
 }
 applyAssembly();
}
function applyAssembly(){
 if(!active?.cad)return;
 const amount=Number($('explode').value),selected=$('cad-part').value;
 for(const mesh of meshes){
  const data=mesh.userData;
  if(data.assembledPosition)mesh.position.copy(data.assembledPosition).addScaledVector(new THREE.Vector3(...(data.explode||[0,0,0])),amount);
  if(data.cadPart)data.baseVisible=selected==='all'?($('cad-panels').checked||!['lid','bezel'].includes(data.kind)):mesh.name===selected;
  if(data.cadReference)data.baseVisible=selected==='all'&&$('cad-'+data.cadReference).checked;
 }
 if(inspector)inspector.applyVisibility();else for(const mesh of meshes)mesh.visible=mesh.userData.baseVisible!==false;
 $('explode-value').textContent=amount===0?'Assembled':Math.round(amount*100)+'% separated';
 requestRender();
}
for(const entry of models){
 const button=document.createElement('button');button.className='model';button.dataset.model=entry.id;button.setAttribute('aria-pressed','false');
 const img=document.createElement('img');img.src=entry.thumbnail||(entry.id==='railgun-built'?'/models/railgun-built/preview.png':('/models/'+entry.id+'/reference.png'));img.alt='';
 const text=document.createElement('span'),strong=document.createElement('strong'),small=document.createElement('small');
 strong.textContent=entry.name;small.textContent=entry.type;text.append(strong,small);button.append(img,text);
 button.onclick=()=>load(entry);$('models').append(button);
}
try {
 renderer=new THREE.WebGLRenderer({antialias:true,alpha:false});
 renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1;
 viewport.append(renderer.domElement);renderer.domElement.setAttribute('aria-label','Rendered 3D model');
 scene=new THREE.Scene();scene.background=new THREE.Color($('background').value);
 camera=new THREE.PerspectiveCamera(40,1,0.001,100);
 controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.dampingFactor=.08;controls.autoRotateSpeed=1.3;controls.addEventListener('change',requestRender);
 hemi=new THREE.HemisphereLight(0xdcecff,0x556477,1);scene.add(hemi);
 key=new THREE.DirectionalLight(0xffffff,2);key.position.set(3,5,4);scene.add(key);
 fill=new THREE.DirectionalLight(0xb8dfff,1.2);fill.position.set(-4,2,-3);scene.add(fill);
 const pmrem=new THREE.PMREMGenerator(renderer),room=new RoomEnvironment();
 envRT=pmrem.fromScene(room,0.04);room.dispose();pmrem.dispose();lights();
 new ResizeObserver(resize).observe(viewport);resize();
 $('reset').onclick=()=>fit();
 $('explode').oninput=applyAssembly;$('explode').onchange=()=>fit();
 for(const id of ['cad-monitor','cad-pc','cad-cover','cad-panels','cad-part'])$(id).onchange=()=>{applyAssembly();fit();};
 $('open-stl').onclick=()=>$('stl-file').click();
 $('stl-file').onchange=()=>{const file=$('stl-file').files[0];if(!file)return;load({id:'local-stl',name:file.name,type:'Local STL',format:'stl',url:URL.createObjectURL(file),local:true,front:0,note:'Local STL geometry, displayed in millimeters. This file stays in your browser and is not uploaded. Use mouse or touch to rotate, zoom and inspect.'});$('stl-file').value='';};
 for(const b of document.querySelectorAll('[data-view]'))b.onclick=()=>fit(b.dataset.view);
 $('chrome').onchange=()=>{chromeEnabled.value=$('chrome').checked?1:0;requestRender();};
 $('surface').onchange=surface;$('wireframe').onchange=surface;$('lighting').onchange=lights;
 $('background').onchange=()=>{scene.background.set($('background').value);requestRender();};
 $('exposure').oninput=()=>{renderer.toneMappingExposure=Number($('exposure').value);requestRender();};
 $('rotate').onchange=()=>{controls.autoRotate=$('rotate').checked;requestRender();};
 $('grid').onchange=()=>{if(grid)grid.visible=$('grid').checked;requestRender();};
 $('fullscreen').onclick=async()=>{try{if(document.fullscreenElement)await document.exitFullscreen();else if(document.querySelector('.workspace').requestFullscreen)await document.querySelector('.workspace').requestFullscreen();else statusMessage('Fullscreen is unavailable in this browser.');}catch{statusMessage('Fullscreen is unavailable in this browser.');}};
 document.addEventListener('visibilitychange',()=>{if(document.hidden){cancelAnimationFrame(frame);frame=0;}else requestRender();});
 viewport.addEventListener('keydown',e=>{if(e.key.toLowerCase()==='r')fit();});
 renderer.domElement.addEventListener('webglcontextlost',e=>{e.preventDefault();status.hidden=false;status.textContent='Graphics context lost. Reload this page to resume.';});
 inspector=createPartInspector({context:()=>({entry:active,model,meshes,scene,camera,controls,renderer}),render:requestRender,appearance:surface,restoreAssembly:mesh=>{if(!active?.cad)return;$('cad-part').value='all';$('cad-panels').checked=true;if(mesh?.userData.cadReference)$('cad-'+mesh.userData.cadReference).checked=true;applyAssembly();}});
 load(models.find(m=>m.id===location.hash.slice(1))||models[0]);
}catch(error){
 console.error(error);status.hidden=false;status.textContent='3D rendering could not start. Enable hardware acceleration or try another browser.';
}
function statusMessage(message){status.hidden=false;status.textContent=message;setTimeout(()=>status.hidden=true,4000);}
