'use strict';
// A small reviewed offline vocabulary; unsupported languages are never guessed.
window.ZephyrVocabulary = (() => {
  const languages = {
    en:{name:'Anglais',profile:'anglais',speech:'en-GB',aliases:['en','english','anglais']},
    es:{name:'Espagnol',profile:'espagnol',speech:'es-ES',aliases:['es','spanish','espagnol','espanol']},
    de:{name:'Allemand',profile:'allemand',speech:'de-DE',aliases:['de','german','allemand','deutsch']},
    it:{name:'Italien',profile:'italien',speech:'it-IT',aliases:['it','italian','italien','italiano']},
    pt:{name:'Portugais',profile:'portugais',speech:'pt-BR',aliases:['pt','portuguese','portugais','portugues']},
    fr:{name:'Français',profile:'français',speech:'fr-FR',aliases:['fr','french','francais']},
  };
  const objects = [
    {id:'house',fr:'Maison',words:{en:'House',es:'Casa',de:'Haus',it:'Casa',pt:'Casa',fr:'Maison'}},
    {id:'tree',fr:'Arbre',words:{en:'Tree',es:'Árbol',de:'Baum',it:'Albero',pt:'Árvore',fr:'Arbre'}},
    {id:'cup',fr:'Tasse',words:{en:'Cup',es:'Taza',de:'Tasse',it:'Tazza',pt:'Xícara',fr:'Tasse'}},
    {id:'book',fr:'Livre',words:{en:'Book',es:'Libro',de:'Buch',it:'Libro',pt:'Livro',fr:'Livre'}},
    {id:'fish',fr:'Poisson',words:{en:'Fish',es:'Pez',de:'Fisch',it:'Pesce',pt:'Peixe',fr:'Poisson'}},
    {id:'heart',fr:'Cœur',words:{en:'Heart',es:'Corazón',de:'Herz',it:'Cuore',pt:'Coração',fr:'Cœur'}},
  ];
  function resolveLanguage(value){
    const normalized=String(value||'').trim().toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'');
    return Object.keys(languages).find(code=>languages[code].aliases.includes(normalized)||new RegExp('^'+code+'[-_][a-z]{2}$').test(normalized))||null;
  }
  // Surface samples of volumetric primitives, not a flat silhouette with jitter.
  function buildGeometry(id,count=2100){
    let seed=Array.from(id).reduce((sum,char)=>sum+char.charCodeAt(0),941);
    const random=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296;};
    const signed=()=>random()*2-1;
    const triangle=(a,b,c)=>{const u=Math.sqrt(random()),v=random();return {x:(1-u)*a[0]+u*(1-v)*b[0]+u*v*c[0],y:(1-u)*a[1]+u*(1-v)*b[1]+u*v*c[1]};};
    function sample(part){
      let x=0,y=0,z=0;
      const angle=random()*Math.PI*2;
      if(part.kind==='sphere'){
        y=signed();const r=Math.sqrt(1-y*y);x=r*Math.cos(angle);z=r*Math.sin(angle);
      }else if(part.kind==='box'){
        x=signed();y=signed();z=signed();const axis=Math.floor(random()*3),side=random()<.5?-1:1;
        if(axis===0)x=side;else if(axis===1)y=side;else z=side;
      }else if(part.kind==='cylinder'){
        const cap=part.caps!==false&&random()<.2,r=cap?Math.sqrt(random()):1;
        x=r*Math.cos(angle);z=r*Math.sin(angle);y=cap?(random()<.5?-1:1):signed();
      }else if(part.kind==='torus'){
        const v=random()*Math.PI*2,r=1+part.tube*Math.cos(v);
        x=r*Math.cos(angle);y=r*Math.sin(angle);z=part.tube*Math.sin(v);
        if(part.horizontal){const swap=y;y=z;z=swap;}
      }else if(part.kind==='prism'){
        if(random()<.55){const p=triangle(...part.outline);x=p.x;y=p.y;z=(random()<.5?-1:1)*part.depth/2;}
        else{const i=Math.floor(random()*3),a=part.outline[i],b=part.outline[(i+1)%3],u=random();x=a[0]*(1-u)+b[0]*u;y=a[1]*(1-u)+b[1]*u;z=signed()*part.depth/2;}
      }else if(part.kind==='heart'){
        // Inflated front/back surfaces of a heart, with a curved depth profile.
        const radial=Math.sqrt(random()),t=angle;
        x=Math.pow(Math.sin(t),3)*radial;
        y=-(13*Math.cos(t)-5*Math.cos(2*t)-2*Math.cos(3*t)-Math.cos(4*t))/16*radial;
        z=(random()<.5?-1:1)*.44*Math.sqrt(1-radial*radial);
      }
      const scale=part.scale||[1,1,1],center=part.center||[0,0,0];
      return {x:x*scale[0]+center[0],y:y*scale[1]+center[1],z:z*scale[2]+center[2]};
    }
    const models={
      house:[
        {kind:'box',weight:58,scale:[.56,.48,.51],center:[0,.35,0]},
        {kind:'prism',weight:32,outline:[[-.74,-.12],[0,-.9],[.74,-.12]],depth:1.16},
        {kind:'box',weight:10,scale:[.10,.26,.12],center:[.36,-.68,.10]},
      ],
      tree:[
        {kind:'cylinder',weight:18,scale:[.12,.55,.12],center:[0,.40,0]},
        {kind:'sphere',weight:38,scale:[.61,.57,.57],center:[0,-.40,0]},
        {kind:'sphere',weight:22,scale:[.42,.39,.41],center:[-.37,-.15,.06]},
        {kind:'sphere',weight:22,scale:[.42,.39,.41],center:[.37,-.18,-.05]},
      ],
      cup:[
        {kind:'cylinder',weight:48,caps:false,scale:[.48,.53,.48],center:[-.16,.07,0]},
        {kind:'cylinder',weight:16,caps:false,scale:[.41,.47,.41],center:[-.16,.02,0]},
        {kind:'torus',weight:14,horizontal:true,tube:.075,scale:[.45,.45,.45],center:[-.16,-.46,0]},
        {kind:'torus',weight:18,tube:.18,scale:[.34,.39,.34],center:[.48,.03,0]},
        {kind:'cylinder',weight:4,scale:[.48,.035,.48],center:[-.16,.60,0]},
      ],
      book:[
        {kind:'box',weight:30,scale:[.55,.73,.025],center:[0,0,-.25]},
        {kind:'box',weight:30,scale:[.55,.73,.025],center:[0,0,.25]},
        {kind:'box',weight:30,scale:[.49,.68,.22],center:[.015,0,0]},
        {kind:'box',weight:10,scale:[.045,.73,.25],center:[-.55,0,0]},
      ],
      fish:[
        {kind:'sphere',weight:70,scale:[.70,.34,.30],center:[.12,0,0]},
        {kind:'prism',weight:17,outline:[[-.5,0],[-1,-.47],[-1,.47]],depth:.14},
        {kind:'prism',weight:9,outline:[[-.2,-.2],[.04,-.64],[.35,-.2]],depth:.12},
        {kind:'sphere',weight:2,scale:[.065,.065,.04],center:[.52,-.10,.26]},
        {kind:'sphere',weight:2,scale:[.065,.065,.04],center:[.52,-.10,-.26]},
      ],
      heart:[{kind:'heart',weight:100,scale:[.82,.82,1],center:[0,-.04,0]}],
    };
    const parts=models[id];if(!parts)throw new Error('Unknown visual object: '+id);
    const total=parts.reduce((sum,p)=>sum+p.weight,0);
    return Array.from({length:count},()=>{
      let selection=random()*total;let part=parts[parts.length-1];
      for(const candidate of parts){selection-=candidate.weight;if(selection<0){part=candidate;break;}}
      return sample(part);
    });
  }

  return {languages,objects,resolveLanguage,buildGeometry};
})();
