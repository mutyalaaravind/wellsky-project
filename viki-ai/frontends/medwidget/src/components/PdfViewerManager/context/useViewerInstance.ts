import useEventBus from "../store/getEventBus";
import { usePdfWidgetStore } from "../store/pdfViewerStore";
import ViewerInstance from "../store/ViewerInstance";
import { getSingletonInstance } from "utils/helpers";

const useViewerInstance = () => {
  const eventBusInstance = useEventBus();
  const store = usePdfWidgetStore();

  const viewerInstance = getSingletonInstance(
    store.storeId + "viewerInstance",
    () => new ViewerInstance(eventBusInstance, store),
  );

  return viewerInstance;
};

export default useViewerInstance;
