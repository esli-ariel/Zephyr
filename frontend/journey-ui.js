'use strict';
window.ZephyrJourneyUI=function({request,content,text,action,task,message,getProfile,isOpen,oralAnswer,resolveSpeechLanguage,onOralBusy,openProfile,selectSection}){
  let activity=null,autoAdvance=true;
  const post=(url,data={})=>request(url,{method:'POST',body:JSON.stringify(data)});
  const date=value=>value?new Date(value).toLocaleString('fr-FR',{dateStyle:'medium',timeStyle:'short'}):'Maintenant';
  const types={lesson:'Leçon',exercise:'Exercices',review:'Révision',practice:'Pratique',correction:'Correction'};
  function panel(title,help){oralAnswer.unmount();content.replaceChildren(text('h3',title),text('p',help,'learning-help'));}
  function back(){content.append(action('Revenir au plan',planHome,true));}
  async function planHome(){
    selectSection('plan');
    let plan=null;try{plan=await request('/api/learning/plan/current');}catch(error){if(error.status!==404)throw error;}
    panel('Votre prochaine séance','Les activités se préparent selon votre langue et votre niveau. Vous répondez aux exercices ; Zéphyr enregistre les corrections et propose la suite.');
    if(plan?.items.length){
      const completed=plan.items.filter(i=>i.completed).length;
      content.append(text('p',completed+' / '+plan.items.length+' activités terminées','assessment-progress'));
      const list=document.createElement('ol');list.className='journey-list';
      for(const item of plan.items){const row=text('li','');row.append(text('span',item.completed?'✓':'○','journey-check'),text('div',types[item.activity_type]+' · '+item.target),text('small',item.estimated_minutes+' min'+(item.score!=null?' · '+item.score+'/100':'')));list.append(row);}content.append(list);
      if(completed<plan.items.length){
        const label=document.createElement('label');label.className='journey-auto';const checkbox=document.createElement('input');checkbox.type='checkbox';checkbox.checked=autoAdvance;checkbox.addEventListener('change',()=>autoAdvance=checkbox.checked);label.append(checkbox,text('span','Enchaîner les activités après validation'));content.append(label,action('Lancer ou reprendre ma séance',next));
      }else content.append(text('p','Séance terminée. Les révisions dues vous attendent dans Révisions.'));
    }else content.append(text('p','Pas encore de plan. Préparez une première séance.'));
    const label=text('label','Durée de la séance'),minutes=document.createElement('select');minutes.id='journey-minutes';label.htmlFor=minutes.id;
    for(const value of [15,30,45,60]){const option=text('option',value+' minutes');option.value=value;option.selected=value===30;minutes.append(option);}content.append(label,minutes);
    content.append(action(plan?.items.length?'Préparer un nouveau plan':'Préparer mon plan',async()=>{message('Préparation du plan…');await post('/api/learning/plan/generate',{available_minutes:Number(minutes.value)});await planHome();message('Plan enregistré. Lancez votre séance quand vous êtes prêt.');},true));
  }
  async function next(){message('Préparation de l’activité…');activity=await post('/api/learning/plan/next');if(isOpen()){activityView(activity);message('');}}
  async function afterRead(correct){activity=await post('/api/learning/plan/items/'+activity.item.id+'/read',correct==null?{}:{correct});if(!isOpen())return;if(autoAdvance)await next();else{activityView(activity);message('Activité enregistrée.');}}
  function activityView(data){
    selectSection('plan');
    activity=data;
    if(data.status==='finished'){panel('Séance terminée','Toutes les activités du plan sont enregistrées. Retrouvez les prochaines échéances dans Révisions.');back();return;}
    if(data.status==='completed'){panel('Activité terminée',data.item.score==null?'Lecture ou autoévaluation enregistrée.':'Score des exercices : '+data.item.score+'/100');content.append(action('Activité suivante',next));back();return;}
    panel(types[data.item.activity_type]+' · '+data.item.target,'Votre progression est sauvegardée. Vous pouvez fermer cet écran et reprendre plus tard.');
    if(data.kind==='lesson'){
      content.append(text('h3',data.lesson.title));for(const section of data.lesson.sections){content.append(text('h4',section.title),text('p',section.content,'journey-prose'));}
      content.append(action('J’ai terminé la lecture',()=>afterRead(null)));
    }else if(data.kind==='review'){
      content.append(text('p','Retrouvez la traduction ou expliquez cette notion avant de regarder.'));
      content.append(action('Afficher la réponse',async()=>{content.append(text('p',data.review.content,'journey-prose'));for(const example of data.review.examples)content.append(text('p',example,'learning-help'));content.append(action('À revoir',()=>afterRead(false),true),action('Je l’ai retrouvé',()=>afterRead(true)));}));
    }else if(data.exercise){
      const exercise=data.exercise;content.append(text('p','Exercice '+(data.progress.answered+1)+' / '+data.progress.total,'assessment-progress'),text('h3',exercise.question));
      const form=document.createElement('form');form.className='assessment-form';const input=document.createElement(exercise.options?.length?'select':'textarea');input.id='journey-answer';input.name='answer';input.required=true;
      if(exercise.options?.length){const empty=text('option','Choisir une réponse');empty.value='';input.append(empty);for(const option of exercise.options){const node=text('option',option);node.value=option;input.append(node);}}else input.maxLength=5000;
      const label=text('label','Votre réponse');label.htmlFor=input.id;form.append(label,input);const button=text('button','Corriger ma réponse','learning-primary');button.type='submit';form.append(button);content.append(form);
      oralAnswer.mount({container:form,input,language:resolveSpeechLanguage(getProfile()?.target_language),question:exercise.question,onBusy:onOralBusy});form.append(button);
      form.addEventListener('submit',event=>{event.preventDefault();if(!form.reportValidity()||!input.value.trim())return;task(async()=>{
        oralAnswer.unmount();message('Correction en cours…');const result=await post('/api/learning/plan/items/'+data.item.id+'/answer',{exercise_id:exercise.id,answer:input.value.trim()});
        if(!isOpen())return;panel(result.evaluation.correct?'Bonne réponse':'À consolider',result.evaluation.feedback);content.append(text('p',result.evaluation.score+'/100','assessment-score'));
        content.append(action(result.activity.status==='completed'?'Continuer le parcours':'Exercice suivant',async()=>{if(result.activity.status==='completed'&&autoAdvance)await next();else activityView(result.activity);}));back();message('Correction enregistrée.');
      });});
    }
    back();
  }
  async function reviewsHome(){
    selectSection('reviews');
    const data=await request('/api/learning/reviews/due');
    panel('Révisions espacées','Essayez de retrouver la réponse, révélez-la puis indiquez honnêtement si vous l’aviez retrouvée. Les échéances se calculent sur votre compte.');
    content.append(text('p',data.count+' carte(s) à revoir maintenant','assessment-progress'));
    if(data.cards.length){const card=data.cards[0];content.append(action('Commencer les révisions',async()=>reviewCard(card)));}
    else content.append(text('p',data.next_review_at?'Prochaine révision : '+date(data.next_review_at):'Ajoutez un premier mot ou une règle pour commencer.'));
    content.append(text('p','Réussite : 1, 3, 7, 14, 30 puis 60 jours. Oubli : reprise dans 10 minutes. Les exercices liés à une notion actualisent aussi son échéance.','learning-help'));
    content.append(action('Ajouter un mot ou une règle',async()=>addNotion(),true));
    if(data.upcoming_count)content.append(text('p',data.upcoming_count+' carte(s) programmée(s) pour plus tard.','learning-help'));
  }
  function reviewCard(card){
    selectSection('reviews');
    panel(card.category==='vocabulary'?'Retrouvez la traduction':'Expliquez cette règle','Prenez quelques secondes avant de révéler la réponse.');content.append(text('h3',card.target,'review-target'));
    content.append(action('Afficher la réponse',async()=>{const data=await post('/api/learning/reviews/reveal',card);content.replaceChildren(text('h3',card.target),text('p',data.content,'journey-prose'));for(const example of data.examples)content.append(text('p',example,'learning-help'));
      const grade=async correct=>{const result=await post('/api/learning/reviews/grade',{...card,correct});await reviewsHome();message('Révision enregistrée. Prochaine échéance : '+date(result.next_review_at)+'.');};
      content.append(action('À revoir',()=>grade(false),true),action('Je l’ai retrouvé',()=>grade(true)));
    }));content.append(action('Revenir aux échéances',reviewsHome,true));
  }
  function addNotion(){
    panel('Votre bibliothèque','Ajoutez une notion dans la langue actuelle du profil. Elle sera immédiatement disponible pour la révision.');
    const form=document.createElement('form');form.className='profile-form';
    const kind=document.createElement('select');kind.id='notion-kind';for(const [value,label] of [['vocabulary','Mot'],['grammar','Règle de grammaire']]){const option=text('option',label);option.value=value;kind.append(option);}
    const target=document.createElement('input');target.id='notion-target';target.maxLength=100;target.required=true;
    const definition=document.createElement('textarea');definition.id='notion-definition';definition.maxLength=200;definition.required=true;kind.addEventListener('change',()=>definition.maxLength=kind.value==='vocabulary'?200:5000);
    for(const [labelText,node] of [['Type',kind],['Mot ou nom de la règle',target],['Traduction française ou explication',definition]]){const label=text('label',labelText);label.htmlFor=node.id;form.append(label,node);}
    const button=text('button','Ajouter à mes révisions','learning-primary');button.type='submit';form.append(button);content.append(form,action('Annuler',reviewsHome,true));
    form.addEventListener('submit',event=>{event.preventDefault();if(!form.reportValidity())return;task(async()=>{
      if(!getProfile()?.target_language||!getProfile()?.level)throw new Error('Renseignez votre langue et votre niveau dans Mon profil.');
      const data=kind.value==='vocabulary'?{word:target.value.trim(),translation:definition.value.trim()}:{rule:target.value.trim(),explanation:definition.value.trim()};
      await post('/api/learning/'+kind.value,data);await reviewsHome();message('Notion ajoutée.');
    });});
  }
  async function todayHome(){
    selectSection('today');
    const data=await request('/api/learning/today?utc_offset_minutes='+(-new Date().getTimezoneOffset()));
    panel('Ma séance du jour','Un pas à la fois. Retrouvez ce qui vous attend, puis reprenez la conversation.');
    const card=document.createElement('section');card.className='today-focus';
    card.append(text('span',data.target_language||'Votre langue à choisir','tag'),text('h3',data.reviews.due?(data.reviews.due===1?'Une révision vous attend':data.reviews.due+' révisions vous attendent'):data.plan.next?data.plan.next.target:data.profile_ready?'Une nouvelle séance vous attend':'Commençons par votre profil'));
    if(data.level)card.append(text('p','Niveau '+data.level,'learning-help'));
    if(!data.profile_ready)card.append(action('Choisir ma langue et mon niveau',openProfile));
    else if(data.reviews.due)card.append(action('Commencer mes révisions',async()=>{const reviews=await request('/api/learning/reviews/due');if(reviews.cards.length)reviewCard(reviews.cards[0]);else await reviewsHome();}));
    else if(data.plan.next)card.append(action(data.plan.next.started?'Reprendre mon activité':'Commencer ma séance',next));
    else card.append(action(data.plan.stale?'Préparer un plan dans ma langue':'Préparer ma séance',planHome));
    content.append(card);
    const grid=document.createElement('dl');grid.className='today-progress';
    for(const [label,value] of [['Activités du plan aujourd’hui',data.plan.completed_today],['Notions révisées aujourd’hui',data.reviews.reviewed_today],['Progression du plan',data.plan.completed+' / '+data.plan.total]])grid.append(text('dt',label),text('dd',String(value)));
    content.append(grid);
    if(data.plan.next){content.append(text('p','À suivre : '+types[data.plan.next.activity_type]+' · '+data.plan.next.estimated_minutes+' min. Environ '+data.plan.remaining_minutes+' min restantes dans le plan.','learning-help'));}
    else if(data.plan.stale)content.append(text('p','Votre langue a changé. Préparez un nouveau plan pour poursuivre.','learning-help'));
    if(data.reviews.next_review_at)content.append(text('p','Prochaine révision programmée : '+date(data.reviews.next_review_at),'learning-help'));
    content.append(action('Voir mon plan',planHome,true),action('Voir mes révisions',reviewsHome,true));
  }

  return {planHome,reviewsHome,todayHome};
};
