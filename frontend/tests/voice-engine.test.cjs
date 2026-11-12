const {test}=require('node:test');
const assert=require('node:assert/strict');
const {readFileSync}=require('node:fs');
const {runInNewContext}=require('node:vm');
const {join}=require('node:path');
const window={};for(const name of ['voice-tools.js','voice-engine.js'])runInNewContext(readFileSync(join(__dirname,'../'+name),'utf8'),{window,Uint8Array});
function fixture(options={}){
  const states=[],results=[],previews=[],errors=[],recognizers=[],spoken=[],timers=new Map();let timerId=0,stops=0,mediaCalls=0,cancels=0;
  class Recognition{constructor(){recognizers.push(this);}start(){this.onstart?.();}stop(){this.stopped=true;}abort(){this.aborted=true;}}
  const stream={getTracks:()=>[{stop:()=>stops++}]};
  const mediaDevices={getUserMedia:()=>{mediaCalls++;return options.media?options.media():Promise.resolve(stream);}};
  const synth={speak:utterance=>spoken.push(utterance),cancel:()=>cancels++};
  class Utterance{constructor(text){this.text=text;}}
  const engine=window.ZephyrVoiceEngine({Recognition,mediaDevices,AudioContext:options.AudioContext,synth,Utterance,settings:()=>({recognitionLanguage:'en-GB',pauseMs:2100}),onState:value=>states.push(value),onTranscript:value=>previews.push(value),onResult:value=>results.push(value),onError:value=>errors.push(value),schedule:(fn,delay)=>{timers.set(++timerId,{fn,delay});return timerId;},cancelTimer:id=>timers.delete(id)});
  return {engine,states,results,previews,errors,recognizers,spoken,timers,stream,get stops(){return stops;},get mediaCalls(){return mediaCalls;},get cancels(){return cancels;},fire(delay){const found=[...timers.entries()].find(([,timer])=>timer.delay===delay);assert.ok(found);timers.delete(found[0]);found[1].fn();}};
}
const result=(text,final)=>Object.assign([{transcript:text}],{isFinal:final});
const emit=(recognizer,...results)=>recognizer.onresult({results});
const speechOptions={lang:'en-GB',rate:.9,pitch:1.1,volume:.7,voice:{voiceURI:'test'}};
test('Capture uses the requested language and releases every track on completion',async()=>{
  const f=fixture();await f.engine.start();const rec=f.recognizers[0];assert.equal(rec.lang,'en-GB');assert.equal(rec.continuous,true);assert.equal(rec.interimResults,true);
  emit(rec,result('Hello',true),result('world',false));emit(rec,result('Hello',true),result('world',true));rec.onend();
  assert.equal(f.results[0].text,'Hello world');assert.equal(f.results[0].interim,'');assert.equal(f.stops,1);assert.equal(f.engine.capturing,false);
});
test('Manual stop waits for the last final words instead of aborting immediately',async()=>{
  const f=fixture();await f.engine.start();const rec=f.recognizers[0];emit(rec,result('Last wor',false));f.engine.finish();assert.equal(rec.stopped,true);assert.equal(rec.aborted,undefined);assert.equal(f.stops,0);
  emit(rec,result('Last words',true));rec.onend();assert.equal(f.results[0].final,'Last words');assert.equal(f.results[0].manual,true);assert.equal(f.stops,1);
});
test('A cancelled permission request cannot leave a microphone open later',async()=>{
  let resolve;const f=fixture({media:()=>new Promise(done=>resolve=done)});const start=f.engine.start();f.engine.cancel();resolve(f.stream);await start;
  assert.equal(f.stops,1);assert.equal(f.recognizers.length,0);assert.equal(f.results.length,0);
});
test('Late events after cancellation cannot send a transcript',async()=>{
  const f=fixture();await f.engine.start();const rec=f.recognizers[0],lateResult=rec.onresult,lateEnd=rec.onend;f.engine.cancel();lateResult({results:[result('late text',true)]});lateEnd();assert.equal(f.results.length,0);assert.equal(f.engine.capturing,false);
});
test('The configured pause asks the recognizer to finalize, with a bounded fallback',async()=>{
  const f=fixture();await f.engine.start();const rec=f.recognizers[0];emit(rec,result('Hello',true));f.fire(2100);assert.equal(rec.stopped,true);f.fire(1800);assert.equal(f.results.length,1);assert.equal(f.results[0].text,'Hello');assert.equal(f.stops,1);
});
test('Capture errors preserve received text for review and release the microphone',async()=>{
  const f=fixture();await f.engine.start();const rec=f.recognizers[0];emit(rec,result('Received words',true));rec.onerror({error:'network'});assert.deepEqual(f.errors,['network']);assert.equal(f.results[0].final,'Received words');assert.equal(f.results[0].error,'network');assert.equal(f.stops,1);
});
test('Speech is chunked, keeps its settings and stays pending until the last chunk',()=>{
  const f=fixture();f.engine.speak('A sentence to read. '.repeat(40),speechOptions);assert.equal(f.spoken.length,1);assert.equal(f.engine.speechPending,true);assert.equal(f.spoken[0].lang,'en-GB');assert.equal(f.spoken[0].rate,.9);assert.equal(f.spoken[0].volume,.7);
  let count=0;while(f.engine.speechPending&&count<30){const utterance=f.spoken.at(-1);utterance.onstart();utterance.onend();count++;}assert.ok(count>1);assert.equal(f.engine.speechPending,false);assert.equal(f.states.at(-1),'idle');assert.equal(f.mediaCalls,0);
});
test('Stopping speech invalidates late events and does not queue another chunk',()=>{
  const f=fixture();f.engine.speak('Some text. '.repeat(50),speechOptions);const late=f.spoken[0].onend;f.engine.silence();late();assert.equal(f.spoken.length,1);assert.equal(f.engine.speechPending,false);assert.equal(f.timers.size,0);
});
test('A stalled speech engine is cancelled instead of blocking the voice loop forever',()=>{
  const f=fixture();f.engine.speak('Hello',speechOptions);f.fire(20000);assert.equal(f.engine.speechPending,false);assert.deepEqual(f.errors,['synthesis-timeout']);assert.equal(f.states.at(-1),'idle');
});
test('A suspended optional analyser does not prevent the recognizer from starting',async()=>{
  class AudioContext{resume(){return new Promise(()=>{});}createAnalyser(){return {fftSize:512,getByteTimeDomainData:array=>array.fill(128)};}createMediaStreamSource(){return {connect(){}};}close(){return Promise.resolve();}}
  const f=fixture({AudioContext});await f.engine.start();assert.equal(f.recognizers.length,1);assert.equal(f.states.at(-1),'listening');assert.equal(f.engine.level(),0);f.engine.cancel();assert.equal(f.stops,1);
});
