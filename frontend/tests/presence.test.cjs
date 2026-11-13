const {test}=require('node:test');const assert=require('node:assert/strict');const {readFileSync}=require('node:fs');const {runInNewContext}=require('node:vm');const {join}=require('node:path');const {pathToFileURL}=require('node:url');
const window={};for(const name of ['visual-vocabulary.js','presence-ui.js'])runInNewContext(readFileSync(join(__dirname,'../'+name),'utf8'),{window});
test('Presence choices accept only points or humanoid and recover safely from obsolete values',()=>{for(const value of [null,undefined,'','robot','<script>','three'])assert.equal(window.ZephyrPresenceMode.normalize(value),'points');assert.equal(window.ZephyrPresenceMode.normalize('humanoid'),'humanoid');});
test('Every catalogue object has finite surface samples from real Three.js geometry',async()=>{
  const {buildVisualObject}=await import(pathToFileURL(join(__dirname,'../presence-3d.mjs')));let totalMeshes=0;
  for(const item of window.ZephyrVocabulary.objects){const model=buildVisualObject(window.ZephyrVocabulary,item.id,300);assert.equal(model.samples.length,900);assert.ok(model.samples.every(Number.isFinite));assert.ok(model.samples.every(value=>Math.abs(value)<1.65),item.id);let meshes=0;model.group.traverse(node=>{if(node.isMesh){meshes++;assert.ok(node.geometry.getAttribute('position').count>0);}});assert.ok(meshes>0,item.id);totalMeshes+=meshes;model.dispose();}assert.ok(totalMeshes>60);
});
test('Surface sampling is reproducible and unknown objects cannot silently become another shape',async()=>{const {buildVisualObject}=await import(pathToFileURL(join(__dirname,'../presence-3d.mjs')));const a=buildVisualObject(window.ZephyrVocabulary,'camera',100),b=buildVisualObject(window.ZephyrVocabulary,'camera',100);assert.deepEqual(a.samples,b.samples);assert.throws(()=>buildVisualObject(window.ZephyrVocabulary,'missing-object',100));a.dispose();b.dispose();});

test('The holographic bust is finite, texture-free, voice-driven and stable with reduced motion',async()=>{
  const {createHumanoid}=await import(pathToFileURL(join(__dirname,'../humanoid.mjs')));const avatar=createHumanoid();const geometries=new Set(),materials=new Set();
  avatar.group.traverse(node=>{if(node.geometry){geometries.add(node.geometry);assert.ok(node.geometry.attributes.position.array.every(Number.isFinite));}if(node.material){materials.add(node.material);assert.ok(!node.material.map);}});
  const mouth=avatar.group.getObjectByName('voice-mouth'),head=avatar.group.getObjectByName('head');
  avatar.update({time:2,volume:.1,state:'speaking',quiet:false,day:false});const small=mouth.scale.y;
  avatar.update({time:3,volume:.9,state:'speaking',quiet:false,day:false});assert.ok(mouth.scale.y>small);
  avatar.update({time:8,volume:0,state:'idle',quiet:true,day:true});const still=[head.rotation.y,head.rotation.z,avatar.group.position.y];assert.equal(mouth.scale.y,1);
  avatar.update({time:18,volume:0,state:'idle',quiet:true,day:true});assert.deepEqual([head.rotation.y,head.rotation.z,avatar.group.position.y],still);
  let released=0;for(const item of [...geometries,...materials])item.addEventListener('dispose',()=>released++);avatar.dispose();assert.equal(released,geometries.size+materials.size);
});
