"""html_game.py — Build single-file HTML5 games.

Standard-library only. Provides:
  * GAME_LOOP_TEMPLATE          — fixed-timestep loop with interpolation.
  * INPUT_HANDLER_TEMPLATE      — keyboard + mouse + touch.
  * AUDIO_MANAGER_TEMPLATE      — WebAudio synth (no asset files).
  * PARTICLE_SYSTEM_TEMPLATE    — lightweight particle FX.
  * STATE_MACHINE_TEMPLATE      — menu / play / pause / game-over.
  * build_game_html(...)        — wrap JS + CSS into a runnable HTML file.
  * save_game(html, filename)   — write to /home/z/my-project/download/games/.
"""
from __future__ import annotations
from pathlib import Path


# ---- Snippet templates ---------------------------------------------------

GAME_LOOP_TEMPLATE = """\
const STEP = 1 / 60;          // 60 Hz physics
let acc = 0, last = 0, alpha = 0;
let running = false;

function frame(now) {
  if (!last) last = now;
  let dt = (now - last) / 1000;
  last = now;
  if (dt > 0.25) dt = 0.25;   // clamp spiral-of-death
  if (running) {
    acc += dt;
    while (acc >= STEP) { update(STEP); acc -= STEP; }
    alpha = acc / STEP;
    render(alpha);
  }
  requestAnimationFrame(frame);
}
"""


INPUT_HANDLER_TEMPLATE = """\
const keys = {};
const mouse = { x: 0, y: 0, down: false };

addEventListener('keydown', e => {
  keys[e.code] = true;
  if (['ArrowUp','ArrowDown','ArrowLeft','ArrowRight','Space'].includes(e.code)) e.preventDefault();
});
addEventListener('keyup', e => { keys[e.code] = false; });

function canvasPos(evt) {
  const r = canvas.getBoundingClientRect();
  const x = (evt.clientX - r.left) * (canvas.width / r.width);
  const y = (evt.clientY - r.top)  * (canvas.height / r.height);
  return { x, y };
}
canvas.addEventListener('mousemove', e => Object.assign(mouse, canvasPos(e)));
canvas.addEventListener('mousedown', e => { Object.assign(mouse, canvasPos(e)); mouse.down = true; });
canvas.addEventListener('mouseup',   () => { mouse.down = false; });
canvas.addEventListener('touchmove', e => {
  e.preventDefault();
  const t = e.touches[0];
  Object.assign(mouse, canvasPos(t));
}, { passive: false });
canvas.addEventListener('touchstart', e => {
  e.preventDefault();
  const t = e.touches[0];
  Object.assign(mouse, canvasPos(t));
  mouse.down = true;
}, { passive: false });
canvas.addEventListener('touchend', () => { mouse.down = false; });
"""


AUDIO_MANAGER_TEMPLATE = """\
let actx = null;
function audioInit() {
  if (!actx) actx = new (window.AudioContext || window.webkitAudioContext)();
  if (actx.state === 'suspended') actx.resume();
}
function sfx(freq, dur = 0.1, type = 'square', vol = 0.2) {
  if (!actx) return;
  const o = actx.createOscillator(), g = actx.createGain();
  o.type = type; o.frequency.value = freq;
  g.gain.setValueAtTime(vol, actx.currentTime);
  g.gain.exponentialRampToValueAtTime(0.001, actx.currentTime + dur);
  o.connect(g).connect(actx.destination);
  o.start(); o.stop(actx.currentTime + dur);
}
// Quick presets:
const SFX = {
  shoot:   () => sfx(440, 0.08, 'square', 0.15),
  hit:     () => sfx(120, 0.15, 'sawtooth', 0.25),
  pickup:  () => sfx(660, 0.05, 'sine', 0.2),
  gameover:() => sfx(80, 0.5, 'triangle', 0.3),
};
"""


PARTICLE_SYSTEM_TEMPLATE = """\
const particles = [];
function burst(x, y, n = 12, color = '#ffd166') {
  for (let i = 0; i < n; i++) {
    const a = Math.random() * Math.PI * 2;
    const s = 80 + Math.random() * 120;
    particles.push({
      x, y,
      vx: Math.cos(a) * s, vy: Math.sin(a) * s,
      life: 0.4 + Math.random() * 0.3, max: 0.7,
      color,
    });
  }
}
function updateParticles(dt) {
  for (let i = particles.length - 1; i >= 0; i--) {
    const p = particles[i];
    p.x += p.vx * dt; p.y += p.vy * dt;
    p.vx *= 0.94; p.vy *= 0.94; p.vy += 200 * dt;
    p.life -= dt;
    if (p.life <= 0) particles.splice(i, 1);
  }
}
function renderParticles(ctx) {
  for (const p of particles) {
    const a = Math.max(0, p.life / p.max);
    ctx.globalAlpha = a;
    ctx.fillStyle = p.color;
    ctx.fillRect(p.x - 2, p.y - 2, 4, 4);
  }
  ctx.globalAlpha = 1;
}
"""


STATE_MACHINE_TEMPLATE = """\
const STATE = { MENU: 'menu', PLAY: 'play', PAUSE: 'pause', OVER: 'over' };
let state = STATE.MENU;
let score = 0, lives = 3, highScore = 0;

function setState(s) {
  state = s;
  overlay.style.display = (s === STATE.PLAY) ? 'none' : 'flex';
  if (s === STATE.OVER) {
    if (score > highScore) { highScore = score; localStorage.setItem('hs_' + GAME_ID, String(highScore)); }
    overlayTitle.textContent = 'Game Over';
    overlaySub.textContent = 'Score: ' + score + ' / Best: ' + highScore;
    startBtn.textContent = 'Restart';
  } else if (s === STATE.MENU) {
    overlayTitle.textContent = GAME_TITLE;
    overlaySub.textContent = '';
    startBtn.textContent = 'Start';
  } else if (s === STATE.PAUSE) {
    overlayTitle.textContent = 'Paused';
    overlaySub.textContent = 'Press P to resume';
  }
}
"""


DEFAULT_CSS = """\
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body {
  height: 100%;
  background: #0a0a0a;
  color: #fff;
  font-family: 'Inter', system-ui, sans-serif;
  overflow: hidden;
  user-select: none;
  -webkit-user-select: none;
}
#wrap {
  position: relative;
  width: 100vw; height: 100vh;
  display: flex; align-items: center; justify-content: center;
}
#game {
  background: #111;
  max-width: 100%; max-height: 100%;
  image-rendering: pixelated;
}
#overlay {
  position: absolute; inset: 0;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  background: rgba(0,0,0,0.7);
  text-align: center;
}
#overlay h1 { font-size: 48px; margin-bottom: 8px; }
#overlay p  { font-size: 18px; color: #ccc; margin-bottom: 24px; }
#startBtn {
  padding: 12px 32px;
  font-size: 18px; font-weight: 600;
  background: #d4502a; color: #fff;
  border: none; border-radius: 8px;
  cursor: pointer;
}
#startBtn:hover { background: #b8401f; }
#hud {
  position: absolute; top: 12px; left: 12px;
  font-size: 16px; font-family: monospace;
  pointer-events: none;
}
"""


# ---- Builder -------------------------------------------------------------

def build_game_html(*,
                    title: str,
                    js_body: str,
                    css: str = "",
                    width: int = 800,
                    height: int = 600,
                    game_id: str | None = None) -> str:
    """Wrap game JS into a complete single-file HTML.

    js_body should define: update(dt), render(alpha), and call requestAnimationFrame(frame).
    The boilerplate (game loop, input, audio, particles, state) is provided
    automatically — extend it inside js_body as needed.
    """
    game_id = game_id or title.lower().replace(" ", "_")
    css_final = css or DEFAULT_CSS
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
<title>{title}</title>
<style>
{css_final}
</style>
</head>
<body>
<div id="wrap">
  <canvas id="game" width="{width}" height="{height}"></canvas>
  <div id="hud">Score: 0</div>
  <div id="overlay">
    <h1 id="overlayTitle">{title}</h1>
    <p id="overlaySub"></p>
    <button id="startBtn">Start</button>
  </div>
</div>
<script>
const GAME_TITLE = {repr(title)};
const GAME_ID = {repr(game_id)};

const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');
const hud = document.getElementById('hud');
const overlay = document.getElementById('overlay');
const overlayTitle = document.getElementById('overlayTitle');
const overlaySub = document.getElementById('overlaySub');
const startBtn = document.getElementById('startBtn');

// === STATE MACHINE ===
{STATE_MACHINE_TEMPLATE}

// === GAME LOOP ===
{GAME_LOOP_TEMPLATE}

// === INPUT ===
{INPUT_HANDLER_TEMPLATE}

// === AUDIO ===
{AUDIO_MANAGER_TEMPLATE}

// === PARTICLES ===
{PARTICLE_SYSTEM_TEMPLATE}

// === HIGH SCORE ===
highScore = parseInt(localStorage.getItem('hs_' + GAME_ID) || '0', 10);

// === BOOT ===
startBtn.addEventListener('click', () => {{
  audioInit();
  setState(STATE.PLAY);
  score = 0; lives = 3;
  running = true;
}});
addEventListener('keydown', e => {{
  if (e.code === 'KeyP' && state === STATE.PLAY) setState(STATE.PAUSE);
  else if (e.code === 'KeyP' && state === STATE.PAUSE) setState(STATE.PLAY);
}});

// === USER GAME CODE ===
{js_body}

requestAnimationFrame(frame);
</script>
</body>
</html>
"""


def save_game(html: str, filename: str,
              out_dir: str = "/home/z/my-project/download/games") -> Path:
    p = Path(out_dir) / filename
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(html, encoding="utf-8")
    return p


# ---- Self-test ------------------------------------------------------------

# A minimal but real game — paddle bouncing a ball, with score + lives.
_DEMO_JS = """\
const ball = { x: 400, y: 300, vx: 240, vy: -180, r: 8 };
const paddle = { x: 350, y: 560, w: 100, h: 12, speed: 480 };
let shake = 0;

function update(dt) {
  if (state !== STATE.PLAY) return;
  // Paddle controls
  if (keys.ArrowLeft || keys.KeyA)  paddle.x -= paddle.speed * dt;
  if (keys.ArrowRight || keys.KeyD) paddle.x += paddle.speed * dt;
  paddle.x = Math.max(0, Math.min(canvas.width - paddle.w, paddle.x));
  // Mouse / touch follow
  if (mouse.x) paddle.x = Math.max(0, Math.min(canvas.width - paddle.w, mouse.x - paddle.w / 2));

  // Ball
  ball.x += ball.vx * dt; ball.y += ball.vy * dt;
  if (ball.x < ball.r || ball.x > canvas.width - ball.r) { ball.vx *= -1; SFX.hit(); }
  if (ball.y < ball.r) { ball.vy *= -1; SFX.hit(); }

  // Paddle collision
  if (ball.y + ball.r > paddle.y && ball.y < paddle.y + paddle.h &&
      ball.x > paddle.x && ball.x < paddle.x + paddle.w) {
    ball.vy = -Math.abs(ball.vy);
    ball.vx += (ball.x - (paddle.x + paddle.w / 2)) * 4;
    ball.vx = Math.max(-360, Math.min(360, ball.vx));
    score += 10;
    hud.textContent = 'Score: ' + score;
    SFX.shoot();
    burst(ball.x, ball.y, 8, '#4caf50');
    addShake(3);
  }

  // Lose
  if (ball.y > canvas.height) {
    lives -= 1;
    SFX.gameover();
    addShake(8);
    if (lives <= 0) { setState(STATE.OVER); running = false; }
    else { ball.x = 400; ball.y = 300; ball.vx = 240; ball.vy = -180; }
  }

  updateParticles(dt);
  shake *= 0.85;
}

function addShake(amt) { shake = Math.min(shake + amt, 12); }

function render(alpha) {
  ctx.save();
  if (shake > 0.5) ctx.translate((Math.random() - 0.5) * shake, (Math.random() - 0.5) * shake);
  ctx.fillStyle = '#111';
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  // Ball
  ctx.fillStyle = '#ffd166';
  ctx.beginPath(); ctx.arc(ball.x, ball.y, ball.r, 0, Math.PI * 2); ctx.fill();
  // Paddle
  ctx.fillStyle = '#4af';
  ctx.fillRect(paddle.x, paddle.y, paddle.w, paddle.h);
  // Particles
  renderParticles(ctx);
  ctx.restore();

  // HUD extras
  ctx.fillStyle = '#fff';
  ctx.font = '14px monospace';
  ctx.fillText('Lives: ' + lives, 12, 32);
}
"""


if __name__ == "__main__":
    html = build_game_html(
        title="Paddle Bounce",
        js_body=_DEMO_JS,
        width=800,
        height=600,
        game_id="paddle_bounce",
    )
    out = save_game(html, "paddle_bounce.html")
    print(f"Game written: {out}")
    print(f"Size: {out.stat().st_size:,} bytes")
    print(f"Open in browser: file://{out}")
