'use strict';
(() => {
  const $ = id => document.getElementById(id);
  const ui = {mic:$('mic'),send:$('send'),input:$('message'),status:$('status'),notice:$('notice'),messages:$('messages'),draft:$('draft'),sound:$('sound'),stop:$('stop'),demo:$('demo')};
  const recognitionType = window.SpeechRecognition || window.webkitSpeechRecognition;
  const synth = window.speechSynthesis;
  const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
  let learnerId = null, ready = false, busy = false, listening = false, starting = false,learningLocked=false;
  let presence=null,profilePage=null,profileVisible=false,currentAccount=null,oralAnswer=null,learningUI=null,companion=null,voiceLoop=null,accountUI=null,voiceEngine=null,voiceSettings=null,voiceSettingsOpen=false,dictationPending=false,approvalBlocked=false,dictationApproval=null,captureLanguage='fr-FR',voiceOn=true;
  let mode = 'idle', volume = 0, boundaryAt = 0, speechStart = 0;
  let conversationStarted = false;
  function beginConversation(){
    if(conversationStarted)return;
    conversationStarted=true;
    document.body.classList.add('conversation-active');
  }
  const stored = key => { try { return localStorage.getItem(key); } catch { return null; } };
  const save = (key, value) => { try { localStorage.setItem(key,value); } catch {} };
  const vocabulary=window.ZephyrVocabulary;
  const objectDeck=vocabulary.createShuffleBag(vocabulary.objects.map((_,index)=>index));
  let objectLanguage=vocabulary.resolveLanguage(stored('zephyr.objectLanguage'))||'en';
  let unknownLanguage='',profileEpoch=0,idleTime=0,currentShapeIndex=objectDeck.next(),lastObjectCycle=0;
  let captionKey='',shapeSettledTime=0,lastGeometryShape=-1;
  function applyProfile(profile){
    profileEpoch++;profilePage?.updateSidebar(profile);
    const code=vocabulary.resolveLanguage(profile.target_language);
    voiceSettings?.setProfileLanguage(code?vocabulary.languages[code].speech:null);
    if(!profile.target_language){objectLanguage=vocabulary.resolveLanguage(stored('zephyr.objectLanguage'))||'en';unknownLanguage='';return;}
    objectLanguage=code;unknownLanguage=code?'':String(profile.target_language);
    if(code)save('zephyr.objectLanguage',code);
  }
  async function refreshProfile(){
    const epoch=profileEpoch;
    try{const profile=await request('/api/learner/profile');if(epoch===profileEpoch)applyProfile(profile);}catch{}
  }
  const systemTheme=matchMedia('(prefers-color-scheme: light)');
  function setTheme(theme,persist=false){
    document.documentElement.dataset.theme=theme;
    const day=theme==='day';
    $('theme-icon').textContent=day?'☾':'☀';
    $('theme-label').textContent=day?'Mode nuit':'Mode jour';
    $('theme-toggle').setAttribute('aria-label',day?'Activer le mode nuit':'Activer le mode jour');
    document.querySelector('meta[name="theme-color"]').content=day?'#f2f6f7':'#060d13';
    if(persist)save('zephyr.theme',theme);
  }
  setTheme(document.documentElement.dataset.theme==='day'?'day':'night');
  $('theme-toggle').addEventListener('click',()=>setTheme(document.documentElement.dataset.theme==='day'?'night':'day',true));
  systemTheme.addEventListener('change',event=>{if(!stored('zephyr.theme'))setTheme(event.matches?'day':'night');});
  function notice(text,error=false){ui.notice.textContent=text;ui.notice.classList.toggle('error',error);}
  function state(next){if(mode!=='idle'&&next==='idle')idleTime=0;mode=next;document.body.dataset.voiceState=next;companion?.updateState(next);ui.status.textContent={idle:'Prêt à vous écouter',listening:'Je vous écoute…',thinking:'Zéphyr prépare sa réponse…',speaking:'Zéphyr vous répond…'}[next];$('activity').textContent={idle:'EN VEILLE',listening:'ÉCOUTE ACTIVE',thinking:'RÉFLEXION',speaking:'TRANSMISSION'}[next];controls();if(next==='idle')voiceLoop?.schedule();}
  function controls(){
    $('continuous-voice').disabled=(!ready||!recognitionType||voiceSettingsOpen)&&!voiceLoop?.enabled;
    $('open-learning').disabled=!ready||busy||starting;
    $('sidebar-learning').disabled=!ready||busy||starting;
    $('open-daily-session').disabled=!ready||busy||starting;
    ui.send.disabled=!ready||busy||listening||starting||learningLocked||voiceSettingsOpen||profileVisible;
    ui.mic.disabled=!ready||busy||learningLocked||voiceSettingsOpen||profileVisible||!recognitionType;
    ui.demo.disabled=busy||learningLocked||voiceSettingsOpen;
    $('chat-recognition-language').disabled=listening||starting||busy||learningLocked||voiceSettingsOpen;
    $('dictation-send').disabled=!ready||busy||listening||starting||learningLocked||voiceSettingsOpen;
  }
  async function request(path,options={},identify=true){
    const response=await fetch(path,{...options,credentials:'same-origin',headers:{'X-Zephyr-Request':'1',...(options.body?{'Content-Type':'application/json'}:{}),...(identify?{'X-Learner-ID':learnerId}:{}),...options.headers},signal:AbortSignal.timeout(135000)});
    const data=await response.json();
    if(!response.ok){const error=new Error(typeof data.detail==='string'?data.detail:'La requête a échoué. Veuillez réessayer.');error.status=response.status;if(response.status===401&&identify){suspendVoice();ready=false;ui.messages.replaceChildren();ui.input.value='';location.reload();}throw error;}
    return data;
  }
  function append(role,text){
    beginConversation();
    const article=document.createElement('article');article.className=`message ${role==='user'?'user':'assistant'}`;
    const label=document.createElement('div');label.className='message-label';label.textContent=role==='user'?'VOUS':'ZÉPHYR';
    const time=document.createElement('span');time.textContent=new Date().toLocaleTimeString('fr-FR',{hour:'2-digit',minute:'2-digit'});label.append(time);
    const p=document.createElement('p');p.textContent=text;article.append(label,p);ui.messages.append(article);ui.messages.scrollTop=ui.messages.scrollHeight;
  }
  function renderTranscript(snapshot){
    $('dictation-panel').hidden=false;ui.draft.replaceChildren();
    if(snapshot.final)ui.draft.append(document.createTextNode(snapshot.final));
    if(snapshot.interim){const provisional=document.createElement('span');provisional.className='dictation-interim';provisional.textContent=(snapshot.final?' ':'')+snapshot.interim;ui.draft.append(provisional);}
    if(!snapshot.text)ui.draft.textContent='Parlez, votre transcription apparaîtra ici…';
    $('dictation-status').textContent=listening||starting?'Transcription en cours':'Dictée à relire';
    $('dictation-language').textContent=window.ZephyrVoiceTools.locales[captureLanguage]?.label||captureLanguage;
    $('dictation-actions').hidden=!dictationPending;if(listening||starting)ui.draft.scrollTop=ui.draft.scrollHeight;
  }
  function clearTranscript(){dictationApproval?.cancel();dictationPending=false;$('dictation-panel').hidden=true;ui.draft.replaceChildren();$('dictation-actions').hidden=true;}
  function preserveDictation(snapshot){
    if(!snapshot.text)return;
    const combined=window.ZephyrVoiceTools.combineTranscript(ui.input.value,snapshot);
    ui.input.value=combined.text;dictationPending=true;renderTranscript(combined);$('dictation-status').textContent='Dictée prête à relire';
    controls();
  }
  function silence(){voiceEngine?.silence();voiceSettings?.setSpeaking(false);ui.stop.hidden=true;if(mode==='speaking')state('idle');voiceLoop?.schedule();}
  function speak(text,language,preview=false){
    dictationApproval?.cancel();
    if((!voiceOn&&!preview)||((voiceSettingsOpen||profileVisible)&&!preview))return;
    if(listening||starting)stopMic(false);
    voiceEngine.speak(text,voiceSettings.speechOptions(language));voiceSettings.setSpeaking(voiceEngine.speechPending);
  }
  async function send(text){
    dictationApproval?.cancel();text=text.trim();if(!text||busy||!ready||listening||starting||learningLocked||voiceSettingsOpen)return;
    if(text.length>5000){notice('Le message est limité à 5 000 caractères. Relisez et raccourcissez votre texte.',true);return;}
    silence();busy=true;controls();state('thinking');$('suggestions')?.remove();append('user',text);ui.input.value='';ui.input.style.height='auto';clearTranscript();
    notice('Zéphyr réfléchit à votre message.');
    try{const data=await request('/api/chat',{method:'POST',body:JSON.stringify({message:text})});append('assistant',data.response);state('idle');notice('À vous. Continuez par écrit ou activez le microphone.');speak(data.response);refreshProfile();}
    catch(error){voiceLoop?.disable();state('idle');ui.input.value=text;notice(error.name==='TimeoutError'?'La réponse a pris trop de temps. Votre message est conservé pour réessayer.':error.message,true);}
    finally{busy=false;controls();voiceLoop?.schedule();}
  }
  function stopMic(submit=true){
    if(submit){notice('Finalisation de la dictée…');voiceEngine?.finish();}
    else{dictationApproval?.cancel();const snapshot=voiceEngine?.cancel();if(snapshot?.text)preserveDictation(snapshot);else if(!dictationPending)clearTranscript();}
  }
  function startMic(){
    if(learningLocked||voiceSettingsOpen||busy||!ready)return;
    if(starting){stopMic(false);notice('Activation du micro annulée.');return;}
    if(listening){stopMic(true);return;}
    if(dictationPending){notice('Envoyez ou effacez la dictée précédente avant d’en commencer une autre.');return;}
    captureLanguage=voiceSettings.capture.recognitionLanguage;approvalBlocked=false;dictationApproval.cancel();
    voiceEngine.start();
  }
  const voiceErrors={
    'recognition-unavailable':'La dictée n’est pas proposée par ce navigateur. Essayez un navigateur compatible, ou utilisez la saisie texte.',
    'microphone-unavailable':'Le micro nécessite localhost ou HTTPS et un navigateur compatible.',
    'not-allowed':'Accès au micro ou à la dictée refusé. Vérifiez les autorisations du navigateur.',
    'NotAllowedError':'Accès au microphone refusé. Autorisez-le dans les réglages du navigateur.',
    'NotFoundError':'Aucun microphone trouvé. Vérifiez le branchement et le micro choisi dans le navigateur.',
    'NotReadableError':'Le microphone est indisponible ou déjà utilisé. Fermez l’autre application et réessayez.',
    'audio-capture':'Le microphone ne peut pas être utilisé. Vérifiez le périphérique et ses autorisations.',
    'network':'Le service de transcription est indisponible. Vérifiez la connexion et réessayez.',
    'service-not-allowed':'Le service de dictée est bloqué dans ce navigateur. Vous pouvez continuer par écrit.',
    'language-not-supported':'Cette langue de dictée n’est pas prise en charge ici. Choisissez une autre langue dans les réglages vocaux.',
    'synthesis-unavailable':'La lecture vocale n’est pas disponible dans ce navigateur. Les réponses restent affichées.',
    'synthesis-not-allowed':'La lecture a été bloquée. Cliquez sur « Écouter un exemple » dans les réglages vocaux, puis réessayez.',
    'synthesis-timeout':'La lecture du navigateur s’est interrompue. Réessayez une voix différente ; la réponse reste affichée.',
    'synthesis-error':'La voix sélectionnée n’a pas pu être lue. Essayez une autre voix dans les réglages.',
  };
  const transcriptionLanguage=$('chat-recognition-language');
  for(const [value,label] of [['profile','Langue étudiée'],...Object.entries(window.ZephyrVoiceTools.locales).map(([key,item])=>[key,item.label])]){const option=document.createElement('option');option.value=value;option.textContent=label;transcriptionLanguage.append(option);}
  function syncTranscription(){transcriptionLanguage.value=voiceSettings.capture.recognitionPreference;$('chat-validation-mode').textContent=voiceSettings.autoSend?'Validation auto · 5 s':'Validation manuelle';}
  function keepForReview(){approvalBlocked=true;dictationApproval.cancel();$('dictation-status').textContent=listening?'Transcription en cours · validation manuelle':'Dictée prête à relire';notice('Envoi automatique annulé. Relisez le texte, puis envoyez-le quand vous êtes prêt.');}
  dictationApproval=window.ZephyrDictationApproval({
    onTick:seconds=>{$('dictation-validation').hidden=seconds===null;if(seconds!==null){const label=seconds===0?'Finalisation de la transcription…':'Validation automatique dans '+seconds+' s';if($('dictation-countdown').textContent!==label)$('dictation-countdown').textContent=label;}},
    canSend:text=>ready&&!busy&&!starting&&!listening&&!learningLocked&&!voiceSettingsOpen&&!profileVisible&&!document.hidden&&!voiceEngine.speechPending&&dictationPending&&ui.input.value===text,
    onSend:text=>send(text)
  });
  $('dictation-keep').addEventListener('click',keepForReview);
  transcriptionLanguage.addEventListener('change',()=>{if(dictationApproval.pending||dictationPending)keepForReview();voiceSettings.setRecognitionLanguage(transcriptionLanguage.value);notice('Langue de transcription : '+window.ZephyrVoiceTools.locales[voiceSettings.capture.recognitionLanguage].label+'.');});
  voiceSettings=window.ZephyrVoiceSettings({synth,Recognition:recognitionType,mediaDevices:navigator.mediaDevices,AudioContext:window.AudioContext||window.webkitAudioContext,
    onOpen:()=>{suspendVoice();voiceSettingsOpen=true;controls();},
    onClose:()=>{voiceSettingsOpen=false;silence();controls();},
    onChange:()=>{dictationApproval.cancel();syncTranscription();},
    onSample:(text,language)=>speak(text,language,true),onStopSpeech:silence,
  });
  syncTranscription();
  voiceEngine=window.ZephyrVoiceEngine({settings:()=>({...voiceSettings.capture,pauseMs:voiceSettings.autoSend&&!approvalBlocked?5000:voiceSettings.capture.pauseMs}),
    onActivity:talking=>{if(!voiceSettings.autoSend||approvalBlocked)return;if(talking)dictationApproval.wait();else dictationApproval.activity();},Recognition:recognitionType,mediaDevices:navigator.mediaDevices,AudioContext:window.AudioContext||window.webkitAudioContext,synth,Utterance:window.SpeechSynthesisUtterance,
    onState:next=>{
      voiceSettings.setSpeaking(next==='speaking');
      starting=next==='starting';listening=next==='listening';
      ui.mic.classList.toggle('active',listening);ui.mic.setAttribute('aria-pressed',String(listening));
      ui.mic.setAttribute('aria-label',starting?'Annuler l’activation du microphone':listening?'Terminer la dictée':'Activer le microphone');
      $('mic-hint').textContent=starting?'Activation du micro…':listening?'Cliquez pour terminer':'Cliquez pour parler';
      if(next==='starting'){renderTranscript({final:'',interim:'',text:''});notice('Activation du micro et de la dictée…');}
      else if(next==='listening'){beginConversation();state('listening');notice('Je vous écoute en '+window.ZephyrVoiceTools.locales[captureLanguage].label.toLowerCase()+'. La dictée peut utiliser le service du navigateur.');}
      else if(next==='speaking'){beginConversation();speechStart=performance.now();state('speaking');ui.stop.hidden=false;}
      else{ui.stop.hidden=true;if(!busy)state('idle');}
      controls();
    },
    onTranscript:renderTranscript,
    onResult:snapshot=>{
      if(!snapshot.text){if(!dictationPending)clearTranscript();if(!snapshot.error)notice('Aucune phrase détectée. Réessayez ou écrivez votre message.');return;}
      const auto=window.ZephyrVoiceTools.shouldAutoSend(snapshot,voiceSettings.autoSend&&!approvalBlocked);
      const text=window.ZephyrVoiceTools.combineTranscript(ui.input.value,snapshot).text;
      if(auto&&ready&&text.length<=5000){preserveDictation(snapshot);notice('La dictée est prête. Vous pouvez encore la relire.');dictationApproval.arm(ui.input.value);}
      else{dictationApproval.cancel();preserveDictation(snapshot);if(!snapshot.error)notice(text.length>5000?'La dictée dépasse 5 000 caractères. Modifiez le texte avant de l’envoyer.':snapshot.interim?'Une partie de la dictée est provisoire. Relisez le texte avant de l’envoyer.':'Relisez votre dictée, puis cliquez sur Envoyer.');}
    },
    onError:reason=>{if(reason!=='no-speech')voiceLoop?.disable();if(voiceSettingsOpen)voiceSettings.reportError(voiceErrors[reason]||'Le vocal est indisponible. Vérifiez les réglages.');notice(reason==='no-speech'?(voiceLoop?.enabled?'Aucune parole détectée. L’écoute va reprendre.':'Aucune parole détectée. Réessayez quand vous êtes prêt.'):voiceErrors[reason]||'Le vocal est indisponible. Vérifiez les réglages et continuez par écrit.',reason!=='no-speech');},
    onBoundary:()=>{boundaryAt=performance.now();},
  });
  ui.mic.addEventListener('click',startMic);
  $('composer').addEventListener('submit',event=>{event.preventDefault();send(ui.input.value);});
  $('dictation-send').addEventListener('click',()=>send(ui.input.value));
  $('dictation-cancel').addEventListener('click',()=>{ui.input.value='';clearTranscript();notice('Dictée effacée.');voiceLoop?.schedule();});
  ui.input.addEventListener('keydown',event=>{if(event.key==='Enter'&&!event.shiftKey&&!event.isComposing){event.preventDefault();send(ui.input.value);}});
  ui.input.addEventListener('input',()=>{if(dictationApproval.pending||dictationPending||listening||starting){approvalBlocked=true;dictationApproval.cancel();notice('Texte modifié : validation manuelle.');}ui.input.style.height='auto';ui.input.style.height=Math.min(ui.input.scrollHeight,120)+'px';if(dictationPending){if(ui.input.value.trim())renderTranscript({final:ui.input.value,interim:'',text:ui.input.value});else{clearTranscript();voiceLoop?.schedule();}}else voiceLoop?.schedule();});
  document.querySelectorAll('[data-prompt]').forEach(button=>button.addEventListener('click',()=>send(button.dataset.prompt)));
  ui.sound.addEventListener('click',()=>{voiceOn=!voiceOn;ui.sound.setAttribute('aria-pressed',String(voiceOn));ui.sound.textContent=voiceOn?'Voix activée ◖))':'Voix coupée';if(!voiceOn)silence();});
  ui.stop.addEventListener('click',silence);
  ui.demo.addEventListener('click',()=>{if(listening||starting)stopMic(false);const options=voiceSettings.speechOptions();speak(window.ZephyrVoiceTools.locales[options.lang].sample,options.lang,true);});
  function suspendVoice(){dictationApproval?.cancel();oralAnswer?.stop();companion?.stop();voiceLoop?.disable();stopMic(false);silence();voiceSettings?.stopTest();}
  voiceLoop=window.ZephyrVoiceLoop({
    canListen:()=>ready&&!profileVisible&&!busy&&!starting&&!listening&&!learningLocked&&!voiceSettingsOpen&&!dictationPending&&!ui.input.value.trim()&&!voiceEngine.speechPending&&mode==='idle'&&!document.hidden,
    listen:startMic,
    onChange:enabled=>{$('continuous-voice').setAttribute('aria-pressed',String(enabled));$('continuous-voice').setAttribute('aria-label',enabled?'Arrêter le mode vocal continu':'Activer le mode vocal continu');$('continuous-label').textContent=enabled?'Vocal continu actif':'Vocal continu';controls();},
  });
  $('continuous-voice').addEventListener('click',()=>{
    if(voiceLoop.enabled){voiceLoop.disable();stopMic(false);notice('Mode vocal continu arrêté. Votre dictée éventuelle est conservée.');return;}
    if(!ready)return;
    if(!recognitionType||!navigator.mediaDevices?.getUserMedia){notice(voiceErrors['recognition-unavailable'],true);return;}
    voiceLoop.enable();notice(dictationPending||ui.input.value.trim()?'Vocal continu activé. Envoyez ou effacez votre brouillon pour reprendre l’écoute.':'Vocal continu activé. L’écoute reprend après chaque réponse, sans enregistrer la voix de Zéphyr.');
  });
  window.addEventListener('pagehide',suspendVoice);
  document.addEventListener('visibilitychange',()=>{if(document.hidden)suspendVoice();});
  $('account-button').addEventListener('click',suspendVoice);
  accountUI=window.ZephyrAccountUI({request,onSignedIn:()=>location.reload(),onSignedOut:()=>{suspendVoice();try{localStorage.removeItem('zephyr.learnerId');}catch{}location.reload();}});
  oralAnswer=window.ZephyrOralAnswer({Recognition:recognitionType,createEngine:callbacks=>window.ZephyrVoiceEngine({...callbacks,Recognition:recognitionType,mediaDevices:navigator.mediaDevices,AudioContext:window.AudioContext||window.webkitAudioContext,synth,Utterance:window.SpeechSynthesisUtterance}),settings:()=>voiceSettings.capture,speechOptions:language=>voiceSettings.speechOptions(language),onState:next=>{if(next==='listening'||next==='speaking')beginConversation();if(next==='speaking')speechStart=performance.now();state(next==='starting'?'idle':next);},onBoundary:()=>{boundaryAt=performance.now();}});
  learningUI=window.ZephyrLearningUI({request,onProfile:applyProfile,resolveLanguage:vocabulary.resolveLanguage,oralAnswer,resolveSpeechLanguage:value=>{const code=vocabulary.resolveLanguage(value);return code?vocabulary.languages[code].speech:null;},
    isReady:()=>ready&&!busy&&!starting,
    suspend:suspendVoice,
    onLock:value=>{learningLocked=value;controls();if(!value){refreshDaily();profilePage?.refreshIfOpen();}},
  });
  let dailyEpoch=0;
  async function refreshDaily(){
    if(!ready)return;const epoch=++dailyEpoch;
    try{const data=await request('/api/learning/today?utc_offset_minutes='+(-new Date().getTimezoneOffset()));if(epoch!==dailyEpoch||!ready)return;
      $('daily-session-summary').textContent=data.reviews.due?data.reviews.due+(data.reviews.due===1?' révision à retrouver':' révisions à retrouver'):data.plan.next?'À suivre : '+data.plan.next.target:data.profile_ready?'Préparez votre prochaine séance.':'Choisissez votre langue et votre niveau.';
      $('daily-session').hidden=false;
    }catch{if(ready){$('daily-session-summary').textContent='Ouvrez votre séance pour actualiser la progression.';$('daily-session').hidden=false;}}
  }
  $('open-daily-session').addEventListener('click',()=>learningUI.open('today'));
  document.addEventListener('visibilitychange',()=>{if(!document.hidden&&!learningLocked)refreshDaily();});
  companion=window.ZephyrCompanionUI();
  profilePage=window.ZephyrProfilePage({request,isReady:()=>ready,getAccount:()=>currentAccount,onProfile:applyProfile,onAccount:()=>{suspendVoice();accountUI.show();},onLearning:section=>learningUI.open(section),onViewChange:visible=>{profileVisible=visible;if(visible){suspendVoice();learningUI.close();}controls();}});
  controls();
  async function initialize(){
    try{
      await request('/health',{},false);
      const session=await request('/api/auth/session',{},false);
      if(session.authentication_required){
        currentAccount=session.user;accountUI.setSession(session);learnerId=session.learner_id;
        applyProfile(await request('/api/learner/profile'));
      }else{
        accountUI.setLegacy();learnerId=stored('zephyr.learnerId');
        if(learnerId){try{applyProfile(await request('/api/learner/profile'));}catch(error){if(error.status===404||error.status===400)learnerId=null;else throw error;}}
        if(!learnerId){const data=await request('/api/learners',{method:'POST'},false);learnerId=data.learner_id;save('zephyr.learnerId',learnerId);applyProfile(await request('/api/learner/profile'));}
      }
      const memory=await request('/api/chat/memory');if(memory.messages?.length){ui.messages.replaceChildren();memory.messages.forEach(m=>append(m.role,m.content));}
      ready=true;$('connection').textContent='Zéphyr connecté';controls();refreshDaily();profilePage.refreshIfOpen();
    }catch(error){if(error.status===401){$('connection').textContent='Connexion requise';notice('Connectez-vous ou créez un compte pour retrouver votre apprentissage.');accountUI.show('login');return;}$('connection').textContent='API indisponible';$('connection-dot').classList.add('off');notice('Connexion impossible : '+error.message+' Rechargez la page pour réessayer. Vous pouvez essayer la voix et le micro.',true);}
  }
  initialize();
  // The microphone drives the field with RMS amplitude. Browser speech synthesis
  // exposes word boundaries, not PCM audio: its envelope is an animation, not a waveform.
  const canvas=$('orb'),ctx=canvas.getContext('2d');
  let width=0,height=0,lastFrame=0,rotation=0,motionTime=0,engagement=0,themeBlend=document.documentElement.dataset.theme==='day'?1:0;
  const feeling={listening:0,thinking:0,speaking:0};
  const points=Array.from({length:2100},(_,i)=>{
    const y=1-2*(i+.5)/2100,r=Math.sqrt(1-y*y),angle=i*2.399963229728653;
    return{x:r*Math.cos(angle),y,z:r*Math.sin(angle),freeX:Math.sin(i*71.17)*1.3,freeY:Math.cos(i*17.91)*.95,freeZ:Math.sin(i*31.7)*.55,position:null,size:.65+((i*.754877666)%1)*.65,spark:i%43===0,phase:i*.73,drifter:i%6===0,driftOffset:(i*.61803398875)%1};
  });
  const shapeCache=new Map();
  function fallbackShape(index){if(!shapeCache.has(index)){shapeCache.set(index,vocabulary.buildGeometry(vocabulary.objects[index].id,points.length));if(shapeCache.size>4)shapeCache.delete(shapeCache.keys().next().value);}return shapeCache.get(index);}
  presence=window.ZephyrPresenceUI({stage:canvas.parentElement,vocabulary,onChange:()=>{idleTime=0;lastObjectCycle=0;captionKey='';$('object-caption').hidden=true;}});
  function caption(show,index){
    if(presence?.mode==='humanoid'){if(captionKey!=='humanoid'){$('object-caption').hidden=true;canvas.setAttribute('aria-label','Avatar humanoïde de Zéphyr');captionKey='humanoid';}return;}
    const item=vocabulary.objects[index],key=[show,index,objectLanguage,unknownLanguage].join('|');if(key===captionKey)return;captionKey=key;
    $('object-caption').hidden=!show;
    $('object-french').textContent=item.fr;
    $('object-word').textContent=objectLanguage?item.words[objectLanguage]:'—';
    $('object-word').lang=objectLanguage||'fr';
    $('object-language').textContent=objectLanguage?vocabulary.languages[objectLanguage].name:'Traduction indisponible : '+unknownLanguage;
    canvas.setAttribute('aria-label',show?item.fr+(objectLanguage?' : '+item.words[objectLanguage]:'. Traduction indisponible : '+unknownLanguage)+'. Objet en trois dimensions.':'Nuage de points de Zéphyr.');
  }
  function resize(){
    const rect=canvas.getBoundingClientRect(),dpr=Math.min(devicePixelRatio||1,2);
    width=rect.width;height=rect.height;canvas.width=width*dpr;canvas.height=height*dpr;
    ctx.setTransform(dpr,0,0,dpr,0,0);
  }
  new ResizeObserver(resize).observe(canvas);resize();
  function draw(now){
    requestAnimationFrame(draw);
    if(document.hidden||profileVisible){lastFrame=now;return;}
    if(now-lastFrame<(reducedMotion.matches?90:30))return;
    const delta=Math.min((now-lastFrame)/1000,.06);lastFrame=now;
    let input=Math.min(1,Math.max(voiceEngine?.level()||0,oralAnswer?.level||0)*7);
    if(mode==='speaking'){
      const elapsed=(now-speechStart)/1000;
      input=.32+.48*Math.abs(Math.sin(elapsed*8.7)*Math.cos(elapsed*3.1))+.2*Math.exp(-(now-boundaryAt)/120);
    }
    volume+=(input-volume)*.2;
    // Blend state changes so shape, glow and colour settle together.
    for(const name of Object.keys(feeling))feeling[name]+=((mode===name?1:0)-feeling[name])*.08;
    engagement+=((conversationStarted?1:0)-engagement)*.06;
    const quiet=reducedMotion.matches;
    themeBlend+=((document.documentElement.dataset.theme==='day'?1:0)-themeBlend)*(quiet?1:.045);
    if(!quiet){rotation+=delta*(.10+engagement*.10+feeling.thinking*.55+feeling.speaking*.14+volume*.18);motionTime+=delta;}
    if(mode==='idle'){if(presence.mode==='points')idleTime=quiet?9:idleTime+delta;}else{idleTime=0;lastObjectCycle=0;}
    const cycle=Math.floor(idleTime/20);if(!quiet&&cycle>lastObjectCycle){currentShapeIndex=objectDeck.next();lastObjectCycle=cycle;}
    const phase=idleTime%20;
    const form=quiet?1:phase<5?0:phase<8?(phase-5)/3:phase<16?1:1-(phase-16)/4;
    const smoothForm=form*form*(3-2*form);
    const activeWeight=Math.min(1,feeling.speaking+feeling.thinking+feeling.listening);
    if(lastGeometryShape!==currentShapeIndex||mode!=='idle'||smoothForm<.98||activeWeight>=.03)shapeSettledTime=0;
    else shapeSettledTime+=delta;
    lastGeometryShape=currentShapeIndex;
    const objectClarity=smoothForm*(1-activeWeight);
    const showCaption=mode==='idle'&&smoothForm>.98&&activeWeight<.03&&(quiet||shapeSettledTime>.7);
    caption(showCaption,currentShapeIndex);
    document.body.dataset.pointScene=presence.mode==='humanoid'?'humanoid':mode==='idle'?(showCaption?'object':'wandering'):mode;
    const pulse=0,pulseAge=10;
    if(presence.render({width,height,delta,time:motionTime,theme:themeBlend,quiet,state:mode,volume,form:smoothForm,objectId:vocabulary.objects[currentShapeIndex].id,pulse:0,pointer:{x:0,y:0,strength:0}}))return;
    const model=fallbackShape(currentShapeIndex);
    const base=Math.min(width*(.32+engagement*.035),height*.34,154+engagement*65)*(.84+.16*engagement);
    const amp=quiet?volume*.018:.018+engagement*.025+feeling.listening*.07+feeling.speaking*.10+volume*.23;
    const breath=quiet?1:1+.025*Math.sin(motionTime*1.5)+feeling.speaking*(.035+volume*.10);
    const tilt=quiet?.15:.15+Math.sin(motionTime*.65)*(.04+engagement*.13);
    ctx.clearRect(0,0,width,height);
    const hue=187+(1-themeBlend)*12+Math.sin(motionTime*.19)*8+feeling.thinking*34+feeling.speaking*7;
    // Two radial gradients give depth without a blur filter on all 2 100 points.
    const auraRadius=base*(1.85+volume*.18);
    const aura=ctx.createRadialGradient(width/2,height/2,base*.20,width/2,height/2,auraRadius);
    const glow=(.065+engagement*.025+feeling.listening*.035+feeling.thinking*.035+feeling.speaking*.08+volume*.075)*(1-themeBlend*.50);
    aura.addColorStop(0,`hsla(${hue},75%,${55-themeBlend*20}%,${glow})`);
    aura.addColorStop(.48,`hsla(${hue},70%,${48-themeBlend*15}%,${glow*.6})`);
    aura.addColorStop(1,`hsla(${hue},70%,45%,0)`);
    ctx.fillStyle=aura;ctx.fillRect(0,0,width,height);
    const core=ctx.createRadialGradient(width/2-base*.12,height/2-base*.12,0,width/2,height/2,base*.95);
    core.addColorStop(0,`hsla(${hue},60%,${62-themeBlend*30}%,${.035+feeling.speaking*.035})`);
    core.addColorStop(1,`hsla(${hue},60%,45%,0)`);
    ctx.fillStyle=core;ctx.fillRect(0,0,width,height);
    const projected=points.map((p,index)=>{
      const wave=Math.sin(p.y*7+p.x*3+motionTime*4.3)*.65+Math.sin(p.z*6-motionTime*3.2)*.35;
      const thinking=quiet?0:feeling.thinking*.055*Math.sin(p.y*11-motionTime*5);
      const listeningWave=quiet?0:feeling.listening*(.025+volume*.20)*Math.sin(p.y*10-motionTime*4);
      const voiceWave=quiet?0:feeling.speaking*volume*.10*Math.sin(p.y*5+motionTime*7);
      const ripple=pulse*.35*Math.sin(p.y*4-pulseAge*10);
      // A fixed subset leaves the surface along staggered, reversible paths.
      // The smooth envelope starts and ends at zero: no spawning or disappearing dots.
      const cycle=(motionTime*.10+p.driftOffset)%1;
      const flight=p.drifter&&!quiet&&cycle<.65?Math.sin(cycle/.65*Math.PI)**2:0;
      const separation=flight*(.32+engagement*.27+volume*.22+pulse*.3);
      const wobble=breath+amp*wave+thinking+listeningWave+voiceWave+ripple+separation;
      const tangent=flight*.13*Math.sin(motionTime*1.2+p.phase);
      const swirl=rotation+(quiet?0:feeling.thinking*(p.y*1.55+.16*Math.sin(motionTime*.8)));
      const cy=Math.cos(swirl),sy=Math.sin(swirl);
      const x=(p.x*cy+p.z*sy)*wobble+tangent*p.z,y=p.y*wobble+tangent*p.x,z=(p.z*cy-p.x*sy)*wobble;
      const free={x:p.freeX+(!quiet?.10*Math.sin(motionTime*.7+p.phase):0),y:p.freeY+(!quiet?.09*Math.cos(motionTime*.5+p.phase):0),z:p.freeZ};
      const modelPoint=model[index];
      const objectYaw=quiet?.45:Math.sin(motionTime*.18)*.65-.20;
      const objectPitch=quiet?-.16:-.16+Math.sin(motionTime*.25)*.10;
      const ox=modelPoint.x*Math.cos(objectYaw)+modelPoint.z*Math.sin(objectYaw);
      const oz=modelPoint.z*Math.cos(objectYaw)-modelPoint.x*Math.sin(objectYaw);
      const shape={x:ox,y:modelPoint.y*Math.cos(objectPitch)-oz*Math.sin(objectPitch),z:modelPoint.y*Math.sin(objectPitch)+oz*Math.cos(objectPitch)};
      const idle={x:free.x*(1-smoothForm)+shape.x*smoothForm,y:free.y*(1-smoothForm)+shape.y*smoothForm,z:free.z*(1-smoothForm)+shape.z*smoothForm};
      const spiralAngle=p.driftOffset*Math.PI*2+motionTime*.8;
      const spiralRadius=.35+.60*((p.phase*.371)%1);
      const thinkingTarget={x:Math.cos(spiralAngle)*spiralRadius,y:Math.sin(spiralAngle)*spiralRadius*.72,z:Math.sin(p.phase+motionTime)*.3};
      const target={
        x:idle.x*(1+pulse*.18)*(1-activeWeight)+free.x*.75*feeling.listening+thinkingTarget.x*feeling.thinking+x*feeling.speaking,
        y:idle.y*(1+pulse*.18)*(1-activeWeight)+(free.y*.8+listeningWave)*feeling.listening+thinkingTarget.y*feeling.thinking+y*feeling.speaking,
        z:idle.z*(1-activeWeight)+free.z*feeling.listening+thinkingTarget.z*feeling.thinking+z*feeling.speaking,
      };
      if(!p.position)p.position={...target};
      const ease=quiet?1:1-Math.exp(-delta*(mode==='speaking'?8:4.2));
      for(const axis of ['x','y','z'])p.position[axis]+=(target[axis]-p.position[axis])*ease;
      const tiltWeight=feeling.speaking;
      const yy=p.position.y*Math.cos(tilt*tiltWeight)-p.position.z*Math.sin(tilt*tiltWeight),zz=p.position.y*Math.sin(tilt*tiltWeight)+p.position.z*Math.cos(tilt*tiltWeight);
      const perspective=2.8/(2.8-zz*.3);
      let px=width/2+p.position.x*base*perspective,py=height/2-12+yy*base*perspective;
      return{x:px,y:py,z:zz,influence:0,flight,tint:p.driftOffset,size:p.size,spark:p.spark,perspective};
    }).sort((a,b)=>a.z-b.z);
    ctx.globalCompositeOperation=themeBlend<.2?'lighter':'source-over';
    for(const p of projected){
      const depth=Math.max(0,Math.min(1,(p.z+1)/2));
      const alpha=Math.min(1,.24+Math.pow(depth,1.3)*.70+volume*.12+p.influence*.22+objectClarity*.22);
      const tint=hue+p.tint*10+p.flight*10;
      const lightness=(62+depth*27+objectClarity*5)*(1-themeBlend)+(23+depth*15)*themeBlend;
      const saturation=58-themeBlend*14+p.flight*8;
      const radius=(.48+depth*1.10)*p.size*p.perspective*(1+volume*.4+p.influence*.4+objectClarity*.18);
      if(p.spark&&depth>.6){
        ctx.fillStyle=`hsla(${tint},70%,${65-themeBlend*25}%,${alpha*(.22-themeBlend*.15)})`;
        ctx.beginPath();ctx.arc(p.x,p.y,radius*3.5,0,Math.PI*2);ctx.fill();
      }
      ctx.fillStyle=`hsla(${tint},${saturation}%,${lightness}%,${Math.min(1,alpha+themeBlend*.12)})`;
      ctx.beginPath();ctx.arc(p.x,p.y,radius*(p.spark?1.18:1),0,Math.PI*2);ctx.fill();
      if(themeBlend<.5&&depth>.62){
        ctx.fillStyle=`rgba(224,252,255,${alpha*.65*(1-themeBlend*2)})`;
        ctx.beginPath();ctx.arc(p.x,p.y,radius*.38,0,Math.PI*2);ctx.fill();
      }
    }
    ctx.globalCompositeOperation='source-over';
  }
  requestAnimationFrame(draw);
})();
