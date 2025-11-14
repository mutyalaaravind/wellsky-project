
import { Box } from "@chakra-ui/react";

function ReadOnlyField(props: any) {
  const { field,  evidencePopover } = props;

  if (!field.displayName) {
    return null;
  }

  return (
    <div style={{ display: "flex", gap: 4 }}>
      {field.displayName}
      <Box children={evidencePopover} />
    </div>
  );
}

export default ReadOnlyField;
