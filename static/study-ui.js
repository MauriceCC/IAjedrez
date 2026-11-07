'use strict';
function moveTypeIcon(row){
 const types={
  'Error grave':['??','#ce3c48'],
  'Error':['?','#d77819'],
  'Imprecisión':['?!','#b18a12'],
  'Permite mate':['#','#823c97'],
  'Pierde mate forzado':['#','#823c97'],
  'Línea de mate':['#','#823c97'],
  'Sin caída importante':['✓','#287b65']
 };
 const [symbol,color]=types[row.kind]||['•','#63758b'];
 return `<span tabindex="0" class="move-icon" role="img" title="${esc(row.kind)}" aria-label="${esc(row.kind)}"><svg viewBox="0 0 36 36" width="36" height="36" aria-hidden="true" focusable="false"><circle cx="18" cy="18" r="17" fill="${color}"/><text x="18" y="24" text-anchor="middle" fill="#fff" font-family="Arial, sans-serif" font-weight="800" font-size="${symbol.length>1?18:23}">${symbol}</text></svg></span>`;
}
function priorityTable(){

 return `<div class="view-intro"><h3>Errores prioritarios</h3></div><p class="table-foot">Ventaja perdida = diferencia entre la mejor alternativa encontrada y tu jugada, con la respuesta del rival. Se expresa en peones de valoración; no significa que hayas perdido esa cantidad de piezas.</p><div class="table-wrap"><table class="results-table priority-table"><thead><tr><th>Jugada</th><th>Tipo</th><th>Ventaja perdida</th><th>Alternativa del motor</th></tr></thead><tbody>${report.ranking.filter(r=>r.priority>=50).map(r=>`<tr tabindex="0" data-jump="${r.ply}"><td><b>${esc(r.label)}</b></td><td>${moveTypeIcon(r)}</td><td>${r.loss_cp===null?`<span>${esc(r.kind)}</span>`:`<strong>${(r.loss_cp/100).toFixed(2)} peones</strong><span class="loss-track" aria-hidden="true"><span style="width:${Math.min(100,r.loss_cp/5)}%"></span></span>`}</td><td><b>${esc(es(r.best.san[0]))}</b><div class="score-comparison">Tu jugada: ${esc(score(r.played))}<br>Alternativa: ${esc(score(r.best))}</div></td></tr>`).join('')||'<tr><td colspan="4">Sin pérdidas superiores al umbral de esta búsqueda.</td></tr>'}</tbody></table></div><p class="table-foot">?! Imprecisión · ? Error · ?? Error grave. Clasificación orientativa.<br>Valoración: + favorece a blancas; − favorece a negras. Ambos valores comparan decisiones desde la misma posición, no el antes y después de la partida. Barras con máximo visual de 5 peones.</p>`;
}
function studyLearning(){
 if(!report)return summary();
 const topics=isInterview?[
  ['Defensa Semieslava · D31',5,'La apertura indicada en tu PGN: 1.d4 c6 2.c4 d5 3.Cc3 e6. Explora cómo se construye el centro antes de la ruptura e4.','https://lichess.org/opening/Semi-Slav_Defense','Explorar la apertura y partidas modelo'],
  ['Ataque doble con peón',31,'Tras 16.e4, revisa la variante de Stockfish: si continúa …Txc3 Dxc3 dxe4, el peón ataca al alfil de d3 y al caballo de f3. Es una posibilidad calculada, no la continuación jugada.','https://lichess.org/training/fork','Practicar ataques dobles'],
  ['Seguridad del caballo',89,'En la partida, 45.Cc7 permitió …Cxc7. Compara Cg7+ y Cc5 con el motor antes de elegir una retirada.','https://lichess.org/training/hangingPiece','Practicar piezas sin defensa']
 ]:[
  ['Apertura de peón de rey',3,'Tu partida comienza 1.e4 e5 2.d3. Estudia desarrollo y control central antes del avance f4; esta referencia corresponde a la familia general de la apertura.','https://lichess.org/opening/Kings_Pawn_Game','Explorar la apertura y partidas modelo'],
  ['Seguridad del rey',17,'Después de 9.Cd2 llegó …Dxg3+ y 10.Re2 fue la única respuesta legal. Revisa cómo los jaques impidieron enrocar y compara las alternativas del motor. En el recurso externo, empieza por patrones de mate y jaques dobles.','https://lichess.org/practice','Estudiar patrones de mate y táctica']
 ];
 return contextBar()+`<div class="lesson-hero"><h3>Aprende de tu partida</h3><p>Explora un tema, ubícalo en el tablero y prueba una alternativa.</p></div>`+topics.map(([title,ply,text,url,link])=>{const row=report.rows.find(r=>r.ply===ply);return `<article class="lesson-prompt"><h3>${esc(title)}</h3><p>${esc(text)}</p><p class="table-foot">Posición vinculada: ${esc(label(ply))}. Candidata calculada: ${esc(es(row.best.san[0]))} · ${esc(score(row.best))}.</p><div class="lesson-actions">${button('Ver en mi partida',`data-topic-position="${ply}"`)}${button('Practicar desde aquí',`data-topic-practice="${ply}"`)}</div><p><a href="${url}" target="_blank" rel="noopener">${esc(link)} ↗</a><small> · Lichess · gratuito</small></p></article>`;}).join('')+`<p class="table-foot">Temas seleccionados para estos dos estudios a partir del PGN y de las variantes del motor. Los recursos externos enseñan el concepto; no analizan tu partida. Puedes cambiar el idioma en Lichess.</p><details><summary>Conversación, fuentes y evidencia</summary>${references()}</details>`;
}
