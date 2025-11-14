import { AddIcon, CloseIcon, Search2Icon } from "@chakra-ui/icons";
import {
  Flex,
  HStack,
  Input,
  InputGroup,
  InputLeftElement,
  Tag,
  TagLabel,
  TagLeftIcon,
} from "@chakra-ui/react";
import { useSearchContext } from "../context/SearchContext";
import { getColumnLabel } from "../utils/helpers";
import { Tags } from "./Tags";

export interface SearchBarProps {
  tags: string[];
}

function SearchBar(props: SearchBarProps) {
  const { state, dispatch } = useSearchContext();
  const tags = props.tags;

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    dispatch?.({ type: "setSearch", payload: event.target.value });
  };

  return (
    <Flex p={2} direction="column">
      <InputGroup>
        <InputLeftElement pointerEvents="none">
          <Search2Icon color="gray.300" />
        </InputLeftElement>
        <Input
          type="tel"
          placeholder="Search"
          value={state.search}
          onChange={handleSearchChange}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              dispatch?.({ type: "setSearchValue", payload: state.search });
            }
          }}
        />
      </InputGroup>
      {/* <Tags tags={tags} /> */}
      {/* <HStack spacing={2} mt={1}>
        {tags.map((tag) => (
          <Tag
            key={tag}
            variant="subtle"
            colorScheme="cyan"
            size="lg"
            onClick={() =>
              dispatch?.({
                type: state.selectedTags.includes(tag)
                  ? "removeSelectedTags"
                  : "addSelectedTags",
                payload: tag,
              })
            }
          >
            {state.selectedTags.includes(tag) ? (
              <TagLeftIcon as={CloseIcon} />
            ) : (
              <TagLeftIcon boxSize="12px" as={AddIcon} />
            )}

            <TagLabel>{getColumnLabel(tag)}</TagLabel>
          </Tag>
        ))}
      </HStack> */}
    </Flex>
  );
}

export default SearchBar;
