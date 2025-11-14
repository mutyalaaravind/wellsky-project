import {
  CheckOutlined,
  EditOutlined,
} from "@ant-design/icons";
import { Input} from "antd";
import { useState } from "react";


import { Box } from "@chakra-ui/react";

function InputWithEdit(props: any) {
  const {  evidencePopover } = props;
  
  const [isEdit, setIsEdit] = useState(false);

  const onFieldChange = (e: any) => {
    if (props.formFieldType === "RADIO") {
      props.onChange({
        radioValues: e.target.value,
      });
    } else {
      props.onChange(e.target.value);
    }
  };

  let value;
  if (props.formFieldType === "RADIO") {
    value = props.value?.radioValues;
  } else {
    value = props.value;
  }

  if (isEdit) {
    return (
      <div
        style={{
          display: "flex",
          flexDirection: "column",
        }}
      >
        <div style={{ display: "flex", gap: 4 }}>
          {props.label}
          <CheckOutlined onClick={() => setIsEdit(false)} />
        </div>

        <Input value={value} onChange={onFieldChange} />
      </div>
    );
  }

  return (
    <div style={{ display: "flex", flexDirection: "column" }}>
      <div style={{ display: "flex", gap: 4 }}>
        {props.label}
        <EditOutlined onClick={() => setIsEdit(true)} />
        {props.field?.displayName && (
          <Box children={evidencePopover} />
        )}
      </div>
      <div>
        <span>{value}</span>
        <Input {...props} value={value} style={{ display: "none" }} />
      </div>
    </div>
  );
}

export default InputWithEdit;
