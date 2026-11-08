'use strict';
function saveStudyFile(blob,name){
 const url=URL.createObjectURL(blob),link=document.createElement('a');
 link.href=url;link.download=name;link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
document.querySelector('.download-options').addEventListener('click',async event=>{
 const button=event.target.closest('[data-download]');if(!button||!game)return;
 document.querySelector('.download-menu').open=false;
 const name=game.headers.White+'-'+game.headers.Black;
 if(button.dataset.download==='pgn'){
  saveStudyFile(new Blob([game.pgn],{type:'application/x-chess-pgn'}),name+'.pgn');return;
 }
 await document.fonts.ready;
 const canvas=document.createElement('canvas');canvas.width=880;canvas.height=940;
 const ctx=canvas.getContext('2d'),pos=currentPosition();
 ctx.fillStyle='#f4f7fc';ctx.fillRect(0,0,880,940);
 ctx.fillStyle='#19314f';ctx.font='bold 22px "Segoe UI",sans-serif';ctx.fillText(name,40,32);
 ctx.font='16px "Segoe UI",sans-serif';ctx.fillText($('current-move').textContent,40,59);
 for(let rank=8;rank>=1;rank--)for(let file=0;file<8;file++){
  const sq='abcdefgh'[file]+rank,x=40+file*100,y=80+(8-rank)*100;
  const cell=$('board').querySelector(`[data-square="${sq}"]`);
  ctx.fillStyle=getComputedStyle(cell).backgroundColor;ctx.fillRect(x,y,100,100);
  const piece=pos.pieces[sq];if(!piece)continue;
  ctx.font='74px "Segoe UI Symbol",serif';ctx.textAlign='center';ctx.textBaseline='middle';
  if(piece===piece.toUpperCase()){ctx.strokeStyle='#1e2834';ctx.lineWidth=2;ctx.strokeText(symbols[piece],x+50,y+52);ctx.fillStyle='white';}
  else ctx.fillStyle='#1e2834';
  ctx.fillText(symbols[piece],x+50,y+52);
 }
 ctx.font='16px "Segoe UI",sans-serif';ctx.fillStyle='#4b6381';ctx.textAlign='center';ctx.textBaseline='middle';
 for(let i=0;i<8;i++){ctx.fillText('abcdefgh'[i],90+i*100,902);ctx.fillText(String(8-i),20,130+i*100);}
 canvas.toBlob(blob=>{if(blob)saveStudyFile(blob,name+'-tablero.png');},'image/png');
});
document.addEventListener('click',event=>{if(!event.target.closest('.download-menu'))document.querySelector('.download-menu').open=false;});
document.addEventListener('keydown',event=>{if(event.key==='Escape'){const menu=document.querySelector('.download-menu');if(menu.open){menu.open=false;menu.querySelector('summary').focus();}}});
