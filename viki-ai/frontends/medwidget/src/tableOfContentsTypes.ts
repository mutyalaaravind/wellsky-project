export enum ProfileType {
  MEDICATION = "medication",
}

// For managing the state of the page profile selection ------------
export interface ContextPageProfileState {
  pageIndex: number;
  isSelected: boolean;
}

export interface ContextPageProfileStateMap {
  // Key is the page index
  [key: number]: ContextPageProfileState;
}

export interface ContextDocumentPageProfileFilter {
  // Key is the profile type (e.g. medication)
  [key: string | number]: ContextPageProfileStateMap;
}

export interface ContextDocumentItemFilter {
  profileFilter: ContextDocumentPageProfileFilter;
}

// For passing the page profile state more succinctly ------------

export interface DocumentItemFilter {
  profileFilter: DocumentPageProfileFilter;
}

export interface DocumentPageProfileFilter {
  [key: string]: PageProfileState;
}

export interface PageProfileState {
  pages: number[];
}
