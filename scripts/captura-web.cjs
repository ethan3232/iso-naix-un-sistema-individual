#!/usr/bin/env node
/*
 * Capturas de las interfaces web (TrueNAS, Proxmox VE, OPNsense) desde el PC.
 * Usa el Chrome instalado (puppeteer-core) por las redirecciones 127.0.0.1:84xx del MikroTik.
 *
 * Uso:  WEB_USER=... WEB_PASS=... NODE_PATH=<dir>/node_modules \
 *         node scripts/captura-web.cjs <producto> <url-base> <salida-dir> <pasos.json>
 *   producto: truenas | proxmox | opnsense
 *   pasos.json: [{"ruta": "/ui/dashboard", "archivo": "01-dashboard.png", "espera": 4000,
 *                 "clic": "texto opcional a pulsar", "ver": "texto hasta el que desplazarse",
 *                 "recorte": {"x":0,"y":0,"width":..,"height":..}}]
 * Las credenciales llegan por variables de entorno: nunca se guardan en el repositorio.
 */
const puppeteer = require('puppeteer-core');
const fs = require('fs');
const path = require('path');

const [producto, base, salida, pasosJson] = process.argv.slice(2);
const pasos = JSON.parse(fs.readFileSync(pasosJson, 'utf8'));
const espera = (ms) => new Promise((r) => setTimeout(r, ms));

async function login(page) {
  const u = process.env.WEB_USER, p = process.env.WEB_PASS;
  await page.goto(base, { waitUntil: 'networkidle2', timeout: 60000 });
  await espera(3000);
  if (producto === 'truenas') {
    await page.type('input[autocomplete="username"]', u);
    await page.type('input[type="password"]', p);
    await page.keyboard.press('Enter');
  } else if (producto === 'proxmox') {
    await page.waitForSelector('input[name="username"]', { timeout: 30000 });
    await page.type('input[name="username"]', u);
    await page.type('input[name="password"]', p);
    await page.keyboard.press('Enter');
  } else if (producto === 'opnsense') {
    await page.type('#usernamefld', u);
    await page.type('#passwordfld', p);
    await page.keyboard.press('Enter');
  }
  await espera(8000);
}

// "1:Texto" pulsa la PRIMERA coincidencia (p. ej. el menú) en vez de la última.
async function pulsarTexto(page, texto) {
  const primero = texto.startsWith('1:');
  if (primero) texto = texto.slice(2);
  const ok = await page.mainFrame().evaluate((t, primero) => {
    const els = [...document.querySelectorAll('a, button, span, div, td, li')]
      .filter((e) => e.offsetParent !== null && e.textContent.trim() === t);
    if (!els.length) return false;
    (primero ? els[0] : els[els.length - 1]).click();
    return true;
  }, texto, primero);
  if (!ok) console.error(`  aviso: no se encontró "${texto}"`);
}

(async () => {
  const browser = await puppeteer.launch({
    executablePath: '/usr/bin/google-chrome',
    headless: true,
    acceptInsecureCerts: true,
    args: ['--ignore-certificate-errors', '--lang=es-ES', '--window-size=1440,900'],
    defaultViewport: { width: 1440, height: 900, deviceScaleFactor: 1 },
  });
  const page = await browser.newPage();
  await page.setExtraHTTPHeaders({ 'Accept-Language': 'es-ES,es;q=0.9' });
  await login(page);
  fs.mkdirSync(salida, { recursive: true });
  for (const paso of pasos) {
    if (paso.ruta) {
      await page.goto(base + paso.ruta, { waitUntil: 'networkidle2', timeout: 60000 }).catch(() => {});
      await espera(3000);
    }
    if (paso.escribir) {
      await page.type(paso.escribir.sel, paso.escribir.texto).catch((e) => console.error('  aviso:', e.message));
      await page.keyboard.press('Enter');
    }
    for (const t of [].concat(paso.clic || [])) { await espera(1500); await pulsarTexto(page, t); }
    await espera(paso.espera || 4000);
    if (paso.ver) {
      await page.evaluate((t) => {
        const e = [...document.querySelectorAll('h1,h2,h3,h4,span,div,mat-card-title')]
          .find((x) => x.offsetParent !== null && x.textContent.trim() === t);
        if (e) e.scrollIntoView({ block: 'start' });
      }, paso.ver);
      await espera(1500);
    }
    const archivo = path.join(salida, paso.archivo);
    await page.screenshot({ path: archivo, clip: paso.recorte });
    console.log(archivo);
  }
  await browser.close();
})().catch((e) => { console.error(e); process.exit(1); });
