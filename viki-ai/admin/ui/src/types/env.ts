export interface Env {
  ADMIN_API: string;
  VERSION: string;
  OKTA_DISABLE: boolean;
  OKTA_ISSUER: string;
  OKTA_CLIENT_ID: string;
  OKTA_SCOPES: Array<string>;
  OKTA_DISABLE_MOCK_USER?: string;
}