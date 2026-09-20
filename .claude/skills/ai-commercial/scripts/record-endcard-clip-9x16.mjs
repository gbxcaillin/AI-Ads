// Records the 9:16 end card (1080x1920) for social: the brand mark animating alone on
// black, then the philosophy line, then www.gbxps.com, with a slow push-in throughout.
// Portrait sibling of record-endcard-clip.mjs; same timeline and T6 env.
//
//   ffmpeg -i public/media/logo-animation.mp4 -vf fps=24 logoframes/l%04d.png
//   T6='{"up":2.0,"phil":2.5,"url":5.9}' node record-endcard-clip-9x16.mjs
//   ffmpeg -framerate 24 -i frames6v/f%04d.png -c:v libx264 -pix_fmt yuv420p -crf 18 clip6-endcard-9x16.mp4
import { chromium } from 'playwright-core'
import { readFileSync, mkdirSync, rmSync } from 'node:fs'
const fontCss = readFileSync(new URL('./fonts/site-embedded.css', import.meta.url), 'utf8')
const FPS = 24, TOTAL = 8.0, N = Math.round(TOTAL * FPS), LOGO_FRAMES = 120
const W = 1080, H = 1920
const OUT = process.env.OUT_DIR || 'frames6v'
const b = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || '/opt/pw-browsers/chromium' })
const ctx = await b.newContext({ viewport: { width: W, height: H }, deviceScaleFactor: 1 })
const p = await ctx.newPage()
await p.route('https://fonts.googleapis.com/**', (r) => r.fulfill({ status: 200, contentType: 'text/css', body: fontCss }))
await p.route('https://fonts.gstatic.com/**', (r) => r.abort())
rmSync(OUT, { recursive: true, force: true }); mkdirSync(OUT)
const html = `<!doctype html><html><head><style>${fontCss}
html,body{margin:0;width:${W}px;height:${H}px;background:#000;overflow:hidden;font-family:'DM Mono',monospace}
#stage{position:absolute;inset:0;transform-origin:${W / 2}px ${H / 2}px}
#logo{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:640px;height:640px;display:block}
#phil{position:absolute;left:0;right:0;top:0;text-align:center;opacity:0;padding:0 70px}
#phil .eyebrow{font-family:'Montserrat',sans-serif;font-weight:500;font-size:22px;letter-spacing:.3em;text-transform:uppercase;color:#2E8B6E;margin:0 0 26px}
#phil .line{font-family:'Cormorant Garamond',serif;font-weight:300;font-style:italic;font-size:78px;line-height:1.16;color:#FFFDF8;margin:0 auto;max-width:940px}
#url{position:absolute;left:0;right:0;top:0;text-align:center;color:#F5F1E8;font-size:40px;letter-spacing:.3em;opacity:0}
</style></head><body>
<div id="stage">
<img id="logo" src="/__cap/logoframes/l0001.png">
<div id="phil"><p class="eyebrow">Our philosophy</p><p class="line">&ldquo;Combining insight with impact for sustainable business growth.&rdquo;</p></div>
<div id="url">www.gbxps.com</div>
</div>
</body></html>`
await p.route('http://127.0.0.1:4173/__cap/**', (r) => {
  const u = new URL(r.request().url()); const f = u.pathname.replace('/__cap/', '')
  if (f === 'index.html') return r.fulfill({ status: 200, contentType: 'text/html', body: html })
  return r.fulfill({ status: 200, contentType: 'image/png', body: readFileSync(f) })
})
await p.goto('http://127.0.0.1:4173/__cap/index.html', { waitUntil: 'load' })
await p.evaluate(async () => { await document.fonts.ready })
await p.waitForTimeout(200)
const T = { up: 2.0, phil: 2.5, url: 5.9, ...(process.env.T6 ? JSON.parse(process.env.T6) : {}) }
const ease = (t) => (t <= 0 ? 0 : t >= 1 ? 1 : t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t)
const clamp01 = (t) => Math.max(0, Math.min(1, t))
for (let i = 0; i < N; i++) {
  const t = i / FPS
  const lf = Math.min(i, LOGO_FRAMES - 1) + 1
  const m = ease(clamp01((t - T.up) / 1.2))        // logo moves up and shrinks
  const ph = ease(clamp01((t - T.phil) / 1.0))     // philosophy fades in
  const u = ease(clamp01((t - T.url) / 0.8))       // web address fades in
  const z = 1 + 0.06 * (t / TOTAL)                 // slow continuous push-in
  const logoTop = H / 2 - 300 * m, logoSize = 640 - 160 * m
  await p.evaluate(([src, logoTop, logoSize, u, ph, z]) => {
    document.getElementById('stage').style.transform = 'scale(' + z + ')'
    const l = document.getElementById('logo'); if (l.getAttribute('src') !== src) { l.src = src }; l.style.top = logoTop + 'px'; l.style.width = l.style.height = logoSize + 'px'
    const phil = document.getElementById('phil'); phil.style.top = (logoTop + logoSize / 2 + 70 + 16 * (1 - ph)) + 'px'; phil.style.opacity = ph
    const url = document.getElementById('url'); url.style.top = (logoTop + logoSize / 2 + 70 + 380 + 14 * (1 - u)) + 'px'; url.style.opacity = u
  }, [`/__cap/logoframes/l${String(lf).padStart(4, '0')}.png`, logoTop, logoSize, u, ph, z])
  await p.evaluate(() => document.getElementById('logo').decode().catch(() => {}))
  if (i === 0) await p.waitForTimeout(300)
  await p.screenshot({ path: `${OUT}/f${String(i).padStart(4, '0')}.png`, animations: 'disabled' })
}
await b.close()
console.log('frames', N)
