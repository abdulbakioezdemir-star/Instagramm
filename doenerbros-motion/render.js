// Usage: node render.js stills 0,4,8   |   node render.js video out.mp4 [fps]
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const http = require('http'), fs = require('fs'), path = require('path');
const root = __dirname;
const types = { '.html': 'text/html', '.js': 'text/javascript', '.png': 'image/png' };
const srv = http.createServer((q, r) => { const f = path.join(root, decodeURIComponent(q.url.split('?')[0]));
  fs.readFile(f, (e, d) => { if (e) { r.writeHead(404); r.end(); return; } r.writeHead(200, { 'Content-Type': types[path.extname(f)] || 'application/octet-stream' }); r.end(d); }); });
(async () => {
  await new Promise(r => srv.listen(0, r)); const port = srv.address().port;
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  p.on('console', m => console.log('[page]', m.text())); p.on('pageerror', e => console.log('[err]', e.message));
  await p.goto(`http://localhost:${port}/scene.html`); await p.waitForFunction(() => window.ready, null, { timeout: 120000 });
  await p.evaluate(() => document.fonts.ready);
  const [mode, arg, fpsArg] = process.argv.slice(2);
  const shot = async t => { await p.evaluate(t => renderFrame(t), t); return p.screenshot({ type: 'jpeg', quality: 94, clip: { x: 0, y: 0, width: 1080, height: 1920 } }); };
  if (mode === 'stills') {
    for (const t of arg.split(',').map(Number)) { const t0 = Date.now(); fs.writeFileSync(path.join(process.env.OUT || '.', `still_${t}.jpg`), await shot(t)); console.log('still', t, Date.now() - t0, 'ms'); }
  } else {
    const fps = Number(fpsArg || 30), N = Math.round(Number(process.env.DUR || 22) * fps), F0 = Number(process.env.FROM || 0);
    const ff = spawn('ffmpeg', ['-y', '-v', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-', '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', arg], { stdio: ['pipe', 'inherit', 'inherit'] });
    const t0 = Date.now();
    for (let i = F0; i < N; i++) { const buf = await shot(i / fps); if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      if (i % 30 === 0) console.log(`frame ${i}/${N}  ${((Date.now() - t0) / 1000).toFixed(0)}s`); }
    ff.stdin.end(); await new Promise(r => ff.on('close', r));
  }
  await b.close(); srv.close();
})();
