"""Run with a server at localhost:8765; screenshots go to the OS temp folder."""
from pathlib import Path
import tempfile
from playwright.sync_api import sync_playwright, expect

with sync_playwright() as p:
    browser = p.chromium.launch(channel='msedge', headless=True)
    page = browser.new_page(viewport={'width': 1440, 'height': 1000})
    errors = []
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.on('console', lambda msg: errors.append(msg.text) if msg.type == 'error' else None)
    page.goto('http://127.0.0.1:8765')
    expect(page).to_have_title('IAjedrez · Revisión guiada')
    expect(page.locator('#board button')).to_have_count(64)
    expect(page.locator('#menu')).to_be_hidden()
    page.screenshot(path=str(Path(tempfile.gettempdir())/'iajedrez-demo-desktop.png'), full_page=True)

    # Identify a concrete error, then ask a question at a selected step.
    page.locator('[data-task="error"]').click()
    expect(page.locator('#move-label')).to_have_text('45. Cc7')
    page.locator('details[data-step="1"] summary').click()
    page.locator('[data-ask-step="1"]').click()
    page.locator('#question').fill('¿Por qué pierdo el caballo?')
    page.locator('#ask .send').click()
    expect(page.locator('#title')).to_have_text('Duda secundaria')
    expect(page.locator('.tree-question')).to_have_count(1)
    page.locator('[data-action="backQuestion"]').click()
    expect(page.locator('details[data-step="1"]')).to_have_attribute('open', '')

    # Learn: replay the mistake, reset and find a safe square; return to the exact step.
    page.locator('[data-action="learn"]').click()
    page.locator('[data-square="e6"]').click()
    page.locator('[data-square="c7"]').click()
    page.locator('[data-action="reply"]').click()
    expect(page.locator('[data-square="c7"]')).to_have_attribute('aria-label','c7 caballo negro')
    page.locator('[data-action="retry"]').click()
    page.locator('[data-square="e6"]').click()
    page.locator('[data-square="c5"]').click()
    expect(page.locator('.learn-feedback')).to_have_class('learn-feedback success')
    page.locator('[data-action="leaveLearn"]').click()
    expect(page.locator('#move-label')).to_have_text('45. Cc7')
    expect(page.locator('details[data-step="1"]')).to_have_attribute('open','')

    # Secondary branch: walk a legal line, then return to the original position and step.
    page.locator('#tree [data-ply="57"]').click()
    page.locator('details[data-step="2"] summary').click()
    page.locator('[data-question="moment"]').click()
    page.locator('[data-action="line29"]').click()
    expect(page.locator('#move-label')).to_have_text('29… Dh1+')
    page.locator('#next').click()
    expect(page.locator('#move-label')).to_have_text('30. Re2')
    page.locator('#next').click()
    expect(page.locator('#move-label')).to_have_text('30… Dxh3')
    page.locator('[data-action="backQuestion"]').click()
    expect(page.locator('#move-label')).to_have_text('29. Rf1')
    expect(page.locator('details[data-step="2"]')).to_have_attribute('open','')
    page.screenshot(path=str(Path(tempfile.gettempdir())/'iajedrez-demo-chain.png'),full_page=True)

    # Unknown free text is explicitly handled as unsupported, never fabricated.
    page.locator('#question').fill('Quiero comprar un telescopio')
    page.locator('#ask .send').click()
    expect(page.locator('.secondary-box')).to_contain_text('no genera respuestas nuevas')
    page.locator('[data-action="backQuestion"]').click()
    page.locator('#toggle').click()
    page.locator('[data-view="advice"]').click()
    expect(page.locator('#title')).to_have_text('Consejos')
    page.locator('#toggle').click()
    page.locator('[data-view="references"]').click()
    expect(page.locator('#title')).to_have_text('Referencias')
    page.locator('#tree [data-ply="108"]').click()
    expect(page.locator('#turn')).to_have_text('0–1 · por tiempo')
    page.locator('#reset-demo').click()
    expect(page.locator('.tree-question')).to_have_count(0)

    page.set_viewport_size({'width':390,'height':844})
    expect(page.locator('#menu')).to_be_hidden()
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
    page.locator('#toggle').click()
    page.locator('[data-view="learn"]').click()
    page.locator('[data-square="e6"]').click()
    page.locator('[data-square="g7"]').click()
    expect(page.locator('.learn-feedback')).to_have_class('learn-feedback success')
    page.screenshot(path=str(Path(tempfile.gettempdir())/'iajedrez-demo-mobile.png'), full_page=True)
    assert not errors, errors
    browser.close()
    print('PASS: three demo flows, contextual return, legal variants, fallback, menu, reset, mobile, console.')
