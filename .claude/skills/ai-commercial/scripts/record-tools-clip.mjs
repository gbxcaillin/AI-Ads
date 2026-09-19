// Records commercial clip 5: a real screen capture of the Tools & Insights page
// and the first two steps of the Business Health Check.
//
// Steps (run from the repo root):
//   1. npm run build && npx vite preview --port 4173      (in another shell)
//   2. Put a CSS file with the site's web fonts embedded as data URIs at
//      scripts/fonts/site-embedded.css (Google Fonts is intercepted and served
//      from that file so headless Chromium renders the real typefaces).
//   3. mkdir -p frames && node scripts/record-tools-clip.mjs
//   4. ffmpeg -framerate 24 -i frames/f%04d.png -t 7.25 -c:v libx264 -pix_fmt yuv420p \
//        -crf 18 docs/commercial/clip5-tools-screencap.mp4
//
// Playwright needs a Chromium binary; set CHROMIUM_PATH if it is not at the
// default location below.
import { chromium } from 'playwright-core'
import { readFileSync } from 'node:fs'
const fontCss = readFileSync(new URL('./fonts/site-embedded.css', import.meta.url), 'utf8')
const b = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || '/opt/pw-browsers/chromium' })
const ctx = await b.newContext({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 })
const p = await ctx.newPage()
await p.route('https://fonts.googleapis.com/**', (r) => r.fulfill({ status: 200, contentType: 'text/css', body: fontCss }))
await p.route('https://fonts.gstatic.com/**', (r) => r.abort())
let n = 0
const FPS = 24
async function frame() { await p.screenshot({ path: `frames/f${String(n++).padStart(4, '0')}.png`, animations: 'disabled' }) }
async function hold(ms) { for (let i = 0; i < Math.round(ms / 1000 * FPS); i++) await frame() }
async function addCursor() {
  await p.addStyleTag({ content: '#fakecur{position:fixed;left:0;top:0;width:24px;height:24px;pointer-events:none;z-index:99999;transform:translate(-3px,-2px);filter:drop-shadow(0 2px 3px rgba(0,0,0,.45))}' })
  await p.evaluate(() => { const c = document.createElement('div'); c.id = 'fakecur'; c.innerHTML = '<svg viewBox="0 0 24 24" width="24" height="24"><path d="M5 3l14 9-6 1 4 7-2.5 1.2L10.5 14 6 18z" fill="#fff" stroke="#111" stroke-width="1.2"/></svg>'; document.body.appendChild(c); window.__cur = (x, y) => { c.style.left = x + 'px'; c.style.top = y + 'px' } })
}
const ease = (t) => (t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t)
async function moveTo(x0, y0, x1, y1, ms) {
  const steps = Math.round(ms / 1000 * FPS)
  for (let i = 1; i <= steps; i++) { const e = ease(i / steps); const x = x0 + (x1 - x0) * e, y = y0 + (y1 - y0) * e; await p.mouse.move(x, y); await p.evaluate(([x, y]) => window.__cur(x, y), [x, y]); await frame() }
}
async function smoothScroll(to, ms) {
  const from = await p.evaluate(() => window.scrollY); const steps = Math.round(ms / 1000 * FPS)
  for (let i = 1; i <= steps; i++) { await p.evaluate((y) => window.scrollTo(0, y), from + (to - from) * ease(i / steps)); await frame() }
}
await p.goto('http://localhost:4173/tools', { waitUntil: 'networkidle' })
await p.evaluate(async () => { await document.fonts.ready })
await p.waitForTimeout(300)
await addCursor()
let cx = 1500, cy = 300
await p.mouse.move(cx, cy); await p.evaluate(([x, y]) => window.__cur(x, y), [cx, cy])
await hold(600)
await smoothScroll(560, 1500)
await hold(380)
await smoothScroll(1150, 1300)
await hold(380)
const card = p.locator('a:has-text("Start the check")').first()
const bb = await card.boundingBox()
const tx = bb.x + bb.width / 2, ty = bb.y + bb.height / 2
await moveTo(cx, cy, tx, ty, 480); cx = tx; cy = ty
await hold(120)
await card.click()
await p.waitForLoadState('networkidle'); await p.evaluate(async () => { await document.fonts.ready }); await addCursor()
await p.evaluate(([x, y]) => window.__cur(x, y), [cx, cy])
await hold(450)
for (let k = 0; k < 2; k++) {
  const opt = p.locator('.wizard__options button').nth(1)
  const ob = await opt.boundingBox(); const ox = ob.x + ob.width / 2, oy = ob.y + ob.height / 2
  await moveTo(cx, cy, ox, oy, 420); cx = ox; cy = oy
  await hold(100)
  await opt.click(); await hold(60)
  await p.waitForTimeout(160)
  await hold(380)
}
await hold(600)
await b.close()
console.log('frames', n)
