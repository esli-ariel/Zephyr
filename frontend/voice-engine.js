'use strict';
window.ZephyrVoiceEngine=function({settings,Recognition,mediaDevices,AudioContext,synth,Utterance,onState,onTranscript,onResult,onError,onBoundary=()=>{},schedule=setTimeout,cancelTimer=clearTimeout,tools=window.ZephyrVoiceTools}){
  let capture=null,captureToken=0,speechToken=0,speechPending=false,speechTimer=null,currentUtterance=null;
  const blank=()=>({final:'',interim:'',text:''});
  function clearCaptureTimers(context){for(const key of ['pauseTimer','stopTimer'])if(context[key]!=null){cancelTimer(context[key]);context[key]=null;}}
  function release(context){
    clearCaptureTimers(context);
    const recognizer=context.recognizer;
    if(recognizer){for(const key of ['onstart','onresult','onend','onerror','onspeechstart','onspeechend'])recognizer[key]=null;try{recognizer.abort();}catch{}}
    context.stream?.getTracks().forEach(track=>track.stop());
    if(context.audioContext)context.audioContext.close().catch(()=>{});
  }
  function complete(context,error=null){
    if(capture!==context)return;
    const snapshot=context.snapshot;capture=null;captureToken++;release(context);onState('idle');
    if(error)onError(error);
    onResult({...snapshot,error,manual:context.manual});
  }
  function cancelCapture(){
    const context=capture;capture=null;captureToken++;
    if(!context)return blank();
    release(context);onState('idle');return {...context.snapshot};
  }
  function finishCapture(){
    const context=capture;if(!context||context.finishing)return;
    context.manual=true;context.finishing=true;clearCaptureTimers(context);
    if(!context.recognizer){complete(context);return;}
    context.stopTimer=schedule(()=>complete(context),1800);
    try{context.recognizer.stop();}catch{complete(context);}
  }
  function armPause(context){
    if(context.pauseTimer!=null)cancelTimer(context.pauseTimer);
    if(!context.snapshot.text||context.finishing)return;
    context.pauseTimer=schedule(()=>{
      if(capture!==context)return;
      context.finishing=true;context.stopTimer=schedule(()=>complete(context),1800);
      try{context.recognizer.stop();}catch{complete(context);}
    },settings().pauseMs);
  }
  function stopSpeaking(){
    speechToken++;speechPending=false;if(speechTimer!=null)cancelTimer(speechTimer);speechTimer=null;
    currentUtterance=null;synth?.cancel();
  }
  async function start(){
    if(capture)return;stopSpeaking();
    if(!Recognition){onError('recognition-unavailable');return;}
    if(!mediaDevices?.getUserMedia){onError('microphone-unavailable');return;}
    const token=++captureToken;
    const context={snapshot:blank(),manual:false,finishing:false,recognizer:null,stream:null,audioContext:null,pauseTimer:null,stopTimer:null,active:false};
    capture=context;onTranscript(context.snapshot);onState('starting');
    try{
      const stream=await mediaDevices.getUserMedia({audio:{echoCancellation:true,noiseSuppression:true,autoGainControl:true},video:false});
      if(capture!==context||token!==captureToken){stream.getTracks().forEach(track=>track.stop());return;}
      context.stream=stream;
      if(AudioContext){
        try{context.audioContext=new AudioContext();context.audioContext.resume().catch(()=>{});
          if(capture!==context||token!==captureToken){release(context);return;}
          context.analyser=context.audioContext.createAnalyser();context.analyser.fftSize=512;
          context.audioContext.createMediaStreamSource(stream).connect(context.analyser);
          context.audioData=new Uint8Array(context.analyser.fftSize);
        }catch{/* Dictation can continue without the optional visual analyser. */}
      }
      if(capture!==context||token!==captureToken)return;
      const recognizer=new Recognition();context.recognizer=recognizer;
      recognizer.lang=settings().recognitionLanguage;recognizer.continuous=true;recognizer.interimResults=true;recognizer.maxAlternatives=1;
      recognizer.onstart=()=>{if(capture!==context)return;context.active=true;onState('listening');};
      recognizer.onresult=event=>{if(capture!==context)return;context.snapshot=tools.transcript(event.results);onTranscript(context.snapshot);armPause(context);};
      recognizer.onspeechstart=()=>{if(context.pauseTimer!=null){cancelTimer(context.pauseTimer);context.pauseTimer=null;}};
      recognizer.onspeechend=()=>{if(capture===context)armPause(context);};
      recognizer.onend=()=>complete(context);
      recognizer.onerror=event=>complete(context,event.error||'recognition-error');
      recognizer.start();
    }catch(error){if(capture===context&&token===captureToken)complete(context,error.name||'microphone-error');}
  }
  function level(){
    const context=capture;if(!context?.analyser||!context.audioData)return 0;
    context.analyser.getByteTimeDomainData(context.audioData);let sum=0;
    for(const value of context.audioData){const sample=(value-128)/128;sum+=sample*sample;}
    return Math.sqrt(sum/context.audioData.length);
  }
  function speak(text,options){
    cancelCapture();stopSpeaking();
    if(!synth||!Utterance){onError('synthesis-unavailable');return;}
    const parts=tools.chunks(text);if(!parts.length){onState('idle');return;}
    const token=speechToken;speechPending=true;
    function fail(reason){if(token!==speechToken)return;stopSpeaking();onState('idle');onError(reason);}
    function play(index){
      if(token!==speechToken)return;
      if(index>=parts.length){speechPending=false;speechTimer=null;currentUtterance=null;onState('idle');return;}
      const utterance=new Utterance(parts[index]);currentUtterance=utterance;utterance.lang=options.lang;utterance.rate=options.rate;utterance.pitch=options.pitch;utterance.volume=options.volume;if(options.voice)utterance.voice=options.voice;
      speechTimer=schedule(()=>fail('synthesis-timeout'),Math.max(20000,parts[index].length*200/options.rate));
      utterance.onstart=()=>{if(token===speechToken&&currentUtterance===utterance)onState('speaking');};
      utterance.onboundary=()=>{if(token===speechToken&&currentUtterance===utterance)onBoundary();};
      utterance.onend=()=>{if(token!==speechToken||currentUtterance!==utterance)return;if(speechTimer!=null)cancelTimer(speechTimer);speechTimer=null;play(index+1);};
      utterance.onerror=event=>{if(token===speechToken&&currentUtterance===utterance)fail(event.error==='not-allowed'?'synthesis-not-allowed':'synthesis-error');};
      try{synth.speak(utterance);}catch{fail('synthesis-error');}
    }
    play(0);
  }
  return {start,finish:finishCapture,cancel:cancelCapture,speak,silence:stopSpeaking,level,
    get capturing(){return !!capture;},get starting(){return !!capture&&!capture.active;},get speechPending(){return speechPending;}};
};
