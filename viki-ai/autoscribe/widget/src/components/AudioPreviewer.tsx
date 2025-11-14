import React from 'react';

import { Sentence, Word } from '../types';

type AudioPreviewerProps = {
  sentences: Array<Sentence>
  blobUrl: string
};


export const AudioPreviewer: React.FC<AudioPreviewerProps> = ({ sentences, blobUrl }) => {
  const [[left, current, right], setActiveWords] = React.useState<Array<Array<Word>>>([[], [], []]);
  const timeUpdated = React.useCallback((e: any | null) => {
    const words = sentences.flatMap(sentence => sentence.words);
    const time = e !== null ? e.target.currentTime : 0;
    // Find index of word that's closest to current playback position
    let minDist = Infinity;
    let wordIndex = -1;
    words.forEach((word, index) => {
      const dist = Math.min(Math.abs(word.start - time), Math.abs(word.end - time));
      if (dist < minDist) {
        wordIndex = index;
        minDist = dist;
      }
    });
    if (wordIndex !== -1) {
      setActiveWords([
        words.slice(0, wordIndex), // left
        words.slice(wordIndex, wordIndex + 1),
        words.slice(wordIndex + 1),
      ]);
    }
  }, [sentences]);
  React.useEffect(() => {
    timeUpdated(null);
  }, [timeUpdated]);
  return (
    <div>
      <div style={{ display: 'flex', flexDirection: 'row', gap: '1rem', alignItems: 'center' }}>
        <div style={{ flex: 1, textAlign: 'right', overflow: 'hidden', whiteSpace: 'nowrap', position: 'relative', fontSize: '1.25rem' }}>
          <div style={{ float: 'right' }}>{left.map(x => x.text).join(' ')}</div>
          <div style={{ position: 'absolute', top: 0, bottom: 0, left: 0, right: 0, pointerEvents: 'none', background: 'linear-gradient(90deg, rgba(255,255,255,1) 0%, rgba(255,255,255,0) 75%, rgba(255,255,255,0) 100%)' }}></div>
        </div>
        <div style={{ flex: 0, textAlign: 'center', fontWeight: '700', fontSize: '1.75rem' }}>{current.map(x => x.text).join(' ')}</div>
        <div style={{ flex: 1, textAlign: 'left', overflow: 'hidden', whiteSpace: 'nowrap', position: 'relative', fontSize: '1.25rem' }}>
          {right.map(x => x.text).join(' ')}
          <div style={{ position: 'absolute', top: 0, bottom: 0, left: 0, right: 0, pointerEvents: 'none', background: 'linear-gradient(90deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0) 75%, rgba(255,255,255,1) 100%)' }}></div>
        </div>
      </div>
      <audio controls src={blobUrl} onTimeUpdate={timeUpdated} style={{ width: '100%' }}></audio>
    </div>
  );
};

