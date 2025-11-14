import axios from "axios"
import { useState } from "react"


export const getReferenceFieldPath = (field: any ) => {
  const suffix = '_original_text_reference'
  const fieldName = field.pathedName || field.fieldName || field.displayName

  if(Array.isArray(fieldName)) {
    return fieldName.map((p: string, i: number) => {
      if (i === fieldName.length - 1) {
        return p + suffix
      }
      return p
    })
  }

  return fieldName + suffix
}

export const scrollToCustomFormField = (mount: string,
      field: any,
      env?: any,
      transcriptId?:string,
      transcriptText?: string,
      extractedText?:string,
      setEvidences?:(evidence:Array<any>)=>void) => {
  console.log("popup field",field,transcriptId,transcriptText );
  if(transcriptId){
    try{
        axios({
          method: 'post',
          url: `${(env as any).API_URL}/api/search`,
          headers:{},
          data:{
            transcript_id: transcriptId,
            query_strings: [field.displayName]
          }
        }
        ).then((data)=>{
          console.log("embedding api", data.data);
          if (data.data && data.data.length > 0) {
            setEvidences?.(data.data);
          }
        }).catch((error:any)=>{
          return "search something errored"
        })
    } catch (ex) {
      console.log(ex);
    }
  }else{
    setEvidences?.([])
  }

  let element = document
    .getElementById(mount)
    ?.shadowRoot?.getElementById(field.pathedName?.join("_"));

  if (!element) {
    element = document
      .getElementById(mount)
      ?.shadowRoot?.getElementById(field.pathedName?.join("."));
  }
  element?.scrollIntoView({
    behavior: "smooth",
    block: "center",
    inline: "nearest",
  });
  return "";
};



export function setNestedValue(key: string, val: any, obj: any = {}) {
  const nestedPath = key.split(".");

  if (nestedPath.length > 1) {
    const head = nestedPath.shift();
    if (head)
      obj[head] = setNestedValue(nestedPath.join("."), val, obj[head] || {});
  } else {
    obj[key] = val;
  }
  return obj;
}

export const convertToNestedObject = (data: any) => {
  let res = {};
  if (data) {
    const keys = Object.keys(data);
    for (const k of keys) {
      setNestedValue(k, data[k], res);
    }

    return res;
  }
  return {};
};
