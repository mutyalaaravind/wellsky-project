const approvedpaths = [
  ["patient_name"],
  ["patient_age"],
  ["patient_medications"],
  ["test_section_1", "field_1"],
  ["test_section_1", "field_3", "field_3_1"],
  ["test_section_1", "field_3", "field_3_4"],
];

const formdata = {
  patient_name: "Pratik Soni",
  approved: {
    patient_name: true,
    date_of_birth: false,
    patient_age: true,
    patient_address: false,
    patient_medications: true,
    test_section_1: {
      field_1: true,
      field_2: false,
    },
  },
  date_of_birth: "01-01-2019",
  patient_age: "5",
  patient_address: "123, Main Street, Arizona, USA",
  patient_medications: "Crocin, Ecosprin",
  test_section_1: {
    field_1: "Field 1 value here",
    field_2: "Field 2 value here",
    field_3: {
      field_3_1: "Field 3.1 Here",
      field_3_2: "Field 3.2 Here",
      field_3_3: "Field 3.3 Here",
      field_3_4: {
        field_3_4_1: "Field 3.4.1 Here",
      },
    },
  },
};

const setNestedObjectValue = (
  path: string[] = [],
  obj: any = {},
  value: any = {},
) => {
  let newObj = obj?.[path[0]] || {};

  if (path.length > 1) {
    obj[path[0]] = setNestedObjectValue(
      path.slice(1),
      newObj,
      value?.[path[0]],
    );
  } else {
    obj[path[0]] = value?.[path[0]];
  }

  return obj;
};

function deriveApprovedValues(
  paths: typeof approvedpaths,
  data: typeof formdata,
) {
  let result: Partial<typeof data> = {};

  for (const path of paths) {
    result = setNestedObjectValue(path, result, formdata);
  }

  console.log(JSON.stringify(result, null, 2));
  return result;
}

// deriveApprovedValues(approvedpaths, formdata);

function createNestedPathedValue(obj: any, prevArray: string[] = []) {
  let result:  any[] = [];
  const keys = Object.keys(obj);
    for (const k of keys) {
      if (
        ["string", "number", "boolean", "undefined"].includes(typeof obj[k]) || obj[k] === null
      ) {
        result.push({name:[...prevArray].concat(k), value: obj[k]})
      }
      else {
        result.push(...(createNestedPathedValue(obj[k], [...prevArray, k])))
      }
    }
    return result
    return [...result].filter(item => {
      // console.log(res.value)
      return item.value === true
      // return true
    }).map(item => (item))
}

const res = createNestedPathedValue({
  // patient_name: true,
  // date_of_birth: true,
  // patient_age: true,
  // patient_address: true,
  // patient_medications: true,
  section_2225: true,
  test_section_1: {
    field_1: "Field 1 value here",
    field_2: "Field 2 value here",
    field_3: {
      field_3_1: "Field 3.1 Here",
      field_3_2: "Field 3.2 Here",
      field_3_3: "Field 3.3 Here",
      field_3_4: {
        field_3_4_1: "Field 3.4.1 Here",
        field_3_4_2: true,
      },
    },
  },
}).filter(item => {
  return item.value === true
}).map(item => (item.name));

console.log(JSON.stringify(res, null, 2))
