'use strict';
window.ZephyrAccountUI=function({request,onSignedIn,onSignedOut}){
  const dialog=document.createElement('dialog');dialog.className='learning-dialog account-dialog';dialog.id='account-dialog';dialog.setAttribute('aria-labelledby','account-title');
  dialog.innerHTML=`<header class="learning-header"><div><span class="tag">VOTRE ESPACE PERSONNEL</span><h2 id="account-title">Se connecter</h2></div><button type="button" id="account-close" aria-label="Fermer la fenêtre de compte">×</button></header><p id="account-status" class="learning-status" role="status"></p><div id="account-content"></div>`;
  document.body.append(dialog);const $=id=>dialog.querySelector('#'+id),content=$('account-content'),status=$('account-status'),button=document.getElementById('account-button');
  let user=null,busy=false;
  const text=(tag,value)=>{const node=document.createElement(tag);node.textContent=value;return node;};
  function message(value,error=false){status.textContent=value;status.classList.toggle('error',error);}
  function setBusy(value){busy=value;content.querySelectorAll('button,input').forEach(node=>node.disabled=value);}
  function show(mode='login'){
    if(busy)return;message('');content.replaceChildren();
    if(user){
      $('account-title').textContent='Mon compte';content.append(text('h3',user.name),text('p',user.email));
      const logout=text('button','Se déconnecter');logout.className='learning-primary';logout.type='button';content.append(logout);
      logout.addEventListener('click',async()=>{setBusy(true);message('Déconnexion…');try{await request('/api/auth/logout',{method:'POST'},false);onSignedOut();}catch(error){message(error.message,true);}finally{setBusy(false);}});
    }else{
      const signup=mode==='register';$('account-title').textContent=signup?'Créer mon compte':'Se connecter';
      const form=document.createElement('form');form.className='account-form';
      form.innerHTML=`${signup?'<label for="account-name">Votre prénom</label><input id="account-name" name="name" autocomplete="given-name" maxlength="100" required>':''}
        <label for="account-email">Adresse e-mail</label><input id="account-email" name="email" type="email" autocomplete="email" maxlength="254" required>
        <label for="account-password">Mot de passe</label><input id="account-password" name="password" type="password" autocomplete="${signup?'new-password':'current-password'}" minlength="${signup?15:1}" maxlength="128" required>
        ${signup?'<p class="learning-help">Choisissez une phrase secrète de 15 à 128 caractères.</p><label for="account-confirm">Confirmer le mot de passe</label><input id="account-confirm" type="password" autocomplete="new-password" maxlength="128" required>':''}
        <button class="learning-primary" type="submit">${signup?'Créer mon compte':'Me connecter'}</button>`;
      content.append(form);
      const toggle=text('button',signup?'J’ai déjà un compte':'Créer un compte');toggle.type='button';toggle.className='learning-secondary';toggle.addEventListener('click',()=>show(signup?'login':'register'));content.append(toggle);
      content.append(text('p',signup?'Votre compte sera utilisable immédiatement sur cette installation de Zéphyr. Aucun e-mail de confirmation n’est envoyé.':'La réinitialisation du mot de passe par e-mail n’est pas encore disponible.'));
      form.addEventListener('submit',async event=>{
        event.preventDefault();if(busy||!form.reportValidity())return;
        const password=$('account-password').value;
        if(signup&&password!==$('account-confirm').value){message('Les deux mots de passe ne correspondent pas.',true);return;}
        const payload={email:$('account-email').value.trim(),password};if(signup)payload.name=$('account-name').value.trim();
        setBusy(true);message(signup?'Création de votre compte…':'Connexion…');
        try{await request('/api/auth/'+(signup?'register':'login'),{method:'POST',body:JSON.stringify(payload)},false);onSignedIn();}
        catch(error){message(error.message,true);}
        finally{if($('account-password'))$('account-password').value='';if($('account-confirm'))$('account-confirm').value='';setBusy(false);}
      });
    }
    if(!dialog.open)dialog.showModal();
  }
  $('account-close').addEventListener('click',()=>dialog.close());
  dialog.addEventListener('close',()=>{dialog.querySelectorAll('input[type="password"]').forEach(input=>input.value='');});
  button.addEventListener('click',()=>show());
  return {show,setSession(session){user=session?.user||null;button.setAttribute('aria-label',user?'Ouvrir mon compte':'Se connecter ou créer un compte');document.getElementById('account-button-label').textContent=user?'Mon compte':'Se connecter';},setLegacy(){button.hidden=true;}};
};
