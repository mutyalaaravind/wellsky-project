import { EventBusEvents, MedWidgetInstanceConfig } from "types";
import { EventBus } from "./eventBus";

class MedWidgetInstance {
  protected eventBus: EventBus;
  protected onUnMountCallback?: () => void;
  protected onReadyCallback?: () => void;
  protected config: MedWidgetInstanceConfig;

  constructor(eventBus: EventBus) {
    this.eventBus = eventBus;
    this.config = {};
  }

  public onReady(callback: (...args: any[]) => void) {
    this.onReadyCallback = callback;
    this.eventBus.on("widgetReady", callback);
  }

  public on(event: EventBusEvents, callback: (data: any) => void) {
    this.eventBus.on(event, callback);
  }

  public off(event: EventBusEvents, callback: (data: any) => void) {
    this.eventBus.off(event, callback);
  }

  public dispatch(event: EventBusEvents, data?: any) {
    this.eventBus.dispatch(event, data);
  }

  public onUnMount(cb: () => void) {
    this.onUnMountCallback = cb;
  }

  public unmount() {
    this.onUnMountCallback?.();
  }

  public getConfig() {
    return this.config;
  }

  public setConfig(config: MedWidgetInstanceConfig) {
    this.config = {
      ...this.config,
      ...config,
    };
  }
}

export default MedWidgetInstance;
