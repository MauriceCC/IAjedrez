"""Replay the user's conversation against real Stockfish. Start the local server first.
Run: venv/bin/python tests/ui_review.py (screenshots are saved in the OS temp directory).
"""
from pathlib import Path
import os
import tempfile
from playwright.sync_api import sync_playwright, expect

BASE_URL = os.getenv('IAJEDREZ_TEST_URL', 'http://127.0.0.1:8765')
ARTIFACTS = Path(tempfile.gettempdir())

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width':1440,'height':900})
    page.set_default_timeout(15000)
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.on('console', lambda msg: errors.append(msg.text) if msg.type == 'error' else None)
    page.goto(BASE_URL+'/?game=mauricio')
    expect(page).to_have_title('IAjedrez — Análisis de ajedrez con IA | Prototipo')
    expect(page.locator('#board .square')).to_have_count(64)
    expect(page.locator('#view-menu')).to_be_hidden()
    board_box = page.locator('#board').bounding_box()

    def fixed_board():
        assert page.locator('#board').bounding_box() == board_box
        assert page.evaluate('window.scrollY') == 0

    def ask(question):
        page.locator('#question').fill(question)
        page.locator('#ask-form .send').click()
        expect(page.locator('#ask-form .send')).to_be_enabled(timeout=180000)
        expect(page.locator('.secondary-box h3')).to_have_text(question.split('[Site ')[0].strip())
        fixed_board()

    def view(name):
        page.locator('#view-toggle').click()
        page.locator(f'#view-menu [data-view="{name}"]').click()
        expect(page.locator('#view-toggle')).to_be_enabled(timeout=180000)
        fixed_board()

    # The same first question, including the supplied PGN, is sent to the real API.
    question = 'Hola ChatGPT, eres experto en ajedrez, ¿podrías indicarme cuál fue mi error en esta partida, por favor?'
    ask(question+'\n'+Path('static/partida-mauricio.pgn').read_text())
    expect(page.locator('.secondary-box')).to_contain_text('19 jugadas')
    expect(page.locator('.secondary-box')).to_contain_text('Stockfish')
    page.locator('[data-summary]').click()
    expect(page.locator('.results-table tbody tr')).not_to_have_count(0)
    page.screenshot(path=str(ARTIFACTS/'iajedrez-stockfish-summary.png'))

    # Follow the earlier 9.Nd2 claim, ask within step 3, explore and return exactly.
    page.locator('[data-jump="17"]').click()
    page.locator('[data-step="2"]').click()
    ask('¿Fue 9. Nd2 el primer error importante?')
    expect(page.locator('.secondary-box')).to_contain_text('7. Ag3')
    page.locator('[data-answer-line="1"]').click()
    expect(page.locator('#current-move')).to_have_text('9. Cd2')
    page.locator('#next').click()
    expect(page.locator('#current-move')).to_have_text('9… Dxg3+')
    page.locator('#next').click()
    expect(page.locator('#current-move')).to_have_text('10. Re2')
    page.locator('#results [data-back-line]').click()
    page.locator('[data-return-analysis]').click()
    expect(page.locator('[data-step="2"]')).to_have_attribute('aria-expanded','true')
    expect(page.locator('#current-move')).to_have_text('9. Cd2')
    expect(page.locator('.query-link')).to_have_count(2)
    fixed_board()

    # The proposed Qf3 defense must include the opponent's actual calculated reply.
    view('resources')
    page.locator('[data-question="¿Era mejor 9. Qf3?"]').click()
    expect(page.locator('#ask-form .send')).to_be_enabled(timeout=180000)
    expect(page.locator('.secondary-box')).to_contain_text('Dc1+')
    page.locator('[data-answer-line="1"]').click()
    expect(page.locator('#current-move')).to_have_text('9. Df3')
    page.locator('#next').click()
    expect(page.locator('#current-move')).to_have_text('9… Dc1+')
    page.locator('#results [data-back-line]').click()
    page.locator('[data-return-analysis]').click()

    # Legal final defense, five moves, unchanged original game, then return.
    ask('¿Era mate después de 19...Rd2+?')
    expect(page.locator('.secondary-box')).to_contain_text('no es jaque mate')
    expect(page.locator('.secondary-box')).to_contain_text('5 peones blancos y 6 negros')
    page.locator('[data-answer-line="0"]').click()
    expect(page.locator('#current-move')).to_have_text('20. Dxd2')
    for _ in range(4):
        page.locator('#next').click()
        expect(page.locator('#prev')).to_be_enabled()
    expect(page.locator('#current-move')).to_have_text('22. Rxd2')
    expect(page.locator('[data-square="d2"]')).to_have_attribute('aria-label','d2 rey blanco')
    expect(page.locator('#board [aria-label$="peón blanco"]')).to_have_count(5)
    expect(page.locator('#board [aria-label$="peón negro"]')).to_have_count(6)
    fixed_board()
    page.screenshot(path=str(ARTIFACTS/'iajedrez-stockfish-final.png'))
    page.locator('#results [data-back-line]').click()
    page.locator('[data-return-analysis]').click()
    expect(page.locator('#current-move')).to_have_text('9. Cd2')

    # Practice is evaluated by the actual engine, not a prepared feedback string.
    view('chain')
    page.locator('[data-step="2"]').click()
    view('learn')
    page.locator('[data-square="d1"]').click()
    page.locator('[data-square="f3"]').click()
    expect(page.locator('.lesson-status')).to_contain_text('Stockfish',timeout=30000)
    expect(page.locator('#current-move')).to_have_text('9. Df3')
    page.locator('[data-reply]').click()
    expect(page.locator('#current-move')).to_have_text('9… Dc1+')
    page.locator('[data-retry]').click()
    page.locator('[data-square="g1"]').click()
    page.locator('[data-square="e2"]').click()
    expect(page.locator('.lesson-status')).to_contain_text('Stockfish',timeout=30000)
    page.locator('[data-exit-learn]').click()
    expect(page.locator('[data-step="2"]')).to_have_attribute('aria-expanded','true')
    expect(page.locator('#current-move')).to_have_text('9. Cd2')
    fixed_board()
    ask('Quiero comprar un telescopio')
    expect(page.locator('.secondary-box')).to_contain_text('No he validado')
    page.locator('[data-return-analysis]').click()

    # Independent scrolling and the same fixed board on a small viewport.
    page.set_viewport_size({'width':390,'height':844})
    page.locator('[data-panel="right-panel"]').click()
    board_box = page.locator('#board').bounding_box()
    for name in ['advice','resources','chain','learn']:
        view(name)
        results = page.locator('#results')
        results.hover()
        page.mouse.wheel(0,2000)
        page.wait_for_timeout(150)
        assert results.evaluate('(e)=>e.scrollTop') > 0
        fixed_board()
        if name=='learn':
            page.screenshot(path=str(ARTIFACTS/'iajedrez-stockfish-mobile.png'))
            page.locator('[data-exit-learn]').click()
    page.locator('[data-panel="tree-panel"]').click()
    page.locator('.tree-scroll').hover()
    page.mouse.wheel(0,2000)
    page.wait_for_timeout(150)
    assert page.locator('.tree-scroll').evaluate('(e)=>e.scrollTop') > 0
    fixed_board()
    assert not errors, errors
    browser.close()
    print('PASS: original query + PGN, move 9, Qf3, final defense, engine practice, exact context return, unsupported query, fixed board, independent mobile scroll, no console errors.')
