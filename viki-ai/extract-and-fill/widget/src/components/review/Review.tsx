import FormRenderer from "./FormRenderer";
import {ReviewProps} from "../../types"

// component to do review
export const Review: React.FC<ReviewProps> = ({
  transcriptId,
    transcriptText,
    extractedText,
    template,
    setApprovedFormFieldValues,
    onApprovedFormFieldValues,
    mount,
    onEvidenceReceived
  }: ReviewProps) => {
    // const [extractedTextState, setExtractedTextState] = React.useState<null | string>("");
  
    // useEffect(() => {
    //   console.log(text);
    //   setExtractedText(text);
    // }, [text]);
    console.log("transcriptText in Review", transcriptText);
  
    return (
      <>
        {/* <Input.TextArea rows={10} value={extractedText || ""}></Input.TextArea> */}
        <FormRenderer
          mount={mount}
          template={template}
          transcriptText={transcriptText}
          transcriptId={transcriptId}
          extractedText={extractedText}
          setApprovedFormFieldValues={setApprovedFormFieldValues}
          onApprovedFormFieldValues={onApprovedFormFieldValues}
          onEvidenceReceived={onEvidenceReceived}
        />
      </>
    );
  };