'use strict';
window.ZephyrVoiceSettings=function({synth,mediaDevices,AudioContext,Recognition,onOpen,onClose,onSample,onStopSpeech}){
  const tools=window.ZephyrVoiceTools,key='zephyr.voicePreferences';let settings;
  try{settings=tools.normalize(JSON.parse(localStorage.getItem(key)||'null'));}catch{settings=tools.normalize(null);}
  let profileLanguage=null,meterStream=null,meterContext=null,meterFrame=null,meterTimeout=null,testToken=0;
  const dialog=document.createElement('dialog');dialog.id='voice-settings-dialog';dialog.className='learning-dialog voice-settings-dialog';dialog.setAttribute('aria-labelledby','voice-settings-title');
  dialog.innerHTML=`<header class="learning-header"><div><span class="tag">PARLONS NATURELLEMENT</span><h2 id="voice-settings-title">Voix et transcription</h2></div><button type="button" id="voice-settings-close" class="voice-close" aria-label="Fermer les réglages vocaux">×</button></header>
  <div class="voice-capabilities"><span id="recognition-capability"></span><span id="synthesis-capability"></span></div><p id="voice-settings-status" class="learning-status" role="status"></p>
  <section class="voice-setting-section"><h3>Votre voix → texte</h3><p class="learning-help">Choisissez la langue que vous allez parler. Les mots provisoires restent visibles jusqu’à leur confirmation.</p><label for="recognition-language">Langue de transcription</label><select id="recognition-language"></select>
  <label for="voice-pause">Pause avant de terminer la dictée <output id="voice-pause-value"></output></label><input id="voice-pause" type="range" min="900" max="3500" step="100">
  <label class="voice-checkbox"><input id="voice-auto-send" type="checkbox"><span>Envoyer automatiquement la dictée confirmée</span></label><p class="learning-help">Désactivez pour relire et modifier le texte avant l’envoi. Le mode continu attend alors votre validation.</p></section>
  <section class="voice-setting-section"><h3>Les réponses de Zéphyr</h3><label for="speech-language">Langue de lecture</label><select id="speech-language"></select><p class="learning-help">Ce choix règle la prononciation ; il ne traduit pas le message.</p><label for="speech-voice">Voix disponible sur cet appareil</label><select id="speech-voice"></select><p id="voice-availability" class="learning-help"></p>
  <div class="voice-slider-grid"><div><label for="speech-rate">Vitesse <output id="speech-rate-value"></output></label><input id="speech-rate" type="range" min="0.7" max="1.4" step="0.05"></div><div><label for="speech-volume">Volume <output id="speech-volume-value"></output></label><input id="speech-volume" type="range" min="0" max="1" step="0.05"></div></div>
  <label for="speech-pitch">Tonalité <output id="speech-pitch-value"></output></label><input id="speech-pitch" type="range" min="0.8" max="1.2" step="0.05"><div><button type="button" id="voice-sample" class="learning-secondary">Écouter un exemple</button><button type="button" id="voice-sample-stop" class="learning-secondary" disabled>Arrêter la lecture</button></div></section>
  <section class="voice-setting-section"><h3>Vérifier le microphone</h3><p id="microphone-device" class="learning-help">Microphone configuré dans votre navigateur.</p><meter id="microphone-level" min="0" max="1" value="0" aria-label="Niveau du microphone"></meter><div><button type="button" id="microphone-test" class="learning-secondary">Tester mon micro</button><button type="button" id="microphone-test-stop" class="learning-secondary" hidden>Arrêter le test</button></div><p class="learning-help">Ce test mesure le volume sans transcrire ni envoyer de son à Zéphyr. Pour changer de microphone, utilisez les autorisations de votre navigateur.</p></section>
  <p class="learning-help">Les réglages sont enregistrés sur ce navigateur. La dictée peut utiliser un service distant du navigateur. Le micro ne s’active jamais au chargement.</p><div class="voice-settings-footer"><button type="button" id="voice-reset" class="learning-secondary">Réglages par défaut</button><button type="button" id="voice-settings-done" class="learning-primary">Terminé</button></div>`;
  document.body.append(dialog);const $=id=>dialog.querySelector('#'+id);
  const localeOptions=()=>{const fragment=document.createDocumentFragment();let option=document.createElement('option');option.value='profile';option.textContent='Langue étudiée non renseignée — français utilisé';fragment.append(option);for(const [code,value] of Object.entries(tools.locales)){option=document.createElement('option');option.value=code;option.textContent=value.label;fragment.append(option);}return fragment;};
  $('recognition-language').append(localeOptions());$('speech-language').append(localeOptions());
  $('recognition-capability').textContent=Recognition?'Dictée disponible':'Dictée indisponible ici';$('synthesis-capability').textContent=synth?'Lecture vocale disponible':'Lecture vocale indisponible';
  function status(value,error=false){$('voice-settings-status').textContent=value;$('voice-settings-status').classList.toggle('error',error);}
  function persist(){try{localStorage.setItem(key,JSON.stringify(settings));status('Réglages enregistrés.');}catch{status('Réglages actifs pour cette session ; stockage du navigateur indisponible.');}}
  function resolved(which){return tools.resolve(settings[which],profileLanguage);}
  function availableVoices(){return (synth?.getVoices()||[]).filter(voice=>voice.lang.split('-')[0].toLowerCase()===resolved('speechLanguage').split('-')[0].toLowerCase());}
  function renderVoices(){
    const language=resolved('speechLanguage'),voices=availableVoices(),select=$('speech-voice');select.replaceChildren();
    const automatic=document.createElement('option');automatic.value='';automatic.textContent='Voix recommandée du navigateur';select.append(automatic);
    for(const voice of voices){const option=document.createElement('option');option.value=voice.voiceURI;option.textContent=voice.name+' · '+voice.lang+(voice.localService?' · sur l’appareil':'');select.append(option);}
    const saved=settings.voices[language];select.value=voices.some(voice=>voice.voiceURI===saved)?saved:'';
    select.disabled=!synth||!voices.length;$('voice-sample').disabled=!synth;
    $('voice-availability').textContent=voices.length?voices.length+' voix disponible(s) en '+tools.locales[language].label.toLowerCase()+'.':synth?'Aucune voix spécifique chargée pour cette langue. Le navigateur choisira sa voix par défaut.':'La lecture vocale n’est pas proposée par ce navigateur.';
  }
  function values(){
    $('voice-pause-value').textContent=(settings.pauseMs/1000).toFixed(1)+' s';$('speech-rate-value').textContent=settings.rate.toFixed(2)+'×';$('speech-volume-value').textContent=Math.round(settings.volume*100)+' %';$('speech-pitch-value').textContent=settings.pitch.toFixed(2);
  }
  function render(){
    $('recognition-language').value=settings.recognitionLanguage;$('speech-language').value=settings.speechLanguage;
    $('voice-pause').value=settings.pauseMs;$('voice-auto-send').checked=settings.autoSend;$('speech-rate').value=settings.rate;$('speech-volume').value=settings.volume;$('speech-pitch').value=settings.pitch;
    values();renderVoices();
  }
  for(const [id,setting] of [['recognition-language','recognitionLanguage'],['speech-language','speechLanguage'],['voice-pause','pauseMs'],['speech-rate','rate'],['speech-volume','volume'],['speech-pitch','pitch'],['voice-auto-send','autoSend']]){
    $(id).addEventListener(id.includes('language')||id==='voice-auto-send'?'change':'input',()=>{
      settings=tools.normalize({...settings,[setting]:id==='voice-auto-send'?$(id).checked:id.includes('language')?$(id).value:Number($(id).value)});values();if(id==='speech-language')renderVoices();persist();
    });
  }
  $('speech-voice').addEventListener('change',()=>{settings.voices[resolved('speechLanguage')]=$('speech-voice').value;persist();});
  synth?.addEventListener?.('voiceschanged',renderVoices);
  function stopTest(){
    testToken++;if(meterFrame!==null)cancelAnimationFrame(meterFrame);if(meterTimeout!==null)clearTimeout(meterTimeout);meterFrame=meterTimeout=null;
    meterStream?.getTracks().forEach(track=>track.stop());meterStream=null;if(meterContext)meterContext.close().catch(()=>{});meterContext=null;
    $('microphone-level').value=0;$('microphone-test-stop').hidden=true;$('microphone-test').disabled=false;
  }
  $('microphone-test').addEventListener('click',async()=>{
    if(!mediaDevices?.getUserMedia||!AudioContext){status('Le test du micro nécessite un navigateur compatible et localhost ou HTTPS.',true);return;}
    stopTest();onStopSpeech();const token=testToken;$('microphone-test').disabled=true;$('microphone-test-stop').hidden=false;status('Autorisez le microphone si le navigateur le demande.');
    try{
      const stream=await mediaDevices.getUserMedia({audio:{echoCancellation:true,noiseSuppression:true,autoGainControl:true},video:false});
      if(token!==testToken||!dialog.open){stream.getTracks().forEach(track=>track.stop());return;}
      meterStream=stream;meterContext=new AudioContext();meterContext.resume().catch(()=>{});if(token!==testToken||!dialog.open)return;
      const analyser=meterContext.createAnalyser();analyser.fftSize=512;meterContext.createMediaStreamSource(stream).connect(analyser);const data=new Uint8Array(analyser.fftSize);
      const track=stream.getAudioTracks()[0];$('microphone-device').textContent='Microphone : '+(track?.label||'microphone par défaut');$('microphone-test-stop').hidden=false;
      status('Parlez : la jauge doit bouger. Le test s’arrête automatiquement après 30 secondes.');
      function meter(){if(token!==testToken)return;analyser.getByteTimeDomainData(data);let sum=0;for(const value of data)sum+=((value-128)/128)**2;$('microphone-level').value=Math.min(1,Math.sqrt(sum/data.length)*6);meterFrame=requestAnimationFrame(meter);}
      meter();meterTimeout=setTimeout(()=>{if(token===testToken){stopTest();status('Test du micro terminé.');}},30000);
    }catch(error){if(token!==testToken)return;stopTest();status(error.name==='NotAllowedError'?'Accès au micro refusé. Autorisez-le dans les réglages du navigateur.':'Microphone indisponible. Vérifiez le périphérique et les autorisations.',true);}
  });
  $('microphone-test-stop').addEventListener('click',()=>{stopTest();status('Test du micro arrêté.');});
  $('voice-sample').addEventListener('click',()=>{stopTest();const lang=resolved('speechLanguage');status('Exemple de lecture en '+tools.locales[lang].label.toLowerCase()+'.');onSample(tools.locales[lang].sample,lang);});
  $('voice-sample-stop').addEventListener('click',()=>{onStopSpeech();status('Lecture arrêtée.');});
  $('voice-reset').addEventListener('click',()=>{stopTest();settings=tools.normalize(null);render();persist();});
  for(const id of ['voice-settings-close','voice-settings-done'])$(id).addEventListener('click',()=>dialog.close());
  dialog.addEventListener('close',()=>{stopTest();onClose();});
  document.getElementById('open-voice-settings').addEventListener('click',()=>{onOpen();status('');render();dialog.showModal();});
  function stopForVisibility(){if(document.hidden){stopTest();if(dialog.open)status('Test suspendu : l’onglet est passé en arrière-plan.');}}
  document.addEventListener('visibilitychange',stopForVisibility);window.addEventListener('pagehide',stopTest);
  render();
  return {get capture(){return {...settings,recognitionLanguage:resolved('recognitionLanguage')};},get autoSend(){return settings.autoSend;},get open(){return dialog.open;},
    speechOptions(override){const lang=override||resolved('speechLanguage'),voices=synth?.getVoices()||[],saved=settings.voices[lang];const sameLanguage=voice=>voice.lang.split('-')[0].toLowerCase()===lang.split('-')[0].toLowerCase();const voice=voices.find(v=>v.voiceURI===saved&&sameLanguage(v))||voices.find(v=>v.lang===lang&&v.localService)||voices.find(v=>v.lang===lang)||voices.find(v=>sameLanguage(v)&&v.localService)||voices.find(sameLanguage);return {lang,voice,rate:settings.rate,pitch:settings.pitch,volume:settings.volume};},
    setSpeaking(value){$('voice-sample-stop').disabled=!value;},reportError(value){if(dialog.open)status(value,true);},setProfileLanguage(value){profileLanguage=value;for(const id of ['recognition-language','speech-language'])$(id).options[0].textContent=profileLanguage?'Langue étudiée : '+tools.locales[profileLanguage].label:'Langue étudiée non reconnue — français utilisé';renderVoices();},stopTest};
};
