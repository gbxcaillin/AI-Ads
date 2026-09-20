// Records the 9:16 product clip for social: the Tools & Insights page on a phone
// viewport (405x720 at 2.667x, so frames are 1080x1920), a smooth scroll down to the
// Business Health Check card, a tap, and the first two wizard steps. No cursor; taps
// are shown as a soft ripple. Portrait sibling of record-tools-clip.mjs.
//
//   npm run build && npx vite preview --port 4173 --host 127.0.0.1   (site repo, other shell)
//   node record-tools-clip-9x16.mjs
//   ffmpeg -framerate 24 -i frames5v/f%04d.png -t 7.25 -c:v libx264 -pix_fmt yuv420p -crf 18 clip5-tools-9x16.mp4
import { chromium } from 'playwright-core'
import { readFileSync, mkdirSync, rmSync } from 'node:fs'
const fontCss = readFileSync(new URL('./fonts/site-embedded.css', import.meta.url), 'utf8')
const OUT = process.env.OUT_DIR || 'frames5v'
const BASE = process.env.SITE || 'http://127.0.0.1:4173'
rmSync(OUT, { recursive: true, force: true }); mkdirSync(OUT)
const b = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || '/opt/pw-browsers/chromium' })
const ctx = await b.newContext({ viewport: { width: 405, height: 720 }, deviceScaleFactor: 1080 / 405, isMobile: true, hasTouch: true })
const p = await ctx.newPage()
await p.route('https://fonts.googleapis.com/**', (r) => r.fulfill({ status: 200, contentType: 'text/css', body: fontCss }))
await p.route('https://fonts.gstatic.com/**', (r) => r.abort())
let n = 0
const FPS = 24
async function frame() { await p.screenshot({ path: `${OUT}/f${String(n++).padStart(4, '0')}.png`, animations: 'disabled' }) }
async function hold(ms) { for (let i = 0; i < Math.round(ms / 1000 * FPS); i++) await frame() }
const ease = (t) => (t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t)
async function smoothScroll(to, ms) {
  const from = await p.evaluate(() => window.scrollY); const steps = Math.round(ms / 1000 * FPS)
  for (let i = 1; i <= steps; i++) { await p.evaluate((y) => window.scrollTo(0, y), from + (to - from) * ease(i / steps)); await frame() }
}
async function addRipple() {
  await p.addStyleTag({ content: '#tap{position:fixed;left:0;top:0;width:44px;height:44px;margin:-22px 0 0 -22px;border-radius:50%;background:rgba(46,139,110,.35);border:2px solid rgba(46,139,110,.8);pointer-events:none;z-index:99999;opacity:0;transform:scale(.4)}' })
  await p.evaluate(() => { const c = document.createElement('div'); c.id = 'tap'; document.body.appendChild(c); window.__tap = (x, y, s, o) => { c.style.left = x + 'px'; c.style.top = y + 'px'; c.style.transform = 'scale(' + s + ')'; c.style.opacity = o } })
}
async function tap(locator, ms = 300) {
  const bb = await locator.boundingBox(); const x = bb.x + bb.width / 2, y = bb.y + bb.height / 2
  const steps = Math.round(ms / 1000 * FPS)
  for (let i = 0; i < steps; i++) { const k = i / steps; await p.evaluate(([x, y, s, o]) => window.__tap(x, y, s, o), [x, y, 0.4 + 0.9 * k, 1 - k]); await frame() }
  await p.evaluate(() => window.__tap(0, 0, 0.4, 0))
  await locator.click()
}
await p.goto(`${BASE}/tools`, { waitUntil: 'networkidle' })
await p.evaluate(async () => { await document.fonts.ready })
await p.waitForTimeout(300)
await addRipple()
await hold(500)
// scroll down to the health check card, in two moves with a short settle between
const card = p.locator('a:has-text("Start the check")').first()
const cardTop = await card.evaluate((el) => el.getBoundingClientRect().top + window.scrollY)
await smoothScroll(Math.max(0, Math.round(cardTop * 0.45)), 1300)
await hold(320)
await smoothScroll(Math.max(0, Math.round(cardTop - 480)), 1300)
await hold(300)
await tap(card)
await p.waitForLoadState('networkidle'); await p.evaluate(async () => { await document.fonts.ready }); await addRipple()
await hold(500)
for (let k = 0; k < 2; k++) {
  const opt = p.locator('.wizard__options button').nth(1)
  await opt.evaluate((el) => el.scrollIntoView({ block: 'center' }))
  await hold(80)
  await tap(opt, 260)
  await p.waitForTimeout(160)
  await hold(400)
}
await hold(600)
await b.close()
console.log('frames', n)
