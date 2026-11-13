'use strict';
window.ZephyrAccountUI=function({request,onSignedIn,onSignedOut}){
  const dialog=document.createElement('dialog');dialog.className='learning-dialog account-dialog';dialog.id='account-dialog';dialog.setAttribute('aria-labelledby','account-title');
  dialog.innerHTML=`<div class="auth-layout"><aside class="auth-story" aria-label="Zéphyr, compagnon de langues"><a class="auth-wordmark" href="/ui/">z<span>·</span><b>ZÉPHYR</b></a><div class="auth-constellation" aria-hidden="true"><i></i><i></i><i></i><i></i><span>z</span></div><div class="auth-story-copy"><span class="auth-eyebrow">UN NOUVEAU SOUFFLE</span><h3>Le monde s’ouvre.<br>À vous de parler.</h3><p>Un compagnon pour apprendre,<br>une conversation à la fois.</p></div><div class="auth-story-foot"><span></span> À VOTRE RYTHME, CHAQUE JOUR</div></aside>
  <section class="auth-main"><button type="button" id="account-close" aria-label="Fermer la fenêtre de compte">×</button><div class="auth-mobile-brand">ZÉPHYR<span>VOTRE COMPAGNON DE LANGUES</span></div><header class="auth-heading"><span class="auth-eyebrow">VOTRE ESPACE PERSONNEL</span><h2 id="account-title">Ravi de vous retrouver.</h2><p id="account-subtitle">Reprenez là où votre dernière conversation s’est arrêtée.</p></header><nav id="account-tabs" class="account-tabs" aria-label="Accès au compte"><button id="account-login-tab" type="button" aria-pressed="true">Connexion</button><button id="account-register-tab" type="button" aria-pressed="false">Inscription</button></nav><p id="account-status" class="learning-status" role="status"></p><div id="account-content"></div><div class="auth-bottom"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><rect x="6" y="10" width="12" height="10" rx="2"/><path d="M9 10V7a3 3 0 0 1 6 0v3"/></svg> Un espace personnel pour votre apprentissage.</div></section></div>`;
  document.body.append(dialog);const $=id=>dialog.querySelector('#'+id),content=$('account-content'),status=$('account-status'),button=document.getElementById('account-button');
  let user=null,busy=false,draftEmail='',authenticationRequired=true;
  const text=(tag,value)=>{const node=document.createElement(tag);node.textContent=value;return node;};
  const eye=`<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12Z"/><circle cx="12" cy="12" r="3"/></svg>`;
  function passwordField(id,label,autocomplete,min,help=''){
    return `<div class="auth-field"><label for="${id}">${label}</label><div class="auth-password"><input id="${id}" ${id==='account-password'?'name="password"':''} type="password" autocomplete="${autocomplete}" minlength="${min}" maxlength="128" ${help?'aria-describedby="account-password-help"':''} required><button type="button" class="password-toggle" data-password-target="${id}" aria-controls="${id}" aria-label="Afficher ${id==='account-confirm'?'la confirmation du mot de passe':'le mot de passe'}" aria-pressed="false">${eye}</button></div>${help?`<p id="account-password-help" class="auth-field-help">${help}</p>`:''}</div>`;
  }
  function message(value,error=false){status.textContent=value;status.classList.toggle('error',error);}
  function setBusy(value){busy=value;content.querySelectorAll('button,input').forEach(node=>node.disabled=value);$('account-login-tab').disabled=value;$('account-register-tab').disabled=value;dialog.classList.toggle('auth-busy',value);}
  function show(mode='login'){
    if(busy)return;if($('account-email'))draftEmail=$('account-email').value;message('');content.replaceChildren();
    $('account-tabs').hidden=!!user||!authenticationRequired;
    if(!authenticationRequired){$('account-title').textContent='Votre profil local.';$('account-subtitle').textContent='Votre parcours est conservé sur cette installation.';content.append(text('p','Cette installation utilise un profil local. La connexion à un compte n’y est pas activée.'));}
    else if(user){
      $('account-title').textContent='Votre espace vous attend.';$('account-subtitle').textContent='Vous êtes connecté à votre compte Zéphyr.';content.append(text('h3',user.name),text('p',user.email));
      const logout=text('button','Se déconnecter');logout.className='learning-primary auth-submit';logout.type='button';content.append(logout);
      logout.addEventListener('click',async()=>{setBusy(true);message('Déconnexion…');try{await request('/api/auth/logout',{method:'POST'},false);onSignedOut();}catch(error){message(error.message,true);}finally{setBusy(false);}});
    }else{
      const signup=mode==='register';$('account-title').textContent=signup?'Une nouvelle aventure.':'Ravi de vous retrouver.';
      $('account-subtitle').textContent=signup?'Créez votre espace et faites le premier pas.':'Reprenez là où votre dernière conversation s’est arrêtée.';
      $('account-login-tab').setAttribute('aria-pressed',String(!signup));$('account-register-tab').setAttribute('aria-pressed',String(signup));
      const form=document.createElement('form');form.className='account-form';
      form.innerHTML=`${signup?'<div class="auth-field"><label for="account-name">Votre prénom</label><input id="account-name" name="name" autocomplete="given-name" maxlength="100" placeholder="Comment vous appelez-vous ?" required></div>':''}
        <div class="auth-field"><label for="account-email">Adresse e-mail</label><input id="account-email" name="email" type="email" autocomplete="email" maxlength="254" placeholder="vous@exemple.com" required></div>
        ${passwordField('account-password','Mot de passe',signup?'new-password':'current-password',signup?8:1,signup?'8 caractères minimum. Les phrases de passe sont aussi acceptées.':'')}
        ${signup?passwordField('account-confirm','Confirmer le mot de passe','new-password',8):''}
        <button class="learning-primary auth-submit" type="submit"><span>${signup?'Créer mon compte':'Me connecter'}</span><span aria-hidden="true">↗</span></button>`;
      content.append(form);$('account-email').value=draftEmail;
      form.querySelectorAll('[data-password-target]').forEach(toggle=>toggle.addEventListener('click',()=>{const input=$(toggle.dataset.passwordTarget),visible=input.type==='password';input.type=visible?'text':'password';toggle.setAttribute('aria-pressed',String(visible));toggle.setAttribute('aria-label',(visible?'Masquer ':'Afficher ')+(input.id==='account-confirm'?'la confirmation du mot de passe':'le mot de passe'));}));
      const switchLine=document.createElement('div');switchLine.className='auth-switch';switchLine.append(text('span',signup?'Vous avez déjà un compte ?':'Pas encore de compte ?'));
      const toggle=text('button',signup?'Se connecter':'Créer un compte');toggle.type='button';toggle.addEventListener('click',()=>show(signup?'login':'register'));switchLine.append(toggle);content.append(switchLine);
      const note=text('p',signup?'Votre compte est utilisable immédiatement. Aucun e-mail de confirmation n’est envoyé.':'La réinitialisation du mot de passe par e-mail n’est pas encore disponible.');note.className='auth-note';content.append(note);
      form.addEventListener('submit',async event=>{
        event.preventDefault();if(busy||!form.reportValidity())return;
        const password=$('account-password').value;
        if(signup&&password!==$('account-confirm').value){message('Les deux mots de passe ne correspondent pas.',true);$('account-confirm').focus();return;}
        const payload={email:$('account-email').value.trim(),password};if(signup)payload.name=$('account-name').value.trim();
        setBusy(true);message(signup?'Création de votre compte…':'Connexion…');
        try{await request('/api/auth/'+(signup?'register':'login'),{method:'POST',body:JSON.stringify(payload)},false);onSignedIn();}
        catch(error){message(error.message,true);}
        finally{if($('account-password'))$('account-password').value='';if($('account-confirm'))$('account-confirm').value='';setBusy(false);}
      });
    }
    if(!dialog.open)dialog.showModal();
    if(!user&&authenticationRequired)$(mode==='register'?'account-name':'account-email').focus();
  }
  $('account-close').addEventListener('click',()=>dialog.close());
  $('account-login-tab').addEventListener('click',()=>show('login'));$('account-register-tab').addEventListener('click',()=>show('register'));
  dialog.addEventListener('close',()=>{dialog.querySelectorAll('#account-password,#account-confirm').forEach(input=>{input.value='';input.type='password';});});
  button.addEventListener('click',()=>show());
  return {show,setSession(session){authenticationRequired=true;user=session?.user||null;button.setAttribute('aria-label',user?'Ouvrir mon compte':'Se connecter ou créer un compte');document.getElementById('account-button-label').textContent=user?(user.name||'Mon compte'):'Se connecter';},setLegacy(){authenticationRequired=false;button.hidden=false;button.setAttribute('aria-label','Informations du profil local');document.getElementById('account-button-label').textContent='Profil local';}};
};
