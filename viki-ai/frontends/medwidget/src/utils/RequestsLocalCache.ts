class RequestsLocalCache {
  cache: Map<string, any>;
  cacheType: "inMemory" | "localStorage";
  protected isUsingApiCaching: boolean = false;
  protected cacheKeyPrefix: string;

  constructor(cacheType: "inMemory", prefix?: string | null, enabled?: boolean);
  constructor(cacheType: "localStorage", prefix: string, enabled?: boolean);
  constructor(
    cacheType: "inMemory" | "localStorage" = "inMemory",
    prefix: string,
    enabled = false,
  ) {
    this.cacheKeyPrefix = prefix;
    this.cacheType = cacheType;
    this.cache = new Map<string, any>();
    this.isUsingApiCaching = enabled;

    if (cacheType === "localStorage") {
      this.cache = new Map(
        JSON.parse(
          localStorage.getItem(this.cacheKeyPrefix + "-RequestsLocalCache") ||
            "[]",
        ),
      );
    }
  }

  enableApiCaching(enable: boolean) {
    this.isUsingApiCaching = enable;
  }

  has(key: string) {
    return this.isUsingApiCaching && this.cache.has(key);
  }

  set(key: string, value: any) {
    if (this.isUsingApiCaching) {
      this.cache.set(key, value);
      if (this.cacheType === "localStorage") {
        localStorage.setItem(
          this.cacheKeyPrefix + "-RequestsLocalCache",
          JSON.stringify(Array.from(this.cache)),
        );
      }
    }
  }

  get(key: string) {
    if (this.isUsingApiCaching) {
      return this.cache.get(key);
    }
    return null;
  }
}

export default RequestsLocalCache;
