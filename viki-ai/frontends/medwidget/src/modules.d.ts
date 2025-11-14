declare module "*.css" {
  function use(options?: { target: ShadowRoot }): void;
  function unuse(options?: { target: ShadowRoot }): void;
}
