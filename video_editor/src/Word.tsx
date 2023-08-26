import { Easing } from 'remotion';
import { interpolate } from 'remotion';
import React from 'react';
import { loadFont } from '@remotion/google-fonts/Poppins';
import { SubtitleItem } from 'parse-srt';

const { fontFamily } = loadFont();

export const Word: React.FC<{
	item: SubtitleItem;
	frame: number;
}> = ({ item, frame }) => {
	const opacity = interpolate(frame, [item.start, item.start + 15], [0, 1], {
		extrapolateLeft: 'clamp',
		extrapolateRight: 'clamp',
	});

	const translateY = interpolate(frame, [item.start, item.start + 15], [0, 1], {
		easing: Easing.out(Easing.cubic),
		extrapolateLeft: 'clamp',
		extrapolateRight: 'clamp',
	});

	const scale = interpolate(frame, [item.start, item.start + 1], [0, 1], {
		easing: Easing.out(Easing.quad),
		extrapolateLeft: 'clamp',
		extrapolateRight: 'clamp',
	});

	return (
		<span
			className="text-center text-7xl text-white font-bold mx-auto"
			style={{
				display: 'inline-block',
				opacity,
				fontFamily,
				scale,
				translate: `0 -${translateY}em`,
			}}
		>
			{item.text.toUpperCase()}
		</span>
	);
};
