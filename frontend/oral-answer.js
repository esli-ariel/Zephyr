'use strict';
// Voice exercise answers are drafts. Only explicit approval can update a form.
window.ZephyrOralSession=function({createEngine,settings,onChange,onState=()=>{},onBoundary=()=>{}}){
  let phase='idle',draft='',provisional=false,error='',language=null,active=true,engine;
  const snapshot=()=>({phase,draft,provisional,error,language});
  const emit=()=>{if(active)onChange(snapshot());};
  engine=createEngine({settings:()=>({...settings(),recognitionLanguage:language}),
    onState:value=>{if(!active)return;phase=value;onState(value);emit();},
    onTranscript:value=>{if(!active)return;draft=value.text;provisional=!!value.interim;emit();},
    onResult:value=>{if(!active)return;draft=value.text;provisional=!!value.interim;if(value.error)error=value.error;emit();},
    onError:value=>{if(!active)return;error=value;emit();},onBoundary,
  });
  function stop(){if(!active)return;const received=engine.cancel();engine.silence();if(received?.text){draft=received.text;provisional=!!received.interim;}phase='idle';onState('idle');emit();}
  function approve(options=[]){
    if(!active||phase!=='idle'||!draft.trim())return {ok:false,reason:'empty-or-busy'};
    const text=draft.trim();if(text.length>5000)return {ok:false,reason:'too-long'};
    if(!options.length)return {ok:true,value:text};
    // Ignore terminal speech punctuation and case, but never infer a QCM answer.
    const normalize=value=>value.trim().toLocaleLowerCase().replace(/[.!?。！？]+$/u,'').trim();
    const matches=options.filter(option=>normalize(option)===normalize(text));
    return matches.length===1?{ok:true,value:matches[0]}:{ok:false,reason:'no-option'};
  }
  return {get state(){return snapshot();},get level(){return engine.level();},
    start(value){if(!active||phase!=='idle'||!Object.hasOwn(window.ZephyrVoiceTools.locales,value))return;language=value;error='';draft='';provisional=false;emit();engine.start();},
    finish(){if(active)engine.finish();},stop,
    edit(value){if(active&&phase==='idle'){draft=value;provisional=false;emit();}},approve,
    speak(text,options){if(!active)return;stop();error='';engine.speak(text,options);emit();},
    dispose(){if(!active)return;stop();active=false;},
  };
};
window.ZephyrOralAnswer=function({createEngine,settings,speechOptions,onState,onBoundary,Recognition}){
  let current=null;
  const errors={'not-allowed':'Autorisez le micro dans le navigateur, ou répondez au clavier.',NotAllowedError:'Accès au micro refusé. La saisie reste disponible.',NotFoundError:'Aucun microphone détecté.',network:'Le service de dictée est indisponible. Votre texte reste à relire.','no-speech':'Aucune parole détectée. Réessayez quand vous êtes prêt.','recognition-unavailable':'La dictée n’est pas disponible ici. Utilisez le clavier.','synthesis-timeout':'La lecture s’est interrompue. Vous pouvez relire la question à l’écran.'};
  function unmount(){if(current){const old=current;current=null;old.session.dispose();old.node.remove();}}
  function mount({container,input,language,question,onBusy,onApproved=()=>{}}){
    unmount();const node=document.createElement('section');node.className='oral-answer';
    node.innerHTML=`<div class="oral-top"><span class="tag">À VOUS DE PARLER</span><span class="oral-indicator" aria-hidden="true"></span></div><label>Langue parlée<select class="oral-language"></select></label><div class="oral-controls"><button type="button" class="learning-secondary oral-record">Répondre à l’oral</button><button type="button" class="learning-secondary oral-cancel" hidden>Arrêter / annuler</button><button type="button" class="learning-secondary oral-read">Écouter la question</button><button type="button" class="learning-secondary oral-slow">Plus lentement</button></div><p class="oral-status learning-help" role="status">Le texte dicté est à relire avant utilisation. Rien n’est envoyé automatiquement.</p><label class="oral-draft-label" hidden>Votre dictée à relire<textarea class="oral-draft" maxlength="5000" rows="3"></textarea></label><button type="button" class="learning-secondary oral-use" hidden>Utiliser cette réponse</button><p class="learning-help">La dictée peut utiliser le service du navigateur. La correction évalue votre texte, pas votre prononciation.</p>`;
    container.append(node);const $=selector=>node.querySelector(selector),select=$('.oral-language'),draft=$('.oral-draft'),status=$('.oral-status');
    const option=(value,label)=>{const item=document.createElement('option');item.value=value;item.textContent=label;select.append(item);};
    option('','Choisir la langue parlée');for(const [code,value] of Object.entries(window.ZephyrVoiceTools.locales))option(code,value.label);select.value=language||'';
    const options=input.tagName==='SELECT'?[...input.options].map(item=>item.value).filter(Boolean):[];
    let recording=false;
    function unavailable(element,value){element.dataset.unavailable=String(value);element.disabled=value;}
    function render(value){
      if(!node.isConnected)return;
      recording=value.phase==='starting'||value.phase==='listening';const busy=recording||value.phase==='speaking';node.dataset.phase=value.phase;
      $('.oral-record').textContent=value.phase==='starting'?'Annuler l’activation':value.phase==='listening'?'Terminer la dictée':'Répondre à l’oral';
      unavailable($('.oral-record'),!Recognition||!select.value||value.phase==='speaking');unavailable(select,busy);
      $('.oral-cancel').hidden=!busy;unavailable($('.oral-cancel'),!busy);
      for(const button of [$('.oral-read'),$('.oral-slow')])unavailable(button,recording||!select.value);
      unavailable(draft,recording);$('.oral-draft-label').hidden=!value.draft&&!recording;$('.oral-use').hidden=!value.draft;unavailable($('.oral-use'),busy||!value.draft.trim());
      if(draft.value!==value.draft)draft.value=value.draft;
      if(value.error)status.textContent=errors[value.error]||'Le vocal est indisponible. Relisez la dictée ou répondez au clavier.';
      else if(value.phase==='starting')status.textContent='Autorisez le micro si le navigateur le demande.';
      else if(value.phase==='listening')status.textContent=value.provisional?'Je vous écoute… mots provisoires.':'Je vous écoute…';
      else if(value.phase==='speaking')status.textContent='Lecture de la question. Vous pouvez l’arrêter à tout moment.';
      else if(value.draft)status.textContent=value.provisional?'Certains mots restent provisoires. Corrigez-les avant utilisation.':'Relisez, puis utilisez la réponse. Vous validerez ensuite la correction.';
      else status.textContent=!Recognition?'Dictée indisponible dans ce navigateur ; la saisie clavier reste disponible.':!select.value?'Choisissez la langue parlée avant de commencer.':'Le texte dicté est à relire avant utilisation. Rien n’est envoyé automatiquement.';
      onBusy(busy);
    }
    const session=window.ZephyrOralSession({createEngine,settings,onState,onBoundary,onChange:render});current={node,session};
    $('.oral-record').addEventListener('click',()=>{const phase=session.state.phase;if(phase==='starting')session.stop();else if(phase==='listening')session.finish();else session.start(select.value);});
    $('.oral-cancel').addEventListener('click',()=>session.stop());select.addEventListener('change',()=>render(session.state));draft.addEventListener('input',()=>session.edit(draft.value));
    $('.oral-use').addEventListener('click',()=>{const result=session.approve(options);if(!result.ok){status.textContent=result.reason==='no-option'?'La dictée ne correspond pas exactement à une option. Modifiez-la ou choisissez votre réponse dans la liste.':'Relisez et raccourcissez votre réponse avant de l’utiliser.';return;}input.value=result.value;input.dispatchEvent(new Event('input',{bubbles:true}));status.textContent='Réponse reportée. Vérifiez-la, puis cliquez sur « Corriger ma réponse ».';onApproved();input.focus();});
    for(const [selector,slow] of [['.oral-read',false],['.oral-slow',true]])$(selector).addEventListener('click',()=>{const options=speechOptions(select.value);session.speak(question,{...options,rate:slow?Math.max(.7,options.rate*.8):options.rate});});
    render(session.state);
  }
  document.addEventListener('visibilitychange',()=>{if(document.hidden)current?.session.stop();});window.addEventListener('pagehide',()=>current?.session.stop());
  return {mount,unmount,stop:()=>current?.session.stop(),get level(){return current?.session.level||0;}};
};
