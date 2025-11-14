import React from 'react';

// import css from './AutoScribe.css';
import './AutoScribe.css';

import { Grid, Headline, Spinner } from '@mediwareinc/wellsky-dls-react';
import { Badge, Divider } from '@chakra-ui/react';

import useEnvJson from './hooks/useEnvJson';
import { Env } from './types';

type NLParseProps = {
  text: string
};

type Dataset = {
  mentions: Array<any>

  problems: Array<any>
  medicines: Array<any>
  procedures: Array<any>
};

export function NLParseWidget({ text }: NLParseProps) {
  const env = useEnvJson<Env>();
  const [dataset, setDataset] = React.useState<Dataset | null>(null);
  const [highlights, setHighlights] = React.useState<Array<string>>([]);
  const itemHovered = React.useCallback((item: any) => {
    setHighlights([item.mention.id, ...item.related_mentions.map((mention: any) => mention.id)]);
  }, []);
  React.useEffect(() => {
    if (env === null) {
      return;
    }
    fetch(`${env?.API_URL}/api/extract`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ content: text }),
    }).then(res => res.json()).then(res => {
      setDataset(res);
    });
  }, [text, env]);
  return (
    <div style={{ height: '100%' }}>
      <Grid gap={1} templateColumns='repeat(4, 1fr)' height="100%">
        <Grid.Item colSpan={2} overflowY="auto">
          <TextSection text={text} dataset={dataset} highlights={highlights} />
        </Grid.Item>
        <Grid.Item colSpan={2} overflowY="auto">
          <FeatureSection dataset={dataset} itemHovered={itemHovered} itemExited={() => setHighlights([])} />
        </Grid.Item>
      </Grid>
    </div>
  );
};

type TextSectionProps = {
  text: string
  dataset: Dataset | null
  highlights: Array<string>
};

type Token = {
  text: string
  label: string
  start: number
};

const TextSection = ({ text, dataset, highlights }: TextSectionProps) => {
  const [tokens, setTokens] = React.useState<Array<Token>>([]);
  React.useEffect(() => {
    // Convert text to tokens
    let start = 0;
    setTokens(text.split(' ').map(word => {
      const token = { text: word, label: '', start: start };
      start += word.length + 1;
      return token;
    }));
  }, [text]);
  React.useEffect(() => {
    let newTokens = [...tokens];
    let modified = false;
    if (dataset !== null) {
      // Merge/upgrade tokens
      console.log('Old:', newTokens.map(x => x.text).join(' '));
      dataset.mentions.forEach(mention => {
        let start = mention.text.begin_offset;
        let end = mention.text.begin_offset + mention.text.content.length;
        console.log(mention.text.content, start, end);
        // Find matching tokens
        // let firstToken = tokens.find(token => token.start === start);
        // Find indexes of first and last matching tokens
        const tokensToReplace = newTokens.filter(token => token.start >= start && token.start < end);
        if (tokensToReplace.length === 0) {
          // TODO
          return;
        }
        // console.log(mention.text.content, tokensToReplace);
        const firstIndex = newTokens.indexOf(tokensToReplace[0]);
        const lastIndex = newTokens.indexOf(tokensToReplace[tokensToReplace.length - 1]);
        if (tokensToReplace[0].label !== '') {
          // Already labeled
          return;
        }
        // console.log(problem.mention.text.content, startIndex, endIndex);
        newTokens.splice(firstIndex, lastIndex - firstIndex + 1, {
          text: mention.text.content,
          label: mention.id,
          start: start
        });
        modified = true;
      });
      if (modified) {
        setTokens(newTokens);
        console.log('New:', newTokens.map(x => x.text).join(' '));
      }
      // for (
      // Replace tokens
    }
  }, [tokens, dataset]);
  return (
    <div>{tokens.map(token => (
      token.label === '' ? <span>{token.text} </span> : <span><Badge bgColor={highlights.indexOf(token.label) !== -1 ? "#779977" : "AAAAAA"} color={highlights.indexOf(token.label) !== -1 ? "#FFFFFF" : "#555555"}>{token.text} <sup>{token.label}</sup></Badge> </span>
    ))}</div>
  );
};

type FeatureSectionProps = {
  dataset: Dataset | null
  itemHovered: (item: any) => void
  itemExited: () => void
};

const FeatureSection = ({ dataset, itemHovered, itemExited }: FeatureSectionProps) => {
  const sections = [
    {
      title: 'Problems',
      array: dataset?.problems,
    },
    {
      title: 'Medicines',
      array: dataset?.medicines,
    },
    {
      title: 'Procedures',
      array: dataset?.procedures,
    },
  ];
  return (
    dataset === null ? <div style={{ padding: '2rem', display: 'flex', justifyContent: 'center', alignItems: 'center', flexDirection: 'column' }}><Spinner /><div style={{ marginTop: '1rem' }}>Extracting features...</div></div> :
      (
        <div>
          {sections.map(section => (
            (section.array && section.array.length > 0) ? (
              <div>
                <Headline>{section.title}</Headline>
                {section.array?.map(item => (
                  <div style={{ padding: '0.5rem 0.5rem 1rem', cursor: 'pointer' }} onMouseEnter={() => itemHovered(item)} onMouseLeave={itemExited}>
                    {item.mention.text.content} <sup>{item.mention.id}</sup>
                    &nbsp;
                    <Badge bgColor="#CCEEAA" color="333333">{item.mention.temporal_assessment ? item.mention.temporal_assessment.value : ''}</Badge>
                    &nbsp;
                    <Badge bgColor="#CCEEAA" color="333333">{item.mention.certainty_assessment ? item.mention.certainty_assessment.value : ''}</Badge>
                    &nbsp;
                    {item.related_mentions.map((mention: any) => (
                      <>
                        <Badge>{mention.text.content} <sup>{mention.id}</sup></Badge>
                      </>
                    ))}
                  </div>
                ))}
                <Divider />
              </div>
            ) : null
          ))}
        </div>
      )
  );
};

