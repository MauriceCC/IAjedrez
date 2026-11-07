from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_moves():
    result = client.post('/api/position', json={'moves': ['e2e4', 'e7e5']})
    assert result.status_code == 200
    assert result.json()['sans'] == ['e4', 'e5']
    assert client.post('/api/position', json={'moves': ['e2e5']}).status_code == 422

def test_castling():
    result = client.post('/api/position', json={'moves': ['e2e4','e7e5','g1f3','b8c6','f1c4','g8f6','e1g1']}).json()
    assert result['pieces']['g1'] == 'K'
    assert result['pieces']['f1'] == 'R'

def test_import():
    assert client.post('/api/import', json={'pgn': '1. e4 e5 2. Nf3 Nc6'}).json()['moves'] == ['e2e4','e7e5','g1f3','b8c6']
    assert client.post('/api/import', json={'pgn': '1. e5'}).status_code == 422

def test_missing_engine(monkeypatch):
    monkeypatch.setattr('app.engine_path', lambda: None)
    assert client.post('/api/analyze', json={'moves': []}).status_code == 503

def test_mate():
    result = client.post('/api/position', json={'moves': ['f2f3','e7e5','g2g4','d8h4']}).json()
    assert result['result'] == '0-1'
    assert result['legal'] == []

def test_interview_game_and_clocks():
    game = client.get('/api/demo').json()
    assert len(game['moves']) == 108
    assert game['headers']['Termination'] == 'Time forfeit'
    assert game['clocks'][41]['white'] == 105
    assert game['clocks'][89]['white'] == 6
    final = client.post('/api/position', json={'moves': game['moves']}).json()
    assert final['result'] is None  # time forfeit is PGN metadata, not checkmate

def test_demo_variations():
    moves = client.get('/api/demo').json()['moves']
    for ply, line in [(57, ['b7h1','f1e2','h1h3']), (88,['e6c7','d5c7']), (88,['e6c5']), (88,['e6g7'])]:
        result = client.post('/api/position', json={'moves': moves[:ply]+line})
        assert result.status_code == 200
    result = client.post('/api/position', json={'moves': moves[:88]+['e6c7','d5c7']}).json()
    assert result['pieces']['c7'] == 'n'
    assert 'N' not in result['pieces'].values()
