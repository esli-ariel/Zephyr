'use strict';
window.ZephyrProfilePage=function({request,isReady,getAccount,onProfile,onAccount,onLearning,onViewChange}){
  const $=id=>document.getElementById(id),page=$('profile-view'),content=$('profile-page-content'),rail=$('sidebar'),menu=$('sidebar-toggle'),scrim=$('sidebar-scrim'),mobile=matchMedia('(max-width:760px)');
  let opened=false,profileView=false,epoch=0,profile=null,summary=null,conversationScroll=0;
  const text=(tag,value,className='')=>{const node=document.createElement(tag);node.textContent=value;if(className)node.className=className;return node;};
  function action(label,handler,secondary=false){const button=text('button',label,secondary?'learning-secondary':'learning-primary');button.type='button';button.addEventListener('click',handler);return button;}
  function status(message,error=false){const node=$('profile-page-status');node.textContent=message;node.classList.toggle('error',error);}
  function closeMenu(returnFocus=false){opened=false;syncMenu();if(returnFocus&&mobile.matches)requestAnimationFrame(()=>{if(!opened)menu.focus();});}
  function syncMenu(){
    if(!mobile.matches)opened=false;
    document.body.classList.toggle('sidebar-open',opened);menu.setAttribute('aria-expanded',String(opened));scrim.hidden=!opened;
    rail.inert=mobile.matches&&!opened;$('workspace-shell').inert=mobile.matches&&opened;
    if(mobile.matches&&!opened)rail.setAttribute('aria-hidden','true');else rail.removeAttribute('aria-hidden');
    if(opened){rail.setAttribute('role','dialog');rail.setAttribute('aria-modal','true');}else{rail.removeAttribute('role');rail.removeAttribute('aria-modal');}
  }
  menu.addEventListener('click',()=>{opened=!opened;syncMenu();if(opened)requestAnimationFrame(()=>{if(opened)$('sidebar-close').focus();});});
  rail.addEventListener('transitionend',event=>{if(opened&&event.propertyName==='transform')$('sidebar-close').focus();});
  $('sidebar-close').addEventListener('click',()=>closeMenu(true));scrim.addEventListener('click',()=>closeMenu(true));mobile.addEventListener('change',syncMenu);
  document.addEventListener('keydown',event=>{
    if(!opened)return;if(event.key==='Escape'){event.preventDefault();closeMenu(true);return;}
    if(event.key==='Tab'){const focus=[...rail.querySelectorAll('a[href],button:not(:disabled)')].filter(node=>node.getClientRects().length),first=focus[0],last=focus.at(-1);if(!rail.contains(document.activeElement)){event.preventDefault();first.focus();}else if(event.shiftKey&&document.activeElement===first){event.preventDefault();last.focus();}else if(!event.shiftKey&&document.activeElement===last){event.preventDefault();first.focus();}}
  });
  rail.querySelectorAll('a').forEach(link=>link.addEventListener('click',event=>{if(!['#profil','#conversation'].includes(link.hash))return;event.preventDefault();const same=link.hash===location.hash;closeMenu(same);if(!same)location.hash=link.hash;}));
  $('account-button').addEventListener('click',()=>closeMenu(false));
  $('sidebar-learning').addEventListener('click',()=>{closeMenu(false);onLearning('today');});
  function updateSidebar(value){$('sidebar-profile-detail').textContent=[value.target_language,value.level].filter(Boolean).join(' · ')||'Votre progression';}
  function guest(){content.replaceChildren(text('section','','profile-empty'));content.firstChild.append(text('p','Connectez-vous pour consulter votre profil.'),action('Ouvrir mon compte',onAccount));status('');}
  function list(title,items,empty){const card=document.createElement('section');card.className='profile-card';card.append(text('h2',title));if(!items?.length)card.append(text('p',empty,'profile-muted'));else{const ul=document.createElement('ul');for(const value of items)ul.append(text('li',value));card.append(ul);}return card;}
  function render(){
    const account=getAccount(),name=profile.name||account?.name||'Votre profil',initials=name.split(/\s+/).filter(Boolean).slice(0,2).map(part=>part[0]).join('').toUpperCase();
    content.replaceChildren();
    const hero=document.createElement('section');hero.className='profile-hero';const badge=text('div',initials,'profile-initials');badge.setAttribute('aria-hidden','true');const identity=document.createElement('div');identity.append(text('h2',name),text('p',[profile.target_language||'Langue à choisir',profile.level?'Niveau du profil : '+profile.level:'Niveau à renseigner'].join(' · '),'profile-muted'));hero.append(badge,identity,action('Modifier mon profil',showEdit));content.append(hero);
    const stats=document.createElement('dl');stats.className='profile-stats';for(const [label,value] of [['Activités du plan',summary?(summary.plan.stale?'À actualiser':summary.plan.completed+' / '+summary.plan.total):'—'],['Révisions dues',summary?String(summary.reviews.due):'—'],['Bilans enregistrés',String((profile.assessment_history||[]).length)]]){const block=document.createElement('div');block.append(text('dt',label),text('dd',value));stats.append(block);}content.append(stats);
    const grid=document.createElement('div');grid.className='profile-grid';
    const goals=list('Vos objectifs',profile.goals,'Aucun objectif.');goals.append(action('Ajouter un objectif',()=>showEdit('profile-edit-goal'),true));grid.append(goals);
    const skills=document.createElement('section');skills.className='profile-card';skills.append(text('h2','Vos compétences'));
    for(const [key,label] of Object.entries({vocabulary:'Vocabulaire',grammar:'Grammaire',comprehension:'Compréhension',expression:'Expression'})){
      const row=document.createElement('div');row.className='profile-skill';const score=profile.competency_scores?.[key],valid=typeof score==='number'&&Number.isFinite(score)&&score>=0&&score<=100;
      row.append(text('span',label),text('strong',valid?Math.round(score)+' / 100':'Non évaluée'));
      if(valid){const meter=document.createElement('meter');meter.min=0;meter.max=100;meter.value=score;meter.setAttribute('aria-label',label);row.append(meter);}skills.append(row);
    }skills.append(action('Évaluer mon niveau',()=>onLearning('assessment'),true));grid.append(skills);
    grid.append(list('Vos points forts',profile.strengths,'À découvrir.'),list('À travailler',profile.weak_points,'Aucun point identifié.'));
    const history=document.createElement('section');history.className='profile-card';history.append(text('h2','Vos derniers bilans'));
    const records=(profile.assessment_history||[]).slice(-3).reverse();
    if(!records.length)history.append(text('p','Aucun bilan.','profile-muted'));
    for(const result of records){const record=document.createElement('div');record.className='profile-assessment';record.append(text('strong',result.estimated_level?'Niveau estimé : '+result.estimated_level:'Bilan enregistré'));if(typeof result.overall_score==='number')record.append(text('span',result.overall_score+' / 100'));history.append(record);}
    history.append(text('p','Les bilans sont des estimations.','profile-muted'));grid.append(history);
    const accountCard=document.createElement('section');accountCard.className='profile-card';accountCard.append(text('h2','Votre compte'));
    if(account){accountCard.append(text('p',account.name||'Compte Zéphyr'),text('p',account.email,'profile-muted'));}else accountCard.append(text('p','Profil local sur cette installation.','profile-muted'));
    accountCard.append(action(account?'Ouvrir mon compte':'Informations du compte',onAccount,true));grid.append(accountCard);content.append(grid);
    const foot=document.createElement('div');foot.className='profile-actions';foot.append(action('Reprendre ma séance',()=>onLearning('today')),action('Revenir à la conversation',()=>{location.hash='conversation';},true));content.append(foot);
  }
  function showEdit(focusId='profile-edit-name'){
    if(typeof focusId!=='string')focusId='profile-edit-name';
    if($('profile-edit-form')){$(focusId).focus();return;}
    const form=document.createElement('form');form.id='profile-edit-form';form.className='profile-editor';
    form.innerHTML=`<h2>Modifier mon profil</h2><div class="profile-edit-fields"><label>Votre prénom<input id="profile-edit-name" maxlength="100" autocomplete="given-name"></label><label>Langue étudiée<input id="profile-edit-language" maxlength="100" required placeholder="Ex. anglais, espagnol…"></label><label>Niveau du profil<select id="profile-edit-level"><option value="">Je ne sais pas encore</option><option>A1</option><option>A2</option><option>B1</option><option>B2</option><option>C1</option><option>C2</option></select></label><label>Ajouter un objectif<input id="profile-edit-goal" maxlength="300" placeholder="Ex. parler pendant un voyage"></label></div><p class="profile-muted">Le nom du compte reste inchangé.</p><div><button class="learning-primary" type="submit">Enregistrer les modifications</button><button class="learning-secondary" id="profile-edit-cancel" type="button">Annuler</button></div><p id="profile-edit-status" role="status" class="learning-status"></p>`;
    content.querySelector('.profile-hero').after(form);$('profile-edit-name').value=profile.name||'';$('profile-edit-language').value=profile.target_language||'';$('profile-edit-level').value=profile.level||'';
    $('profile-edit-cancel').addEventListener('click',()=>{form.remove();content.querySelector('.profile-hero button').focus();});
    form.addEventListener('submit',async event=>{
      event.preventDefault();if(!form.reportValidity())return;const message=$('profile-edit-status'),language=$('profile-edit-language').value.trim(),level=$('profile-edit-level').value,goal=$('profile-edit-goal').value.trim();
      if(!language){message.textContent='Indiquez une langue étudiée.';return;}if(!level&&profile.level){message.textContent='Choisissez un niveau pour modifier le niveau existant.';return;}
      const data={name:$('profile-edit-name').value.trim(),target_language:language};if(level)data.level=level;if(goal&&!profile.goals?.includes(goal))data.goal=goal;
      form.querySelectorAll('button,input,select').forEach(node=>node.disabled=true);const token=epoch;message.textContent='Enregistrement…';
      try{const updated=await request('/api/learner/profile',{method:'PUT',body:JSON.stringify(data)});if(token!==epoch||!profileView)return;profile=updated;onProfile(profile);summary=null;render();status('Votre profil est enregistré.');$('profile-page-title').focus();try{summary=await request('/api/learning/today?utc_offset_minutes='+(-new Date().getTimezoneOffset()));if(token===epoch&&profileView)render();}catch{if(token===epoch&&profileView)status('Profil enregistré ; progression temporairement indisponible.',true);}}
      catch(error){if(token===epoch&&profileView){message.textContent=error.message;message.classList.add('error');form.querySelectorAll('button,input,select').forEach(node=>node.disabled=false);}}
    });
    $(focusId).focus();
  }
  async function load(){
    if(!profileView)return;const token=++epoch;if(!isReady()){guest();return;}
    status('Chargement du profil…');content.replaceChildren();
    try{const [data,today]=await Promise.all([request('/api/learner/profile'),request('/api/learning/today?utc_offset_minutes='+(-new Date().getTimezoneOffset())).catch(()=>null)]);if(token!==epoch||!profileView||!isReady())return;profile=data;summary=today;onProfile(profile);render();status(today?'':'Le profil est chargé ; la progression est temporairement indisponible.',!today);}
    catch(error){if(token!==epoch||!profileView)return;status(error.message,true);content.replaceChildren(action('Réessayer',load,true));}
  }
  function route(event){
    const next=location.hash==='#profil';const changed=next!==profileView;if(changed&&next)conversationScroll=window.scrollY;profileView=next;epoch++;
    $('conversation-view').hidden=next;page.hidden=!next;document.body.dataset.page=next?'profile':'conversation';
    $('nav-profile').toggleAttribute('aria-current',next);$('nav-conversation').toggleAttribute('aria-current',!next);for(const id of ['nav-profile','nav-conversation'])if($(id).hasAttribute('aria-current'))$(id).setAttribute('aria-current','page');
    document.title=next?'Mon profil — Zéphyr':'Zéphyr — Votre espace de conversation';closeMenu(false);onViewChange(next);
    if(next){load();if(changed){window.scrollTo(0,0);$('profile-page-title').focus();}}else if(changed||event){if(changed)window.scrollTo(0,conversationScroll);$('conversation-title').focus();}
  }
  window.addEventListener('hashchange',route);syncMenu();route();
  return {refreshIfOpen:()=>{if(!$('profile-edit-form'))return load();},updateSidebar,get visible(){return profileView;}};
};
