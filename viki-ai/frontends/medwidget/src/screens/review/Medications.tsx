import { useCallback, useRef, useState } from "react";

import {
  Alert,
  AlertDescription,
  AlertTitle,
  Box,
  Heading,
  IconButton,
  Tooltip,
  useToken,
} from "@chakra-ui/react";
import { DeleteIcon, EditIcon, RepeatIcon } from "@chakra-ui/icons";
import {
  DynamicTableContainer,
  LinkButton,
  Spinner,
} from "@mediwareinc/wellsky-dls-react";
import { AlertCircle, History } from "@mediwareinc/wellsky-dls-react-icons";

import { Block } from "components/Block";
import { capitalizeWords } from "utils/i18n";
import { Env, Medication } from "types";

import { useMedicationsApi } from "hooks/useMedicationsApi";

import { AddMedication, DeleteMedication, EditMedication } from "./Dialogs";
import { MagicSparkle } from "icons/MagicSparkle";
import { useAuth } from "hooks/useAuth";
import { EvidenceInfo, DocumentFile } from "types";
import { useExpandableContext } from "context/ExpandableContext";

type MedicationWithIndex = Medication & {
  [key: string]: any;
};
type KeyValue = {
  [key: string]: any;
};

export const Medications = ({
  env,
  onSubmit,
  documentsInReview,
  currentDocument,
  onEvidenceRequested,
}: {
  env: Env;
  onSubmit: () => void;
  documentsInReview: DocumentFile[];
  currentDocument: DocumentFile | null;
  onEvidenceRequested: (evidenceInfo: EvidenceInfo) => void;
}) => {
  const [tableHeaderColor, deletedColor] = useToken(
    // the key within the theme, in this case `theme.colors`
    "colors",
    // the subkey(s), resolving to `theme.colors.red.100`
    ["neutral.100", "elm.500"],
    // a single fallback or fallback array matching the length of the previous arg
  );

  const { patientId } = useAuth();
  const {
    medications,
    busy,
    error,
    refreshMedications,
    createMedication,
    updateMedication,
    deleteMedication,
    undeleteMedication,
    getEvidence,
  } = useMedicationsApi({
    apiRoot: env?.API_URL,
    patientId,
    documentsInReview,
  });

  const [busyMedicationIds, setBusyMedicationIds] = useState<any[]>([]);
  const cachedEvidences = useRef<KeyValue>({});

  const { resetCollapsedBoxes } = useExpandableContext();

  // const [medications, setMedications] = useState<any[]>([]);
  const excludeColumns = [
    "id",
    "reference",
    "evidence",
    "app_id",
    "document_reference",
    "document_id",
    "tenant_id",
  ];
  // const mergeColumns = [{date_range: ['start_date', 'end_date'], name_dose_route: ['dosage', 'frequency', 'route']}];
  let columns = (medications.length ? Object.keys(medications[0]) : []).filter(
    (column) => !excludeColumns.includes(column),
  );
  columns = ["page_number", "name", "dosage", "frequency", "end_date"];
  const emptyColumns = columns.filter((column) =>
    medications.every(
      (medication: MedicationWithIndex) => medication[column] === null,
    ),
  );
  columns = columns.filter((column) => !emptyColumns.includes(column));

  const [addingMedication, setAddingMedication] = useState(false);
  const [editingMedication, setEditingMedication] = useState<any | null>(null);
  const [deletingMedication, setDeletingMedication] = useState<any | null>(
    null,
  );

  const loadEvidence = useCallback(
    (id: string) => {
      setBusyMedicationIds((prev) => [...prev, id]);
      let promise;
      if (cachedEvidences.current[id]) {
        promise = Promise.resolve(cachedEvidences.current[id]);
      } else {
        promise = getEvidence(id);
      }

      promise
        .then((evidenceInfo: EvidenceInfo) => {
          onEvidenceRequested(evidenceInfo);
          cachedEvidences.current[id] = evidenceInfo;
        })
        .finally(() => {
          setBusyMedicationIds((prev) =>
            prev.filter((busyId) => busyId !== id),
          );
          resetCollapsedBoxes();
        });
    },
    [getEvidence, onEvidenceRequested, resetCollapsedBoxes],
  );

  // const loadEvidenceFromGroupedMedications = useCallback((medication: any) => {
  //   return () => {
  //     getEvidenceForGroupedMedications(medication).then((evidenceInfo: EvidenceInfo) => onEvidenceRequested(evidenceInfo));
  //   };
  // }, [getEvidenceForGroupedMedications, onEvidenceRequested]);

  // Source
  // Name/Dose/Route
  // Start Date
  // End Date
  // Actions (Edit/Delete)

  const renderCell = (
    content: any,
    obj: any,
    useStrikeThrough: boolean = false,
  ) => {
    // DynamicTableContainer does not allow us to override the style of entire row, so we have to do this for each cell.
    // This function is called for each cell, so we can apply the style here.
    if (obj.deleted === true) {
      return (
        <span
          style={{
            color: deletedColor,
            opacity: 0.5,
            textDecoration: useStrikeThrough ? "line-through" : "none",
          }}
        >
          {content}
        </span>
      );
    }
    return content;
  };

  return (
    <Block style={{ position: "relative", gap: "1rem" }}>
      <AddMedication
        apiRoot={env.API_URL}
        isOpen={addingMedication}
        onSave={(medication) => {
          if (currentDocument === null) {
            console.error("No current document to add medication to");
          } else {
            createMedication(currentDocument.id, medication);
            refreshMedications();
          }
          setAddingMedication(false);
        }}
        onCancel={() => {
          setAddingMedication(false);
        }}
      />
      <EditMedication
        apiRoot={env.API_URL}
        isOpen={editingMedication !== null}
        medication={editingMedication}
        onSave={(newValues) => {
          const id = editingMedication.id;
          setEditingMedication(null);
          updateMedication(id, newValues);
          refreshMedications();
          // updateMedication(editingMedication?.id || '', editingMedication || {}).then(() => {
          //   setEditingMedication(null);
          //   getMedications();
          // }
        }}
        onCancel={() => setEditingMedication(null)}
      />
      <DeleteMedication
        medication={deletingMedication}
        onDelete={(medication) => {
          setDeletingMedication(null);
          deleteMedication(medication.id);
          refreshMedications();
        }}
        onCancel={() => setDeletingMedication(null)}
      />
      <Heading
        size="sm"
        style={{ margin: "2rem", display: "flex", flexDirection: "row" }}
      >
        Medications
        <IconButton
          variant="link"
          style={{ marginLeft: "1rem" }}
          size="lg"
          onClick={refreshMedications}
          aria-label="Refresh"
          icon={<RepeatIcon />}
        />
        <div style={{ flex: "1 1 0" }}></div>
        <LinkButton onClick={() => setAddingMedication(true)}>
          Add Medication
        </LinkButton>
      </Heading>
      {busy && (
        <div
          style={{
            position: "absolute",
            inset: "0",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            height: "100%",
            flexDirection: "column",
            gap: "1rem",
            padding: "2rem",
            backgroundColor: "rgba(255, 255, 255, 0.8)",
            zIndex: "2",
          }}
        >
          <Spinner />
          Loading medications...
        </div>
      )}

      <div
        style={{
          display: "flex",
          flex: "1 1 0",
          flexDirection: "column",
          gap: "1rem",
          overflowY: "auto",
        }}
      >
        {error !== null ? (
          <Alert status="error">
            <AlertCircle />
            <Box>
              <AlertTitle>An error occured</AlertTitle>
              <AlertDescription>
                Failed to fetch medications: {error.toString()}
              </AlertDescription>
            </Box>
          </Alert>
        ) : medications.length === 0 ? (
          <Alert>
            <AlertCircle />
            <Box>
              <AlertTitle>No medications to display</AlertTitle>
            </Box>
          </Alert>
        ) : (
          <DynamicTableContainer
            pagination={{
              // Round medications.length up to the nearest power of 10
              defaultPageSize: Math.pow(
                10,
                Math.ceil(Math.log10(medications.length)),
              ),
              totalPages: 1,
              currentPage: 1,
            }}
            tableProps={{ size: "sm" }}
            headerColor={tableHeaderColor}
            columns={[
              {
                dataIndex: "id",
                id: "evidence-button",
                sortable: false,
                render: (id: any) =>
                  busyMedicationIds.includes(id) ? (
                    <div
                      style={{
                        width: "24px",
                        height: "24px",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                      }}
                    >
                      <Spinner size="sm" />
                    </div>
                  ) : (
                    <div style={{ display: "flex", justifyContent: "center" }}>
                      <MagicSparkle
                        fontSize={32}
                        animated={false}
                        onClick={() => {
                          loadEvidence(id);
                        }}
                      />
                    </div>
                  ),
                title: "",
                width: "40px",
              },
              {
                dataIndex: "id",
                id: "profile",
                sortable: false,
                render: (id: any, obj: any) => {
                  const currentMed = medications.find(
                    (medication) => medication.id === id,
                  ) as MedicationWithIndex;
                  return renderCell(
                    <div style={{ display: "flex", justifyContent: "center" }}>
                      <Tooltip label={currentMed?.medication_status}>
                        <div>
                          {currentMed?.medication_status?.[0]?.toUpperCase()}
                        </div>
                      </Tooltip>
                    </div>,
                    obj,
                  );
                },
                title: "",
                width: "40px",
              },
              ...columns.map((column) => ({
                dataIndex: column,
                id: column,
                sortable: true,
                title: capitalizeWords(column),
                render: (value: any, obj: any) =>
                  renderCell(
                    <span
                      style={{
                        fontWeight:
                          !obj.deleted && column === "name" ? "bold" : "normal",
                      }}
                    >
                      {value}
                    </span>,
                    obj,
                    column === "name",
                  ),
                // render: (value: any) => {
                //   return (column !== "records" ? <>{value}</> : <div style={{ display: 'flex', gap: '0.5rem', flexDirection: 'column' }}>
                //     <div>{value?.[0].name}</div>
                //     {/* make sure manually created record since wont have evidences, we dont show links for the same */}
                //     <div style={{ display: 'flex', gap: '0.5rem', flexDirection: 'row' }}>{value?.map((e: any, index: number) => { return e.created_by && e.evidences.length === 0 ? <div></div> : <div>[<Link onClick={loadEvidenceFromGroupedMedications(e)}>{index + 1}</Link>]</div> })}</div>
                //   </div>);
                // },
              })),
              {
                dataIndex: "id",
                id: "actions",
                sortable: false,
                render: (id: any, obj: any) => {
                  const currentMed = medications.find(
                    (medication) => medication.id === id,
                  );
                  const isDeleted = currentMed !== null && currentMed?.deleted;
                  return (
                    <div
                      style={{
                        display: "flex",
                        gap: "0.5rem",
                        flexDirection: "row",
                      }}
                    >
                      <IconButton
                        variant="link"
                        aria-label="Edit"
                        icon={<EditIcon />}
                        onClick={() => {
                          setEditingMedication(currentMed || null);
                        }}
                        style={{
                          opacity: isDeleted ? 0 : 1,
                          pointerEvents: isDeleted ? "none" : "auto",
                        }}
                      />
                      {isDeleted ? (
                        <IconButton
                          variant="link"
                          aria-label="Undelete"
                          icon={<History fontSize="24" />}
                          onClick={() => {
                            undeleteMedication(id);
                          }}
                        />
                      ) : (
                        <IconButton
                          variant="link"
                          aria-label="Delete"
                          icon={<DeleteIcon />}
                          onClick={() => {
                            setDeletingMedication(currentMed);
                          }}
                        />
                      )}
                    </div>
                  );
                },
                title: "Actions",
              },
            ]}
            dataSource={medications.sort((m1: any, m2: any) => {
              return m1.page_number > m2.page_number ? 1 : -1;
            })}
            onRowClick={(column) => {}}
          />
        )}
      </div>

      {/*
      <div style={{ display: 'flex', gap: '1rem', padding: '0 1rem 1rem', justifyContent: 'flex-end' }}>
        <PrimaryButton onClick={onSubmit}>Update Medication Profile</PrimaryButton>
      </div>
      */}
    </Block>
  );
};
