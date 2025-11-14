import React from 'react';

import { Avatar } from '@chakra-ui/react';
import { Checkbox } from '@mediwareinc/wellsky-dls-react';
import './Transcript.scss';
import { PlayCircle, PauseCircle } from '@mediwareinc/wellsky-dls-react-icons';
import { AutoResizeTextarea } from './AutoResizeTextarea';

import { Sentence, TextSentence } from '../types';

type TranscriptProps = {
  blobUrl: string | null,
  sentences: Array<Sentence>,
  ongoing: Boolean,
  onInput: (text: string) => any,
};

const getSpeakerId = (speaker_tag: number) => {
  return speaker_tag === 0 ? 'unknown' : speaker_tag === 1 ? 1 : 2;
};

const getSpeakerAbbrev = (speaker_tag: number) => {
  return speaker_tag === 0 ? '?' : String.fromCharCode(64 + speaker_tag);
};

const Bubble: React.FC<{ blobUrl: string | null, textSentence: TextSentence, onChange: (s: string) => any }> = ({ blobUrl, textSentence, onChange }) => {
  const startStr = `${Math.floor(textSentence.start / 60)}:${Math.floor(textSentence.start % 60).toString().padStart(2, '0')}`;
  // const endStr = `${Math.floor(textSentence.end / 60)}:${Math.floor(textSentence.end % 60).toString().padStart(2, '0')}`;
  const audioEl = React.useRef<HTMLAudioElement>(null);
  const wordsEl = React.useRef<HTMLDivElement>(null);
  const [isPlaying, setIsPlaying] = React.useState<boolean>(false);

  const [text, setText] = React.useState<string>('');

  React.useEffect(() => {
    setText(textSentence.text);
  }, [textSentence]);

  const listen = React.useCallback(() => {
    if (blobUrl === null) {
      return;
    }
    if (audioEl.current === null) {
      return;
    }
    audioEl.current.play();
    audioEl.current.currentTime = textSentence.start;
    setIsPlaying(true);
  }, [textSentence.start, blobUrl]);
  const stop = React.useCallback(() => {
    if (audioEl.current === null || wordsEl.current === null) {
      return;
    }
    // wordsEl.current.querySelectorAll('[data-word-index]').forEach((el: any) => el.classList.remove('bubble-active-word'));
    audioEl.current.pause();
    setIsPlaying(false);
  }, []);
  const timeUpdated = React.useCallback((e: any) => {
    const time = e.target.currentTime;

    // let minDist = Infinity;
    // let wordIndex = -1;
    // words.forEach((word, index) => {
    //   const dist = Math.min(Math.abs(word.start - time), Math.abs(word.end - time));
    //   if (dist < minDist) {
    //     wordIndex = index;
    //     minDist = dist;
    //   }
    // });
    // // console.log(wordIndex);
    // if (wordsEl.current !== null) {
    //   wordsEl.current.querySelectorAll('[data-word-index]').forEach((el: any) => el.classList.remove('bubble-active-word'));
    //   if (wordIndex !== -1 && !audioEl.current?.paused) {
    //     const wordEl = wordsEl.current.querySelector(`[data-word-index="${wordIndex}"]`);
    //     if (wordEl !== null) {
    //       wordEl.classList.add('bubble-active-word');
    //     }
    //   }
    // }

    if (time > textSentence.end) {
      e.target.pause();
      setIsPlaying(false);
    }
  }, [textSentence.end]);
  const textEdited = React.useCallback((e: any) => {
    const text = e.target.innerText;
    setText(text);
    onChange(text);
  }, [onChange]);
  return (
    <div className={`bubble-ctn speaker-${getSpeakerId(textSentence.speaker_tag)}`}>
      <div className="bubble-left">
        <Avatar name={getSpeakerAbbrev(textSentence.speaker_tag)} size="sm" className="bubble-avatar" />
      </div>
      <div className="bubble-right">
        {textSentence.is_final && (
          <div className="bubble-header">
            <span className="bubble-speaker">Speaker {getSpeakerId(textSentence.speaker_tag)}</span>
            <span className="bubble-time">
              <span style={{ opacity: 0.75 }}>{startStr}</span>
              {blobUrl !== null && <button onClick={isPlaying ? stop : listen} className="bubble-button">{isPlaying ? <PauseCircle fontSize={32} /> : <PlayCircle fontSize={32} />}</button>}
            </span>
          </div>
        )}
        <div className="bubble-content">
          {/*<div className="bubble-speaker">Speaker {speaker_tag}</div>*/}
          {/*<div className="bubble-text" contentEditable={true} ref={wordsEl}>
            {words.map((word, i) => <><span data-word-index={i}>{word.text}</span><span> </span></>)}
          </div>*/}
          <div className="bubble-text" contentEditable={true} suppressContentEditableWarning={true} ref={wordsEl} onBlur={textEdited} >
            {text}
          </div>
        </div>
        {blobUrl !== null && <audio src={`${blobUrl}#t={start},{end}`} onTimeUpdate={timeUpdated} ref={audioEl}></audio>}
      </div>
    </div>
  );
};


const getTimeStr = (time: number) => {
  return `${Math.floor(time / 60)}:${Math.floor(time % 60).toString().padStart(2, '0')}`;
}


export const Transcript: React.FC<TranscriptProps> = ({ blobUrl, sentences: sourceSentences, ongoing, onInput }: TranscriptProps) => {
  const [textSentences, setTextSentences] = React.useState<Array<TextSentence>>([]);
  const [text, setText] = React.useState<string>('');
  const [raw, setRaw] = React.useState<boolean>(false);

  React.useEffect(() => {
    // Convert sourceSentences to array of TextSentence
    setTextSentences(sourceSentences.map(sentence => {
      const start = sentence.words[0].start;
      const end = sentence.words[sentence.words.length - 1].end;
      const speaker_tag = sentence.speaker_tag;
      const text = sentence.words.map(word => word.text).join(' ').replace(/\s+([,\.!\?])/g, '$1');
      const is_final = sentence.is_final;
      return { start, end, speaker_tag, text, is_final };
    }));
  }, [sourceSentences]);

  React.useEffect(() => {
    onInput(text);
  }, [text, onInput]);

  const rawTextChanged = React.useCallback((e: any) => {
    const text = e.target.value;
    // Parse text into array of Sentence, each line of format "Speaker [time]: words":
    const newTextSentences = text.split('\n').map((line: string) => {
      const match = line.match(/^([A-Z\?])\s*\[(\d+):(\d+)\]\s*:\s*(.*)$/);
      if (match) {
        const speaker_tag = match[1] === '?' ? 0 : match[1].charCodeAt(0) - 64;
        const start = parseInt(match[2]) * 60 + parseInt(match[3]);
        const text = match[4];
        // setSentences(sentences => [...sentences, { speaker_tag, words, is_final: true }]);
        return { speaker_tag, start, end: start + 1, text, is_final: true };
      }
      return null;
    }).filter((sentence: TextSentence | null) => sentence !== null);
    setTextSentences(newTextSentences);
  }, []);

  const bubbleTextChanged = React.useCallback((textSentence: TextSentence, text: string) => {
    setTextSentences(textSentences => textSentences.map(
      s => s === textSentence ? { ...s, text } : s
    ));
  }, []);

  React.useEffect(() => {
    setText(textSentences.map(textSentence => {
      const startStr = getTimeStr(textSentence.start);
      return `${getSpeakerAbbrev(textSentence.speaker_tag)} [${startStr}]: ${textSentence.text}`;
    }).join('\n'));
  }, [textSentences]);

  const bottomDiv = React.useRef<HTMLDivElement>(null);
  bottomDiv.current?.scrollIntoView({ behavior: 'smooth' });

  return (
    <div>
      {!ongoing && (
        <div style={{ margin: '0.5rem' }}>
          <Checkbox onChange={e => setRaw(e.target.checked)}>Raw text</Checkbox>
        </div>
      )}
      {!raw ? textSentences.map(textSentence => (
        <div>
          <Bubble blobUrl={blobUrl} textSentence={textSentence} onChange={bubbleTextChanged.bind(this, textSentence)} />
        </div>
      )) : <AutoResizeTextarea defaultValue={text} onBlur={rawTextChanged} />}
    </div>
  );

  // return (
  //   <>
  //     {ongoing ?
  //       (
  //         <div>
  //           {sentences.map(sentence => <div key={sentence.text} style={{ color: !ongoing ? '#000000' : sentence.is_final ? '#007700' : '#995500' }}>{sentence.speaker_tag !== '?' ? <strong>{`${speakerIcons[sentence.speaker_tag]}: `}</strong> : null}{sentence.text}</div>)}
  //         </div>
  //       ) : (
  //         <AutoResizeTextarea rows={4} value={text} onChange={(e: any) => setText(e.target.value)}></AutoResizeTextarea>
  //       )
  //     }
  //     <div ref={bottomDiv}></div>
  //   </>
  // );
};

