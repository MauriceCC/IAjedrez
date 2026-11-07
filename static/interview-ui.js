'use strict';
// Uses the approved layout; original statements are never engine verdicts.
const InterviewUI={
 headers(){
  const h=game.headers;
  document.querySelectorAll('.player-name').forEach((el,i)=>el.textContent=h[i===0?'Black':'White']);
  document.querySelectorAll('.player-meta').forEach((el,i)=>el.textContent='· '+h[i===0?'BlackElo':'WhiteElo']);
  document.querySelector('.board-info > .subtle').textContent=h.Date.replaceAll('.','/');
  document.querySelector('.tree-panel .panel-header .subtle').textContent=(isGemini?'10 min':isInterview?'3+0':'5 min')+' · '+h.Result;
 },
 cards(){return `<div class="demo-intro"><strong>Tu conversación, paso a paso</strong><small>Elige una duda y contrástala</small></div><div class="demo-grid">${[
  ['16.e4','¿Activo el alfil de b7 con 16.e4?','Apertura → ruptura central'],
  ['21.Te2','En 21.Te2 quería activar mi torre. ¿Fue correcto?','Tu intención y el reloj'],
  ['29.Rf1','¿29.Kf1 permite Qh1+ y ganar h3?','Amenaza y mejor defensa'],
  ['45.Cc7','¿Qué alternativas tenía en 45.Nc7?','Final y seguridad de piezas']
 ].map(([move,q,caption])=>`<button class="demo-card" data-question="${esc(q)}"><span class="task-no">${esc(move)}</span><strong>${esc(caption)}</strong><small>${esc(q)}</small></button>`).join('')}</div>`;},
 topic(ply){const t=report?.topics?.[ply];if(!t)return '';return `<div class="lesson-prompt"><strong>${esc(t.title)}</strong><p><b>ChatGPT antes:</b> ${esc(t.original)}</p><p><b>Tu observación:</b> ${esc(t.user)}</p><p><b>Revisión didáctica:</b> ${esc(t.explanation)}</p>${button('Contrastar esta conversación',`data-question="Revisar ${esc(label(ply))}"`)}</div>`;},
 summary(){
  const intro=`<div class="lesson-hero"><span class="eyebrow">Timmy-t (1578) — Kuanynsh (1594) · 1 nov. 2026</span><h3>De tu conversación al tablero</h3><p>Tu partida blitz 3+0, vista desde blancas. Revisa los comentarios de ChatGPT, tus objeciones y las variantes calculadas por Stockfish.</p></div>`;
  const switcher=`<p class="table-foot"><a href="/?game=mauricio">Abrir el estudio anterior: Mauricio0120</a></p>`;
  if(!report)return intro+`<p class="lesson-prompt">Partida completa: 54 jugadas. La conversación original no usó motor. Pulsa Analizar para calcular las 54 decisiones de blancas y contrastar tus dudas; la primera revisión puede tardar unos minutos.</p>${button('Analizar mi partida','data-task="summary"')}${this.cards()}${switcher}`;
  return contextBar()+priorityTable()+`${this.cards()}${this.timeline()}${evidenceNote()}<p class="table-foot">${esc(report.engine)} · calculado ${esc(new Date(report.generated_at).toLocaleString())}. <a href="/api/review/analyze?game=entrevista" data-evidence-download>Descargar evidencia JSON</a></p>${switcher}`;
 },
 timeline(){return `<div class="view-intro"><h3>Desde la apertura hasta el final</h3></div><div class="lesson-actions">${[[1,'1–15 · Apertura'],[31,'16 · Ruptura'],[41,'21 · Torre activa'],[57,'29 · Seguridad del rey'],[77,'39 · Cambio de damas'],[89,'45 · Caballo'],[107,'54 · Final']].map(([ply,text])=>button(text,`data-jump="${ply}"`)).join('')}</div>`;},
 advice(){if(!report)return this.summary();return contextBar()+this.timeline()+`<div class="table-wrap"><table class="results-table"><thead><tr><th>Etapa / jugada</th><th>Stockfish</th><th>Próximo paso</th></tr></thead><tbody>${report.rows.map(r=>`<tr tabindex="0" data-jump="${r.ply}"><td>${esc(r.label)}</td><td>${esc(r.kind)} · ${esc(loss(r))}</td><td>${esc(es(r.best.san[0]))} (${esc(score(r.best))}). Abrir posición y variantes.</td></tr>`).join('')}</tbody></table></div>${evidenceNote()}`;},
 references(){return contextBar()+`<div class="view-intro"><h3>Qué dijo cada fuente</h3></div><p class="lesson-prompt">La conversación se conserva como síntesis atribuida. Stockfish calcula jugadas y variantes; no valida automáticamente toda una explicación en lenguaje natural.</p>${[31,41,57,89].map(ply=>this.topic(ply)).join('')}<div class="resource-row"><a class="link-resource" href="/static/partida-entrevista.pgn" download>Partida completa con relojes (PGN)</a></div><div class="resource-row"><a class="link-resource" href="/static/conversacion-entrevista.md" target="_blank" rel="noopener">Síntesis de la conversación y correcciones</a></div><div class="resource-row"><a class="link-resource" href="https://stockfishchess.org/" target="_blank" rel="noopener">Stockfish · proyecto oficial</a></div>${report?evidenceNote():''}`;}
};

document.addEventListener('click',async event=>{
 const link=event.target.closest('[data-evidence-download]');if(!link)return;
 event.preventDefault();
 if(!report)return;
 const url=URL.createObjectURL(new Blob([JSON.stringify(report,null,2)],{type:'application/json'}));
 const a=document.createElement('a');a.href=url;a.download='stockfish-sTNRsqPl.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
});
