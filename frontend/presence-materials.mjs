import * as THREE from './vendor/three/three.module.js';

// Small procedural surface maps: no image upload, external asset or CDN.
export function createSurfaceMaterials(){
  const textures=new Map(),materials=new Map();let seed=7421;
  const random=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296;};
  function texture(kind){
    if(textures.has(kind))return textures.get(kind);
    const canvas=document.createElement('canvas');canvas.width=canvas.height=128;const ctx=canvas.getContext('2d');
    ctx.fillStyle='#e1dfd8';ctx.fillRect(0,0,128,128);
    for(let i=0;i<2000;i++){const tone=160+Math.floor(random()*90);ctx.fillStyle=`rgba(${tone},${tone},${tone},.30)`;ctx.fillRect(random()*128,random()*128,1+random()*2,1+random()*2);}
    if(kind==='wood')for(let x=0;x<128;x++){ctx.strokeStyle=`rgba(65,42,23,${.06+random()*.12})`;ctx.beginPath();for(let y=0;y<128;y++){const px=x+Math.sin(y*.04+x*.03)*3;y?ctx.lineTo(px,y):ctx.moveTo(px,y);}ctx.stroke();}
    if(kind==='fabric'||kind==='paper')for(let n=0;n<128;n+=kind==='paper'?5:3){ctx.strokeStyle=kind==='paper'?'#9b968a':'#9c9b95';ctx.globalAlpha=.25;ctx.beginPath();ctx.moveTo(0,n);ctx.lineTo(128,n);if(kind==='fabric'){ctx.moveTo(n,0);ctx.lineTo(n,128);}ctx.stroke();ctx.globalAlpha=1;}
    if(kind==='brick'){ctx.strokeStyle='#79776e';ctx.lineWidth=2;for(let y=0;y<128;y+=20){ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(128,y);ctx.stroke();for(let x=(y/20)%2?0:20;x<128;x+=40){ctx.beginPath();ctx.moveTo(x,y);ctx.lineTo(x,y+20);ctx.stroke();}}}
    if(kind==='leaf'){ctx.strokeStyle='#777f65';ctx.globalAlpha=.3;for(let y=0;y<128;y+=12){ctx.beginPath();ctx.moveTo(64,y);ctx.lineTo(5,y+32);ctx.moveTo(64,y);ctx.lineTo(123,y+32);ctx.stroke();}ctx.globalAlpha=1;}
    if(kind==='clock'){ctx.fillStyle='#f4efdf';ctx.fillRect(0,0,128,128);ctx.strokeStyle='#3d4141';for(let i=0;i<12;i++){const a=i/12*Math.PI*2;ctx.lineWidth=i%3===0?3:1;ctx.beginPath();ctx.moveTo(64+Math.sin(a)*47,64+Math.cos(a)*47);ctx.lineTo(64+Math.sin(a)*55,64+Math.cos(a)*55);ctx.stroke();}}
    if(kind==='globe'){ctx.fillStyle='#669ac0';ctx.fillRect(0,0,128,128);ctx.fillStyle='#8eac72';for(const [x,y,rx,ry] of [[23,30,17,20],[42,76,9,27],[73,42,10,20],[88,28,25,14],[108,86,13,9]]){ctx.beginPath();ctx.ellipse(x,y,rx,ry,-.3,0,Math.PI*2);ctx.fill();}ctx.strokeStyle='#d0dfdf55';ctx.lineWidth=.6;for(let n=16;n<128;n+=16){ctx.beginPath();ctx.moveTo(n,0);ctx.lineTo(n,128);ctx.moveTo(0,n);ctx.lineTo(128,n);ctx.stroke();}}
    if(kind==='ball'){ctx.fillStyle='#e8e9e5';ctx.fillRect(0,0,128,128);ctx.fillStyle='#344047';for(const [x,y] of [[24,25],[88,24],[56,83],[120,88]]){ctx.beginPath();for(let i=0;i<5;i++){const a=i*Math.PI*2/5;const px=x+Math.sin(a)*13,py=y+Math.cos(a)*13;i?ctx.lineTo(px,py):ctx.moveTo(px,py);}ctx.closePath();ctx.fill();}}
    const map=new THREE.CanvasTexture(canvas);map.colorSpace=THREE.SRGBColorSpace;map.wrapS=map.wrapT=THREE.RepeatWrapping;map.anisotropy=2;textures.set(kind,map);return map;
  }
  const M=(color,kind='grain',roughness=.62,metalness=.03)=>({color,kind,roughness,metalness});
  function recipe(id,index){
    const wood=M('#b47d48','wood',.5),darkWood=M('#67452c','wood',.58),leaf=M('#53854b','leaf',.86),metal=M('#b4bdc3','grain',.30,.70),rubber=M('#252a2d','grain',.95),white=M('#f0ede0','grain',.44),glass=M('#81b6bb','grain',.12,.20);
    if(id==='house')return index===1||index===2?M('#b26344','brick',.9):index===3?darkWood:index>=4?glass:M('#d9c397','brick',.92);
    if(id==='tree')return index===0?darkWood:leaf;
    if(id==='cup'||id==='teapot')return M('#81b7b8','grain',.23);
    if(id==='book')return index===2?M('#efe8d6','paper',.95):M('#6c3743','fabric',.76);
    if(id==='fish')return index>=3?rubber:index===0?M('#d8a75d','grain',.45):M('#b56a3b','grain',.58);
    if(id==='heart')return M('#c2444a','grain',.35);
    if(id==='apple')return index===0?M('#c9483c','grain',.40):index===1?darkWood:leaf;
    if(id==='pear')return index<2?M('#b8b65d','grain',.57):darkWood;
    if(id==='banana')return M('#e4c45b','grain',.55);
    if(id==='car')return index>=2?rubber:index===1?glass:M('#a64740','grain',.27,.35);
    if(id==='airplane')return index===0?white:metal;
    if(id==='boat')return index<=1?wood:M('#e8dcc2','fabric',.94);
    if(id==='rocket')return index===0?white:index===4?M('#e8a15b','grain',.38):M('#a34c47','grain',.38,.18);
    if(id==='bicycle')return index<2?rubber:index===5?darkWood:metal;
    if(id==='chair'||id==='table')return wood;
    if(id==='lamp')return index===2?M('#d6c6a7','fabric',.88):metal;
    if(id==='key')return M('#c9a45a','grain',.25,.85);
    if(id==='umbrella')return index===0?M('#4f7f96','fabric',.9):index===1?metal:darkWood;
    if(id==='clock')return index===0?M('#f1ead7','clock',.65):rubber;
    if(id==='star')return M('#d5b66b','grain',.28,.7);
    if(id==='moon')return M('#d5cba9','grain',.9);
    if(id==='flower')return index<=1?leaf:index===2?M('#d7ae42','grain',.86):M('#c58d9a','fabric',.8);
    if(id==='bottle')return index===3?metal:M('#438276','grain',.18,.12);
    if(id==='hat')return index===2?darkWood:M('#58616a','fabric',.92);
    if(id==='castle'||id==='bridge')return M('#aaa599','brick',.96);
    if(id==='ball')return M('#eeeeea','ball',.75);
    if(id==='diamond')return M('#b4d5e5','grain',.13,.30);
    if(id==='drum')return index===0?M('#965148','wood',.5):metal;
    if(id==='snowman')return M('#e6ebec','grain',.95);
    if(id==='globe')return index===0?M('#ffffff','globe',.65):metal;
    if(id==='camera')return index===0?M('#373e43','fabric',.9):index===1?M('#354e59','grain',.12,.3):metal;
    if(id==='guitar')return index<2?wood:index===2?darkWood:rubber;
    if(id==='pineapple')return index===0?M('#b39b58','grain',.86):leaf;
    return white;
  }
  return {surface(id,part,index){const spec=recipe(id,index),key=JSON.stringify(spec);if(!materials.has(key)){const map=texture(spec.kind);const material=new THREE.MeshStandardMaterial({color:spec.color,map,bumpMap:map,bumpScale:spec.kind==='wood'?.018:.009,roughness:spec.roughness,metalness:spec.metalness,transparent:true,opacity:1,side:THREE.DoubleSide});materials.set(key,material);}return materials.get(key);},dispose(){for(const material of materials.values())material.dispose();for(const map of textures.values())map.dispose();}};
}
