// Shared, deterministic drawing helpers for the Red Sea scenes.
// Every scene draws a pure function of its own timeline time — no clocks, no Math.random.
(function () {
  const W = 1920;
  const H = 1080;

  function rng(seed) {
    let a = seed >>> 0;
    return function () {
      a = (a + 0x6d2b79f5) >>> 0;
      let t = a;
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  function hash(n) {
    const s = Math.sin(n * 127.1 + 311.7) * 43758.5453;
    return s - Math.floor(s);
  }

  // Smooth 1D value noise in [0, 1].
  function noise(x) {
    const i = Math.floor(x);
    const f = x - i;
    const u = f * f * (3 - 2 * f);
    return hash(i) * (1 - u) + hash(i + 1) * u;
  }

  const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
  const lerp = (a, b, t) => a + (b - a) * t;
  const smooth = (a, b, v) => {
    const t = clamp((v - a) / (b - a), 0, 1);
    return t * t * (3 - 2 * t);
  };
  const easeOut = (t) => 1 - Math.pow(1 - clamp(t, 0, 1), 3);
  const easeInOut = (t) => {
    t = clamp(t, 0, 1);
    return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
  };

  // A robed figure, feet at (x, y), height h. Seen from behind or the side.
  // o: { phase, walk, staff, arms, bundle, child, lean, fill }
  function figure(ctx, x, y, h, o) {
    o = o || {};
    const phase = o.phase || 0;
    const walk = o.walk || 0;
    const bob = walk * Math.abs(Math.sin(phase)) * h * 0.025;
    const sway = walk * Math.sin(phase) * h * 0.018;
    const lean = (o.lean || 0) * h * 0.08;
    const w = h * (o.child ? 0.3 : 0.25);
    const hr = h * (o.child ? 0.085 : 0.07);
    ctx.save();
    ctx.translate(x, y - bob);
    ctx.fillStyle = o.fill || "#05070d";
    const hem = w * (0.56 + 0.06 * Math.sin(phase + 1.3) * walk);
    const sh = -h * 0.74;
    // robe: flared hem, rounded shoulders, narrow neck
    ctx.beginPath();
    ctx.moveTo(-hem + sway * 0.5, 0);
    ctx.bezierCurveTo(-w * 0.5, -h * 0.3, -w * 0.48, -h * 0.55, -w * 0.46 + lean, sh);
    ctx.quadraticCurveTo(-w * 0.42 + lean, sh - h * 0.05, -w * 0.14 + lean, sh - h * 0.06);
    ctx.lineTo(w * 0.14 + lean, sh - h * 0.06);
    ctx.quadraticCurveTo(w * 0.42 + lean, sh - h * 0.05, w * 0.46 + lean, sh);
    ctx.bezierCurveTo(w * 0.48, -h * 0.55, w * 0.5, -h * 0.3, hem + sway * 0.5, 0);
    ctx.closePath();
    ctx.fill();
    // sleeves: a slight bulge where the arms hang and swing
    const swing = walk * Math.sin(phase) * w * 0.12;
    ctx.beginPath();
    ctx.ellipse(-w * 0.47 + lean - swing, -h * 0.55, w * 0.11, h * 0.17, 0.08, 0, Math.PI * 2);
    ctx.ellipse(w * 0.47 + lean + swing, -h * 0.55, w * 0.11, h * 0.17, -0.08, 0, Math.PI * 2);
    ctx.fill();
    // head, and the head-cloth draping to the shoulders
    const hx = lean * 1.2 + sway * 0.3;
    const hy = sh - h * 0.06 - hr * 0.95;
    ctx.beginPath();
    ctx.arc(hx, hy, hr, 0, Math.PI * 2);
    ctx.fill();
    ctx.beginPath();
    ctx.moveTo(hx - hr * 1.05, hy - hr * 0.1);
    ctx.quadraticCurveTo(hx, hy - hr * 1.55, hx + hr * 1.05, hy - hr * 0.1);
    ctx.quadraticCurveTo(hx + hr * 1.5, hy + hr * 1.4, w * 0.3 + lean, sh + h * 0.02);
    ctx.lineTo(-w * 0.3 + lean, sh + h * 0.02);
    ctx.quadraticCurveTo(hx - hr * 1.5, hy + hr * 1.4, hx - hr * 1.05, hy - hr * 0.1);
    ctx.fill();
    if (o.bundle) {
      ctx.beginPath();
      ctx.ellipse(-w * 0.05 + lean, -h * 0.6, w * 0.4, h * 0.11, -0.15, 0, Math.PI * 2);
      ctx.fill();
    }
    if (o.arms) {
      ctx.lineWidth = Math.max(1, w * 0.24);
      ctx.lineCap = "round";
      ctx.strokeStyle = ctx.fillStyle;
      ctx.beginPath();
      ctx.moveTo(-w * 0.4, sh + h * 0.03);
      ctx.lineTo(-w * 0.85, sh - h * 0.36);
      ctx.moveTo(w * 0.4, sh + h * 0.03);
      ctx.lineTo(w * 0.85, sh - h * 0.36);
      ctx.stroke();
    }
    if (o.staff) {
      ctx.lineWidth = Math.max(1, w * 0.075);
      ctx.lineCap = "round";
      ctx.strokeStyle = ctx.fillStyle;
      ctx.beginPath();
      ctx.moveTo(w * 0.62 + swing, 0);
      ctx.lineTo(w * 0.6 + swing, -h * 1.02);
      ctx.stroke();
    }
    ctx.restore();
  }

  // A crowd laid out in depth bands. Returns an array of people sorted far → near.
  function crowd(seed, count, region) {
    const r = rng(seed);
    const people = [];
    for (let i = 0; i < count; i++) {
      const d = Math.pow(r(), 0.8); // 0 far → 1 near
      people.push({
        d,
        x: lerp(region.x0, region.x1, r()) + (r() - 0.5) * 30,
        phase: r() * Math.PI * 2,
        speed: 0.7 + r() * 0.6,
        child: r() < 0.18,
        staff: r() < 0.12,
        bundle: r() < 0.3,
        lean: (r() - 0.5) * 0.3,
      });
    }
    people.sort((a, b) => a.d - b.d);
    return people;
  }

  function stars(seed, n) {
    const r = rng(seed);
    const out = [];
    for (let i = 0; i < n; i++) out.push({ x: r() * W, y: r() * H * 0.55, s: 0.6 + r() * 1.6, p: r() * 6.28 });
    return out;
  }

  function drawStars(ctx, list, t, alpha) {
    for (const s of list) {
      const a = alpha * (0.45 + 0.55 * (0.5 + 0.5 * Math.sin(t * 1.7 + s.p)));
      ctx.fillStyle = `rgba(235, 228, 210, ${a})`;
      ctx.fillRect(s.x, s.y, s.s, s.s);
    }
  }

  // Film grain: a fixed pool of specks re-seeded per 1/12s step.
  function grain(ctx, t, amount) {
    const step = Math.floor(t * 12);
    const r = rng(9001 + step);
    ctx.save();
    for (let i = 0; i < 900; i++) {
      const v = r() > 0.5 ? 255 : 0;
      ctx.fillStyle = `rgba(${v},${v},${v},${amount * r()})`;
      ctx.fillRect(r() * W, r() * H, 2, 2);
    }
    ctx.restore();
  }

  function vignette(ctx, strength) {
    const g = ctx.createRadialGradient(W / 2, H / 2, H * 0.35, W / 2, H / 2, H * 1.05);
    g.addColorStop(0, "rgba(0,0,0,0)");
    g.addColorStop(1, `rgba(0,0,0,${strength})`);
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, W, H);
  }

  // Pillar of fire: a flickering vertical column centered on x, base at y.
  function pillarOfFire(ctx, x, y, h, t, intensity) {
    ctx.save();
    ctx.globalCompositeOperation = "lighter";
    const glow = ctx.createRadialGradient(x, y - h * 0.45, 10, x, y - h * 0.45, h * 0.75);
    glow.addColorStop(0, `rgba(255, 170, 70, ${0.38 * intensity})`);
    glow.addColorStop(1, "rgba(255, 120, 30, 0)");
    ctx.fillStyle = glow;
    ctx.fillRect(x - h, y - h * 1.3, h * 2, h * 2.2);
    const widths = [96, 78, 62, 46, 32, 18];
    const cols = ["rgba(255,90,20,", "rgba(255,110,30,", "rgba(255,140,45,", "rgba(255,170,60,", "rgba(255,205,110,", "rgba(255,240,190,"];
    const alphas = [0.12, 0.16, 0.2, 0.26, 0.32, 0.45];
    for (let k = 0; k < widths.length; k++) {
      const wk = widths[k];
      const col = cols[k];
      ctx.beginPath();
      const steps = 40;
      for (let i = 0; i <= steps; i++) {
        const v = i / steps;
        const yy = y - v * h;
        const ww = wk * (0.55 + 0.6 * noise(v * 6 - t * 3 + k * 10)) * (1 - v * 0.35);
        const xx = x + (noise(v * 3 - t * 1.4 + k) - 0.5) * 30 - ww;
        if (i === 0) ctx.moveTo(xx, yy);
        else ctx.lineTo(xx, yy);
      }
      for (let i = steps; i >= 0; i--) {
        const v = i / steps;
        const yy = y - v * h;
        const ww = wk * (0.55 + 0.6 * noise(v * 6 - t * 3 + k * 10 + 5)) * (1 - v * 0.35);
        const xx = x + (noise(v * 3 - t * 1.4 + k) - 0.5) * 30 + ww;
        ctx.lineTo(xx, yy);
      }
      ctx.closePath();
      ctx.fillStyle = col + alphas[k] * intensity + ")";
      ctx.fill();
    }
    ctx.restore();
  }

  // A soft cloud bank: overlapping elliptical radial gradients. Canvas blur is far too slow
  // under software rendering, so softness comes from the gradients alone.
  function cloud(ctx, x, y, w, h, color, seed) {
    const r = rng(seed);
    const m = /rgba\((\d+),\s*(\d+),\s*(\d+),\s*([\d.]+)\)/.exec(color);
    const rgb = m ? `${m[1]}, ${m[2]}, ${m[3]}` : "0, 0, 0";
    const a = m ? parseFloat(m[4]) : 0.5;
    for (let i = 0; i < 6; i++) {
      const cx = x + (r() - 0.5) * w;
      const cy = y + (r() - 0.5) * h * 0.6;
      const rx = w * (0.22 + r() * 0.22);
      const ry = h * (0.6 + r() * 0.5);
      ctx.save();
      ctx.translate(cx, cy);
      ctx.scale(rx / ry, 1);
      const g = ctx.createRadialGradient(0, 0, 0, 0, 0, ry);
      g.addColorStop(0, `rgba(${rgb}, ${a * 0.7})`);
      g.addColorStop(0.6, `rgba(${rgb}, ${a * 0.35})`);
      g.addColorStop(1, `rgba(${rgb}, 0)`);
      ctx.fillStyle = g;
      ctx.fillRect(-ry, -ry, ry * 2, ry * 2);
      ctx.restore();
    }
  }

  // Drive a canvas draw(t) from the scene's paused timeline. Seek-safe:
  // the proxy's t is a pure function of timeline time.
  function drive(tl, duration, draw) {
    const proxy = { t: 0 };
    draw(0);
    tl.to(proxy, { t: duration, duration, ease: "none", onUpdate: () => draw(proxy.t) }, 0);
  }

  window.RS = { W, H, rng, hash, noise, clamp, lerp, smooth, easeOut, easeInOut, figure, crowd, stars, drawStars, grain, vignette, pillarOfFire, cloud, drive };
})();
