import os
from playwright.sync_api import sync_playwright,expect
with sync_playwright() as p:
 b=p.chromium.launch();page=b.new_page(viewport={'width':1440,'height':900});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto(os.getenv('TEST_BASE_URL','http://127.0.0.1:8766'));page.locator('.side-option').nth(1).click()
 with page.expect_file_chooser() as chooser:page.locator('#attach-pgn').click()
 chooser.value.set_files({'name':'partida.pgn','mimeType':'application/x-chess-pgn','buffer':b'1. e4 e5 2. Nf3 Nc6 *'})
 expect(page.locator('#pgn')).to_have_value('1. e4 e5 2. Nf3 Nc6 *')
 page.locator('#send-pgn').click();page.wait_for_url('**/?game=pgn-*');page.wait_for_function('report && !busy',timeout=60000)
 assert page.evaluate('game.player_color')=='black';assert page.evaluate('report.rows.map(r=>r.ply)')==[2,4]
 page.locator('[data-view="advice"]').click();page.wait_for_function('!busy');page.locator('[data-preview="2"]').first.click();page.wait_for_function('!busy');assert page.locator('.board-arrows').count()==1
 page.locator('#results [data-back-line]').click();page.wait_for_function('!busy');page.locator('#question').fill('Juego con negras. Explica brevemente mi jugada 1...e5 usando la evidencia.')
 with page.expect_response(lambda r:'/api/review/query' in r.url,timeout=180000) as response:page.locator('#question').press('Enter')
 assert response.value.status==200,response.value.text();print('Ollama:',response.value.json()['model'],flush=True)
 page.wait_for_function('!busy');page.locator('[data-view="learn"]').click();page.wait_for_function('!busy');page.locator('[data-learn]').click();page.wait_for_function('!busy');assert page.evaluate('state.practice.position.turn')=='negras'
 move=page.evaluate('report.rows.find(r=>r.ply===state.practice.base+1).best.pv[0]');page.locator(f'[data-square="{move[:2]}"]').click();page.locator(f'[data-square="{move[2:4]}"]').click();page.wait_for_function('state.practice.result && !busy',timeout=30000)
 for kind in ['pgn','png']:
  page.locator('.download-menu summary').click()
  with page.expect_download():page.locator(f'[data-download="{kind}"]').click()
 assert not errors,errors
 page.goto(os.getenv('TEST_BASE_URL','http://127.0.0.1:8766'));page.set_viewport_size({'width':390,'height':844});page.screenshot(path='/tmp/new-ui-import-mobile.png',full_page=True)
 print('Color, file picker, analysis, arrows, Ollama, black practice and downloads OK');b.close()
