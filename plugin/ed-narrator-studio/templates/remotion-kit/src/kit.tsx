// A small motion kit for demo films: a camera rig over recorded footage, soft scene dissolves, understated lower-thirds.
// House rules (see docs/motion-design-playbook.md): every frame is a pure function of the frame number (no Math.random, no CSS animations);
// nothing appears from nowhere (it slides, grows or is revealed); exits before entries; smooth settles, no bounce; no glows, particle bursts or corner labels.
import React from 'react';
import {AbsoluteFill, Easing, OffthreadVideo, continueRender, delayRender, interpolate, staticFile, useCurrentFrame} from 'remotion';

/* ---------- theme: take these from the app (scripts/extract-brand.mjs), never invent them ---------- */
export const theme = {ground: '#0B1220', accent: '#8F8FFF', text: '#FFFFFF', muted: 'rgba(255,255,255,.72)', display: 'system-ui, sans-serif', sans: 'system-ui, sans-serif', mono: 'ui-monospace, Menlo, monospace'};

/* ---------- timing ---------- */
export const eOut = Easing.bezier(0.16, 1, 0.3, 1);   // fast in, long settle: entries
export const eIO = Easing.bezier(0.76, 0, 0.24, 1);   // camera moves and fades
export const eIn = Easing.bezier(0.7, 0, 0.84, 0);    // exits
export const p = (f: number, a: number, b: number, e: (t: number) => number = eOut) => interpolate(f, [a, b], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: e});
export const lerp = (a: number, b: number, t: number) => a + (b - a) * t;

/** Load brand fonts before the first frame: [{family, file (in public/), weight}]. */
export const loadFonts = (fonts: {family: string; file: string; weight?: string}[]) => {
	const h = delayRender('fonts');
	Promise.all(fonts.map((f) => new FontFace(f.family, `url(${staticFile(f.file)})`, {weight: f.weight ?? '400'}).load().then((ff) => document.fonts.add(ff)))).then(() => continueRender(h));
};

/* ---------- camera: pan and zoom over a 1920x1080 plane, a hold between moves, a little handheld drift ---------- */
export type Key = {f: number; x: number; y: number; s: number};
export const Stage: React.FC<{keys: Key[]; drift?: number; children: React.ReactNode}> = ({keys, drift = 0.5, children}) => {
	const f = useCurrentFrame();
	const g = (sel: (k: Key) => number) => interpolate(f, keys.map((k) => k.f), keys.map(sel), {easing: eIO, extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
	const s = Math.max(1, g((k) => k.s));
	// The point (x, y) of the plane lands at the screen centre at zoom s. Clamped so the plane always covers the screen: a focus too near
	// an edge would show a black band, which is the most common camera bug.
	const x = Math.min(1920 - 960 / s, Math.max(960 / s, g((k) => k.x))), y = Math.min(1080 - 540 / s, Math.max(540 / s, g((k) => k.y)));
	const hx = (Math.sin(f * 0.045) * 3 + Math.sin(f * 0.11) * 1.5) * drift, hy = Math.cos(f * 0.037) * 2.5 * drift;
	return (
		<AbsoluteFill style={{overflow: 'hidden'}}>
			<div style={{position: 'absolute', left: 0, top: 0, width: 1920, height: 1080, transformOrigin: '0 0', transform: `translate(${960 - x * s + hx}px,${540 - y * s + hy}px) scale(${s})`}}>{children}</div>
		</AbsoluteFill>
	);
};

/* ---------- scenes: neighbours overlap by FADE frames, which reads as a soft dissolve ---------- */
export const FADE = 12;
export const Scene: React.FC<{dur: number; children: React.ReactNode}> = ({dur, children}) => {
	const f = useCurrentFrame();
	return <AbsoluteFill style={{opacity: p(f, 0, FADE, eIO) * (1 - p(f, dur - FADE, dur, eIO)), background: theme.ground}}>{children}</AbsoluteFill>;
};
export type Def = {id: string; dur: number};
/** Start frame of every scene and the total length, with the overlap applied. */
export const timeline = (defs: Def[]) => {
	const out: {id: string; from: number; dur: number}[] = [];
	defs.forEach((d, i) => out.push({id: d.id, from: i === 0 ? 0 : out[i - 1].from + out[i - 1].dur - FADE, dur: d.dur}));
	const last = out[out.length - 1];
	return {scenes: out, total: last.from + last.dur};
};

/* ---------- recorded footage ---------- */
/** A cut-scenes.py clip, sped up or slowed down to fill its scene exactly. clipSeconds comes from clips.json. */
export const Clip: React.FC<{name: string; clipSeconds: number; dur: number; keys: Key[]; children?: React.ReactNode}> = ({name, clipSeconds, dur, keys, children}) => {
	// Land the last frame at (or just past) the scene end: a clip that ends early renders a glitch frame (scan-pops.py finds it).
	const rate = Math.min(2.4, Math.max(0.75, (clipSeconds / (dur / 30)) * 0.97));
	return (
		<>
			<Stage keys={keys}><OffthreadVideo src={staticFile(`clips/${name}.mp4`)} playbackRate={rate} muted style={{position: 'absolute', left: 0, top: 0, width: 1920, height: 1080}} /></Stage>
			{children}
		</>
	);
};

/* ---------- captions: number, one short title, one line of detail ---------- */
export const Lower: React.FC<{n: string; title: string; sub?: string; on: number; off: number}> = ({n, title, sub, on, off}) => {
	const f = useCurrentFrame();
	const t = p(f, on, on + 16) * (1 - p(f, off, off + 14, eIn));   // the old caption is gone before the next scene's caption enters
	if (t <= 0.001) return null;
	return (
		<div style={{position: 'absolute', left: 80, bottom: 70, opacity: t, transform: `translateY(${(1 - t) * 14}px)`, display: 'flex', alignItems: 'center', gap: 26, padding: '22px 34px 22px 26px', borderRadius: 18, background: 'rgba(11,18,32,.92)', border: '1px solid rgba(255,255,255,.08)'}}>
			<div style={{fontFamily: theme.mono, fontSize: 20, color: theme.accent, letterSpacing: '0.1em', padding: '6px 12px', borderRadius: 8, background: 'rgba(143,143,255,.14)'}}>{n}</div>
			<div>
				<div style={{fontFamily: theme.display, fontWeight: 700, fontSize: 40, color: theme.text, lineHeight: 1.1}}>{title}</div>
				{sub ? <div style={{fontFamily: theme.sans, fontSize: 22, color: theme.muted, marginTop: 6}}>{sub}</div> : null}
			</div>
		</div>
	);
};

/* ---------- spotlight: dims everything but one region (a rectangle of the 1920x1080 plane) ---------- */
export const Spot: React.FC<{rect: {f: number; x: number; y: number; w: number; h: number}[]; on: number; off: number}> = ({rect, on, off}) => {
	const f = useCurrentFrame(); const fr = rect.map((r) => r.f);
	const g = (sel: (r: (typeof rect)[0]) => number) => interpolate(f, fr, rect.map(sel), {easing: eIO, extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
	const op = p(f, on, on + 12) * (1 - p(f, off, off + 12));
	if (op <= 0.001) return null;
	return <div style={{position: 'absolute', left: g((r) => r.x), top: g((r) => r.y), width: g((r) => r.w), height: g((r) => r.h), borderRadius: 14, boxShadow: `0 0 0 4000px rgba(6,7,13,${0.6 * op}), 0 0 0 3px rgba(143,143,255,${op})`}} />;
};

/* ---------- the real logo: shapes from scripts/extract-brand.mjs; the mark settles first, then the letters slide in ---------- */
export const Logo: React.FC<{shapes: {d: string; fillRule?: string; transform?: string}[]; viewBox: string; width: number; fill?: string; at?: number}> = ({shapes, viewBox, width, fill = '#fff', at = 0}) => {
	const f = useCurrentFrame(); const [x, y, w, h] = viewBox.split(' ').map(Number);
	return (
		<svg width={width} height={(width * h) / w} viewBox={viewBox} style={{overflow: 'visible'}}>
			{shapes.map((s, i) => { const t = p(f, at + i * 1.5, at + 14 + i * 1.5); return <path key={i} d={s.d} fillRule={s.fillRule as any} fill={fill} opacity={t} transform={`translate(${(t - 1) * 30} 0) ${s.transform ?? ''}`} />; })}
		</svg>
	);
};
void interpolate;
