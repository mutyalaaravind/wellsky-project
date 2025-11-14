import { AuthContext } from "context/AuthContext";
import { useCallback, useContext } from "react";
import { PageProfile } from "store/storeTypes";
import { Env } from "types";
import { isUsingApiCaching } from "utils/constants";
import RequestsLocalCache from "utils/RequestsLocalCache";

type TableOfContentsApiHookParams = {
  env: Env | null;
};

type TableOfContentsApiHook = {
  getTOC: (documentId: string) => Promise<TableOfContents[]>;
  getPageProfiles: (
    documentId: string,
    profile_type: string,
  ) => Promise<Record<number, PageProfile>>;
  getPageProfilesV4: (
    documentId: string,
    profile_type: string,
  ) => Promise<Record<number, PageProfile>>;
  getEntityTOC: (documentId: string) => Promise<EntityTOCSummary>;
};

export type TableOfContents = {
  id: string;
  document_id: string;
  pageProfiles: PageProfile[];
};

export type DocumentToc = {
  app_id: string;
  tenant_id: string;
  patient_id: string;
  document_id: string;
  page_count: number;
  pageProfiles: Map<number, PageProfile>;
};

export type EntityCategory = {
  category: string;
  label: string;
  count: number;
};

export type EntityTOCSummary = {
  document_id: string;
  total_entities: number;
  categories: EntityCategory[];
  runs: Array<{
    run_id: string;
    total_entities: number;
    categories: EntityCategory[];
    created_at?: string;
    updated_at?: string;
  }>;
};

const localCache = new Map<string, any>();

const requestsLocalCache = new RequestsLocalCache(
  "localStorage",
  "medications",
  isUsingApiCaching,
);

export const useTableOfContentsApi = ({
  env,
}: TableOfContentsApiHookParams): TableOfContentsApiHook => {
  const token = useContext(AuthContext).token;
  const apiRoot = env?.API_URL;

  const getTOC = useCallback(
    (documentId: string) => {
      return fetch(`${apiRoot}/api/documents/${documentId}/toc`, {
        headers: { Authorization: `Bearer ${token}` },
      })
        .then((response) => response.json())
        .catch((error) => {
          console.error("Failed to fetch document PDF URL:", error);
          throw error;
        });
    },
    [apiRoot, token],
  );

  const getPageProfiles = useCallback(
    (documentId: string, profile_type: string) => {
      if (localCache.has(`page-profiles-${documentId}-${profile_type}`)) {
        return Promise.resolve(
          localCache.get(`page-profiles-${documentId}-${profile_type}`),
        );
      }
      if (
        requestsLocalCache.has(`page-profiles-${documentId}-${profile_type}`)
      ) {
        return Promise.resolve(
          requestsLocalCache.get(`page-profiles-${documentId}-${profile_type}`),
        );
      }
      return fetch(
        `${apiRoot}/api/documents/${documentId}/toc/pageprofiles/${profile_type}`,
        { headers: { Authorization: `Bearer ${token}` } },
      )
        .then((response) => {
          const data = response.json();
          localCache.set(`page-profiles-${documentId}-${profile_type}`, data);

          return data;
        })
        .then((data) => {
          requestsLocalCache.set(
            `page-profiles-${documentId}-${profile_type}`,
            data,
          );
          return data;
        })
        .catch((error) => {
          console.error("Failed to fetch document page profiles:", error);
          throw error;
        });
    },
    [apiRoot, token],
  );

  const getPageProfilesV4 = useCallback(
    (documentId: string, profile_type: string) => {
      if (localCache.has(`page-profiles-${documentId}-${profile_type}`)) {
        return Promise.resolve(
          localCache.get(`page-profiles-${documentId}-${profile_type}`),
        );
      }
      if (
        requestsLocalCache.has(`page-profiles-${documentId}-${profile_type}`)
      ) {
        return Promise.resolve(
          requestsLocalCache.get(`page-profiles-${documentId}-${profile_type}`),
        );
      }
      return fetch(
        `${apiRoot}/api/v4/documents/${documentId}/toc/pageprofiles/${profile_type}`,
        { headers: { Authorization: `Bearer ${token}` } },
      )
        .then((response) => {
          const data = response.json();
          localCache.set(`page-profiles-${documentId}-${profile_type}`, data);

          return data;
        })
        .then((data) => {
          requestsLocalCache.set(
            `page-profiles-${documentId}-${profile_type}`,
            data,
          );
          return data;
        })
        .catch((error) => {
          console.error("Failed to fetch document page profiles:", error);
          throw error;
        });
    },
    [apiRoot, token],
  );

  const getEntityTOC = useCallback(
    (documentId: string) => {
      if (localCache.has(`entity-toc-${documentId}`)) {
        return Promise.resolve(localCache.get(`entity-toc-${documentId}`));
      }
      if (requestsLocalCache.has(`entity-toc-${documentId}`)) {
        return Promise.resolve(
          requestsLocalCache.get(`entity-toc-${documentId}`),
        );
      }
      return fetch(`${apiRoot}/api/v2/documents/${documentId}/toc`, {
        headers: { Authorization: `Bearer ${token}` },
      })
        .then((response) => {
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
          return response.json();
        })
        .then((data) => {
          localCache.set(`entity-toc-${documentId}`, data);
          requestsLocalCache.set(`entity-toc-${documentId}`, data);
          return data;
        })
        .catch((error) => {
          console.error("Failed to fetch entity TOC:", error);
          // Return empty structure on error to prevent UI crashes
          return {
            document_id: documentId,
            total_entities: 0,
            categories: [],
            runs: [],
          };
        });
    },
    [apiRoot, token],
  );

  return {
    getTOC,
    getPageProfiles,
    getPageProfilesV4,
    getEntityTOC,
  };
};
