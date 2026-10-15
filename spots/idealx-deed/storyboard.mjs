// Storyboard for IDEALX "The Reading of the Deed" (30 s hero).
// Eight 16:9 frames. Live-action shots are drawn as simple animatic sketches;
// the designed frames (the rule super, the Portal insert, the end card) use the
// real IDEALX type, colours and lockup so they read as they will on screen.
// Run from the repo root: node spots/idealx-deed/storyboard.mjs
import { chromium } from 'playwright-core'
import { readFileSync } from 'node:fs'

const D = 'spots/idealx-deed'
const font = (f) => 'data:font/ttf;base64,' + readFileSync(`${D}/fonts/${f}`).toString('base64')
const LOCKUP_DARK = readFileSync('spots/idealx-smsf/brand/idealx-lockup-on-dark.svg', 'utf8')
  .replace('<svg ', '<svg class="lock" ')

const INK = '#0D0D0F', INDIGO = '#5158F6', CLOUD = '#F0F0F0', SLATE = '#5B5B63'

// ---------- sketch helpers (640 x 360 panels) ----------
const svg = (inner, bg = '') => `<svg class="ov" viewBox="0 0 640 360">${bg}${inner}</svg>`
const defs = `<defs>
<radialGradient id="lamp" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#FFD9A0" stop-opacity=".55"/><stop offset="1" stop-color="#FFD9A0" stop-opacity="0"/></radialGradient>
<linearGradient id="wall" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2A1C14"/><stop offset="1" stop-color="#4A3122"/></linearGradient>
<linearGradient id="day" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#EDEBE6"/><stop offset="1" stop-color="#D9D4CB"/></linearGradient>
<linearGradient id="paper" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#E9DDBF"/><stop offset="1" stop-color="#CBB98F"/></linearGradient>
<marker id="ar" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#fff" opacity=".85"/></marker>
</defs>`

// a person: head, hair, shoulders. facing: 'front' | 'back' | 'left' | 'right'
function person(x, y, s, o = {}) {
  const { skin = '#C99A7A', hair = '#3A2A20', top = '#3C4048', facing = 'front', glasses = false, hairStyle = 'short' } = o
  const hw = 15 * s, sw = 52 * s, sh = 70 * s
  let g = `<path d="M${x - sw},${y + sh} C${x - sw},${y + 22 * s} ${x - sw * .7},${y + 14 * s} ${x},${y + 14 * s} C${x + sw * .7},${y + 14 * s} ${x + sw},${y + 22 * s} ${x + sw},${y + sh} Z" fill="${top}"/>`
  g += `<rect x="${x - 6 * s}" y="${y + 2 * s}" width="${12 * s}" height="${14 * s}" fill="${skin}"/>`
  const hx = facing === 'left' ? x - 3 * s : facing === 'right' ? x + 3 * s : x
  g += `<ellipse cx="${hx}" cy="${y - 12 * s}" rx="${hw}" ry="${19 * s}" fill="${facing === 'back' ? hair : skin}"/>`
  if (facing !== 'back') {
    if (hairStyle === 'long') g += `<path d="M${hx - hw - 2 * s},${y - 8 * s} C${hx - hw - 4 * s},${y - 36 * s} ${hx + hw + 4 * s},${y - 36 * s} ${hx + hw + 2 * s},${y - 8 * s} L${hx + hw + 4 * s},${y + 14 * s} L${hx + hw - 3 * s},${y + 14 * s} L${hx + hw - 2 * s},${y - 16 * s} C${hx + 6 * s},${y - 24 * s} ${hx - 6 * s},${y - 24 * s} ${hx - hw + 2 * s},${y - 16 * s} L${hx - hw + 3 * s},${y + 14 * s} L${hx - hw - 4 * s},${y + 14 * s} Z" fill="${hair}"/>`
    else if (hairStyle === 'bald') g += `<path d="M${hx - hw},${y - 10 * s} C${hx - hw},${y - 20 * s} ${hx - hw + 4 * s},${y - 22 * s} ${hx - hw + 5 * s},${y - 18 * s} Z M${hx + hw},${y - 10 * s} C${hx + hw},${y - 20 * s} ${hx + hw - 4 * s},${y - 22 * s} ${hx + hw - 5 * s},${y - 18 * s} Z" fill="${hair}"/>`
    else g += `<path d="M${hx - hw - 1 * s},${y - 10 * s} C${hx - hw - 2 * s},${y - 38 * s} ${hx + hw + 2 * s},${y - 38 * s} ${hx + hw + 1 * s},${y - 10 * s} C${hx + 6 * s},${y - 24 * s} ${hx - 6 * s},${y - 24 * s} ${hx - hw - 1 * s},${y - 10 * s} Z" fill="${hair}"/>`
    if (facing === 'front') {
      g += `<circle cx="${hx - 5.5 * s}" cy="${y - 12 * s}" r="${1.6 * s}" fill="#222"/><circle cx="${hx + 5.5 * s}" cy="${y - 12 * s}" r="${1.6 * s}" fill="#222"/>`
      if (glasses) g += `<path d="M${hx - 11 * s},${y - 11 * s} h${9 * s} M${hx + 2 * s},${y - 11 * s} h${9 * s}" stroke="#111" stroke-width="${1.6 * s}"/><path d="M${hx - 2 * s},${y - 11 * s} h${4 * s}" stroke="#111" stroke-width="${1 * s}"/>`
    }
  }
  return g
}
const rain = (x, y, w, h) => `<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="#1B2A36"/>` +
  [...Array(26)].map((_, i) => { const rx = x + ((i * 37) % w), ry = y + ((i * 53) % (h - 20)); return `<line x1="${rx}" y1="${ry}" x2="${rx - 4}" y2="${ry + 16}" stroke="#9FB6C8" stroke-opacity=".45" stroke-width="1"/>` }).join('') +
  `<path d="M${x + w / 2},${y} v${h} M${x},${y + h / 2} h${w}" stroke="#2A1C14" stroke-width="5"/><rect x="${x}" y="${y}" width="${w}" height="${h}" fill="none" stroke="#2A1C14" stroke-width="7"/>`
const panels = (x0, x1, y1) => [...Array(Math.floor((x1 - x0) / 46))].map((_, i) => `<rect x="${x0 + i * 46 + 4}" y="14" width="38" height="${y1 - 28}" rx="2" fill="none" stroke="#5A3D2A" stroke-opacity=".7" stroke-width="2"/>`).join('')
const lamp = (x, y, s = 1) => `<circle cx="${x}" cy="${y}" r="${130 * s}" fill="url(#lamp)"/><rect x="${x - 2 * s}" y="${y}" width="${4 * s}" height="${30 * s}" fill="#B08A3E"/><path d="M${x - 26 * s},${y + 4 * s} L${x - 18 * s},${y - 12 * s} L${x + 18 * s},${y - 12 * s} L${x + 26 * s},${y + 4 * s} Z" fill="#1E5A3A"/><ellipse cx="${x}" cy="${y + 31 * s}" rx="${14 * s}" ry="${3 * s}" fill="#8A6A2E"/>`
const deed = (x, y, w, h, rot = 0) => `<g transform="rotate(${rot} ${x + w / 2} ${y + h / 2})"><rect x="${x}" y="${y}" width="${w}" height="${h}" rx="2" fill="url(#paper)" stroke="#8C7A55"/><rect x="${x + 3}" y="${y + 3}" width="${w}" height="${h}" rx="2" fill="none" stroke="#B9A57A" stroke-opacity=".7"/><path d="M${x + w * .2},${y} v${h}" stroke="#8E1E2A" stroke-width="4"/></g>`
const office = (deskY = 232) => `<rect width="640" height="360" fill="url(#wall)"/>${panels(150, 640, deskY)}${rain(26, 40, 104, 150)}`
const tag = (t) => `<div class="tag">${t}</div>`
const super1 = `<div class="super"><div class="eb"><span class="code">RULE 01</span><span class="rule"></span><span class="lab">TRUSTEE RULE</span></div><div class="hl">Your deed has to <span class="acc">allow</span> it.</div></div>`

const P = []
// 1. the reading
P.push({ t: '0.0 to 4.5 s', h: 'The reading', src: 'Generated, dialogue',
  pic: 'Wide, slow push-in. A wood-panelled office at dusk, rain on the window, one green banker\'s lamp. The lawyer, late 50s, deadpan, unties the red ribbon on a thick yellowed document. The trustee couple, mid 40s, sit shoulder to shoulder, backs to camera, as solemn as a will reading.',
  line: 'LAWYER: "The trust deed. Nineteen ninety-eight."', sound: 'Rain, a slow clock tick, one low cello note.',
  body: svg(defs + office() + lamp(470, 168) + person(320, 128, 1.15, { glasses: true, hairStyle: 'bald', hair: '#9A9A9A', top: '#2B2F38' }) +
    `<rect x="120" y="232" width="400" height="128" fill="#3A2416"/><rect x="120" y="228" width="400" height="8" fill="#5B3A24"/>` + deed(285, 214, 70, 20, -2) +
    person(272, 330, 1.25, { facing: 'back', hair: '#4A3426', top: '#596273' }) + person(372, 334, 1.25, { facing: 'back', hair: '#1F1A17', top: '#7A5B4F' })) })
// 2. shares, property and cash
P.push({ t: '4.5 to 9.5 s', h: 'Shares, property and cash', src: 'Generated, dialogue',
  pic: 'Medium close-up, lawyer centred, lamp-lit from the right. He reads from the deed held low; the page faces him, so no text is ever seen. A long pause before each item.',
  line: 'LAWYER: "The trustees may invest in shares ... property ... and cash."', sound: 'Clock tick in each pause.',
  body: svg(defs + office(360) + lamp(560, 120, 1.2) + person(320, 150, 2.6, { glasses: true, hairStyle: 'bald', hair: '#9A9A9A', top: '#2B2F38' }) +
    `<g transform="rotate(-8 320 330)"><rect x="232" y="288" width="176" height="90" fill="#CBB98F" stroke="#8C7A55"/><path d="M262,288 v90" stroke="#8E1E2A" stroke-width="5"/></g>`) })
// 3. and the crypto?
P.push({ t: '9.5 to 12.0 s', h: '"And the crypto?"', src: 'Generated, dialogue',
  pic: 'Two-shot of the trustees, close together in the centre third. He glances at her; she leans in, polite, hopeful.',
  line: 'TRUSTEE (her): "And the crypto?"', sound: 'The clock stops ticking.',
  body: svg(defs + office(360) + person(275, 170, 2.1, { facing: 'right', hair: '#4A3426', top: '#596273' }) + person(372, 160, 2.2, { facing: 'left', hairStyle: 'long', hair: '#1F1A17', skin: '#B88466', top: '#7A5B4F' })) })
// 4. the page turn
P.push({ t: '12.0 to 14.5 s', h: 'The page turn', src: 'Generated',
  pic: 'Close on the lawyer\'s hands and face. He turns the page. Nothing. He turns it back. Nothing. He does not blink.',
  line: '(no dialogue)', sound: 'Two crisp page turns; rain gusts once.',
  body: svg(defs + office(360) + lamp(560, 110, 1.1) + person(320, 120, 2.2, { glasses: true, hairStyle: 'bald', hair: '#9A9A9A', top: '#2B2F38' }) +
    `<rect x="200" y="250" width="240" height="110" fill="#CBB98F" stroke="#8C7A55"/><path d="M320,250 C360,215 410,205 445,222 L445,330 C410,316 360,322 320,360 Z" fill="#E9DDBF" stroke="#8C7A55"/>` +
    `<path d="M455,210 C500,200 520,240 500,268" fill="none" stroke="#fff" stroke-width="2" stroke-dasharray="4 5" marker-end="url(#ar)"/><path d="M190,220 C150,210 135,250 158,276" fill="none" stroke="#fff" stroke-width="2" stroke-dasharray="4 5" marker-end="url(#ar)"/>`) })
// 5. holds it to the light + super
P.push({ t: '14.5 to 17.0 s', h: 'Up to the light', src: 'Generated + designed super',
  pic: 'He lifts the page up to the lamp and squints through it, as if the crypto might be in the watermark. Hold on the deadpan. The rule super eases up, lower left, no gag moving under it.',
  line: '(no dialogue)', super: 'RULE 01 / TRUSTEE RULE. Your deed has to allow it.', sound: 'Low cello resolves; silence under the super.',
  body: svg(defs + office(360) + lamp(470, 92, 1.3) + `<rect x="352" y="40" width="130" height="160" fill="#FFF2D4" fill-opacity=".85" stroke="#8C7A55"/><rect x="352" y="40" width="130" height="160" fill="url(#lamp)"/>` +
    person(268, 150, 2.2, { facing: 'right', glasses: true, hairStyle: 'bald', hair: '#9A9A9A', top: '#2B2F38' })) + super1 })
// 6. updated deed
P.push({ t: '17.0 to 21.0 s', h: 'Updated', src: 'Generated, picture only',
  pic: 'Hard cut to daylight. The same couple at a bright kitchen table. A slim new deed with a paper clip is set down beside a laptop; she opens the laptop. The lid is plain and matte; the screen faces them.',
  line: 'VO: "When your deed covers it, IDEALX keeps shares, ETFs and digital assets side by side."', sound: 'Room tone, a bird outside, a light piano note.',
  body: svg(defs + `<rect width="640" height="360" fill="url(#day)"/><rect x="430" y="30" width="170" height="170" fill="#FFFFFF"/><path d="M515,30 v170 M430,115 h170" stroke="#D9D4CB" stroke-width="5"/>` +
    person(262, 170, 1.7, { facing: 'right', hair: '#4A3426', top: '#8FA3B8' }) + person(372, 166, 1.75, { facing: 'left', hairStyle: 'long', hair: '#1F1A17', skin: '#B88466', top: '#C9B8A6' }) +
    `<rect x="0" y="262" width="640" height="98" fill="#B9AA96"/><rect x="0" y="258" width="640" height="8" fill="#CDBFAC"/>` +
    `<path d="M300,262 L292,212 L382,212 L374,262 Z" fill="#7C8088"/><rect x="290" y="260" width="96" height="6" fill="#5F636B"/>` + `<rect x="168" y="242" width="72" height="22" fill="#FFFFFF" stroke="#BDBDBD"/><path d="M178,240 v8" stroke="${INDIGO}" stroke-width="3"/>`) })
// 7. Portal insert (designed)
P.push({ t: '21.0 to 24.0 s', h: 'Side by side', src: 'Designed Portal screen (IDEALX to supply real screens)',
  pic: 'Over her shoulder into the screen, slow push-in. The IDEALX Portal: the fund\'s holdings side by side. No prices, returns or charts.',
  line: 'VO continues under it, then a beat.', sound: 'One soft click.',
  body: `<div class="portal"><div class="pt"><span class="pmark">${LOCKUP_DARK.replace('class="lock"', 'class="plock"').replace(/#FFFFFF/g, INK)}</span><span class="pfund">Henderson Family Super Fund</span></div>
  <div class="peb"><span class="code">SMSF</span><span class="rule"></span><span class="lab">FIRST</span></div>
  <div class="ph">Everything the fund holds, side by <span class="acc">side</span>.</div>
  <div class="cards"><div class="card"><div class="ct">Shares</div><div class="cs">ASX and international</div></div><div class="card"><div class="ct">ETFs</div><div class="cs">The large issuers</div></div><div class="card sel"><div class="ct">Digital assets</div><div class="cs">A wallet that belongs to the fund</div></div></div></div>` })
// 8. end card
P.push({ t: '24.0 to 30.0 s', h: 'End card', src: 'Designed, real lockup',
  pic: 'Ink card. Lockup, then the line, then the risk super, all held together for at least 5 s with nothing moving but a slow push-in.',
  line: 'VO: "Digital assets are high risk. General information only. Consider your fund\'s deed and strategy."', super: 'Read the deed first. + risk super + licence line.', sound: 'Cello and piano resolve; clean tail.',
  body: `<div class="end">${LOCKUP_DARK}<div class="eh">Read the <span class="acc">deed</span> first.</div>
  <div class="risk">Digital assets are high risk and you could lose all of your investment. General information only, not advice. Consider your circumstances and your fund's deed and strategy.</div>
  <div class="lic">IDEALX is a brand of Idealx Platform Pty Ltd (ABN 83 694 912 126), a Corporate Authorised Representative of Idealx Securities Limited (AFSL 531729). Digital asset services by Idealx Digital Assets Pty Ltd, registered with AUSTRAC.</div></div>` })

const html = `<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{font-family:Inter;font-weight:300;src:url(${font('Inter-300.ttf')})}
@font-face{font-family:Inter;font-weight:400;src:url(${font('Inter-400.ttf')})}
@font-face{font-family:Inter;font-weight:500;src:url(${font('Inter-500.ttf')})}
@font-face{font-family:Inter;font-weight:600;src:url(${font('Inter-600.ttf')})}
@font-face{font-family:'Instrument Serif';font-weight:400;src:url(${font('InstrumentSerif-400.ttf')})}
*{box-sizing:border-box;margin:0;padding:0}
body{width:2800px;background:#FFFFFF;font-family:Inter,sans-serif;color:${INK};padding:48px 48px 40px}
.top{display:flex;justify-content:space-between;align-items:flex-end;border-bottom:1px solid #0D0D0F1A;padding-bottom:22px;margin-bottom:30px}
.top .eb{display:flex;align-items:center;gap:12px;font-size:15px;font-weight:500;letter-spacing:.14em;margin-bottom:12px}
.code{color:${INDIGO};font-variant-numeric:tabular-nums}
.rule{display:inline-block;width:40px;height:1px;background:${INDIGO};opacity:.55}
.lab{color:${SLATE}}
h1{font-weight:300;font-size:56px;letter-spacing:-.03em;line-height:1.04}
.acc{font-family:'Instrument Serif',serif;font-size:1.06em;text-decoration:underline;text-decoration-color:${INDIGO};text-decoration-thickness:.09em;text-underline-offset:.14em}
.meta{font-size:17px;color:${SLATE};text-align:right;line-height:1.55}
.meta b{color:${INK};font-weight:500}
.grid{display:grid;grid-template-columns:repeat(4,640px);gap:34px 32px}
.f{width:640px;height:360px;position:relative;overflow:hidden;border-radius:14px;background:#222}
.ov{position:absolute;inset:0;width:640px;height:360px}
.n{position:absolute;left:12px;top:10px;font-weight:600;font-size:16px;color:#fff;background:#0D0D0F99;border-radius:6px;padding:2px 8px}
.tag{display:inline-block;font-size:12px;font-weight:500;letter-spacing:.08em;text-transform:uppercase;color:${INDIGO};background:#EEEFFE;border-radius:999px;padding:3px 10px;margin:12px 0 6px}
.cap .t{font-size:14px;color:${SLATE};font-weight:500;letter-spacing:.06em;font-variant-numeric:tabular-nums}
.cap .h{font-size:24px;font-weight:400;letter-spacing:-.01em;margin:2px 0 4px}
.cap p{font-size:15.5px;line-height:1.45;color:#2A2A30;margin-top:4px}
.cap p.l{color:${INK};font-weight:500}
.cap p.s{color:${SLATE}}
/* rule super over footage */
.super{position:absolute;left:34px;bottom:30px;color:#fff;text-shadow:0 1px 12px rgba(0,0,0,.45)}
.super .eb{display:flex;align-items:center;gap:8px;font-size:10px;font-weight:500;letter-spacing:.14em;margin-bottom:8px}
.super .code{color:#8B90F9}.super .rule{background:#8B90F9;width:28px}.super .lab{color:#E7E7EA}
.super .hl{font-weight:300;font-size:30px;letter-spacing:-.03em;line-height:1.04}
/* portal */
.portal{position:absolute;inset:0;background:#FFFFFF;padding:22px 26px}
.pt{display:flex;align-items:center;justify-content:space-between;padding-left:34px;border-bottom:1px solid #0D0D0F1A;padding-bottom:12px;margin-bottom:16px}
.plock{height:15px;width:auto}
.pfund{font-size:12px;color:${SLATE}}
.peb{display:flex;align-items:center;gap:8px;font-size:9.5px;font-weight:500;letter-spacing:.14em;margin-bottom:8px}
.ph{font-weight:300;font-size:30px;letter-spacing:-.03em;line-height:1.04;margin-bottom:22px}
.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
.card{background:${CLOUD};border-radius:16px;padding:16px 14px;height:118px;display:flex;flex-direction:column;justify-content:space-between;border:1px solid transparent}
.card.sel{background:#EEEFFE;border-color:${INDIGO}}
.ct{font-size:17px;font-weight:400}.cs{font-size:11.5px;color:${SLATE};line-height:1.35}
/* end card */
.end{position:absolute;inset:0;background:linear-gradient(#16161A,#0D0D0F);border-top:3px solid ${INDIGO};padding:34px 40px;color:#fff}
.end .lock{height:26px;width:auto;display:block;margin-bottom:40px}
.eh{font-weight:300;font-size:46px;letter-spacing:-.03em;line-height:1.04;margin-bottom:26px}
.risk{font-size:13px;line-height:1.45;color:#FFFFFF;max-width:520px;margin-bottom:12px}
.lic{font-size:9px;line-height:1.45;color:#A3A3AA;max-width:540px}
.notes{margin-top:40px;display:grid;grid-template-columns:repeat(4,1fr);gap:32px;border-top:1px solid #0D0D0F1A;padding-top:26px}
.notes h3{font-size:13px;font-weight:500;letter-spacing:.14em;color:${SLATE};text-transform:uppercase;margin-bottom:10px}
.notes p{font-size:15.5px;line-height:1.5;color:#2A2A30;margin-bottom:6px}
</style></head><body>
<div class="top"><div><div class="eb"><span class="code">CONCEPT 01</span><span class="rule"></span><span class="lab">STORYBOARD FOR REVIEW</span></div>
<h1>The Reading of the <span class="acc">Deed</span></h1></div>
<div class="meta"><b>IDEALX, SMSF campaign</b><br>30 s hero, 16:9 master composed for a 9:16 crop<br>Meta and TikTok; YouTube version swaps "crypto" for "ETFs"<br>Words: about 50 including the risk line</div></div>
<div class="grid">${P.map((p, i) => `<div><div class="f">${p.body}<div class="n">${i + 1}</div></div>
<div class="cap">${tag(p.src)}<div class="t">${p.t}</div><div class="h">${p.h}</div><p>${p.pic}</p><p class="l">${p.line}</p>${p.super ? `<p class="l">SUPER: ${p.super}</p>` : ''}<p class="s">SOUND: ${p.sound}</p></div></div>`).join('')}</div>
<div class="notes">
<div><h3>Cast</h3><p>Lawyer: late 50s, dignified, deadpan; the deed is the joke, never him.</p><p>Trustees: a couple in their mid 40s, smart casual; curious, not foolish. Nobody looks at the camera.</p></div>
<div><h3>Voices</h3><p>Dialogue is generated with the shot so lips match; each speaker's voice is locked with a short reference so it holds across shots.</p><p>Narrator: calm, warm Australian, unhurried; one take for the payoff and the risk line.</p></div>
<div><h3>Look</h3><p>Office: tungsten lamp, rain-blue window, deep shadows, slight grain. Payoff: soft daylight, clean and airy.</p><p>No readable text in any generated frame; the deed's page always faces away. All lettering is designed.</p></div>
<div><h3>Compliance</h3><p>The joke is the 1998 document, not crypto. No prices, returns or charts. Nobody is told to start an SMSF.</p><p>Risk super spoken and held at least 5 s with no gag. Legal to confirm "your deed has to allow it" reads as information.</p></div>
</div>
</body></html>`

const br = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || '/opt/pw-browsers/chromium' })
const pg = await (await br.newContext({ viewport: { width: 2800, height: 1200 } })).newPage()
await pg.setContent(html, { waitUntil: 'load' })
await pg.evaluate(async () => { await document.fonts.ready })
await pg.waitForTimeout(200)
await pg.screenshot({ path: `${D}/storyboard.png`, fullPage: true })
await br.close()
console.log('wrote storyboard.png')
