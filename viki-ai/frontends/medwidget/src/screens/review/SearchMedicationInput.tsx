import { Flex, Spinner } from "@chakra-ui/react";
import { TextInput } from "@mediwareinc/wellsky-dls-react";
import { CloseCircleOutline } from "@mediwareinc/wellsky-dls-react-icons";
import { DebouncedState } from "use-debounce";

export type SearchMedicationInputProps = {
  setSearchValue: (value: string) => void;
  debounceSearch: DebouncedState<(value: string) => void>;
  searchValue: string;
  clearSearch: () => void;
  searchRef: React.LegacyRef<HTMLInputElement> | undefined;
  fieldWiseErrors?: Map<string, string[]>;
  completionBusy: boolean;
};

function SearchMedicationInput({
  setSearchValue,
  searchValue,
  clearSearch,
  searchRef,
  fieldWiseErrors,
  completionBusy,
  debounceSearch,
}: SearchMedicationInputProps) {
  return (
    <Flex
      position="relative"
      w="full"
      data-pendoid="search-medication-container"
    >
      <TextInput
        label="Search"
        onChange={(event) => {
          setSearchValue((event.target as any).value);
          debounceSearch((event.target as any).value);
        }}
        onKeyDown={(e) => {
          if (searchValue && (e.code === "Escape" || e.key === "Escape")) {
            e.preventDefault();
            e.stopPropagation();
            clearSearch();
          }
        }}
        inputProps={{
          ref: searchRef,
          value: searchValue,
          defaultValue: "-",
          isInvalid: fieldWiseErrors?.has("medispanId"),
        }}
        isInvalid={fieldWiseErrors?.has("medispanId")}
        // helpText="Search for medication by name"
        errorMessage={fieldWiseErrors?.get("medispanId")?.[0]}
        data-pendoid="search-medication-input"
      />
      {completionBusy || debounceSearch.isPending() ? (
        <div
          style={{
            position: "absolute",
            top: "50%",
            marginTop: "-20px",
            right: "8px",
            opacity: debounceSearch.isPending() ? "0.25" : "1",
          }}
        >
          <Spinner size="lg" />
        </div>
      ) : searchValue ? (
        <div
          style={{
            position: "absolute",
            top: "50%",
            marginTop: "-20px",
            right: "8px",
            opacity: debounceSearch.isPending() ? "0.25" : "1",
          }}
        >
          <CloseCircleOutline
            style={{
              cursor: "pointer",
              fontSize: "40px",
            }}
            onClick={clearSearch}
            data-pendoid="cancel-search-button"
          />
        </div>
      ) : null}
    </Flex>
  );
}

export default SearchMedicationInput;
