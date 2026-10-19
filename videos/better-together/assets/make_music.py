"""Synthesize the 30s piano + strings bed for "Better Together" (deterministic, offline).

Bar = 3.25s, so the halves lock together (19.5s) on the downbeat of bar 6,
where the progression resolves home to C major.
"""
import sys
import wave

import numpy as np

SR = 48000
DUR = 30.0
N = int(SR * DUR)
BAR = 3.25
EIGHTH = BAR / 8
rng = np.random.default_rng(7)


def hz(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)


def piano(midi, length=3.2, vel=0.3):
    t = np.arange(int(SR * length)) / SR
    f = hz(midi)
    out = np.zeros_like(t)
    for k, amp in enumerate([1.0, 0.5, 0.28, 0.16, 0.09, 0.05], start=1):
        inharm = 1 + 0.0004 * k * k
        decay = 1.8 / (1 + 0.6 * (k - 1)) * (1.4 if midi < 52 else 1.0)
        out += amp * np.sin(2 * np.pi * f * k * inharm * t) * np.exp(-t / decay)
    out *= np.minimum(1, t / 0.004)  # hammer attack
    out *= np.minimum(1, (length - t) / 0.3)  # release tail
    return vel * out / 2.2


def pad(midis, start, length, gain):
    t = np.arange(int(SR * length)) / SR
    out = np.zeros_like(t)
    for i, m in enumerate(midis):
        f = hz(m)
        vib = 1 + 0.0025 * np.sin(2 * np.pi * (4.6 + i * 0.3) * t)
        phase = 2 * np.pi * np.cumsum(f * vib) / SR
        out += np.sin(phase) + 0.25 * np.sin(2 * phase) + 0.1 * np.sin(3 * phase)
    env = np.minimum(1, t / 0.9) * np.minimum(1, (length - t) / 0.9)
    return start, gain * out * env / len(midis)


CHORDS = [
    ("Fmaj7", 41, [53, 57, 60, 64]),
    ("Cmaj7", 36, [52, 55, 59, 64]),
    ("Am7", 45, [52, 55, 60, 64]),
    ("Fmaj7", 41, [53, 57, 60, 64]),
    ("Dm7", 38, [53, 57, 60, 65]),
    ("Gsus", 43, [50, 55, 60, 62]),
    ("Cmaj7", 36, [52, 55, 59, 64]),  # the halves meet here
    ("Am7", 45, [52, 55, 60, 64]),
    ("Fmaj7", 41, [53, 57, 60, 64]),
    ("C", 36, [52, 55, 60, 64]),
]
PATTERN = [0, 1, 2, 3, 2, 1, 2, 3]
# melody (bar, beat-in-eighths, midi, length)
MELODY = [
    (6, 0, 76, 2.6), (6, 5, 74, 0.8), (6, 6, 72, 1.6),
    (7, 0, 72, 1.6), (7, 3, 71, 0.8), (7, 4, 69, 2.0),
    (8, 0, 69, 1.4), (8, 3, 67, 1.0), (8, 6, 72, 2.2),
    (9, 0, 76, 3.2),
]

L = np.zeros(N)
R = np.zeros(N)


def place(sig, start, pan=0.0):
    i = int(start * SR)
    if i >= N:
        return
    j = min(N, i + len(sig))
    L[i:j] += sig[: j - i] * (1 - pan) ** 0.5
    R[i:j] += sig[: j - i] * (1 + pan) ** 0.5


for b, (_, bass, arp) in enumerate(CHORDS):
    t0 = b * BAR
    lift = 1.0 if b < 6 else 1.18
    place(piano(bass, 3.6, 0.32 * lift), t0, -0.1)
    place(piano(bass + 12, 3.0, 0.12 * lift), t0 + EIGHTH * 4, -0.05)
    if b == 0:
        steps = [0, 2, 4, 6]  # a sparse first bar
    elif b == 9:
        steps = [0, 1, 2, 3]  # the last chord rolls once and rings
    else:
        steps = range(8)
    for s in steps:
        m = arp[PATTERN[s]]
        v = (0.16 if s % 2 else 0.2) * lift * (0.9 + 0.2 * rng.random())
        place(piano(m, 2.6, v), t0 + s * EIGHTH + rng.random() * 0.008, 0.15 * (PATTERN[s] - 1.5) / 1.5)
    st, sig = pad([bass + 12] + arp, t0, BAR + 1.0, 0.05 if b < 6 else 0.085)
    place(sig, st)

for bar, e, m, ln in MELODY:
    place(piano(m, ln + 1.6, 0.3), bar * BAR + e * EIGHTH, 0.1)

# Room: convolve with a short decaying-noise impulse per channel (FFT convolution).
def reverb(x, seed):
    r = np.random.default_rng(seed)
    n = int(SR * 2.8)
    ir = r.standard_normal(n) * np.exp(-np.arange(n) / (SR * 0.7))
    ir[: int(SR * 0.012)] = 0
    size = 1 << int(np.ceil(np.log2(len(x) + n)))
    y = np.fft.irfft(np.fft.rfft(x, size) * np.fft.rfft(ir, size), size)[: len(x)]
    return y / (np.max(np.abs(y)) + 1e-9) * np.max(np.abs(x))


wetL, wetR = reverb(L, 1), reverb(R, 2)
L = 0.78 * L + 0.42 * wetL
R = 0.78 * R + 0.42 * wetR

t = np.arange(N) / SR
fade = np.minimum(1, t / 0.8) * np.clip((DUR - t) / 1.4, 0, 1)
L *= fade
R *= fade
peak = max(np.max(np.abs(L)), np.max(np.abs(R)))
L, R = L / peak * 0.89, R / peak * 0.89
stereo = (np.stack([L, R], axis=1) * 32767).astype(np.int16)
with wave.open(sys.argv[1], "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(stereo.tobytes())
print("wrote", sys.argv[1])
