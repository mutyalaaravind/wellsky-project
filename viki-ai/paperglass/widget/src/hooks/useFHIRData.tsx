import { data } from "../utils/data";

// TODO: Add parameters
function useFHIRData() {
  const medicationData = data.entry.filter((entry: (typeof data.entry)[0]) => {
    return entry.resource.resourceType === "MedicationRequest";
  });

  const medicationSimpleData = medicationData.map(
    (medication: (typeof medicationData)[0]) => {
      const frequencyObject = (
        medication?.resource?.dosageInstruction?.[0] as any
      )?.timing?.repeat;

      const frequency = frequencyObject
        ? `${frequencyObject.frequency} times per ${frequencyObject.period}${frequencyObject.periodUnit}`
        : "N/A";

      return {
        id: medication?.resource?.id,
        medication: medication?.resource?.medicationCodeableConcept?.text,
        doseForm:
          (medication?.resource?.dosageInstruction?.[0] as any)
            ?.doseAndRate?.[0]?.doseAndRateQuantity?.code || "N/A",
        // strengthRatio: (medication?.resource?.dosageInstruction?.[0] as any)
        //   ?.doseAndRate?.[0]?.doseAndRateQuantity?.value,
        // strengthRatio:
        //   medication?.resource?.dosageInstruction?.[0]?.doseAndRate[0]
        //     ?.doseAndRateQuantity?.value,
        // description: (medication?.resource?.medicationCodeableConcept?.[0] as any)
        //   ?.text as string,
        frequency,
        requester: medication?.resource?.requester?.display,
        reason: medication?.resource?.reasonReference?.[0]?.display,
        status: medication?.resource?.status,
      };
    },
  );

  // const uniqueMedicationSimpleData: typeof medicationSimpleData = Array.from(
  //   new Set(medicationSimpleData.map((a: unknown) => JSON.stringify(a))),
  // ).map((a: unknown) => JSON.parse(a as string));

  return {
    // medication: uniqueMedicationSimpleData,
    medication: medicationSimpleData,
  };
}

export default useFHIRData;
