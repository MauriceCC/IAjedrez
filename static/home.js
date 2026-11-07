'use strict';
let selection=0;
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
  byId('prompt').textContent=button.dataset.game==='mauricio'?first+'\n\n'+game.pgn:game.pgn+'\n\n'+second;
  byId('chat-title').textContent=game.headers.White+' — '+game.headers.Black;
  byId('open-analysis').href='/?game='+button.dataset.game;
  byId('welcome').hidden=true;byId('conversation').hidden=false;byId('status').textContent='';
  document.querySelector('main').scrollTop=0;
 }catch(error){if(request===selection)byId('status').textContent=error.message;}
});
byId('new-chat').onclick=()=>{selection++;byId('welcome').hidden=false;byId('conversation').hidden=true;byId('status').textContent='';document.querySelectorAll('.history').forEach(b=>b.classList.remove('active'));byId('pgn').focus();};
