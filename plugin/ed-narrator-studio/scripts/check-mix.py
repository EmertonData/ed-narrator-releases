#!/usr/bin/env python3
"""Voice-to-music ratio for every cue of a finished film: the voice must sit clear of the music, or the narration is hard to follow.
Usage: check-mix.py <voiced film> <script.srt> [ffmpeg]
For each cue it measures the mean level while the cue speaks and in the gap just before it (music only), and reports the margin in dB.
Rule of thumb: 5 dB or more is fine, under 3 dB is hard to follow. When it fails, lower the music (mix-narration.sh music_gain) or open the app's Music mix panel."""
import re, shutil, subprocess, sys

film, srt = sys.argv[1], sys.argv[2]; ff = sys.argv[3] if len(sys.argv) > 3 else shutil.which("ffmpeg")
if not ff: sys.exit("ffmpeg not found: pass its path as the third argument")
sec = lambda s: int(s[:2]) * 3600 + int(s[3:5]) * 60 + int(s[6:8]) + int(s[9:12]) / 1000
def level(t, d):
    r = subprocess.run([ff, "-hide_banner", "-ss", f"{t:.3f}", "-t", f"{d:.3f}", "-i", film, "-vn", "-af", "volumedetect", "-f", "null", "-"], capture_output=True, text=True)
    m = re.search(r"mean_volume: (-?[\d.]+) dB", r.stderr); return float(m.group(1)) if m else None
cues = re.findall(r"(\d+)\n(\d\d:\d\d:\d\d,\d{3}) --> (\d\d:\d\d:\d\d,\d{3})\n(.+)", open(srt).read())
worst = 99.0
for n, a, b, text in cues:
    a, b = sec(a), sec(b); v = level(a + 0.2, max(0.5, b - a - 0.4)); g = level(max(0, a - 0.9), 0.7) if a > 1 else None
    margin = None if (v is None or g is None or g < -80) else v - g
    note = "no music-only gap to compare (silence before the cue)" if g is not None and g < -80 else ""
    if margin is not None: worst = min(worst, margin)
    print(f"cue {int(n):2d} {a:6.1f}s  voice {v} dB  gap {g} dB  margin {'n/a' if margin is None else f'{margin:+.1f} dB'} {note}")
print("worst margin:", "n/a" if worst == 99.0 else f"{worst:+.1f} dB", "(5+ fine, under 3 hard to follow)")
