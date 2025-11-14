import { TableCellProps, TableColumnHeaderProps } from "@chakra-ui/react";
import { get } from "lodash";
import { Env } from "../types";

export const ucFirst = (str: string) => {
  return str[0].toUpperCase() + str.slice(1);
};

export const getColumnLabel = (
  name: string,
  extraArgs?: {
    columnNameMap?: Record<string, any>;
    schema?: string;
    columnStyles?: {
      [key: string]: TableCellProps | TableColumnHeaderProps;
    };
  },
) => {
  const { columnNameMap, schema } = extraArgs || {};
  if (columnNameMap) {
    const path = [schema, name].filter((i) => i).join(".");
    const label = get(columnNameMap, path);

    if (label) {
      return label;
    }
  }

  return ucFirst(
    name.replace(/([A-Z])/gm, (match) => {
      return " " + match;
    }),
  );
};

export function getColumnsFromData(
  datas: Record<string, any>[],
  extraArgs?: {
    columnNameMap?: Record<string, any>;
    schema?: string;
    columnStyles?: {
      [key: string]: TableCellProps | TableColumnHeaderProps;
    };
    hideColumns?: string[];
  },
) {
  const { columnStyles, hideColumns } = extraArgs || {};
  const uniqueSet = new Set<string>();

  for (const data of datas) {
    const keys = Object.keys(data);
    for (const k of keys) {
      if (hideColumns?.includes(k)) {
        continue;
      }
      uniqueSet.add(k);
    }
  }

  const uniqueKeys = Array.from(uniqueSet);

  return uniqueKeys.map((k) => {
    return {
      id: k,
      title: getColumnLabel(k, extraArgs),
      dataIndex: k,
      cssProps: columnStyles?.[k],
    };
  });
}

export const fetchSearchData = async (
  env: Env,
  search: string,
  identifier: string,
) => {
  const response = await fetch(
    `${env.API_URL}/api/search_fhir?identifier=${identifier}&search_query=${search}`,
  );
  const data = await response.json();
  return data;
};

export const getReferenceFieldPath = (field: any) => {
  const suffix = "_original_text_reference";
  const fieldName = field.pathedName || field.fieldName || field.displayName;

  if (Array.isArray(fieldName)) {
    return fieldName.map((p: string, i: number) => {
      if (i === fieldName.length - 1) {
        return p + suffix;
      }
      return p;
    });
  }

  return fieldName + suffix;
};

export const scrollToCustomFormField = (
  mount: string,
  field: any,
  env?: any,
  transcriptId?: string,
  transcriptText?: string,
  extractedText?: string,
  setEvidences?: (evidence: Array<any>) => void,
) => {
  console.log("popup field", field, transcriptId, transcriptText);
  if (transcriptId) {
    try {
      // axios({
      //   method: 'post',
      //   url: `${(env as any).API_URL}/api/search`,
      //   headers:{},
      //   data:{
      //     transcript_id: transcriptId,
      //     query_strings: [field.displayName]
      //   }
      // }
      // ).then((data)=>{
      //   console.log("embedding api", data.data);
      //   if (data.data && data.data.length > 0) {
      //     setEvidences?.(data.data);
      //   }
      // }).catch((error:any)=>{
      //   return "search something errored"
      // })
    } catch (ex) {
      console.log(ex);
    }
  } else {
    setEvidences?.([]);
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

export const getDebugValue = () => {
  let searchParams = new URLSearchParams(window.location.search);
  const debug = searchParams.get("debug") === "true";
  console.log({ debug });
  return debug;
};

export const getAnnotation = (data: any, pageResults: any) => {
  console.log("gettting data for annotation", data, pageResults);
  const normalizedVertices = data.normalized_vertices;
  //let pageNumber = 1;
  // if(pageResults){
  //   Object.keys(pageResults).forEach((key) => {
  //     const pageResult = pageResults[key];
  //     if(pageResult["summarizer"] === data.page_result_id){
  //       pageNumber = parseInt(key);
  //       console.log("found page with result", pageNumber, key, pageResult, data.page_result_id);
  //     }
  //   });
  // }
  // console.log("normalized vertices", normalizedVertices, pageNumber);
  return {
    x: data.x,
    y: data.y,
    width: data.width,
    height: data.height,
    text: data.text,
    page: data.page,
  }
  //return {
  //      x: normalizedVertices[0]['x'],
  //      y: normalizedVertices[0]['y'],
  //      width: normalizedVertices[2]['x'] - normalizedVertices[0]['x'],
  //      height: normalizedVertices[2]['y'] - normalizedVertices[0]['y'],
  //}
}

export const setToken = (token: string) => {
  localStorage.setItem("token", token);
}

export const getToken = () => {
  return localStorage.getItem("token");
}
