"""Engine evidence and a bounded, explicit tutor for the supplied study game.

Natural-language answers are templates built from computed evidence, not an LLM.
All evaluations use White's perspective; root-restricted searches compare moves
at the same position. Labels are local teaching thresholds, not Chess.com labels.
"""
import hashlib
import io
import threading
import unicodedata
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import re
import history_evidence

import chess
import chess.engine
import chess.pgn

GAME_PATH = Path(__file__).parent / 'static/partida-mauricio.pgn'
ENGINE_LOCK = threading.Lock()
DEPTH = 19
SECONDS = 1.5
_cache = {}


def load_game(game_path=GAME_PATH):
    pgn = game_path.read_text(encoding='utf-8')
    game = chess.pgn.read_game(io.StringIO(pgn))
    if game is None or game.errors:
        raise ValueError('La partida precargada no es válida.')
    board = game.board()
    moves, sans, positions, clocks = [], [], [position(board)], []
    for node in game.mainline():
        move = node.move
        clocks.append(node.clock())
        sans.append(board.san(move))
        moves.append(move.uci())
        board.push(move)
        positions.append(position(board))
    return dict(pgn=pgn, headers=dict(game.headers), moves=moves, sans=sans, positions=positions, clocks=clocks)


def position(board):
    return dict(fen=board.fen(), pieces={chess.square_name(s): p.symbol() for s,p in board.piece_map().items()},
                legal=[m.uci() for m in board.legal_moves], turn='blancas' if board.turn else 'negras',
                check=board.is_check(), checkmate=board.is_checkmate())


def board_for(moves):
    board = chess.Board()
    for move in moves:
        board.push_uci(move)
    return board


def spanish(san):
    return re.sub('[KQRBN]', lambda m: dict(K='R', Q='D', R='T', B='A', N='C')[m[0]], san)


def label(ply, san):
    return f'{(ply + 1)//2}{"." if ply % 2 else "…"} {spanish(san)}'


def pack(board, info):
    score = info['score'].white()
    replay = board.copy()
    moves, sans = [], []
    for move in info.get('pv', [])[:10]:
        sans.append(replay.san(move))
        moves.append(move.uci())
        replay.push(move)
    return dict(cp_white=score.score(), mate_white=score.mate(), depth=info.get('depth', 0),
                nodes=info.get('nodes', 0), pv=moves, san=sans)


def search(engine, board, root=None):
    options = {'root_moves': [root]} if root is not None else {}
    info = engine.analyse(board, chess.engine.Limit(depth=DEPTH, time=SECONDS), **options)
    return pack(board, info)


def compare_scores(best, played, white):
    # Never pretend that a forced mate is a numeric centipawn loss.
    if best['mate_white'] is not None or played['mate_white'] is not None:
        sign = 1 if white else -1
        best_mate, played_mate = best['mate_white'], played['mate_white']
        new_loss = played_mate is not None and played_mate * sign <= 0 and not (
            best_mate is not None and best_mate * sign <= 0)
        missed_win = best_mate is not None and best_mate * sign > 0 and not (
            played_mate is not None and played_mate * sign > 0)
        return dict(loss_cp=None, kind='Permite mate' if new_loss else 'Pierde mate forzado' if missed_win else 'Línea de mate',
                    grade='danger' if new_loss or missed_win else 'neutral', priority=10000 if new_loss or missed_win else 0)
    loss = max(0, (best['cp_white'] - played['cp_white']) * (1 if white else -1))
    kind, grade = ('Error grave', 'danger') if loss >= 200 else ('Error', 'danger') if loss >= 100 else ('Imprecisión', 'warning') if loss >= 50 else ('Sin caída importante', 'neutral')
    return dict(loss_cp=loss, kind=kind, grade=grade, priority=loss)


def compare(engine, board, move):
    if move not in board.legal_moves:
        raise ValueError('La jugada propuesta no es legal en esta posición.')
    best = search(engine, board)
    played = best if best['pv'] and best['pv'][0] == move.uci() else search(engine, board, move)
    return dict(best=best, played=played, move=move.uci(), san=board.san(move),
                **compare_scores(best, played, board.turn))


def score_text(score):
    if score['mate_white'] is not None:
        mate = score['mate_white']
        return f'mate a favor de {"blancas" if mate > 0 else "negras"} en {abs(mate)}'
    return f'{score["cp_white"]/100:+.2f}'


def row_text(row):
    best = spanish(row['best']['san'][0]) if row['best']['san'] else 'sin continuación'
    change = f'La pérdida estimada es {row["loss_cp"]/100:.2f} peones.' if row['loss_cp'] is not None else row['kind'] + '.'
    return (f'{row["label"]}: {score_text(row["best"])} con {best}, frente a '
            f'{score_text(row["played"])} al forzar la jugada de la partida. {change} '
            'Las puntuaciones se leen desde blancas y son aproximaciones de esta búsqueda.')


def line(board, sans, base, name):
    moves = []
    for san in sans:
        move = board.parse_san(san)
        moves.append(move.uci())
        board.push(move)
    return dict(base=base, moves=moves, san=sans, name=name)


def analyze_game(path):
    game = load_game()
    saved = history_evidence.load('mauricio', game['pgn'], DEPTH, SECONDS)
    if saved:
        return saved
    engine_file = Path(path).resolve()
    key = (str(engine_file), engine_file.stat().st_mtime_ns,
           hashlib.sha256(game['pgn'].encode()).hexdigest(), DEPTH, SECONDS)
    with ENGINE_LOCK:
        if key in _cache:
            return _cache[key]
        with chess.engine.SimpleEngine.popen_uci(path, timeout=15) as engine:
            engine.configure({'Threads': 1, 'Hash': 128})
            rows = []
            board = chess.Board()
            for i, uci in enumerate(game['moves']):
                move = chess.Move.from_uci(uci)
                if board.turn == chess.WHITE:
                    item = compare(engine, board, move)
                    rows.append(dict(ply=i+1, label=label(i+1, board.san(move)), **item))
                board.push(move)
            final_best = search(engine, board)
            final_line = line(board.copy(), ['Qxd2','Qxf3','gxf3','exd2','Kxd2'], 38,
                              'Variante citada: 20. Dxd2 Dxf3 21. gxf3 exd2 22. Rxd2')
            final_line['evaluation'] = search(engine, board_for(game['moves'] + final_line['moves']))
            # Evaluate the first defensive move separately. A legal continuation is not forced.
            defense = compare(engine, board, board.parse_san('Qxd2'))
            qf3_board = board_for(game['moves'][:16])
            qf3 = compare(engine, qf3_board, qf3_board.parse_san('Qf3'))
            qf3_line = line(qf3_board.copy(), ['Qf3','Qxg3+','Qxg3'], 16,
                            'Hipótesis citada: 9. Df3 Dxg3+ 10. Dxg3')
            material_board = board_for(game['moves'] + final_line['moves'])
            material = {color: dict(Counter(p.symbol().upper() for p in material_board.piece_map().values() if p.color == side))
                        for color, side in [('white', chess.WHITE), ('black', chess.BLACK)]}
            result = dict(engine=engine.id.get('name', 'Stockfish'), generated_at=datetime.now(timezone.utc).isoformat(),
                          settings=dict(depth_target=DEPTH, seconds_per_search=SECONDS, threads=1, hash_mb=128),
                          perspective='white', rows=rows, ranking=sorted(rows, key=lambda r:r['priority'], reverse=True),
                          final=dict(**position(board), best=final_best, defense=defense, line=final_line, material=material,
                                     result=game['headers']['Result'], termination=game['headers'].get('Termination')),
                          qf3=dict(comparison=qf3, line=qf3_line),
                          method='Mejor candidata y jugada real comparadas desde la misma posición. Búsqueda limitada; etiquetas orientativas: 50/100/200 centipeones. No son clasificaciones de Chess.com.')
        _cache.clear()
        _cache[key] = result
        return result


def practice(path, moves, candidate):
    board = board_for(moves)
    move = chess.Move.from_uci(candidate)
    with ENGINE_LOCK, chess.engine.SimpleEngine.popen_uci(path, timeout=15) as engine:
        engine.configure({'Threads': 1, 'Hash': 128})
        result = compare(engine, board, move)
        result['engine'] = engine.id.get('name', 'Stockfish')
    board.push(move)
    return dict(**result, position=position(board))


def query(path, question, ply):
    game = load_game()
    q = ''.join(c for c in unicodedata.normalize('NFD', question.lower()) if not unicodedata.combining(c))
    # If a pasted PGN is present, don't silently analyze a different game.
    if '[site ' in q or re.search(r'\b1\.\s*e4\s+e5', q):
        start = question.find('[') if '[' in question else re.search(r'\b1\.', question).start()
        pasted = chess.pgn.read_game(io.StringIO(question[start:]))
        if pasted is None or pasted.errors or [m.uci() for m in pasted.mainline_moves()] != game['moves']:
            raise ValueError('El PGN de la consulta no coincide con la partida cargada. Este recorrido analiza Mauricio0120–santoshglklklk.')
        q = q[:start]
    report = analyze_game(path)
    rows = {r['ply']:r for r in report['rows']}
    target, lines, paragraphs = ply, [], []
    supported = True
    # These routes are a bounded interpretation of the supplied conversation.
    if re.search(r'qf3|df3|defend.*g3|alternativa.*9', q):
        target = 17
        evidence = report['qf3']['comparison']
        paragraphs = ['9. Df3 es legal. La secuencia Df3 Dxg3+ Dxg3 también es legal, pero las negras no están obligadas a capturar en g3.',
                      f'Stockfish valora Df3 en {score_text(evidence["played"])}; su candidata principal es {spanish(evidence["best"]["san"][0])} ({score_text(evidence["best"])}).',
                      f'La respuesta calculada a Df3 comienza con {spanish(evidence["played"]["san"][1]) if len(evidence["played"]["san"]) > 1 else "la variante mostrada"}, no con la captura hipotética en g3. Por eso una defensa posible no equivale a la recomendación principal del motor.']
        lines = [report['qf3']['line'], dict(base=16, moves=evidence['played']['pv'], name='Respuesta calculada a 9. Df3')]
    elif re.search(r'final|mate|rd2|td2|qxd2|dxd2|abandon|continuar|termin', q):
        target = 38
        final = report['final']
        paragraphs = ['19…Td2+ no es jaque mate: existen cuatro respuestas legales. El PGN solo indica 0–1; no permite atribuir la derrota a abandono o tiempo.',
                      f'La variante citada 20. Dxd2 Dxf3 21. gxf3 exd2 22. Rxd2 es legal. Al final quedan torre y alfil contra torre y caballo, con {final["material"]["white"].get("P", 0)} peones blancos y {final["material"]["black"].get("P", 0)} negros.',
                      f'La posición final de la partida se evalúa en {score_text(final["best"])}; la posición después de la variante citada, en {score_text(final["line"]["evaluation"])}. La segunda cifra corresponde a esa variante, que no es forzada.',
                      f'Para 20. Dxd2, la evaluación con la mejor resistencia hallada es {score_text(final["defense"]["played"])}. No basta con mostrar una línea legal para concluir que el rival la elegirá.']
        lines = [final['line'], dict(base=38, moves=final['best']['pv'], name='Continuación principal de Stockfish')]
    else:
        matches = [(r['ply'], r) for r in report['rows'] if re.search(r'(?<!\d)'+str((r['ply']+1)//2)+r'\s*\.?\s*(?:'+re.escape(r['san'].lower())+'|'+re.escape(spanish(r['san']).lower())+r')(?![a-z0-9])', q)]
        if matches:
            target, row = matches[0]
        elif re.search(r'mi error|mis errores|esta partida|resumen|principal|primer error|mayor error|peor jugada', q):
            row = report['ranking'][0]
            target = row['ply']
            paragraphs.append('He comparado las 19 jugadas de blancas con Stockfish. Las mayores caídas estimadas de esta revisión son: ' + '; '.join(row_text(r) for r in report['ranking'][:3]))
            paragraphs.append('La conversación previa destacaba 9. Cd2 como primer error importante. La revisión también detecta una caída anterior en 7. Ag3; no conviene copiar esa conclusión sin matizarla.')
        elif re.search(r'jugada|posicion|error|mejor|alternativa|amenaza|por que|consejo', q) and ply in rows:
            row = rows[ply]
            paragraphs.append('Esta respuesta se limita a la comparación calculada de la jugada seleccionada; no valida todas las afirmaciones posibles de la pregunta.')
        else:
            supported = False
            row = None
            paragraphs = ['No puedo interpretar esa consulta con el tutor de este recorrido. Puedes preguntar «¿Cuál fue mi error en esta partida?», «¿Fue 9. Nd2 el primer error?», «¿Era mejor 9. Qf3?» o «¿Era mate después de 19…Rd2+?». No he validado la afirmación de tu pregunta.']
        if row:
            paragraphs.append(row_text(row))
            if target == 17:
                paragraphs.append('9…Dxg3+ es legal y ocurrió. 10. Re2 era la única respuesta legal al jaque; eso explica la pérdida del derecho a enrocar. Sin embargo, 7. Ag3 también merece revisión antes de llamar a 9. Cd2 el primer error.')
            if target == 37:
                paragraphs.append(f'19. Tf3 sí ataca la dama de f4. La respuesta calculada comienza con {spanish(row["played"]["san"][1]) if len(row["played"]["san"]) > 1 else "la variante mostrada"}; en la partida las negras eligieron Td2+. Que ese jaque no sea mate no demuestra que Tf3 conservara la evaluación anterior.')
            lines = [dict(base=target-1, moves=row['best']['pv'], name='Alternativa principal de Stockfish'),
                     dict(base=target-1, moves=row['played']['pv'], name='Respuesta a la jugada de la partida')]
    return dict(question=question, target_ply=target, supported=supported, paragraphs=paragraphs,
                lines=lines, engine=report['engine'], generated_at=report['generated_at'],
                source='Tutor de alcance limitado: texto de plantilla con evidencia calculada por Stockfish.')
