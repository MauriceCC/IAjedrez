"""Real browser/API review of the supplied conversation. Start uvicorn first."""
import json
import os
import tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

BASE = os.getenv('IAJEDREZ_TEST_URL', 'http://127.0.0.1:8765')
ARTIFACTS = Path(tempfile.gettempdir())

with sync_playwright() as p:
    # Browser plugin not available; use installed Edge with Playwright.
    browser = p.chromium.launch(channel='msedge', headless=True)
    page = browser.new_page(viewport={'width':1440, 'height':900})
    page.set_default_timeout(15000)
    errors = []
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.on('console', lambda m: errors.append(m.text) if m.type == 'error' else None)
    page.goto(BASE+'/?game=entrevista')
    expect(page).to_have_title('IAjedrez — Análisis de ajedrez con IA | Prototipo')
    expect(page.locator('#board .square')).to_have_count(64)
    expect(page.locator('.player-name').last).to_have_text('Timmy-t')
    expect(page.locator('.sample-tag')).to_contain_text('tiempo')
    expect(page.locator('.response-tabs button')).to_have_count(5)
    box = page.locator('#board').bounding_box()

    def ask(question):
        page.locator('#question').fill(question)
        page.locator('#ask-form .send').click()
        expect(page.locator('#ask-form .send')).to_be_enabled(timeout=300000)
        expect(page.locator('.secondary-box')).to_be_visible()
        assert page.locator('#board').bounding_box() == box

    def view(name):
        page.locator(f'[data-view="{name}"]').click()
        expect(page.locator('[data-view="summary"]')).to_be_enabled(timeout=300000)

    ask('¿Cuáles fueron mis errores?\n'+Path('static/partida-entrevista.pgn').read_text(encoding='utf-8'))
    expect(page.locator('.secondary-box')).to_contain_text('54 decisiones')
    expect(page.locator('.secondary-box')).to_contain_text('Apertura y desarrollo')
    expect(page.locator('.secondary-box')).to_contain_text('Conversión y tiempo')
    ask('En la jugada 16 activo el alfil de b7; en la 21 quiero una torre activa; en la 29 puede ir a h1.')
    for text in ['16.e4', '21.Te2', '29.Rf1', 'Evidencia Stockfish', 'no es forzada']:
        expect(page.locator('.secondary-box')).to_contain_text(text)
    expect(page.locator('.secondary-box')).to_contain_text('Txc3')
    ask('¿29.Kf1 permite Qh1+?')
    page.screenshot(path=str(ARTIFACTS/'iajedrez-interview-conversation.png'))
    page.get_by_role('button', name='…Dh1+: defensa calculada por Stockfish', exact=True).click()
    expect(page.locator('#current-move')).to_contain_text('Dh1+')
    page.locator('#next').click()
    expect(page.locator('#current-move')).to_contain_text('30.')
    page.locator('#results [data-back-line]').click()
    expect(page.locator('.secondary-box h3')).to_have_text('¿29.Kf1 permite Qh1+?')
    ask('¿Qué ocurrió en 45.Nc7?')
    expect(page.locator('.secondary-box')).to_contain_text('Cg7+')
    view('learn')
    page.locator('#board [data-square="e6"]').click()
    page.locator('#board [data-square="g7"]').click()
    expect(page.locator('.lesson-status')).to_contain_text('Calculado por Stockfish', timeout=30000)
    expect(page.locator('#board [data-square="g7"]')).to_contain_text('♘')
    page.locator('[data-exit-learn]').click()
    expect(page.locator('.secondary-box h3')).to_have_text('¿Qué ocurrió en 45.Nc7?')
    page.locator('[data-summary]').click()
    expect(page.locator('.results-table tbody tr').first).to_be_visible()
    with page.expect_download() as download:
        page.locator('[data-evidence-download]').click()
    path = ARTIFACTS/'iajedrez-interview-ui-evidence.json'
    download.value.save_as(path)
    assert len(json.loads(path.read_text(encoding='utf-8'))['rows']) == 54
    view('advice')
    expect(page.locator('.results-table tbody tr')).to_have_count(54)
    page.locator('#results').evaluate('(e)=>e.scrollTop=e.scrollHeight')
    assert page.locator('#board').bounding_box() == box
    view('resources')
    expect(page.locator('#results')).to_contain_text('Qué dijo cada fuente')
    page.screenshot(path=str(ARTIFACTS/'iajedrez-interview-desktop.png'))
    page.set_viewport_size({'width':390,'height':844})
    page.locator('[data-panel="right-panel"]').click()
    expect(page.locator('#board')).to_be_visible()
    page.screenshot(path=str(ARTIFACTS/'iajedrez-interview-mobile.png'))
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
    # The original study remains available and has the correct player labels.
    page.goto(BASE+'/?game=mauricio')
    expect(page.locator('.player-name').last).to_have_text('Mauricio0120')
    assert not errors, errors
    print('PASS: desktop/mobile, conversation, engine variants, practice, return, download, original study; no console errors.')
    print(ARTIFACTS)
    browser.close()
