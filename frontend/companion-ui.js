'use strict';
window.ZephyrCompanionUI=function(){
  const panel=document.createElement('section');panel.id='companion-panel';panel.className='companion-panel';panel.hidden=true;panel.setAttribute('aria-label','Caméra locale');
  panel.innerHTML=`<div class="companion-top"><span class="tag">VOTRE CAMÉRA</span><button type="button" id="companion-close" aria-label="Masquer la caméra">×</button></div><div class="companion-grid camera-only"><div class="companion-camera"><video id="local-camera" autoplay playsinline muted aria-label="Aperçu local de votre caméra" hidden></video><div id="camera-placeholder"><span aria-hidden="true">◉</span><p>Votre caméra, à votre rythme</p></div><span class="camera-badge" id="camera-badge">CAMÉRA ARRÊTÉE</span></div></div><div class="companion-controls"><button type="button" class="learning-secondary" id="camera-toggle">Activer ma caméra</button><button type="button" class="learning-secondary" id="avatar-example">Écouter Zéphyr</button></div><p id="camera-status" class="learning-help" role="status">Aperçu local uniquement. Aucune image enregistrée ou envoyée.</p>`;
  document.querySelector('.voice-actions').after(panel);const $=id=>panel.querySelector('#'+id),trigger=document.getElementById('open-companion');
  let cameraState='off';const errors={'NotAllowedError':'Accès caméra refusé. Vérifiez les autorisations du navigateur.','NotFoundError':'Aucune caméra détectée.','NotReadableError':'Caméra déjà utilisée ou indisponible.','unavailable':'La caméra nécessite localhost ou HTTPS et un navigateur compatible.','ended':'La caméra a été déconnectée ou son autorisation retirée.'};
  const camera=window.ZephyrCameraController({mediaDevices:navigator.mediaDevices,
    onStream:stream=>{const video=$('local-camera');video.srcObject=stream;video.hidden=!stream;$('camera-placeholder').hidden=!!stream;if(stream)video.play().catch(()=>{$('camera-status').textContent='La caméra est active. Si l’aperçu ne démarre pas, arrêtez puis réactivez-la.';});},
    onState:state=>{cameraState=state;$('camera-toggle').textContent=state==='off'?'Activer ma caméra':state==='starting'?'Annuler l’activation':'Arrêter ma caméra';$('camera-toggle').setAttribute('aria-pressed',String(state==='on'));$('camera-badge').textContent=state==='on'?'APERÇU LOCAL · ACTIF':state==='starting'?'AUTORISATION…':'CAMÉRA ARRÊTÉE';$('camera-status').textContent=state==='starting'?'Autorisez la caméra si le navigateur le demande.':state==='on'?'Caméra active sur cet appareil. Aucun enregistrement ni envoi d’images.':'Caméra arrêtée. L’avatar reste disponible avec le vocal.';},
    onError:reason=>{$('camera-status').textContent=errors[reason]||'Impossible d’activer la caméra. Le vocal reste disponible.';},
  });
  function hide(){camera.stop();panel.hidden=true;trigger.setAttribute('aria-expanded','false');}
  trigger.addEventListener('click',()=>{if(!panel.hidden){hide();return;}panel.hidden=false;trigger.setAttribute('aria-expanded','true');updateState(document.body.dataset.voiceState||'idle');});
  $('companion-close').addEventListener('click',hide);
  $('camera-toggle').addEventListener('click',()=>{if(cameraState==='off')camera.start();else camera.stop();});
  $('avatar-example').addEventListener('click',()=>document.getElementById('demo').click());
  function updateState(state){panel.dataset.state=state;}
  document.addEventListener('visibilitychange',()=>{if(document.hidden)camera.stop();});window.addEventListener('pagehide',()=>camera.stop());document.getElementById('account-button').addEventListener('click',()=>camera.stop());
  return {updateState,stop:()=>camera.stop()};
};
