import React from 'react';
import {AbsoluteFill, Sequence} from 'remotion';
import {Clip, Lower, Scene, theme, timeline} from './kit';

// clips.json is written by scripts/cut-scenes.py: {"mark": seconds}. The scenes below fill a film from a capture tour.
// eslint-disable-next-line @typescript-eslint/no-var-requires
const clips: Record<string, number> = (() => { try { return require('./clips.json'); } catch { return {}; } })();

// One row per beat: what is on screen, what moves, why it is there. Durations in frames (30 fps); the dissolve overlap is applied by timeline().
const DEFS = [
	{id: 'search', dur: 240, title: 'Filter the composition', sub: 'By ingredient name, or by nutrient.',
		keys: [{f: 0, x: 900, y: 420, s: 1.0}, {f: 40, x: 760, y: 340, s: 1.4}, {f: 200, x: 900, y: 420, s: 1.15}, {f: 240, x: 900, y: 420, s: 1.15}]},
];
export const T = timeline(DEFS);
export const TOTAL = T.total;

export const Demo: React.FC = () => (
	<AbsoluteFill style={{background: theme.ground}}>
		{DEFS.map((d, i) => (
			<Sequence key={d.id} from={T.scenes[i].from} durationInFrames={d.dur}>
				<Scene dur={d.dur}>
					<Clip name={d.id} clipSeconds={clips[d.id] ?? 8} dur={d.dur} keys={d.keys} />
					<Lower n={String(i + 1).padStart(2, '0')} title={d.title} sub={d.sub} on={16} off={d.dur - 40} />
				</Scene>
			</Sequence>
		))}
	</AbsoluteFill>
);
