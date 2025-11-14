import {
  TableContainer,
  Table,
  Thead,
  Tr,
  Th,
  Tbody,
  Td,
} from "@chakra-ui/react";

const MedicationSuggestionsTableV2 = ({
  suggestions,
}: {
  suggestions: any[];
}) => {
  return (
    <TableContainer className="medication-autocomplete-table">
      <Table size="sm" variant="striped" display="block" position="absolute">
        <Thead display="block">
          <Tr display="grid" gridTemplateColumns="repeat(6, 1fr)">
            <Th display="block" whiteSpace="initial">
              Generic Name
            </Th>
            <Th display="block" whiteSpace="initial">
              Brand Name
            </Th>
            <Th display="block" whiteSpace="initial">
              Route
            </Th>
            <Th display="block" whiteSpace="initial">
              Form
            </Th>
            <Th display="block" whiteSpace="initial">
              Strength
            </Th>
            <Th display="block" whiteSpace="initial">
              Packaging
            </Th>
          </Tr>
        </Thead>
        <Tbody display="grid" gridTemplateColumns="1fr">
          {suggestions.map((suggestion) => (
            <Tr
              key={suggestion.toString()}
              style={{ cursor: "pointer" }}
              // onClick={() => {
              //   autoComplete(suggestion);
              //   setSearchValue("");
              //   setSuggestions([]);
              //   setUnlisted(false);
              // }}
            >
              <Td>{suggestion.generic_name}</Td>
              <Td>{suggestion.brand_name}</Td>
              <Td>{suggestion.route}</Td>
              <Td>{suggestion.form}</Td>
              <Td>
                {suggestion.strength.value} {suggestion.strength.unit}
              </Td>
              <Td>
                {suggestion.package.value} {suggestion.package.unit}
              </Td>
            </Tr>
          ))}
        </Tbody>
      </Table>
    </TableContainer>
  );
};

export default MedicationSuggestionsTableV2;
