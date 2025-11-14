/*
  * This component renders an "annotated form".
  * It's currently using LHC form as renderer, so it can only be used with host application that uses LHC form as well.
  * We'll need to replace LHC form with a generic form renderer owned by us.
*/

import { CheckCircleOutlined, ExclamationCircleOutlined, HistoryOutlined, RobotOutlined } from '@ant-design/icons';
import { Heading, IconButton, Input, useToken, Select as ChakraSelect, Flex, Box } from '@chakra-ui/react';
import { Checkbox, Grid, LinkButton, PrimaryButton, SecondaryButton, Select, TextInput, Tooltip } from '@mediwareinc/wellsky-dls-react';
import { VariableSizeList as List } from 'react-window';
import React, { useMemo } from 'react';
import { EditIcon } from '@chakra-ui/icons';

export type AnnotatedFormProps = {
  originalData: any;
  newData: any;
  onPreferenceChange?: (preferredData: any) => void;
  onEvidenceRequested?: (evidenceRequestedFor: any) => void;
}

enum NavDirection {
  UP,
  DOWN
}

const AnnotatedForm: React.FC<AnnotatedFormProps> = ({ originalData, newData, onPreferenceChange, onEvidenceRequested }) => {
  // console.log("AnnotatedForm:originalData",originalData);
  // console.log("AnnotatedForm:newData",newData);
  const [displayMode, setDisplayMode] = React.useState<'oneCol' | 'twoCol'>('oneCol');
  const highlightedFieldPathStr = React.useRef<string | null>(null);

  // const [newDataState, setNewDataState] = React.useState<any>(newData);
  // const [originalDataState, setOriginalDataState] = React.useState<any>(originalData);
  const [preferredValues, setPreferredValues] = React.useState<any>({});
  // const topKeys = Object.keys(originalData);
  // TODO: Use react-window to render the list for better performance.
  // This requires us to calculate the height of each item in the list.
  // const TopSection = (index: any, style: any) => {
  //   return <div style={style}>
  //     <Section originalData={originalData[index]} newData={typeof newData[topKeys[index]] !== null && newData.hasOwnProperty(topKeys[index]) ? newData[topKeys[index]] : null} depth={0} displayMode={displayMode} />
  //   </div>
  // };

  const fieldControllers = React.useRef<any>({});

  const setFieldController = React.useCallback((path: Array<string>, controller: any) => {
    fieldControllers.current[JSON.stringify(path)] = controller;
  }, []);

  const aiValues: any = React.useMemo(() => {
    // aiValues contains a map of all the fields (key is JSON-ified path, value is whether the field has AI value)
    // originalObj has ordered dict, so we use it for sorting.
    // obj is unordered dict (backend prompting is messing up the order)
    const result: any = [];
    const recurse = (originalObj: any, obj: any, path: Array<string>) => {
      if (Array.isArray(obj)) {
        console.error('Arrays not implemented yet');
        return;
      } else if (typeof obj === 'object' && obj !== null) {
        // Section or field
        if (obj.hasOwnProperty('value')) {
          // Field
          result.push([JSON.stringify(path), obj !== null && typeof obj !== 'undefined']);
        } else {
          // Section
          if (typeof originalObj !== 'object' || originalObj === null || typeof originalObj === 'undefined') {
            return;
          }
          Object.keys(originalObj).filter(key => key !== '_meta').forEach(key => recurse(originalObj[key], obj[key], path.concat(key)));
        }
      } else {
        result.push([JSON.stringify(path), obj !== null && typeof obj !== 'undefined']);
      }
    };
    recurse(originalData, newData, []);
    return result;
  }, [originalData, newData]);
  console.log('Navigatable AI values:', aiValues.map((pair: any, index: any) => pair.concat(index)).filter(([path, hasValue, index]: any) => hasValue));

  const updatePreference = React.useCallback((path: Array<string>, value: any) => {
    setPreferredValues((prev: any) => {
      // TODO: Handle arrays
      let isInitial = false;
      const newPreferredValues = { ...prev };
      let current = newPreferredValues;
      for (let i = 0; i < path.length - 1; i++) {
        if (!current.hasOwnProperty(path[i])) {
          current[path[i]] = {};
        }
        current = current[path[i]];
      }
      if (!current.hasOwnProperty(path[path.length - 1])) {
        isInitial = true;
        //console.log('INITIAL: ', path, value);
      }
      current[path[path.length - 1]] = value;
      if (!isInitial) {
        //console.log('UPDATED: ', path, value);
        onPreferenceChange?.(newPreferredValues);
      }
      return newPreferredValues;
    });
  }, [onPreferenceChange]);

  const requestEvidence = React.useCallback((path: Array<string>, evidenceRequestedFor: any) => {
    if (highlightedFieldPathStr.current !== null) {
      fieldControllers.current[highlightedFieldPathStr.current]?.unhighlight();
    }
    highlightedFieldPathStr.current = JSON.stringify(path);
    fieldControllers.current[highlightedFieldPathStr.current]?.highlight();
    onEvidenceRequested?.(evidenceRequestedFor);
  }, [onEvidenceRequested]);

  const navigateRelatively = React.useCallback((path: Array<string>, direction: NavDirection) => {
    const pathStr = JSON.stringify(path);
    // console.log('navigateRelatively', pathStr, direction);
    const currentFieldIndex = aiValues.findIndex(([path, _]: any) => path === pathStr);
    if (currentFieldIndex === -1) {
      console.error('navigateRelatively: current path not found in aiValues');
      return;
    }
    let nextFieldIndex = currentFieldIndex;
    if (direction === NavDirection.UP) {
      nextFieldIndex--;
      while (nextFieldIndex >= 0 && !aiValues[nextFieldIndex][1]) {
        nextFieldIndex--;
      }
    } else if (direction === NavDirection.DOWN) {
      nextFieldIndex++;
      while (nextFieldIndex < aiValues.length && !aiValues[nextFieldIndex][1]) {
        nextFieldIndex++;
      }
    }
    if (nextFieldIndex < 0 || nextFieldIndex >= aiValues.length) {
      // Nowhere to navigate
      // TODO: Circular navigation?
      return;
    }
    console.log('navigateRelatively: next field index =', nextFieldIndex, 'path =', aiValues[nextFieldIndex][0]);
    if (fieldControllers.current.hasOwnProperty(aiValues[nextFieldIndex][0])) {
      fieldControllers.current[aiValues[nextFieldIndex][0]].focus();
    }
  }, [aiValues]);

  return (
    <div>
      {/* <Checkbox onChange={e => setDisplayMode(e.target.checked ? 'twoCol' : 'oneCol')}>Switch between 1- or 2-column display</Checkbox> */}
      {/* <Heading size="lg" style={{ margin: '1rem 0',width: '100%', height: '100%', paddingLeft: '12px', paddingRight: '12px', paddingTop: '16px', paddingBottom: '16px', background: '#2D9CDB', justifyContent: 'space-between', alignItems: 'center', display: 'inline-flex' }}>Start of Care</Heading> */}
      {/*
      <List itemCount={topKeys.length} width="100%">
        {TopSection}
      </List>
      */}
      <Section pathStr={'[]'} originalData={originalData} newData={newData} depth={0} displayMode={displayMode} onPreferenceChange={updatePreference} onEvidenceClicked={requestEvidence} onRelativeNavigation={navigateRelatively} onControllerReady={setFieldController} />
    </div>
  );
};

type SectionProps = {
  originalData: any;
  newData: any;
  depth: number;
  pathStr: string;
  displayMode: 'oneCol' | 'twoCol';
  onControllerReady?: (path: Array<string>, controller: any) => void;
  onPreferenceChange: (path: Array<string>, value: any) => void;
  onEvidenceClicked?: (path: Array<string>, evidenceRequestedFor: any) => void;
  onRelativeNavigation?: (path: Array<string>, direction: NavDirection) => void;
}

const Section = React.memo(({ originalData, newData, depth, pathStr, displayMode, onControllerReady, onPreferenceChange, onEvidenceClicked, onRelativeNavigation }: SectionProps) => {
  const path = JSON.parse(pathStr);
  const [headingColor, fieldColor] = useToken(
    // the key within the theme, in this case `theme.colors`
    'colors',
    // the subkey(s), resolving to `theme.colors.red.100`
    ['elm.500', 'bigStone.700'],
    // a single fallback or fallback array matching the length of the previous arg
  )
  // allKeys contains keys from both originalData & newData while preserving ordering
  const allKeys = Object.keys(originalData);//.concat(newData === null ? [] : Object.keys(newData).filter(key => !originalData.hasOwnProperty(key)));
  const metaNew = newData !== null && newData.hasOwnProperty('_meta') ? newData._meta : {};
  const metaOriginal = originalData !== null && originalData.hasOwnProperty('_meta') ? originalData._meta : {};
  const meta = { ...metaOriginal, ...metaNew };

  return <Grid templateColumns="repeat(2, 1fr)" gap={2}>
    {allKeys.filter(key => key !== '_meta').map(key => {
      const originalValue = originalData[key];
      const newValue = (newData !== null && newData.hasOwnProperty(key)) ? newData[key] : null;
      // some times _meta appears under the originalValue and not just as sepratae node
      const metaNode = meta.hasOwnProperty(key) ? meta[key] : (newValue?.hasOwnProperty('_meta') ? newValue?._meta : null);

      return Array.isArray(originalValue) ? (
        // Array
        <Grid.Item colSpan={2} key={key} alignSelf="center">
          <div>{key}: List</div>
        </Grid.Item>
      ) : (typeof originalValue === 'object' && originalValue !== null) ? (
        // Nested section
        <Grid.Item colSpan={2} key={key} alignSelf="center">
          {/* <Heading size="md" style={{ paddingLeft: `${depth * 4}rem`, padding: '0.75rem 0 0.75rem 0.5rem' }} bgColor={headingColor} color={'#FFFFFF'}> */}
          {/*<Checkbox borderColor={'#FFFFFF'} fill={'#FFFFFF'} style={{ verticalAlign: 'middle' }} stroke="red" color="red" size="lg" />*/}
          {/* <span style={{ verticalAlign: 'middle' }}>{key}</span> */}
          <div style={{ margin: '1rem 0', width: '100%', height: '100%', paddingLeft: '12px', paddingRight: '12px', paddingTop: '16px', paddingBottom: '16px', background: '#D7F1FE', justifyContent: 'space-between', alignItems: 'center', display: 'inline-flex' }} >
            <div style={{ color: 'rgba(0, 0, 0, 0.38)', fontSize: '14px', fontFamily: 'Roboto', fontWeight: '600', lineHeight: '30px', wordWrap: 'break-word' }}>{key}</div>
          </div>
          {/* </Heading> */}
          <div style={{ borderLeft: `0.25rem solid ${headingColor}`, padding: '1rem 0 0 1rem' }}>
          {/* <div style={{ padding: '1rem 0 0 1rem' }}> */}
            <Section pathStr={JSON.stringify(path.concat(key))} originalData={originalValue} newData={newValue} depth={depth + 1} displayMode={displayMode} onPreferenceChange={onPreferenceChange} onEvidenceClicked={onEvidenceClicked} onRelativeNavigation={onRelativeNavigation} onControllerReady={onControllerReady} />
          </div>
        </Grid.Item>
      ) : (
        // Field
        displayMode === 'twoCol' ? (
          <>
            <Grid.Item alignSelf="center">
              <div style={{ paddingLeft: `${depth * 2 * 0}rem`, textAlign: 'left', color: fieldColor }}>
                {key}
              </div>
            </Grid.Item>
            <Grid.Item alignSelf="center">
              <Field pathStr={JSON.stringify(path.concat(key))} name={key} originalData={originalValue} newDataObj={newValue} meta={metaNode} onPreferenceChange={onPreferenceChange} onEvidenceClicked={onEvidenceClicked} onRelativeNavigation={onRelativeNavigation} onControllerReady={onControllerReady} />
            </Grid.Item>
          </>
        ) : (
          <Grid.Item alignSelf="center" colSpan={2}>
            <div style={{ paddingLeft: `${depth * 4 * 0}rem`, textAlign: 'left', color: fieldColor, display: 'flex', alignItems: 'start' }}>
              <div style={{ display: 'inline-block', flex: 1 }}>
                <Field pathStr={JSON.stringify(path.concat(key))} name={key} originalData={originalValue} newDataObj={newValue} meta={metaNode} onPreferenceChange={onPreferenceChange} onEvidenceClicked={onEvidenceClicked} onRelativeNavigation={onRelativeNavigation} onControllerReady={onControllerReady} />
              </div>
            </div>
          </Grid.Item>
        )
      )
    })}
  </Grid>;
});

type FieldProps = {
  originalData: any;
  newDataObj: any;
  meta: any | null;
  name: string;
  pathStr: string;
  onControllerReady?: (path: Array<string>, controller: any) => void;
  onPreferenceChange: (path: Array<string>, value: any) => void;
  onEvidenceClicked?: (path: Array<string>, evidenceRequestedFor: any) => void;
  onRelativeNavigation?: (path: Array<string>, direction: NavDirection) => void;
}

const Uninitialized = Symbol('UninitializedField');

const Field = React.memo(({ name, pathStr, originalData, newDataObj, meta, onControllerReady, onPreferenceChange, onEvidenceClicked, onRelativeNavigation }: FieldProps) => {
  const path = JSON.parse(pathStr);
  const newData = newDataObj?.hasOwnProperty('value') ? newDataObj.value : newDataObj;
  const hasOriginalValue = originalData !== null;
  const hasNewValue = newData !== null;
  const hasContention = hasOriginalValue && hasNewValue && originalData !== newData;
  const hasAnswers = meta && meta.answers && meta.answers.length;

  const selfRef = React.useRef<HTMLDivElement>(null);
  const inputRef = React.useRef<any>(null);

  const [contentionColor, originalColor, originalDarkColor, newColor, newBgColor, normalColor, normalBgColor] = useToken(
    // the key within the theme, in this case `theme.colors`
    'colors',
    // the subkey(s), resolving to `theme.colors.red.100`
    ['status.200', 'bigStone.200', 'bigStone.300', 'zest.400', 'zest.100', 'bigStoneA.400', 'bigStoneA.100'],
    // a single fallback or fallback array matching the length of the previous arg
  )

  React.useEffect(() => {
    console.log('Constructed controller for', pathStr);
    onControllerReady?.(JSON.parse(pathStr), {
      focus: () => {
        console.log('focus() called on', pathStr);
        if (inputRef.current !== null) {
          inputRef.current.focus();
          // TODO: This duplicates code in label's onClick
          onEvidenceClicked?.(JSON.parse(pathStr), { "question": name, "answer": newDataObj?.value, "verbatim_source": newDataObj?.verbatim_source });
        }
      },
      highlight: () => {
        console.log('highlight() called on', pathStr);
        if (selfRef.current !== null) {
          selfRef.current.style.background = 'rgba(175, 238, 238, 0.2)';
        }
      },
      unhighlight: () => {
        console.log('unhighlight() called on', pathStr);
        if (selfRef.current !== null) {
          selfRef.current.style.background = 'none';
        }
      }
    });
  }, [onControllerReady, pathStr, name, newDataObj, onEvidenceClicked]);

  // const [state, setState] = React.useState<'added' | 'contention' | 'ignored'>('ignored');
  const [preferredValue, setPreferredValue] = React.useState<string | null | typeof Uninitialized>(Uninitialized);
  const [resolved, setResolved] = React.useState<boolean>(false);
  // let color = 'white';
  // let state = 'ignored';
  React.useEffect(() => {
    if (originalData !== newData) {
      // Original data & AI data are different
      if (originalData === null) {
        // Use AI data
        setResolved(false);
        setPreferredValue(newData);
      } else if (newData === null) {
        // Use original data
        setResolved(false);
        setPreferredValue(originalData);
      } else {
        // Contention
        setResolved(false);
        setPreferredValue(originalData);
      }
    } else {
      // Original data & AI data are same
      setResolved(false);
      setPreferredValue(originalData);
    }
  }, [pathStr, onPreferenceChange, originalData, newData]);

  const resolve = React.useCallback((value: string) => {
    if (!hasContention) {
      console.error('resolve() called when there is no contention');
    }
    setPreferredValue(value);
    setResolved(true);
  }, [hasContention]);

  const manualEntry = React.useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.value.length) {
      setPreferredValue(null);
    } else {
      setPreferredValue(e.target.value);
    }
    if (hasContention) {
      setResolved(true);
    }
  }, [hasContention]);
  const manualCheck = React.useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setPreferredValue(e.target.checked ? meta.answers[0] : null);
    if (hasContention) {
      setResolved(true);
    }
  }, [hasContention, meta]);

  React.useEffect(() => {
    if (preferredValue !== Uninitialized) {
      onPreferenceChange(JSON.parse(pathStr), preferredValue);
    }
  }, [pathStr, onPreferenceChange, preferredValue]);

  let inputColor;
  const isCheckbox = meta && meta.displayControl?.answerLayout?.type === 'CHECK_BOX';
  if (preferredValue === originalData) {
    inputColor = originalColor;
    if (hasContention) {
      // Resolving a contention to original value should make the field blue to look "modified"
      inputColor = normalColor;
    }
  } else if (preferredValue === newData) {
    inputColor = newColor;
  } else {
    inputColor = normalColor;
  }

  let iconColor;
  if (hasContention) {
    if (resolved) {
      if (preferredValue === originalData) {
        iconColor = originalColor;
      } else if (preferredValue === newData) {
        iconColor = newColor;
      } else {
        iconColor = normalColor;
      }
    } else {
      iconColor = contentionColor;
    }
  } else {
    iconColor = normalColor;
  }

  const onKeyDown = React.useCallback((e: React.KeyboardEvent<HTMLElement>) => {
    if (e.keyCode === 38) {
      // Key is up arrow
      e.preventDefault();
      onRelativeNavigation?.(JSON.parse(pathStr), NavDirection.UP);
    } else if (e.keyCode === 40) {
      // Key is down arrow
      e.preventDefault();
      onRelativeNavigation?.(JSON.parse(pathStr), NavDirection.DOWN);
    }
  }, [onRelativeNavigation, pathStr]);

  const isSelect = meta && meta.answers && meta.answers.length > 0 && meta.answers[0] !== null;


  const checkboxParentContainerStyles = useMemo(() => (
    {
      display: 'flex',
      flexDirection: 'row-reverse',
      justifyContent: 'flex-end',
    }
  ), [])
  // Dropdown
  if (preferredValue === Uninitialized) {
    return null;
  }
  return (
    <div style={{ display: 'flex', alignItems: 'start' }} ref={selfRef}>
      <div style={{ display: 'inline-block', padding: '1.9rem 1rem 0 0' }}>
        {(hasContention && !resolved) ? (
          <Tooltip placement="top" label={<div><div>Our AI thinks this value should be different.</div><div>Original value: <strong>{originalData}</strong></div><div>AI-suggested value: <strong>{newData}</strong></div></div>}>
            <ExclamationCircleOutlined style={{ color: contentionColor, fontSize: '1.5rem' }} />
          </Tooltip>
        ) : (
          preferredValue === originalData ? (
            <HistoryOutlined style={{ color: originalColor, fontSize: '1.5rem', opacity: 0 }} />
          ) : preferredValue === newData ? (
            <RobotOutlined style={{ color: newColor, fontSize: '1.5rem', opacity: 0 }} />
          ) : (
            <EditIcon style={{ color: normalColor, fontSize: '1.5rem', opacity: 0 }} />
          )
        )}
      </div>
      <div style={{ display: 'inline-block', flex: 1 }}>
        <div style={isCheckbox ? checkboxParentContainerStyles : ({} as any)}>
          <div style={{ fontSize: '0.9rem', display: isCheckbox ? 'inline-flex' : 'block' }}>
            <Tooltip placement="top" label={<div>Click to highlight evidences</div>}>
              <strong style={{ cursor: 'pointer', userSelect: 'none' }} onClick={() => { onEvidenceClicked?.(path, { "question": name, "answer": preferredValue, "verbatim_source": newDataObj?.verbatim_source }) }}>{name}&nbsp;</strong>
            </Tooltip>
          </div>
          {!isCheckbox && (isSelect ? (
            /* DLS Select does not support ref?! */
            <ChakraSelect
              ref={inputRef}
              _hover={{ borderColor: inputColor }}
              _active={{ borderColor: inputColor }}
              style={{ width: '100%' }}
              focusBorderColor={inputColor}
              borderColor={inputColor}
              borderBottomWidth="2px"
              value={preferredValue !== null && (!hasContention || resolved) ? preferredValue : 'Not selected'}
              onChange={e => resolve(e.target.value)}
              onKeyDown={onKeyDown}
            >
              {[null].concat(meta.answers).map((answer: string | null) => <option value={answer !== null ? answer : ''}>{answer === null ? 'Not selected' : answer}</option>)}
            </ChakraSelect>
          ) : (
            <Input
              ref={inputRef}
              _hover={{ borderColor: inputColor }}
              paddingLeft="0.5rem"
              focusBorderColor={inputColor}
              borderColor={inputColor}
              borderWidth='2px'
              value={preferredValue !== null && (!hasContention || resolved) ? preferredValue : ''}
              onInput={manualEntry}
              onKeyDown={onKeyDown}
            />
          ))}
          {isCheckbox && (
            <Flex
              direction="column"
              gap="3px"
            >
              <Checkbox
                ref={inputRef}
                isChecked={Boolean(preferredValue)}
                onChange={manualCheck}
                onKeyDown={onKeyDown}
              ></Checkbox>
              {originalColor !== inputColor && <Box
                height="2px"
                backgroundColor={inputColor}
                marginRight="7px"
              ></Box>}
            </Flex>
          )}
        </div>
        <div style={{ padding: '0.5rem 0', display: 'flex', gap: '0' }}>
          <>
            <div>
              {
                (hasContention || (hasOriginalValue && preferredValue !== originalData)) ? (
                  <Tooltip placement="bottom" label={<div>Click to use original value</div>}>
                    <IconButton
                      borderRadius={0}
                      borderWidth={0}
                      aria-label="Using previous value"
                      bgColor={preferredValue === originalData && (!hasContention || resolved) ? normalColor : 'transparent'}
                      color={preferredValue === originalData && (!hasContention || resolved) ? "#FFFFFF" : normalColor}
                      borderColor={normalColor}
                      onClick={() => resolve(originalData)}
                    >
                      <EditIcon />
                    </IconButton>
                  </Tooltip>
                ) :
                  (
                    // Disabling this button as per Balki's request
                    (false && preferredValue !== originalData && preferredValue !== newData) && (
                      <Tooltip placement="bottom" label={<div>Indicates manually selected value</div>}>
                        <IconButton
                          borderRadius={0}
                          borderWidth={0}
                          aria-label="Using manual value"
                          bgColor={normalColor}
                          color={'#FFFFFF'}
                          borderColor={normalColor}
                          borderTopLeftRadius={0}
                          borderBottomLeftRadius={0}
                        >
                          <EditIcon style={{ color: '#FFFFFF' }} />
                        </IconButton>
                      </Tooltip>
                    )
                  )
              }
            </div>
            <div>
              {
                (hasContention || (hasNewValue && preferredValue !== newData)) && (
                  <Tooltip placement="bottom" label={<div>Click to use AI value</div>}>
                    <IconButton
                      borderRadius={0}
                      borderWidth={0} aria-label="Using AI value"
                      bgColor={preferredValue === newData && (!hasContention || resolved) ? newColor : 'transparent'}
                      color={preferredValue === newData && (!hasContention || resolved) ? "#FFFFFF" : newColor}
                      borderColor={newColor}
                      onClick={() => resolve(newData)}
                    >
                      <RobotOutlined style={{ color: preferredValue === newData ? '#FFFFFF' : newColor }} />
                    </IconButton>
                  </Tooltip>
                )
              }
            </div>

          </>
        </div>
      </div>
    </div >
  );
});

export default AnnotatedForm;
