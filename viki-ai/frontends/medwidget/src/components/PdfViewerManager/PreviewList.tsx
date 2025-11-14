import { ChevronDownIcon, ChevronUpIcon } from "@chakra-ui/icons";
import {
  Box,
  Flex,
  HStack,
  Icon,
  IconButton,
  Tooltip,
  useToken,
  VStack,
} from "@chakra-ui/react";
import { PageProfile } from "store/storeTypes";
import PageBadge from "./PageBadge";
import { useLayoutEffect, useRef, useState } from "react";
import OverlayLoader from "screens/review/OverlayLoader";

type PreviewListProps = {
  totalPages: number;
  pageNumber: number;
  renderPreview: (
    pageNumber: number,
    ref: HTMLCanvasElement,
    cb?: () => void,
  ) => void;
  onPageChange: (pageNumber: number) => void;
  documentId: string;
  currentDocumentPageProfile?: Record<
    string | number,
    Record<number, PageProfile>
  >;
  extractionType?: string;
};

type PreviewCanvasProps = {
  documentId: string;
  i: number;
  renderPreview: (
    pageNumber: number,
    ref: HTMLCanvasElement,
    cb?: () => void,
  ) => void;
  onPageChange: (pageNumber: number) => void;
  pageNumber: number;
};

const PreviewCanvas = ({
  documentId,
  i,
  renderPreview,
  onPageChange,
  pageNumber,
}: PreviewCanvasProps) => {
  const [pageHighlightColor] = useToken(
    // the key within the theme, in this case `theme.colors`
    "colors",
    // the subkey(s), resolving to `theme.colors.red.100`
    ["elm.700"],
    // a single fallback or fallback array matching the length of the previous arg
  );

  const [loading, setLoading] = useState(true);

  const ref = useRef<HTMLCanvasElement | null>(null);

  useLayoutEffect(() => {
    if (ref.current) {
      try {
        renderPreview(i + 1, ref.current, () => setLoading(false));
      } catch (error) {
        console.error(error);
      }
    }
  }, [i, renderPreview]);

  return (
    <>
      {loading && <OverlayLoader size="xs" />}
      <canvas
        key={documentId + i}
        id={documentId + i}
        ref={ref}
        onClick={() => onPageChange(i + 1)}
        style={{
          cursor: "pointer",
          width: "100%",
          borderTop: "1px solid rgba(0, 0, 0, 0.5)",
          borderBottom: "1px solid rgba(0, 0, 0, 0.5)",
          boxShadow:
            pageNumber - 1 === i ? `0 0 16px ${pageHighlightColor}` : "none",
        }}
      />
    </>
  );
};

const PreviewList = ({
  totalPages = 0,
  pageNumber = 1,
  renderPreview,
  onPageChange,
  documentId,
  currentDocumentPageProfile,
  extractionType = "medication",
}: PreviewListProps) => {
  // const highlighted = props.pageNumber ===;

  return (
    <Flex direction="column" maxW="10vw" minW="100px">
      <HStack
        color="#FFFFFF"
        backgroundColor="#10222F"
        // background={pageHighlightColor}
        gap={"0.5rem"}
        padding={"0.5rem"}
        height="40px"
        alignItems="center"
        justifyContent={"center"}
      >
        <Tooltip
          label="Select previous page of interest"
          aria-label="A tooltip"
        >
          <IconButton
            variant="link"
            aria-label="Previous Page"
            onClick={() => {
              // findNextPageOfIntrest("previous");
            }}
            isDisabled={pageNumber === 1}
            style={{
              color: "white",
              transform: "scale(2)",
            }}
            data-pendoid="previous-page"
          >
            <Icon as={ChevronUpIcon} />
          </IconButton>
        </Tooltip>

        <Tooltip label="Select next page of interest" aria-label="A tooltip">
          <IconButton
            variant="link"
            aria-label="Next Page"
            onClick={() => {
              // findNextPageOfIntrest("next");
            }}
            isDisabled={pageNumber === totalPages}
            style={{
              color: "white",
              transform: "scale(2)",
            }}
            data-pendoid="next-page"
          >
            <Icon as={ChevronDownIcon} />
          </IconButton>
        </Tooltip>
      </HStack>
      <VStack overflowX="auto" p={2} gap={2}>
        {Array(totalPages)
          .fill(0)
          .map((_, i) => (
            <Flex
              key={"flex" + documentId + i}
              padding={1}
              cursor="pointer"
              w="100%"
              position="relative"
            >
              <Box w={"100%"}>
                <PageBadge
                  pageNumber={i + 1}
                  documentId={documentId}
                  extractionType={extractionType}
                  profile={
                    currentDocumentPageProfile?.[extractionType]?.[i + 1]
                  }
                  data-pendoid={`page-badge-${documentId}-${i + 1}`}
                />
              </Box>
              <PreviewCanvas
                data-pendoid={`preview-canvas-${documentId}-${i + 1}`}
                key={documentId + i}
                documentId={documentId}
                i={i}
                renderPreview={renderPreview}
                onPageChange={onPageChange}
                pageNumber={pageNumber}
              />
            </Flex>
          ))}
      </VStack>
    </Flex>
  );
};

export default PreviewList;
