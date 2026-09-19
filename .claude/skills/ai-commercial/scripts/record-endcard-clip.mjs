// Records commercial clip 6: the brand mark animating alone on black, then the
// philosophy line in large serif, then www.gbxps.com. Narration is muxed on afterwards.
//
// Steps (run from the repo root):
//   1. npm run build && npx vite preview --port 4173 --host 127.0.0.1   (in another shell)
//   2. Extract the logo animation at 24fps into logoframes/:
//        ffmpeg -i public/media/logo-animation.mp4 -vf fps=24 logoframes/l%04d.png
//   3. node scripts/record-endcard-clip.mjs   (needs scripts/fonts/site-embedded.css)
//   4. ffmpeg -framerate 24 -i frames6/f%04d.png -c:v libx264 -pix_fmt yuv420p \
//        -crf 18 docs/commercial/clip6-endcard-screencap.mp4
//
// A slow push-in runs across the whole card so it never sits as a frozen frame.
// Timeline (8s, default T): logo alone, then at T.up it eases upward, at T.phil the
// philosophy fades in, at T.url the address. Set T6 env (JSON) to match the narration onsets found with ffmpeg silencedetect, e.g. T6='{"up":1.8,"phil":2.3,"url":5.85}'.
import { chromium } from 'playwright-core'
import { readFileSync, mkdirSync, rmSync } from 'node:fs'
const S = process.cwd()
const fontCss = readFileSync(new URL('./fonts/site-embedded.css', import.meta.url), 'utf8')
const FPS = 24, TOTAL = 8.0, N = Math.round(TOTAL * FPS), LOGO_FRAMES = 120
const b = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || '/opt/pw-browsers/chromium' })
const ctx = await b.newContext({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 })
const p = await ctx.newPage()
await p.route('https://fonts.googleapis.com/**', (r) => r.fulfill({ status: 200, contentType: 'text/css', body: fontCss }))
await p.route('https://fonts.gstatic.com/**', (r) => r.abort())

// End card: the animated GBX mark, then the philosophy line, then the address, on
// black. A slow continuous push-in keeps the card alive rather than a frozen frame.
rmSync('frames6', { recursive: true, force: true }); mkdirSync('frames6')
const html = `<!doctype html><html><head><style>${fontCss}
html,body{margin:0;width:1920px;height:1080px;background:#000;overflow:hidden;font-family:'DM Mono',monospace}
#stage{position:absolute;inset:0;transform-origin:960px 540px}
#logo{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:520px;height:520px;display:block}
#phil{position:absolute;left:0;right:0;top:0;text-align:center;opacity:0}
#phil .eyebrow{font-family:'Montserrat',sans-serif;font-weight:500;font-size:20px;letter-spacing:.3em;text-transform:uppercase;color:#2E8B6E;margin:0 0 22px}
#phil .line{font-family:'Cormorant Garamond',serif;font-weight:300;font-style:italic;font-size:74px;line-height:1.18;color:#FFFDF8;margin:0 auto;max-width:1500px}
#url{position:absolute;left:0;right:0;top:0;text-align:center;color:#F5F1E8;font-size:40px;letter-spacing:.3em;opacity:0}
</style></head><body>
<div id="stage">
<img id="logo" src="/__cap/logoframes/l0001.png">
<div id="phil"><p class="eyebrow">Our philosophy</p><p class="line">&ldquo;Combining insight with impact for sustainable business growth.&rdquo;</p></div>
<div id="url">www.gbxps.com</div>
</div>
</body></html>`
// everything is served from the intercept, so no dev server is needed
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
  const logoTop = 540 - 290 * m, logoSize = 520 - 140 * m
  await p.evaluate(([src, logoTop, logoSize, u, ph, z]) => {
    document.getElementById('stage').style.transform = 'scale(' + z + ')'
    const l = document.getElementById('logo'); if (l.getAttribute('src') !== src) { l.src = src }; l.style.top = logoTop + 'px'; l.style.width = l.style.height = logoSize + 'px'
    const phil = document.getElementById('phil'); phil.style.top = (logoTop + logoSize / 2 + 34 + 14 * (1 - ph)) + 'px'; phil.style.opacity = ph
    const url = document.getElementById('url'); url.style.top = (logoTop + logoSize / 2 + 300 + 12 * (1 - u)) + 'px'; url.style.opacity = u
  }, [`/__cap/logoframes/l${String(lf).padStart(4, '0')}.png`, logoTop, logoSize, u, ph, z])
  await p.evaluate(() => document.getElementById('logo').decode().catch(() => {}))
  if (i === 0) await p.waitForTimeout(300)
  await p.screenshot({ path: `frames6/f${String(i).padStart(4, '0')}.png`, animations: 'disabled' })
}
await b.close()
console.log('frames', N)
