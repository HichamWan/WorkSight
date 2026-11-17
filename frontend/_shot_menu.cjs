const { chromium } = require('playwright-core')

;(async () => {
  const browser = await chromium.launch({ channel: 'msedge' })
  const page = await browser.newPage({ viewport: { width: 1280, height: 760 }, deviceScaleFactor: 2 })
  await page.goto('http://localhost:5173/login', { waitUntil: 'networkidle' })
  await page.fill('#li-username', 'alice')
  await page.fill('#li-password', 'password')
  await page.click('button[type="submit"]')
  await page.waitForFunction(() => location.pathname !== '/login', null, { timeout: 25000 })

  const search = page.locator('.gsearch__input')
  await search.click()
  await search.type('e', { delay: 30 })
  await page.waitForTimeout(800)

  const box = await page.locator('.gsearch').boundingBox()
  await page.screenshot({
    path: 'd:/WorkSight/frontend/_menu_ok.png',
    clip: { x: box.x - 20, y: box.y - 20, width: 440, height: 380 }
  })
  await browser.close()
})()
