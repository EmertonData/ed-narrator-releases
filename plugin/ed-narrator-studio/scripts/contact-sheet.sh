#!/usr/bin/env bash
# One image of a film at chosen moments, to check a render without watching it.
# Usage: contact-sheet.sh <film> <out.jpg> <cols> <t1> <t2> ...   (times in seconds)
set -euo pipefail
FF="${FFMPEG:-$(command -v ffmpeg)}"; film="$1"; out="$2"; cols="$3"; shift 3
case "$film" in -*) film="./$film";; esac   # a leading - would read as an option
tmp="$(mktemp -d)"; i=0; : > "$tmp/list.txt"
for t in "$@"; do "$FF" -y -loglevel error -ss "$t" -protocol_whitelist file,pipe -i "$film" -frames:v 1 -vf scale=640:360 "$tmp/f$i.png"; echo "file f$i.png" >> "$tmp/list.txt"; i=$((i+1)); done
rows=$(( (i + cols - 1) / cols ))
"$FF" -y -loglevel error -f concat -safe 0 -i "$tmp/list.txt" -vf "tile=${cols}x${rows}" -frames:v 1 "$out"; rm -r "$tmp"; echo "$out"
