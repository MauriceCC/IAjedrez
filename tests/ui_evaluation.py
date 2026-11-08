"""Navigation and evaluation-table interactions against the local server."""
import os
import tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

BASE=os.getenv('IAJEDREZ_TEST_URL','http://127.0.0.1:8765')
with sync_playwright() as p:
    browser=p.chromium.launch(channel='msedge',headless=True)
    page=browser.new_page(viewport={'width':1440,'height':900})
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    for game,count,last in [('entrevista',54,'54'),('mauricio',19,'19'),('gemini',34,'34.')]:
        page.goto(BASE+'/?game='+game)
        expect(page.locator('.priority-table')).to_be_visible()
        assert page.locator('.priority-table th').evaluate_all('(es)=>es.map(e=>{const c=e.cloneNode(true);c.querySelectorAll(".type-legend").forEach(t=>t.remove());return c.textContent})')==['Jugada','Tipo ?','Explicación','Jugada sugerida']
        expect(page.locator('#first')).to_be_disabled()
        page.locator('#last').click()
        expect(page.locator('#current-move')).to_contain_text(last)
        expect(page.locator('#last')).to_be_disabled()
        page.locator('#first').click()
        expect(page.locator('#current-move')).to_have_text('Posición inicial')
        first=page.locator('.priority-table tbody tr').first
        expect(first.locator('.eval-score')).to_have_count(2)
        first.locator('[data-preview]').first.click()
        expect(page.locator('[data-view="summary"]')).to_have_attribute('aria-pressed','true')
        expect(page.locator('.board-arrows')).to_be_visible()
        expect(page.locator('#move-subtitle')).to_contain_text('Variante')
        page.locator('#next').click()
        expect(page.locator('#move-subtitle')).to_contain_text('2/')
        page.locator('#last').click()
        expect(page.locator('.board-arrows')).to_have_count(0)
        expect(page.locator('#current-move')).to_contain_text(last)
        page.locator('[data-view="advice"]').click()
        expect(page.locator('.evaluation-table tbody tr')).to_have_count(count)
        assert page.locator('.evaluation-table th').evaluate_all('(es)=>es.map(e=>{const c=e.cloneNode(true);c.querySelectorAll(".type-legend").forEach(t=>t.remove());return c.textContent})')==['Jugada','Tipo ?','Consejo','Explicación']
        page.locator('.type-help').hover()
        expect(page.locator('#type-legend')).to_contain_text('Brillante')
        page.keyboard.press('Escape')
        page.locator('.evaluation-table [data-preview]').first.click()
        expect(page.locator('[data-view="advice"]')).to_have_attribute('aria-pressed','true')
        expect(page.locator('.board-arrows')).to_be_visible()
        page.locator('#results [data-back-line]').click()
        page.locator('.evaluation-table [data-jump]').first.click()
        expect(page.locator('[data-view="chain"]')).to_have_attribute('aria-pressed','true')
    page.goto(BASE+'/?game=entrevista')
    page.locator('[data-view="advice"]').click()
    page.locator('[data-preview="89"]').first.click()
    expect(page.locator('#current-move')).to_contain_text('Cg7+')
    page.screenshot(path=str(Path(tempfile.gettempdir())/'iajedrez-evaluation.png'))
    page.set_viewport_size({'width':390,'height':844})
    page.locator('[data-panel="right-panel"]').click()
    expect(page.locator('#first')).to_be_visible()
    expect(page.locator('#last')).to_be_visible()
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    sizes=page.locator('#board .square').evaluate_all('(es)=>es.map(e=>{const r=e.getBoundingClientRect();return [r.width,r.height]})')
    assert all(abs(w-h)<1 for w,h in sizes)
    page.screenshot(path=str(Path(tempfile.gettempdir())/'iajedrez-evaluation-mobile.png'))
    assert not errors,errors
    print('PASS: all three studies, endpoint navigation, separate cell actions, evaluations, legend, arrows, return, mobile; no JS errors')
    browser.close()
