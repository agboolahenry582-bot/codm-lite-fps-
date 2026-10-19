from flask import Flask, render_template_string

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CODM Lite - FPS</title>
<style>
body{margin:0;overflow:hidden;background:#000;font-family:Arial;color:white}
#hud{position:fixed;top:0;left:0;width:100%;padding:15px;display:flex;justify-content:space-between;pointer-events:none;z-index:10}
#crosshair{position:fixed;top:50%;left:50%;width:20px;height:20px;transform:translate(-50%,-50%);pointer-events:none;z-index:10}
#crosshair::before,#crosshair::after{content:'';position:absolute;background:white}
#crosshair::before{width:2px;height:20px;left:9px;top:0}
#crosshair::after{width:20px;height:2px;left:0;top:9px}
#start{position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.9);display:flex;flex-direction:column;justify-content:center;align-items:center;z-index:20}
button{padding:15px 30px;font-size:18px;background:#38bdf8;border:none;border-radius:8px;font-weight:bold;cursor:pointer}
#gun{position:fixed;bottom:0;right:20%;width:300px;height:200px;pointer-events:none;z-index:5;background:linear-gradient(0deg, #222 0%, transparent 100%);}
</style>
<script type="importmap">
{"imports":{"three":"https://unpkg.com/three@0.160.0/build/three.module.js","three/addons/":"https://unpkg.com/three@0.160.0/examples/jsm/"}}
</script>
</head>
<body>

<div id="hud">
<div>❤️ HP: <span id="hp">100</span> | 🎯 Score: <span id="score">0</span> | 🔫 Ammo: <span id="ammo">30</span></div>
<div>WASD = Move | Mouse = Look | Click = Shoot | R = Reload</div>
</div>

<div id="crosshair"></div>

<div id="start">
<h1 style="color:#38bdf8;font-size:48px">CODM LITE 🔫</h1>
<p>Your FPS Shooter - Like Call of Duty Mobile</p>
<p style="color:#aaa">Enemies go spawn, shoot them!</p>
<br>
<button id="playBtn">▶️ CLICK TO PLAY</button>
<br><br>
<a href="/" style="color:#555;font-size:12px">Back to Portfolio</a>
</div>

<script type="module">
import * as THREE from 'three';
import { PointerLockControls } from 'three/addons/controls/PointerLockControls.js';

let scene,camera,renderer,controls;
let enemies=[], score=0, hp=100, ammo=30;
let keys={};

init();
function init(){
 scene=new THREE.Scene();
 scene.background=new THREE.Color(0x87CEEB);
 scene.fog=new THREE.Fog(0x87CEEB, 0, 750);
 
 camera=new THREE.PerspectiveCamera(75, innerWidth/innerHeight, 0.1, 1000);
 
 renderer=new THREE.WebGLRenderer({antialias:true});
 renderer.setSize(innerWidth,innerHeight);
 document.body.appendChild(renderer.domElement);
 
 // Light
 scene.add(new THREE.HemisphereLight(0xffffff, 0x444444, 1));
 let light=new THREE.DirectionalLight(0xffffff,0.8);
 light.position.set(0,20,10);
 scene.add(light);
 
 // Floor
 let floor=new THREE.Mesh(new THREE.PlaneGeometry(2000,2000), new THREE.MeshLambertMaterial({color:0x228B22}));
 floor.rotation.x=-Math.PI/2;
 scene.add(floor);
 
 // Walls / Cover like CODM map
 for(let i=0;i<20;i++){
   let box=new THREE.Mesh(new THREE.BoxGeometry(10,10,2), new THREE.MeshLambertMaterial({color:0x888888}));
   box.position.set((Math.random()-0.5)*200,5,(Math.random()-0.5)*200);
   scene.add(box);
 }
 
 controls=new PointerLockControls(camera, document.body);
 scene.add(controls.getObject());
 controls.getObject().position.set(0,10,30);
 
 document.getElementById('playBtn').onclick=()=>{ controls.lock(); };
 controls.addEventListener('lock',()=>{ document.getElementById('start').style.display='none'; });
 controls.addEventListener('unlock',()=>{ document.getElementById('start').style.display='flex'; });
 
 // Movement
 document.addEventListener('keydown',e=>{ keys[e.code]=true; if(e.code==='KeyR'){ ammo=30; updateHUD(); } });
 document.addEventListener('keyup',e=>keys[e.code]=false);
 document.addEventListener('click',()=>{ if(controls.isLocked) shoot(); });
 
 spawnEnemy();
 setInterval(spawnEnemy, 3000);
 animate();
}

function spawnEnemy(){
 let geom=new THREE.BoxGeometry(4,8,4);
 let mat=new THREE.MeshLambertMaterial({color:0xff0000});
 let enemy=new THREE.Mesh(geom,mat);
 enemy.position.set((Math.random()-0.5)*100,4,(Math.random()-0.5)*100-50);
 enemy.userData.hp=2;
 scene.add(enemy);
 enemies.push(enemy);
}

function shoot(){
 if(ammo<=0) return;
 ammo--; updateHUD();
 // Raycast
 let ray=new THREE.Raycaster();
 ray.setFromCamera(new THREE.Vector2(0,0), camera);
 let hits=ray.intersectObjects(enemies);
 if(hits.length>0){
   let e=hits[0].object;
   e.userData.hp--;
   e.material.color.set(0xffff00);
   setTimeout(()=>e.material.color.set(0xff0000),100);
   if(e.userData.hp<=0){
     scene.remove(e);
     enemies=enemies.filter(x=>x!==e);
     score+=10; updateHUD();
   }
 }
 // Flash
 document.getElementById('crosshair').style.transform='translate(-50%,-50%) scale(1.5)';
 setTimeout(()=>document.getElementById('crosshair').style.transform='translate(-50%,-50%) scale(1)',50);
}

function updateHUD(){
 document.getElementById('score').innerText=score;
 document.getElementById('hp').innerText=hp;
 document.getElementById('ammo').innerText=ammo;
}

let prevTime=performance.now();
function animate(){
 requestAnimationFrame(animate);
 let time=performance.now();
 let delta=(time-prevTime)/1000;
 prevTime=time;
 
 if(controls.isLocked){
   let speed=50*delta;
   if(keys['KeyW']) controls.moveForward(speed);
   if(keys['KeyS']) controls.moveForward(-speed);
   if(keys['KeyA']) controls.moveRight(-speed);
   if(keys['KeyD']) controls.moveRight(speed);
   // gravity
   if(controls.getObject().position.y>10) controls.getObject().position.y-=20*delta;
   if(controls.getObject().position.y<10) controls.getObject().position.y=10;
 }
 
 // Enemies chase small
 enemies.forEach(en=>{
   let dir=new THREE.Vector3().subVectors(controls.getObject().position, en.position).normalize();
   en.position.add(dir.multiplyScalar(0.05));
   if(en.position.distanceTo(controls.getObject().position)<6){
     hp-=0.1; updateHUD();
     if(hp<=0){ hp=100; score=0; alert('YOU DIED! Score reset'); }
   }
 });
 
 renderer.render(scene,camera);
}
</script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML)

if __name__ == '__main__':
    app.run()
