// Records Brightday clip 4 from the public site: the Investing page, a scroll from the
// "Who are you?" section through the investment options, with a fake cursor.
// The headless browser does not trust the session's egress proxy certificate, so every
// request is fetched through curl (which does) and handed to the page; TLS stays verified.
//   OUT_DIR=frames4 W=1920 H=1080 node scripts/record-invest-clip.mjs
//   PHONE=1 OUT_DIR=frames4v node scripts/record-invest-clip.mjs   (405x720 at 2.667x for 9:16)
import { chromium } from 'playwright-core'
import { mkdirSync, rmSync, readFileSync, unlinkSync } from 'node:fs'
import { execFileSync } from 'node:child_process'
const OUT = process.env.OUT_DIR || 'frames4'
const PHONE = !!process.env.PHONE
const W = PHONE ? 405 : parseInt(process.env.W || '1920'), H = PHONE ? 720 : parseInt(process.env.H || '1080')
const URL = process.env.URL || 'https://www.brightday.com.au/invest'
rmSync(OUT, { recursive: true, force: true }); mkdirSync(OUT)
const b = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || '/opt/pw-browsers/chromium' })
const ctx = await b.newContext({ viewport: { width: W, height: H }, deviceScaleFactor: PHONE ? 1080 / 405 : 1, isMobile: PHONE, hasTouch: PHONE,
  userAgent: PHONE ? 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1' : undefined })
const p = await ctx.newPage()
const cache = new Map()
await p.route('**/*', async (r) => {
  const req = r.request(); const u = req.url()
  if (req.method() !== 'GET' || !u.startsWith('http')) return r.abort()
  try {
    if (!cache.has(u)) {
      const tmp = `/tmp/claude-0/curl-${process.pid}-${cache.size}`
      const type = execFileSync('curl', ['-sS', '-L', '-o', tmp, '-w', '%{content_type}', '-A', req.headers()['user-agent'] || 'Mozilla/5.0', u], { maxBuffer: 64 * 1024 * 1024 }).toString().trim()
      cache.set(u, { body: readFileSync(tmp), type: type || 'application/octet-stream' }); unlinkSync(tmp)
    }
    const { body, type } = cache.get(u)
    await r.fulfill({ status: 200, contentType: type, body })
  } catch (e) { await r.abort() }
})
let n = 0
const FPS = 24
async function frame() { await p.screenshot({ path: `${OUT}/f${String(n++).padStart(4, '0')}.png`, animations: 'disabled' }) }
async function hold(ms) { for (let i = 0; i < Math.round(ms / 1000 * FPS); i++) await frame() }
const ease = (t) => (t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t)
async function smoothScroll(to, ms) {
  const from = await p.evaluate(() => window.scrollY); const steps = Math.round(ms / 1000 * FPS)
  for (let i = 1; i <= steps; i++) { await p.evaluate((y) => window.scrollTo(0, y), from + (to - from) * ease(i / steps)); await frame() }
}
async function addCursor() {
  if (PHONE) return
  await p.addStyleTag({ content: '#fakecur{position:fixed;left:0;top:0;width:24px;height:24px;pointer-events:none;z-index:99999;transform:translate(-3px,-2px);filter:drop-shadow(0 2px 3px rgba(0,0,0,.45))}' })
  await p.evaluate(() => { const c = document.createElement('div'); c.id = 'fakecur'; c.innerHTML = '<svg viewBox="0 0 24 24" width="24" height="24"><path d="M5 3l14 9-6 1 4 7-2.5 1.2L10.5 14 6 18z" fill="#fff" stroke="#111" stroke-width="1.2"/></svg>'; document.body.appendChild(c); window.__cur = (x, y) => { c.style.left = x + 'px'; c.style.top = y + 'px' } })
}
async function moveTo(x0, y0, x1, y1, ms) {
  if (PHONE) return
  const steps = Math.round(ms / 1000 * FPS)
  for (let i = 1; i <= steps; i++) { const e = ease(i / steps); const x = x0 + (x1 - x0) * e, y = y0 + (y1 - y0) * e; await p.evaluate(([x, y]) => window.__cur(x, y), [x, y]); await frame() }
}
await p.goto(URL, { waitUntil: 'networkidle', timeout: 120000 })
await p.evaluate(async () => { await document.fonts.ready })
// hide cookie banners and announcement bars if any
await p.addStyleTag({ content: '.sqs-cookie-banner-v2, .sqs-announcement-bar-dropzone, #siteWrapper .sqs-popup-overlay{display:none!important}' })
await p.waitForTimeout(500)
await addCursor()
const who = await p.evaluate(() => { const h = [...document.querySelectorAll('h1,h2,h3')].find((e) => /who are you/i.test(e.textContent)); return h ? h.getBoundingClientRect().top + window.scrollY : 600 })
let cx = W * 0.78, cy = H * 0.35
await p.evaluate(([x, y]) => window.__cur && window.__cur(x, y), [cx, cy])
await hold(500)
await smoothScroll(Math.max(0, Math.round(who - H * 0.18)), 1500)
await hold(450)
await moveTo(cx, cy, W * 0.52, H * 0.55, 500); cx = W * 0.52; cy = H * 0.55
await hold(200)
await smoothScroll(Math.max(0, Math.round(who + H * 0.75)), 1500)
await hold(450)
await smoothScroll(Math.max(0, Math.round(who + H * 1.55)), 1300)
await hold(650)
await b.close()
console.log('frames', n, 'who at', who)
