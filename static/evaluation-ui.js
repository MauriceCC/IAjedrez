'use strict';
// Teaching labels built from saved evidence, not official platform classifications.
function teachingType(row){
 if(row.loss_cp===null||row.loss_cp>=50)return row.kind;
 if(row.best.pv[0]===row.move)return 'Mejor jugada';
 return row.loss_cp<=10?'Excelente':'Buena';
}
function moveReason(row){
 const specific={
  entrevista:{31:'Abre la posibilidad de …Txc3 y después …dxe4, con ataque simultáneo al alfil de d3 y al caballo de f3.',41:'La maniobra Te4–e2–c2–c6 busca actividad en la columna abierta. El tiempo consumido se evalúa aparte.',57:'Permite …Dh1+ por la diagonal b7–h1. La línea calculada incluye la captura de h3.',89:'El caballo se retira a c7, casilla controlada por el caballo negro de d5: …Cxc7 pierde la pieza.'},
  gemini:{23:'El caballo captura d5 y el peón e6 puede responder …exd5. Comprueba la pérdida de material.',49:'El enroque permite la táctica …Axf3 contra el caballo y la dama. Las negras jugaron otra respuesta en la partida.',51:'Cxg5 captura la dama, pero …Axd1 captura también la tuya: hay que contar toda la secuencia.'},
  mauricio:{17:'Permite …Dxg3+; el rey debe ir a e2 y pierde el derecho a enrocar.',37:'La torre ataca la dama, pero el rival conserva recursos tácticos. Compara la respuesta calculada con …Td2+, que ocurrió.'}
 };
 if(specific[studyId]?.[row.ply])return specific[studyId][row.ply];
 const reply=row.played.san[1],follow=row.played.san.slice(1,4).map(es).join(' → ');
 if(row.played.mate_white!==null)return `La variante calculada contiene ${score(row.played).toLowerCase()}. Recorre los jaques antes de valorar solo el material.`;
 if(row.loss_cp<50)return `Mantiene una valoración cercana a la candidata del motor.${reply?' La continuación calculada empieza '+follow+'.':''}`;
 if(reply?.includes('x'))return `El rival puede responder ${es(reply)}, una captura${reply.includes('+')?' con jaque':''}. La secuencia ${follow} explica la pérdida de valoración frente a la alternativa.`;
 if(reply?.includes('+'))return `El rival obtiene un jaque con ${es(reply)}. Compara la continuación ${follow} con la defensa de la línea sugerida.`;
 return `Tras esta decisión, el motor encuentra ${follow||'una continuación más favorable al rival'}. La valoración empeora frente a la candidata; recorre ambas líneas para comparar la actividad y el material.`;
}
function suggestionReason(row){
 const san=row.best.san[0],reply=row.best.san[1];
 return `${san.includes('x')?'Captura':san.includes('+')?'Da jaque con':'Prueba'} ${es(san)}${reply?'; la respuesta calculada es '+es(reply):''}. ${row.best.pv[0]===row.move?'Coincide con tu jugada.':'Ofrece '+score(row.best)+' frente a '+score(row.played)+' de la jugada real.'}`;
}
function typeCell(row){
 const kind=teachingType(row);
 return `${moveTypeIcon({...row,kind})}${row.loss_cp===null?`<small>${esc(row.kind)}</small>`:`<small class="loss-value" title="Diferencia estimada entre la alternativa y la jugada real">−${(row.loss_cp/100).toFixed(2)} peones</small><span class="loss-track" aria-hidden="true"><span style="width:${Math.min(100,row.loss_cp/5)}%"></span></span>`}`;
}
function evaluationTable(priority=false){
 const rows=priority?report.ranking.filter(r=>r.priority>=50):report.rows;
 return `<div class="view-intro"><h3>${priority?'Errores prioritarios':'Evaluación de tus jugadas'}</h3></div><div class="table-wrap"><table class="results-table priority-table evaluation-table"><thead><tr><th>Jugada</th><th>Tipo ${typeLegend()}</th><th>${priority?'Explicación':'Consejo'}</th><th>${priority?'Jugada sugerida':'Explicación'}</th></tr></thead><tbody>${rows.map(row=>{
 const reason=moveReason(row),suggestion=suggestionReason(row);
 const preview=(text,heading='')=>`<button type="button" class="cell-preview" data-preview="${row.ply}">${heading}${esc(text)}</button>`;
 const real=`<button class="cell-move" type="button" data-jump="${row.ply}">${esc(row.label)}<small class="eval-score">${esc(score(row.played))}</small></button>`;
 const recommended=`<b>${esc(es(row.best.san[0]))}</b><small class="eval-score">${esc(score(row.best))}</small>`;
 return `<tr class="${focusPly()===row.ply?'highlight-row':''}"><td>${real}</td><td>${typeCell(row)}</td><td>${preview(priority?reason:suggestion)}</td><td>${preview(priority?suggestion:reason,priority?recommended:'')}</td></tr>`;
 }).join('')||'<tr><td colspan="4">No se detectaron pérdidas importantes en esta búsqueda.</td></tr>'}</tbody></table></div>`;
}
async function previewSuggestion(ply){
 const row=report.rows.find(r=>r.ply===ply);if(!row)return;
 const scroll=$('results').scrollTop;
 if(state.line)restoreLine();
 state.cursor=ply;
 await openLine({base:ply-1,moves:row.best.pv,name:'Sugerencia para '+row.label,illustrated:true});
 $('results').scrollTop=scroll;
 revealSelection();
}
function boardArrows(){
 const l=state.line;if(!l?.illustrated)return '';
 // Each arrow is a move in the calculated line; it is not a complete attack map.
 const previous=l.offset>0?l.moves[l.offset-1]:null,next=l.moves[l.offset];
 const point=s=>[('abcdefgh'.indexOf(s[0])+.5)*100,(8-Number(s[1])+.5)*100];
 const arrow=(uci,color,id,dashed)=>{
  if(!uci)return '';const [x1,y1]=point(uci.slice(0,2)),[x2,y2]=point(uci.slice(2,4));
  // Knight paths are bent to make their movement legible.
  const knight=Math.abs(x2-x1)*Math.abs(y2-y1)===20000;
  const path=knight?`M${x1},${y1} L${x1},${y2} L${x2},${y2}`:`M${x1},${y1} L${x2},${y2}`;
  return `<defs><marker id="${id}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="3" markerHeight="3" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10Z" fill="${color}"/></marker></defs><path d="${path}" fill="none" stroke="${color}" stroke-width="12" stroke-linecap="round" opacity=".85" ${dashed?'stroke-dasharray="18 12"':''} marker-end="url(#${id})"/>`;
 };
 return `<svg class="board-arrows" viewBox="0 0 800 800" aria-hidden="true">${arrow(previous,'#185bd5','played-arrow',false)}${arrow(next,'#ce6324','reply-arrow',true)}</svg>`;
}
