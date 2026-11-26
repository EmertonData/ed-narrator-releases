#!/usr/bin/env bash
# Put a music bed back under a narration track, ducked while the voice speaks, on the original video (video stream is copied).
# Use when the app's own music mix is not enough or did not reach the output (check: volumedetect in the gaps between cues).
# Usage: mix-narration.sh <film.mp4> <narration.wav> <music.wav|mp3> <out.mp4> [music_gain=0.26] [seconds]
set -euo pipefail
FF="${FFMPEG:-$(command -v ffmpeg)}"; film="$1"; narr="$2"; music="$3"; out="$4"; gain="${5:-0.26}"
for v in film narr music; do case "${!v}" in -*) printf -v "$v" ./%s "${!v}";; esac; done   # a leading - would read as an option
WL="-protocol_whitelist file,pipe"
# ffmpeg -i with no output exits non-zero: "|| true" keeps pipefail from aborting the duration probe
len="${6:-$( ("$FF" -hide_banner $WL -i "$film" 2>&1 || true) | awk -F'[:, ]+' '/Duration/{print int($3*3600+$4*60+$5+0.5)}')}"
"$FF" -y -loglevel error $WL -i "$film" $WL -i "$narr" $WL -i "$music" -filter_complex \
"[1:a]aformat=sample_rates=48000:channel_layouts=stereo,asplit=2[n1][n2];[2:a]aformat=sample_rates=48000:channel_layouts=stereo,volume=${gain}[m];[m][n1]sidechaincompress=threshold=0.012:ratio=8:attack=30:release=600:makeup=1[md];[md][n2]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[a]" \
-map 0:v -map "[a]" -c:v copy -c:a aac -b:a 256k -t "$len" "$out"
echo "mixed: $out"
echo "check the balance: voice windows should sit about 5-10 dB above the music-only gaps:"
echo "  $FF -hide_banner -ss <t> -t <s> -i $out -vn -af volumedetect -f null - 2>&1 | grep mean_volume"
