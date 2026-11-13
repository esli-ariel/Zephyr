import * as THREE from './vendor/three/three.module.js';
import {MeshSurfaceSampler} from './vendor/three/MeshSurfaceSampler.js';

// Original procedural holographic bust. No downloaded model or texture.
export function createHumanoid(){
  const group=new THREE.Group(),head=new THREE.Group(),geometries=[],materials=[];
  group.add(head);head.name='head';
  const glass=new THREE.MeshBasicMaterial({color:0x73e4df,transparent:true,opacity:.045,depthWrite:false,side:THREE.DoubleSide});
  const grid=new THREE.LineBasicMaterial({color:0x73e4df,transparent:true,opacity:.09,depthWrite:false});
  const ink=new THREE.LineBasicMaterial({color:0xa0f5ee,transparent:true,opacity:.80,depthWrite:false});
  const dots=new THREE.PointsMaterial({color:0x73e4df,size:.012,transparent:true,opacity:.65,depthWrite:false});
  materials.push(glass,grid,ink,dots);
  const skinParts=[];
  function sculpt(parent,profile,depth){
    const curve=new THREE.SplineCurve(profile.map(([radius,y])=>new THREE.Vector2(radius,y)));
    const geometry=new THREE.LatheGeometry(curve.getPoints(40),64);geometry.scale(1,1,depth);geometry.computeVertexNormals();
    const mesh=new THREE.Mesh(geometry,glass);parent.add(mesh);geometries.push(geometry);skinParts.push({parent,mesh});
    const wire=new THREE.WireframeGeometry(geometry);parent.add(new THREE.LineSegments(wire,grid));geometries.push(wire);
  }
  // A closed jaw/cranium and one connected shoulder/neck volume.
  sculpt(head,[[.015,-.10],[.18,-.04],[.29,.13],[.35,.37],[.36,.60],[.31,.82],[.19,.98],[.002,1.035]],.82);
  sculpt(group,[[.01,-1.10],[.45,-1.10],[.65,-.97],[.76,-.64],[.66,-.49],[.35,-.35],[.145,-.21],[.13,-.02]],.48);
  function line(parent,points,material=ink,closed=false){
    const curve=new THREE.CatmullRomCurve3(points.map(p=>new THREE.Vector3(...p)),closed);
    const geometry=new THREE.BufferGeometry().setFromPoints(curve.getPoints(64));geometries.push(geometry);
    const item=new THREE.Line(geometry,material);parent.add(item);return item;
  }
  const eyes=[];
  for(const sign of [-1,1]){
    const eye=new THREE.Group();eye.position.set(sign*.151,.53,.271);head.add(eye);eye.name='eye';eyes.push(eye);
    line(eye,[[-.09,0,0],[-.045,.025,.012],[.025,.026,.012],[.085,.002,0]]);
    line(eye,[[-.09,0,0],[0,-.026,.015],[.085,.002,0]]);
    line(head,[[sign*.065,.645,.27],[sign*.14,.668,.27],[sign*.24,.64,.215]]);
    line(head,[[sign*.29,.45,.15],[sign*.31,.28,.16],[sign*.22,.11,.19]],grid);
    // Small iris instead of the former oversized cartoon eyes.
    const iris=new THREE.EllipseCurve(0,0,.018,.025).getPoints(24).map(p=>[p.x,p.y,.023]);line(eye,iris,ink,true);
  }
  line(head,[[0,.61,.30],[-.025,.40,.34],[-.045,.335,.37],[0,.32,.39],[.05,.34,.36]]);
  line(head,[[-.11,.19,.257],[-.04,.21,.281],[0,.20,.29],[.04,.21,.281],[.11,.19,.257]]);
  const lowerLip=new THREE.Group();lowerLip.position.set(0,.19,.27);head.add(lowerLip);lowerLip.name='voice-mouth';
  line(lowerLip,[[-.11,0,-.013],[-.05,-.026,.015],[0,-.034,.02],[.05,-.026,.015],[.11,0,-.013]]);
  line(group,[[-.60,-.59,.18],[-.32,-.48,.24],[0,-.59,.27],[.32,-.48,.24],[.60,-.59,.18]],grid);
  line(group,[[0,-.58,.28],[0,-.78,.30],[0,-1.04,.22]],grid);
  // Deterministic surface particles give volume without solid plastic surfaces.
  let seed=89;const random=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296;};
  for(const {parent,mesh} of skinParts){
    const sampler=new MeshSurfaceSampler(mesh).setRandomGenerator(random).build(),position=new THREE.Vector3(),values=[];
    for(let i=0;i<1250;i++){sampler.sample(position);values.push(position.x,position.y,position.z);}
    const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.Float32BufferAttribute(values,3));geometries.push(geometry);parent.add(new THREE.Points(geometry,dots));
  }
  const ringMaterial=new THREE.LineBasicMaterial({color:0x73e4df,transparent:true,opacity:.22,depthWrite:false});materials.push(ringMaterial);
  for(const radius of [.55,.70])line(group,Array.from({length:65},(_,i)=>{const a=i/64*Math.PI*2;return [Math.cos(a)*radius,-1.14,Math.sin(a)*radius*.60];}),ringMaterial,true);
  group.userData.design='holographic-humanoid';
  return {group,update({time,volume,state,quiet,day}){
    const blink=quiet?0:time%5.4<.18?Math.sin(time%5.4/.18*Math.PI):0;
    eyes.forEach(eye=>eye.scale.y=1-blink*.93);
    lowerLip.scale.y=state==='speaking'?1+(quiet?.5:volume*2):1;
    head.rotation.y=quiet?-.10:Math.sin(time*.32)*.10-.10;
    head.rotation.z=quiet?0:state==='thinking'?-.04:Math.sin(time*.5)*.008;
    group.position.y=.035+(quiet?0:Math.sin(time*1.4)*.01);
    for(const material of materials){material.color.set(day?'#14636c':'#73e4df');material.blending=day?THREE.NormalBlending:THREE.AdditiveBlending;}
    ink.opacity=day?.85:.75;grid.opacity=day?.12:.075;dots.opacity=day?.7:.60;glass.opacity=day?.035:.045;
  },dispose(){geometries.forEach(item=>item.dispose());materials.forEach(item=>item.dispose());}};
}
