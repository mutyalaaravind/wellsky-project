import { Accordion, AccordionButton, AccordionIcon, AccordionItem, AccordionPanel, Box, Heading, Spinner, Tab, TabList, TabPanel, TabPanels, Tabs, VStack } from "@chakra-ui/react";
import DataTable from "./components/DataTable";
import SearchBar from "./components/SearchBar";
import { useSearchContext } from "./context/SearchContext";
import useFHIRData from "./hooks/useFHIRData";
import useSearchFhirApi from "./hooks/useSearchFhirApi";
import { useEffect, useState } from "react";
import { getColumnLabel } from "./utils/helpers";
import DocsSearchContainer from "./DocsSearchContainer";
import { Tags } from "./components/Tags";

const getResource = (resourceId:string, results:any) => {
  const medicationResource = results.MedicationRequest?.find((result:any) => {
    if (resourceId.includes(result.id)) {
      return true;
    }
    return false;
  });

  const diagnosticReportResource = results.DiagnosticReport?.find((result:any) => {
    if (resourceId.includes(result.id)) {
      return true;
    }
    return false;
  });

  const AllergyIntolleranceResource = results.AllergyIntolerance?.find((result:any) => {
    if (resourceId.includes(result.id)) {
      return true;
    }
    return false;
  });
  //console.log(resourceId, medicationResource, diagnosticReportResource, AllergyIntolleranceResource);
  return medicationResource || diagnosticReportResource || AllergyIntolleranceResource;
}

const getSummaryResourcesGroupedByType = (summary:any, resultData:any) => {
  const summaryResources:any = {};
  summary.summaryWithMetadata && summary.summaryWithMetadata?.citationMetadata?.citations?.[0].sources.map((citation:any)=>{
    if(citation.referenceIndex){
      const resource = getResource(summary.summaryWithMetadata.references[citation.referenceIndex].document, resultData);
      if (resource) {
        if (!summaryResources[resource.resourceType]) {
          summaryResources[resource.resourceType] = [];
        }
        summaryResources[resource.resourceType].push(resource);
      }
    }
  })
  console.log("summaryResources",summaryResources);
  return summaryResources; 
}

function SearchContainer(props: any) {
  const { identifier } = props;

  const { medication } = useFHIRData();
  const { resultData, tags, loading, summary } = useSearchFhirApi(props.env); // Use the useSearchData hook (defined in the next step
  const [summaryResourcesByType,setSummaryResourcesByType] = useState<any>([]);
  const allTags = [...tags];
  const { state, dispatch } = useSearchContext();

  useEffect(() => {
    if (identifier) {
      dispatch?.({ type: "setIdentifier", payload: identifier });
    }
  }, [dispatch, identifier]);

  useEffect(() => {
    if(summary && resultData){
      const summaryResources = getSummaryResourcesGroupedByType(summary, resultData);
      console.log("summaryResources", summaryResources);
      setSummaryResourcesByType(summaryResources);
    }
  },[summary, resultData])

  return (
    <Box>
      <SearchBar tags={allTags} /> {/* Use the SearchBar component */}
      {loading ? (
        <VStack>
          <Spinner size="xl" />
        </VStack>
      ) : (
            <>
            {/* <Tabs defaultIndex={1} display="flex" flexDirection="column" flex="1 1 0" height="100vh" maxHeight="100vh" overflowY="auto">
              <TabList>
                <Tab>Source: Documents</Tab>
                <Tab>Source: Structured</Tab>
              </TabList>

              <TabPanels flex="1 1 0">
                <TabPanel>
                    <DocsSearchContainer
                      env={props.env}
                      identifier={identifier}
                      searchText={state.searchValue}
                      onSearchResults={(results: any, summary: any) => {
                        
                      }}
                      />
                </TabPanel>
                <TabPanel> */}
                {/* ToDo: below component to be moved to a FHIR search componnent similar to doc search container*/}
                {summary && 
                  <>
                  <Heading>Summary</Heading>
                  <Box>{summary.summaryWithMetadata ? summary.summaryWithMetadata.summary: summary.summaryText} </Box>
                  <Accordion allowToggle>
                    <AccordionItem>
                      <h2>
                        <AccordionButton>
                          <Box flex="1" textAlign="left">
                            References
                          </Box>
                          <AccordionIcon />
                        </AccordionButton>
                        <AccordionPanel pb={4}>
                        {summaryResourcesByType && <Box><DataTable
                          data={summaryResourcesByType.MedicationRequest}
                          heading={"MedicationRequest"}
                          search={state.searchValue}
                        /></Box>}
                        {summaryResourcesByType && <DataTable
                          data={summaryResourcesByType.DiagnosticReport}
                          heading={"DiagnosticReport"}
                          search={state.searchValue}
                        />}
                        {summaryResourcesByType && <DataTable
                          data={summaryResourcesByType.AllergyIntolerance}
                          heading={"AllergyIntolerance"}
                          search={state.searchValue}
                        />}
                        {summaryResourcesByType && <DataTable
                          data={summaryResourcesByType.DocumentReference}
                          heading={"DocumentReference"}
                          search={state.searchValue}
                        />}
                        </AccordionPanel>
                      </h2>
                    </AccordionItem>
                  </Accordion>
                  
                  </>
                }
                <>
                {summary && <Heading>Results</Heading>}
                <Tags tags={allTags} />
                {state.selectedTags.map((tag) => {
                  let tableData;
                  switch (tag) {
                    case "Inpatient Meds":
                      tableData = medication;
                      break;
                    case "MedicationRequest":
                      tableData = resultData.MedicationRequest;
                      break;
                    case "DiagnosticReport":
                      tableData = resultData.DiagnosticReport;
                      break;
                    case "AllergyIntolerance":
                      tableData = resultData.AllergyIntolerance;
                      break;
                      case "DocumentReference":
                        tableData = resultData.DocumentReference;
                        break;
                  }
                  return (
                    <DataTable
                      data={tableData}
                      heading={getColumnLabel(tag)}
                      search={state.searchValue}
                    />
                  );
                })}
                </>
                {/* </TabPanel>
              </TabPanels>
            </Tabs> */}
            </>
          )}
    </Box>
  );
}

export default SearchContainer;
