import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

const $=id=>document.getElementById(id);
const models=[
 {id:'railgun',name:'Instagib railgun',type:'Weapon',file:'railgun.glb',note:'Long accelerator rails and cyan accents. First-pass geometry with visible texture artifacts.',front:Math.PI},
 {id:'bumper',name:'Pinball bumper',type:'Table component',file:'bumper.glb',note:'Red cap, impact ring and metal pedestal. Generated textures still need cleanup.',front:Math.PI},
 {id:'woman',name:'Woman character',type:'Character study',file:'woman.glb',note:'Static, unrigged character. Face, hands and clothing show significant reconstruction artifacts.',front:Math.PI}
];
let scene,camera,renderer,controls,model,grid,envRT,key,fill,hemi;
let ticket=0,active,meshes=[],fitDistance=4,radius=1,frame=0;
const viewport=$('viewport'), status=$('status');
const clay=new THREE.MeshStandardMaterial({color:0xbcc4cc,roughness:0.75,metalness:0});
const normals=new THREE.MeshNormalMaterial();
function dispose(root){
 const geometries=new Set(),materials=new Set(),textures=new Set();
 root.traverse(o=>{if(!o.isMesh)return;geometries.add(o.geometry);const orig=o.userData.originalMaterial||o.material;for(const m of (Array.isArray(orig)?orig:[orig])){materials.add(m);for(const v of Object.values(m))if(v?.isTexture)textures.add(v);}});
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
 const directions={home:[0.6,0.3,1],front:[0,0,1],back:[0,0,-1],left:[-1,0,0],right:[1,0,0],top:[0,1,0.001]};
 const direction=new THREE.Vector3(...directions[view]).normalize();
 controls.target.set(0,0,0);camera.position.copy(direction.multiplyScalar(fitDistance));
 camera.near=radius/1000;camera.far=radius*100;camera.updateProjectionMatrix();
 controls.minDistance=radius*0.04;controls.maxDistance=radius*20;controls.update();requestRender();
}
function surface(){
 const mode=$('surface').value,wire=$('wireframe').checked;
 for(const mesh of meshes){
  mesh.material=mode==='clay'?clay:mode==='normals'?normals:mesh.userData.originalMaterial;
  for(const m of (Array.isArray(mesh.material)?mesh.material:[mesh.material]))m.wireframe=wire;
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
  const gltf=await new GLTFLoader().loadAsync('/models/'+entry.id+'/'+entry.file+'?v=uv2');
  if(current!==ticket){dispose(gltf.scene);return;}
  if(model){scene.remove(model);dispose(model);}
  model=gltf.scene;active=entry;meshes=[];
  model.rotation.y=entry.front;
  model.updateMatrixWorld(true);
  const box=new THREE.Box3().setFromObject(model),center=box.getCenter(new THREE.Vector3());
  model.position.sub(center);model.updateMatrixWorld(true);
  radius=box.getBoundingSphere(new THREE.Sphere()).radius;
  let triangles=0;
  model.traverse(o=>{if(o.isMesh){o.userData.originalMaterial=o.material;meshes.push(o);triangles+=(o.geometry.index?.count||o.geometry.attributes.position.count)/3;}});
  scene.add(model);
  if(grid){scene.remove(grid);grid.geometry.dispose();for(const m of (Array.isArray(grid.material)?grid.material:[grid.material]))m.dispose();}
  grid=new THREE.GridHelper(radius*5,20,0x425464,0x293947);grid.position.y=box.min.y-center.y-0.015*radius;grid.visible=$('grid').checked;scene.add(grid);
  $('title').textContent=entry.name;$('description').textContent=entry.note;
  $('stats').textContent=triangles.toLocaleString()+' triangles · 1024px textures';
  $('download').href='/models/'+entry.id+'/'+entry.file+'?v=uv2';
  $('reference-image').src='/models/'+entry.id+'/reference.png';
  $('reference-link').href=$('reference-image').src;
  for(const button of document.querySelectorAll('.model'))button.setAttribute('aria-pressed',String(button.dataset.model===entry.id));
  history.replaceState(null,'','#'+entry.id);
  surface();fit();status.hidden=true;viewport.dataset.state='ready';viewport.dataset.model=entry.id;
 }catch(error){
  if(current!==ticket)return;
  console.error(error);status.textContent='Could not load this model. Check your connection and select it again to retry.';
  viewport.dataset.state='error';
 }
}
for(const entry of models){
 const button=document.createElement('button');button.className='model';button.dataset.model=entry.id;button.setAttribute('aria-pressed','false');
 const img=document.createElement('img');img.src='/models/'+entry.id+'/reference.png';img.alt='';
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
 for(const b of document.querySelectorAll('[data-view]'))b.onclick=()=>fit(b.dataset.view);
 $('surface').onchange=surface;$('wireframe').onchange=surface;$('lighting').onchange=lights;
 $('background').onchange=()=>{scene.background.set($('background').value);requestRender();};
 $('exposure').oninput=()=>{renderer.toneMappingExposure=Number($('exposure').value);requestRender();};
 $('rotate').onchange=()=>{controls.autoRotate=$('rotate').checked;requestRender();};
 $('grid').onchange=()=>{if(grid)grid.visible=$('grid').checked;requestRender();};
 $('fullscreen').onclick=async()=>{try{if(document.fullscreenElement)await document.exitFullscreen();else if(document.querySelector('.workspace').requestFullscreen)await document.querySelector('.workspace').requestFullscreen();else statusMessage('Fullscreen is unavailable in this browser.');}catch{statusMessage('Fullscreen is unavailable in this browser.');}};
 document.addEventListener('visibilitychange',()=>{if(document.hidden){cancelAnimationFrame(frame);frame=0;}else requestRender();});
 viewport.addEventListener('keydown',e=>{if(e.key.toLowerCase()==='r')fit();});
 renderer.domElement.addEventListener('webglcontextlost',e=>{e.preventDefault();status.hidden=false;status.textContent='Graphics context lost. Reload this page to resume.';});
 load(models.find(m=>m.id===location.hash.slice(1))||models[0]);
}catch(error){
 console.error(error);status.hidden=false;status.textContent='3D rendering could not start. Enable hardware acceleration or try another browser.';
}
function statusMessage(message){status.hidden=false;status.textContent=message;setTimeout(()=>status.hidden=true,4000);}
