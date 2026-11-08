"""End-to-end test of the exact PGN supplied by the user; requires real engines."""
from pathlib import Path
import json
import os
from playwright.sync_api import sync_playwright,expect
with sync_playwright() as p:
 b=p.chromium.launch(); page=b.new_page(viewport={'width':1440,'height':900}); errors=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto(os.getenv('TEST_BASE_URL', 'http://127.0.0.1:8765'))
 page.locator('#pgn').fill((Path(__file__).parent / 'fixtures/aldinobabinote.pgn').read_text())
 with page.expect_response(lambda r:'/api/review/import' in r.url) as res:page.locator('#send-pgn').click()
 print('Import:',res.value.status,flush=True)
 page.wait_for_url('**/?game=pgn-*');print('URL:',page.url,flush=True)
 page.wait_for_function('typeof report!=="undefined" && report!==null && !busy',timeout=240000)
 info=page.evaluate('({headers:game.headers,halfmoves:game.moves.length,rows:report.rows.length,engine:report.engine,ranking:report.ranking.slice(0,3).map(r=>({label:r.label,kind:r.kind,loss_cp:r.loss_cp}))})')
 print('Analysis:',json.dumps(info,ensure_ascii=False),flush=True)
 assert info['halfmoves']==55 and info['rows']==28
 page.screenshot(path='/tmp/iajedrez-user-pgn-analysis.png')
 page.locator('#question').fill('¿Cuáles fueron mis errores principales jugando con blancas? Explica brevemente y respeta que gané por tiempo según el PGN.')
 with page.expect_response(lambda r:'/api/review/query' in r.url,timeout=180000) as res:page.locator('#ask-form .send').click()
 print('Tutor status:',res.value.status,flush=True)
 answer=res.value.json();print('Tutor:',json.dumps(answer,ensure_ascii=False),flush=True)
 assert res.value.status==200 and answer['model']=='llama3.1:8b'
 expect(page.locator('.secondary-box')).to_be_visible()
 page.screenshot(path='/tmp/iajedrez-user-pgn-tutor.png')
 assert not errors,errors
 print('SUCCESS; no JS errors',flush=True);b.close()
