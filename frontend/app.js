'use strict';
(() => {
  const $ = id => document.getElementById(id);
  const ui = {mic:$('mic'),send:$('send'),input:$('message'),status:$('status'),notice:$('notice'),messages:$('messages'),draft:$('draft'),sound:$('sound'),stop:$('stop'),demo:$('demo')};
  const recognitionType = window.SpeechRecognition || window.webkitSpeechRecognition;
  const synth = window.speechSynthesis;
  const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
  let learnerId = null, ready = false, busy = false, listening = false, starting = false,learningLocked=false;
  let stream, audioContext, analyser, audioData, recognition, utterance;
  let micToken = 0, voiceToken = 0, finalTranscript = '', interim = '', voiceOn = true;
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
  const languageSelect=$('object-language-select');
  const languageStatus=$('object-language-status');
  let objectIndex=0,objectLanguage=vocabulary.resolveLanguage(stored('zephyr.objectLanguage'))||'en';
  let unknownLanguage='',languageSaving=false,profileEpoch=0,idleTime=0,currentShapeIndex=0;
  let captionKey='',shapeSettledTime=0,lastGeometryShape=-1;
  languageSelect.value=objectLanguage;
  languageStatus.textContent='Traductions hors ligne · sélectionnez la langue étudiée.';
  function applyProfile(profile){
    if(!profile.target_language){languageStatus.textContent=vocabulary.languages[objectLanguage].name+' · aperçu. Choisissez une langue pour l’enregistrer dans le profil.';return;}
    const code=vocabulary.resolveLanguage(profile.target_language);
    if(code){objectLanguage=code;unknownLanguage='';languageSelect.value=code;save('zephyr.objectLanguage',code);languageStatus.textContent='Langue du profil : '+vocabulary.languages[code].name+'.';}
    else{
      unknownLanguage=String(profile.target_language);objectLanguage=null;
      let option=languageSelect.querySelector('[data-unsupported]');
      if(!option){option=document.createElement('option');option.value='';option.disabled=true;option.dataset.unsupported='true';languageSelect.prepend(option);}
      option.textContent=unknownLanguage;languageSelect.value='';
      languageStatus.textContent='Traductions non disponibles pour « '+unknownLanguage+' ». Choisissez une des six langues proposées.';
    }
  }
  async function refreshProfile(){
    const epoch=profileEpoch;
    try{const profile=await request('/api/learner/profile');if(epoch===profileEpoch&&!languageSaving)applyProfile(profile);}catch{}
  }
  languageSelect.addEventListener('change',async()=>{
    const code=languageSelect.value;if(!vocabulary.languages[code])return;
    profileEpoch++;objectLanguage=code;unknownLanguage='';save('zephyr.objectLanguage',code);
    if(!ready){languageStatus.textContent='Aperçu en '+vocabulary.languages[code].name+' ; profil non synchronisé.';return;}
    languageSaving=true;controls();languageStatus.textContent='Enregistrement de la langue…';
    try{const profile=await request('/api/learner/profile',{method:'PUT',body:JSON.stringify({target_language:vocabulary.languages[code].profile})});applyProfile(profile);}
    catch{languageStatus.textContent='Aperçu en '+vocabulary.languages[code].name+' ; langue non enregistrée dans le profil. Réessayez.';}
    finally{languageSaving=false;controls();}
  });
  $('next-object').addEventListener('click',()=>{
    if(mode!=='idle'||busy||listening||starting)return;
    objectIndex=(currentShapeIndex+1)%vocabulary.objects.length;currentShapeIndex=objectIndex;idleTime=9;
  });
  $('read-object').addEventListener('click',()=>{
    if(!objectLanguage||mode!=='idle'||busy||listening||starting)return;
    const item=vocabulary.objects[currentShapeIndex];if(!voiceOn)ui.sound.click();
    speak(item.words[objectLanguage],vocabulary.languages[objectLanguage].speech);
  });
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
  function state(next){if(mode!=='idle'&&next==='idle')idleTime=0;mode=next;document.body.dataset.voiceState=next;ui.status.textContent={idle:'Prêt à vous écouter',listening:'Je vous écoute…',thinking:'Zéphyr prépare sa réponse…',speaking:'Zéphyr vous répond…'}[next];$('activity').textContent={idle:'EN VEILLE',listening:'ÉCOUTE ACTIVE',thinking:'RÉFLEXION',speaking:'TRANSMISSION'}[next];controls();}
  function controls(){$('open-learning').disabled=!ready||busy||starting||languageSaving;ui.send.disabled=!ready||busy||listening||starting||learningLocked;ui.mic.disabled=busy||starting||learningLocked;ui.demo.disabled=busy||starting||learningLocked;languageSelect.disabled=busy||listening||starting||languageSaving||learningLocked;$('next-object').disabled=mode!=='idle'||busy||listening||starting;$('read-object').disabled=!objectLanguage||mode!=='idle'||busy||listening||starting;}
  async function request(path,options={},identify=true){
    const response=await fetch(path,{...options,headers:{...(options.body?{'Content-Type':'application/json'}:{}),...(identify?{'X-Learner-ID':learnerId}:{}),...options.headers},signal:AbortSignal.timeout(135000)});
    const data=await response.json();
    if(!response.ok){const error=new Error(typeof data.detail==='string'?data.detail:'La requête a échoué. Veuillez réessayer.');error.status=response.status;throw error;}
    return data;
  }
  function append(role,text){
    beginConversation();
    const article=document.createElement('article');article.className=`message ${role==='user'?'user':'assistant'}`;
    const label=document.createElement('div');label.className='message-label';label.textContent=role==='user'?'VOUS':'ZÉPHYR';
    const time=document.createElement('span');time.textContent=new Date().toLocaleTimeString('fr-FR',{hour:'2-digit',minute:'2-digit'});label.append(time);
    const p=document.createElement('p');p.textContent=text;article.append(label,p);ui.messages.append(article);ui.messages.scrollTop=ui.messages.scrollHeight;
  }
  function silence(){voiceToken++;if(synth)synth.cancel();utterance=null;ui.stop.hidden=true;if(mode==='speaking')state('idle');}
  function speak(text,language='fr-FR'){
    silence();if(!voiceOn)return;
    if(!synth){notice('La lecture vocale n’est pas disponible dans ce navigateur. Le texte reste accessible.');return;}
    const token=voiceToken;utterance=new SpeechSynthesisUtterance(text.replace(/[*#`]/g,''));utterance.lang=language;utterance.rate=.97;
    const voices=synth.getVoices();const voice=voices.find(v=>v.lang===language)||voices.find(v=>v.lang.startsWith(language.split('-')[0]));if(voice)utterance.voice=voice;
    utterance.onstart=()=>{if(token!==voiceToken)return;beginConversation();speechStart=performance.now();state('speaking');ui.stop.hidden=false;};
    utterance.onboundary=()=>{boundaryAt=performance.now();};
    utterance.onend=()=>{if(token!==voiceToken)return;state('idle');ui.stop.hidden=true;utterance=null;};
    utterance.onerror=e=>{if(token!==voiceToken)return;state('idle');ui.stop.hidden=true;if(e.error!=='interrupted'&&e.error!=='canceled')notice('La lecture vocale n’a pas pu démarrer. Vous pouvez lire la réponse dans la conversation.',true);};
    synth.speak(utterance);
  }
  async function send(text){
    text=text.trim();if(!text||busy||!ready||listening||starting||learningLocked)return;
    if(text.length>5000){notice('Le message est limité à 5 000 caractères.',true);return;}
    silence();busy=true;controls();state('thinking');$('suggestions')?.remove();append('user',text);ui.input.value='';ui.input.style.height='auto';ui.draft.textContent='';
    notice('Zéphyr réfléchit à votre message.');
    try{const data=await request('/api/chat',{method:'POST',body:JSON.stringify({message:text})});append('assistant',data.response);state('idle');notice('À vous. Continuez par écrit ou activez le microphone.');speak(data.response);refreshProfile();}
    catch(error){state('idle');ui.input.value=text;notice(error.name==='TimeoutError'?'La réponse a pris trop de temps. Réessayez dans quelques instants.':error.message,true);}
    finally{busy=false;controls();}
  }
  function releaseMic(){
    listening=false;starting=false;stream?.getTracks().forEach(track=>track.stop());stream=null;
    if(audioContext){audioContext.close().catch(()=>{});audioContext=null;}analyser=null;audioData=null;
    ui.mic.classList.remove('active');ui.mic.setAttribute('aria-pressed','false');ui.mic.setAttribute('aria-label','Activer le microphone');$('mic-hint').textContent='Cliquez pour parler';
    if(mode==='listening')state('idle');controls();
  }
  function stopMic(submit=true){
    micToken++;const activeRecognition=recognition;recognition=null;
    if(activeRecognition){activeRecognition.onend=null;activeRecognition.onresult=null;activeRecognition.onerror=null;try{activeRecognition.abort();}catch{}}
    const text=(finalTranscript+' '+interim).trim();releaseMic();
    if(submit&&text){ui.draft.textContent='';if(ready)send(text);else{ui.input.value=text;notice('Votre dictée est prête. Reconnectez l’API pour l’envoyer.');}}
    else{ui.draft.textContent='';notice(recognitionType?'Écoute terminée. Vous pouvez reprendre la conversation.':'Écoute terminée. Écrivez votre message pour l’envoyer.');}
  }
  async function startMic(){
    if(busy||starting)return;if(listening){stopMic();return;}
    if(!navigator.mediaDevices?.getUserMedia){notice('Le microphone nécessite localhost ou une connexion HTTPS et un navigateur compatible.',true);return;}
    silence();starting=true;controls();const token=++micToken;finalTranscript='';interim='';
    try{
      const acquired=await navigator.mediaDevices.getUserMedia({audio:{echoCancellation:true,noiseSuppression:true},video:false});
      if(token!==micToken){acquired.getTracks().forEach(t=>t.stop());return;}
      stream=acquired;const AudioCtx=window.AudioContext||window.webkitAudioContext;if(!AudioCtx)throw new Error('L’analyse audio est indisponible.');
      audioContext=new AudioCtx();await audioContext.resume();
      if(token!==micToken)return;
      analyser=audioContext.createAnalyser();analyser.fftSize=512;audioContext.createMediaStreamSource(stream).connect(analyser);audioData=new Uint8Array(analyser.fftSize);
      beginConversation();listening=true;starting=false;state('listening');controls();ui.mic.classList.add('active');ui.mic.setAttribute('aria-pressed','true');ui.mic.setAttribute('aria-label','Terminer l’écoute et envoyer');$('mic-hint').textContent='Cliquez pour terminer';
      if(!recognitionType){notice('Les points réagissent à votre voix. La dictée est indisponible ici : écrivez votre message, ou essayez Chrome.');return;}
      notice('Je vous écoute. Votre phrase sera envoyée à la fin de l’écoute. La dictée peut utiliser le service vocal du navigateur.');
      recognition=new recognitionType();recognition.lang='fr-FR';recognition.continuous=false;recognition.interimResults=true;
      recognition.onresult=event=>{if(token!==micToken)return;interim='';for(let i=event.resultIndex;i<event.results.length;i++){const result=event.results[i];if(result.isFinal)finalTranscript+=result[0].transcript+' ';else interim+=result[0].transcript;}ui.draft.textContent=(finalTranscript+' '+interim).trim();};
      recognition.onend=()=>{if(token!==micToken)return;const text=(finalTranscript+' '+interim).trim();recognition=null;releaseMic();ui.draft.textContent='';if(text){if(ready)send(text);else ui.input.value=text;}else notice('Aucune phrase détectée. Réessayez ou écrivez votre message.');};
      recognition.onerror=event=>{if(token!==micToken)return;const reason=event.error;stopMic(false);notice(reason==='not-allowed'?'La dictée a été refusée. Autorisez le microphone dans les réglages du navigateur.':reason==='no-speech'?'Aucune parole détectée. Réessayez ou écrivez votre message.':'La dictée est indisponible ('+reason+'). Vous pouvez continuer par écrit.',true);};
      recognition.start();
    }catch(error){if(token!==micToken)return;stopMic(false);notice(error.name==='NotAllowedError'?'Accès au microphone refusé. Vous pouvez l’autoriser dans le navigateur ou écrire à Zéphyr.':error.name==='NotFoundError'?'Aucun microphone détecté. Branchez-en un ou écrivez votre message.':'Impossible d’activer le micro : '+error.message,true);}
  }
  ui.mic.addEventListener('click',startMic);
  $('composer').addEventListener('submit',event=>{event.preventDefault();send(ui.input.value);});
  ui.input.addEventListener('keydown',event=>{if(event.key==='Enter'&&!event.shiftKey&&!event.isComposing){event.preventDefault();send(ui.input.value);}});
  ui.input.addEventListener('input',()=>{ui.input.style.height='auto';ui.input.style.height=Math.min(ui.input.scrollHeight,120)+'px';});
  document.querySelectorAll('[data-prompt]').forEach(button=>button.addEventListener('click',()=>send(button.dataset.prompt)));
  ui.sound.addEventListener('click',()=>{voiceOn=!voiceOn;ui.sound.setAttribute('aria-pressed',String(voiceOn));ui.sound.textContent=voiceOn?'Voix activée ◖))':'Voix coupée';if(!voiceOn)silence();});
  ui.stop.addEventListener('click',silence);
  ui.demo.addEventListener('click',()=>{if(listening)stopMic(false);if(!voiceOn)ui.sound.click();speak('Bonjour, je suis Zéphyr, votre compagnon d’apprentissage. Ensemble, donnons un nouveau souffle à votre pratique des langues.');});
  window.addEventListener('pagehide',()=>{micToken++;stopMic(false);silence();});
  window.ZephyrLearningUI({request,onProfile:applyProfile,resolveLanguage:vocabulary.resolveLanguage,
    isReady:()=>ready&&!busy&&!starting&&!languageSaving,
    suspend:()=>{silence();if(listening)stopMic(false);},
    onLock:value=>{learningLocked=value;controls();},
  });
  controls();
  async function initialize(){
    try{
      await request('/health',{},false);learnerId=stored('zephyr.learnerId');
      if(learnerId){try{applyProfile(await request('/api/learner/profile'));}catch(error){if(error.status===404||error.status===400)learnerId=null;else throw error;}}
      if(!learnerId){const data=await request('/api/learners',{method:'POST'},false);learnerId=data.learner_id;save('zephyr.learnerId',learnerId);applyProfile(await request('/api/learner/profile'));}
      const memory=await request('/api/chat/memory');if(memory.messages?.length){ui.messages.replaceChildren();memory.messages.forEach(m=>append(m.role,m.content));}
      ready=true;$('connection').textContent='Zéphyr connecté';controls();
    }catch(error){$('connection').textContent='API indisponible';$('connection-dot').classList.add('off');notice('Connexion impossible : '+error.message+' Rechargez la page pour réessayer. Vous pouvez essayer la voix et le micro.',true);}
  }
  initialize();
  // The microphone drives the field with RMS amplitude. Browser speech synthesis
  // exposes word boundaries, not PCM audio: its envelope is an animation, not a waveform.
  const canvas=$('orb'),ctx=canvas.getContext('2d');
  let width=0,height=0,lastFrame=0,rotation=0,motionTime=0,engagement=0,themeBlend=document.documentElement.dataset.theme==='day'?1:0;
  const pointer={x:0,y:0,active:false,strength:0};
  const feeling={listening:0,thinking:0,speaking:0};
  let pulseAt=-10000;
  const points=Array.from({length:2100},(_,i)=>{
    const y=1-2*(i+.5)/2100,r=Math.sqrt(1-y*y),angle=i*2.399963229728653;
    return{x:r*Math.cos(angle),y,z:r*Math.sin(angle),freeX:Math.sin(i*71.17)*1.3,freeY:Math.cos(i*17.91)*.95,freeZ:Math.sin(i*31.7)*.55,position:null,size:.65+((i*.754877666)%1)*.65,spark:i%43===0,phase:i*.73,drifter:i%6===0,driftOffset:(i*.61803398875)%1};
  });
  const shapes=vocabulary.objects.map(item=>vocabulary.buildGeometry(item.id,points.length));
  function caption(show,index){
    const item=vocabulary.objects[index],key=[show,index,objectLanguage,unknownLanguage].join('|');if(key===captionKey)return;captionKey=key;
    $('object-caption').hidden=!show;
    $('object-french').textContent=item.fr;
    $('object-word').textContent=objectLanguage?item.words[objectLanguage]:'—';
    $('object-word').lang=objectLanguage||'fr';
    $('object-language').textContent=objectLanguage?vocabulary.languages[objectLanguage].name:'Traduction indisponible : '+unknownLanguage;
    canvas.setAttribute('aria-label',show?item.fr+(objectLanguage?' : '+item.words[objectLanguage]:'')+'. Nuage interactif, cliquez pour une pulsation.':'Nuage de points interactif : déplacement au pointeur, pulsation au clic ou avec Entrée.');
  }
  function resize(){
    const rect=canvas.getBoundingClientRect(),dpr=Math.min(devicePixelRatio||1,2);
    width=rect.width;height=rect.height;canvas.width=width*dpr;canvas.height=height*dpr;
    ctx.setTransform(dpr,0,0,dpr,0,0);
  }
  function pointAt(event){
    const rect=canvas.getBoundingClientRect();pointer.x=event.clientX-rect.left;pointer.y=event.clientY-rect.top;pointer.active=true;
  }
  canvas.addEventListener('pointermove',pointAt);
  canvas.addEventListener('pointerleave',()=>{pointer.active=false;});
  canvas.addEventListener('pointercancel',()=>{pointer.active=false;});
  canvas.addEventListener('pointerup',event=>{if(event.pointerType!=='mouse')pointer.active=false;});
  canvas.addEventListener('pointerdown',event=>{pointAt(event);pulseAt=performance.now();});
  canvas.addEventListener('keydown',event=>{
    if(event.key==='Enter'||event.key===' '){event.preventDefault();pulseAt=performance.now();}
  });
  new ResizeObserver(resize).observe(canvas);resize();
  function draw(now){
    requestAnimationFrame(draw);
    if(document.hidden){lastFrame=now;return;}
    if(now-lastFrame<(reducedMotion.matches?90:30))return;
    const delta=Math.min((now-lastFrame)/1000,.06);lastFrame=now;
    let input=0;
    if(analyser&&audioData){
      analyser.getByteTimeDomainData(audioData);let sum=0;
      for(const value of audioData){const sample=(value-128)/128;sum+=sample*sample;}
      input=Math.min(1,Math.sqrt(sum/audioData.length)*7);
    }
    if(mode==='speaking'){
      const elapsed=(now-speechStart)/1000;
      input=.32+.48*Math.abs(Math.sin(elapsed*8.7)*Math.cos(elapsed*3.1))+.2*Math.exp(-(now-boundaryAt)/120);
    }
    volume+=(input-volume)*.2;
    // Blend state changes so shape, glow and colour settle together.
    for(const name of Object.keys(feeling))feeling[name]+=((mode===name?1:0)-feeling[name])*.08;
    engagement+=((conversationStarted?1:0)-engagement)*.06;
    pointer.strength+=((pointer.active?1:0)-pointer.strength)*.12;
    const quiet=reducedMotion.matches;
    themeBlend+=((document.documentElement.dataset.theme==='day'?1:0)-themeBlend)*(quiet?1:.045);
    if(!quiet){rotation+=delta*(.10+engagement*.10+feeling.thinking*.55+feeling.speaking*.14+volume*.18);motionTime+=delta;}
    if(mode==='idle')idleTime=quiet?9:idleTime+delta;else idleTime=0;
    const phase=idleTime%20;
    currentShapeIndex=(objectIndex+Math.floor(idleTime/20))%shapes.length;
    const form=quiet?1:phase<5?0:phase<8?(phase-5)/3:phase<16?1:1-(phase-16)/4;
    const smoothForm=form*form*(3-2*form);
    const activeWeight=Math.min(1,feeling.speaking+feeling.thinking+feeling.listening);
    if(lastGeometryShape!==currentShapeIndex||mode!=='idle'||smoothForm<.98||activeWeight>=.03)shapeSettledTime=0;
    else shapeSettledTime+=delta;
    lastGeometryShape=currentShapeIndex;
    const objectClarity=smoothForm*(1-activeWeight);
    const showCaption=mode==='idle'&&smoothForm>.98&&activeWeight<.03&&(quiet||shapeSettledTime>.7);
    caption(showCaption,currentShapeIndex);
    $('read-object').disabled=!showCaption||!objectLanguage||busy||listening||starting;
    document.body.dataset.pointScene=mode==='idle'?(showCaption?'object':'wandering'):mode;
    const pulseAge=(now-pulseAt)/1000;
    const pulse=!quiet&&pulseAge<1.4?Math.sin(Math.min(pulseAge/.22,1)*Math.PI/2)*Math.exp(-pulseAge*2.8):0;
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
      const modelPoint=shapes[currentShapeIndex][index];
      const objectYaw=quiet?.45:motionTime*.32+.45;
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
      const dx=px-pointer.x,dy=py-pointer.y,distance=Math.hypot(dx,dy);
      const influence=Math.exp(-(distance*distance)/(2*85*85))*pointer.strength;
      if(!quiet&&distance>0){
        const force=influence*(28+volume*35)*(.55+(zz+1)*.3);
        px+=dx/distance*force;py+=dy/distance*force;
      }
      return{x:px,y:py,z:zz,influence,flight,tint:p.driftOffset,size:p.size,spark:p.spark,perspective};
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
