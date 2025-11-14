import { Card, Form } from "antd";
import { useState } from "react";
import InputWithJSON from "./InputWithJSON";
import {
  CheckOutlined,
  EditOutlined
} from "@ant-design/icons";

import { Box } from "@chakra-ui/react";

function EditableCard(props: any) {
  const { field, evidencePopover } = props;
  const [isEdit, setIsEdit] = useState(false);
  const [editCompleteFlag, setEditCompleteFlag] = useState<any>(null);
  
  return (
    <Card
      size="small"
      title={
        <div style={{ display: "flex", gap: 4 }}>
          <label>{field.displayName}</label>
          {isEdit ? (
            <CheckOutlined onClick={() => setEditCompleteFlag(Date.now())} />
          ) : (
            <EditOutlined onClick={() => setIsEdit(true)} />
          )}
          <Box children={evidencePopover} />
        </div>
      }
      key={field.pathedName || field.fieldName || field.displayName}
      style={{ marginBottom: 10, width: "100%" }}
    >
      <Form.Item
        key={field.pathedName || field.fieldName || field.displayName}
        name={field.pathedName || field.fieldName || field.displayName}
      >
        <InputWithJSON
          isEdit={isEdit}
          setIsEdit={setIsEdit}
          editCompleteFlag={editCompleteFlag}
          setEditCompleteFlag={setEditCompleteFlag}
        />
      </Form.Item>
    </Card>
  );
}

export default EditableCard;
