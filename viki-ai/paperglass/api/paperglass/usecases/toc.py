from typing import List, Dict
import json

from paperglass.domain.model_toc import (
            PageTOC, 
            PageTOCContainer, 
            PageTOCMedication, 
            PageTOCProfile,
            DocumentTOC, 
            DocumentTOCEmbeddedDocument, 
            DocumentTOCSection, 
            DocumentTOCSectionMedication, 
            TOCPageRange,
            ProfileType,
            ProfileItem,
    )

from paperglass.domain.util_json import convertToJson

from paperglass.log import getLogger
LOGGER = getLogger(__name__)

async def assemble(app_id: str, tenant_id:str, patient_id:str, document_id: str, page_tocs: List[PageTOC]) -> DocumentTOC:
    
    LOGGER.info("Assembling TOC Number of pages: %d", len(page_tocs))

    toc: DocumentTOC = DocumentTOC(
        app_id=app_id,
        tenant_id=tenant_id,
        patient_id=patient_id,
        document_id = document_id,
        page_count = len(page_tocs),
        documents=[]
    )
    embeddedDoc: DocumentTOCEmbeddedDocument = None  

    last_page_last_section: DocumentTOCSection = None
    last_page_internal_page_number = None

    for page in page_tocs:
        LOGGER.info("Page %d", page.page_number)

        result = page.toc.prompt_output_data
        LOGGER.debug("TOC Extraction result: %s", result)

        if result is None:
            LOGGER.warn("No TOC data found on page %d", page.page_number)
            continue

        container = PageTOCContainer(**result)
        LOGGER.debug("Constructed PageTOCContainer")

        LOGGER.info("Page: %s", json.dumps(container.dict(), indent=4))

        if embeddedDoc is None or not isContinuedDocument(container, embeddedDoc, last_page_internal_page_number):
            LOGGER.debug("Creating new embedded document: %s of type %s", container.doc.name, container.doc.documentType)
            embeddedDoc = DocumentTOCEmbeddedDocument(
                name = container.doc.name,
                documentType = container.doc.documentType,
                pageRange = TOCPageRange(start=page.page_number, end=page.page_number),
                sections = []
            )
            toc.documents.append(embeddedDoc)
            last_page_last_section = None
        else:
            # Detected that this page is a continuation of the last embedded document
            LOGGER.debug("Continuing embedded document: %s of type %s", container.doc.name, container.doc.documentType)
            embeddedDoc.pageRange.end = page.page_number


        # Process Sections -----------------------------------------------------------------------------------------
        sections: List[DocumentTOCSection] = []        
        for index, section  in enumerate(container.doc.sections):
            LOGGER.debug("Processing section %s in absolute page number %s", section.name, page.page_number)

            this_meds = convertToDocumentSectionMedications(page.page_number, section.meds)
            
            this_section = DocumentTOCSection(
                name = section.name,
                meds = this_meds,
                pageRange = TOCPageRange(start=page.page_number, end=page.page_number)
            )

            
            if index==0 and isSectionContinuedFromLastPage(embeddedDoc, this_section):
                # Section is continued from the last page
                last_page_last_section.pageRange.end = page.page_number
                last_page_last_section.meds.extend(this_section.meds)

            else:
                embeddedDoc.sections.append(this_section)            

            last_page_last_section = this_section

        last_page_internal_page_number = container.doc.internalPageNumber

    LOGGER.debug("TOC Assembled")

    return toc

async def indexPageProfiles(toc:DocumentTOC):
    # Map of page number to List of PageTOCProfile
    pageProfiles: Dict[str, List[PageTOCProfile]] = {}

    LOGGER.debug("Seeding page profiles...")
    for i in range(1, toc.page_count + 1):
        key = str(i)
        pageProfiles[key] = [PageTOCProfile(type=ProfileType.MEDICATION, 
                            hasItems=False,
                            numberOfItems=0,
                            items=[])]
    LOGGER.debug("Seed complete: %s", pageProfiles)

    LOGGER.debug("Indexing page profiles...")
    for doc in toc.documents:        
        LOGGER.debug("Indexing document %s", doc.name)
        for section in doc.sections:
            LOGGER.debug("\tIndexing section %s", section.name)
            for med in section.meds:
                LOGGER.debug("\t + Assessing medication: %s", med.name)
                if med.pageNumber not in pageProfiles:
                    LOGGER.debug("\t\tPage number %s not in profile.  Creating...", med.pageNumber)
                    pageProfiles[med.pageNumber] = [createFirstPageProfile(ProfileItem(name=med.name))]   # Belt and suspenders.  Expect all to be created in the seeding step earlier                                                               
                else:
                    # Getting the medication profile for this page
                    LOGGER.debug("\t\tFiltering for medication profile for page %s ...", med.pageNumber)                    
                    pageProfile: PageTOCProfile = filterPageProfilesByType(pageProfiles[med.pageNumber], ProfileType.MEDICATION)
                    if pageProfile:
                        LOGGER.debug("\t\tPage profile found.  Updating...")
                        # Happy path, page profile already exists
                        pageProfile.hasItems = True
                        pageProfile.numberOfItems += 1
                        pageProfile.items.append(ProfileItem(name=med.name))

                    else:
                        # Case where pageProfile exists for this page, but none are medication.  Should never happen in current iteration, but future usecases it may...
                        LOGGER.debug("\t\tPage profiles exist for page, but no medication profile not found.  Creating...")
                        pageProfile = createFirstPageProfile(ProfileItem(name=med.name))
                        pageProfiles[med.pageNumber].append(pageProfile)

    LOGGER.debug("PageProfiles: %s", pageProfiles)

    return pageProfiles


def createFirstPageProfile(item: ProfileItem) -> PageTOCProfile:
    LOGGER.debug("Creating first page profile for medication %s", item.name)

    profileItem = ProfileItem(name=item.name)
    
    LOGGER.debug("Creating PageTOCProfile")
    ret = PageTOCProfile(type=ProfileType.MEDICATION, 
                          hasItems=True,
                          numberOfItems=1,
                          items=[profileItem]
                            )

    return ret


def filterPageProfilesByType(pageProfiles:List[PageTOCProfile], profileType:ProfileType) -> PageTOCProfile:    
    LOGGER.debug("Filtering page profiles by type %s: %s", profileType, pageProfiles)
    if pageProfiles is None or len(pageProfiles)==0:
        LOGGER.debug("No medication profiles found in page profiles.  Returning null")
        return None
    
    for pageProfile in pageProfiles:
        LOGGER.debug("Checking if pageProfile is medication %s", pageProfile)
        if pageProfile.type == profileType:
            LOGGER.debug("Found medication PageProfile %s", pageProfile)   
            return pageProfile
    

def isContinuedDocument(current_page:PageTOCContainer, current_document:DocumentTOCEmbeddedDocument, last_page_internal_page_number:str=None):    
    
    LOGGER.debug("Checking if document %s of type %s is continued", current_page.doc.name, current_page.doc.documentType)
    
    page_docname = ""
    if current_page.doc.name is not None:
        docname = current_page.doc.name.lower()

    doc_docname = ""
    if current_document.name is not None:
        doc_docname = current_document.name.lower()


    if page_docname == doc_docname and current_page.doc.documentType.lower() == current_document.documentType.lower():
        LOGGER.debug("Document %s of type %s is continued due to name and documentType", current_page.doc.name, current_page.doc.documentType)
        return True
    
    if current_page.doc.internalPageNumber == "1":
        # Reset to a new embedded document if we are able to determine that the internal page number is 1
        LOGGER.debug("Document %s of type %s is not continued due to reset of internal page number", current_page.doc.name, current_page.doc.documentType)
        return False
    
    if current_page.doc.internalPageCount is not None and current_page.doc.internalPageNumber != last_page_internal_page_number:
        # Definitely part of a sequential set of pages (probably, could be a case that documents were jumbled or missing pages in between)
        LOGGER.debug("Document %s of type %s is continued due to page count evaluation: %s != %s", current_page.doc.name, current_page.doc.documentType, current_page.doc.internalPageNumber, last_page_internal_page_number)
        return True
    
    # If the last section of the prior page has the same section as the first in this page, then it is likely a continuation
    # TODO This logic is not perfect.  It is possible that the last section of the prior page is not the same as the first section of this page
    if current_document.sections and current_page.doc.sections and len(current_page.doc.sections) > 0 and len(current_document.sections) > 0:
        last_section = current_document.sections[-1]
        if last_section.name.lower() == current_page.doc.sections[0].name.lower():
            LOGGER.debug("Document %s of type %s is continued due to section continuation", current_page.doc.name, current_page.doc.documentType)
            return True

    return False
    
def isSectionContinuedFromLastPage(current_document:DocumentTOCEmbeddedDocument, current_section:DocumentTOCSection):
    if current_document and current_document.sections:
        last_section = current_document.sections[-1]
        if last_section.name.lower() == current_section.name.lower():
            return True
    return False

def convertToDocumentSectionMedications(pageNumber:int, meds: List[PageTOCMedication]) -> List[DocumentTOCSectionMedication]:
    this_meds: List[DocumentTOCSectionMedication] = []
    for med in meds:
        LOGGER.debug("Processing medication %s", med.name)
        this_meds.append(DocumentTOCSectionMedication(
            name = med.name,
            dosage = med.dosage,
            route = med.route,
            form = med.form,
            pageNumber = pageNumber
        ))
    return this_meds
