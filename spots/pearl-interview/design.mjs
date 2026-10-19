// Pearl founder interview: the designed frames (question cards, name super, end card) at 1920x1080,
// rendered as transparent or full PNGs for the edit, plus a paper-edit storyboard for review.
// Run from the repo root: node spots/pearl-interview/design.mjs
import { chromium } from 'playwright-core'
import { readFileSync, writeFileSync } from 'node:fs'

const D = 'spots/pearl-interview'
const cut = JSON.parse(readFileSync(`${D}/cut.json`, 'utf8'))
const b64 = (p, m) => `data:${m};base64,` + readFileSync(p).toString('base64')
const font = (f) => b64(`${D}/fonts/${f}`, 'font/ttf')
const LOGO_DARK = b64(`${D}/brand/pearl-logo-on-dark.png`, 'image/png')
const AUBERGINE = '#281347', BLUSH = '#D2B8AE'

const css = `
@font-face{font-family:Jost;font-weight:300;src:url(${font('Jost-300.ttf')})}
@font-face{font-family:Jost;font-weight:400;src:url(${font('Jost-400.ttf')})}
@font-face{font-family:Jost;font-weight:500;src:url(${font('Jost-500.ttf')})}
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1920px;height:1080px;background:transparent;font-family:Jost,sans-serif;overflow:hidden}
.bg{position:absolute;inset:0;background:radial-gradient(ellipse 80% 90% at 30% 40%,#3A1E62 0%,${AUBERGINE} 55%,#170A2B 100%)}
.rings{position:absolute;right:-260px;top:50%;transform:translateY(-50%);width:1000px;height:1000px;opacity:.13}
.rings div{position:absolute;left:50%;bottom:0;transform:translateX(-50%);border:34px solid ${BLUSH};border-radius:50%}
.q{position:absolute;left:180px;top:50%;transform:translateY(-50%);width:1250px}
.q .eb{display:flex;align-items:center;gap:22px;color:${BLUSH};font-weight:500;font-size:26px;letter-spacing:.32em;text-transform:uppercase;margin-bottom:38px}
.q .eb i{display:block;width:70px;height:2px;background:${BLUSH}}
.q h1{color:#fff;font-weight:300;font-size:92px;line-height:1.08;letter-spacing:-.01em}
.lt{position:absolute;left:120px;bottom:110px;padding:26px 40px 26px 34px;background:linear-gradient(90deg,rgba(23,10,43,.86),rgba(23,10,43,.55) 70%,rgba(23,10,43,0));border-left:5px solid ${BLUSH}}
.lt .n{color:#fff;font-weight:400;font-size:50px;letter-spacing:.01em}
.lt .r{color:${BLUSH};font-weight:500;font-size:24px;letter-spacing:.28em;text-transform:uppercase;margin-top:6px}
.end{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center}
.end img{width:760px}
.end .url{color:#fff;font-weight:300;font-size:40px;letter-spacing:.12em;margin-top:56px}
.end .line{color:${BLUSH};font-weight:400;font-size:30px;letter-spacing:.02em;margin-top:18px}
.end .ga{position:absolute;bottom:56px;left:0;right:0;text-align:center;color:rgba(255,255,255,.62);font-size:21px;font-weight:300;letter-spacing:.01em}
`
const rings = `<div class="rings"><div style="width:1000px;height:1000px"></div><div style="width:700px;height:700px;bottom:60px"></div><div style="width:400px;height:400px;bottom:120px"></div></div>`
const pages = {}
cut.cards.forEach((c, i) => {
  pages[`card-q${i + 1}`] = `<div class="bg"></div>${rings}<div class="q"><div class="eb"><i></i>${c.eyebrow}</div><h1>${c.question}</h1></div>`
})
pages['name-super'] = `<div class="lt"><div class="n">${cut.name_super.name}</div><div class="r">${cut.name_super.role}</div></div>`
pages['end-card'] = `<div class="bg"></div>${rings}<div class="end"><img src="${LOGO_DARK}"><div class="url">${cut.end_card.url}</div><div class="line">${cut.end_card.line}</div><div class="ga">${cut.end_card.general_advice}</div></div>`

const br = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || '/opt/pw-browsers/chromium' })
const pg = await (await br.newContext({ viewport: { width: 1920, height: 1080 } })).newPage()
for (const [name, body] of Object.entries(pages)) {
  await pg.setContent(`<!doctype html><html><head><meta charset="utf-8"><style>${css}</style></head><body>${body}</body></html>`, { waitUntil: 'load' })
  await pg.evaluate(async () => { await document.fonts.ready })
  await pg.screenshot({ path: `${D}/cards/${name}.png`, omitBackground: true })
}

// paper edit: one row of frames with the cut list under each
const ref = b64(`${D}/cards/ref-andrew-cam1.png`, 'image/png')
const img = (n) => b64(`${D}/cards/${n}.png`, 'image/png')
const tiles = []
let t = 0
for (const seg of cut.timeline) {
  const d = seg.kind === 'answer' ? seg.parts.reduce((s, p) => s + (p[1] - p[0]), 0) : seg.dur
  let pic
  if (seg.kind === 'card') pic = `<img src="${img(seg.card)}">`
  else if (seg.kind === 'end') pic = `<img src="${img('end-card')}">`
  else pic = `<img src="${ref}" style="${seg.framing === 'punch-in' ? 'transform:scale(1.18);transform-origin:50% 38%' : ''}">${seg.name_super ? `<img src="${img('name-super')}">` : ''}${seg.broll ? `<div class="br">Optional OpenArt cutaway: ${seg.broll}</div>` : ''}`
  tiles.push(`<div class="tile"><div class="fr">${pic}</div><div class="tc">${t.toFixed(1)} to ${(t + d).toFixed(1)} s</div><div class="tt">${seg.label}</div>${seg.kind === 'answer' ? `<div class="say">"${seg.says}"</div><div class="src">${seg.parts.map(p => `${p[0].toFixed(2)} to ${p[1].toFixed(2)}`).join(' + ')} (switched edit time) &middot; ${seg.framing}</div>` : ''}</div>`)
  t += d
}
const sb = `<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{font-family:Jost;font-weight:300;src:url(${font('Jost-300.ttf')})}
@font-face{font-family:Jost;font-weight:400;src:url(${font('Jost-400.ttf')})}
@font-face{font-family:Jost;font-weight:500;src:url(${font('Jost-500.ttf')})}
*{margin:0;padding:0;box-sizing:border-box}
body{width:2400px;background:#F7F3F1;font-family:Jost,sans-serif;color:${AUBERGINE};padding:44px}
h1{font-weight:300;font-size:52px}.sub{font-size:20px;color:#6A5A78;margin:6px 0 30px}
.row{display:grid;grid-template-columns:repeat(4,560px);gap:30px 26px}
.fr{width:560px;height:315px;position:relative;overflow:hidden;border-radius:10px;background:#111}
.fr img{position:absolute;inset:0;width:560px;height:315px;object-fit:cover}
.br{position:absolute;right:10px;top:10px;background:${BLUSH};color:${AUBERGINE};font-size:14px;padding:4px 10px;border-radius:99px;max-width:330px}
.tc{font-size:15px;font-weight:500;letter-spacing:.08em;color:#8E6F86;margin-top:10px}
.tt{font-size:24px;font-weight:400;margin-top:2px}
.say{font-size:17px;line-height:1.4;margin-top:4px}
.src{font-size:13px;color:#7A6E86;margin-top:4px}
</style></head><body><h1>Pearl: founder interview, paper edit</h1>
<div class="sub">${t.toFixed(1)} s, 1920x1080, for the Pearl website. Questions on screen, then Andrew. Picture is a CAM1 reference frame until the footage is pulled.</div>
<div class="row">${tiles.join('')}</div></body></html>`
await pg.setViewportSize({ width: 2400, height: 900 })
await pg.setContent(sb, { waitUntil: 'load' })
await pg.evaluate(async () => { await document.fonts.ready })
await pg.screenshot({ path: `${D}/paper-edit.png`, fullPage: true })
await br.close()
console.log('cards and paper-edit.png written, running time', t.toFixed(2))
