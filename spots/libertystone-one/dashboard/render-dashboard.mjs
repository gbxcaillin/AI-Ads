// Renders the LibertyStone portfolio dashboard to a crisp PNG for compositing
// onto the generated solution-shot laptop plate. Dark navy brand look, one
// balance, a single holdings list that mixes Shares, ETFs and Crypto.
//
// Run:  node spots/libertystone-one/dashboard/render-dashboard.mjs
// Out:  spots/libertystone-one/dashboard/dashboard.png (2560x1600)
import { chromium } from 'playwright-core'
import { readFileSync } from 'node:fs'

const ROOT = 'spots/libertystone-one'
const b64 = (p, mime) => `data:${mime};base64,` + readFileSync(p).toString('base64')
const m500 = b64('.claude/skills/ai-commercial/scripts/fonts/Montserrat-500.ttf', 'font/ttf')
const m600 = b64('.claude/skills/ai-commercial/scripts/fonts/Montserrat-600.ttf', 'font/ttf')
const logo = b64(`${ROOT}/brand/logo-wordmark-trans.png`, 'image/png')

// Single holdings list; values sum to the hero balance 287,340.
const holdings = [
  { name: 'Meridian Group',     type: 'Shares', value: '$84,210', chg: '+0.8%', up: true },
  { name: 'Harbour Industries', type: 'Shares', value: '$61,540', chg: '-0.4%', up: false },
  { name: 'Global 200 ETF',     type: 'ETF',    value: '$72,980', chg: '+0.6%', up: true },
  { name: 'Bitcoin',            type: 'Crypto', value: '$41,160', chg: '+2.3%', up: true },
  { name: 'Ethereum',           type: 'Crypto', value: '$27,450', chg: '+1.1%', up: true },
]
const pill = (t) => {
  const cls = t === 'Crypto' ? 'crypto' : t === 'ETF' ? 'etf' : 'shares'
  return `<span class="pill ${cls}">${t}</span>`
}
const rows = holdings.map(h => `
  <div class="row">
    <div class="rl"><span class="dot ${h.type.toLowerCase()}"></span><span class="nm">${h.name}</span>${pill(h.type)}</div>
    <div class="rr"><span class="val">${h.value}</span><span class="chg ${h.up ? 'up' : 'dn'}">${h.chg}</span></div>
  </div>`).join('')

// A quiet upward sparkline.
const pts = [0,8,5,14,11,20,17,26,24,33,30,41,38,48,52]
const W = 1180, H = 150
const sx = (i) => (i / (pts.length - 1)) * W
const sy = (v) => H - (v / 55) * H
const line = pts.map((v, i) => `${i ? 'L' : 'M'}${sx(i).toFixed(1)},${sy(v).toFixed(1)}`).join(' ')
const area = `${line} L${W},${H} L0,${H} Z`

const html = `<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{font-family:'Montserrat';font-weight:500;src:url(${m500}) format('truetype')}
@font-face{font-family:'Montserrat';font-weight:600;src:url(${m600}) format('truetype')}
*{margin:0;padding:0;box-sizing:border-box;font-family:'Montserrat',sans-serif}
:root{--navy:#0A1224;--panel:#121D30;--line:#1E2A40;--ink:#E8ECF2;--mut:#8A97AD;--teal:#38B2A8;--up:#5FC9A8;--dn:#C98477}
html,body{width:2560px;height:1600px;background:var(--navy);overflow:hidden}
body{background:radial-gradient(130% 120% at 18% 12%, #0E1728 0%, #0A1224 55%, #081020 100%)}
.wrap{padding:96px 120px;height:100%;display:flex;flex-direction:column;color:var(--ink)}
.top{display:flex;align-items:center;justify-content:space-between;margin-bottom:84px}
.brand{height:120px;width:720px;display:flex;align-items:center;overflow:hidden}
.brand img{height:300px;margin:-90px -70px;object-fit:contain}
.who{display:flex;align-items:center;gap:22px;color:var(--mut);font-weight:500;font-size:30px;letter-spacing:.04em}
.who .av{width:58px;height:58px;border-radius:50%;background:linear-gradient(140deg,#1b3a44,#122236);border:1px solid var(--line)}
.lead{color:var(--mut);font-weight:500;font-size:30px;letter-spacing:.26em;text-transform:uppercase;margin-bottom:26px}
.bal{display:flex;align-items:flex-end;gap:40px}
.bal .big{font-weight:600;font-size:170px;line-height:.9;letter-spacing:-.02em}
.bal .delta{font-weight:600;font-size:40px;color:var(--up);padding-bottom:22px}
.spark{margin:60px 0 78px}
.hhead{display:flex;align-items:center;justify-content:space-between;color:var(--mut);font-weight:600;font-size:28px;letter-spacing:.14em;text-transform:uppercase;border-bottom:1px solid var(--line);padding-bottom:30px;margin-bottom:12px}
.row{display:flex;align-items:center;justify-content:space-between;padding:34px 4px;border-bottom:1px solid var(--line)}
.rl{display:flex;align-items:center;gap:30px}
.dot{width:16px;height:16px;border-radius:50%}
.dot.shares{background:#7FA8D0}.dot.etf{background:#B9A4E0}.dot.crypto{background:var(--teal)}
.nm{font-weight:600;font-size:46px;letter-spacing:.005em;min-width:520px}
.pill{font-weight:600;font-size:26px;letter-spacing:.12em;text-transform:uppercase;padding:10px 22px;border-radius:999px}
.pill.shares{background:rgba(127,168,208,.14);color:#AFC6E0}
.pill.etf{background:rgba(185,164,224,.14);color:#CDBCEC}
.pill.crypto{background:rgba(56,178,168,.18);color:#6FD6CC}
.rr{display:flex;align-items:baseline;gap:34px}
.val{font-weight:600;font-size:46px;letter-spacing:.01em}
.chg{font-weight:600;font-size:32px;min-width:140px;text-align:right}
.chg.up{color:var(--up)}.chg.dn{color:var(--dn)}
.foot{margin-top:auto;display:flex;align-items:center;justify-content:space-between;color:var(--mut);font-weight:500;font-size:26px;letter-spacing:.06em}
</style></head><body>
<div class="wrap">
  <div class="top">
    <div class="brand"><img src="${logo}"></div>
    <div class="who"><span>Portfolio</span><span class="av"></span></div>
  </div>
  <div class="lead">Total portfolio value</div>
  <div class="bal"><div class="big">$287,340</div><div class="delta">+$4,812 &nbsp;1.7% today</div></div>
  <div class="spark">
    <svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" preserveAspectRatio="none">
      <defs><linearGradient id="g" x1="0" x2="0" y1="0" y2="1">
        <stop offset="0" stop-color="#38B2A8" stop-opacity="0.28"/>
        <stop offset="1" stop-color="#38B2A8" stop-opacity="0"/></linearGradient></defs>
      <path d="${area}" fill="url(#g)"/>
      <path d="${line}" fill="none" stroke="#38B2A8" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
  </div>
  <div class="hhead"><span>Holdings</span><span>Value</span></div>
  ${rows}
  <div class="foot"><span>Shares &middot; ETFs &middot; Crypto, together</span><span>Updated just now</span></div>
</div>
</body></html>`

const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || '/opt/pw-browsers/chromium' })
const ctx = await browser.newContext({ viewport: { width: 2560, height: 1600 }, deviceScaleFactor: 1 })
const page = await ctx.newPage()
await page.setContent(html, { waitUntil: 'load' })
await page.evaluate(async () => { await document.fonts.ready })
await page.waitForTimeout(200)
await page.screenshot({ path: `${ROOT}/dashboard/dashboard.png`, animations: 'disabled' })
await browser.close()
console.log('wrote dashboard.png 2560x1600')
