const {test}=require('node:test');
const assert=require('node:assert/strict');
const {readFileSync}=require('node:fs');
const {runInNewContext}=require('node:vm');
const {join}=require('node:path');
const window={};
runInNewContext(readFileSync(join(__dirname,'../visual-vocabulary.js'),'utf8'),{window});
const {objects,languages,resolveLanguage,buildGeometry}=window.ZephyrVocabulary;

test('Profile languages resolve across accents, names and locales',()=>{
  for(const [input,expected] of [['English','en'],['anglais','en'],['EN-us','en'],['Español','es'],['de_DE','de'],['Português','pt'],['français','fr'],['Italiano','it']])assert.equal(resolveLanguage(input),expected);
});
test('Unknown or missing profile languages never become an English translation',()=>{
  for(const input of [null,undefined,'','bambara','wolof','en-unknown'])assert.equal(resolveLanguage(input),null);
});
test('Every object has a unique identity and a word in each advertised language',()=>{
  assert.ok(objects.length===15);
  assert.equal(new Set(objects.map(item=>item.id)).size,objects.length);
  for(const item of objects){
    assert.ok(item.fr.trim());
    for(const code of Object.keys(languages)){assert.equal(typeof item.words[code],'string');assert.ok(item.words[code].trim());}
  }
  assert.equal(objects.find(item=>item.id==='tree').words.es,'Árbol');
  assert.equal(objects.find(item=>item.id==='house').words.en,'House');
});


test('Every object has bounded, genuinely volumetric geometry',()=>{
  for(const item of objects){
    const points=buildGeometry(item.id,1000);assert.equal(points.length,1000);
    for(const p of points)for(const axis of ['x','y','z'])assert.ok(Number.isFinite(p[axis])&&Math.abs(p[axis])<1.6);
    const spans=['x','y','z'].map(axis=>Math.max(...points.map(p=>p[axis]))-Math.min(...points.map(p=>p[axis])));
    assert.ok(spans.every(span=>span>(['house','tree','cup','book','fish','heart'].includes(item.id)?.4:.1)),`${item.id} must have depth, width and height`);
    const mean=axis=>points.reduce((sum,p)=>sum+p[axis],0)/points.length;
    const center=['x','y','z'].map(mean);
    const cov=(a,b)=>points.reduce((sum,p)=>sum+(p[['x','y','z'][a]]-center[a])*(p[['x','y','z'][b]]-center[b]),0)/points.length;
    const a=cov(0,0),b=cov(0,1),c=cov(0,2),d=cov(1,1),e=cov(1,2),f=cov(2,2);
    assert.ok(a*(d*f-e*e)-b*(b*f-c*e)+c*(b*e-c*d)>.00001,`${item.id} cannot lie in a plane`);
  }
});


test('A shuffled cycle visits every object exactly once and never repeats at a boundary',()=>{
  let seed=123;const random=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296;};
  const values=objects.map(item=>item.id),bag=window.ZephyrVocabulary.createShuffleBag(values,random);let previous;
  for(let cycle=0;cycle<8;cycle++){const drawn=Array.from({length:values.length},()=>bag.next());assert.equal(new Set(drawn).size,values.length);assert.notEqual(drawn[0],previous);previous=drawn.at(-1);assert.notDeepEqual(drawn,values);}
});
test('Random cycles do not mutate their source and reject an empty collection',()=>{
  const source=['a','b','c'];const bag=window.ZephyrVocabulary.createShuffleBag(source,()=>0);for(let i=0;i<12;i++)assert.ok(source.includes(bag.next()));assert.deepEqual(source,['a','b','c']);assert.throws(()=>window.ZephyrVocabulary.createShuffleBag([]));
});
