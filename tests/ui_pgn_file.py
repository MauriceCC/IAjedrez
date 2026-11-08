"""Local PGN file selection and submission through the real home page."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

BASE = os.getenv('TEST_BASE_URL', 'http://127.0.0.1:8765')
fixture = Path(__file__).parent / 'fixtures/aldinobabinote.pgn'
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={'width': 1440, 'height': 900})
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.goto(BASE)
    field = page.locator('#pgn-file')
    field.set_input_files({'name':'notas.txt','mimeType':'text/plain','buffer':b'1. e4 e5'})
    expect(page.locator('#status')).to_contain_text('extensión .pgn')
    field.set_input_files({'name':'vacio.pgn','mimeType':'application/x-chess-pgn','buffer':b''})
    expect(page.locator('#status')).to_contain_text('vacío')
    field.set_input_files({'name':'grande.pgn','mimeType':'application/x-chess-pgn','buffer':b'x'*100001})
    expect(page.locator('#status')).to_contain_text('100 KB')
    field.set_input_files({'name':'invalido.pgn','mimeType':'application/x-chess-pgn','buffer':b'1. e5'})
    expect(page.locator('#pgn')).to_have_value('1. e5')
    page.locator('#send-pgn').click()
    expect(page.locator('#status')).to_contain_text('PGN inválido')
    with page.expect_file_chooser() as chooser:
        page.locator('#attach-pgn').click()
    chooser.value.set_files(str(fixture))
    expect(page.locator('#pgn')).to_have_value(fixture.read_text().strip())
    expect(page.locator('#status')).to_contain_text('Pulsa Enviar PGN')
    page.set_viewport_size({'width':390,'height':844})
    expect(page.locator('#attach-pgn')).to_be_visible()
    expect(page.locator('#file-preview')).to_be_visible()
    page.screenshot(path='/tmp/iajedrez-import-file-mobile.png', full_page=True)
    with page.expect_request(lambda request:'/api/review/import' in request.url) as pending:
        page.locator('#send-pgn').click()
    assert pending.value.post_data_json['pgn'] == fixture.read_text().strip()
    page.wait_for_url('**/?game=pgn-*')
    page.wait_for_function('typeof game!=="undefined" && game!==null')
    assert page.evaluate('game.moves.length') == 55
    assert page.evaluate('game.headers.White') == 'aldinobabinote'
    assert not errors, errors
    print('Local PGN file: extension, size, empty/invalid PGN, preview, mobile and real import OK')
    browser.close()
