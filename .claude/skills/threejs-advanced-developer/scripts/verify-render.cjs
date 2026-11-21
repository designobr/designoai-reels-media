const { chromium } = require('playwright');

(async () => {
const base = process.env.BASE_URL || 'http://127.0.0.1:4173';
const out = process.env.OUT_DIR;
if (!out) { console.error('Defina OUT_DIR com a pasta das capturas.'); process.exit(2); }
const browser = await chromium.launch({
  executablePath: '/opt/pw-browsers/chromium',
  args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--no-sandbox'],
});
const results = [];
for (const [name, path, ready] of [
  ['vanilla', '/', () => window.__threeReady === true],
  ['r3f', '/r3f.html', () => !!document.querySelector('canvas')],
]) {
  const page = await browser.newPage({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1 });
  const errors = [];
  page.on('console', (m) => { if (m.type() === 'error' || m.type() === 'warning') errors.push(`${m.type()}: ${m.text()}`); });
  page.on('pageerror', (e) => errors.push(`pageerror: ${e.message}`));
  await page.goto(base + path, { waitUntil: 'load' });
  await page.waitForFunction(ready, null, { timeout: 20000 });
  await page.waitForTimeout(3000);
  const info = await page.evaluate(() => {
    const c = document.querySelector('canvas');
    if (!c) return { canvas: false };
    const gl = c.getContext('webgl2') || c.getContext('webgl');
    let nonBlank = null;
    try {
      const px = new Uint8Array(4 * 16);
      // Amostra uma grade do canvas via 2D copia (evita readPixels com preserveDrawingBuffer=false).
      const tmp = document.createElement('canvas');
      tmp.width = 64; tmp.height = 36;
      tmp.getContext('2d').drawImage(c, 0, 0, 64, 36);
      const d = tmp.getContext('2d').getImageData(0, 0, 64, 36).data;
      let sum = 0; for (let i = 0; i < d.length; i += 4) sum += d[i] + d[i + 1] + d[i + 2];
      nonBlank = sum / (64 * 36 * 3);
    } catch (e) { nonBlank = 'err ' + e.message; }
    return { canvas: true, width: c.width, height: c.height, webgl: !!gl, meanBrightness: nonBlank };
  });
  await page.screenshot({ path: `${out}/${name}.png` });
  results.push({ name, ...info, errors });
  await page.close();
}
await browser.close();
console.log(JSON.stringify(results, null, 2));
})().catch((e) => { console.error(e); process.exit(1); });
