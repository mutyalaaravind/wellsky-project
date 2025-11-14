import {
  TableContainer,
  Table,
  Thead,
  Tr,
  Th,
  Tbody,
  Td,
} from "@chakra-ui/react";
import { Suggestion } from "types";

type MedicationSuggestionsTableProps = {
  suggestions: Suggestion[];
  onSelect?: (
    suggestion: MedicationSuggestionsTableProps["suggestions"][0],
  ) => void;
};

const MedicationSuggestionsTable = ({
  suggestions,
  onSelect,
}: MedicationSuggestionsTableProps) => {
  return (
    <TableContainer className="medication-autocomplete-table">
      <Table size="sm" variant="striped">
        <Thead>
          <Tr>
            <Th>Generic Name</Th>
            <Th>Brand Name</Th>
            <Th>Route</Th>
            <Th>Form</Th>
            <Th>Strength</Th>
            <Th>Packaging</Th>
          </Tr>
        </Thead>
        <Tbody>
          {suggestions.map((suggestion) => (
            <Tr
              key={suggestion.toString()}
              style={{ cursor: "pointer" }}
              onClick={() => {
                onSelect?.(suggestion);
              }}
            >
              <Td>{suggestion.generic_name}</Td>
              <Td>{suggestion.brand_name}</Td>
              <Td>{suggestion.route}</Td>
              <Td>{suggestion.form}</Td>
              <Td>
                {suggestion?.strength?.value} {suggestion?.strength?.unit}
              </Td>
              <Td>
                {suggestion?.package?.value} {suggestion?.package?.unit}
              </Td>
            </Tr>
          ))}
        </Tbody>
      </Table>
    </TableContainer>
  );
};

export default MedicationSuggestionsTable;
