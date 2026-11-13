'use strict';
// Counts silence and waits for the recognizer's confirmed result before sending.
window.ZephyrDictationApproval=function({onTick,onSend,canSend,now=Date.now,schedule=setTimeout,cancelTimer=clearTimeout,delay=5000}){
  let deadline=null,timer=null,candidate=null,epoch=0;
  function clear(){epoch++;if(timer!==null)cancelTimer(timer);timer=null;}
  function tick(){
    clear();if(deadline===null)return;
    const remaining=Math.max(0,deadline-now());onTick(Math.ceil(remaining/1000));
    if(remaining===0){if(candidate!==null){const text=candidate;candidate=null;deadline=null;onTick(null);if(canSend(text))onSend(text);}return;}
    const token=epoch;timer=schedule(()=>{if(token!==epoch)return;timer=null;tick();},Math.min(200,remaining));
  }
  return {
    activity(){candidate=null;deadline=now()+delay;tick();},
    wait(){clear();candidate=null;deadline=null;onTick(null);},
    arm(text){candidate=text;if(deadline===null)deadline=now()+delay;tick();},
    cancel(){clear();candidate=null;deadline=null;onTick(null);},
    get pending(){return deadline!==null;}
  };
};
