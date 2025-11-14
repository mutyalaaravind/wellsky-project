import React, { useEffect } from 'react';

// import css from './AutoScribe.css';
import './AutoScribe.css';

import { Drawer, FloatButton } from 'antd';
import { AudioOutlined, SettingOutlined, CheckOutlined } from '@ant-design/icons';
import { PrimaryButton, SecondaryButton, LinkButton, Grid, Popover, Select, TextArea, CustomSideDrawer, Tooltip } from '@mediwareinc/wellsky-dls-react';
import { Badge, Box, IconButton, Text } from '@chakra-ui/react';
import { Microphone, Refresh, CheckSimple, Upload } from '@mediwareinc/wellsky-dls-react-icons';

import { useMicrophone, RecordingState } from './hooks/microphone';
import useEnvJson from './hooks/useEnvJson';
import { Env, Section, Sentence, TextSentence, Word } from './types';
import { BackendSelector } from './components/BackendSelector';
import { ModelSelector } from './components/ModelSelector';
import { Transcript, PreviewTranscript } from './components/Transcript';
import { AudioPreviewer } from './components/AudioPreviewer';
import { createPortal } from 'react-dom';

type AutoscribeProps = {
  transactionId: string;
  sectionId: string;
  onOpen?: () => void;
  onConfirm?: (textSentences: Array<TextSentence>, transactionId: string, sectionId: string, version: number) => void;
  inlineWidgetEmbedding?: boolean;
  evidences?: Array<string>;
  verbatimSourceEvidence?: string;
};

export function AutoScribeWidget({ onConfirm, transactionId, sectionId, inlineWidgetEmbedding, evidences, verbatimSourceEvidence }: AutoscribeProps) {
  const { start, stop, reset, state, blobUrl } = useMicrophone();
  const [audioSignedUrl, setAudioSignedUrl] = React.useState<string | null>(null);
  const [sentences, setSentences] = React.useState<Array<Sentence>>([]);
  const ws = React.useRef<null | WebSocket>(null);
  const [textSentences, setTextSentences] = React.useState<Array<TextSentence>>([]);
  const [isUnsaved, setIsUnsaved] = React.useState<boolean>(false);
  const [error, setError] = React.useState<string>('');
  const [backend, setBackend] = React.useState<string>('google_v1');
  const [model, setModel] = React.useState<string>('medical_conversation');
  const [showRecording, setShowRecording] = React.useState<boolean>(false);
  const [loading, setLoading] = React.useState<boolean>(true);
  const [existing, setExisting] = React.useState<boolean>(false);
  const lastVersion = React.useRef<number>(0);
  const env = useEnvJson<Env>();

  const toggleShowRecording = React.useCallback(() => setShowRecording(v => !v), []);

  React.useEffect(() => {
    if (env === null) {
      return;
    }
    fetch(`${env?.API_URL}/api/transactions/${transactionId}/sections/${sectionId}`, {
      method: 'GET',
    }).then(response => response.json()).then(sectionData => {
      if (sectionData !== null) {
        // Transaction already exists
        setExisting(true);
        setTextSentences(sectionData.text_sentences);
        lastVersion.current = sectionData.version;
      }
      setLoading(false);
    });
    fetch(`${env?.API_URL}/api/transactions/${transactionId}/sections/${sectionId}/audio-url`, {
      method: 'GET',
    }).then(response => response.json()).then(data => {
      setAudioSignedUrl(data.url);
    });
  }, [env, transactionId, sectionId]);

  const reRecord = React.useCallback(() => {
    setExisting(false);
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
    setSentences([{ words: [{ text: '...', start: 0, end: 0 }], is_final: false, speaker_tag: 0 }]);
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
          'transaction_id': transactionId,
          'section_id': sectionId,
        };
        console.log('WebSocket opened, sending metadata', metadata);
        // Send metadata
        ws.current.send(JSON.stringify(metadata));
        queue.forEach(blob => blob.size && (ws.current as any).send(blob));
        setSentences([{ words: [{ text: '...', start: 0, end: 0 }], is_final: false, speaker_tag: 0 }]);
        ws.current.onmessage = message => {
          const data = JSON.parse(message.data);
          if (data.type === 'start') {
            //
          } else if (data.type === 'recognition') {
            setSentences(sentences => sentences.filter(s => s.is_final).concat({ words: [{ text: data.transcript, start: 0, end: 0 }], is_final: false, speaker_tag: 0 }));
            // if (data.is_final) {
            //   setSentences(sentences => sentences.filter(sentence => sentence.is_final).concat({ words: data.words, is_final: true, speaker_tag: '?' }, { words: [{text: '...', start: 0, end: 0, speaker_tag: '0'}], is_final: false, speaker_tag: '?' }));
            // } else {
            // setSentences(sentences => sentences.filter(sentence => sentence.is_final).concat({ words: data.words, is_final: false, speaker_tag: '?' }));
            // }
          } else if (data.type === 'diarization') {
            setSentences(data.sentences.map((sentence: any) => ({ ...sentence, is_final: true })));
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
  }, [start, env, stopRecording, backend, model, transactionId, sectionId]);

  const confirmRequested = React.useCallback(() => {
    setSentences([]);
    // setTextSentences([]); // Do not reset
    setExisting(true);
    reset();
    fetch(`${env?.API_URL}/api/finalize`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        transaction_id: transactionId,
        section_id: sectionId,
        text_sentences: textSentences,
      }),
    }).then(response => response.json()).then(data => {
      lastVersion.current = data.version;
      if (typeof onConfirm !== 'undefined' && sectionId === "default") {
        onConfirm(textSentences, transactionId, sectionId, data.version);
      }
    });
  }, [onConfirm, reset, textSentences, transactionId, sectionId, env?.API_URL]);

  const confirmExisting = React.useCallback(() => {
    if (isUnsaved) {
      fetch(`${env?.API_URL}/api/finalize`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          transaction_id: transactionId,
          section_id: sectionId,
          text_sentences: textSentences,
        }),
      }).then(response => response.json()).then(data => {
        lastVersion.current = data.version;
        if (typeof onConfirm !== 'undefined') {
          onConfirm(textSentences, transactionId, sectionId, data.version);
        }
      });
      setIsUnsaved(false);
    } else {
      if (typeof onConfirm !== 'undefined') {
        onConfirm(textSentences, transactionId, sectionId, lastVersion.current);
      }
    }
  }, [onConfirm, textSentences, transactionId, sectionId, isUnsaved, env?.API_URL]);

  const setTextSentencesAndMarkUnsaved = React.useCallback((sentences: Array<TextSentence>) => {
    setTextSentences(sentences);
    setIsUnsaved(true);
  }, []);

  if (!env) {
    return <div>Loading configuration...</div>;
  }

  if (loading) {
    return <div>Checking for existing transcription...</div>;
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', gap: '1rem', flex: '1', minHeight: 0 }}>
      {!inlineWidgetEmbedding && <Box borderBottom="1px" borderColor="gray.200" paddingY={1}>
        <Text fontSize="lg" fontWeight="bold">
          Assessment Visit Transcript
        </Text>
      </Box>}
      {!existing ? (
        <>
          <div style={{ flex: 1, overflowY: 'auto', paddingBottom: '2rem' }}>
            <div style={{ float: 'right' }}>
              <Popover title="Settings" content={(
                <div style={{ /*minWidth: '30vw'*/ }}>
                  <Grid gap={1} templateColumns='repeat(4, 1fr)'>
                    <Grid.Item colSpan={4}>
                      Version: <Badge colorScheme="blue">{env.VERSION.length === 40 ? env.VERSION.substr(0, 7) : env.VERSION}</Badge>
                    </Grid.Item>
                    <Grid.Item colSpan={4}>
                      <div>Transaction ID:</div>
                      <Badge colorScheme="green">{transactionId}</Badge>
                    </Grid.Item>
                    <Grid.Item colSpan={4}>
                      <div>Section ID:</div>
                      <Badge colorScheme="orange">{sectionId}</Badge>
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
            {((state === RecordingState.RECORDING || state === RecordingState.FINISHED) && !error) && <Transcript blobUrl={blobUrl} sentences={sentences} ongoing={state === RecordingState.RECORDING} onInput={setTextSentences} evidences={evidences} verbatimSourceEvidence={verbatimSourceEvidence} />}
          </div>
          <Badge>ID: {transactionId}</Badge>
          {state === RecordingState.FINISHED && blobUrl !== null && (
            <div>
              {showRecording && <AudioPreviewer sentences={sentences} blobUrl={blobUrl} />}
              {<LinkButton style={{ width: '100%' }} onClick={toggleShowRecording}>{showRecording ? 'Hide' : 'Show'} recording</LinkButton>}
            </div>
          )}
          {state === RecordingState.FINISHED && textSentences.length > 0 && (
            <div>
              <PrimaryButton
                leftIcon={<CheckSimple />}
                size="large"
                onClick={confirmRequested}
                style={{ width: '100%' }}
              >
                USE THIS TRANSCRIPTION
              </PrimaryButton>
            </div>
          )}
          <div>
            {(state === RecordingState.IDLE || state === RecordingState.AWAITING_PERMISSION || state === RecordingState.RECORDING || state === RecordingState.NO_PERMISSION) ? (
              <div style={{ width: '100%', display: 'flex', flexDirection: 'row' }}>
                <PrimaryButton
                  onClick={state === RecordingState.IDLE || state === RecordingState.NO_PERMISSION ? startRecording : stopRecording}
                  isLoading={state === RecordingState.AWAITING_PERMISSION}
                  loadingText={"Awaiting permission"}
                  leftIcon={<Microphone />}
                  size="large"
                  style={{ flex: 1 }}
                >
                  {{
                    [RecordingState.IDLE]: 'START RECORDING',
                    [RecordingState.FINISHED]: 'RESTART RECORDING',
                    [RecordingState.AWAITING_PERMISSION]: 'AWAITING PERMISSION',
                    [RecordingState.RECORDING]: 'STOP RECORDING',
                    [RecordingState.NO_PERMISSION]: 'NO PERMISSION',
                  }[state]}
                </PrimaryButton>
                {state === RecordingState.IDLE && (
                  <Tooltip label="Upload a file instead" aria-label="Upload a file instead">
                    <IconButton
                      aria-label="Upload file"
                      icon={<Upload />}
                      onClick={() => { }}
                      variant="link"
                      size="large"
                    />
                  </Tooltip>
                )}
              </div>
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
        </>
      ) : (
        <>
          {/*<p>This section has already been recorded.</p>*/}
          <div style={{ flex: 1, overflowY: 'auto', paddingBottom: '2rem' }}>
            <div style={{ margin: '1rem' }}>
              {/*<div>{JSON.stringify(blobUrl)}, {JSON.stringify(audioSignedUrl)}</div>*/}
              <PreviewTranscript textSentences={textSentences} evidences={evidences} verbatimSourceEvidence={verbatimSourceEvidence} onInput={setTextSentencesAndMarkUnsaved} blobUrl={blobUrl || audioSignedUrl} />
            </div>
          </div>
          <div>
            <PrimaryButton
              leftIcon={<CheckSimple />}
              size="large"
              onClick={confirmExisting}
              style={{ width: '100%' }}
            >
              USE THIS TRANSCRIPTION {isUnsaved ? '*' : ''}
            </PrimaryButton>
          </div>
          <SecondaryButton
            onClick={reRecord}
            leftIcon={<Refresh />}
            size="large"
            style={{ width: '100%' }}
          >
            RE-RECORD
          </SecondaryButton>
        </>
      )}
    </div>
  );
};

type AutoscribeBubbleProps = {
  onOpen?: () => void;
  onConfirm?: (textSentences: Array<TextSentence>, transactionId: string, sectionId: string, version: number) => void;
  onCancel?: () => void;
  transactionId: string;
  sectionId: string;
};

export function AutoScribeBubble({ onOpen, onConfirm, onCancel, transactionId, sectionId }: AutoscribeBubbleProps) {
  const env = useEnvJson<Env>(); // TODO: This must be optimized since we're calling it in AutoScribeWidget as well
  const [isOpen, setIsOpen] = React.useState(false);
  const [existing, setExisting] = React.useState(false);

  // React.useEffect(() => {
  //   // We are duplicating this call here since Drawer contents don't render until it's visible,
  //   // but we need to know right now if the section exists to show proper icon.
  //   if (env === null) {
  //     return;
  //   }
  //   fetch(`${env?.API_URL}/api/transactions/${transactionId}/sections/${sectionId}`, {
  //     method: 'GET',
  //   }).then(response => response.json()).then(sectionData => {
  //     setExisting(sectionData !== null);
  //   });
  // }, [sectionId, transactionId, env]);

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

  // const onConfirmRequested = React.useCallback((textSentences: Array<TextSentence>, transactionId: string, sectionId: string, version: number) => {
  //   console.log("onConfirmRequested", onConfirm, textSentences, transactionId, sectionId, version);
  //   onConfirm && onConfirm(textSentences, transactionId, sectionId, version);
  // },[onConfirm]);

  const onConfirmRequested = React.useCallback(onConfirm ? onConfirm : () => {
    console.log("onConfirmRequested callback not set")
  }, [onConfirm]);

  // const onConfirmRequested = React.useCallback((textSentences: Array<TextSentence>, transactionId: string, sectionId: string) => {
  //   setIsOpen(false);
  //   fetch(`${env?.API_URL}/api/finalize`, {
  //     method: 'POST',
  //     headers: {
  //       'Content-Type': 'application/json',
  //     },
  //     body: JSON.stringify({
  //       transaction_id: transactionId,
  //       section_id: sectionId,
  //       text_sentences: textSentences,
  //     }),
  //   }).then(response => response.json()).then(data => {
  //     //lastVersion.current = data.version;
  //     if (typeof onConfirm !== 'undefined' && sectionId === "default") {
  //       onConfirm(textSentences, transactionId, sectionId, data.version);
  //     }
  //   });
  //   // if (typeof onConfirm !== 'undefined') {
  //   //   //onConfirm(textSentences, transactionId, sectionId);
  //   // }
  // }, [onConfirm]);

  const drawer = (
    <Drawer placement="right" onClose={onClose} open={isOpen} size="large">
      <AutoScribeWidget onOpen={onOpen} onConfirm={onConfirmRequested} transactionId={transactionId} sectionId={sectionId} />
    </Drawer>
  );

  // if (el) {
  //   // Render in portal
  //   return createPortal((
  //     <>
  //     <div style={{float: 'right'}}>
  //       {existing ? (
  //         <SecondaryButton onClick={open} leftIcon={<CheckOutlined />}>WellSky Companion</SecondaryButton>
  //       ) : (
  //         <PrimaryButton onClick={open} leftIcon={<AudioOutlined />}>WellSky Companion</PrimaryButton>
  //       )}
  //       </div>
  //       {drawer}
  //     </>
  //   ), el);
  // }
  useEffect(() => {
    //if sectionId, we want this drawer to open up since this means
    // button is clicked
    console.log("autoscribe sectionid", sectionId);
    if (sectionId !== "default") {
      setIsOpen(true)
    }
  }, [sectionId])

  return (
    <>
      {/* if section id then we want no floater */}
      {sectionId === "default" ? <FloatButton icon={existing ? <CheckOutlined /> : <AudioOutlined />} style={{ right: 94 }} tooltip="AI Speech Recognition" onClick={open} type={existing ? "default" : "primary"} /> : <></>}
      {drawer}
    </>
  );
};

type AutoscribeReadOnlyProps = {
  transactionId: string;
  sectionId: string;
  evidences?: Array<string>;
  verbatimSourceEvidence?: string;
};

export function AutoScribeReadonlyWidget({ transactionId, sectionId, evidences, verbatimSourceEvidence }: AutoscribeReadOnlyProps) {
  const [textSentences, setTextSentences] = React.useState<Array<TextSentence>>([]);
  const [loading, setLoading] = React.useState<boolean>(true);
  const [existing, setExisting] = React.useState<boolean>(false);
  const [audioSignedUrl, setAudioSignedUrl] = React.useState<string | null>(null);
  const env = useEnvJson<Env>();

  React.useEffect(() => {
    if (env === null) {
      return;
    }
    fetch(`${env?.API_URL}/api/transactions/${transactionId}/sections/${sectionId}`, {
      method: 'GET',
    }).then(response => response.json()).then(sectionData => {
      if (sectionData !== null) {
        // Transaction already exists
        setExisting(true);
        setTextSentences(sectionData.text_sentences);
      }
      setLoading(false);
    });
    fetch(`${env?.API_URL}/api/transactions/${transactionId}/sections/${sectionId}/audio-url`, {
      method: 'GET',
    }).then(response => response.json()).then(data => {
      setAudioSignedUrl(data.url);
    });
  }, [env, transactionId, sectionId]);

  if (!env) {
    return <div>Loading configuration...</div>;
  }

  if (loading) {
    return <div>Checking for existing transcription...</div>;
  }

  if (!existing) {
    return <div>This section has not been recorded yet.</div>;
  }

  return (
    <div style={{ flex: 1, overflowY: 'auto', paddingBottom: '2rem' }}>
      <div style={{ margin: '1rem' }}>
        <PreviewTranscript blobUrl={audioSignedUrl} textSentences={textSentences} evidences={evidences} verbatimSourceEvidence={verbatimSourceEvidence} />
      </div>
    </div>
  );
}
