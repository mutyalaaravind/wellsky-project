import { useEffect, useCallback, useState, useRef } from "react";
import { Header, Tooltip } from "@mediwareinc/wellsky-dls-react";
import { Badge, Box, Spinner, VStack } from "@chakra-ui/react";

import useEnvJson from "hooks/useEnvJson";
import { MagicSparkle } from "icons/MagicSparkle";
import { useBack } from "hooks/useBack";
import { BackProvider } from "context/BackContext";
import { FeedbackScreen } from "screens/feedback/FeedbackScreen";
import { ListingScreen } from "screens/listing/ListingScreen";
import { ReviewScreen } from "screens/review/ReviewScreen";

import css from "./MedWidget.css";
import { Close } from "@mediwareinc/wellsky-dls-react-icons";
import { useStyles } from "hooks/useStyles";
import { ExitConfirmation } from "screens/review/DialogsV2";
import { usePatientProfileStore } from "store/patientProfileStore";
import { ExpandableContextProvider } from "context/ExpandableContext";
import { useMedWidgetInstanceContext } from "context/MedWidgetInstanceContext";
import { AppConfigProvider } from "context/AppConfigContext";

import NewRelicScript from "NewRelicScript";
import { Env } from "types";
import { SlideWithDrawer } from "components/SlideWithDrawer";

export const Slide = ({
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
  const magicSparkle = <MagicSparkle fontSize={24} animated={true} />;
  const backIcon = <Close fontSize={36} />;

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

      <div
        style={{
          position: "fixed",
          transition: "background 0.2s ease-in-out",
          left: "0",
          top: "0",
          width: "100%",
          height: "100%",
          pointerEvents: isOpen ? "auto" : "none",
          backgroundColor: isOpen ? "rgba(0, 0, 0, 0.5)" : "rgba(0, 0, 0, 0.0)",
          zIndex: 100,
        }}
        onClick={toggle}
        data-pendo="widget-background-overlay"
      ></div>
      {/* Inserting Dialog here */}
      <ExitConfirmation
        isOpen={isCloseDialogOpen}
        onOk={() => {
          exitWidget();
        }}
        onCancel={() => setIsCloseDialogOpen(false)}
      />
      {/* Inserting Dialog Ends here */}
      <div
        style={{
          position: "fixed",
          transition: "left 0.4s cubic-bezier(.59,.17,.07,.99)",
          left: isOpen ? "40px" : "100vw",
          top: "0",
          width: "100vw",
          height: "100vh",
          zIndex: 100,
        }}
      >
        <div
          style={{
            position: "absolute",
            top: "100px",
            left: isOpen ? "-40px" : "-56px",
            width: "40px",
            height: "40px",
            backgroundColor: "white",
            // boxShadow: "0 0 10px rgba(0, 0, 0, 0.5)",
            boxShadow: isOpen
              ? "0 0 10px rgba(0, 0, 0, 0.5)"
              : "rgba(0, 0, 0, 0.5) 1px 0px 10px 3px",
            borderRadius: "50% 0 0 50%",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            cursor: "pointer",
          }}
          onClick={toggle}
          data-pendo="widget-toggle-container"
        >
          {!isOpen ? (
            <Tooltip
              label={
                <>
                  <div>Open Extract</div>
                  <div>
                    (<Badge>{isMacOS ? "Option" : "Alt"}</Badge> +{" "}
                    <Badge>M</Badge>)
                  </div>
                </>
              }
              id="widget-toggle-button-tooltip"
            >
              {magicSparkle}
            </Tooltip>
          ) : !isOpen ? (
            magicSparkle
          ) : (
            backIcon
          )}
        </div>
        {!isOpen && (
          <div
            style={{
              position: "absolute",
              top: "100px",
              left: "-16px",
              width: "15px",
              height: "40px",
              backgroundColor: "white",
              boxShadow: "rgba(0, 0, 0, 0.5) 15px 0px 10px 5px",
            }}
          ></div>
        )}
        <div
          style={{
            position: "absolute",
            top: "0",
            left: "0",
            width: "calc(100% - 40px)",
            height: "100%",
            backgroundColor: "white",
            display: "flex",
            flexDirection: "column",
            ...(style ? style : {}),
            ...(isOpen
              ? { boxShadow: "0 0 10px rgba(0, 0, 0, 0.5)" }
              : { display: "none" }),
          }}
        >
          {children}
        </div>
      </div>
    </>
  );
};

enum WidgetState {
  Listing,
  Review,
  Feedback,
}

export const MedWidget = () => {
  // Dialog from wellsky-dls-react does not support full width
  const { medWidgetInstance } = useMedWidgetInstanceContext();
  const env = useEnvJson<Env>();
  const [isOpen, _setIsOpen] = useState(false);
  // const [loading, setLoading] = useState(showLoadingIndicatorWhileImport);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const { hasMedicationUpdates } = usePatientProfileStore();

  const { documentsInReview, setDocumentsInReview } = usePatientProfileStore();
  const [widgetState, setWidgetState] = useState<WidgetState>(
    WidgetState.Listing,
  );
  const backRef = useRef<() => void>(() => {});

  const refreshSignal = useRef(hasMedicationUpdates);

  useEffect(() => {
    refreshSignal.current = hasMedicationUpdates;
  }, [hasMedicationUpdates]);

  const setIsOpen: typeof _setIsOpen = useCallback(
    (open) => {
      if (isOpen && refreshSignal.current) {
        // Send refresh signal instead of refreshing the page
        setIsRefreshing(true);
        setTimeout(() => {
          window.location.reload();
        }, 1000);
      }
      if (!open) {
        setDocumentsInReview([]);
        setWidgetState(WidgetState.Listing);
      }
      _setIsOpen(open);
    },
    [isOpen, setDocumentsInReview],
  );

  const onReviewScreenClose = useCallback(() => {
    setDocumentsInReview([]);
    setWidgetState(WidgetState.Listing);
  }, [setDocumentsInReview]);

  const onFeedbackScreenClose = useCallback(() => {
    backRef.current();
    // Give some time for the slide to close
    setTimeout(() => {
      setWidgetState(WidgetState.Listing);
    }, 500);
  }, []);

  useEffect(() => {
    medWidgetInstance.dispatch("widgetReady", {});
  }, [medWidgetInstance]);

  useEffect(() => {
    medWidgetInstance.dispatch(isOpen ? "open" : "close", {});
  }, [isOpen, medWidgetInstance]);

  const isValidNewRelicEnv =
    env?.NEWRELIC_ACCOUNT_ID &&
    env?.NEWRELIC_TRUST_KEY &&
    env?.NEWRELIC_APPLICATION_ID &&
    env?.NEWRELIC_API_BROWSER_KEY;

  if (!isOpen) {
    return (
      <SlideWithDrawer
        isOpen={isOpen}
        setIsOpen={setIsOpen}
        backRef={backRef}
        isRefreshing={isRefreshing}
      >
        <VStack h="100%" justify="center">
          <Spinner
            thickness="4px"
            speed="0.65s"
            emptyColor="gray.200"
            color="elm.500"
            size="xl"
          />
        </VStack>
      </SlideWithDrawer>
    );
  }

  return (
    <SlideWithDrawer
      isOpen={isOpen}
      setIsOpen={setIsOpen}
      backRef={backRef}
      isRefreshing={isRefreshing}
    >
      {isValidNewRelicEnv && env && (
        <NewRelicScript
          accountID={env.NEWRELIC_ACCOUNT_ID}
          trustKey={env.NEWRELIC_TRUST_KEY}
          applicationID={env.NEWRELIC_APPLICATION_ID}
          licenseKey={env.NEWRELIC_API_BROWSER_KEY}
        />
      )}
      <Header
        showMenu={false}
        title={
          widgetState === WidgetState.Feedback
            ? "User Experience Feedback Survey"
            : "Extract"
        }
        data-pendo="widget-header"
      />
      {env === null ? (
        <div data-pendo="widget-loading">Loading configuration...</div>
      ) : widgetState === WidgetState.Listing ? (
        <ListingScreen
          env={env as any}
          onReviewPressed={(selectedDocuments) => {
            setDocumentsInReview(selectedDocuments);
            setWidgetState(WidgetState.Review);
          }}
          onSubmit={() => {
            setWidgetState(WidgetState.Feedback);
          }}
          documentsInReview={documentsInReview}
          data-pendo="widget-listing-screen"
        />
      ) : widgetState === WidgetState.Review ? (
        <ExpandableContextProvider>
          <ReviewScreen
            env={env as any}
            documentsInReview={documentsInReview}
            onClose={onReviewScreenClose}
            onSubmit={() => {
              setWidgetState(WidgetState.Feedback);
            }}
            data-pendo="widget-review-screen"
          />
        </ExpandableContextProvider>
      ) : (
        <FeedbackScreen onClose={onFeedbackScreenClose} data-pendo="widget-feedback-screen" />
      )}
    </SlideWithDrawer>
  );
};

export const MedWidgetButton = () => {
  useStyles(css);
  return (
    <>
      {/*<PrimaryButton onClick={() => setIsOpen(true)}>MedWidget</PrimaryButton>*/}
      <BackProvider>
        <AppConfigProvider>
          <MedWidget />
        </AppConfigProvider>
      </BackProvider>
    </>
  );
};
