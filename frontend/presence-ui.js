'use strict';
window.ZephyrPresenceMode={normalize:value=>value==='humanoid'?'humanoid':'points'};
window.ZephyrPresenceUI=function({stage,vocabulary,onChange}){
  const key='zephyr.visualMode';let mode='points',renderer=null,lastSync='';
  try{mode=window.ZephyrPresenceMode.normalize(localStorage.getItem(key));}catch{}
  const controls=document.createElement('div');controls.className='presence-switch';controls.setAttribute('role','group');controls.setAttribute('aria-label','Apparence de Zéphyr');
  controls.innerHTML='<button type="button" data-presence="points" aria-pressed="true">Points</button><button type="button" data-presence="humanoid" aria-pressed="false">Avatar humanoïde</button>';
  document.querySelector('.voice-actions').before(controls);
  const fallback=document.createElement('div');fallback.className='humanoid-fallback';fallback.setAttribute('aria-hidden','true');
  fallback.innerHTML=`<svg viewBox="0 0 300 340" fill="none"><defs><radialGradient id="holo-fill"><stop stop-color="currentColor" stop-opacity=".10"/><stop offset="1" stop-color="currentColor" stop-opacity=".02"/></radialGradient></defs><g class="human-bust" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"><path d="M97 106C94 64 111 35 150 35s56 29 53 71l-5 44c-6 30-25 52-48 54-23-2-42-24-48-54Z" fill="url(#holo-fill)"/><path d="M130 194v22c-27 17-71 22-80 58l-7 39h214l-7-39c-9-36-53-41-80-58v-22" fill="url(#holo-fill)"/><path d="M99 112q51-18 102 0M102 145q48-13 96 0M111 173q39-8 78 0M150 35v68m-38-54q-16 65 3 134m73-134q16 65-3 134M67 251q83 44 166 0M49 285q101 31 202 0M150 219v90" opacity=".22"/><g class="human-eyes"><path d="M114 123q12-9 25 0-13 8-25 0m47 0q12-9 25 0-13 8-25 0"/><path d="m114 112 25-3m22 0 25 3"/></g><path d="m150 122-6 27 10 3m-18 21q14-6 28 0"/><ellipse class="human-mouth" cx="150" cy="176" rx="14" ry="2"/><ellipse cx="150" cy="320" rx="87" ry="9" opacity=".3"/></g></svg>`;
  stage.append(fallback);
  function sync(){const next=mode+'|'+!!renderer?.ready;if(lastSync===next)return;lastSync=next;document.body.dataset.visualMode=mode;stage.classList.toggle('webgl-ready',!!renderer?.ready);stage.dataset.renderer=renderer?.ready?'webgl':'canvas';fallback.hidden=mode!=='humanoid'||!!renderer?.ready;for(const button of controls.querySelectorAll('button'))button.setAttribute('aria-pressed',String(button.dataset.presence===mode));}
  controls.addEventListener('click',event=>{const button=event.target.closest('[data-presence]');if(!button)return;mode=window.ZephyrPresenceMode.normalize(button.dataset.presence);try{localStorage.setItem(key,mode);}catch{}sync();onChange(mode);});sync();
  import('/ui/presence-3d.mjs?v=0.8.9-hologram').then(module=>{try{renderer=module.createPresenceScene({stage,vocabulary,onReady:sync,onUnavailable:sync});sync();}catch{sync();}}).catch(()=>sync());
  window.addEventListener('pagehide',event=>{if(!event.persisted)renderer?.dispose();});
  return {get mode(){return mode;},render(frame){sync();if(renderer?.ready)return renderer.render({...frame,mode});if(mode==='humanoid'){fallback.dataset.state=frame.state;fallback.style.setProperty('--mouth-open',frame.state==='speaking'?String(1+frame.volume*3):'1');return true;}return false;}};
};
