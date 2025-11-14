```mermaid
flowchart TD
    subgraph DocumentCreatedEventHandler
        direction TB
        B{OrchestrateV3 FF enabled}
        B -->|yes| Orchestrate_v3
        B -->|No| D[run orchestrate_v2]
        Orchestrate_v3
        end
    subgraph Orchestrate_v3
        direction TB
        CreateDocumentOperationInstance["CreateDocumentOperationInstance/orchestration start - t1.orchestration.start"] --> DocumentProcessorAgent
        end
    subgraph DocumentProcessorAgent
        direction TB
        SplitPages["SplitPages (for each page, generate pageSplitCreatedEvent)"]
        end
    subgraph PageSplitCreatedEventHandlerA
        direction TB
        subgraph PageClassificationAgentA
            direction TB
            CreatePage_A --> PerformOCR_A --> ExtractText_A --> ClassifyPage_A --> CreatePageOperationA
            end
        end
    subgraph PageSplitCreatedEventHandlerB
        direction TB
        subgraph PageClassificationAgentB
            direction TB
            CreatePage_B --> PerformOCR_B --> ExtractText_B --> ClassifyPage_B --> CreatePageOperationB
            end
        end
    subgraph MedicationExtractionEventHandlerA
        direction TB
        subgraph MedicationExtractionAgentA
            direction TB
            MLA{Medication Label Exists}
            MLA --> |yes|ExtractMedication_A --> MedispanMatching_A --> NormalizeMedications_A --> CreateOrUpdateMedicatonProfile_A --> updatePageOperationObjectA
            MLA --> |No|updatePageOperationObjectA
            end
        end
    subgraph MedicationExtractionEventHandlerB
        direction TB
        subgraph MedicationExtractionAgentB
            direction TB
            MLB{Medication Label Exists}
            MLB --> |yes|ExtractMedication_B --> MedispanMatching_B --> NormalizeMedications_B --> CreateOrUpdateMedicatonProfile_B --> updatePageOperationObjectB
            MLB --> |No|updatePageOperationObjectB
            end
        end
    subgraph MedispanMatching_A
        direction TB
        SimilaritySearch_A["For Each medication, do similarity search and prompt to find right match"]
        end
    subgraph MedispanMatching_B
        direction TB
        SimilaritySearch_B["For Each medication, do similarity search and prompt to find right match"]
        end
    subgraph NormalizeMedications_A
        direction TB
        Normalize_A["For Each medication, normalize to update dosage and amount"]
        end
    subgraph NormalizeMedications_B
        direction TB
        Normalize_B["For Each medication, normalize to update dosage and amount"]
        end
    subgraph PageOperationUpdatedEventHandler
        direction TB
        ExtractionStatus{All Pages Operation Completed for Medication Extraction & Allergy Extraction?}
        ExtractionStatus --> |yes|UpdateDocumentOperation
        ExtractionStatus --> |No|Ignore
        end
    subgraph UpdateDocumentOperation
        direction TB
        updateDocOperation[update DocumentOperation With Active DocOperationInstanceId]
        updateDocOperation --> LogEnd["orchestration complete - t1.orchestration.end"] --> stop
        end
    A[Document Uploaded] -->|DocumentCreatedEvent| B{OrchestrateV3 FF enabled}
    SplitPages -->|PageSplitCreatedEventA|PageSplitCreatedEventHandlerA
    SplitPages -->|PageSplitCreatedEventB|PageSplitCreatedEventHandlerB
    ClassifyPage_A --> |PageClassifiedEvent|MLA
    ClassifyPage_B --> |PageClassifiedEvent|MLB
    updatePageOperationObjectA --> |PageOperationStatusUpdated|ExtractionStatus
    updatePageOperationObjectB --> |PageOperationStatusUpdated|ExtractionStatus
    
    


