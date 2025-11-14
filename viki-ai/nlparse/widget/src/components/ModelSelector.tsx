import React from 'react';

import { Select } from '@mediwareinc/wellsky-dls-react';

type ModelSelectorProps = {
  onChange: (text: string) => any,
};
export const ModelSelector: React.FC<ModelSelectorProps> = ({ onChange }: ModelSelectorProps) => {
  const [currentModel, setCurrentModel] = React.useState<string>('medical_conversation');
  React.useEffect(() => {
    onChange(currentModel)
  }, [currentModel, onChange]);
  const onModelSelected = React.useCallback((e: any) => {
    setCurrentModel(e.target.value);
  }, []);
  const options = [
    {
      name: 'latest_long',
      description: 'Use this model for any kind of long form content such as media or spontaneous speech and conversations. Consider using this model in place of the video model, especially if the video model is not available in your target language. You can also use this in place of the default model.',
    },
    {
      name: 'latest_short',
      description: 'Use this model for short utterances that are a few seconds in length. It is useful for trying to capture commands or other single shot directed speech use cases. Consider using this model instead of the command and search model.',
    },
    {
      name: 'command_and_search',
      description: 'Best for short or single-word utterances like voice commands or voice search.',
    },
    {
      name: 'phone_call',
      description: 'Best for audio that originated from a phone call (typically recorded at an 8khz sampling rate).',
    },
    {
      name: 'video',
      description: 'Best for audio from video clips or other sources (such as podcasts) that have multiple speakers. This model is also often the best choice for audio that was recorded with a high-quality microphone or that has lots of background noise. For best results, provide audio recorded at 16,000Hz or greater sampling rate.',
    },
    {
      name: 'medical_dictation',
      description: 'Use this model to transcribe notes dictated by a medical professional. This is a premium model that costs more than the standard rate. See the pricing page for more details.',
    },
    {
      name: 'medical_conversation',
      description: 'Use this model to transcribe a conversation between a medical professional and a patient. This is a premium model that costs more than the standard rate. See the pricing page for more details.',
    },
    {
      name: 'default',
      description: 'Best for audio that does not fit the other audio models, like long-form audio or dictation. The default model will produce transcription results for any type of audio, including audio such as video clips that have a separate model specifically tailored to it. However, recognizing video clip audio using the default model will likely yield lower-quality results than using the video model. Ideally the audio is high-fidelity, recorded at a 16khz or greater sampling rate.',
    }
  ];
  return (
    <Select style={{ width: '100%' }} defaultValue="medical_conversation" onChange={onModelSelected} label="Model">
      {options.map(option => (
        <option value={option.name} key={option.name}>
          <div>
            <strong style={{ fontSize: '1.25rem' }}>{option.name.toUpperCase()}</strong>
          </div>
          &nbsp;&mdash;&nbsp;
          <div style={{ whiteSpace: 'normal', fontSize: '0.75rem' }}>{option.description}</div>
        </option>
      ))}
    </Select>
  );
};

