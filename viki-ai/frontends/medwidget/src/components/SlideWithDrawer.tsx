import React, { useCallback, useEffect, useRef, useState } from "react";
import SparkleButton from "./SparkleButton";
import {
  Badge,
  Box,
  Drawer,
  DrawerContent,
  DrawerOverlay,
  Spinner,
  VStack,
} from "@chakra-ui/react";
import { useBack } from "hooks/useBack";
import { usePatientProfileStore } from "store/patientProfileStore";
import { Tooltip } from "@mediwareinc/wellsky-dls-react";
import { ExitConfirmation } from "screens/review/DialogsV2";

export const SlideWithDrawer = ({
  children,
  style,
  backRef,
  isOpen,
  setIsOpen,
  isRefreshing,
}: {
  children: any;
  style?: any;
  backRef?: React.MutableRefObject<() => void>;
  isOpen: boolean;
  isRefreshing: boolean;
  setIsOpen: (open: boolean) => void;
}) => {
  const [isCloseDialogOpen, setIsCloseDialogOpen] = useState(false);
  const { addBackHandler, back } = useBack();
  const { destroyStore, hasMedicationUpdates } = usePatientProfileStore();

  const destroyRef = useRef(destroyStore);

  // Install global keyboard shortcut for opening the widget (Alt + M, or Option + M on Mac)
  useEffect(() => {
    const handleActivationShortcut = (event: KeyboardEvent) => {
      if (
        event.altKey &&
        (event.key.toLowerCase() === "m" || event.code === "KeyM")
      ) {
        setIsOpen(true);
      }
    };
    window.addEventListener("keydown", handleActivationShortcut);
    return () => {
      window.removeEventListener("keydown", handleActivationShortcut);
    };
  });

  // Set backRef
  useEffect(() => {
    if (backRef) {
      backRef.current = back;
    }
  }, [backRef, back]);

  useEffect(() => {
    return addBackHandler(() => {
      setIsOpen(false);
      destroyRef.current?.();
    });
  }, [addBackHandler, setIsOpen]);

  const exitWidget = useCallback(() => {
    setIsCloseDialogOpen(false);
    setIsOpen(false);
    destroyRef.current?.();
  }, [setIsOpen]);

  const reloadFlag = useRef(hasMedicationUpdates);

  useEffect(() => {
    reloadFlag.current = hasMedicationUpdates;
  }, [hasMedicationUpdates]);

  const toggle = useCallback(() => {
    if (!isOpen) {
      setIsOpen(true);
      setIsCloseDialogOpen(false);
    } else {
      // if (reloadFlag.current) {
      //   setIsCloseDialogOpen(true);
      // } else {
      //   exitWidget();
      // }
      exitWidget();
      // setIsOpen(false);
      // console.log(back);
      // TODO: May cause possible bug.
      // back();
    }
  }, [isOpen, setIsOpen, exitWidget]);

  const isMacOS = navigator.platform.toUpperCase().indexOf("MAC") >= 0;

  return (
    <>
      {isRefreshing && (
        <VStack
          position="fixed"
          top="50%"
          left="50%"
          transform="translate(-50%, -50%)"
        >
          <Spinner size={"lg"}></Spinner>
          <Box>Please wait while page is being refreshed...</Box>
        </VStack>
      )}
      {!isOpen && (
        <Tooltip
          label={
            <>
              <div>Open Extract</div>
              <div>
                (<Badge>{isMacOS ? "Option" : "Alt"}</Badge> + <Badge>M</Badge>)
              </div>
            </>
          }
          id="widget-toggle-button-tooltip"
          data-pendo="widget-open-button-tooltip"
        >
          <SparkleButton
            mode={"open"}
            onClick={toggle}
            data-pendo="widget-open-button"
          />
        </Tooltip>
      )}

      <Drawer
        onClose={toggle}
        isOpen={isOpen}
        size={"full"}
        closeOnEsc={false}
        closeOnOverlayClick={false}
        id="coding-widget-drawer"
        data-pendo="widget-drawer-container"
      >
        <DrawerOverlay data-pendo="widget-drawer-overlay" />
        <DrawerContent
          style={{
            // height: "100%",
            maxHeight: "100%",
          }}
          // left="40px"
          // right={0}
          maxWidth="calc(100vw - 40px)"
          pos={"relative"}
          maxH={"100%"}
          data-pendo="widget-drawer-content"
        >
          <ExitConfirmation
            isOpen={isCloseDialogOpen}
            onOk={() => {
              exitWidget();
            }}
            onCancel={() => setIsCloseDialogOpen(false)}
            data-pendo="widget-exit-confirmation-dialog"
          />
          <SparkleButton
            mode={"close"}
            onClick={toggle}
            data-pendo="widget-close-button-x"
          />
          {children}
        </DrawerContent>
      </Drawer>
    </>
  );
};
