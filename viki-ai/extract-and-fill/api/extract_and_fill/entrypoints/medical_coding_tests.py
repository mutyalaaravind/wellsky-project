# if you run into module not found error. In shell do following:
# export PYTHONPATH=$PYTHONPATH:yourprojectpath/eai-ai/extract-and-fill/api

import asyncio
import json
import os,sys
from typing import List
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from extract_and_fill.usecases.prompt_manager import PromptTemplateWithVerbatimSourceExtractionManager

def predict_with_grounding():
  import vertexai
  from vertexai.language_models import TextGenerationModel
  from vertexai.language_models import GroundingSource

  vertexai.init(project="viki-dev-app-wsky", location="us-central1")
  parameters = {
      "max_output_tokens": 1024,
      "temperature": 0.9,
      "top_p": 1
  }
  grounding_source = GroundingSource.VertexAISearch(data_store_id="oasis-redacted-samples_1707246676419", location="us", project="145042810266")
  model = TextGenerationModel.from_pretrained("text-bison-32k")
  response = model.predict(
      """please find relevant icd-10 codes""",
      **parameters,
      grounding_source=grounding_source
  )
  print(f"Response from Model: {response.text}")
  
def search_with_vertex_ai_search_and_conversation():
  from typing import List

  from google.api_core.client_options import ClientOptions
  from google.cloud import discoveryengine_v1 as discoveryengine

  def search_sample(
      project_id: str,
      location: str,
      data_store_id: str,
      search_query: str,
      serving_config = "default_config"
  ) -> List[discoveryengine.SearchResponse]:
      #  For more information, refer to:
      # https://cloud.google.com/generative-ai-app-builder/docs/locations#specify_a_multi-region_for_your_data_store
      client_options = (
          ClientOptions(api_endpoint=f"{location}-discoveryengine.googleapis.com")
          if location != "global"
          else None
      )

      # Create a client
      client = discoveryengine.SearchServiceClient(client_options=client_options)

      # The full resource name of the search engine serving config
      # e.g. projects/{project_id}/locations/{location}/dataStores/{data_store_id}/servingConfigs/{serving_config_id}
      serving_config = client.serving_config_path(
          project=project_id,
          location=location,
          data_store=data_store_id,
          serving_config=serving_config,
      )

      # Optional: Configuration options for search
      # Refer to the `ContentSearchSpec` reference for all supported fields:
      # https://cloud.google.com/python/docs/reference/discoveryengine/latest/google.cloud.discoveryengine_v1.types.SearchRequest.ContentSearchSpec
      content_search_spec = discoveryengine.SearchRequest.ContentSearchSpec(
          # For information about snippets, refer to:
          # https://cloud.google.com/generative-ai-app-builder/docs/snippets
          snippet_spec=discoveryengine.SearchRequest.ContentSearchSpec.SnippetSpec(
              return_snippet=True
          ),
          # For information about search summaries, refer to:
          # https://cloud.google.com/generative-ai-app-builder/docs/get-search-summaries
          summary_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec(
              summary_result_count=5,
              include_citations=True,
              ignore_adversarial_query=True,
              ignore_non_summary_seeking_query=True,
          ),
      )

      # Refer to the `SearchRequest` reference for all supported fields:
      # https://cloud.google.com/python/docs/reference/discoveryengine/latest/google.cloud.discoveryengine_v1.types.SearchRequest
      request = discoveryengine.SearchRequest(
          serving_config=serving_config,
          query=search_query,
          page_size=20,
          content_search_spec=content_search_spec,
          query_expansion_spec=discoveryengine.SearchRequest.QueryExpansionSpec(
              condition=discoveryengine.SearchRequest.QueryExpansionSpec.Condition.AUTO,
          ),
          spell_correction_spec=discoveryengine.SearchRequest.SpellCorrectionSpec(
              mode=discoveryengine.SearchRequest.SpellCorrectionSpec.Mode.AUTO
          ),
      )

      response = client.search(request)
      print(response)

      return response
  
  project_id = "viki-dev-app-wsky"
  location = "us"
  data_store_id = "oasis-redacted-samples_1707246676419"
  data_store_id = "fhir-store-search"
  search_query = "please share all patient data for patient with id: c70ee241-126a-719b-4b53-c48e5ae3714b"
  serving_config = f"projects/{project_id}/locations/us/collections/default_collection/dataStores/{data_store_id}/servingConfigs/default_search:search"
  
  result = search_sample(project_id, location, data_store_id, search_query, serving_config=serving_config)
  
def document_ai_tests():
  from typing import Optional, Sequence

  from google.api_core.client_options import ClientOptions
  from google.cloud import documentai

  # TODO(developer): Uncomment these variables before running the sample.
  # project_id = "YOUR_PROJECT_ID"
  # location = "YOUR_PROCESSOR_LOCATION" # Format is "us" or "eu"
  # processor_id = "YOUR_PROCESSOR_ID" # Create processor before running sample
  # processor_version = "rc" # Refer to https://cloud.google.com/document-ai/docs/manage-processor-versions for more information
  # file_path = "/path/to/local/pdf"
  # mime_type = "application/pdf" # Refer to https://cloud.google.com/document-ai/docs/file-types for supported file types


  def process_document_entity_extraction_sample(
      project_id: str,
      location: str,
      processor_id: str,
      processor_version: str,
      file_path: str,
      mime_type: str,
  ) -> None:
      # Online processing request to Document AI
      document = process_document(
          project_id, location, processor_id, processor_version, file_path, mime_type
      )

      # Print extracted entities from entity extraction processor output.
      # For a complete list of processors see:
      # https://cloud.google.com/document-ai/docs/processors-list
      #
      # OCR and other data is also present in the processor's response.
      # Refer to the OCR samples for how to parse other data in the response.

      print(f"Found {len(document.entities)} entities:")
      for entity in document.entities:
          print_entity(entity)
          # Print Nested Entities (if any)
          for prop in entity.properties:
              print_entity(prop)


  def print_entity(entity: documentai.Document.Entity) -> None:
      # Fields detected. For a full list of fields for each processor see
      # the processor documentation:
      # https://cloud.google.com/document-ai/docs/processors-list
      key = entity.type_

      # Some other value formats in addition to text are availible
      # e.g. dates: `entity.normalized_value.date_value.year`
      text_value = entity.text_anchor.content
      confidence = entity.confidence
      normalized_value = entity.normalized_value.text
      print(f"    * {repr(key)}: {repr(text_value)}({confidence:.1%} confident)")

      if normalized_value:
          print(f"    * Normalized Value: {repr(normalized_value)}")

  def list_processor_versions_sample(
    project_id: str, location: str, processor_id: str
  ) -> None:
      # You must set the `api_endpoint` if you use a location other than "us".
      opts = ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")

      client = documentai.DocumentProcessorServiceClient(client_options=opts)

      # The full resource name of the processor
      # e.g.: projects/project_id/locations/location/processors/processor_id
      parent = client.processor_path(project_id, location, processor_id)
      print(parent)
      # Make ListProcessorVersions request
      processor_versions = client.list_processor_versions(parent=parent)
      print(processor_versions)
      # Print the processor version information
      for processor_version in processor_versions:
          processor_version_id = client.parse_processor_version_path(
              processor_version.name
          )["processor_version"]

          print(f"Processor Version: {processor_version_id}")
          print(f"Display Name: {processor_version.display_name}")
          print(processor_version.state)
          print("")

  def process_document(
      project_id: str,
      location: str,
      processor_id: str,
      processor_version: str,
      file_path: str,
      mime_type: str,
      process_options: Optional[documentai.ProcessOptions] = None,
  ) -> documentai.Document:
      # You must set the `api_endpoint` if you use a location other than "us".
      client = documentai.DocumentProcessorServiceClient(
          client_options=ClientOptions(
              api_endpoint=f"{location}-documentai.googleapis.com"
          )
      )

      # The full resource name of the processor version, e.g.:
      # `projects/{project_id}/locations/{location}/processors/{processor_id}/processorVersions/{processor_version_id}`
      # You must create a processor before running this sample.
      name = client.processor_version_path(
          project_id, location, processor_id, processor_version
      )

      # Read the file into memory
      with open(file_path, "rb") as image:
          image_content = image.read()

      # Configure the process request
      request = documentai.ProcessRequest(
          name=name,
          raw_document=documentai.RawDocument(content=image_content, mime_type=mime_type),
          # Only supported for Document OCR processor
          process_options=process_options,
      )

      result = client.process_document(request=request)

      # For a full list of `Document` object attributes, reference this page:
      # https://cloud.google.com/document-ai/docs/reference/rest/v1/Document
      return result.document

  project_id="viki-dev-app-wsky"
  location="us"
  #processor_id="7359477870825dbb"
  processor_id="fcaac0296ec91273"
  #processor_version="pretrained"
  processor_version="pretrained-foundation-model-v1.0-2023-08-22"
  file_path="/Users/vkoova/Downloads/Sample Chart/Client Coordination Notes Report-redacted info.pdf"
  mime_type="application/pdf"
  process_options={}
    
  # list_processor_versions_sample(
  #   project_id,location,processor_id
  # )
  
  result = process_document(
    project_id,
    location,
    processor_id,
    processor_version,
    file_path,
    mime_type,
    process_options
  )
  
  print(result)
  
if __name__ == "__main__":
  #predict_with_grounding()
  search_with_vertex_ai_search_and_conversation()
  #document_ai_tests()
      
    
    