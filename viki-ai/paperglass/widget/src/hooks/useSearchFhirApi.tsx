import React, { useEffect, useState } from "react";
import { useSearchContext } from "../context/SearchContext";
import { fetchSearchData } from "../utils/helpers";

function useSearchFhirApi(env: any) {
  const [loading, setLoading] = useState(false);
  const [resultData, setResultData] = useState<any>({} as any);
  const [summary, setSummary] = useState<any>(null);
  const [tags, setTags] = useState([]);
  const {
    state: { searchValue, identifier },
  } = useSearchContext();

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        setResultData({} as any);
        const resultWithSummary = await fetchSearchData(env, searchValue, identifier);
        const result = resultWithSummary.results;
        console.log("result", resultWithSummary);

        const tags = result.map((d: any) => d.type);

        const responseData: any = {};

        const summaryReferences = resultWithSummary.summaryWithMetadata;

        for (const d of result) {
          switch (d.type) {
            case "MedicationRequest":
              responseData.MedicationRequest = d.results?.map((r: any) => {
                return {
                  id: r.id,
                  date: r.resource?.[d.type].authoredOn,

                  medication:
                    r.resource?.[d.type]?.medicationCodeableConcept?.text,
                  doseForm:
                    r.resource?.[d.type]?.dosageInstruction?.[0]
                      ?.doseAndRate?.[0]?.doseAndRateQuantity?.code || "N/A",
                  frequency: r.resource?.[d.type]?.dosageInstruction?.[0]
                    ?.timing?.repeat
                    ? `${r.resource?.[d.type]?.dosageInstruction?.[0]?.timing?.repeat?.frequency} times per ${r.resource?.[d.type]?.dosageInstruction?.[0]?.timing?.repeat?.period}${r.resource?.[d.type]?.dosageInstruction?.[0]?.timing?.repeat?.periodUnit}`
                    : "N/A",
                  requester: r.resource?.[d.type]?.requester?.display,
                  reason: r.resource?.[d.type]?.reasonReference?.[0]?.display,
                  status: r.resource?.[d.type]?.status,
                  route:
                    r.resource?.[d.type]?.dosageInstruction?.[0]?.route?.text,
                  instruction:
                    r.resource?.[d.type]?.dispenseRequest?.[0]?.initialFill?.[0]
                      ?.quantity?.value,
                  resourceType: "MedicationRequest"
                };
              });
              break;
            case "DiagnosticReport":
              responseData.DiagnosticReport = d.results?.map((r: any) => {
                return {
                  id: r.id,
                  date: r.resource?.[d.type].effectiveDateTime,
                  status: r.resource?.[d.type].status,
                  type: r.resource?.[d.type]?.category?.[0]?.coding[0]?.display,
                  author: r.resource?.[d.type]?.performer?.[0]?.display,
                  snippet: r.snippets,
                  infoData: r.resource?.[d.type]?.presentedForm?.[0]?.data,
                  resourceType: "DiagnosticReport"
                };
              });
              break;
            case "AllergyIntolerance":
              responseData.AllergyIntolerance = d.results.map((r: any) => {
                return {
                  id: r.id,
                  reaction: r?.resource?.[d.type]?.reaction
                    .map((reaction: any) => {
                      return {
                        manifestation: reaction?.manifestation
                          ?.map((m: any) => m.text)
                          ?.join(", "),
                      };
                    })
                    .map((r: any) => r.manifestation)
                    .join(", "),
                  allergy: r.resource?.[d.type].code.text,
                  clinicalStatus:
                    r.resource?.[d.type]?.clinicalStatus?.coding?.[0]?.code,
                  verificationStatus:
                    r.resource?.[d.type]?.verificationStatus?.coding?.[0]?.code,
                  note: r.resource?.[d.type]?.note,
                  resourceType: "AllergyIntolerance"
                };
              });
              break;
            case "DocumentReference":
              responseData.DocumentReference = d.results.map((r: any) => {
                return {
                  id: r?.resource?.[d.type]?.identifier[0].value,
                  infoData: r?.resource?.[d.type]?.content[0]?.attachment.contentType === "application/pdf" ? r?.resource?.[d.type]?.content[0]?.attachment.url: r?.resource?.[d.type]?.content[0]?.attachment.data,
                  status: r.resource?.[d.type].status,
                  snippets: r.snippets,
                  resourceType: "DocumentReference"
                };
              });
              break;
          }
        }
        setResultData(responseData);
        setTags(tags);
        setLoading(false);
        setSummary(resultWithSummary.summary);
      } catch (error) {
        console.error(error);
      }
    }

    if (searchValue && identifier) {
      fetchData();
    }
  }, [env, identifier, searchValue]);

  return { loading, resultData, tags , summary };
}

export default useSearchFhirApi;
