"""Real browser + Stockfish + Ollama smoke test. Run against a fresh server."""
import os
from playwright.sync_api import sync_playwright, expect

BASE = os.getenv('TEST_BASE_URL', 'http://127.0.0.1:8766')
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={'width': 1440, 'height': 900})
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.goto(BASE)
    page.locator('#pgn').fill('1. e5')
    page.locator('#send-pgn').click()
    expect(page.locator('#status')).to_contain_text('PGN inválido')
    page.locator('#pgn').fill('[White "Prueba"]\n[Black "Rival"]\n\n1. e4 e5 2. Nf3 Nc6 *')
    page.locator('#send-pgn').click()
    page.wait_for_url('**/?game=pgn-*')
    page.wait_for_function('typeof report !== "undefined" && report !== null && !busy', timeout=60000)
    expect(page.locator('#board .square')).to_have_count(64)
    page.locator('#question').fill('Explica brevemente 2.Nf3 y qué debo revisar antes de mover.')
    with page.expect_response(lambda r: '/api/review/query' in r.url, timeout=180000) as pending:
        page.locator('#ask-form .send').click()
    response = pending.value
    assert response.status == 200, response.text()
    result = response.json()
    assert result['model'] == 'llama3.1:8b'
    assert result['paragraphs'] and result['target_ply'] == 3
    expect(page.locator('.secondary-box')).to_contain_text('Ollama')
    page.locator('[data-answer-line="0"]').click()
    page.wait_for_function('!!state.line && !busy')
    page.locator('#results [data-back-line]').click()
    page.locator('[data-return-analysis]').click()
    for view in ['summary', 'advice', 'chain', 'learn']:
        page.locator('[data-view="'+view+'"]').click()
        page.wait_for_function('!busy')
    page.locator('[data-learn]').click()
    page.wait_for_function('!!state.practice && !busy')
    page.locator('[data-hint]').click()
    uci = page.evaluate('report.rows.find(r=>r.ply===state.practice.base+1).best.pv[0]')
    page.locator('[data-square="'+uci[:2]+'"]').click()
    page.locator('[data-square="'+uci[2:4]+'"]').click()
    page.wait_for_function('!!state.practice.result && !busy', timeout=30000)
    page.locator('[data-exit-learn]').click()
    page.set_viewport_size({'width':390,'height':844})
    expect(page.locator('#board .square')).to_have_count(64)
    assert not errors, errors
    page.screenshot(path='/tmp/iajedrez-ollama-mobile.png')
    print('PGN, real Ollama response, variants, four views, practice and mobile: OK')
    print('Model:',result['model'], 'Answer:',result['paragraphs'][0][:250])
    browser.close()
