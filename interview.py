"""The supplied conversation, with separately calculated engine evidence."""
import hashlib
import io
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

import chess
import chess.engine
import chess.pgn
import review as core
import history_evidence

GAME_PATH = Path(__file__).parent / 'static/partida-entrevista.pgn'
_cache = {}

# These are attributed summaries, not engine conclusions or a literal transcript.
TOPICS = {
    31: dict(title='16.e4 · abrir el centro', original='ChatGPT llamó buena a la ruptura central.',
             user='Pero activo el alfil negro de b7.',
             explanation='Tu duda sobre b7 es pertinente: la secuencia jugada despeja d5 y acaba dejando d4 aislado. Pero la respuesta anterior omitió comprobar recursos tácticos antes de …dxe4. No se debe justificar e4 únicamente por los intercambios que ocurrieron: revisa la respuesta calculada del rival.'),
    41: dict(title='21.Te2 · activar la torre', original='ChatGPT cuestionó las maniobras y el tiempo consumido.',
             user='Lo hice para mejorar la posición y tener una torre activa.',
             explanation='Tu intención es coherente: Te4–e2–c2–c6 ocupa la columna abierta y ataca la dama en d6. El PGN registra 18 segundos para Te2 y 33 segundos entre las jugadas 20 y 23 de blancas. El coste de reloj y la calidad de la jugada son cuestiones distintas.'),
    57: dict(title='29.Rf1 · la entrada de la dama', original='ChatGPT lo describió como centralización y después aseguró que perdía h3.',
             user='La dama puede ir a h1 con jaque y luego ganar un peón.',
             explanation='La diagonal b7–h1 está abierta y …Dh1+ es legal. La línea …Dh1+ Re2 Dxh3 también es legal, pero Re2 no es forzada. Se calcula por separado la mejor defensa tras …Dh1+ y la respuesta real …Cd5; una línea ilustrativa no prueba una pérdida inevitable.'),
    89: dict(title='45.Cc7 · seguridad del caballo', original='ChatGPT señaló la pérdida del caballo como el error táctico decisivo.',
             user='¿Qué alternativa conservaba mi caballo?',
             explanation='El rey de f5 ataca el caballo en e6. Cc7 permite …Cxc7 desde d5, tal como ocurrió. Cc5 y Cg7+ son alternativas legales; el motor las compara sin asumir que ambas sean igual de buenas. Quedaban 7 segundos antes de mover y 6 después.'),
}


def load_game():
    return core.load_game(GAME_PATH)


def analyze_game(path):
    game = load_game()
    saved = history_evidence.load('entrevista', game['pgn'], core.DEPTH, core.SECONDS)
    if saved:
        return saved
    executable = Path(path).resolve()
    key = (str(executable), executable.stat().st_mtime_ns,
           hashlib.sha256(game['pgn'].encode()).hexdigest(), core.DEPTH, core.SECONDS)
    with core.ENGINE_LOCK:
        if key in _cache:
            return _cache[key]
        with chess.engine.SimpleEngine.popen_uci(path, timeout=15) as engine:
            engine.configure({'Threads': 1, 'Hash': 128})
            rows, board = [], chess.Board()
            for i, uci in enumerate(game['moves']):
                move = chess.Move.from_uci(uci)
                if board.turn == chess.WHITE:
                    rows.append(dict(ply=i+1, label=core.label(i+1, board.san(move)),
                                     **core.compare(engine, board, move)))
                board.push(move)
            # Check the user's tactical claim against best defense, not just legality.
            after_king = core.board_for(game['moves'][:57])
            queen_check = core.compare(engine, after_king, after_king.parse_san('Qh1+'))
            actual_reply = core.compare(engine, after_king, after_king.parse_san('Nd5'))
            illustration = core.line(after_king.copy(), ['Qh1+', 'Ke2', 'Qxh3'], 57,
                                     'Línea citada, no forzada: …Dh1+ Re2 Dxh3')
            knight_board = core.board_for(game['moves'][:88])
            alternatives = [core.compare(engine, knight_board, knight_board.parse_san(s))
                            for s in ['Nc5', 'Ng7+']]
            result = dict(engine=engine.id.get('name', 'Stockfish'),
                          generated_at=datetime.now(timezone.utc).isoformat(),
                          pgn_sha256=key[2], perspective='white',
                          settings=dict(depth_target=core.DEPTH, seconds_per_search=core.SECONDS, threads=1, hash_mb=128),
                          rows=rows, ranking=sorted(rows, key=lambda r:r['priority'], reverse=True),
                          topics=TOPICS, queen_check=queen_check, actual_reply=actual_reply,
                          illustration=illustration, alternatives=alternatives,
                          final=dict(**core.position(board), best=core.search(engine, board), result='0-1', termination='Time forfeit'),
                          method='Mejor candidata y jugada real desde la misma posición; búsqueda limitada. Etiquetas locales: 50/100/200 centipeones. No son clasificaciones de Lichess.')
        _cache.clear()
        _cache[key] = result
        return result


def query(path, question, ply):
    game = load_game()
    start = re.search(r'\[(?:Event|Site|White)\s|(?:^|\n)1\.\s', question)
    if start:
        pasted = chess.pgn.read_game(io.StringIO(question[start.start():].strip()))
        if pasted is None or pasted.errors or [m.uci() for m in pasted.mainline_moves()] != game['moves']:
            raise ValueError('El PGN de la consulta no coincide con Timmy-t–Kuanynsh.')
        question_text = question[:start.start()]
    else:
        question_text = question
    q = ''.join(c for c in unicodedata.normalize('NFD', question_text.lower()) if not unicodedata.combining(c))
    report = analyze_game(path)
    rows = {r['ply']: r for r in report['rows']}
    paragraphs, lines, targets = [], [], []
    for number, pattern in [(16, r'\b16\b|alfil.*b7|romp.*centro'), (21, r'\b21\b|torre.*activ|activar.*torre'),
                            (29, r'\b29\b|h1|rey.*f1'), (45, r'\b45\b|caballo.*pier|nc7|cc7')]:
        if re.search(pattern, q):
            targets.append(number * 2 - 1)
    if not targets:
        for row in rows.values():
            number = (row['ply'] + 1)//2
            if re.search(r'(?<!\d)' + str(number) + r'\s*\.?\s*(?:' + re.escape(row['san'].lower()) + '|' + re.escape(core.spanish(row['san']).lower()) + r')(?!\w)', q):
                targets.append(row['ply'])
                break
    if targets:
        for target in targets:
            row = rows[target]
            topic = TOPICS.get(target)
            if topic:
                paragraphs.extend([topic['title'], 'Respuesta anterior: ' + topic['original'],
                                   'Tu observación: ' + topic['user'], 'Revisión didáctica: ' + topic['explanation']])
            paragraphs.append('Evidencia Stockfish: ' + core.row_text(row) +
                              f' Profundidades alcanzadas: {row["best"]["depth"]}/{row["played"]["depth"]}.')
            lines.extend([dict(base=target-1, moves=row['best']['pv'], name=f'{row["label"]}: candidata del motor'),
                          dict(base=target-1, moves=row['played']['pv'], name=f'{row["label"]}: respuesta a tu jugada')])
            if target == 31 and row['played']['pv'][1:2] == ['c8c3']:
                paragraphs.append('Corrección de la conversación: Stockfish encuentra 16…Txc3! antes de capturar en e4. Tras 17.Dxc3 dxe4, el peón ataca simultáneamente al alfil de d3 y al caballo de f3. La partida siguió con 16…dxe4, una respuesta distinta. La explicación anterior de «ruptura defendible sin error táctico» no queda respaldada por esta búsqueda.')
            if target == 41 and row['best']['pv'][:1] == [row['move']]:
                paragraphs.append('En esta búsqueda, 21.Te2 coincide con la primera candidata de Stockfish. Esto respalda la jugada de activación, aunque no certifica todas las continuaciones posteriores del plan.')
            if target == 57:
                check, actual = report['queen_check'], report['actual_reply']
                paragraphs.append(f'Tras 29.Rf1: …Dh1+ obtiene {core.score_text(check["played"])} con la resistencia hallada; …Cd5 obtiene {core.score_text(actual["played"])}. Perspectiva blanca. Profundidades: {check["played"]["depth"]}/{actual["played"]["depth"]}.')
                lines.extend([report['illustration'], dict(base=57, moves=check['played']['pv'], name='…Dh1+: defensa calculada por Stockfish')])
            if target == 89:
                for alternative in report['alternatives']:
                    paragraphs.append(f'{core.spanish(alternative["san"])}: {core.score_text(alternative["played"])}; profundidad {alternative["played"]["depth"]}.')
                    lines.append(dict(base=88, moves=alternative['played']['pv'], name='Probar '+core.spanish(alternative['san'])))
        target, supported = targets[0], True
    elif re.search(r'final|termin|tiempo|mate', q):
        target, supported = 108, True
        paragraphs = ['El PGN registra victoria negra por tiempo, no jaque mate. Los relojes son registros posteriores a cada jugada; el último segundo mostrado no contradice la caída de bandera posterior.',
                      'Evaluación del tablero final por Stockfish: '+core.score_text(report['final']['best'])+'.']
        lines = [dict(base=108, moves=report['final']['best']['pv'], name='Continuación del motor desde el final')]
    elif re.search(r'error|partida|resumen|paso a paso|apertura', q):
        target, supported = report['ranking'][0]['ply'], True
        paragraphs = ['He comparado las 54 decisiones de blancas con Stockfish. Las mayores caídas estimadas son: ' + '; '.join(core.row_text(r) for r in report['ranking'][:3]),
                      'Recorrido cronológico: apertura (1–15), ruptura 16.e4, actividad de torre 21.Te2, seguridad del rey 29.Rf1, simplificación (31–39), final 45.Cc7 y derrota por tiempo. Abre cada momento para contrastar la conversación, recorrer variantes y practicar.',
                      'El reloj no forma parte de la evaluación de Stockfish: 21.Te2 consumió 18 s, 26.De3 16 s y 29.Rf1 13 s. Son 47 s de los 180 iniciales; esto no clasifica por sí solo las jugadas como errores.']
        for title, first, last in [('Apertura y desarrollo', 1, 15), ('Ruptura central', 16, 20),
                                   ('Actividad y seguridad del rey', 21, 30), ('Simplificación', 31, 39),
                                   ('Final de caballos', 40, 45), ('Conversión y tiempo', 46, 54)]:
            stage = [r for r in report['rows'] if first <= (r['ply']+1)//2 <= last]
            critical = max(stage, key=lambda r: r['priority'])
            paragraphs.append(f'{first}–{last} · {title}. Mayor caída estimada en esta etapa: ' + core.row_text(critical))
            lines.append(dict(base=critical['ply']-1, moves=critical['played']['pv'], name=f'{title}: {critical["label"]}'))
    else:
        target, supported = ply, False
        paragraphs = ['No he validado esa afirmación: este tutor usa respuestas preparadas, no un LLM. Pregunta por 16.e4, 21.Te2, 29.Rf1, 45.Cc7, otra jugada concreta o el final.']
    return dict(question=question, target_ply=target, supported=supported, paragraphs=paragraphs, lines=lines,
                engine=report['engine'], generated_at=report['generated_at'],
                source='Síntesis atribuida de la conversación + revisión didáctica + evidencia calculada por Stockfish. Las variantes no son forzadas salvo comprobación explícita.')
