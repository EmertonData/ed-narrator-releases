#!/usr/bin/env python3
"""Cut a capture-tour into one constant-30-fps clip per marked scene.
Usage: cut-scenes.py <capture dir with meta.json> <output dir for clips> [ffmpeg]
Writes <output>/<mark>.mp4 (1920x1080, yuv420p, no audio) and <output>/clips.json {mark: seconds}."""
import bisect, json, os, shutil, subprocess, sys

src, dst = sys.argv[1], sys.argv[2]
ff = sys.argv[3] if len(sys.argv) > 3 else shutil.which("ffmpeg")
if not ff: sys.exit("ffmpeg not found: pass its path as the third argument")
meta = json.load(open(os.path.join(src, "meta.json"))); frames = meta["frames"]; times = [f["t"] for f in frames]
os.makedirs(dst, exist_ok=True); info = {}
for name, m in meta["marks"].items():
    s, e = m["start"], m.get("end", meta["END"]); n = int((e - s) * 30)
    p = subprocess.Popen([ff, "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", "30", "-c:v", "mjpeg", "-i", "pipe:0",
        "-vf", "scale=1920:1080:in_range=pc:out_range=tv:flags=bicubic,format=yuv420p", "-r", "30", "-c:v", "libx264", "-crf", "17", "-preset", "medium", "-g", "30", "-an",
        os.path.join(dst, f"{name}.mp4")], stdin=subprocess.PIPE)
    for i in range(n):  # the screencast only emits a frame when the page changes: repeat the last one to get a constant rate
        j = max(0, bisect.bisect_right(times, s + i / 30) - 1); p.stdin.write(open(frames[j]["file"], "rb").read())
    p.stdin.close(); p.wait(); info[name] = round(e - s, 2); print(name, info[name], "s")
json.dump(info, open(os.path.join(dst, "clips.json"), "w"))
