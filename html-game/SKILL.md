---
name: html-game
description: Build production-quality HTML5 games (single-file, runs in any browser). Covers game loop, input, collision, audio, particles, state management, and polish. Use for any browser-game project.
---

# HTML-Game Skill

## Overview
Build a single-file HTML5 game that runs in any modern browser — no build step, no framework.
- Canvas 2D for rendering (WebGL only when justified by performance).
- Vanilla JS + requestAnimationFrame game loop.
- Embed CSS + JS inline so the file is portable.

## Bundled Helper Module
**`skill/html-game/scripts/html_game.py`** (stdlib only):
- `build_game_html(title, js, css, width, height)` — wrap JS into a runnable HTML file.
- `GAME_LOOP_TEMPLATE` — fixed-timestep loop with interpolation.
- `INPUT_HANDLER_TEMPLATE` — keyboard + mouse + touch.
- `AUDIO_MANAGER_TEMPLATE` — WebAudio synth (no asset files needed).
- `PARTICLE_SYSTEM_TEMPLATE` — lightweight particle FX.
- `STATE_MACHINE_TEMPLATE` — menu / play / pause / game-over states.
- `save_game(html, filename)` — write to `/home/z/my-project/download/games/`.

```python
import sys; sys.path.insert(0, "skill/html-game/scripts")
from html_game import (build_game_html, save_game, GAME_LOOP_TEMPLATE,
                        INPUT_HANDLER_TEMPLATE, AUDIO_MANAGER_TEMPLATE,
                        PARTICLE_SYSTEM_TEMPLATE, STATE_MACHINE_TEMPLATE)
```
Run `python skill/html-game/scripts/html_game.py` to emit a starter game file.

## Production-Quality Checklist (the bar)
A "game company sale-level" game must have:
- [ ] **Title screen** with start button.
- [ ] **Game loop** with fixed-timestep update + interpolation (no frame-rate-dependent physics).
- [ ] **Input**: keyboard + mouse + touch (responsive on mobile).
- [ ] **Audio**: SFX for key events (shoot / hit / pickup / game-over) + BGM.
- [ ] **Particles**: hit effects, trails, explosions.
- [ ] **Screen shake** on impact.
- [ ] **HUD**: score, lives, time — readable, doesn't overlap action.
- [ ] **Pause** (Esc / P) with overlay.
- [ ] **Game over** screen with restart button.
- [ ] **High score** persisted to localStorage.
- [ ] **Difficulty ramp** — gets harder over time.
- [ ] **Juice**: squash-and-stretch, hit-stop, easing on tweens.
- [ ] **Pixel-perfect** or AABB collision (no clipping through walls).
- [ ] **Responsive canvas** — scales to viewport without distortion.
- [ ] **No external assets** (or all assets embedded as data URIs).
- [ ] **Performance**: 60 FPS on a mid-range laptop.

## File Structure (single HTML)

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
  <title>{title}</title>
  <style>
    /* reset, layout, HUD, overlays */
  </style>
</head>
<body>
  <canvas id="game" width="{w}" height="{h}"></canvas>
  <div id="hud">...</div>
  <div id="overlay">...</div>
  <script>
    /* === CONFIG === */
    /* === STATE === */
    /* === INPUT === */
    /* === AUDIO === */
    /* === ENTITIES === */
    /* === PARTICLES === */
    /* === COLLISION === */
    /* === RENDER === */
    /* === GAME LOOP === */
    /* === BOOT === */
  </script>
</body>
</html>
```

## Game Loop (fixed-timestep)

```javascript
const STEP = 1 / 60;          // 60 Hz physics
let acc = 0, last = 0, alpha = 0;

function frame(now) {
  if (!last) last = now;
  let dt = (now - last) / 1000;
  last = now;
  if (dt > 0.25) dt = 0.25;   // clamp spiral-of-death
  acc += dt;
  while (acc >= STEP) {
    update(STEP);
    acc -= STEP;
  }
  alpha = acc / STEP;
  render(alpha);
  requestAnimationFrame(frame);
}
requestAnimationFrame(frame);
```

## Input (multi-device)

```javascript
const keys = {};
addEventListener('keydown', e => { keys[e.code] = true; });
addEventListener('keyup',   e => { keys[e.code] = false; });

// Mouse / touch → canvas coords
function canvasPos(evt) {
  const r = canvas.getBoundingClientRect();
  const x = (evt.clientX - r.left) * (canvas.width / r.width);
  const y = (evt.clientY - r.top)  * (canvas.height / r.height);
  return { x, y };
}
canvas.addEventListener('mousemove', e => mouse = canvasPos(e));
canvas.addEventListener('touchmove', e => {
  e.preventDefault();
  const t = e.touches[0];
  mouse = canvasPos(t);
}, { passive: false });
```

## Audio (no asset files — WebAudio synth)

```javascript
let actx;
function sfx(freq, dur=0.1, type='square', vol=0.2) {
  if (!actx) actx = new (AudioContext || webkitAudioContext)();
  const o = actx.createOscillator(), g = actx.createGain();
  o.type = type; o.frequency.value = freq;
  g.gain.setValueAtTime(vol, actx.currentTime);
  g.gain.exponentialRampToValueAtTime(0.001, actx.currentTime + dur);
  o.connect(g).connect(actx.destination);
  o.start(); o.stop(actx.currentTime + dur);
}
// sfx(440, 0.08, 'square') — shoot
// sfx(120, 0.15, 'sawtooth') — hit
// sfx(660, 0.05, 'sine') — pickup
```

## Particles

```javascript
const particles = [];
function burst(x, y, n=12, color='#ff6') {
  for (let i = 0; i < n; i++) {
    const a = Math.random() * Math.PI * 2, s = 80 + Math.random() * 120;
    particles.push({ x, y, vx: Math.cos(a)*s, vy: Math.sin(a)*s,
                     life: 0.4 + Math.random()*0.3, max: 0.7, color });
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
```

## Screen Shake

```javascript
let shake = 0;
function addShake(amt) { shake = Math.min(shake + amt, 12); }
// In render(): ctx.save(); ctx.translate(rand(-shake,shake), rand(-shake,shake));
// ... draw ... ctx.restore(); shake *= 0.85;
```

## Collision (AABB)

```javascript
function aabb(a, b) {
  return a.x < b.x + b.w && a.x + a.w > b.x &&
         a.y < b.y + b.h && a.y + a.h > b.y;
}
```

## High Score (localStorage)

```javascript
function loadHighScore() {
  return parseInt(localStorage.getItem('hs_' + GAME_ID) || '0', 10);
}
function saveHighScore(s) {
  localStorage.setItem('hs_' + GAME_ID, String(s));
}
```

## Workflow

1. **Concept** — genre, 1-sentence pitch, win/lose conditions.
2. **Mechanics** — controls, core loop, scoring, difficulty ramp.
3. **Asset plan** — embed as data URIs or generate with canvas / WebAudio.
4. **Build** — use `build_game_html()` to scaffold, then fill in entities.
5. **Test in browser** — open the file, play to 60s, check FPS.
6. **Polish** — add particles, screen shake, SFX, easing.
7. **Save** — `save_game(html, "my_game.html")`.

## Output Format

```markdown
# Game — {title}

## Pitch
{1 sentence}

## How to Play
- Controls: {keys / mouse / touch}
- Goal: {win condition}
- Lose: {lose condition}

## File
- Path: /home/z/my-project/download/games/{filename}
- Open: file:///home/z/my-project/download/games/{filename}

## Mechanics
- Difficulty ramp: {description}
- Scoring: {description}
- Power-ups: {list}

## Tech
- Render: Canvas 2D
- Audio: WebAudio synth (no asset files)
- Size: {N} KB
- Tested FPS: {60 / 30 / ...}
```

## Common Pitfalls

| Pitfall | Fix |
|---|---|
| Frame-rate-dependent physics | Use fixed-timestep loop |
| Touch doesn't work | `preventDefault()` on touch events |
| Audio blocked on load | Resume AudioContext on first user gesture |
| Canvas blurry on HiDPI | Scale by `devicePixelRatio` |
| Screen too small on mobile | Responsive canvas + `user-scalable=no` |
| Asset 404s | Embed as data URI |
| Memory leak (particles) | Cap particle count; splice dead ones |
| Sprite flicker | Double-buffer (canvas handles this); clear before draw |
