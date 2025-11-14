import React from 'react';

// import fixWebmDuration from 'webm-duration-fix';

import MediaRecorder from 'opus-media-recorder';
import encoderWorkerCode from '!!raw-loader!opus-media-recorder/encoderWorker.umd.js';
import OggOpusWasmDataURI from 'opus-media-recorder/OggOpusEncoder.wasm';
import WebMOpusWasmDataURI from 'opus-media-recorder/WebMOpusEncoder.wasm';

// const root = new URL((document as any).currentScript.src).origin;

// Non-standard options
const workerOptions = {
  // This is atrocious. It's 2023 and shit still cannot be imported properly. And opus-media-recorder is outdated, but is the ONLY audio/ogg polyfill.
  // Additionally, Chrome still can't even support ogg-opus. What have we become?
  // encoderWorkerFactory: () => new Worker(`${root}/encoderWorker.umd.js`),
  encoderWorkerFactory: () => new Worker(URL.createObjectURL(new Blob([encoderWorkerCode], { type: "text/plain; charset=utf-8" }))),
  OggOpusEncoderWasmPath: OggOpusWasmDataURI,
  WebMOpusEncoderWasmPath: WebMOpusWasmDataURI,
};

export enum RecordingState {
  IDLE,
  AWAITING_PERMISSION,
  RECORDING,
  NO_PERMISSION,
  FINISHED,
};


export const useMicrophone = () => {
  const recorder = React.useRef<null | MediaRecorder>(null);
  const [stream, setStream] = React.useState<null | MediaStream>(null);
  const [state, setState] = React.useState<RecordingState>(RecordingState.IDLE);
  const [blobUrl, setBlobUrl] = React.useState<string | null>(null);
  const blobs = React.useRef<Array<Blob>>([]);

  const start = React.useCallback((onStarted: () => void, onData: (data: Blob) => void) => {
    setBlobUrl(null);
    setState(RecordingState.AWAITING_PERMISSION);
    navigator.mediaDevices.getUserMedia({ audio: true }).then(newStream => {
      setState(RecordingState.RECORDING);
      setStream(newStream);
      const newRecorder = new MediaRecorder(newStream, { mimeType: 'audio/ogg; codecs=opus' }, workerOptions);
      recorder.current = newRecorder;
      // TODO: Get sample rate fom recorder (below line doesn't work in Firefox)
      // console.log('Sample rate:', this.recorder.stream.getAudioTracks()[0].getSettings().sampleRate);
      (window as any).recorder = newRecorder;
      (window as any).stream = newStream;
      blobs.current = []; // Important - this makes sure we're writing to a new array
      recorder.current.addEventListener('dataavailable', event => {
        blobs.current.push(event.data);
        onData(event.data);
      });
      recorder.current.start(100);
      onStarted();
    }).catch(error => {
      console.error(error);
      setState(RecordingState.NO_PERMISSION);
    });
  }, []);

  const stop = React.useCallback((callback?: () => void) => {
    setState(RecordingState.FINISHED);
    if (!recorder.current) {
      // Recording stopped before it started
      callback?.();
      return;
    }
    if (recorder.current) {
      if (typeof callback !== 'undefined') {
        recorder.current.onstop = callback;
      }
      // console.log('REC', recorder.current.stop);
      recorder.current.stop(); // TODO: This fails for whatever reason
      // https://bugzilla.mozilla.org/show_bug.cgi?id=1068001
      // https://github.com/w3c/mediacapture-record/issues/67#issuecomment-247283783
      // https://github.com/w3c/mediacapture-record/issues/119#issuecomment-1153888129
      // fixWebmDuration(new Blob(blobs.current, {type: 'audio/webm; codecs=opus'})).then(fixedBlob => {
      //   const url = window.URL.createObjectURL(fixedBlob);
      //   setBlobUrl(url);
      // });
      const url = window.URL.createObjectURL(new Blob(blobs.current, { type: 'audio/ogg; codecs=opus' }));
      console.log('Created audio blob:', url);
      setBlobUrl(url);
    }
    if (stream !== null) {
      stream.getTracks().forEach(track => track.stop());
    }
  }, [stream]);

  const reset = React.useCallback(() => setState(RecordingState.IDLE), []);

  return { start, stop, reset, state, blobUrl };
};
