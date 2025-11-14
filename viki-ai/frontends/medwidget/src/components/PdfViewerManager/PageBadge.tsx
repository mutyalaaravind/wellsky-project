import { Box, Tag, TagLabel, Tooltip } from "@chakra-ui/react";
import { CheckSimple } from "@mediwareinc/wellsky-dls-react-icons";
import { useCallback } from "react";
import { PageProfile } from "store/storeTypes";
import { usePdfViewerContext } from "./context/PdfViewerContext";

type PageBadgeProps = {
  documentId: string;
  profile?: PageProfile;
  extractionType: string;
  pageNumber: number;
};

const PageBadge = ({
  documentId,
  profile,
  extractionType,
  pageNumber,
}: PageBadgeProps) => {
  const isToggled = Boolean(profile?.isSelected);

  const { updatePageProfileState } = usePdfViewerContext();

  const toggleState = useCallback(() => {
    updatePageProfileState?.(documentId, extractionType, pageNumber, {
      isSelected: !isToggled,
    });
  }, [
    documentId,
    extractionType,
    isToggled,
    updatePageProfileState,
    pageNumber,
  ]);

  if (!profile?.numberOfItems) {
    return null;
  }

  return (
    <Box
      position="absolute"
      top="0"
      right="0"
      margin="4px auto"
      padding="0"
      paddingLeft="0.25rem"
      paddingRight="0.25rem"
      zIndex={1}
    >
      <Tooltip
        label={
          isToggled ? "Click to remove medications" : "Click to add medications"
        }
        aria-label="A tooltip"
      >
        <Tag
          variant="subtle"
          colorScheme={isToggled ? "red" : "gray"}
          style={{
            display: "inline-flex",
            maxWidth: 180,
            padding: "3px 4px",
            justifyContent: "center",
            alignItems: "flex-start",
            gap: 4,
            color: "white",

            borderRadius: 50,
            background: "var(--palette-accent-ws-elm-500, #228189)",

            ...(isToggled
              ? {}
              : {
                  border: "1px solid var(--Secondary-ws-elm-700, #196E76)",
                  background: "var(--Secondary-ws-elm-50, #E4F0F1)",
                  color:
                    "var(--Secondary-ws-elm-700, var(--palette-accent-ws-elm-700, #196E76))",
                }),
          }}
          size="xs"
          onClick={toggleState}
        >
          {isToggled ? (
            <span>
              <CheckSimple
                style={{
                  fontSize: 20,
                  fontWeight: "bolder",
                  padding: 0,
                }}
              />
            </span>
          ) : (
            <span>+</span>
          )}
          <TagLabel>{profile?.numberOfItems}</TagLabel>
        </Tag>
      </Tooltip>
    </Box>
  );
};

export default PageBadge;
