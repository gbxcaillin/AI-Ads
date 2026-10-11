// Renders the end-card text (USP tagline + Australian risk line) as a
// transparent 1280x720 overlay to composite over the supplied logo animation.
// drawtext is not in this ffmpeg build, so text is rendered in the browser.
import { chromium } from 'playwright-core'
import { readFileSync } from 'node:fs'
const ROOT = 'spots/libertystone-one'
const b64 = (p, mime) => `data:${mime};base64,` + readFileSync(p).toString('base64')
const m600 = b64('.claude/skills/ai-commercial/scripts/fonts/Montserrat-600.ttf', 'font/ttf')
const m500 = b64('.claude/skills/ai-commercial/scripts/fonts/Montserrat-500.ttf', 'font/ttf')

const html = `<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{font-family:'Montserrat';font-weight:600;src:url(${m600}) format('truetype')}
@font-face{font-family:'Montserrat';font-weight:500;src:url(${m500}) format('truetype')}
*{margin:0;padding:0;box-sizing:border-box;font-family:'Montserrat',sans-serif}
html,body{width:1280px;height:720px;background:transparent;overflow:hidden}
.tag{position:absolute;left:0;right:0;top:492px;text-align:center;color:#E8ECF2;font-weight:600;font-size:34px;letter-spacing:.01em}
.risk{position:absolute;left:0;right:0;top:632px;text-align:center;color:#8A97AD;font-weight:500;font-size:15px;line-height:1.5;letter-spacing:.02em;padding:0 120px}
</style></head><body>
<div class="tag">Your whole SMSF, in one place.</div>
<div class="risk">General information only. It does not consider your objectives, financial situation or needs.<br>Investing and crypto assets carry risk, including loss of capital.</div>
</body></html>`

const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || '/opt/pw-browsers/chromium' })
const ctx = await browser.newContext({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1 })
const page = await ctx.newPage()
await page.setContent(html, { waitUntil: 'load' })
await page.evaluate(async () => { await document.fonts.ready })
await page.waitForTimeout(150)
await page.screenshot({ path: `${ROOT}/clips/endcard-text.png`, omitBackground: true })
await browser.close()
console.log('wrote endcard-text.png (transparent)')
