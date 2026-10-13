// Storyboard for the Brightday "seven steps" logo animation.
// Eight 16:9 key frames built from the real mark, the real "b" and the real
// wordmark on the logo's own navy (#13355A). Petals in the transition frames
// are drawn stand-ins (rounded pentagons in the brand pink) to show motion.
// Run from repo root: node spots/brightday-logo-steps/storyboard.mjs
import { chromium } from 'playwright-core'
import { readFileSync } from 'node:fs'

const D = 'spots/brightday-logo-steps'
const b64 = (p, m) => `data:${m};base64,` + readFileSync(p).toString('base64')
const MARK = b64(`${D}/brand/brightday-mark.webp`, 'image/webp')
const B = b64(`${D}/brand/b-white.png`, 'image/png')
const WORD = b64(`${D}/brand/wordmark-white.png`, 'image/png')
const UB = 'https://fonts.googleapis.com/css2?family=Ubuntu:wght@500;700&display=swap'

const PINK = '#F00870', DARK = '#980848'
const pent = (cx, cy, r, rot = 0, fill = PINK, op = 1) => {
  const pts = [...Array(5)].map((_, k) => {
    const a = (90 + 72 * k + rot) * Math.PI / 180
    return `${(cx + r * Math.cos(a)).toFixed(1)},${(cy + r * Math.sin(a)).toFixed(1)}`
  }).join(' ')
  return `<polygon points="${pts}" fill="${fill}" stroke="${fill}" stroke-width="${(r * 0.38).toFixed(1)}" stroke-linejoin="round" opacity="${op}" filter="url(#sh)"/>`
}
const svg = (inner) => `<svg class="ov" viewBox="0 0 640 360"><defs>
<filter id="sh" x="-50%" y="-50%" width="200%" height="200%"><feDropShadow dx="0" dy="6" stdDeviation="5" flood-color="#000" flood-opacity=".55"/></filter>
<marker id="ar" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#E8EEF6" opacity=".8"/></marker>
</defs>${inner}</svg>`

// steps: 7 petals as a rising staircase, flat tops (point-down pentagons)
const STEPS = [...Array(7)].map((_, i) => ({ x: 128 + i * 62, top: 296 - i * 30 }))
const stepsSvg = (op = 1) => STEPS.map(s => pent(s.x, s.top + 0.809 * 26, 26, 0, PINK, op)).join('')

const panels = [
  { t: '0.0 to 1.0 s', h: 'The mark', d: 'The mark alone on the navy, lit by a soft key light from above. Deep shadow at the edges.',
    body: `<img src="${MARK}" style="left:256px;top:116px;width:128px">` },
  { t: '1.0 to 1.8 s', h: 'Break apart', d: 'The seven petals unlock and drift outward, each turning as it goes.',
    body: svg([...Array(7)].map((_, k) => { const a = (k * 360 / 7 - 90) * Math.PI / 180; const r = 96
      return `<line x1="${320 + 30 * Math.cos(a)}" y1="${180 + 30 * Math.sin(a)}" x2="${320 + 70 * Math.cos(a)}" y2="${180 + 70 * Math.sin(a)}" stroke="#E8EEF6" stroke-opacity=".35" stroke-width="2" stroke-dasharray="3 5"/>` + pent(320 + r * Math.cos(a), 180 + r * Math.sin(a), 24, k * 51 + 20) }).join('')) },
  { t: '1.8 to 2.6 s', h: 'Seven steps', d: 'They fly into place as a staircase of seven steps, rising left to right.',
    body: svg(stepsSvg()) },
  { t: '2.6 to 4.6 s', h: 'The b climbs', d: 'The white b drops in and hops up the steps, one per beat, with a little squash on each landing.',
    body: svg(stepsSvg() + `<path d="M${STEPS[0].x},${STEPS[0].top - 4} ` + STEPS.slice(1, 5).map((s, i) => `Q${(STEPS[i].x + s.x) / 2},${s.top - 52} ${s.x},${s.top - 4}`).join(' ') + `" fill="none" stroke="#E8EEF6" stroke-opacity=".55" stroke-width="2" stroke-dasharray="4 5" marker-end="url(#ar)"/>`)
      + `<img src="${B}" style="left:${STEPS[4].x - 17}px;top:${STEPS[4].top - 86}px;width:34px">` },
  { t: '4.6 to 5.6 s', h: 'The swirl', d: 'From the top step the b leaps; the steps lift and swirl around it in a tightening spiral.',
    body: svg([...Array(7)].map((_, k) => { const a = (k * 360 / 7) * Math.PI / 180; const r = 92 + k * 3
      return pent(320 + r * Math.cos(a), 168 + r * 0.62 * Math.sin(a), 20, k * 40) }).join('')
      + `<path d="M190,120 A140,90 0 0 1 452,140" fill="none" stroke="#E8EEF6" stroke-opacity=".5" stroke-width="2" marker-end="url(#ar)"/><path d="M452,222 A140,90 0 0 1 188,206" fill="none" stroke="#E8EEF6" stroke-opacity=".5" stroke-width="2" marker-end="url(#ar)"/>`)
      + `<img src="${B}" style="left:303px;top:132px;width:34px">` },
  { t: '5.6 to 6.4 s', h: 'Reform and land', d: 'The spiral closes and locks back into the mark; the b drops and lands right beside it.',
    body: `<img src="${MARK}" style="left:338px;top:118px;width:84px">` + `<img src="${B}" style="left:276px;top:150px;width:40px;transform:scaleY(.9) scaleX(1.06);transform-origin:bottom">`
      + svg(`<line x1="268" y1="214" x2="252" y2="210" stroke="#E8EEF6" stroke-opacity=".5" stroke-width="2"/><line x1="326" y1="214" x2="342" y2="210" stroke="#E8EEF6" stroke-opacity=".5" stroke-width="2"/>`) },
  { t: '6.4 to 7.4 s', h: 'The word stretches out', d: 'b r i g h t d a y slides out from behind the b; the b eases left and the y nudges the mark into its corner.',
    body: `<div style="position:absolute;left:150px;top:135px;width:${374 * 0.6}px;height:95px;overflow:hidden"><img src="${WORD}" style="position:absolute;left:0;top:0;width:374px"></div>`
      + svg(`<line x1="${150 + 374 * 0.6 + 4}" y1="170" x2="${150 + 374 * 0.6 + 40}" y2="170" stroke="#E8EEF6" stroke-opacity=".45" stroke-width="2" marker-end="url(#ar)"/><line x1="${150 + 374 * 0.6 + 4}" y1="196" x2="${150 + 374 * 0.6 + 30}" y2="196" stroke="#E8EEF6" stroke-opacity=".3" stroke-width="2"/>`)
      + `<img src="${MARK}" style="left:${150 + 374 * 0.6 + 54}px;top:104px;width:76px">` },
  { t: '7.4 to 9.0 s', h: 'Final frame', d: 'The finished logo exactly as supplied, a slow light sweep across it, held to the end.',
    body: `<img src="${WORD}" style="left:125.4px;top:135.2px;width:373.8px"><img src="${MARK}" style="left:497.9px;top:94.9px;width:77.8px">`
      + `<div style="position:absolute;inset:0;background:linear-gradient(105deg,transparent 40%,rgba(255,255,255,.10) 50%,transparent 60%)"></div>` },
]

const html = `<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="${UB}"><style>
*{box-sizing:border-box;margin:0;padding:0}
body{width:2720px;background:#0B1626;font-family:'Ubuntu',sans-serif;color:#E8EEF6;padding:40px}
h1{font-weight:700;font-size:40px;margin-bottom:6px}
.sub{font-size:20px;color:#9FB2C8;margin-bottom:30px}
.grid{display:grid;grid-template-columns:repeat(4,640px);gap:28px 26px}
.f{width:640px;height:360px;position:relative;overflow:hidden;border-radius:6px;
   background:radial-gradient(ellipse 70% 75% at 50% 32%,#1E4C7E 0%,#13355A 48%,#081629 100%)}
.f img{position:absolute}
.ov{position:absolute;inset:0;width:640px;height:360px}
.n{position:absolute;left:12px;top:10px;font-weight:700;font-size:18px;color:#fff;opacity:.85}
.cap{margin-top:10px}
.cap .t{font-size:15px;color:#F00870;font-weight:700;letter-spacing:.04em}
.cap .h{font-size:22px;font-weight:700;margin:2px 0 3px}
.cap .d{font-size:16px;color:#B8C6D6;line-height:1.35}
</style></head><body>
<h1>brightday: seven steps (logo animation storyboard)</h1>
<div class="sub">16:9, 1920 x 1080, 24 fps, about 9 s. Navy #13355A throughout, pink #F00870, overlap #980848, white b and wordmark. High-contrast key light, deep shadows, smooth fluid motion.</div>
<div class="grid">${panels.map((p, i) => `<div><div class="f">${p.body}<div class="n">${i + 1}</div></div>
<div class="cap"><div class="t">${p.t}</div><div class="h">${p.h}</div><div class="d">${p.d}</div></div></div>`).join('')}</div>
</body></html>`

const br = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || '/opt/pw-browsers/chromium' })
const pg = await (await br.newContext({ viewport: { width: 2720, height: 1100 } })).newPage()
await pg.setContent(html, { waitUntil: 'networkidle' }).catch(() => {})
await pg.evaluate(async () => { await document.fonts.ready })
await pg.waitForTimeout(300)
await pg.screenshot({ path: `${D}/storyboard.png`, fullPage: true })
await br.close()
console.log('wrote storyboard.png')
