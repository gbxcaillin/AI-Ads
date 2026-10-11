// Corner-pins the LibertyStone dashboard onto the dark laptop screen in the
// solution-shot plate (a still), producing a composited still we then animate
// with a push-in. Perspective via CSS matrix3d homography. Corners are in the
// plate's native pixel space (2752x1536); tweak SCREEN if the fit needs nudging.
import { chromium } from 'playwright-core'
import { readFileSync } from 'node:fs'

const ROOT = 'spots/libertystone-one'
const PLATE_W = 2752, PLATE_H = 1536
const DASH_W = 2560, DASH_H = 1600
const b64 = (p, mime) => `data:${mime};base64,` + readFileSync(p).toString('base64')
const plate = b64(`${ROOT}/clips/plate-A.png`, 'image/png')
const dash = b64(`${ROOT}/dashboard/dashboard.png`, 'image/png')

// Screen glass corners in plate pixel space: TL, TR, BR, BL
const SCREEN = (process.env.SCREEN && JSON.parse(process.env.SCREEN)) || {
  tl: [1330, 600], tr: [2448, 524], br: [2512, 1348], bl: [1286, 1300],
}

const html = `<!doctype html><html><head><meta charset="utf-8"><style>
*{margin:0;padding:0}
#frame{position:relative;width:${PLATE_W}px;height:${PLATE_H}px;overflow:hidden}
#frame img.bg{position:absolute;inset:0;width:${PLATE_W}px;height:${PLATE_H}px}
#screen{position:absolute;left:0;top:0;width:${DASH_W}px;height:${DASH_H}px;transform-origin:0 0}
#screen .dash{position:absolute;inset:0;width:100%;height:100%;filter:brightness(.9) contrast(1.02)}
/* glass sheen + edge falloff so it reads as an emissive panel behind glass */
#screen .sheen{position:absolute;inset:0;background:linear-gradient(118deg, rgba(255,255,255,.10) 0%, rgba(255,255,255,.03) 22%, rgba(255,255,255,0) 44%, rgba(0,0,0,.05) 100%);mix-blend-mode:screen}
#screen .vig{position:absolute;inset:0;box-shadow:inset 0 0 120px 24px rgba(0,0,0,.45)}
</style></head><body>
<div id="frame">
  <img class="bg" src="${plate}">
  <div id="screen">
    <img class="dash" src="${dash}">
    <div class="sheen"></div>
    <div class="vig"></div>
  </div>
</div>
<script>
const S=${JSON.stringify(SCREEN)}, DW=${DASH_W}, DH=${DASH_H};
function adj(m){return [m[4]*m[8]-m[5]*m[7],m[2]*m[7]-m[1]*m[8],m[1]*m[5]-m[2]*m[4],
 m[5]*m[6]-m[3]*m[8],m[0]*m[8]-m[2]*m[6],m[2]*m[3]-m[0]*m[5],
 m[3]*m[7]-m[4]*m[6],m[1]*m[6]-m[0]*m[7],m[0]*m[4]-m[1]*m[3]];}
function mm(a,b){const c=[];for(let i=0;i<3;i++)for(let j=0;j<3;j++){let s=0;for(let k=0;k<3;k++)s+=a[3*i+k]*b[3*k+j];c[3*i+j]=s;}return c;}
function mv(m,v){return [m[0]*v[0]+m[1]*v[1]+m[2]*v[2],m[3]*v[0]+m[4]*v[1]+m[5]*v[2],m[6]*v[0]+m[7]*v[1]+m[8]*v[2]];}
function basis(x1,y1,x2,y2,x3,y3,x4,y4){const m=[x1,x2,x3,y1,y2,y3,1,1,1];const v=mv(adj(m),[x4,y4,1]);return mm(m,[v[0],0,0,0,v[1],0,0,0,v[2]]);}
function proj(s,d){return mm(basis(...d),adj(basis(...s)));}
const src=[0,0, DW,0, DW,DH, 0,DH];
const dst=[...S.tl,...S.tr,...S.br,...S.bl];
let H=proj(src,dst);
H=H.map(x=>x/H[8]);
const m3d=[H[0],H[3],0,H[6], H[1],H[4],0,H[7], 0,0,1,0, H[2],H[5],0,H[8]];
document.getElementById('screen').style.transform='matrix3d('+m3d.join(',')+')';
</script>
</body></html>`

const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || '/opt/pw-browsers/chromium' })
const ctx = await browser.newContext({ viewport: { width: PLATE_W, height: PLATE_H }, deviceScaleFactor: 1 })
const page = await ctx.newPage()
await page.setContent(html, { waitUntil: 'load' })
await page.waitForTimeout(250)
await page.screenshot({ path: `${ROOT}/clips/plate-A-composited.png`, animations: 'disabled' })
await browser.close()
console.log('wrote plate-A-composited.png')
