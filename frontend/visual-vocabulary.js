'use strict';
// A reviewed offline vocabulary; unsupported languages are never guessed.
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
  objects.push(...[{"id":"apple","fr":"Pomme","words":{"en":"Apple","es":"Manzana","de":"Apfel","it":"Mela","pt":"Maçã","fr":"Pomme"}},{"id":"banana","fr":"Banane","words":{"en":"Banana","es":"Plátano","de":"Banane","it":"Banana","pt":"Banana","fr":"Banane"}},{"id":"pear","fr":"Poire","words":{"en":"Pear","es":"Pera","de":"Birne","it":"Pera","pt":"Pera","fr":"Poire"}},{"id":"car","fr":"Voiture","words":{"en":"Car","es":"Coche","de":"Auto","it":"Automobile","pt":"Carro","fr":"Voiture"}},{"id":"airplane","fr":"Avion","words":{"en":"Airplane","es":"Avión","de":"Flugzeug","it":"Aereo","pt":"Avião","fr":"Avion"}},{"id":"boat","fr":"Bateau","words":{"en":"Boat","es":"Barco","de":"Boot","it":"Barca","pt":"Barco","fr":"Bateau"}},{"id":"rocket","fr":"Fusée","words":{"en":"Rocket","es":"Cohete","de":"Rakete","it":"Razzo","pt":"Foguete","fr":"Fusée"}},{"id":"bicycle","fr":"Vélo","words":{"en":"Bicycle","es":"Bicicleta","de":"Fahrrad","it":"Bicicletta","pt":"Bicicleta","fr":"Vélo"}},{"id":"chair","fr":"Chaise","words":{"en":"Chair","es":"Silla","de":"Stuhl","it":"Sedia","pt":"Cadeira","fr":"Chaise"}},{"id":"table","fr":"Table","words":{"en":"Table","es":"Mesa","de":"Tisch","it":"Tavolo","pt":"Mesa","fr":"Table"}},{"id":"lamp","fr":"Lampe","words":{"en":"Lamp","es":"Lámpara","de":"Lampe","it":"Lampada","pt":"Lâmpada","fr":"Lampe"}},{"id":"key","fr":"Clé","words":{"en":"Key","es":"Llave","de":"Schlüssel","it":"Chiave","pt":"Chave","fr":"Clé"}},{"id":"umbrella","fr":"Parapluie","words":{"en":"Umbrella","es":"Paraguas","de":"Regenschirm","it":"Ombrello","pt":"Guarda-chuva","fr":"Parapluie"}},{"id":"clock","fr":"Horloge","words":{"en":"Clock","es":"Reloj","de":"Uhr","it":"Orologio","pt":"Relógio","fr":"Horloge"}},{"id":"star","fr":"Étoile","words":{"en":"Star","es":"Estrella","de":"Stern","it":"Stella","pt":"Estrela","fr":"Étoile"}},{"id":"moon","fr":"Lune","words":{"en":"Moon","es":"Luna","de":"Mond","it":"Luna","pt":"Lua","fr":"Lune"}},{"id":"flower","fr":"Fleur","words":{"en":"Flower","es":"Flor","de":"Blume","it":"Fiore","pt":"Flor","fr":"Fleur"}},{"id":"bottle","fr":"Bouteille","words":{"en":"Bottle","es":"Botella","de":"Flasche","it":"Bottiglia","pt":"Garrafa","fr":"Bouteille"}},{"id":"hat","fr":"Chapeau","words":{"en":"Hat","es":"Sombrero","de":"Hut","it":"Cappello","pt":"Chapéu","fr":"Chapeau"}},{"id":"castle","fr":"Château","words":{"en":"Castle","es":"Castillo","de":"Schloss","it":"Castello","pt":"Castelo","fr":"Château"}},{"id":"bridge","fr":"Pont","words":{"en":"Bridge","es":"Puente","de":"Brücke","it":"Ponte","pt":"Ponte","fr":"Pont"}},{"id":"teapot","fr":"Théière","words":{"en":"Teapot","es":"Tetera","de":"Teekanne","it":"Teiera","pt":"Bule","fr":"Théière"}},{"id":"ball","fr":"Balle","words":{"en":"Ball","es":"Pelota","de":"Ball","it":"Palla","pt":"Bola","fr":"Balle"}},{"id":"diamond","fr":"Diamant","words":{"en":"Diamond","es":"Diamante","de":"Diamant","it":"Diamante","pt":"Diamante","fr":"Diamant"}},{"id":"drum","fr":"Tambour","words":{"en":"Drum","es":"Tambor","de":"Trommel","it":"Tamburo","pt":"Tambor","fr":"Tambour"}},{"id":"snowman","fr":"Bonhomme de neige","words":{"en":"Snowman","es":"Muñeco de nieve","de":"Schneemann","it":"Pupazzo di neve","pt":"Boneco de neve","fr":"Bonhomme de neige"}},{"id":"globe","fr":"Globe","words":{"en":"Globe","es":"Globo terráqueo","de":"Globus","it":"Mappamondo","pt":"Globo terrestre","fr":"Globe"}},{"id":"camera","fr":"Appareil photo","words":{"en":"Camera","es":"Cámara","de":"Kamera","it":"Fotocamera","pt":"Câmera","fr":"Appareil photo"}},{"id":"guitar","fr":"Guitare","words":{"en":"Guitar","es":"Guitarra","de":"Gitarre","it":"Chitarra","pt":"Guitarra","fr":"Guitare"}},{"id":"pineapple","fr":"Ananas","words":{"en":"Pineapple","es":"Piña","de":"Ananas","it":"Ananas","pt":"Abacaxi","fr":"Ananas"}}]);
  function resolveLanguage(value){
    const normalized=String(value||'').trim().toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'');
    return Object.keys(languages).find(code=>languages[code].aliases.includes(normalized)||new RegExp('^'+code+'[-_][a-z]{2}$').test(normalized))||null;
  }
  // Surface samples of volumetric primitives, not a flat silhouette with jitter.
  function buildGeometry(id,count=2100,partsOnly=false){
    let seed=Array.from(id).reduce((sum,char)=>sum+char.charCodeAt(0),941);
    const random=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296;};
    const signed=()=>random()*2-1;
    const triangle=(a,b,c)=>{const u=Math.sqrt(random()),v=random();return {x:(1-u)*a[0]+u*(1-v)*b[0]+u*v*c[0],y:(1-u)*a[1]+u*(1-v)*b[1]+u*v*c[1]};};
    function sample(part){
      let x=0,y=0,z=0;
      const angle=random()*(part.arc||Math.PI*2);
      if(part.kind==='sphere'){
        y=signed();const r=Math.sqrt(1-y*y);x=r*Math.cos(angle);z=r*Math.sin(angle);
      }else if(part.kind==='box'){
        x=signed();y=signed();z=signed();const axis=Math.floor(random()*3),side=random()<.5?-1:1;
        if(axis===0)x=side;else if(axis===1)y=side;else z=side;
      }else if(part.kind==='cylinder'){
        const cap=part.caps!==false&&random()<.2,r=cap?Math.sqrt(random()):1;
        x=r*Math.cos(angle);z=r*Math.sin(angle);y=cap?(random()<.5?-1:1):signed();
      }else if(part.kind==='cone'){
        y=signed();const r=(1+y)/2;x=r*Math.cos(angle);z=r*Math.sin(angle);
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
      x*=scale[0];y*=scale[1];z*=scale[2];
      const [rx,ry,rz]=part.rotate||[0,0,0];
      [y,z]=[y*Math.cos(rx)-z*Math.sin(rx),y*Math.sin(rx)+z*Math.cos(rx)];
      [x,z]=[x*Math.cos(ry)+z*Math.sin(ry),-x*Math.sin(ry)+z*Math.cos(ry)];
      [x,y]=[x*Math.cos(rz)-y*Math.sin(rz),x*Math.sin(rz)+y*Math.cos(rz)];
      return {x:x+center[0],y:y+center[1],z:z+center[2]};
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
    const P=(kind,weight,scale,center=[0,0,0],extra={})=>({kind,weight,scale,center,...extra});
    const box=(w,s,c,e)=>P('box',w,s,c,e),sphere=(w,s,c)=>P('sphere',w,s,c),cylinder=(w,s,c,e)=>P('cylinder',w,s,c,e),cone=(w,s,c,e)=>P('cone',w,s,c,e),torus=(w,s,c,e={})=>P('torus',w,s,c,{tube:.14,...e});
    const legs=(height=.5,top=.42,width=.45)=>[-1,1].flatMap(x=>[-1,1].map(z=>box(6,[.065,height,.065],[x*width,top,z*width])));
    Object.assign(models,{
      apple:[sphere(85,[.62,.58,.55],[0,.12,0]),cylinder(7,[.055,.20,.055],[.02,-.57,0],{rotate:[0,0,.2]}),sphere(8,[.25,.07,.12],[.22,-.64,0])],
      banana:[torus(100,[.75,.75,.95],[-.08,-.25,0],{tube:.25,arc:2.8,rotate:[0,0,.25]})],
      pear:[sphere(68,[.59,.57,.52],[0,.36,0]),sphere(25,[.32,.48,.32],[0,-.19,0]),cylinder(7,[.045,.18,.045],[.02,-.75,0],{rotate:[0,0,.18]})],
      car:[box(45,[.84,.26,.38],[0,.25,0]),box(25,[.46,.25,.32],[-.09,-.22,0]),...[-.51,.51].flatMap(x=>[-.39,.39].map(z=>cylinder(7.5,[.21,.10,.21],[x,.48,z],{rotate:[Math.PI/2,0,0]})))],
      airplane:[sphere(45,[.18,.16,1],[0,0,0]),box(30,[.98,.045,.28],[0,0,.08]),box(15,[.49,.035,.17],[0,-.05,-.72]),box(10,[.035,.29,.17],[0,-.27,-.73])],
      boat:[sphere(45,[.85,.22,.39],[0,.58,0]),cylinder(10,[.035,.74,.035],[0,-.18,0]),P('prism',35,[1,1,1],[0,0,0],{outline:[[.06,-.90],[.06,.36],[.74,.36]],depth:.10}),P('prism',10,[1,1,1],[0,0,0],{outline:[[-.06,-.7],[-.06,.32],[-.47,.32]],depth:.10})],
      rocket:[cylinder(45,[.30,.62,.30],[0,.02,0]),cone(22,[.30,.29,.30],[0,-.86,0]),...[-1,1].map(x=>P('prism',12,[1,1,1],[0,0,0],{outline:[[x*.26,.20],[x*.62,.76],[x*.26,.66]],depth:.2})),cone(9,[.18,.28,.18],[0,.90,0],{rotate:[0,0,Math.PI]})],
      bicycle:[...[-.64,.64].map(x=>torus(23,[.40,.40,.40],[x,.38,0],{tube:.14})),cylinder(12,[.04,.40,.04],[-.28,.01,0],{rotate:[0,0,-.55]}),cylinder(12,[.04,.43,.04],[.24,.01,0],{rotate:[0,0,.65]}),cylinder(10,[.04,.45,.04],[0,-.22,0],{rotate:[0,0,Math.PI/2]}),box(10,[.22,.045,.24],[-.22,-.43,0]),box(10,[.16,.045,.24],[.50,-.47,0])],
      chair:[box(28,[.52,.08,.45],[0,.10,0]),box(24,[.52,.47,.07],[0,-.42,-.41]),...legs(.38,.54,.43)],
      table:[box(60,[.84,.09,.59],[0,-.28,0]),...legs(.53,.34,.49)],
      lamp:[cylinder(18,[.43,.05,.43],[0,.78,0]),cylinder(14,[.045,.58,.045],[0,.15,0]),cone(68,[.68,.42,.68],[0,-.55,0])],
      key:[torus(55,[.40,.40,.64],[-.42,-.31,0],{tube:.20}),box(25,[.065,.59,.10],[.02,.28,0],{rotate:[0,0,-.58]}),box(10,[.17,.065,.13],[.40,.61,0]),box(10,[.17,.065,.13],[.24,.38,0])],
      umbrella:[sphere(65,[.90,.25,.70],[0,-.38,0]),cylinder(20,[.045,.56,.045],[0,.27,0]),torus(15,[.18,.18,.26],[.15,.83,0],{tube:.22,arc:Math.PI})],
      clock:[cylinder(70,[.73,.16,.73],[0,0,0],{rotate:[Math.PI/2,0,0]}),box(15,[.035,.27,.06],[0,-.23,.19]),box(15,[.26,.035,.06],[.22,0,.19])],
      star:Array.from({length:10},(_,i)=>{const vertex=n=>{const angle=n*Math.PI/5-Math.PI/2,r=n%2?.42:.91;return [Math.cos(angle)*r,Math.sin(angle)*r];};return P('prism',10,[1,1,1],[0,0,0],{outline:[[0,0],vertex(i),vertex((i+1)%10)],depth:.5});}),
      moon:[torus(100,[.72,.72,.95],[0,0,0],{tube:.25,arc:4.6,rotate:[0,0,.84]})],
      flower:[cylinder(15,[.04,.50,.04],[0,.55,0]),sphere(10,[.30,.075,.12],[.23,.45,0]),sphere(15,[.22,.22,.30],[0,-.33,.05]),...Array.from({length:6},(_,i)=>{const a=i*Math.PI/3;return sphere(10,[.28,.28,.23],[Math.cos(a)*.39,-.33+Math.sin(a)*.39,0]);})],
      bottle:[cylinder(58,[.36,.59,.36],[0,.33,0]),sphere(22,[.36,.27,.36],[0,-.26,0]),cylinder(15,[.14,.27,.14],[0,-.66,0]),cylinder(5,[.17,.055,.17],[0,-.95,0])],
      hat:[cylinder(35,[.92,.045,.69],[0,.38,0]),cylinder(50,[.48,.36,.43],[0,-.02,0]),torus(15,[.48,.43,.43],[0,.20,0],{horizontal:true,tube:.08})],
      castle:[box(35,[.56,.52,.44],[0,.25,0]),...[-.70,.70].flatMap(x=>[cylinder(20,[.24,.70,.24],[x,.08,0]),cone(10,[.28,.24,.28],[x,-.86,0])]),box(5,[.15,.27,.04],[0,.50,.47])],
      bridge:[box(40,[1.03,.10,.34],[0,.10,0]),...[-.77,.77].map(x=>box(20,[.14,.41,.34],[x,.51,0])),...[-.35,.35].map(x=>torus(10,[.35,.38,.35],[x,.38,0],{tube:.14,arc:Math.PI,rotate:[0,0,Math.PI]}))],
      teapot:[sphere(50,[.55,.46,.48],[0,.16,0]),cylinder(12,[.38,.035,.36],[0,-.34,0]),sphere(5,[.10,.08,.10],[0,-.45,0]),torus(16,[.35,.36,.30],[-.56,.08,0],{tube:.17}),cone(17,[.15,.45,.16],[.60,-.05,0],{rotate:[0,0,.72]})],
      ball:[sphere(100,[.77,.77,.77],[0,0,0])],
      diamond:[cone(55,[.78,.30,.78],[0,-.30,0]),cone(45,[.78,.52,.78],[0,.52,0],{rotate:[0,0,Math.PI]})],
      drum:[cylinder(70,[.65,.45,.65],[0,0,0]),...[-.45,.45].map(y=>torus(15,[.66,.66,.66],[0,y,0],{tube:.055,horizontal:true}))],
      snowman:[sphere(45,[.56,.54,.51],[0,.54,0]),sphere(35,[.43,.41,.40],[0,-.21,0]),sphere(20,[.29,.28,.28],[0,-.82,0])],
      globe:[sphere(65,[.61,.61,.61],[0,-.21,0]),torus(15,[.72,.72,.72],[0,-.21,0],{tube:.025,rotate:[0,.35,.2]}),cylinder(8,[.055,.20,.055],[0,.62,0]),cylinder(12,[.42,.045,.30],[0,.86,0])],
      camera:[box(65,[.66,.42,.25],[0,.10,0]),cylinder(20,[.30,.10,.30],[0,.10,.35],{rotate:[Math.PI/2,0,0]}),torus(10,[.30,.30,.30],[0,.10,.47],{tube:.08}),box(5,[.16,.09,.15],[.34,-.39,0])],
      guitar:[sphere(37,[.40,.40,.25],[0,.60,0]),sphere(28,[.30,.28,.22],[0,.17,0]),box(23,[.075,.58,.075],[0,-.50,0]),box(7,[.13,.17,.10],[0,-1.13,0]),box(5,[.15,.025,.03],[0,.67,.26])],
      pineapple:[sphere(76,[.45,.61,.40],[0,.24,0]),...[-.45,0,.45].map(a=>cone(8,[.12,.40,.13],[a*.4,-.67,0],{rotate:[0,0,a]}))],
    });
    models.house.push(box(4,[.12,.23,.025],[0,.59,.53]),box(3,[.11,.10,.025],[-.32,.20,.53]),box(3,[.11,.10,.025],[.32,.20,.53]));

    const parts=models[id];if(!parts)throw new Error('Unknown visual object: '+id);
    if(partsOnly)return parts;
    const total=parts.reduce((sum,p)=>sum+p.weight,0);
    return Array.from({length:count},()=>{
      let selection=random()*total;let part=parts[parts.length-1];
      for(const candidate of parts){selection-=candidate.weight;if(selection<0){part=candidate;break;}}
      return sample(part);
    });
  }

  function createShuffleBag(values,random=Math.random){
    if(!values.length)throw new Error('An object collection cannot be empty.');
    const source=[...values];let bag=[],previous;
    return {next(){if(!bag.length){bag=[...source];for(let i=bag.length-1;i>0;i--){const j=Math.floor(random()*(i+1));[bag[i],bag[j]]=[bag[j],bag[i]];}if(bag.length>1&&bag.at(-1)===previous)[bag[0],bag[bag.length-1]]=[bag.at(-1),bag[0]];}previous=bag.pop();return previous;}};
  }
  return {languages,objects,resolveLanguage,buildGeometry,getModelParts:id=>buildGeometry(id,0,true),createShuffleBag};
})();
