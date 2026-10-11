// Script and timing sheet for the LibertyStone SMSF spot (review v3.3), as a PDF.
// Timings are the cut's actual values from build_review_cut.py.
// Run from the repo root:  node spots/libertystone-one/make_script_pdf.mjs
import { chromium } from 'playwright-core'
import { readFileSync } from 'node:fs'

const ROOT = 'spots/libertystone-one'
const b64 = (p, mime) => `data:${mime};base64,` + readFileSync(p).toString('base64')
const m500 = b64('.claude/skills/ai-commercial/scripts/fonts/Montserrat-500.ttf', 'font/ttf')
const m600 = b64('.claude/skills/ai-commercial/scripts/fonts/Montserrat-600.ttf', 'font/ttf')
const logo = b64(`${ROOT}/brand/logo-wordmark-trans.png`, 'image/png')

const shots = [
  ['0.0 - 4.0', 'Order', 'Composed woman, late 50s, at her home study desk at dusk. Warm lamp, city skyline. Slow push-in.',
   'You set up your own super fund to take control.', 'Music bed fades in.'],
  ['4.0 - 8.4', 'Overload builds', 'The desk fills around her: a second laptop, a phone lighting up, folders, statements. Slow orbit.',
   'But now it\'s spread everywhere. Shares here. Crypto there.', 'Soft notification pings begin.'],
  ['8.4 - 13.0', 'Overload peak', 'Piled desk, two laptops, towers of paperwork. Hand to her temple. Screens turned away, no readable text.',
   'A login for each. Statements for the auditor.', 'Pings come closer together.'],
  ['13.0 - 16.4', 'Friction', 'Cold, fast inserts: thumb on a phone, typing, a login field, pen on paper, a loading spinner.',
   '(no voice)', 'Key clicks accelerate.'],
  ['16.4 - 20.6', 'THE SIGH', 'Tight on her face in cold screen light. She breathes in, closes her eyes and lets out one long, audible sigh. Hold. Fade to black.',
   '(no voice: her sigh only)', 'Clicks cut dead at 16.4. Music ducked almost to silence. In-breath 16.6, sigh 19.0 to 19.8.'],
  ['20.6 - 20.9', 'Reset', 'Black.', 'LibertyStone is the investment platform built for self-managed super funds. (20.75 to 25.9)', 'Music returns.'],
  ['20.9 - 27.8', 'One place', 'Her relief: eyes open into a settled, closed-mouth smile behind one clean laptop. Slow push-in until the dashboard owns the frame and she drifts out (about 26.0). Dashboard: SMSF portfolio, total fund value $287,340, one holdings list of Shares, ETF and Crypto.',
   '(line continues)  Shares, ETFs and crypto. (26.3 to 29.1)', ''],
  ['27.2 - 33.5', 'End card', 'Dissolve (27.2 to 27.8) to the LibertyStone logo animation, held. Caption and risk line fade in at 29.5.',
   'Your whole S M (0.1 s) S F, in one place. (29.5 to 32.8)', 'Soft chime as the mark lands (28.4). Music fades out over the last 2.2 s.'],
]

const vo = [
  ['0.6 - 3.4', 'You set up your own super fund to take control.'],
  ['4.3 - 13.6', 'But now it\'s spread everywhere. Shares here. Crypto there. A login for each. Statements for the auditor.'],
  ['13.6 - 20.75', '(silence for the friction and the sigh)'],
  ['20.75 - 25.9', 'LibertyStone is the investment platform built for self-managed super funds.'],
  ['26.3 - 29.1', 'Shares, ETFs and crypto.'],
  ['29.5 - 32.8', 'Your whole SMSF, in one place.'],
]

const row = (s) => `<tr><td class="t">${s[0]}</td><td class="n">${s[1]}</td><td>${s[2]}</td><td class="v">${s[3]}</td><td class="s">${s[4]}</td></tr>`
const html = `<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{font-family:'Montserrat';font-weight:500;src:url(${m500}) format('truetype')}
@font-face{font-family:'Montserrat';font-weight:600;src:url(${m600}) format('truetype')}
@page{size:A4 landscape;margin:14mm 14mm 14mm 14mm}
*{box-sizing:border-box;font-family:'Montserrat',sans-serif}
body{margin:0;color:#1B2433;font-size:8.8pt;line-height:1.38}
.head{background:#0A1224;color:#E8ECF2;padding:12px 22px;border-radius:6px;display:flex;align-items:center;justify-content:space-between}
.brand{height:46px;width:300px;overflow:hidden;display:flex;align-items:center}
.brand img{height:115px;margin:-34px -27px}
.head .meta{text-align:right;font-size:8.6pt;color:#B4C0D2;line-height:1.55}
.head .meta b{color:#E8ECF2;font-weight:600}
h1{font-weight:600;font-size:15pt;margin:12px 0 2px;color:#0A1224}
.sub{color:#5A6880;margin-bottom:10px}
h2{font-weight:600;font-size:10.5pt;letter-spacing:.12em;text-transform:uppercase;color:#2A8F87;margin:12px 0 5px}
table{width:100%;border-collapse:collapse}
th{font-weight:600;text-align:left;font-size:7.8pt;letter-spacing:.1em;text-transform:uppercase;color:#5A6880;border-bottom:1.5px solid #0A1224;padding:5px 7px}
td{vertical-align:top;padding:4.5px 7px;border-bottom:1px solid #DDE3EC}
td.t{white-space:nowrap;font-weight:600;color:#0A1224;width:74px}
td.n{font-weight:600;width:92px}
td.v{font-style:italic;color:#0A1224;width:30%}
td.s{color:#4A5870;width:20%}
tr.sigh td{background:#EEF6F5}
.vo td.t{width:90px}
.vo td{font-size:10pt}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}
.box{border:1px solid #DDE3EC;border-radius:6px;padding:10px 12px}
.box p{margin:0 0 5px}
.k{font-weight:600;color:#0A1224}
.risk{font-size:8.4pt;color:#4A5870}
.foot{margin-top:12px;font-size:7.6pt;color:#8A97AD}
.pb{page-break-before:always}
</style></head><body>
<div class="head"><div class="brand"><img src="${logo}"></div><div class="meta"><b>LibertyStone, SMSF commercial</b><br>Script and timing, review cut v3.3<br>11 October 2026 &middot; Status: parked</div></div>
<h1>Your whole SMSF, in one place.</h1>
<div class="sub">33.5 s &middot; 16:9, 1280 x 720, 24 fps (480p drafts, 1080p on approval) &middot; loudness -14.2 LUFS, -1.4 dBTP &middot; cloned Australian male narrator</div>

<h2>Shot by shot</h2>
<table><tr><th>Time (s)</th><th>Shot</th><th>Picture</th><th>Voice</th><th>Sound</th></tr>
${shots.map((s, i) => i === 4 ? row(s).replace('<tr>', '<tr class="sigh">') : row(s)).join('')}
</table>

<div class="pb"></div>
<h2>Voice-over, as recorded</h2>
<table class="vo"><tr><th>Time (s)</th><th>Line</th></tr>
${vo.map(v => `<tr><td class="t">${v[0]}</td><td>${v[1]}</td></tr>`).join('')}
</table>

<div class="grid" style="margin-top:14px">
<div class="box">
<p class="k">Delivery notes</p>
<p>Calm, warm, unhurried Australian male voice; premium and quiet, never salesy.</p>
<p>SMSF is said as letters in two pairs with a very short gap: "S M" (0.1 s) "S F".</p>
<p>The narrator is silent from the auditor line to the reset, so the sigh stands alone.</p>
<p>"Built for" self-managed super funds (chosen over "perfect for" for compliance).</p>
</div>
<div class="box">
<p class="k">On screen</p>
<p>Dashboard (20.9 to 27.8): header "SMSF portfolio"; "Total fund value" $287,340; holdings Meridian Group (Shares), Harbour Industries (Shares), Global 200 ETF (ETF), Bitcoin (Crypto), Ethereum (Crypto). Placeholder names.</p>
<p>End card (from 29.5): caption "Your whole SMSF, in one place."</p>
<p class="risk">Risk line: General information only. It does not consider your objectives, financial situation or needs. Investing and crypto assets carry risk, including loss of capital.</p>
</div>
</div>

<h2>Open before release</h2>
<table><tr><th>Item</th><th>Owner</th></tr>
<tr><td>AFSL number for the end card</td><td>Client</td></tr>
<tr><td>Compliance sign-off on the risk line, including any SMSF, PDS or Target Market Determination wording</td><td>Client compliance</td></tr>
<tr><td>1080p upgrade of the approved draft shots</td><td>Production, on approval</td></tr>
<tr><td>Optional strict 30 s version (tighten overload pauses and end-card hold)</td><td>Production, if needed</td></tr>
</table>
<div class="foot">Source of truth: spots/libertystone-one/spot.json. Cut built by build_review_cut.py. Dashboard is a designed mockup composited in post, not generated.</div>
</body></html>`

const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || '/opt/pw-browsers/chromium' })
const page = await (await browser.newContext()).newPage()
await page.setContent(html, { waitUntil: 'load' })
await page.evaluate(async () => { await document.fonts.ready })
await page.pdf({ path: `${ROOT}/LibertyStone-SMSF-script-and-timing.pdf`, format: 'A4', landscape: true, printBackground: true })
await browser.close()
console.log('wrote LibertyStone-SMSF-script-and-timing.pdf')
