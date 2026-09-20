// Records the Brightday end card at 1920x1080: the OpenArt logo animation plays as the
// ground (frames in logoframes/, navy #0A1E39), then the tagline, the address and the
// general advice line fade in on cue. A slow push-in runs throughout.
//   ffmpeg -i brand/brightday-logo-animation-832x480.mp4 -vf "fps=24,scale=1920:-2" logoframes/l%04d.png
//   T6='{"tag":4.5,"url":5.9}' OUT_DIR=frames6 node scripts/record-endcard-brightday.mjs
//   ffmpeg -framerate 24 -i frames6/f%04d.png -c:v libx264 -pix_fmt yuv420p -crf 18 clips/clip6-endcard-picture.mp4
import { chromium } from 'playwright-core'
import { readFileSync, mkdirSync, rmSync, readdirSync } from 'node:fs'
const fontCss = readFileSync(new URL('./fonts/brightday-embedded.css', import.meta.url), 'utf8')
const FPS = 24, TOTAL = parseFloat(process.env.TOTAL || '8.0'), N = Math.round(TOTAL * FPS)
const LOGO_DIR = process.env.LOGO_DIR || 'logoframes'
const LOGO_FRAMES = readdirSync(LOGO_DIR).filter((f) => f.endsWith('.png')).length
const W = parseInt(process.env.W || '1920'), H = parseInt(process.env.H || '1080')
const OUT = process.env.OUT_DIR || 'frames6'
const T = { tag: 4.5, url: 5.9, ...(process.env.T6 ? JSON.parse(process.env.T6) : {}) }
const NAVY = '#0A1E39', PINK = '#F5157A', WHITE = '#FFFFFF'
const b = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || '/opt/pw-browsers/chromium' })
const ctx = await b.newContext({ viewport: { width: W, height: H }, deviceScaleFactor: 1 })
const p = await ctx.newPage()
rmSync(OUT, { recursive: true, force: true }); mkdirSync(OUT)
const portrait = H > W
// the animation frames are 16:9; in portrait they sit centred with navy above and below
const logoW = portrait ? W : W, logoH = Math.round(logoW * 9 / 16)
const logoTop = portrait ? Math.round(H * 0.30 - logoH / 2) : 0
const tagTop = portrait ? Math.round(H * 0.30 + logoH / 2 + 40) : Math.round(H * 0.72)
const urlTop = portrait ? tagTop + 300 : Math.round(H * 0.84)
const tagSize = portrait ? 52 : 48, urlSize = portrait ? 40 : 36, compSize = portrait ? 24 : 20
const html = `<!doctype html><html><head><style>${fontCss}
html,body{margin:0;width:${W}px;height:${H}px;background:${NAVY};overflow:hidden;font-family:'Work Sans',sans-serif}
#stage{position:absolute;inset:0;transform-origin:${W / 2}px ${H / 2}px}
#logo{position:absolute;left:0;top:${logoTop}px;width:${logoW}px;height:${logoH}px;display:block}
#tag{position:absolute;left:0;right:0;top:${tagTop}px;text-align:center;opacity:0;padding:0 80px}
#tag .line{font-family:'Ubuntu',sans-serif;font-weight:700;font-size:${tagSize}px;line-height:1.3;color:${WHITE};margin:0}
#tag .line b{color:${PINK};font-weight:700}
#url{position:absolute;left:0;right:0;top:${urlTop}px;text-align:center;opacity:0;font-family:'Work Sans',sans-serif;font-weight:600;font-size:${urlSize}px;letter-spacing:.06em;color:${WHITE}}
#comp{position:absolute;left:0;right:0;bottom:${portrait ? 150 : 40}px;text-align:center;opacity:0;font-family:'Work Sans',sans-serif;font-weight:400;font-size:${compSize}px;color:rgba(255,255,255,.62);padding:0 80px;line-height:1.5}
</style></head><body>
<div id="stage">
<img id="logo" src="/__cap/${LOGO_DIR}/l0001.png">
<div id="tag"><p class="line"><b>Better</b> super. <b>Better</b> investing. <b>Better</b> advice.</p></div>
<div id="url">brightday.com.au</div>
<div id="comp">General advice only, not personal financial advice. Consider whether it is right for you. Brightday Advisers AFSL 484139.</div>
</div>
</body></html>`
await p.route('http://127.0.0.1:4173/__cap/**', (r) => {
  const u = new URL(r.request().url()); const f = decodeURIComponent(u.pathname.replace('/__cap/', ''))
  if (f === 'index.html') return r.fulfill({ status: 200, contentType: 'text/html', body: html })
  return r.fulfill({ status: 200, contentType: 'image/png', body: readFileSync(f) })
})
await p.goto('http://127.0.0.1:4173/__cap/index.html', { waitUntil: 'load' })
await p.evaluate(async () => { await document.fonts.ready })
await p.waitForTimeout(200)
const ease = (t) => (t <= 0 ? 0 : t >= 1 ? 1 : t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t)
const clamp01 = (t) => Math.max(0, Math.min(1, t))
for (let i = 0; i < N; i++) {
  const t = i / FPS
  const lf = Math.min(i, LOGO_FRAMES - 1) + 1
  const tg = ease(clamp01((t - T.tag) / 0.9))
  const u = ease(clamp01((t - T.url) / 0.8))
  const c = ease(clamp01((t - T.tag - 0.3) / 1.0))
  const z = 1 + 0.05 * (t / TOTAL)
  await p.evaluate(([src, tg, u, c, z, tagTop, urlTop]) => {
    document.getElementById('stage').style.transform = 'scale(' + z + ')'
    const l = document.getElementById('logo'); if (l.getAttribute('src') !== src) { l.src = src }
    const tag = document.getElementById('tag'); tag.style.top = (tagTop + 14 * (1 - tg)) + 'px'; tag.style.opacity = tg
    const url = document.getElementById('url'); url.style.top = (urlTop + 12 * (1 - u)) + 'px'; url.style.opacity = u
    document.getElementById('comp').style.opacity = c
  }, [`/__cap/${LOGO_DIR}/l${String(lf).padStart(4, '0')}.png`, tg, u, c, z, tagTop, urlTop])
  await p.evaluate(() => document.getElementById('logo').decode().catch(() => {}))
  if (i === 0) await p.waitForTimeout(300)
  await p.screenshot({ path: `${OUT}/f${String(i).padStart(4, '0')}.png`, animations: 'disabled' })
}
await b.close()
console.log('frames', N)
