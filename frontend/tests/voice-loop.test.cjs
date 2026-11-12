const {test}=require('node:test');
const assert=require('node:assert/strict');
const {readFileSync}=require('node:fs');
const {runInNewContext}=require('node:vm');
const {join}=require('node:path');
const window={};runInNewContext(readFileSync(join(__dirname,'../voice-loop.js'),'utf8'),{window});
function fixture(){let allowed=true,calls=0,next=0;const timers=new Map(),changes=[];
  const loop=window.ZephyrVoiceLoop({canListen:()=>allowed,listen:()=>calls++,onChange:value=>changes.push(value),schedule:fn=>{timers.set(++next,fn);return next;},cancel:id=>timers.delete(id)});
  return {loop,timers,changes,get calls(){return calls;},allow:value=>allowed=value,flush(){const callbacks=[...timers.values()];timers.clear();callbacks.forEach(fn=>fn());}};
}
test('No microphone use before opt-in; explicit enable schedules once',()=>{const f=fixture();f.loop.schedule();f.flush();assert.equal(f.calls,0);f.loop.enable();f.loop.enable();assert.equal(f.timers.size,1);f.flush();assert.equal(f.calls,1);assert.deepEqual(f.changes,[true]);});
test('Disabling cancels queued listening and prevents any later restart',()=>{const f=fixture();f.loop.enable();f.loop.disable();f.loop.schedule();f.flush();assert.equal(f.calls,0);assert.equal(f.loop.enabled,false);assert.deepEqual(f.changes,[true,false]);});
test('Busy/speaking/signed-out states block capture until a fresh idle notification',()=>{const f=fixture();f.allow(false);f.loop.enable();f.flush();assert.equal(f.calls,0);assert.equal(f.timers.size,0);f.allow(true);f.loop.schedule();f.loop.schedule();f.flush();assert.equal(f.calls,1);assert.equal(f.timers.size,0);});
