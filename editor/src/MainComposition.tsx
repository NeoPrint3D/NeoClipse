import { staticFile } from 'remotion';
import { AudiogramComposition } from './Composition';

export const MainComposition = () => {
	return (
		<div className="bg-black w-screen">
			<AudiogramComposition
				audioOffsetInFrames={0}
				source={staticFile('subtitle.srt')}
			/>
		</div>
	);
};
