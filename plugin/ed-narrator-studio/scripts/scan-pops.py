#!/usr/bin/env python3
"""Scan a film for single-frame pops (one frame that jumps out and back: a flicker, a stale frame, a layout glitch) and list its hard cuts.
Usage: scan-pops.py <film> [ffmpeg]      Reads 64x36 gray frames, so it is fast and needs no dependencies.
Pop = a big change into frame i and a big change out, while frames i-1 and i+1 look alike. Hard cut = a big change that stays.
Review each reported time with transition-strip.sh before deciding: a pop at a deliberate flash is intended, anywhere else it is a bug."""
import shutil, subprocess, sys

film = sys.argv[1]; ff = sys.argv[2] if len(sys.argv) > 2 else shutil.which("ffmpeg")
if not ff: sys.exit("ffmpeg not found: pass its path as the second argument")
W, H, FPS = 64, 36, 30; N = W * H
p = subprocess.Popen([ff, "-loglevel", "error", "-i", film, "-vf", f"fps={FPS},scale={W}:{H},format=gray", "-f", "rawvideo", "-"], stdout=subprocess.PIPE)
frames = []
while True:
    b = p.stdout.read(N)
    if len(b) < N: break
    frames.append(b)
d = lambda a, b: sum(abs(x - y) for x, y in zip(a, b)) / N
diffs = [d(frames[i], frames[i + 1]) for i in range(len(frames) - 1)]
T = 18.0  # mean gray-level change that counts as "big" on a 0-255 scale
pops, cuts = [], []
for i in range(1, len(frames) - 1):
    if diffs[i - 1] > T and diffs[i] > T and d(frames[i - 1], frames[i + 1]) < T / 3: pops.append(i)
    elif diffs[i - 1] > T * 1.6 and diffs[i] < T / 4: cuts.append(i)
fmt = lambda i: f"{i / FPS:6.2f}s (frame {i})"
print(f"{len(frames)} frames, {len(frames) / FPS:.1f}s")
print(f"single-frame pops: {len(pops)}"); [print("  pop ", fmt(i)) for i in pops]
print(f"hard cuts: {len(cuts)}"); [print("  cut ", fmt(i)) for i in cuts]
