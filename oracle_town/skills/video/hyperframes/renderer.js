#!/usr/bin/env node
/**
 * HELEN HyperFrames Renderer v2
 *
 * HTML composition → PNG frames → MP4
 *
 * Usage:
 *   node renderer.js \
 *     --input   composition.html \
 *     --output  output.mp4 \
 *     --width   1920 \
 *     --height  1080 \
 *     --fps     30 \
 *     --duration 45
 *
 * Pipeline:
 *   1. Launch headless Chrome (Puppeteer)
 *   2. Load composition HTML
 *   3. Signal helen:render-start → GSAP timeline plays
 *   4. Capture frames at 1/fps intervals via page.screenshot()
 *   5. Pipe frames to FFmpeg → MP4 (h264, yuv420p, web-safe)
 *
 * Determinism: same HTML → same frames → same video hash.
 * No randomness. Timestamps frozen via Clock.setTime.
 */

'use strict';

const puppeteer = require('puppeteer');
const { execFile, spawn }  = require('child_process');
const { promisify } = require('util');
const path  = require('path');
const fs    = require('fs');
const crypto = require('crypto');

const execFileAsync = promisify(execFile);

// ── CLI args ───────────────────────────────────────────────────────────────────

function parseArgs() {
  const args = process.argv.slice(2);
  const out  = { width: 1920, height: 1080, fps: 30, duration: 30, input: null, output: null };
  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case '--input':    out.input    = args[++i]; break;
      case '--output':   out.output   = args[++i]; break;
      case '--width':    out.width    = parseInt(args[++i], 10); break;
      case '--height':   out.height   = parseInt(args[++i], 10); break;
      case '--fps':      out.fps      = parseInt(args[++i], 10); break;
      case '--duration': out.duration = parseFloat(args[++i]); break;
    }
  }
  if (!out.input)  { console.error('Missing --input');  process.exit(1); }
  if (!out.output) { console.error('Missing --output'); process.exit(1); }
  return out;
}

// ── Frame capture ──────────────────────────────────────────────────────────────

async function captureFrames(opts) {
  const { input, width, height, fps, duration } = opts;
  const totalFrames = Math.ceil(duration * fps);
  const frameDir    = fs.mkdtempSync('/tmp/helen-frames-');

  console.log(`[helen-renderer] ${width}×${height} @ ${fps}fps | ${duration}s | ${totalFrames} frames`);
  console.log(`[helen-renderer] frames → ${frameDir}`);

  const browser = await puppeteer.launch({
    headless: 'new',
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      `--window-size=${width},${height}`,
      '--disable-web-security',
      '--allow-file-access-from-files',
    ],
  });

  const page = await browser.newPage();
  await page.setViewport({ width, height, deviceScaleFactor: 1 });

  // Freeze randomness sources for determinism
  await page.evaluateOnNewDocument(() => {
    Math.random = (() => { let s = 0.42; return () => { s = (s * 9301 + 49297) % 233280; return s / 233280; }; })();
    const _now = Date.now;
    window.__helenStartTime = _now();
    Date.now = () => window.__helenStartTime;
    performance.now = () => 0;
  });

  const fileUrl = `file://${path.resolve(input)}`;
  await page.goto(fileUrl, { waitUntil: 'load', timeout: 30000 });

  // Wait until composition signals it is fully initialised
  await page.waitForFunction('window.__ready === true', { timeout: 15000 });

  // Capture frames by seeking the master timeline per-frame
  // (no helen:render-start — that is for live preview only)
  for (let f = 0; f < totalFrames; f++) {
    const t = f / fps;

    await page.evaluate((time) => {
      if (typeof window.__seek === 'function') {
        window.__seek(time);
      }
    }, t);

    const framePath = path.join(frameDir, `frame_${String(f).padStart(6, '0')}.png`);
    await page.screenshot({ path: framePath, type: 'png' });

    if (f % 30 === 0) {
      process.stdout.write(`\r[helen-renderer] frame ${f}/${totalFrames} (${(t).toFixed(1)}s)`);
    }
  }

  process.stdout.write('\n');
  await browser.close();
  return { frameDir, totalFrames };
}

// ── FFmpeg encode ──────────────────────────────────────────────────────────────

async function encodeVideo(opts, frameDir) {
  const { output, fps, width, height } = opts;

  fs.mkdirSync(path.dirname(path.resolve(output)), { recursive: true });

  const ffmpegArgs = [
    '-y',
    '-framerate', String(fps),
    '-i',         path.join(frameDir, 'frame_%06d.png'),
    '-c:v',       'libx264',
    '-preset',    'medium',
    '-crf',       '18',
    '-pix_fmt',   'yuv420p',
    '-vf',        `scale=${width}:${height}`,
    '-movflags',  '+faststart',
    output,
  ];

  console.log(`[helen-renderer] FFmpeg → ${output}`);

  await new Promise((resolve, reject) => {
    const proc = spawn('ffmpeg', ffmpegArgs, { stdio: ['ignore', 'pipe', 'pipe'] });
    proc.stderr.on('data', d => process.stderr.write(d));
    proc.on('close', code => code === 0 ? resolve() : reject(new Error(`FFmpeg exited ${code}`)));
  });
}

// ── Hash output ────────────────────────────────────────────────────────────────

function hashFile(filePath) {
  const bytes = fs.readFileSync(filePath);
  return 'sha256:' + crypto.createHash('sha256').update(bytes).digest('hex');
}

// ── Cleanup ────────────────────────────────────────────────────────────────────

function cleanup(frameDir) {
  fs.readdirSync(frameDir).forEach(f => fs.unlinkSync(path.join(frameDir, f)));
  fs.rmdirSync(frameDir);
}

// ── Main ───────────────────────────────────────────────────────────────────────

async function main() {
  const opts = parseArgs();

  console.log(`[helen-renderer] input: ${opts.input}`);

  const { frameDir } = await captureFrames(opts);
  await encodeVideo(opts, frameDir);
  cleanup(frameDir);

  const hash = hashFile(opts.output);
  const size = fs.statSync(opts.output).size;

  const result = {
    output:   opts.output,
    hash,
    duration: opts.duration,
    frames:   Math.ceil(opts.duration * opts.fps),
    size_bytes: size,
    authority: false,
  };

  // Print JSON receipt to stdout for Python to parse
  console.log('\n[helen-renderer] RECEIPT:');
  console.log(JSON.stringify(result, null, 2));
}

main().catch(err => {
  console.error('[helen-renderer] ERROR:', err.message);
  process.exit(1);
});
