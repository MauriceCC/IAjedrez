from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


def test_roni_is_a_permanent_history_study():
    assert 'data-game="roni"' in client.get('/').text
    game = client.get('/api/review/game?game=roni').json()
    assert game['headers']['White'] == 'Roni'
    assert game['headers']['Black'] == 'Computer'
    assert game['headers']['Result'] == '0-1'
    assert len(game['moves']) == 76
    assert game['positions'][-1]['checkmate']
    assert game['sans'][-1] == 'g6#'


def test_saved_examples_have_legal_variants_and_practice():
    import review
    game = client.get('/api/review/game?game=roni').json()
    example = game['example']
    assert len(example['threads']) == 3
    for thread in example['threads']:
        answer = thread['answer']
        assert answer['model'] == 'llama3.1:8b'
        assert 0 <= answer['target_ply'] <= 76
        assert answer['paragraphs']
        for line in answer['lines']:
            review.board_for(game['moves'][:line['base']] + line['moves'])
    practice = example['practice']
    board = review.board_for(game['moves'][:practice['base']] + practice['moves'])
    assert board.fen() == practice['position']['fen']
