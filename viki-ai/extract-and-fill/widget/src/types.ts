export interface Env {
  API_URL: string
  VERSION: string
  NLPARSE_WIDGET_HOST: string
  AUTOSCRIBE_WIDGET_HOST: string
  FORMS_WIDGETS_HOST: string
}

export type ReviewProps = {
  transcriptId: string;
    transcriptText?: null | string;
    extractedText?: null | string;
    json_template?: string;
    extractFields?: Array<any>;
    model?: string;
    template?: any;
    onExtractionCompleted?: (extractedText: string | null) => void;
    setApprovedFormFieldValues?: (approvedFields: any) => {};
    onApprovedFormFieldValues?: (approvedFields: any) => void;
    mount?: string;
    onEvidenceReceived: (evidence: any) => void;
    onFormSaveEvent?: (evidence: any) => void;
    onEvidenceRequestedEvent?: (item: any) => void;
    sectionId?: string;
  };

export type Evidence = {
    distance: number;
    sentence: {sentence: string, sentence_group_id: string,sentence_id: string, updatedAt: string, created_at: string, id: string};
}
