"""Synthesize the 30s ambient bed for the Red Sea film (deterministic, offline)."""
import sys
import wave

import numpy as np

SR = 48000
DUR = 30.0
N = int(SR * DUR)
t = np.arange(N) / SR
rng = np.random.default_rng(14)


def shaped_noise(lo, hi, tilt=0.0, seed=0):
    """White noise band-limited to [lo, hi] Hz with a 1/f^tilt spectral tilt."""
    r = np.random.default_rng(seed)
    spec = np.fft.rfft(r.standard_normal(N))
    f = np.fft.rfftfreq(N, 1 / SR)
    resp = np.zeros_like(f)
    band = (f >= lo) & (f <= hi)
    resp[band] = 1.0
    # soft band edges
    resp *= np.clip((f - lo * 0.7) / (lo * 0.3 + 1e-9), 0, 1) * np.clip((hi * 1.3 - f) / (hi * 0.3), 0, 1)
    resp[1:] /= np.power(f[1:], tilt / 2)
    out = np.fft.irfft(spec * resp, n=N)
    return out / (np.max(np.abs(out)) + 1e-9)


def env(points):
    """Piecewise-linear envelope from (time, value) pairs."""
    ts, vs = zip(*points)
    return np.interp(t, ts, vs)


wind = shaped_noise(150, 1800, tilt=1.0, seed=1)
wind *= 0.75 + 0.25 * np.sin(2 * np.pi * 0.23 * t) * np.sin(2 * np.pi * 0.071 * t + 1.0)
wind *= env([(0, 0.22), (5.5, 0.28), (7.0, 0.55), (11.5, 0.6), (13, 0.45), (19, 0.4), (24, 0.22), (30, 0.1)])

rumble = shaped_noise(25, 140, tilt=1.5, seed=2)
rumble *= env([(0, 0.25), (6, 0.3), (12, 0.35), (13.5, 1.0), (17, 0.85), (19.5, 0.45), (25, 0.3), (30, 0.1)])

roar = shaped_noise(250, 2500, tilt=0.6, seed=3)
roar *= env([(0, 0), (12.6, 0), (14.2, 0.55), (16.5, 0.45), (19.2, 0.12), (25, 0.06), (26, 0)])

# Thunder, timed to the lightning in scene 2 (5.9s + 2.55s, and a second strike).
thunder = np.zeros(N)
for start, gain in [(8.45, 1.0), (8.98, 0.55)]:
    burst = shaped_noise(20, 400, tilt=1.8, seed=int(start * 100))
    d = np.clip(t - start, 0, None)
    shape = np.where(t >= start, (1 - np.exp(-d / 0.02)) * np.exp(-d / 1.1), 0)
    crackle = shaped_noise(800, 5000, tilt=0.2, seed=int(start * 100) + 7) * np.where(t >= start, np.exp(-d / 0.12), 0)
    thunder += gain * (burst * shape + 0.35 * crackle)

# Dawn: an A-major pad that rises as the procession nears the far shore.
pad = np.zeros(N)
for i, freq in enumerate([110.0, 164.81, 220.0, 277.18, 329.63, 440.0]):
    detune = 1 + (i - 2.5) * 0.0012
    pad += np.sin(2 * np.pi * freq * detune * t + i) * (0.9 if i < 3 else 0.6)
    pad += 0.5 * np.sin(2 * np.pi * freq * 2.001 * t + i * 2) * 0.3
pad /= np.max(np.abs(pad))
pad *= 0.85 + 0.15 * np.sin(2 * np.pi * 0.5 * t)
pad *= env([(0, 0), (19.5, 0), (22, 0.08), (25.5, 0.2), (27.5, 0.28), (30, 0.2)])

mix = 0.55 * wind + 0.8 * rumble + 0.6 * roar + 0.9 * thunder + 0.55 * pad
mix *= env([(0, 0), (1.2, 1), (28.6, 1), (30, 0)])
mix /= np.max(np.abs(mix)) / 0.89

# Gentle stereo: decorrelate the wind/roar slightly between channels.
side = 0.12 * shaped_noise(200, 2000, tilt=1.0, seed=9) * env([(0, 0.2), (13, 0.6), (19, 0.3), (30, 0.05)])
left = np.clip(mix + side, -1, 1)
right = np.clip(mix - side, -1, 1)
stereo = (np.stack([left, right], axis=1) * 32767).astype(np.int16)

with wave.open(sys.argv[1], "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(stereo.tobytes())
print("wrote", sys.argv[1])
