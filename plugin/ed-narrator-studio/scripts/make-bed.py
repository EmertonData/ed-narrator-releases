#!/usr/bin/env python3
"""A calm, original music bed (pads, soft sub, a gentle arpeggio, a very soft pulse) generated from scratch: no licence to clear.
Usage: make-bed.py <seconds> <out.wav> [accent times as JSON list, e.g. "[12.5,30]"]
Accents are soft bell notes: put them on scene changes. Pure Python, no dependencies. For the user's own track, use that instead."""
import array, json, math, random, sys, wave

DUR = float(sys.argv[1]); OUT = sys.argv[2]; ACC = json.loads(sys.argv[3]) if len(sys.argv) > 3 else []
random.seed(11); SR = 44100; N = int(SR * DUR); TAU = 2 * math.pi
L = array.array("f", [0.0]) * N; R = array.array("f", [0.0]) * N
def add(t0, buf, gl=1.0, gr=1.0):
    i0 = int(t0 * SR)
    for i, v in enumerate(buf):
        j = i0 + i
        if 0 <= j < N: L[j] += v * gl; R[j] += v * gr
mid = lambda n: 440 * 2 ** ((n - 69) / 12)
CH = [[57, 60, 64, 67], [53, 57, 60, 64], [60, 64, 67, 71], [55, 59, 62, 67]]; ROOT = [33, 29, 36, 31]; BAR = 4.0
for bi in range(int(math.ceil(DUR / BAR))):                         # pads: one chord per bar, overlapped
    t0 = bi * BAR - 0.8; t1 = t0 + BAR + 1.6; lvl = 0.10 if bi < 2 else 0.15
    for i in range(int((t1 - t0) * SR)):
        t = t0 + i / SR; j = int(t * SR)
        if not 0 <= j < N: continue
        env = min(1, (t - t0) / 1.4) * min(1, (t1 - t) / 1.4); tr = 0.85 + 0.15 * math.sin(TAU * 0.18 * t); sl = sr = 0.0
        for nn in CH[bi % 4]:
            f0 = mid(nn); sl += math.sin(TAU * f0 * 0.998 * t) + 0.25 * math.sin(TAU * f0 * 2 * 0.998 * t); sr += math.sin(TAU * f0 * 1.002 * t) + 0.25 * math.sin(TAU * f0 * 2 * 1.002 * t)
        L[j] += sl * env * tr * lvl / 4; R[j] += sr * env * tr * lvl / 4
    f0 = mid(ROOT[bi % 4])                                           # soft sub root
    for i in range(int(BAR * SR)):
        t = bi * BAR + i / SR; j = int(t * SR)
        if j >= N: break
        v = math.sin(TAU * f0 * t) * 0.16 * min(1, (i / SR) / 0.6) * min(1, (BAR - i / SR) / 0.6) * (0.5 if bi < 2 else 1.0); L[j] += v; R[j] += v
def pluck(t, f0, g):
    add(t, [(math.sin(TAU * f0 * i / SR) + 0.3 * math.sin(TAU * f0 * 2 * i / SR)) * math.exp(-(i / SR) * 5.5) * 0.11 * g for i in range(int(0.9 * SR))], 0.6 + 0.4 * random.random(), 0.6 + 0.4 * random.random())
def bell(t, f0, g=1.0, dur=3.0):
    b = [(math.sin(TAU * f0 * i / SR) + 0.4 * math.sin(TAU * f0 * 2.76 * i / SR)) * math.exp(-(i / SR) * 1.8) * 0.09 * g for i in range(int(dur * SR))]; add(t, b, 0.8, 1.0); add(t + 0.02, b, 0.5, 0.9)
t, k = 6.0, 0
while t < DUR - 4: pluck(t, mid(CH[int(t // BAR) % 4][k % 4] + 12), 0.8 if t < 20 else 1.0); k += 1; t += 0.5
t = 14.0
while t < DUR - 6:                                                  # very soft pulse: felt, not heard
    add(t, [math.sin(TAU * (45 * i / SR + 70 * (1 - math.exp(-24 * i / SR)) / 24)) * math.exp(-(i / SR) * 9) * 0.30 for i in range(int(0.35 * SR))]); t += 1.0
for a in ACC: bell(a, mid(81), 0.9)
bell(max(0, DUR - 6.0), mid(88), 1.1, 4.5)
peak = 0.0
for i in range(N):
    t = i / SR; f = min(1.0, t / 1.5) * min(1.0, (DUR - t) / 3.0)
    L[i] = math.tanh(L[i] * 1.2) * f; R[i] = math.tanh(R[i] * 1.2) * f; peak = max(peak, abs(L[i]), abs(R[i]))
g = 0.85 / peak; w = wave.open(OUT, "wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); o = array.array("h")
for i in range(N): o.append(int(L[i] * g * 32767)); o.append(int(R[i] * g * 32767))
w.writeframes(o.tobytes()); w.close(); print("ok", OUT, DUR, "s")
