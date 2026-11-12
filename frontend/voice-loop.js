'use strict';
// Explicit opt-in, no stored preference and no background polling of the microphone.
window.ZephyrVoiceLoop=function({canListen,listen,onChange,schedule=setTimeout,cancel=clearTimeout,delay=650}){
  let enabled=false,timer=null;
  function clear(){if(timer!==null){cancel(timer);timer=null;}}
  function queue(){clear();if(!enabled)return;timer=schedule(()=>{timer=null;if(enabled&&canListen())listen();},delay);}
  function disable(){clear();if(!enabled)return;enabled=false;onChange(false);}
  return {get enabled(){return enabled;},enable(){if(enabled)return;enabled=true;onChange(true);queue();},disable,schedule:queue};
};
