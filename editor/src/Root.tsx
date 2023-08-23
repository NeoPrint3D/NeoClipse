import { Composition, staticFile } from 'remotion';
import { MainComposition } from './MainComposition';
import './style.css';
import { useAudioData } from '@remotion/media-utils';

const fps = 30;

export const RemotionRoot: React.FC = () => {
	const audioData = useAudioData(staticFile('voice.mp3'));
	if (!audioData) {
		return null;
	}

	const audioDuration = Math.round(audioData.durationInSeconds + 2.5);
	return (
		<>
			<Composition
				id="Main"
				component={MainComposition}
				durationInFrames={fps * audioDuration}
				fps={fps}
				width={1078}
				height={1920}
			/>
		</>
	);
};
