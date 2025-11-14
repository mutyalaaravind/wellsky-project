import { Env } from "./types";
import { SearchContextProvider } from "./context/SearchContext";
import SearchContainer from "./SearchContainer";
import DocsSearchContainer from "./DocsSearchContainer";
import { Radio, RadioGroup, Stack } from "@chakra-ui/react";
import React from "react";

type SearchGlassProps = {
  env: Env;
  identifier: string;
};

export const SearchGlass = ({ env, identifier }: SearchGlassProps) => {
  const [searchType, setSearchType] = React.useState("docs");

  return (
    <SearchContextProvider>
      {/* <RadioGroup
        onChange={(e: any) => {
          setSearchType(e);
        }}
        value={searchType}
      >
        <Stack direction="row">
          <Radio value="docs">Documents</Radio>
          <Radio value="fhir">FHIR</Radio>
        </Stack>
      </RadioGroup> */}
      {/* {searchType === "fhir" && ( */}
        <SearchContainer env={env} identifier={identifier} />
      {/* )}
      {searchType === "docs" && (
        <DocsSearchContainer env={env} identifier={identifier} />
      )} */}
    </SearchContextProvider>
  );
};
