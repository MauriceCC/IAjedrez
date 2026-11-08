from fastapi.testclient import TestClient
import pytest
import app
import review

client = TestClient(app.app)


def test_invalid_color_and_missing_black_moves():
    assert client.post('/api/review/import', json={'pgn':'1. e4 *','player_color':'green'}).status_code == 422
    assert client.post('/api/review/import', json={'pgn':'1. e4 *','player_color':'black'}).status_code == 422


def test_selected_side_analysis(monkeypatch):
    if not app.engine_path():
        pytest.skip('Stockfish no instalado')
    monkeypatch.setattr(review, 'SECONDS', .05)
    for color, plies in [('white',[1,3]), ('black',[2,4])]:
        token = client.post('/api/review/import',json={'pgn':'1. e4 e5 2. Nf3 Nc6 *','player_color':color}).json()['id']
        game = client.get('/api/review/game',params={'game':token}).json()
        assert game['player_color']==color
        report = client.post('/api/review/analyze',params={'game':token}).json()
        assert [r['ply'] for r in report['rows']]==plies
        assert report['perspective']=='white'
        for row in report['rows']:
            if row['loss_cp'] is not None:
                sign = 1 if color=='white' else -1
                assert row['loss_cp']==max(0,sign*(row['best']['cp_white']-row['played']['cp_white']))
