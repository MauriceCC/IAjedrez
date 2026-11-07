"""Validate supplied PGN, engine evidence and Gemini-specific corrections."""
import chess
import pytest
from fastapi.testclient import TestClient
import gemini
import review
from app import app, engine_path

client=TestClient(app)

def test_game_and_annotations():
    game=client.get('/api/review/game?game=gemini').json()
    assert len(game['moves'])==67
    assert game['headers']['White']=='j017371'
    assert game['headers']['Result']=='1-0'
    assert '$9' in game['pgn'] and '$4' in game['pgn']
    assert len(game['followups'])==2
    assert not game['positions'][-1]['checkmate']
    board=review.board_for(game['moves'][:54])
    assert not board.pieces(chess.QUEEN,chess.WHITE)
    assert not board.pieces(chess.QUEEN,chess.BLACK)

@pytest.fixture(scope='module')
def evidence():
    path=engine_path()
    if not path: pytest.skip('Stockfish unavailable')
    return path,gemini.analyze_game(path)

def test_real_engine_evidence(evidence):
    _,report=evidence
    game=gemini.load_game()
    assert len(report['rows'])==34
    assert {r['ply'] for r in report['opponent']}=={26,50}
    assert 'Stockfish' in report['engine']
    for row in report['rows']+report['opponent']:
        assert row['played']['pv'][0]==game['moves'][row['ply']-1]
        for kind in ['best','played']:
            assert row[kind]['depth']>0
            review.board_for(game['moves'][:row['ply']-1]+row[kind]['pv'])

def test_conversation_queries(evidence):
    path,_=evidence
    for q,target in [('enseñame a entender la notación',53),('que cosas me recomendarias aprender para mejorar',23),('¿25…Dxg5 regaló la dama?',49),('¿Cómo terminó?',67)]:
        answer=gemini.query(path,q,0)
        assert answer['supported'] and answer['target_ply']==target
        for line in answer['lines']:
            review.board_for(gemini.load_game()['moves'][:line['base']]+line['moves'])
    assert gemini.query(path,gemini.load_game()['study_prompt'],0)['supported']
    assert not gemini.query(path,'Quiero comprar un telescopio',0)['supported']
    with pytest.raises(ValueError,match='no coincide'):
        gemini.query(path,review.load_game()['pgn'],0)

def test_missing_engine(monkeypatch):
    monkeypatch.setattr('app.engine_path',lambda:None)
    assert client.post('/api/review/analyze?game=gemini',json={}).status_code==503
