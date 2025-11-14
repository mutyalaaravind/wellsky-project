class InstanceManager<TInstance> {
  private static stores: Map<string, any>;

  constructor() {
    InstanceManager.stores =
      InstanceManager.stores || (new Map() as Map<string, TInstance>);
  }

  getOrCreate(storeId: string, createStore: () => TInstance): TInstance {
    if (!InstanceManager.stores.has(storeId)) {
      this.setInstance(storeId, createStore());
    }
    return this.getInstance(storeId);
  }

  getInstance(storeId: string): TInstance {
    return InstanceManager.stores.get(storeId);
  }

  setInstance(storeId: string, store: TInstance) {
    InstanceManager.stores.set(storeId, store);
  }

  removeInstance(storeId: string) {
    InstanceManager.stores.delete(storeId);
  }
}

export default InstanceManager;
