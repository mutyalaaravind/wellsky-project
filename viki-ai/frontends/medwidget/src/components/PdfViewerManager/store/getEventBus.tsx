import { EventBus } from "utils/eventBus";
import { usePdfWidgetStore } from "./pdfViewerStore";
import InstanceManager from "utils/InstanceManager";

const useEventBus = () => {
  const manager = new InstanceManager<EventBus>();

  const eventBusCreator = () => new EventBus();

  const { storeId } = usePdfWidgetStore();

  return manager.getOrCreate(
    storeId + "eventBusInstance",
    eventBusCreator,
  ) as EventBus;
};

export const getEventBus = (storeId: string) => {
  const manager = new InstanceManager<EventBus>();
  return manager.getInstance(storeId);
};

export default useEventBus;
