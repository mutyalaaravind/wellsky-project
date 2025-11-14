import { AuthContext } from "context/AuthContext";
import { useCallback, useContext } from "react";
import { usePatientProfileStore } from "store/patientProfileStore";
import { DocumentFileApiResponse, DocumentFile, pipelineStatus } from "types";
import { isUsingApiCaching } from "utils/constants";
import RequestsLocalCache from "utils/RequestsLocalCache";

type DocumentsApiHookParams = {
  apiRoot: string;
  patientId: string;
  env?: any;
};

type DocumentsApiHook = {
  documents: DocumentFile[];
  fetchDocuments: () => Promise<DocumentFile[]>;
  fetchDocumentsV2: (params: {
    startAt: string | null;
    endAt: string | null;
    limit: number;
    cb?: (result?: any, err?: any) => any;
    useAsyncDocumentStatus?: boolean;
    loadStatuses?: boolean;
  }) => Promise<DocumentFile[]>;
  uploadDocument: (file: File) => Promise<any>;
  getPdfUrl: (documentId: string) => Promise<string>;
  extract: (documentId: string) => Promise<any>;
  getPage: (documentId: string, pageNumber: number) => Promise<any>;
  getDocumentStatus: (documentId: string) => Promise<any>;
  moveToPriorityQueue: (documentId: string) => Promise<any>;
  upsertGoldenDatasetTestcase: (documentId: string) => Promise<any>;
};

const apiLocalCache = new Map<string, any>();

const requestsLocalCache = new RequestsLocalCache(
  "localStorage",
  "documents",
  isUsingApiCaching,
);

export const useDocumentsApi = ({
  apiRoot,
  patientId,
  env,
}: DocumentsApiHookParams): DocumentsApiHook => {
  const { token, oktaToken, ehrToken } = useContext(AuthContext);

  const { documents, setDocuments } = usePatientProfileStore();
  const { setDocumentStatuses } = usePatientProfileStore();

  const fetchDocuments = useCallback(
    async (cb?: (result?: any, err?: any) => any) => {
      let data: DocumentFile[] = [];
      const fetchCall = async () => {
        const res = await fetch(
          `${apiRoot}/api/documents?patientId=${patientId}`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
              "okta-Token": oktaToken,
              "ehr-token": ehrToken,
            },
          },
        );

        if (!res.ok) {
          cb?.(null, res);
          throw new Error(`Failed to fetch documents: ${res.statusText}`);
        }
        return res.json();
      };

      if (requestsLocalCache.has(patientId)) {
        data = requestsLocalCache.get(patientId) as DocumentFileApiResponse[];
      } else {
        data = (await fetchCall()) as DocumentFileApiResponse[];
        requestsLocalCache.set(patientId, data);
      }

      const documents = data.map((doc) => {
        const { id, created_at, file_name, page_count, status, total_records } =
          doc;
        return {
          id,
          created_at,
          file_name,
          page_count,
          status,
          total_records,
        } satisfies DocumentFile;
      });

      setDocuments((prev) => {
        if (documents?.length === 0) {
          return prev;
        }
        const prevStr = JSON.stringify(prev);
        const newStr = JSON.stringify(documents);
        if (prevStr !== newStr) {
          return documents;
        }
        return prev;
      });
      cb?.(data);
      return data;
    },
    [apiRoot, patientId, token, oktaToken, ehrToken, setDocuments],
  );

  const getDocumentStatus = useCallback(
    (documentId: string) => {
      return fetch(`${apiRoot}/api/documents/${documentId}/status`, {
        headers: { Authorization: `Bearer ${token}`, "okta-Token": oktaToken },
      })
        .then((response) => {
          response.json().then((data) => {
            setDocumentStatuses((prev) => {
              //console.log("data", documentId, data, prev);
              //prev[documentId] = data as pipelineStatus;
              const newPrev = { ...prev };
              newPrev[documentId] = data as pipelineStatus;
              return newPrev;
              // return prev;
            });
          });
        })
        .catch((error) => {
          console.error("Failed to fetch document status:", error);
          throw error;
        });
    },
    [apiRoot, token, oktaToken, setDocumentStatuses],
  );

  const fetchDocumentsV2 = useCallback(
    async ({
      startAt,
      endAt,
      limit,
      cb,
      useAsyncDocumentStatus = false,
      loadStatuses = false,
    }: Parameters<DocumentsApiHook["fetchDocumentsV2"]>[0]) => {
      let data: DocumentFile[] = [];
      const fetchCall = async () => {
        const res = await fetch(
          `${apiRoot}/api/documents_with_pagination?patientId=${patientId}&startAt=${startAt}&endAt=${endAt}&limit=${limit}`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
              "okta-Token": oktaToken,
              "ehr-token": ehrToken,
            },
          },
        );

        if (!res.ok) {
          cb?.(null, res);
          throw new Error(`Failed to fetch documents: ${res.statusText}`);
        }
        return res.json();
      };

      if (requestsLocalCache.has(patientId)) {
        data = requestsLocalCache.get(patientId) as DocumentFileApiResponse[];
      } else {
        data = (await fetchCall()) as DocumentFileApiResponse[];
        requestsLocalCache.set(patientId, data);
      }

      const documents = data.map((doc) => {
        const {
          id,
          created_at,
          file_name,
          page_count,
          status,
          total_records,
          operation_status,
          priority,
          metadata
        } = doc;
        return {
          id,
          created_at,
          file_name,
          page_count,
          status,
          total_records,
          operation_status,
          priority,
          metadata
        } satisfies DocumentFile;
      });

      setDocuments((prev) => {
        if (documents?.length === 0) {
          return prev;
        }
        const prevStr = JSON.stringify(prev);
        const newStr = JSON.stringify(documents);
        if (prevStr !== newStr) {
          return documents;
        }
        return prev;
      });

      if (useAsyncDocumentStatus && loadStatuses) {
        await Promise.allSettled(
          documents
            .filter((doc) => doc.status?.status === "UNKNOWN")
            .map((d) => getDocumentStatus(d.id)),
        );
      }

      cb?.(data);
      return data;
    },
    [
      patientId,
      setDocuments,
      apiRoot,
      token,
      oktaToken,
      ehrToken,
      getDocumentStatus,
    ],
  );

  const uploadDocument = useCallback(
    (file: File) => {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("patientId", patientId);
      return fetch(`${apiRoot}/api/documents`, {
        method: "POST",
        body: formData,
        headers: { Authorization: `Bearer ${token}` },
      })
        .then((response) => response.json())
        .then((data) => {})
        .catch((error) => {
          console.error("Failed to upload document:", error);
          throw error;
        });
    },
    [apiRoot, patientId, token],
  );

  const getPdfUrl = useCallback(
    (documentId: string) => {
      if (apiLocalCache.has(`pdf-url-${documentId}`)) {
        return Promise.resolve(apiLocalCache.get(`pdf-url-${documentId}`));
      }
      return fetch(`${apiRoot}/api/documents/${documentId}/pdf-url`, {
        headers: { Authorization: `Bearer ${token}` },
      })
        .then((response) => {
          const res = response.json();
          apiLocalCache.set(`pdf-url-${documentId}`, res);
          return res;
        })
        .catch((error) => {
          console.error("Failed to fetch document PDF URL:", error);
          throw error;
        });
    },
    [apiRoot, token],
  );

  const extract = useCallback(
    (documentId: string) => {
      return fetch(`${apiRoot}/api/documents/${documentId}/extract`, {
        headers: { Authorization: `Bearer ${token}` },
        method: "POST",
      })
        .then((response) => response.json())
        .catch((error) => {
          console.error("Failed to retrigger document:", error);
          throw error;
        });
    },
    [token, apiRoot],
  );

  const getPage = useCallback(
    (documentId: string, pageNumber: number) => {
      return fetch(
        `${apiRoot}/api/documents/${documentId}/pages/${pageNumber}`,
        { headers: { Authorization: `Bearer ${token}` } },
      )
        .then((response) => response.json())
        .catch((error) => {
          console.error("Failed to fetch document page:", error);
          throw error;
        });
    },
    [apiRoot, token],
  );

  const moveToPriorityQueue = useCallback(
    (documentId: string) => {
      return fetch(`${apiRoot}/api/orchestrate/medication_extraction`, {
        headers: { Authorization: `Bearer ${token}` },
        method: "POST",
        body: JSON.stringify({ document_id: documentId, priority: "high" }),
      })
        .then((response) => response.json())
        .catch((error) => {
          console.error("Failed to move document to priority queue:", error);
          throw error;
        });
    },
    [token, apiRoot],
  );

  const upsertGoldenDatasetTestcase = useCallback(
    (documentId: string) => {
      return fetch(`${apiRoot}/api/documents/${documentId}/create-testcase`, {
        headers: { Authorization: `Bearer ${token}` },
        method: "POST",
        body: JSON.stringify({}),
      })
        .then((response) => response.json())
        .catch((error) => {
          console.error("Failed to create or update test case for document:", error);
          throw error;
        });
    },
    [token, apiRoot],
  );


  return {
    documents,
    fetchDocuments,
    fetchDocumentsV2,
    uploadDocument,
    getPdfUrl,
    extract,
    getPage,
    getDocumentStatus,
    moveToPriorityQueue,
    upsertGoldenDatasetTestcase,
  };
};
