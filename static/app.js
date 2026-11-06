const $ = id => document.getElementById(id);
const esc = value => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const symbols = {K:'♔',Q:'♕',R:'♖',B:'♗',N:'♘',P:'♙',k:'♚',q:'♛',r:'♜',b:'♝',n:'♞',p:'♟'};
let moves=[], cursor=0, variation=[], position, sans=[], view='summary', selected='', busy=false, step=0;
let answers={}, analyses={};
const active = () => moves.slice(0,cursor).concat(variation);
const key = () => active().join(' ');
async function api(path, data){const r=await fetch('/api/'+path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});const body=await r.json();if(!r.ok)throw Error(typeof body.detail==='string'?body.detail:'Datos inválidos');return body;}
async function run(work){if(busy)return;busy=true;document.querySelectorAll('button').forEach(b=>b.disabled=true);$('status').textContent='Procesando…';try{await work();$('status').textContent='Listo · cambios conservados en esta sesión. Guarda el estudio para recuperarlos.';}catch(e){$('status').textContent=e.message;}finally{busy=false;document.querySelectorAll('button').forEach(b=>b.disabled=false);$('prev').disabled=cursor===0;$('next').disabled=cursor===moves.length;}}
async function refresh(){position=await api('position',{moves:active()});sans=position.sans;selected='';render();}
function render(){
 $('turn').textContent=position.result?'Resultado '+position.result:'Turno: '+position.turn+(position.check?' · jaque':'');
 $('move-label').textContent=variation.length?'Variante · '+sans.at(-1):(cursor?sans.at(-1):'Posición inicial');
 $('board-help').textContent=view==='learn'?'Selecciona origen y destino. Los destinos legales se resaltan.':'Abre Aprende para probar alternativas legales.';
 $('board').innerHTML='';for(let rank=8;rank>0;rank--)for(let f=0;f<8;f++){const sq='abcdefgh'[f]+rank,p=position.pieces[sq],b=document.createElement('button');b.className='square '+((rank+f)%2?'light':'dark')+(selected===sq?' selected-square':'')+(selected&&position.legal.some(m=>m.startsWith(selected+sq))?' target':'');b.setAttribute('aria-label',sq+(p?' '+p:''));b.innerHTML=p?`<span class="piece ${p===p.toUpperCase()?'white':'black'}">${symbols[p]}</span>`:'';b.onclick=()=>square(sq);$('board').append(b);}
 $('tree').innerHTML='<button class="tree-move" data-index="0">Posición inicial</button>'+moves.map((m,i)=>`<div class="tree-entry ${cursor===i+1?'selected':''}"><button class="tree-move" data-index="${i+1}">${Math.floor(i/2)+1}${i%2?'…':'.'} ${esc(m)} <small>${(answers[moves.slice(0,i+1).join(' ')]||[]).length} consultas</small></button></div>`).join('')+(variation.length?`<div class="branch-wrap">Variante: ${esc(variation.join(' → '))}</div>`:'');renderResults();
}
function renderResults(){
 const labels={summary:'Análisis de la posición',advice:'Consejos',references:'Referencias',chain:'Cadena de aprendizaje',learn:'Aprende'};$('title').textContent=labels[view];const analysis=analyses[key()];let html='';
 if(view==='references')html='<p>Recursos generales, seleccionados manualmente:</p><p><a href="https://lichess.org/learn" target="_blank" rel="noopener">Fundamentos del ajedrez</a></p><p><a href="https://lichess.org/practice" target="_blank" rel="noopener">Práctica de tácticas</a></p>';
 else if(view==='chain')html=['Observar la posición','Identificar amenazas','Comparar alternativas','Extraer una recomendación'].map((s,i)=>`<details ${step===i?'open':''}><summary data-step="${i}">${i+1}. ${s}</summary><p>Pregunta al tutor sobre esta etapa. La respuesta se conserva con esta posición.</p></details>`).join('');
 else if(view==='learn')html='<p>Prueba movimientos legales en el tablero. Puedes explorar varias respuestas y volver a la posición original sin modificar la partida. Analiza cada variante para comparar sus evaluaciones.</p>';
 else if(view==='advice')html='<p>Revisa seguridad del rey, piezas atacadas y control del centro. Son orientaciones generales; consulta al tutor para explicaciones basadas en esta posición.</p>';
 else html='<p>Analiza la posición seleccionada. Las evaluaciones positivas favorecen a blancas. Esta primera versión no clasifica automáticamente los errores de toda la partida.</p>';
 if(analysis)html+=`<p><strong>${esc(analysis.engine)}</strong> · búsqueda limitada a 0,4 s</p>`+analysis.candidates.map(c=>`<p>${c.mate_white!==null?'Mate (blancas): '+c.mate_white:'Evaluación: '+(c.cp_white/100).toFixed(2)} · profundidad ${c.depth}<br>${esc(c.pv.join(' → '))}</p>`).join('');
 html+=(answers[key()]||[]).map(a=>`<div class="query-entry"><strong>Paso ${a.step+1}: ${esc(a.q)}</strong><p>${esc(a.a)}</p></div>`).join('');$('results').innerHTML=html;
}
function square(sq){if(busy||view!=='learn')return;if(!selected){selected=sq;render();return;}const uci=selected+sq;const move=position.legal.find(m=>m===uci)||position.legal.find(m=>m===uci+$('promotion').value);if(move)run(async()=>{variation.push(move);await refresh();});else{selected=sq;render();}}
function changeView(v){view=v;selected='';$('menu').hidden=true;$('toggle').setAttribute('aria-expanded','false');render();}
async function load(pgn){const result=await api('import',{pgn});moves=result.moves;cursor=moves.length;variation=[];answers={};analyses={};await refresh();}
const sample='1. e4 e5 2. Nf3 Nc6 3. Bc4 Bc5 4. c3 Nf6 5. d3 d6 6. O-O O-O 7. Re1 a6 8. Bb3 Ba7 9. Nbd2 Be6 10. Nf1 h6 11. Ng3 Re8 12. h3 d5';
 $('sample').onclick=()=>run(()=>load(sample));$('import').onclick=()=>run(()=>load($('pgn').value));
 $('tree').onclick=e=>{const b=e.target.closest('[data-index]');if(b)run(async()=>{cursor=Number(b.dataset.index);variation=[];await refresh();});};
 $('prev').onclick=()=>run(async()=>{cursor=Math.max(0,cursor-1);variation=[];await refresh();});$('next').onclick=()=>run(async()=>{cursor=Math.min(moves.length,cursor+1);variation=[];await refresh();});
 $('return').onclick=()=>run(async()=>{variation=[];await refresh();});
 $('toggle').onclick=()=>{$('menu').hidden=!$('menu').hidden;$('toggle').setAttribute('aria-expanded',String(!$('menu').hidden));};$('menu').onclick=e=>{if(e.target.dataset.view)changeView(e.target.dataset.view);};$('summary').onclick=()=>changeView('summary');
 $('results').onclick=e=>{if(e.target.dataset.step!==undefined)step=Number(e.target.dataset.step);};
 $('analyze').onclick=()=>run(async()=>{analyses[key()]=await api('analyze',{moves:active()});renderResults();});
 $('ask').onsubmit=e=>{e.preventDefault();run(async()=>{const q=$('question').value.trim();if(!q)return;const result=await api('chat',{moves:active(),question:q,step});(answers[key()]||=[]).push({q,a:result.answer,step});analyses[key()]=result.evidence;$('question').value='';render();});};
 $('export').onclick=()=>{const url=URL.createObjectURL(new Blob([JSON.stringify({version:1,moves,cursor,variation,answers})],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='iajedrez-estudio.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};
 $('restore').onchange=e=>{const file=e.target.files[0];if(file)run(async()=>{if(file.size>2000000)throw Error('Estudio demasiado grande');const d=JSON.parse(await file.text());if(d.version!==1||!Array.isArray(d.moves)||!Array.isArray(d.variation)||!Number.isInteger(d.cursor)||d.cursor<0||d.cursor>d.moves.length)throw Error('Formato de estudio inválido');await api('position',{moves:d.moves});await api('position',{moves:d.moves.slice(0,d.cursor).concat(d.variation)});const clean={};for(const [k,items] of Object.entries(d.answers||{})){if(!Array.isArray(items))throw Error('Consultas inválidas');clean[k]=items.map(a=>({q:String(a.q),a:String(a.a),step:Number.isInteger(a.step)&&a.step>=0&&a.step<4?a.step:0}));}moves=d.moves;variation=d.variation;cursor=d.cursor;answers=clean;analyses={};await refresh();});};
 run(refresh);
