export interface Env {
  AUTOSCRIBE_WIDGET_HOST: string;
  EXTRACT_WIDGET_HOST: string;
  MED_WIDGET_HOST: string;
  DEMO_API: string;
  VERSION: string;
  FORMS_WIDGETS_HOST: string;
  FORMS_API: string;
  FORMS_API_KEY: string;
  OKTA_DISABLE: boolean;
  OKTA_ISSUER: string;
  OKTA_CLIENT_ID: string;
  OKTA_SCOPES: Array<string>;
}

type Patient = {
  id: string
  firstName: string
  lastName: string
  dob: string
  updatedAt: string
  tenantId: string
  appId: string
  // organizationId: string
  // createdAt: string
  // createdBy: string
  // updatedBy: string
}

export type { Patient }


// export class Env {
//   constructor(opts: Env) {
//     Object.assign(this, opts);
//   }
//   // constructor(readonly AUTOSCRIBE_WIDGET_HOST: string, readonly EXTRACT_WIDGET_HOST: string) {
//   // }
//   // AUTOSCRIBE_WIDGET_HOST: string;
//   // EXTRACT_WIDGET_HOST: string;
//   // VERSION: string;
//   // FORMS_WIDGETS_HOST: string;
//   // FORMS_API: string;
//   // FORMS_API_KEY: string;
//   // OKTA_DISABLE: boolean;
//   // OKTA_ISSUER: string;
//   // OKTA_CLIENT_ID: string;
//   // OKTA_SCOPES: Array<string>;
// }
