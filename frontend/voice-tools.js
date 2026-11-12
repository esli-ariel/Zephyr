'use strict';
window.ZephyrVoiceTools=(()=>{
  const locales={
    'fr-FR':{label:'Français',sample:'Bonjour, je suis Zéphyr. Prenons le temps de parler et d’apprendre ensemble.'},
    'en-GB':{label:'Anglais britannique',sample:'Hello, I am Zephyr. Let us practise a language together, one conversation at a time.'},
    'en-US':{label:'Anglais américain',sample:'Hello, I am Zephyr. Let us practise a language together, one conversation at a time.'},
    'es-ES':{label:'Espagnol',sample:'Hola, soy Zéphyr. Vamos a aprender juntos, una conversación a la vez.'},
    'de-DE':{label:'Allemand',sample:'Hallo, ich bin Zéphyr. Gemeinsam lernen wir, ein Gespräch nach dem anderen.'},
    'it-IT':{label:'Italien',sample:'Ciao, sono Zéphyr. Impariamo insieme, una conversazione alla volta.'},
    'pt-BR':{label:'Portugais',sample:'Olá, sou Zéphyr. Vamos aprender juntos, uma conversa de cada vez.'},
  };
  const defaults={recognitionLanguage:'fr-FR',speechLanguage:'fr-FR',rate:.95,pitch:1,volume:1,pauseMs:1600,autoSend:true,voices:{}};
  function normalize(value){
    value=value&&typeof value==='object'?value:{};
    const number=(key,min,max)=>typeof value[key]==='number'&&Number.isFinite(value[key])?Math.max(min,Math.min(max,value[key])):defaults[key];
    const language=key=>value[key]==='profile'||Object.hasOwn(locales,value[key])?value[key]:defaults[key];
    const voices={};if(value.voices&&typeof value.voices==='object')for(const lang of Object.keys(locales))if(typeof value.voices[lang]==='string')voices[lang]=value.voices[lang].slice(0,512);
    return {recognitionLanguage:language('recognitionLanguage'),speechLanguage:language('speechLanguage'),rate:number('rate',.7,1.4),pitch:number('pitch',.8,1.2),volume:number('volume',0,1),pauseMs:Math.round(number('pauseMs',900,3500)),autoSend:typeof value.autoSend==='boolean'?value.autoSend:true,voices};
  }
  function resolve(language,profileLanguage){return language==='profile'?(Object.hasOwn(locales,profileLanguage)?profileLanguage:'fr-FR'):Object.hasOwn(locales,language)?language:'fr-FR';}
  function transcript(results){
    const final=[],interim=[];
    for(let i=0;i<results.length;i++){const result=results[i],text=String(result?.[0]?.transcript||'').trim();if(text)(result.isFinal?final:interim).push(text);}
    const clean=parts=>parts.join(' ').replace(/\s+/g,' ').trim();
    const confirmed=clean(final),provisional=clean(interim);
    return {final:confirmed,interim:provisional,text:clean([confirmed,provisional])};
  }
  function combineTranscript(existing,snapshot){
    const final=[String(existing||'').trim(),String(snapshot.final||'').trim()].filter(Boolean).join(' ');
    const interim=String(snapshot.interim||'').trim();
    return {final,interim,text:[final,interim].filter(Boolean).join(' ')};
  }
  function shouldAutoSend(snapshot,enabled){return !!enabled&&!snapshot.error&&!!snapshot.final&&!snapshot.interim;}
  function chunks(value,max=230){
    let text=String(value||'').replace(/[*#`]/g,'').replace(/\s+/g,' ').trim();const result=[];
    while(text.length>max){
      const head=text.slice(0,max+1);let cut=Math.max(head.lastIndexOf('. '),head.lastIndexOf('? '),head.lastIndexOf('! '),head.lastIndexOf('; '));
      if(cut<max*.4)cut=head.lastIndexOf(' ');else cut++;
      if(cut<=0)cut=max;
      result.push(text.slice(0,cut).trim());text=text.slice(cut).trim();
    }
    if(text)result.push(text);return result;
  }
  return {locales,defaults,normalize,resolve,transcript,chunks,shouldAutoSend,combineTranscript};
})();
