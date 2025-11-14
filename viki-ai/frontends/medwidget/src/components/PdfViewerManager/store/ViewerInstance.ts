import { Coordinate, EventBusEvents } from "types";
import { EventBus } from "utils/eventBus";
import { PdfStoreState } from "./storeTypes";

class ViewerInstance {
  protected eventBus: EventBus;
  protected store: PdfStoreState;

  constructor(eventBus: EventBus, store: PdfStoreState) {
    this.eventBus = eventBus;
    this.store = store;
  }

  public get totalPages(): number {
    return 0;
  }

  public get currentPage(): number {
    return 0;
  }

  public goToPage(page: number): void {
    return;
  }

  public get isLoading(): boolean {
    return false;
  }

  public hightlightAnnotation(
    documentId: string,
    pageNumber: number,
    coordinates: Coordinate[],
  ): void {
    if (this.store) {
      this.store.addAnnotation(documentId, pageNumber, coordinates);
    }
  }

  public removeAnnotations(documentId: string, pageNumber: number): void {
    if (this.store) {
      this.store.removeAnnotation(documentId, pageNumber, true);
    }
  }

  public addEventListener(
    event: EventBusEvents,
    callback: (data: any) => void,
  ): void {
    if (this.eventBus) {
      this.eventBus.on(event, callback);
    }
  }

  public removeEventListener(
    event: EventBusEvents,
    callback: (data: any) => void,
  ): void {
    if (this.eventBus) {
      this.eventBus.off(event, callback);
    }
  }

  public dispatchEvent(event: EventBusEvents, data: any): void {
    if (this.eventBus) {
      this.eventBus.dispatch(event, data);
    }
  }
}

export default ViewerInstance;
