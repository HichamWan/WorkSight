const { chromium } = require('playwright-core')

const BASE = 'http://localhost:5173'

;(async () => {
  const browser = await chromium.launch({ channel: 'msedge' })
  const page = await browser.newPage({ viewport: { width: 1280, height: 800 } })
  const errors = []
  page.on('pageerror', (e) => errors.push(`pageerror: ${e.message}`))
  page.on('console', (m) => {
    if (m.type() === 'error') errors.push(`console: ${m.text()}`)
  })

  try {
    await page.goto(`${BASE}/login`, { waitUntil: 'networkidle' })
    await page.fill('#li-username', 'alice')
    await page.fill('#li-password', 'password')
    await page.click('button[type="submit"]')
    await page.waitForFunction(() => location.pathname !== '/login', null, { timeout: 25000 })

    const search = page.locator('.gsearch__input')
    await search.click()

    for (const term of ['alex', 'eng', 'zzz', 'john smith']) {
      await search.fill('')
      await search.type(term, { delay: 30 })
      await page.waitForTimeout(700)
      const names = await page.locator('.gsearch__name').allInnerTexts()
      console.log(`"${term}" -> ${names.length}: ${names.map((n) => n.trim()).join(', ')}`)
    }

    // menu must be opaque
    await search.fill('')
    await search.type('alex', { delay: 30 })
    await page.waitForTimeout(700)
    const bg = await page.locator('.gsearch__menu').evaluate((el) => getComputedStyle(el).backgroundColor)
    const z = await page.locator('.gsearch__menu').evaluate((el) => getComputedStyle(el).zIndex)
    console.log('menu background:', bg, '| z-index:', z)

    // keyboard nav: ArrowDown then Enter
    await page.keyboard.press('ArrowDown')
    const activeName = await page.locator('.gsearch__item--active .gsearch__name').innerText()
    console.log('active after ArrowDown:', activeName.trim())
    await page.keyboard.press('Enter')
    await page.waitForTimeout(900)
    console.log('Enter navigated to:', await page.evaluate(() => location.pathname))

    await page.screenshot({ path: 'd:/WorkSight/frontend/_search_ok.png' })
    console.log('js errors:', errors.length ? errors : 'none')
  } catch (e) {
    console.log('FAIL:', e.message)
    await page.screenshot({ path: 'd:/WorkSight/frontend/_search_fail.png' })
    console.log('errors:', errors)
  } finally {
    await browser.close()
  }
})()
