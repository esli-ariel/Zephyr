'use strict';
window.ZephyrLearningUI = function({request,onProfile,suspend,onLock,isReady,resolveLanguage,oralAnswer,resolveSpeechLanguage}){
  const dialog=document.createElement('dialog');dialog.id='learning-dialog';dialog.className='learning-dialog';
  dialog.setAttribute('aria-labelledby','learning-title');
  dialog.innerHTML=`<header class="learning-header"><div><span class="tag">VOTRE PARCOURS</span><h2 id="learning-title">Apprendre avec Zéphyr</h2></div><button type="button" id="learning-close" aria-label="Fermer mon parcours">×</button></header>
  <nav class="learning-tabs" aria-label="Sections du parcours"><button type="button" id="today-tab" aria-pressed="false">Aujourd’hui</button><button type="button" id="profile-tab" aria-pressed="true">Mon profil</button><button type="button" id="assessment-tab" aria-pressed="false">Mon niveau</button><button type="button" id="plan-tab" aria-pressed="false">Mon plan</button><button type="button" id="reviews-tab" aria-pressed="false">Révisions</button></nav>
  <p id="learning-status" class="learning-status" role="status"></p><div id="learning-content"></div>`;
  document.body.append(dialog);
  const $=id=>dialog.querySelector('#'+id),content=$('learning-content'),status=$('learning-status');
  let profile=null,progress=null,working=false,oralBusy=false,section='today',currentQuestion=null;
  const text=(tag,value,className='')=>{const node=document.createElement(tag);node.textContent=value;if(className)node.className=className;return node;};
  const english=()=>resolveLanguage(profile?.target_language)==='en';
  function message(value,error=false){status.textContent=value;status.classList.toggle('error',error);}
  function lock(){dialog.querySelectorAll('button,input,select,textarea').forEach(node=>{if(node.id!=='learning-close')node.disabled=working||(!node.closest('.oral-answer')&&oralBusy)||node.dataset.unavailable==='true';});}
  function action(label,handler,secondary=false){const button=text('button',label,secondary?'learning-secondary':'learning-primary');button.type='button';button.addEventListener('click',()=>task(handler));return button;}
  async function task(handler){
    if(working)return;working=true;lock();
    try{await handler();}catch(error){message(error.message||'Le service est indisponible. Réessayez.',true);}
    finally{working=false;lock();}
  }
  function selectSection(next){section=next;for(const name of ['today','profile','assessment','plan','reviews'])$(name+'-tab').setAttribute('aria-pressed',String(next===name));}
  function list(title,items){const box=document.createElement('section');box.append(text('h3',title));const ul=document.createElement('ul');for(const item of items||[])ul.append(text('li',item));if(!ul.children.length)ul.append(text('li','Aucun élément pour le moment.'));box.append(ul);return box;}
  function profileView(){
    selectSection('profile');content.replaceChildren();
    const form=document.createElement('form');form.className='profile-form';form.id='profile-form';
    form.innerHTML=`<label>Votre prénom<input id="profile-name" name="name" maxlength="100" autocomplete="given-name"></label>
    <label>Langue étudiée<input id="profile-language" name="language" maxlength="100" required placeholder="Ex. anglais, espagnol…"></label>
    <label>Niveau déclaré<select id="profile-level"><option value="">Je ne sais pas encore</option><option>A1</option><option>A2</option><option>B1</option><option>B2</option><option>C1</option><option>C2</option></select></label>
    <label>Ajouter un objectif<input id="profile-goal" maxlength="300" placeholder="Ex. préparer un entretien en anglais"></label>
    <p class="learning-help">Le niveau déclaré est votre estimation. L’évaluation d’anglais peut ensuite l’actualiser.</p><button class="learning-primary" type="submit">Enregistrer mon profil</button>`;
    content.append(form);
    $('profile-name').value=profile.name||'';$('profile-language').value=profile.target_language||'';$('profile-level').value=profile.level||'';
    form.addEventListener('submit',event=>{event.preventDefault();if(!form.reportValidity())return;task(async()=>{
      const data={name:$('profile-name').value.trim(),target_language:$('profile-language').value.trim()};
      if(!data.target_language){message('Indiquez une langue étudiée.',true);return;}
      const level=$('profile-level').value;if(level)data.level=level;
      const goal=$('profile-goal').value.trim();if(goal&&!profile.goals?.includes(goal))data.goal=goal;
      if(!level&&profile.level){message('Pour modifier un niveau existant, choisissez un autre niveau de A1 à C2.',true);return;}
      profile=await request('/api/learner/profile',{method:'PUT',body:JSON.stringify(data)});onProfile(profile);profileView();message('Votre profil est enregistré.');
    });});
    content.append(list('Vos objectifs',profile.goals));
    const history=profile.assessment_history||[];
    content.append(text('p',history.length?history.length+' évaluation(s) enregistrée(s).':'Vous n’avez pas encore de bilan d’évaluation.','learning-help'));
  }
  function guard(){
    if(english())return true;
    content.replaceChildren(text('h3','Évaluation d’anglais'),text('p','La banque actuelle évalue uniquement l’anglais. Pour tester cette langue, choisissez « anglais » dans votre profil. Les autres langues seront ajoutées plus tard.'));
    content.append(action('Ouvrir mon profil',async()=>{profileView();message('');},true));return false;
  }
  function progressLine(value){
    const answered=value?.answered||0;
    return text('p',(value?.current_level||'A1')+' · '+answered+' réponse'+(answered>1?'s':'')+' enregistrée'+(answered>1?'s':'')+' · parcours adaptatif','assessment-progress');
  }
  function assessmentHome(){
    selectSection('assessment');content.replaceChildren();if(!guard())return;
    content.append(text('h3','Situer votre niveau d’anglais'),text('p','Un parcours adaptatif de A1 à C2. Vous pouvez fermer cet écran et reprendre plus tard. Les questions ouvertes sont corrigées par l’IA.'),progressLine(progress));
    if(progress?.finished){content.append(action('Afficher mon bilan',showResult));}
    else if(progress?.answered){content.append(action('Reprendre l’évaluation',loadQuestion));}
    else{content.append(action('Démarrer l’évaluation',async()=>{await ensureEnglish();const data=await request('/api/assessment/start',{method:'POST'});progress=data.progress;questionView(data);}));}
    if(progress?.answered||progress?.finished)content.append(action('Recommencer…',async()=>restartView(),true));
  }
  async function ensureEnglish(){profile=await request('/api/learner/profile');onProfile(profile);if(!english())throw new Error('Le profil n’est plus configuré en anglais. Ouvrez Mon profil avant de poursuivre.');}
  function questionView(data,preservedAnswer=''){
    progress=data.progress;currentQuestion=data.question;
    if(data.finished||!currentQuestion){finishedView();return;}
    content.replaceChildren(progressLine(progress),text('h3',currentQuestion.question));
    content.append(text('p',currentQuestion.type==='closed'?'Choisissez une réponse.':'Répondez en anglais. La correction utilise l’IA.','learning-help'));
    const form=document.createElement('form');form.className='assessment-form';form.id='assessment-form';
    const questionId=currentQuestion.id;
    if(currentQuestion.options?.length){
      const fieldset=document.createElement('fieldset');fieldset.append(text('legend','Votre réponse','sr-only'));
      currentQuestion.options.forEach((option,index)=>{const label=document.createElement('label'),radio=document.createElement('input');radio.type='radio';radio.name='answer';radio.value=String(option);radio.required=true;radio.checked=option===preservedAnswer;radio.id='assessment-option-'+index;label.append(radio,text('span',option));fieldset.append(label);});form.append(fieldset);
    }else{const label=text('label','Votre réponse'),input=document.createElement('textarea');input.name='answer';input.id='assessment-answer';input.required=true;input.maxLength=5000;input.rows=4;input.value=preservedAnswer;label.htmlFor=input.id;form.append(label,input);}
    const submit=text('button','Valider ma réponse','learning-primary');submit.type='submit';form.append(submit);content.append(form);
    form.addEventListener('submit',event=>{event.preventDefault();if(!form.reportValidity())return;const answer=String(new FormData(form).get('answer')||'').trim();if(!answer){message('Saisissez votre réponse.',true);return;}
      task(async()=>{
        await ensureEnglish();message('Correction de votre réponse…');
        try{const result=await request('/api/assessment/answer',{method:'POST',body:JSON.stringify({answer})});progress=result.progress;feedbackView(result);message('Réponse enregistrée.');}
        catch(error){
          // A lost response can still have been saved. Re-read before offering a retry.
          currentQuestion=null;content.replaceChildren(text('h3','Vérifier votre progression'));
          message('Vérification de la dernière réponse…');
          try{const data=await request('/api/assessment/question');progress=data.progress;
            if(data.finished||data.question?.id!==questionId){questionView(data);message('La progression du serveur a été reprise. La réponse précédente ne sera pas renvoyée.');}
            else{questionView(data,answer);message(error.message+' Votre réponse est conservée pour réessayer.',true);}
          }catch{content.append(action('Reprendre depuis le serveur',loadQuestion,true));message('Impossible de vérifier l’enregistrement. Reprenez la session avant de répondre à nouveau.',true);}
        }
      });
    });
  }
  function feedbackView(result){
    currentQuestion=null;content.replaceChildren(progressLine(progress));
    const evaluation=result.evaluation||{};
    content.append(text('h3',evaluation.correct?'Bonne réponse':'À retravailler'),text('p','Score : '+evaluation.score+'/100','assessment-score'),text('p',evaluation.feedback||'La correction a été enregistrée.'));
    content.append(action(result.finished?'Voir mon bilan':'Question suivante',result.finished?showResult:loadQuestion));
  }
  function finishedView(){content.replaceChildren(text('h3','Évaluation terminée'),progressLine(progress),text('p','Votre bilan récapitule votre niveau estimé et vos pistes de travail.'));content.append(action('Afficher mon bilan',showResult));}
  async function loadQuestion(){await ensureEnglish();const data=await request('/api/assessment/question');questionView(data);message('');}
  async function showResult(){
    await ensureEnglish();message('Préparation du bilan…');
    const result=await request('/api/assessment/result');
    content.replaceChildren(text('h3',result.estimated_level?'Votre niveau estimé : '+result.estimated_level:'Niveau à consolider'),text('p','Score global : '+result.overall_score+'/100','assessment-score'));
    const labels={vocabulary:'Vocabulaire',grammar:'Grammaire',comprehension:'Compréhension',expression:'Expression'};
    const dl=document.createElement('dl');dl.className='competency-list';
    for(const [key,label] of Object.entries(labels)){dl.append(text('dt',label),text('dd',result.competency_scores?.[key]==null?'Non évalué':result.competency_scores[key]+'/100'));}content.append(dl);
    content.append(list('Vos points forts',result.strengths),list('À travailler',result.weak_points));
    content.append(action('Revenir à mon profil',async()=>{profile=await request('/api/learner/profile');onProfile(profile);profileView();message('');},true));
    content.append(action('Recommencer…',async()=>restartView(),true));
    profile=await request('/api/learner/profile');onProfile(profile);message('Bilan enregistré dans votre profil. Ce résultat est une estimation pédagogique.');
  }
  function restartView(){
    content.replaceChildren(text('h3','Recommencer cette évaluation ?'),text('p','Les réponses de la session actuelle seront remplacées. Les bilans déjà enregistrés dans votre profil sont conservés.'));
    content.append(action('Recommencer depuis A1',async()=>{await ensureEnglish();const data=await request('/api/assessment/start',{method:'POST'});progress=data.progress;questionView(data);message('Nouvelle évaluation démarrée.');}));
    content.append(action('Conserver ma session',async()=>assessmentHome(),true));
  }
  const journey=window.ZephyrJourneyUI({request,content,text,action,task,message,getProfile:()=>profile,isOpen:()=>dialog.open,oralAnswer,resolveSpeechLanguage,onOralBusy:value=>{oralBusy=value;lock();},openProfile:()=>loadSection('profile'),selectSection});
  async function loadSection(next){
    oralAnswer.unmount();selectSection(next);message('Chargement de votre parcours…');content.replaceChildren();
    [profile,progress]=await Promise.all([request('/api/learner/profile'),request('/api/assessment/progress')]);onProfile(profile);
    if(next==='today')await journey.todayHome();else if(next==='profile')profileView();else if(next==='plan')await journey.planHome();else if(next==='reviews')await journey.reviewsHome();else assessmentHome();message('');
  }
  $('profile-tab').addEventListener('click',()=>task(()=>loadSection('profile')));
  $('assessment-tab').addEventListener('click',()=>task(()=>loadSection('assessment')));
  for(const name of ['today','plan','reviews'])$(name+'-tab').addEventListener('click',()=>task(()=>loadSection(name)));
  $('learning-close').addEventListener('click',()=>dialog.close());
  dialog.addEventListener('close',()=>{oralAnswer.unmount();onLock(false);});
  function open(next=section){if(!isReady())return;suspend();dialog.showModal();onLock(true);task(()=>loadSection(next));}
  document.getElementById('open-learning').addEventListener('click',()=>open());
  return {open,close:()=>{if(dialog.open)dialog.close();}};
};
