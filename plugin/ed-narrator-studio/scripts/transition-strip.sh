#!/usr/bin/env bash
# Every frame around a moment as one strip: a transition lasts a fraction of a second, so one still per second never shows how it happens.
# Usage: transition-strip.sh <film> <seconds> <out.jpg> [half-window=0.3] [fps=30]   (frames from t-w to t+w, 6 per row)
set -euo pipefail
FF="${FFMPEG:-$(command -v ffmpeg)}"; film="$1"; t="$2"; out="$3"; w="${4:-0.3}"; fps="${5:-30}"
case "$film" in -*) film="./$film";; esac   # a leading - would read as an option
start=$(awk -v t="$t" -v w="$w" 'BEGIN{s=t-w; if(s<0)s=0; print s}'); dur=$(awk -v w="$w" 'BEGIN{print 2*w}')
n=$(awk -v d="$dur" -v f="$fps" 'BEGIN{printf "%d", d*f}'); rows=$(( (n + 5) / 6 ))
"$FF" -y -loglevel error -ss "$start" -t "$dur" -protocol_whitelist file,pipe -i "$film" -vf "fps=$fps,scale=320:180,drawtext=text='%{pts\:hms}':x=6:y=6:fontcolor=white:box=1:boxcolor=black@0.5:fontsize=14,tile=6x${rows}" -frames:v 1 "$out" 2>/dev/null \
 || "$FF" -y -loglevel error -ss "$start" -t "$dur" -protocol_whitelist file,pipe -i "$film" -vf "fps=$fps,scale=320:180,tile=6x${rows}" -frames:v 1 "$out"   # some ffmpeg builds have no drawtext
echo "$out"
