import ReactDOM from "react-dom/client";
import { ChakraProvider, Portal } from "@chakra-ui/react";
import { lightTheme } from "@mediwareinc/wellsky-dls-react";
import createCache from "@emotion/cache";
import { CacheProvider } from "@emotion/react";

import reportWebVitals from "./reportWebVitals";
import { MedWidgetButton } from "./MedWidget";
import css from "./index.css";
import fonts from "./fonts.css";
import { AuthProvider } from "context/AuthContext";
import { useRef } from "react";
import { ShadowDOMContext } from "context/ShadowDOMContext";
import { useStyles } from "hooks/useStyles";
import { jwtDecode } from "jwt-decode";
import MedWidgetInstance from "utils/MedWidgetInstance";
import { getSingletonInstance } from "utils/helpers";
import { EventBus } from "utils/eventBus";
import { MedWidgetInstanceContextProvider } from "context/MedWidgetInstanceContext";
import { EnvProvider } from "context/EnvContext";
import useEnvJson from "hooks/useEnvJson";
import { Env } from "types";

type MedWidgetAppProps = {
  root: ShadowRoot;
  patientId: string;
  token: string;
  ehrToken: string;
  oktaToken: string;
};

const MedWidgetWrapper = ({
  root,
  patientId,
  token,
  ehrToken,
  oktaToken,
}: MedWidgetAppProps) => {
  // This component puts entire app inside a Chakra Portal.
  //
  // Why? Because Chakra uses portals to render popups/dialogs/tooltips.
  // Chakra's default portal container is `document.body`, which is outside the shadow DOM, and we cannot change it.
  //
  // This means that popups/dialogs/tooltips will not be rendered inside the shadow DOM, and will be rendered outside the shadow DOM.
  //
  // However, by default Chakra will respect its parent portal. So if we put the entire app inside a Chakra portal,
  // all child portals will be rendered inside the parent portal (that we create here), which is inside the shadow DOM.
  const cache = createCache({ key: "chakra-css", container: root });
  const rootRef = useRef<ShadowRoot>(root);
  useStyles(css);
  const env = useEnvJson<Env>();
  return (
    <Portal containerRef={rootRef as any}>
      <CacheProvider value={cache}>
        <ChakraProvider theme={lightTheme}>
          <AuthProvider value={{ patientId, token, ehrToken, oktaToken }}>
              {env ? <EnvProvider value={env}>
                <MedWidgetButton />
              </EnvProvider>
              : <>Loading...</>}
          </AuthProvider>
        </ChakraProvider>
      </CacheProvider>
    </Portal>
  );
};

type InitMedWidgetButtonProps = {
  el: HTMLElement;
  patientId: string;
  token: string;
  ehrToken: string;
  oktaToken: string;
  options?: {
    enableUpload?: boolean;
  };
};

(window as any).initMedWidgetButton = ({
  el,
  token,
  ehrToken,
  oktaToken,
  options,
}: InitMedWidgetButtonProps) => {
  const shadowRoot = el.attachShadow({ mode: "open" });
  const reactRoot = ReactDOM.createRoot(shadowRoot);
  const widgetId = crypto.randomUUID();

  const eventBus = getSingletonInstance(
    `${widgetId}-eventBus`,
    () => new EventBus(),
  );

  const medWidgetInstance = getSingletonInstance(
    `${widgetId}-instance`,
    () => new MedWidgetInstance(eventBus),
  );

  if (options) {
    medWidgetInstance.setConfig(options);
  }

  // Ensure that fonts CSS is loaded OUTSIDE of Shadow DOM, or the fonts will break: https://github.com/mdn/interactive-examples/issues/887#issuecomment-432418008
  fonts.use({ target: document.head as any });

  const patientId = jwtDecode<{ patientId: string }>(token).patientId;

  reactRoot.render(
    <ShadowDOMContext.Provider value={{ shadowRoot }}>
      <MedWidgetInstanceContextProvider medWidgetInstance={medWidgetInstance}>
        <MedWidgetWrapper
          root={shadowRoot}
          patientId={patientId}
          token={token}
          ehrToken={ehrToken}
          oktaToken={oktaToken}
        />
      </MedWidgetInstanceContextProvider>
    </ShadowDOMContext.Provider>,
  );

  medWidgetInstance?.onUnMount(() => {
    reactRoot?.unmount?.();
    fonts?.unuse?.();
  });

  return medWidgetInstance;

  // return () => {
  //   reactRoot.unmount();
  //   fonts.unuse();
  // };
};

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
