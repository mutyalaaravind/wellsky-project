import React from "react";
import { Tag, TagLabel, Tooltip } from "@chakra-ui/react";

import { PageProfile } from "store/storeTypes";

import { ContextDocumentItemFilter } from "tableOfContentsTypes";

import "./PageBadge.css";
import { CheckSimple } from "@mediwareinc/wellsky-dls-react-icons";
import { usePageOcrApi } from "hooks/usePageOcr";
import { useConfigData } from "context/AppConfigContext";

interface PageBadgeProps {
  documentId: string;
  page: number;
  pageProfile: PageProfile;
  onPageProfileSelection: (
    documentId: string,
    pageIndex: number,
    isSelected: boolean,
  ) => void;
  pageProfileState: Record<string, ContextDocumentItemFilter>;
  getPageProfileState: (
    documentId: string,
    profileType: string,
    page: number,
  ) => boolean;
}

const PageBadge: React.FC<PageBadgeProps> = ({
  documentId,
  page,
  pageProfile,
  onPageProfileSelection,
  pageProfileState,
  getPageProfileState,
}) => {
  const profileType: string = "medication";
  const {triggerOcr} = usePageOcrApi();

  const config = useConfigData();

  const pageNumber = page + 1;
  const isToggled = getPageProfileState(documentId, profileType, pageNumber);

  const toggleState = () => {
    onPageProfileSelection(documentId, pageNumber, !isToggled);
    if (!isToggled && config.ocrTriggerConfig.enabled && config.ocrTriggerConfig.touchPoints.bubbleClick) {
      triggerOcr( documentId, pageNumber);
    }
    
  };

  return (
    <div
      style={{
        position: "absolute",
        top: "1rem",
        margin: "4px auto",
        padding: "0",
        paddingLeft: "0.25rem",
        paddingRight: "0.25rem",
        width: "100%",
        display: "flex",
        justifyContent: "right",
      }}
    >
      <span className="badge-container">
        {/* <Badge count={pageProfile.numberOfItems}></Badge> */}
        <Tooltip
          label={
            isToggled
              ? "Click to remove medications"
              : "Click to add medications"
          }
          aria-label="A tooltip"
        >
          <Tag
            key={page}
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

              // backgroundColor: isToggled ? '#B02828' : 'gray',
              // paddingLeft: "0.25rem",
              // paddingRight: "0.25rem",
              // cursor: "pointer",
              // borderRadius: "2rem",
              // height: "2rem"
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
            <TagLabel>{pageProfile.numberOfItems}</TagLabel>
          </Tag>
        </Tooltip>
      </span>
    </div>
  );
};

export default PageBadge;
