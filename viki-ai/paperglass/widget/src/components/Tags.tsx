import { AddIcon, CloseIcon } from "@chakra-ui/icons";
import { HStack, Tag, TagLabel, TagLeftIcon } from "@chakra-ui/react"
import { getColumnLabel } from "../utils/helpers";
import { useSearchContext } from "../context/SearchContext";

interface SearchBarProps {
    tags: string[];
  }

export const Tags = (props:SearchBarProps) => {
    const { state, dispatch } = useSearchContext();
    return (
        <HStack spacing={2} mt={1}>
            {props.tags.map((tag) => (
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
        </HStack>
    )
}