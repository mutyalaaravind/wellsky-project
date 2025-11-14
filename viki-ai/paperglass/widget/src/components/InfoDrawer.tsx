import {
  Drawer,
  DrawerOverlay,
  DrawerContent,
  DrawerCloseButton,
  DrawerHeader,
  DrawerBody,
} from "@chakra-ui/react";

import { EvidenceViewer,EvidenceViewerProps } from "../EvidenceViewer";

const highlightWords = (text: string, words: string[]) => {
  let newText = text;
  words.forEach((word) => {
    const re = new RegExp(word, "ig");
    newText = newText.replace(
      re,
      `<b style="background-color: yellow;">${word}</b>`,
    );
  });
  return newText;
};

function InfoDrawer(props: any) {
  return (
    <Drawer onClose={props.onClose} isOpen size="xl">
      <DrawerOverlay />
      <DrawerContent>
        <DrawerCloseButton />
        <DrawerHeader>{` Contents`}</DrawerHeader>
        {props.evidenceViewerProps?.identifier && <DrawerBody><EvidenceViewer identifier={props.evidenceViewerProps?.identifier || ""} substring={props.evidenceViewerProps?.substring || ""} /></DrawerBody>}
        {!props.evidenceViewerProps?.identifier && <DrawerBody>
          <pre
            style={{
              textWrap: "wrap",
            }}
            dangerouslySetInnerHTML={
              props.data
                ? {
                    __html: highlightWords(
                      atob(props.data),
                      props.search?.split(" "),
                    ),
                  }
                : { __html: "" }
            }
          ></pre>
        </DrawerBody>}
      </DrawerContent>
    </Drawer>
  );
}

export default InfoDrawer;
