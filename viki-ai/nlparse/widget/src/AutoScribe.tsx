import React from 'react';

// import css from './AutoScribe.css';
import './AutoScribe.css';

import { FloatButton } from 'antd';
import { AudioOutlined, SettingOutlined } from '@ant-design/icons';
import { PrimaryButton, SecondaryButton, LinkButton, Grid, Popover, Select, TextArea, CustomSideDrawer } from '@mediwareinc/wellsky-dls-react';
import { Badge } from '@chakra-ui/react';
import { Microphone, CheckSimple } from '@mediwareinc/wellsky-dls-react-icons';

import { useMicrophone, RecordingState } from './hooks/microphone';
import useEnvJson from './hooks/useEnvJson';
import { Env, Sentence, Word } from './types';
import { BackendSelector } from './components/BackendSelector';
import { ModelSelector } from './components/ModelSelector';
import { Transcript } from './components/Transcript';
import { AudioPreviewer } from './components/AudioPreviewer';

type AutoscribeProps = {
  onOpen?: () => void;
  onConfirm?: (text: string) => void;
};

export function AutoScribeWidget({ onConfirm }: AutoscribeProps) {
  const { start, stop, reset, state, blobUrl } = useMicrophone();
  const [sentences, setSentences] = React.useState<Array<Sentence>>([]);
  const ws = React.useRef<null | WebSocket>(null);
  const [text, setText] = React.useState<string>('');
  const [error, setError] = React.useState<string>('');
  const [backend, setBackend] = React.useState<string>('google_v1');
  const [model, setModel] = React.useState<string>('medical_conversation');
  const [showRecording, setShowRecording] = React.useState<boolean>(false);
  const env = useEnvJson<Env>();

  const toggleShowRecording = React.useCallback(() => setShowRecording(v => !v), []);

  React.useEffect(() => {
    // css.use({target: root});
  }, []);

  const stopRecording = React.useCallback(() => {
    stop(() => {
      if (!ws.current) {
        return;
      }
      ws.current.close();
      ws.current = null;
    });
  }, [stop]);

  const startRecording = React.useCallback(() => {
    setSentences([{ words: [{text: '...', start: 0, end: 0}], is_final: false, speaker_tag: 0 }]);
    setError('');
    let queue: Array<Blob> = [];
    if (env === null) {
      return;
    }
    start(() => {
      const url = new URL(env.API_URL);
      const host = url.host;
      const proto = url.protocol === 'https:' ? 'wss:' : 'ws:';
      ws.current = new WebSocket(`${proto}//${host}/ws/transcribe/`);
      ws.current.onopen = () => {
        if (!ws.current) {
          return;
        }
        const metadata = {
          'token': 'todo-send-okta-jwt-token-here',
          'backend': backend,
          'model': model,
        };
        console.log('WebSocket opened, sending metadata', metadata);
        // Send metadata
        ws.current.send(JSON.stringify(metadata));
        queue.forEach(blob => blob.size && (ws.current as any).send(blob));
        setSentences([{ words: [{text: '...', start: 0, end: 0}], is_final: false, speaker_tag: 0 }]);
        ws.current.onmessage = message => {
          const data = JSON.parse(message.data);
          if (data.type === 'recognition') {
            setSentences(sentences => sentences.filter(s => s.is_final).concat({words: [{text: data.transcript, start: 0, end: 0}], is_final: false, speaker_tag: 0}));
            // if (data.is_final) {
            //   setSentences(sentences => sentences.filter(sentence => sentence.is_final).concat({ words: data.words, is_final: true, speaker_tag: '?' }, { words: [{text: '...', start: 0, end: 0, speaker_tag: '0'}], is_final: false, speaker_tag: '?' }));
            // } else {
            // setSentences(sentences => sentences.filter(sentence => sentence.is_final).concat({ words: data.words, is_final: false, speaker_tag: '?' }));
            // }
          } else if (data.type === 'diarization') {
            setSentences(data.sentences.map((sentence: any) => ({...sentence, is_final: true})));
            // setSentences(sentences => sentences.filter(s => s.is_final).concat({words: data.words, is_final: true, speaker_tag: data.speaker_tag}));
            // setSentences(data.sentences.map((sentence: any) => ({ text: sentence.words.join(' '), is_final: true, speaker_tag: sentence.speaker_tag })));
          } else if (data.type === 'error') {
            stopRecording();
            setError(data.message);
          }
        };
      };
      ws.current.onerror = () => {
        stopRecording();
        setError('Connection error');
      };
    }, blob => {
      if (!ws.current) {
        return;
      }
      if (ws.current.readyState === WebSocket.OPEN) {
        if (blob.size) {
          ws.current.send(blob);
        }
      } else {
        queue.push(blob);
      }
    });
  }, [start, env, stopRecording, backend, model]);

  const confirmRequested = React.useCallback(() => {
    setSentences([]);
    setText('');
    reset();
    if (typeof onConfirm !== 'undefined') {
      onConfirm(text);
    }
  }, [onConfirm, reset, text]);

  if (!env) {
    return <div>Loading configuration...</div>;
  }

  return (
    <>
      <div style={{ display: 'flex', flexDirection: 'column', height: '100%', gap: '1rem' }}>
        <div style={{ flex: 1, overflowY: 'auto', paddingBottom: '2rem' }}>
          <div style={{ float: 'right' }}>
            <Popover title="Settings" content={(
              <div style={{ /*minWidth: '30vw'*/ }}>
                <Grid gap={1} templateColumns='repeat(4, 1fr)'>
                  <Grid.Item colSpan={4}>
                    Version: <Badge colorScheme="blue">{env.VERSION.length === 40 ? env.VERSION.substr(0, 7) : env.VERSION}</Badge>
                  </Grid.Item>
                  <Grid.Item colSpan={4}>
                    <BackendSelector onChange={setBackend} />
                  </Grid.Item>
                  <Grid.Item colSpan={4}>
                    <ModelSelector onChange={setModel} />
                  </Grid.Item>
                </Grid>
              </div>
            )} trigger="click">
              <LinkButton><SettingOutlined /></LinkButton>
            </Popover>
          </div>
          <div style={{ textAlign: 'center', margin: '1rem', minHeight: '2rem' }}>
            {state === RecordingState.IDLE && (
              <div>
                <div>Press the record button at the bottom to start recognizing your speech.</div>
              </div>
            )}
            {state === RecordingState.RECORDING && (
              <div>
                <div style={{ marginBottom: '0.5rem' }}>
                  <span className="recording-dot"></span>
                  <span className="recording-text">Recording in progress</span>
                </div>
                <div>
                  Press "stop recording" when you are done.
                </div>
              </div>
            )}
            {state === RecordingState.NO_PERMISSION && (
              <div>
                <div style={{ color: '#770000', marginBottom: '0.5rem' }}>Failed to start recording</div>
                <div>We could not access your microphone. Please make sure you allowed this page to access it.</div>
              </div>
            )}
            {state === RecordingState.FINISHED && (
              error ? (
                <div>Error: {error}</div>
              ) : (
                <div>
                  <div style={{ color: '#007700', marginBottom: '0.5rem' }}>Recording finished!</div>
                  <div>You can edit the transcript to correct any mistakes.</div>
                </div>
              )
            )}
          </div>
          {((state === RecordingState.RECORDING || state === RecordingState.FINISHED) && !error) && <Transcript blobUrl={blobUrl} sentences={sentences} ongoing={state === RecordingState.RECORDING} onInput={setText} />}
        </div>
        {state === RecordingState.FINISHED && blobUrl !== null && (
          <div>
            {showRecording && <AudioPreviewer sentences={sentences} blobUrl={blobUrl} />}
            {<LinkButton style={{ width: '100%' }} onClick={toggleShowRecording}>{showRecording ? 'Hide' : 'Show'} recording</LinkButton>}
          </div>
        )}
        {state === RecordingState.FINISHED && text.trim().length > 0 && (
          <div>
            <PrimaryButton
              leftIcon={<CheckSimple />}
              size="large"
              onClick={confirmRequested}
              style={{ width: '100%' }}
            >
              CONFIRM TRANSCRIPTION
            </PrimaryButton>
          </div>
        )}
        <div>
          {(state === RecordingState.IDLE || state === RecordingState.AWAITING_PERMISSION || state === RecordingState.RECORDING || state === RecordingState.NO_PERMISSION) ? (
            <PrimaryButton
              onClick={state === RecordingState.IDLE || state === RecordingState.NO_PERMISSION ? startRecording : stopRecording}
              isLoading={state === RecordingState.AWAITING_PERMISSION}
              loadingText={"Awaiting permission"}
              leftIcon={<Microphone />}
              size="large"
              style={{ width: '100%' }}
            >
              {{
                [RecordingState.IDLE]: 'START RECORDING',
                [RecordingState.FINISHED]: 'RESTART RECORDING',
                [RecordingState.AWAITING_PERMISSION]: 'AWAITING PERMISSION',
                [RecordingState.RECORDING]: 'STOP RECORDING',
                [RecordingState.NO_PERMISSION]: 'NO PERMISSION',
              }[state]}
            </PrimaryButton>
          ) : (
            <SecondaryButton
              onClick={startRecording}
              leftIcon={<Microphone />}
              size="large"
              style={{ width: '100%' }}
            >
              {{
                [RecordingState.FINISHED]: 'RESTART RECORDING',
              }[state]}
            </SecondaryButton>
          )}
        </div>
      </div >
    </>
  );
};

type AutoscribeBubbleProps = {
  onOpen?: () => void;
  onConfirm?: (text: string) => void;
  onCancel?: () => void;
};

export function AutoScribeBubble({ onOpen, onConfirm, onCancel }: AutoscribeBubbleProps) {
  const [isOpen, setIsOpen] = React.useState(false);

  const open = React.useCallback(() => {
    setIsOpen(true);
    if (typeof onOpen !== 'undefined') {
      onOpen();
    }
  }, [onOpen]);

  const onClose = React.useCallback(() => {
    setIsOpen(false);
    if (typeof onCancel !== 'undefined') {
      onCancel();
    }
  }, [onCancel]);

  const onConfirmRequested = React.useCallback((text: string) => {
    setIsOpen(false);
    if (typeof onConfirm !== 'undefined') {
      onConfirm(text);
    }
  }, [onConfirm]);

  return (
    <>
      <FloatButton icon={<AudioOutlined />} tooltip="AI Speech Recognition" onClick={open} type="primary" />
      <CustomSideDrawer placement="right" handleOk={onClose} handleCancel={onClose} isOpen={isOpen} size="md">
        <AutoScribeWidget onOpen={onOpen} onConfirm={onConfirmRequested} />
      </CustomSideDrawer>
    </>
  );
};
