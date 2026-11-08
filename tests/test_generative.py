import httpx
from pathlib import Path
from fastapi.testclient import TestClient
import app as server

client = TestClient(server.app)


def test_user_supplied_pgn_from_home():
    pgn = (Path(__file__).parent / 'fixtures/aldinobabinote.pgn').read_text()
    response = client.post('/api/review/import', json={'pgn': pgn})
    assert response.status_code == 200
    game = client.get('/api/review/game', params={'game': response.json()['id']}).json()
    assert len(game['moves']) == 55
    assert len(game['positions']) == 56
    assert game['headers']['White'] == 'aldinobabinote'
    assert game['headers']['Result'] == '1-0'
    assert 'tiempo' in game['headers']['Termination']
    assert game['sans'][-1] == 'Rxc7+'
    assert not game['positions'][-1]['checkmate']


def test_import_isolation_and_validation():
    first = client.post('/api/review/import', json={'pgn': '1. e4 e5 2. Nf3 *'}).json()['id']
    second = client.post('/api/review/import', json={'pgn': '1. d4 d5 *'}).json()['id']
    assert first != second
    assert len(client.get('/api/review/game', params={'game': first}).json()['moves']) == 3
    assert client.get('/api/review/game', params={'game': second}).json()['moves'][0] == 'd2d4'
    assert client.post('/api/review/import', json={'pgn': '1. e5'}).status_code == 422


def test_ollama_request_and_failure(monkeypatch):
    monkeypatch.setenv('OLLAMA_MODEL', 'test-model')
    monkeypatch.setenv('OLLAMA_BASE_URL', 'http://model.example/')
    monkeypatch.setattr(server, 'evaluate', lambda moves: {'engine': 'Stockfish', 'fen': 'evidence'})
    def post(url, **kwargs):
        assert url == 'http://model.example/api/chat'
        assert kwargs['json']['model'] == 'test-model'
        assert 'evidence' in kwargs['json']['messages'][0]['content']
        return httpx.Response(200, json={'message': {'content': 'Explicación del modelo'}}, request=httpx.Request('POST', url))
    monkeypatch.setattr(server.httpx, 'post', post)
    result = client.post('/api/chat', json={'question': '¿Qué hago?', 'moves': []})
    assert result.json()['answer'] == 'Explicación del modelo'
    def fail(*args, **kwargs):
        raise httpx.ConnectError('offline')
    monkeypatch.setattr(server.httpx, 'post', fail)
    assert client.post('/api/chat', json={'question': '¿Qué hago?'}).status_code == 503
    monkeypatch.delenv('OLLAMA_MODEL')
    assert client.post('/api/chat', json={'question': '¿Qué hago?'}).status_code == 503


def test_study_query_uses_model_and_preserves_engine_lines(monkeypatch):
    token = client.post('/api/review/import', json={'pgn': '1. e4 e5 *'}).json()['id']
    row = dict(ply=1, san='e4', label='1. e4', kind='Error', loss_cp=100,
               best={'pv': ['d2d4'], 'san': ['d4'], 'cp_white': 100, 'mate_white': None},
               played={'pv': ['e2e4'], 'san': ['e4'], 'cp_white': 0, 'mate_white': None})
    monkeypatch.setattr(server.studies.STUDIES[token], 'analyze_game', lambda path: dict(
        rows=[row], ranking=[row], engine='Stockfish', method='test', generated_at='now'))
    monkeypatch.setattr(server, 'engine_path', lambda: 'engine')
    def answer(question, evidence, step):
        assert evidence['selected_comparison']['jugada_real'] == '1. e4'
        assert evidence['selected_comparison']['alternativa_recomendada'] == 'd4'
        assert evidence['selected_comparison']['perdida_en_peones'] == 1
        assert step == 2
        return 'Respuesta generativa\n\nSegundo párrafo', 'test-model'
    monkeypatch.setattr(server, 'ollama_answer', answer)
    result = client.post('/api/review/query', params={'game': token}, json={'question': 'Explica 1.e4', 'step': 2}).json()
    assert result['model'] == 'test-model'
    assert result['target_ply'] == 1
    assert result['lines'][0]['moves'] == ['d2d4']
    assert len(result['paragraphs']) == 2


def test_question_with_another_pgn_is_rejected():
    token = client.post('/api/review/import', json={'pgn': '1. e4 e5 *'}).json()['id']
    response = client.post('/api/review/query', params={'game': token}, json={
        'question': 'Revisa [White "Otro"]\n\n1. d4 d5 *'})
    assert response.status_code == 422
    assert 'no coincide' in response.json()['detail']
