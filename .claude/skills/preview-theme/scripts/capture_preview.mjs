// Imports a theme zip into a locally-running futo-org/keyboard-theme-editor
// dev server (see setup_editor.sh) via its real "File > Import theme..."
// flow, and screenshots the rendered #workcanvas -- a real render using
// FUTO's own rendering code, not an approximation.
//
// Usage: node capture_preview.mjs <path-to-theme.zip> <output-dir> [port]
import { chromium } from 'playwright';
import path from 'node:path';
import fs from 'node:fs/promises';

const ZIP_PATH = process.argv[2];
const OUT_DIR = process.argv[3];
const PORT = process.argv[4] ?? '8000';

if (!ZIP_PATH || !OUT_DIR) {
  console.error('Usage: node capture_preview.mjs <path-to-theme.zip> <output-dir> [port]');
  process.exit(1);
}

const URL = `http://127.0.0.1:${PORT}/`;

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1600, height: 1000 } });

let importAlert = null;
page.on('dialog', async (dialog) => {
  importAlert = dialog.message();
  await dialog.accept();
});
page.on('console', (msg) => {
  const text = msg.text();
  // "data.asset[other] is absent" is expected/benign for themes with no
  // [[asset.other]] block (font/background don't require one) -- only
  // surface anything else, so real problems aren't buried in noise.
  if (msg.type() === 'error' && !text.includes('data.asset[other] is absent')) {
    console.log('[console.error]', text);
  }
});

await page.goto(URL, { waitUntil: 'load' });
await page.waitForSelector('#menuBar', { timeout: 15000 });

// An "About" window is open by default on first load and covers part of
// the canvas -- close any open window before doing anything else.
const closeButtons = page.locator('.win .bar button');
const openWindows = await closeButtons.count();
for (let i = 0; i < openWindows; i++) {
  await closeButtons.first().click();
  await page.waitForTimeout(200);
}

await page.click('header#menuBar >> text=File');
const fileChooserPromise = page.waitForEvent('filechooser');
await page.click('li.item >> text=Import theme...');
const fileChooser = await fileChooserPromise;
await fileChooser.setFiles(path.resolve(ZIP_PATH));

await page.waitForTimeout(1500);
await page.waitForSelector('#workcanvas', { timeout: 15000 });
await page.waitForTimeout(500);

if (!importAlert || !importAlert.startsWith('Project imported')) {
  console.error('Import may have failed -- no "Project imported" dialog seen.');
  await browser.close();
  process.exit(1);
}

await fs.mkdir(OUT_DIR, { recursive: true });
const outPath = path.join(OUT_DIR, 'preview.png');
await page.locator('#workcanvas').screenshot({ path: outPath });

await browser.close();
console.log(importAlert);
console.log('screenshot:', outPath);
