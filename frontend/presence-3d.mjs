import * as THREE from './vendor/three/three.module.js';
import {MeshSurfaceSampler} from './vendor/three/MeshSurfaceSampler.js';
import {createHumanoid} from './humanoid.mjs?v=0.8.9-hologram';

function primitive(part){
  if(part.kind==='sphere')return new THREE.SphereGeometry(1,24,16);
  if(part.kind==='box')return new THREE.BoxGeometry(2,2,2);
  if(part.kind==='cylinder')return new THREE.CylinderGeometry(1,1,2,32,1,part.caps===false);
  if(part.kind==='cone')return new THREE.ConeGeometry(1,2,part.segments||32).rotateZ(Math.PI);
  if(part.kind==='torus'){const geometry=new THREE.TorusGeometry(1,part.tube,12,48,part.arc||Math.PI*2);if(part.horizontal)geometry.rotateX(Math.PI/2);return geometry;}
  const shape=new THREE.Shape();
  if(part.kind==='prism'){part.outline.forEach(([x,y],i)=>i?shape.lineTo(x,y):shape.moveTo(x,y));shape.closePath();return new THREE.ExtrudeGeometry(shape,{depth:part.depth,bevelEnabled:false}).translate(0,0,-part.depth/2);}
  if(part.kind==='heart'){
    for(let i=0;i<=64;i++){const t=i/64*Math.PI*2,x=Math.sin(t)**3,y=-(13*Math.cos(t)-5*Math.cos(2*t)-2*Math.cos(3*t)-Math.cos(4*t))/16;i?shape.lineTo(x,y):shape.moveTo(x,y);}shape.closePath();
    return new THREE.ExtrudeGeometry(shape,{depth:.40,bevelEnabled:true,bevelSegments:3,steps:1,bevelSize:.12,bevelThickness:.13}).translate(0,0,-.20);
  }
  throw new Error('Unsupported 3D primitive: '+part.kind);
}

function contourGeometry(part,geometry){
  const outline=new THREE.EdgesGeometry(geometry,35),values=[...outline.attributes.position.array];outline.dispose();
  const curve=points=>{for(let i=1;i<points.length;i++)values.push(...points[i-1],...points[i]);};
  const ring=(fn,arc=Math.PI*2)=>curve(Array.from({length:65},(_,i)=>fn(i/64*arc)));
  if(part.kind==='sphere'){
    ring(a=>[Math.cos(a),Math.sin(a),0]);ring(a=>[0,Math.sin(a),Math.cos(a)]);
    ring(a=>[Math.cos(a),0,Math.sin(a)]);
  }else if(part.kind==='torus'){
    for(const v of [0,Math.PI,Math.PI/2])ring(a=>{const radius=1+part.tube*Math.cos(v),x=radius*Math.cos(a),y=radius*Math.sin(a),z=part.tube*Math.sin(v);return part.horizontal?[x,z,y]:[x,y,z];},part.arc||Math.PI*2);
  }else if(part.kind==='cone'){
    for(let i=0;i<4;i++){const a=i*Math.PI/2;curve([[0,-1,0],[Math.cos(a),1,Math.sin(a)]]);}
  }
  const result=new THREE.BufferGeometry();result.setAttribute('position',new THREE.Float32BufferAttribute(values,3));return result;
}

export function buildVisualObject(vocabulary,id,count=2100,materials={}){
  const group=new THREE.Group(),geometries=[],samplers=[];
  const owned=!materials.surface&&!materials.createSurface;
  const surface=materials.surface||new THREE.MeshBasicMaterial({transparent:true,opacity:.04,side:THREE.DoubleSide});
  const edge=materials.edge||new THREE.LineBasicMaterial({transparent:true,opacity:.16});
  let seed=Array.from(id).reduce((n,c)=>Math.imul(n,31)+c.charCodeAt(0),41)>>>0;
  const random=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296;};
  for(const [partIndex,part] of vocabulary.getModelParts(id).entries()){
    const geometry=primitive(part),scale=new THREE.Vector3(...(part.scale||[1,1,1])),center=new THREE.Vector3(...(part.center||[0,0,0]));
    const rotation=new THREE.Quaternion().setFromEuler(new THREE.Euler(...(part.rotate||[0,0,0]),'ZYX'));
    const edges=contourGeometry(part,geometry),matrix=new THREE.Matrix4().compose(center,rotation,scale);
    geometry.applyMatrix4(matrix);edges.applyMatrix4(matrix);geometry.computeVertexNormals();
    const mesh=new THREE.Mesh(geometry,materials.createSurface?materials.createSurface(id,part,partIndex):surface);
    mesh.userData.surface=true;group.add(mesh,new THREE.LineSegments(edges,edge));geometries.push(geometry,edges);
    samplers.push({weight:part.weight,edges:edges.attributes.position.array,sampler:new MeshSurfaceSampler(mesh).setRandomGenerator(random).build()});
  }
  // Catalogue coordinates use downward-positive Y; convert once to Three's world.
  group.scale.y=-1;
  const total=samplers.reduce((sum,item)=>sum+item.weight,0),samples=new Float32Array(count*3),point=new THREE.Vector3();
  for(let i=0;i<count;i++){
    let pick=random()*total,selected=samplers.at(-1);
    for(const item of samplers){pick-=item.weight;if(pick<0){selected=item;break;}}
    if(selected.edges.length&&random()<.40){const e=selected.edges,n=Math.floor(random()*(e.length/6))*6,t=random();point.set(e[n]*(1-t)+e[n+3]*t,e[n+1]*(1-t)+e[n+4]*t,e[n+2]*(1-t)+e[n+5]*t);}else selected.sampler.sample(point);samples.set([point.x,-point.y,point.z],i*3);
  }
  return {group,samples,dispose(){geometries.forEach(item=>item.dispose());if(owned){surface.dispose();edge.dispose();}}};
}

export function createPresenceScene({stage,vocabulary,onReady,onUnavailable,count=2100}){
  const canvas=document.createElement('canvas');canvas.className='presence-webgl';canvas.setAttribute('aria-hidden','true');
  const context=canvas.getContext('webgl2',{alpha:true,antialias:true,powerPreference:'low-power'});if(!context)throw new Error('WebGL 2 unavailable');
  const renderer=new THREE.WebGLRenderer({canvas,context,alpha:true,antialias:true,powerPreference:'low-power'});renderer.setClearColor(0,0);renderer.setPixelRatio(Math.min(devicePixelRatio||1,1.6));renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.05;
  stage.prepend(canvas);const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(38,1,.1,40);camera.position.z=4.4;
  scene.add(new THREE.HemisphereLight(0xffffff,0x26333b,2.1));const key=new THREE.DirectionalLight(0xfff0da,3.0);key.position.set(-3,4,5);scene.add(key);const rimLight=new THREE.DirectionalLight(0x77e4e1,2.4);rimLight.position.set(3,1,-3);scene.add(rimLight);
  const avatar=createHumanoid();scene.add(avatar.group);
  const positions=new Float32Array(count*3),sizes=new Float32Array(count),geometry=new THREE.BufferGeometry();for(let i=0;i<count;i++)sizes[i]=.7+((i*.75487766)%1)*.65;
  geometry.setAttribute('position',new THREE.BufferAttribute(positions,3).setUsage(THREE.DynamicDrawUsage));geometry.setAttribute('aSize',new THREE.BufferAttribute(sizes,1));
  const material=new THREE.ShaderMaterial({transparent:true,depthWrite:false,uniforms:{uColor:{value:new THREE.Color('#73e4df')},uRatio:{value:renderer.getPixelRatio()},uSize:{value:23},uOpacity:{value:1}},
    vertexShader:`attribute float aSize;uniform float uRatio;uniform float uSize;varying float vDepth;void main(){vec4 mv=modelViewMatrix*vec4(position,1.0);gl_Position=projectionMatrix*mv;gl_PointSize=clamp(aSize*uSize/-mv.z*uRatio,1.0,12.0*uRatio);vDepth=clamp((position.z+1.6)/3.2,.0,1.0);}`,
    fragmentShader:`uniform vec3 uColor;uniform float uOpacity;varying float vDepth;void main(){float r=length(gl_PointCoord-.5)*2.0;if(r>1.0)discard;float halo=pow(1.0-r,2.2);float core=1.0-smoothstep(.0,.32,r);float alpha=(halo*.48+core*.72)*(.48+vDepth*.52)*uOpacity;vec3 tint=pow(uColor,vec3(1.0/2.2));gl_FragColor=vec4(tint+core*.12,alpha);}`});
  const cloud=new THREE.Points(geometry,material);cloud.frustumCulled=false;scene.add(cloud);
  const surface=new THREE.MeshBasicMaterial({color:0x73e4df,transparent:true,opacity:.025,side:THREE.DoubleSide,depthWrite:false});
  const edge=new THREE.LineBasicMaterial({color:0x73e4df,transparent:true,opacity:.11,depthWrite:false});
  const cache=new Map();let currentId=null,current=null,width=0,height=0,ready=true,disposed=false,first=true;
  function object(id){if(cache.has(id))return cache.get(id);const entry=buildVisualObject(vocabulary,id,count,{surface,edge});cache.set(id,entry);scene.add(entry.group);entry.group.visible=false;if(cache.size>4){const [key,value]=cache.entries().next().value;if(key!==id){scene.remove(value.group);value.dispose();cache.delete(key);}}return entry;}
  canvas.addEventListener('webglcontextlost',event=>{event.preventDefault();ready=false;onUnavailable();});
  canvas.addEventListener('webglcontextrestored',()=>{if(!disposed){ready=true;first=true;onReady();}});
  onReady();
  return {get ready(){return ready&&!disposed;},render(frame){
    if(!ready||disposed)return false;
    if(frame.width<=0||frame.height<=0)return true;
    if(width!==frame.width||height!==frame.height){width=frame.width;height=frame.height;renderer.setSize(width,height,false);camera.aspect=width/height;camera.position.z=4.4/Math.min(1,camera.aspect*1.25);camera.updateProjectionMatrix();}
    const human=frame.mode==='humanoid';avatar.group.visible=human;cloud.visible=!human;
    if(current)current.group.visible=false;
    const day=frame.theme>.5;scene.background=null;material.uniforms.uSize.value=23;
    if(human){avatar.update({time:frame.time,volume:frame.volume,state:frame.state,quiet:frame.quiet,day});}
    else{
      if(currentId!==frame.objectId){currentId=frame.objectId;current=object(currentId);}
      current.group.visible=frame.form>.02&&frame.state==='idle';current.group.rotation.set(frame.quiet?-.16:-.16+Math.sin(frame.time*.25)*.10,frame.quiet?.28:Math.sin(frame.time*.18)*.65-.20,0);
      const opacity=THREE.MathUtils.smoothstep(frame.form,.18,.95);
      edge.opacity=opacity*(day?.28:.23);material.uniforms.uOpacity.value=1;material.uniforms.uSize.value=23-7*frame.form;
      surface.opacity=opacity*.012;surface.color.set(day?'#207b81':'#73e4df');edge.color.copy(surface.color);
      material.blending=day?THREE.NormalBlending:THREE.AdditiveBlending;material.uniforms.uColor.value.setHSL((187+Math.sin(frame.time*.19)*8+(frame.state==='thinking'?34:0))/360,.60,day?.27:.62);
      const yaw=frame.quiet?.28:Math.sin(frame.time*.18)*.65-.20,pitch=frame.quiet?-.16:-.16+Math.sin(frame.time*.25)*.10,cy=Math.cos(yaw),sy=Math.sin(yaw),cp=Math.cos(pitch),sp=Math.sin(pitch);
      for(let i=0;i<count;i++){
        const index=i*3,y=1-2*(i+.5)/count,r=Math.sqrt(1-y*y),angle=i*2.399963229728653,phase=i*.73;
        const freeX=Math.sin(i*71.17)*1.30+(frame.quiet?0:Math.sin(frame.time*.7+phase)*.10),freeY=Math.cos(i*17.91)*.95+(frame.quiet?0:Math.cos(frame.time*.5+phase)*.09),freeZ=Math.sin(i*31.7)*.55;
        const source=current.samples,sx=source[index],my=source[index+1],sz=source[index+2],ox=sx*cy+sz*sy,oz=sz*cy-sx*sy;
        let x=freeX*(1-frame.form)+ox*frame.form,yy=freeY*(1-frame.form)+(my*cp-oz*sp)*frame.form,z=freeZ*(1-frame.form)+(my*sp+oz*cp)*frame.form;
        if(frame.state==='listening'){x=freeX*.85;yy=freeY*.85+(frame.quiet?0:Math.sin(y*10-frame.time*4)*frame.volume*.20);z=freeZ;}
        else if(frame.state==='speaking'){
          const spin=angle+frame.time*.24,wave=frame.quiet?1:1+frame.volume*.17+Math.sin(y*7+frame.time*4.3)*.055,flight=!frame.quiet&&i%6===0?Math.sin(frame.time*.8+phase)*.12:0;
          x=r*Math.cos(spin)*(wave+flight);yy=y*wave;z=r*Math.sin(spin)*(wave+flight);
        }else if(frame.state==='thinking'){const spin=angle+frame.time*.8,rad=.35+.55*((phase*.371)%1);x=Math.cos(spin)*rad;yy=Math.sin(spin)*rad*.72;z=Math.sin(phase+frame.time)*.3;}
        const pulse=frame.quiet?0:frame.pulse*.10;x*=1+pulse;yy*=1+pulse;z*=1+pulse;
        const ease=first||frame.quiet?1:1-Math.exp(-frame.delta*(frame.state==='speaking'?8:4.8));positions[index]+=(x-positions[index])*ease;positions[index+1]+=(yy-positions[index+1])*ease;positions[index+2]+=(z-positions[index+2])*ease;
      }
      geometry.attributes.position.needsUpdate=true;first=false;
    }
    renderer.render(scene,camera);return true;
  },dispose(){disposed=true;ready=false;for(const value of cache.values())value.dispose();avatar.dispose();geometry.dispose();material.dispose();surface.dispose();edge.dispose();renderer.dispose();canvas.remove();}};
}
