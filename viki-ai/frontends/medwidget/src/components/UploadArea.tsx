import { useCallback, useEffect, useRef, useState } from "react";

import { SecondaryButton, Spinner } from "@mediwareinc/wellsky-dls-react";
import { Upload } from "@mediwareinc/wellsky-dls-react-icons";
import { Heading, Link } from "@chakra-ui/react";

import { useDocumentsApi } from "hooks/useDocumentsApi";
import { Env } from "types";

type UploadAreaProps = {
  env: Env;
  patientId: string;
  onFileUploaded?: (file: File) => void;
  showAsButton?: boolean;
};

export const UploadArea = ({
  env,
  patientId,
  onFileUploaded,
  showAsButton,
}: UploadAreaProps) => {
  const [fileAreaEl, setFileAreaEl] = useState<HTMLDivElement | null>(null);
  const [fileInputEl, setFileInputEl] = useState<HTMLInputElement | null>(null);
  const [busy, setBusy] = useState(false);
  const currentFile = useRef<File | null>(null);

  const { uploadDocument } = useDocumentsApi({
    apiRoot: env?.API_URL,
    patientId,
  });

  const uploadFile = useCallback(
    (file: File) => {
      currentFile.current = file;
      setBusy(true);
      uploadDocument(file)
        .then(() => {
          onFileUploaded?.(file);
        })
        .catch(() => {})
        .finally(() => {
          currentFile.current = null;
          setBusy(false);
        });
    },
    [onFileUploaded, uploadDocument],
  );

  useEffect(() => {
    if (fileInputEl) {
      const onFileInputChange = (event: Event) => {
        const file = (event.target as HTMLInputElement).files?.[0];
        if (file) {
          uploadFile(file);
        } else {
          console.log("No file selected");
        }
      };
      fileInputEl.addEventListener("change", onFileInputChange);
      return () => {
        fileInputEl.removeEventListener("change", onFileInputChange);
      };
    }
  }, [fileInputEl, uploadFile]);

  const onFileAreaClick = useCallback(() => {
    if (fileInputEl) {
      fileInputEl.click();
    }
  }, [fileInputEl]);

  const onFileAreaDrop = useCallback(
    (event: React.DragEvent<HTMLDivElement>) => {
      event.preventDefault();
      if (fileAreaEl) {
        fileAreaEl.style.border = "2px dashed rgba(0, 0, 0, 0.5)";
      }
      const file = event.dataTransfer.files[0];
      if (file) {
        uploadFile(file);
      }
    },
    [fileAreaEl, uploadFile],
  );

  const onFileAreaDragOver = useCallback(
    (event: React.DragEvent<HTMLDivElement>) => {
      if (fileInputEl && fileAreaEl) {
        fileAreaEl.style.border = "2px solid rgba(0, 0, 0, 0.5)";
      }
      event.preventDefault();
    },
    [fileInputEl, fileAreaEl],
  );

  const onFileAreaDragLeave = useCallback(
    (event: React.DragEvent<HTMLDivElement>) => {
      if (fileInputEl && fileAreaEl) {
        fileAreaEl.style.border = "2px dashed rgba(0, 0, 0, 0.5)";
      }
      event.preventDefault();
    },
    [fileInputEl, fileAreaEl],
  );

  if (showAsButton) {
    return (
      <div
        onDrop={onFileAreaDrop}
        onDragOver={onFileAreaDragOver}
        onDragLeave={onFileAreaDragLeave}
        ref={setFileAreaEl}
        style={{
          width: "100%",
          display: "flex",
          justifyContent: "center",
          border: "none !important",
        }}
        data-pendoid="upload-area-button"
      >
        <SecondaryButton
          borderStyle={"dashed"}
          onClick={onFileAreaClick}
          w={"100%"}
        >
          <input type="file" style={{ display: "none" }} ref={setFileInputEl} />
          <Upload fontSize="1.5rem" />
          {busy ? (
            <div>
              Uploading{" "}
              <strong>
                {currentFile.current ? currentFile.current.name : "file"}
              </strong>{" "}
              ...
            </div>
          ) : (
            "Upload File"
          )}
        </SecondaryButton>
      </div>
    );
  }

  return (
    <div>
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: "0.5rem",
          minHeight: "200px",
          justifyContent: "center",
          alignItems: "center",
          cursor: "pointer",
          position: "relative",
          border: "2px dashed rgba(0, 0, 0, 0.5)",
          borderRadius: "4px",
          boxShadow: "none",
          pointerEvents: busy ? "none" : "auto",
        }}
        onClick={onFileAreaClick}
        onDrop={onFileAreaDrop}
        onDragOver={onFileAreaDragOver}
        onDragLeave={onFileAreaDragLeave}
        ref={setFileAreaEl}
        data-pendoid="upload-area-button"
      >
        <input type="file" style={{ display: "none" }} ref={setFileInputEl} />
        <Upload fontSize="3rem" />
        <div>
          Drag and drop or{" "}
          <Link color="blue.500" textDecoration="underline">
            browse files
          </Link>
        </div>
        <div>Max file size: 100MB</div>
        <div style={{ fontSize: "0.8rem" }}>Supported file types: PDF</div>
        {busy && (
          <div
            style={{
              position: "absolute",
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              backgroundColor: "rgba(255, 255, 255, 0.5)",
            }}
          >
            <Spinner />
          </div>
        )}
      </div>
      <Heading size="sm" style={{ margin: "1rem 0 0" }}>
        {busy ? (
          <div>
            Uploading{" "}
            <strong>
              {currentFile.current ? currentFile.current.name : "file"}
            </strong>{" "}
            ...
          </div>
        ) : (
          "There are currently no file uploads in progress"
        )}
      </Heading>
    </div>
  );
};
