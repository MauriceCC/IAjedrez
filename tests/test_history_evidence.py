"""History survives server restarts without launching Stockfish."""
import pytest
from fastapi.testclient import TestClient
import chess.engine
import history_evidence
import review
import interview
import gemini
from app import app

@pytest.mark.parametrize('name,module,count',[('mauricio',review,19),('entrevista',interview,54),('gemini',gemini,34)])
def test_history_never_launches_engine(monkeypatch,name,module,count):
    def forbidden(*args,**kwargs):
        raise AssertionError('History must not launch Stockfish')
    monkeypatch.setattr(chess.engine.SimpleEngine,'popen_uci',forbidden)
    report=module.analyze_game(None)
    assert report['preloaded'] and len(report['rows'])==count
    response=TestClient(app).get('/api/review/game?game='+name)
    assert response.status_code==200
    assert response.json()['report']['generated_at']==report['generated_at']
    assert module.query(None,'Resumen de errores de esta partida',0)['supported']

def test_stale_or_missing_evidence_is_not_reused():
    pgn=review.load_game()['pgn']
    assert history_evidence.load('mauricio',pgn+'\n',review.DEPTH,review.SECONDS) is None
    assert history_evidence.load('mauricio',pgn,review.DEPTH+1,review.SECONDS) is None
    assert history_evidence.load('missing',pgn,review.DEPTH,review.SECONDS) is None
