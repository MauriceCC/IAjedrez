'use strict';
let selection=0,fileRead=0;
const byId=id=>document.getElementById(id);
document.querySelectorAll('[data-game]').forEach(button=>button.onclick=async()=>{
 const request=++selection;
 document.querySelectorAll('.history').forEach(b=>b.classList.toggle('active',b===button));
 byId('status').textContent='Cargando tu conversación…';
 try{
  const response=await fetch('/api/review/game?game='+button.dataset.game);
  if(!response.ok)throw Error('No se pudo cargar la partida. Inténtalo nuevamente.');
  const game=await response.json();if(request!==selection)return;
  const first='Hola Chat gpt, eres experto en ajedrez, podrias indicarme cual fue mi error en esta partida por favor?';
  const second='esta es la partida que jugue y necesito que me indiques los momentos en donde cometi errores clave. Paso a paso desde la apertura hasta el final del juego';
  byId('prompt').textContent=game.study_prompt ? game.study_prompt+'\n\n'+game.followups.map((q,i)=>'Consulta '+(i+2)+': '+q).join('\n\n') : button.dataset.game==='mauricio'?first+'\n\n'+game.pgn:game.pgn+'\n\n'+second;
  byId('chat-title').textContent=game.headers.White+' — '+game.headers.Black;
  byId('open-analysis').href='/?game='+button.dataset.game;
  byId('welcome').hidden=true;byId('conversation').hidden=false;byId('status').textContent='';
  document.querySelector('main').scrollTop=0;
 }catch(error){if(request===selection)byId('status').textContent=error.message;}
});
byId('new-chat').onclick=()=>{selection++;document.querySelector('[name="player-color"][value="white"]').checked=true;byId('welcome').hidden=false;byId('conversation').hidden=true;byId('status').textContent='';document.querySelectorAll('.history').forEach(b=>b.classList.remove('active'));byId('pgn').focus();};

byId('remove-file').onclick=()=>{fileRead++;byId('pgn-file').value='';byId('pgn').value='';byId('file-preview').hidden=true;byId('status').textContent='';byId('send-pgn').disabled=false;byId('pgn').focus();};
byId('pgn').addEventListener('input',()=>{fileRead++;byId('pgn-file').value='';byId('file-preview').hidden=true;byId('send-pgn').disabled=false;});
byId('pgn-file').onchange=async()=>{
 const file=byId('pgn-file').files[0],request=++fileRead,view=selection;
 byId('send-pgn').disabled=false;if(!file)return;
 if(!/\.pgn$/i.test(file.name)){byId('status').textContent='Selecciona un archivo con extensión .pgn.';byId('pgn-file').value='';return;}
 if(file.size>100000){byId('status').textContent='El archivo PGN debe pesar como máximo 100 KB.';byId('pgn-file').value='';return;}
 byId('send-pgn').disabled=true;byId('status').textContent='Leyendo '+file.name+'…';
 try{const text=(await file.text()).replace(/^\uFEFF/,'').trim();if(request!==fileRead||view!==selection)return;
 if(!text)throw Error('El archivo PGN está vacío. Selecciona otra partida.');
 byId('pgn').value=text;byId('file-name').textContent=file.name;byId('file-preview').hidden=false;byId('status').textContent='Archivo '+file.name+' cargado. Pulsa Enviar PGN para analizarlo.';
 }catch(error){if(request===fileRead&&view===selection){byId('status').textContent=error.message;byId('pgn-file').value='';}}
 finally{if(request===fileRead)byId('send-pgn').disabled=false;}
};
byId('pgn-form').onsubmit=async event=>{
 event.preventDefault();const pgn=byId('pgn').value.trim();if(!pgn){byId('status').textContent='Pega una partida en formato PGN.';return;}
 const request=++selection;byId('send-pgn').disabled=true;byId('status').textContent='Validando tu partida…';
 try{const response=await fetch('/api/review/import',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({pgn,player_color:document.querySelector('[name="player-color"]:checked').value})});const result=await response.json();
 if(!response.ok)throw Error(typeof result.detail==='string'?result.detail:'Revisa el formato del PGN.');
 if(request===selection)location.href='/?game='+encodeURIComponent(result.id);
 }catch(error){if(request===selection)byId('status').textContent=error.message;}
 finally{byId('send-pgn').disabled=false;}
};
