export interface Env {
  API_URL: string
  VERSION: string
}

export type Word = {
  text: string,
  start: number,
  end: number,
};

export type Sentence = {
  is_final: Boolean,
  words: Array<Word>,
  speaker_tag: number,
};

export type TextSentence = {
  text: string,
  start: number,
  end: number,
  speaker_tag: number,
  is_final: Boolean,
};
