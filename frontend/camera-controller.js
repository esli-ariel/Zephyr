'use strict';
window.ZephyrCameraController=function({mediaDevices,onStream,onState,onError}){
  let stream=null,pending=false,token=0;
  function stop(){token++;pending=false;const old=stream;stream=null;old?.getTracks().forEach(track=>{track.onended=null;track.stop();});onStream(null);onState('off');}
  async function start(){
    if(stream||pending)return;
    if(!mediaDevices?.getUserMedia){onError('unavailable');return;}
    pending=true;const attempt=++token;onState('starting');
    try{
      const acquired=await mediaDevices.getUserMedia({audio:false,video:{facingMode:'user',width:{ideal:640},height:{ideal:480}}});
      if(attempt!==token){acquired.getTracks().forEach(track=>track.stop());return;}
      stream=acquired;pending=false;for(const track of stream.getTracks())track.onended=()=>{stop();onError('ended');};
      onStream(stream);onState('on');
    }catch(error){if(attempt!==token)return;stop();onError(error.name||'unknown');}
  }
  return {start,stop,get active(){return !!stream||pending;}};
};
