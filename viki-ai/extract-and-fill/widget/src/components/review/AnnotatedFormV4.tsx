/*
  * This component renders an "annotated form".
  * It's currently using LHC form as renderer, so it can only be used with host application that uses LHC form as well.
  * We'll need to replace LHC form with a generic form renderer owned by us.
*/


import React, { useMemo } from 'react';
import { EditIcon } from '@chakra-ui/icons';
import CustomFormsComponent from '../custom-form';
import useEnvJson from '../../hooks/useEnvJson';
import { Box } from '@chakra-ui/react';

export type CustomFormAnnotatedFormProps = {
  schema: any;
  originalData: any;
  newData: any;
  formInstanceId?: string;
  formTemplateId?: string;
  onPreferenceChange?: (preferredData: any) => void;
  onEvidenceRequested?: (field: any) => void;
}

enum NavDirection {
  UP,
  DOWN
}

const CustomFormAnnotatedForm: React.FC<CustomFormAnnotatedFormProps> = ({ schema, originalData, newData, formInstanceId, formTemplateId, onPreferenceChange, onEvidenceRequested }) => {
  const env:any = useEnvJson();
  return (
    <Box width={"100%"}>
      {env && env?.FORMS_WIDGETS_HOST && <CustomFormsComponent widgetHost={env?.FORMS_WIDGETS_HOST} env={env} formInstanceId={formInstanceId} formTemplateId={formTemplateId} newData={newData} onEvidenceRequested={onEvidenceRequested} />}
    </Box>
  )
}

export default CustomFormAnnotatedForm;