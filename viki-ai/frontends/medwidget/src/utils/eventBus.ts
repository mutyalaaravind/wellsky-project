import { EventBusEvents } from "types";

export class EventBus {
  protected watchers: Function[] = [];
  protected listeners: Record<EventBusEvents, Function[]> = {} as Record<
    EventBusEvents,
    Function[]
  >;

  protected watch(callBack: (event: EventBusEvents, ...args: any[]) => void) {
    this.watchers.push(callBack);

    return this.unwatch.bind(this, callBack);
  }

  protected unwatch(callBack: (event: EventBusEvents, ...args: any[]) => void) {
    this.watchers = this.watchers.filter((watcher) => watcher !== callBack);
  }

  on(event: EventBusEvents, callback: Function) {
    if (!this.listeners[event]) {
      this.listeners[event] = [];
    }
    this.listeners[event].push(callback);
  }

  off(event: EventBusEvents, callback: Function) {
    if (!this.listeners[event]) {
      return;
    }
    this.listeners[event] = this.listeners[event].filter(
      (listener) => listener !== callback,
    );
  }

  dispatch(event: EventBusEvents, ...args: any[]) {
    if (!this.listeners[event]) {
      return;
    }
    this.listeners[event].forEach((listener) => listener(...args));

    if (this.watchers.length) {
      this.watchers.forEach((watcher) => watcher(event, ...args));
    }
  }
}

const eventBusInstance = new EventBus();

export default eventBusInstance;
