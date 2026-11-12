const {test}=require('node:test');
const assert=require('node:assert/strict');
const {readFileSync}=require('node:fs');
const {runInNewContext}=require('node:vm');
const {join}=require('node:path');
const window={};runInNewContext(readFileSync(join(__dirname,'../voice-tools.js'),'utf8'),{window});
const tools=window.ZephyrVoiceTools;
const result=(text,final)=>Object.assign([{transcript:text}],{isFinal:final});
test('Settings validate stored values, clamp controls and reject unknown languages',()=>{
  const normalized=tools.normalize({rate:90,pitch:-1,volume:NaN,pauseMs:-100,autoSend:'yes',recognitionLanguage:'made-up',speechLanguage:'profile',voices:{'fr-FR':'voice',evil:'ignore'}});
  assert.equal(normalized.rate,1.4);assert.equal(normalized.pitch,.8);assert.equal(normalized.volume,1);assert.equal(normalized.pauseMs,900);assert.equal(normalized.autoSend,true);assert.equal(normalized.recognitionLanguage,'fr-FR');assert.equal(normalized.speechLanguage,'profile');assert.deepEqual(Object.keys(normalized.voices),['fr-FR']);
});
test('Profile language resolves explicitly with a French fallback for unsupported profiles',()=>{
  assert.equal(tools.resolve('profile','en-GB'),'en-GB');assert.equal(tools.resolve('profile','unknown'),'fr-FR');assert.equal(tools.resolve('es-ES','en-GB'),'es-ES');
});
test('Revised result lists replace interim words instead of appending duplicates',()=>{
  assert.equal(tools.transcript([result('Bon',false)]).text,'Bon');
  const revision=tools.transcript([result('Bonjour',true),result('le mon',false)]);
  assert.equal(revision.final,'Bonjour');assert.equal(revision.interim,'le mon');
  const confirmed=tools.transcript([result('Bonjour',true),result('le monde',true)]);
  assert.equal(confirmed.text,'Bonjour le monde');assert.equal(confirmed.interim,'');
  assert.equal(tools.transcript([result('Bonjour',true)]).text,'Bonjour');
});
test('Only confirmed, error-free transcripts can be sent automatically',()=>{
  assert.equal(tools.shouldAutoSend({final:'Bonjour',interim:'',error:null},true),true);
  for(const snapshot of [{final:'',interim:'Bonjour'},{final:'Bonjour',interim:'le mon'},{final:'Bonjour',interim:'',error:'network'}])assert.equal(tools.shouldAutoSend(snapshot,true),false);
  assert.equal(tools.shouldAutoSend({final:'Bonjour',interim:''},false),false);
});
test('Speech chunking preserves words and bounds long responses',()=>{
  const input=('Bonjour le monde. Prenons le temps d’apprendre ensemble ! ').repeat(30).trim();
  const parts=tools.chunks(input);assert.ok(parts.length>1);assert.ok(parts.every(part=>part.length<=230));assert.equal(parts.join(' '),input);
  const unbroken='x'.repeat(600);assert.equal(tools.chunks(unbroken).join(''),unbroken);
});

test('Typed drafts are preserved while provisional speech remains marked as provisional',()=>{
  const combined=tools.combineTranscript('Mon brouillon', {final:'bonjour',interim:'le mon'});
  assert.equal(combined.final,'Mon brouillon bonjour');assert.equal(combined.interim,'le mon');assert.equal(combined.text,'Mon brouillon bonjour le mon');
});
