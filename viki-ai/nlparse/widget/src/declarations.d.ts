// Required for TypeScript + style-loader
// https://stackoverflow.com/a/55993985/3455614
declare module '*.css';
declare module '*.scss';
// Text files
declare module '!!raw-loader!opus-media-recorder/encoderWorker.umd.js' {
  const content: string;
  export default content;
};
// Required for WASM loading
declare module '*.wasm';
// declare module 'opus-media-recorder/encoderWorker.js' {
//   class EncoderWorker extends Worker {
//     constructor();
//   }
//
//   export default EncoderWorker
// }
//
