"""Bounded review of the Gemini conversation; evaluations come from UCI."""
import hashlib
import io
import re
import unicodedata
from pathlib import Path
from datetime import datetime, timezone
import chess
import chess.engine
import chess.pgn
import review as core
import history_evidence

GAME_PATH = Path(__file__).parent / 'static/partida-gemini.pgn'
_cache = {}
NOTATION = [
    'El tablero tiene columnas a–h y filas 1–8 vistas desde blancas. PGN usa K/Q/R/B/N; en español corresponden a R/D/T/A/C. El peón no lleva letra.',
    '12.Nxd5 / Cxd5: el caballo captura en d5. 12…exd5: el peón de la columna e captura ese caballo. 14…Nxb5 captura un peón blanco, no una pieza menor.',
    '15.Bxb5+ / Axb5+: el alfil captura el caballo de b5 y da jaque. 25.O-O: enroque corto. 27.Rfxd1 / Tfxd1: la torre de la columna f captura en d1; la letra f distingue las dos torres.',
    'x = captura; + = jaque; # = mate; O-O-O = enroque largo; e8=Q sería una promoción a dama (ejemplo ajeno a esta partida).',
    'Corrección de Gemini: ! corresponde a $1; ? a $2; !! a $3; ?? a $4; !? a $5; ?! a $6. Por tanto $6 no significa ?? y ?! es la anotación convencional de jugada dudosa. $9 expresa la peor jugada en la tabla NAG. Estas anotaciones venían en el PGN: no son resultados de nuestro motor.'
]
LESSONS = [
    'No se puede medir tu fuerza ni predecir una subida de Elo con una sola partida. Ganaste y aprovechaste capturas, pero conviene revisar también las oportunidades perdidas. La perspectiva de este estudio es blancas, como en la respuesta de Gemini.',
    'Antes de mover, revisa jaques, capturas y amenazas de ambos bandos. En 12.Cxd5, comprueba …exd5; en 26.Cxg5, mira también …Axd1 antes de contar una dama ganada.',
    'Practica piezas sin defensa y clavadas relativas; después, desarrollo, seguridad del rey y mates básicos. Enrocar requiere comprobar la posición concreta: no es siempre la mejor decisión.',
    'Una rutina posible es dedicar unos minutos a ejercicios, jugar una partida con tiempo para pensar y revisar un momento con el motor. Los porcentajes y la promesa de llegar a 800–1000 de Gemini son sugerencias, no resultados demostrados.'
]

def load_game():
    game = core.load_game(GAME_PATH)
    game['study_prompt'] = game['pgn'] + '\n\ncrees que se jugar bien?'
    game['followups'] = ['que cosas me recomendarias aprender para mejorar', 'enseñame a entender la notación']
    return game

def analyze_game(path):
    game = load_game()
    saved = history_evidence.load('gemini', game['pgn'], core.DEPTH, core.SECONDS)
    if saved:
        return saved
    executable = Path(path).resolve()
    key = (str(executable), executable.stat().st_mtime_ns, hashlib.sha256(game['pgn'].encode()).hexdigest(), core.DEPTH, core.SECONDS)
    with core.ENGINE_LOCK:
        if key in _cache:
            return _cache[key]
        with chess.engine.SimpleEngine.popen_uci(path, timeout=15) as engine:
            engine.configure({'Threads': 1, 'Hash': 128})
            rows, opponent, board = [], [], chess.Board()
            for i, uci in enumerate(game['moves']):
                move = chess.Move.from_uci(uci)
                if board.turn or i+1 in (26, 50):
                    row = dict(ply=i+1, label=core.label(i+1, board.san(move)), **core.compare(engine, board, move))
                    (rows if board.turn else opponent).append(row)
                board.push(move)
            result = dict(engine=engine.id.get('name','Stockfish'), generated_at=datetime.now(timezone.utc).isoformat(),
                          pgn_sha256=key[2], perspective='white', rows=rows, opponent=opponent,
                          ranking=sorted(rows,key=lambda r:r['priority'],reverse=True),
                          settings=dict(depth_target=core.DEPTH,seconds_per_search=core.SECONDS,threads=1,hash_mb=128),
                          exchange=core.line(core.board_for(game['moves'][:48]), ['O-O','Qxg5','Nxg5','Bxd1','Rfxd1','Rg4+','Kf1','Rxg5'],48,'Secuencia real: se capturan ambas damas'),
                          final=dict(**core.position(board),best=core.search(engine,board),result='1-0',termination=None),
                          method='Comparación de candidatas desde la misma posición. Umbrales locales 50/100/200 cp; los NAG del PGN se conservan como anotaciones originales y no determinan estas etiquetas.')
        _cache.clear()
        _cache[key]=result
        return result

def query(path, question, ply):
    game=load_game()
    text=question
    start=re.search(r'\[(?:Event|Site|White)\s',text)
    if start:
        pasted=chess.pgn.read_game(io.StringIO(text[start.start():]))
        if pasted is None or pasted.errors or [m.uci() for m in pasted.mainline_moves()]!=game['moves']:
            raise ValueError('El PGN no coincide con j017371–zhorzho11.')
        # Prompt may be before or after the PGN.
        text=text[:start.start()]+' '+text[text.rfind('1-0')+3:]
    q=''.join(c for c in unicodedata.normalize('NFD',text.lower()) if not unicodedata.combining(c))
    report=analyze_game(path)
    rows={r['ply']:r for r in report['rows']+report['opponent']}
    target, supported, lines = ply, True, []
    if re.search(r'notacion|simbolo|leer|nag',q):
        target=53
        paragraphs=NOTATION
        lines=[dict(base=52,moves=game['moves'][52:53],name='27.Tfxd1: leer la captura en el tablero')]
    elif re.search(r'aprender|mejorar|rutina|recom|800|1000',q):
        target=23
        paragraphs=LESSONS
    elif re.search(r'25|26|dama|clavad|enroc',q):
        target=49
        paragraphs=['Gemini afirmó que 25…Dxg5 regaló la dama y liquidó la partida. La secuencia real fue 26.Cxg5 Axd1 27.Tfxd1: desaparecen ambas damas. Después …Tg4+ Rf1 Txg5 recupera el caballo. No es una dama gratis.',
                    'El caballo de f3 estaba en la diagonal del alfil g4 hacia la dama d1: una clavada relativa, no una prohibición legal de mover. La torre de f4 lo ataca, pero no lo clava al rey g1.',
                    core.row_text(rows[49]),core.row_text(rows[50]),core.row_text(rows[51])]
        reply=rows[49]['played']['san'][1:2]
        if reply:
            paragraphs.append('Contra 25.O-O, la respuesta calculada comienza con '+core.spanish(reply[0])+'. Compárala con …Dxg5, que fue la respuesta real. Que ambas damas desaparezcan no hace correcta la decisión negra: consulta su pérdida estimada.')
        lines=[report['exchange']]
    elif re.search(r'12|13|14|regal|caballo',q):
        target=23
        paragraphs=['12.Cxd5 exd5 entrega un caballo por un peón. 13…Cc5 permite 14.dxc5. Comprueba cuánto cambia la valoración: devolver material no implica automáticamente igualar la posición.',
                    core.row_text(rows[23]),core.row_text(rows[26]),core.row_text(rows[27])]
    elif re.search(r'final|mate|termin',q):
        target=67
        paragraphs=['La última jugada es 34.Txf7. El PGN indica 1–0, sin motivo de terminación. No es jaque mate; no se puede afirmar abandono o tiempo.', 'Evaluación final: '+core.score_text(report['final']['best'])+'.']
    elif re.search(r'bien|error|partida|resumen|nivel',q):
        target=report['ranking'][0]['ply']
        paragraphs=[LESSONS[0], 'Stockfish compara las 34 decisiones blancas. Mayores pérdidas estimadas: '+ '; '.join(core.row_text(r) for r in report['ranking'][:3]), 'También se verifican 13…Cc5 y 25…Dxg5, porque la conversación juzga esas decisiones negras. Las anotaciones $2, $4 y $9 no se adoptan como conclusiones del motor.']
    else:
        match=re.search(r'(?:jugada\s+)?\b(\d{1,2})\s*\.?\s*(?:[a-z]|$)',q)
        candidate=int(match[1])*2-1 if match else ply
        if candidate in rows and re.search(r'jugada|ocurr|alternativa|\d',q):
            target=candidate;paragraphs=[core.row_text(rows[target])]
        else:
            supported=False;paragraphs=['No he validado esa consulta. Este recorrido preparado admite tu nivel, recomendaciones, notación, 12.Cxd5, 13…Cc5, 25.O-O, 26.Cxg5 y el final.']
    if supported and target in rows:
        row=rows[target]
        lines.extend([dict(base=target-1,moves=row['best']['pv'],name='Alternativa calculada por Stockfish'),dict(base=target-1,moves=row['played']['pv'],name='Tu jugada y respuesta del rival')])
    return dict(question=question,target_ply=target,supported=supported,paragraphs=paragraphs,lines=lines,engine=report['engine'],generated_at=report['generated_at'],source='Síntesis de Gemini contrastada con Stockfish. Tutor de plantillas; no se utiliza Gemini ni Ollama en vivo.')
