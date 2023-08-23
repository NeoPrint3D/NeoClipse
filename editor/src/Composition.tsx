import { useAudioData, visualizeAudio } from '@remotion/media-utils';
import React, { useEffect, useRef, useState } from 'react';
import {
	AbsoluteFill,
	Audio,
	continueRender,
	delayRender,
	interpolate,
	Sequence,
	staticFile,
	useCurrentFrame,
	useVideoConfig,
	Video,
} from 'remotion';
import { PaginatedSubtitles } from './Subtitles';

const AudioViz = () => {
	const frame = useCurrentFrame();
	const { fps } = useVideoConfig();
	const audioData = useAudioData(staticFile('voice.mp3'));

	if (!audioData) {
		return null;
	}

	const allVisualizationValues = visualizeAudio({
		fps,
		frame,
		audioData,
		numberOfSamples: 256, // Use more samples to get a nicer visualisation
	});

	// Pick the low values because they look nicer than high values
	// feel free to play around :)
	const visualization = allVisualizationValues.slice(8, 22);

	const mirrored = [...visualization.slice(1).reverse(), ...visualization];

	return (
		<div className="flex items-center gap-3 justify-center mx-auto ">
			{mirrored.map((v, i) => {
				return (
					<div
						key={i}
						className="bg-gradient-to-tr from-red-500/90 via-purple-500 to-blue-500/90 w-6 rounded-lg"
						style={{
							height: `${1000 * Math.sqrt(v) + 1}px`,
						}}
					/>
				);
			})}
		</div>
	);
};

export const AudiogramComposition: React.FC<{
	source: string;
	audioOffsetInFrames: number;
}> = ({ source, audioOffsetInFrames }) => {
	const { durationInFrames } = useVideoConfig();

	const [handle] = useState(() => delayRender());
	const [subtitles, setSubtitles] = useState<string | null>(null);
	const frame = useCurrentFrame();

	const opacity = interpolate(
		frame,
		[0, 20, durationInFrames - 20, durationInFrames],
		[1, 0, 0, 1]
	);
	const ref = useRef<HTMLDivElement>(null);

	const fadeInRef = useRef<HTMLDivElement>(null);

	useEffect(() => {
		fetch(source)
			.then((res) => res.text())
			.then((text) => {
				setSubtitles(text);
				continueRender(handle);
			})
			.catch((err) => {
				console.log('Error fetching subtitles', err);
			});
	}, [handle, source]);

	if (!subtitles) {
		return null;
	}

	return (
		<div ref={ref}>
			<Sequence from={-audioOffsetInFrames}>
				<AbsoluteFill>
					<div
						ref={fadeInRef}
						className="h-full w-full bg-black/90 z-50 backdrop-blur-3xl"
						style={{ opacity }}
					/>
				</AbsoluteFill>
				<Audio src={staticFile('voice.mp3')} volume={1} />
				<Audio loop src={staticFile('music.mp3')} volume={0.1} />
				<AbsoluteFill>
					<Video loop src={staticFile('background.mp4')} playbackRate={0.75} />
				</AbsoluteFill>
				<AbsoluteFill>
					<div className="bg-black/60 w-full h-full" />
				</AbsoluteFill>
				<AbsoluteFill>
					<div className="flex items-center w-full h-full">
						<PaginatedSubtitles
							subtitles={subtitles}
							startFrame={0}
							endFrame={durationInFrames}
							linesPerPage={1}
						/>
					</div>
				</AbsoluteFill>
				<AbsoluteFill>
					<div className="flex items-end h-full w-full justify-center">
						<div className="flex items-center h-32 bg-black/20 backdrop-blur-3xl px-5 rounded-full mb-80">
							<AudioViz />
						</div>
					</div>
				</AbsoluteFill>
			</Sequence>
		</div>
	);
};
