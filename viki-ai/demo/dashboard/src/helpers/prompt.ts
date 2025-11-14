export const buildExtractPromptTemplate = (template: any, transcriptText: string) => {
    const buildInnerPromptTemplate = (
      extractPromptTemplateTemp: any,
      field: any
    ) => {
      if (
        extractPromptTemplateTemp &&
        field.fields &&
        field.fields.length > 0 &&
        field.isList
      ) {
        //inner fields
        const resolvedField = field.fieldName || field.displayName;
        extractPromptTemplateTemp[resolvedField] = [{}];
        field.fields.forEach((innerfield: any) => {
          let index = 0;
          if (extractPromptTemplateTemp[resolvedField][index]) {
          } else {
            extractPromptTemplateTemp[resolvedField][index] = [{}];
          }
          extractPromptTemplateTemp[resolvedField][index] =
            buildInnerPromptTemplate(
              extractPromptTemplateTemp[resolvedField][index],
              innerfield
            );
        });
        return extractPromptTemplateTemp[resolvedField];
      } else if (
        extractPromptTemplateTemp &&
        field.fields &&
        field.fields.length > 0
      ) {
        const resolvedField = field.fieldName || field.displayName;
        if (field.formFieldType !== "FIELD_GROUP") {
          extractPromptTemplateTemp[resolvedField] = {};
        } else {
          if (extractPromptTemplateTemp) {
          } else {
            extractPromptTemplateTemp = {};
          }
        }
  
        // console.log("field", field);
        field.fields.forEach((innerfield: any) => {
          if (field.formFieldType === "FIELD_GROUP") {
            extractPromptTemplateTemp = buildInnerPromptTemplate(
              extractPromptTemplateTemp,
              innerfield
            );
          } else {
            extractPromptTemplateTemp[resolvedField][
              innerfield.fieldName || innerfield.displayName
            ] = buildInnerPromptTemplate(
              extractPromptTemplateTemp[resolvedField],
              innerfield
            );
          }
        });
        return extractPromptTemplateTemp[resolvedField];
      } else {
        extractPromptTemplateTemp[field.fieldName || field.displayName] = "";
        return extractPromptTemplateTemp;
      }
    };
    let extractPromptTemplateTemp: Record<any, string | Array<any>> = {};
    template?.fields?.forEach((field: any) => {
      buildInnerPromptTemplate(extractPromptTemplateTemp, field);
    });
    //console.log("extractPromptTemplateTemp", extractPromptTemplateTemp);
    
    const promptTemplate = `You are medical transcriber.Your job is extract relevant content from following
    context and return a json response. Use the JSON template below. Please make sure new key's are not added
    inthe json schema. if its array datatype, you can create more than one items in the array. Also any date value to
    use yyyy-mm-dd format. Translate by mouth as orally
    ${JSON.stringify(extractPromptTemplateTemp)
      .replace(/{/gi, "{{")
      .replace(/}/gi, "}}")}
    use below mechanism to calculate symptom presence:
    0. No (enter 0 for symptom frequency)
    1. Yes (enter 0-3 for symptom frequency)
    9. No Response
    use below instructions to calculate symptom frequency:
    0. Never or 1 day
    1. 2-6 days (several days)
    2. 7-11 days (half or more of the days)
    3. 12-14 days (nearly every day)
    context: ${transcriptText}
    `;

    return promptTemplate;
  };

export const buildLHCSPromptTemplate = (template: any, transcriptText: string) => {
  console.log("LHCPromptTemplate", template);

  if(template) {
    const promptTemplate = `You are medical transcriber.Your job is extract relevant content from following
    context and return a json response. Use the JSON template below. Please make sure new key's are not added
    inthe json schema. if its array datatype, you can create more than one items in the array. Also any date value to
    use yyyy-mm-dd format. use _meta to understand possible values for each field
    ${JSON.stringify(template)
      .replace(/{/gi, "{{")
      .replace(/}/gi, "}}")}
    use below mechanism to calculate symptom presence:
    0. No (enter 0 for symptom frequency)
    1. Yes (enter 0-3 for symptom frequency)
    9. No Response
    use below instructions to calculate symptom frequency:
    0. Never or 1 day
    1. 2-6 days (several days)
    2. 7-11 days (half or more of the days)
    3. 12-14 days (nearly every day)
    context: {}
    `;
  
  console.log(promptTemplate);
  return JSON.stringify(template);
  }
  
  return null;

}