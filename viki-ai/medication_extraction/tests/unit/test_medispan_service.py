import pytest
from unittest.mock import MagicMock, Mock, patch, AsyncMock
from datetime import datetime
import json
import sys


from services.medispan_service import MedispanMatchService
from models import ExtractedMedication, MedicationValue, MedispanDrug, MedispanStatus, OperationMeta, MedispanMatchConfig

        
        
@pytest.fixture
def mock_dependencies():
    with patch('adapters.llm.genai') as mock_genai, \
         patch('adapters.llm.StorageAdapter') as mock_storage_adapter, \
         patch('adapters.llm.CloudTaskAdapter') as mock_cloud_task_adapter, \
         patch('adapters.llm.GooglePubSubAdapter') as mock_pubsub_adapter:
        
        # Setup storage mock
        mock_storage = MagicMock()
        mock_storage.get_base_path = AsyncMock()
        mock_storage.write_text = AsyncMock()
        mock_storage_adapter.return_value = mock_storage

        # Setup cloud task mock
        mock_cloud_task = MagicMock()
        mock_cloud_task.create_task = AsyncMock()
        mock_cloud_task_adapter.return_value = mock_cloud_task

        # Setup pubsub mock
        mock_pubsub = MagicMock()
        mock_pubsub.publish = AsyncMock()
        mock_pubsub_adapter.return_value = mock_pubsub

        yield {
            'genai': mock_genai,
            'storage': mock_storage,
            'cloud_task': mock_cloud_task,
            'pubsub': mock_pubsub
        }
        
@pytest.fixture
def service(mock_dependencies):
    return MedispanMatchService("test_tenant",None)

@pytest.fixture
def medispan_drug():
    return MedispanDrug(
        id="12345",
        GenericName="Test Generic",
        NameDescription="Test Med 10mg",
        Strength="10",
        StrengthUnitOfMeasure="mg",
        Dosage_Form="tablet",
        Route="oral"
    )

@pytest.fixture
def extracted_medication():
    med_value = MedicationValue(
        name="Test Med",
        strength="10mg",
        form="tablet",
        route="oral"
    )
    return ExtractedMedication(
        id="test_id_1",
        medication=med_value,
        app_id="test_app",
        tenant_id="test_tenant",
        patient_id="test_patient",
        document_id="test_doc",
        page_number=1,
        document_reference="test_ref",
        page_id="test_page",
        explaination="test explanation"
    )

@pytest.mark.asyncio
async def test_run_empty_medications(service):
    """Test run method with empty medications list"""
    medications, medispan_search_result = await service.run(
        app_id="test_app",
        tenant_id="test_tenant",
        patient_id="test_patient",
        document_id="test_doc",
        page_number=1,
        run_id="test_run",
        extracted_medications_raw=[]
    )
    assert medications == [],[]

# @pytest.mark.asyncio
# async def test_medispan_matching_batch_processing(service):
#     """Test batch processing in medispan matching"""
#     test_input = [
#         {"id": "1", "medication_name": "Med1", "index": 0, "medispan_options": []},
#         {"id": "2", "medication_name": "Med2", "index": 1, "medispan_options": []}
#     ]
    
#     with patch('adapters.llm.StandardPromptAdapter') as mock_llm:
#         llm_instance = AsyncMock()
#         llm_instance.multi_modal_predict_2.return_value = json.dumps([
#             {"1": "med1_id"},
#             {"2": "med2_id"}
#         ])
#         mock_llm.return_value = llm_instance

#         result, context = await service.medispanmatching_batch(
#             prompt_template="test {SEARCH_TERM} {DATA}",
#             model="test-model",
#             prompt_input=test_input
#         )

#         assert len(result) == 2
#         assert result[0]["id"] == "1"
#         assert result[1]["id"] == "2"

def test_chunk_array(service):
    """Test array chunking functionality"""
    test_array = [1, 2, 3, 4, 5]
    chunks = service.chunk_array(test_array, 2)
    assert chunks == [[1, 2], [3, 4], [5]]

def test_convert_to_json_wrapped(service):
    """Test JSON conversion with wrapped content"""
    test_input = '```json\n{"key": "value"}\n```'
    result = service.convertToJson(test_input)
    assert result == {"key": "value"}

def test_convert_to_json_unwrapped(service):
    """Test JSON conversion with unwrapped content"""
    test_input = '{"key": "value"}'
    result = service.convertToJson(test_input)
    assert result == {"key": "value"}

def test_split_tuple_object(service):
    """Test tuple object splitting"""
    test_input = {"key": "value"}
    key, value = service.split_tuple_object(test_input)
    assert key == "key"
    assert value == "value"

# Reranking functionality tests
def test_extract_numeric_components(service):
    """Test extraction of numeric components from strength strings"""
    # Test various strength formats
    assert service._extract_numeric_components("10 mg") == ["10"]
    assert service._extract_numeric_components("2.5 mg") == ["2.5"]
    assert service._extract_numeric_components("10/25 mg") == ["10", "25"]
    assert service._extract_numeric_components("100mg/5ml") == ["100", "5"]
    assert service._extract_numeric_components("0.25 mg") == ["0.25"]
    assert service._extract_numeric_components("12.5/25 mg") == ["12.5", "25"]
    
    # Test edge cases
    assert service._extract_numeric_components("") == []
    assert service._extract_numeric_components(None) == []
    assert service._extract_numeric_components("no numbers here") == []
    assert service._extract_numeric_components("mg only") == []

# New tests using MedispanMatchConfig

@pytest.fixture
def service_with_rerank_config():
    """Service with reranking enabled"""
    config = MedispanMatchConfig(
        v2_enabled_globally=True,
        v2_settings=MedispanMatchConfig.MedispanMatchV2Settings(
            rerank_settings=MedispanMatchConfig.RerankSettings(
                enabled=True,
                rerank_strength_enabled=True,
                rerank_form_enabled=True,
                strength_ranking_eligible_forms=["tablet", "capsule", "powder"]
            )
        )
    )
    return MedispanMatchService("test_tenant", config)

@pytest.fixture
def service_with_rerank_disabled():
    """Service with reranking disabled"""
    config = MedispanMatchConfig(
        v2_enabled_globally=True,
        v2_settings=MedispanMatchConfig.MedispanMatchV2Settings(
            rerank_settings=MedispanMatchConfig.RerankSettings(
                enabled=False,
                rerank_strength_enabled=False,
                rerank_form_enabled=False
            )
        )
    )
    return MedispanMatchService("test_tenant", config)

def test_rerank_medications_successful_strength_reranking(service_with_rerank_config):
    """Test successful strength reranking when conditions are met"""
    extracted_medication = MedicationValue(
        name="Lisinopril",
        strength="10 mg",
        form="tablet",
        route="oral"
    )
    
    medispan_results = [
        MedispanDrug(
            id="1",
            NameDescription="Lisinopril 5mg Tablet",
            GenericName="Lisinopril",
            Route="Oral",
            Strength="5",
            StrengthUnitOfMeasure="mg",
            Dosage_Form="tablet"
        ),
        MedispanDrug(
            id="2",
            NameDescription="Lisinopril 10mg Tablet",
            GenericName="Lisinopril",
            Route="Oral",
            Strength="10",
            StrengthUnitOfMeasure="mg",
            Dosage_Form="tablet"
        ),
        MedispanDrug(
            id="3",
            NameDescription="Lisinopril 20mg Tablet",
            GenericName="Lisinopril",
            Route="Oral",
            Strength="20",
            StrengthUnitOfMeasure="mg",
            Dosage_Form="tablet"
        )
    ]
    
    reranked = service_with_rerank_config.rerank_medications(medispan_results, "Lisinopril 10 mg tablet", extracted_medication)
    
    # Verify that 10mg medication is moved to the top
    assert len(reranked) == 3
    assert reranked[0].Strength == "10"
    assert reranked[0].id == "2"

def test_rerank_medications_successful_form_reranking(service_with_rerank_config):
    """Test successful form reranking"""
    extracted_medication = MedicationValue(
        name="Lisinopril",
        strength="10 mg",
        form="capsule",
        route="oral"
    )
    
    medispan_results = [
        MedispanDrug(
            id="1",
            NameDescription="Lisinopril 10mg Tablet",
            GenericName="Lisinopril",
            Route="Oral",
            Strength="10",
            Dosage_Form="tablet"
        ),
        MedispanDrug(
            id="2",
            NameDescription="Lisinopril 10mg Capsule",
            GenericName="Lisinopril",
            Route="Oral",
            Strength="10",
            Dosage_Form="capsule"
        ),
        MedispanDrug(
            id="3",
            NameDescription="Lisinopril 10mg Injection",
            GenericName="Lisinopril",
            Route="IV",
            Strength="10",
            Dosage_Form="injection"
        )
    ]
    
    reranked = service_with_rerank_config.rerank_medications(medispan_results, "Lisinopril 10 mg capsule", extracted_medication)
    
    # Verify that capsule form is moved to the top
    assert len(reranked) == 3
    assert reranked[0].Dosage_Form == "capsule"
    assert reranked[0].id == "2"

def test_rerank_medications_priority_based(service_with_rerank_config):
    """Test that reranking follows proper priority: both matches, strength only, form only, no matches"""
    extracted_medication = MedicationValue(
        name="Lisinopril",
        strength="10 mg",
        form="tablet",
        route="oral"
    )
    
    medispan_results = [
        MedispanDrug(
            id="1",
            NameDescription="Lisinopril 5mg Capsule",
            GenericName="Lisinopril",
            Route="Oral",
            Strength="5",
            Dosage_Form="capsule"
        ),
        MedispanDrug(
            id="2",
            NameDescription="Lisinopril 20mg Tablet",
            GenericName="Lisinopril",
            Route="Oral",
            Strength="20",
            Dosage_Form="tablet"
        ),
        MedispanDrug(
            id="3",
            NameDescription="Lisinopril 10mg Tablet",
            GenericName="Lisinopril",
            Route="Oral",
            Strength="10",
            Dosage_Form="tablet"
        ),
        MedispanDrug(
            id="4",
            NameDescription="Lisinopril 10mg Capsule",
            GenericName="Lisinopril",
            Route="Oral",
            Strength="10",
            Dosage_Form="capsule"
        )
    ]
    
    reranked = service_with_rerank_config.rerank_medications(medispan_results, "Lisinopril 10 mg tablet", extracted_medication)
    
    # First should be both form AND strength match (highest priority)
    assert reranked[0].Dosage_Form == "tablet"
    assert reranked[0].Strength == "10"
    assert reranked[0].id == "3"
    
    # Second should be strength only match
    assert reranked[1].Dosage_Form == "capsule"
    assert reranked[1].Strength == "10"
    assert reranked[1].id == "4"
    
    # Third should be form only match
    assert reranked[2].Dosage_Form == "tablet"
    assert reranked[2].Strength == "20"
    assert reranked[2].id == "2"
    
    # Fourth should be no matches
    assert reranked[3].Dosage_Form == "capsule"
    assert reranked[3].Strength == "5"
    assert reranked[3].id == "1"

def test_rerank_medications_disabled(service_with_rerank_disabled):
    """Test that reranking is bypassed when disabled"""
    extracted_medication = MedicationValue(
        name="Lisinopril",
        strength="10 mg",
        form="tablet",
        route="oral"
    )
    
    medispan_results = [
        MedispanDrug(id="1", NameDescription="Lisinopril 5mg", GenericName="Lisinopril", Route="Oral", Strength="5", Dosage_Form="tablet"),
        MedispanDrug(id="2", NameDescription="Lisinopril 10mg", GenericName="Lisinopril", Route="Oral", Strength="10", Dosage_Form="tablet"),
    ]
    
    reranked = service_with_rerank_disabled.rerank_medications(medispan_results, "test", extracted_medication)
    
    # Should return original order when disabled
    assert reranked == medispan_results

def test_rerank_medications_form_only_enabled():
    """Test when only form reranking is enabled"""
    config = MedispanMatchConfig(
        v2_enabled_globally=True,
        v2_settings=MedispanMatchConfig.MedispanMatchV2Settings(
            rerank_settings=MedispanMatchConfig.RerankSettings(
                enabled=True,
                rerank_strength_enabled=False,
                rerank_form_enabled=True
            )
        )
    )
    service = MedispanMatchService("test_tenant", config)
    
    extracted_medication = MedicationValue(
        name="Lisinopril",
        strength="10 mg",
        form="tablet",
        route="oral"
    )
    
    medispan_results = [
        MedispanDrug(id="1", NameDescription="Lisinopril 10mg Capsule", GenericName="Lisinopril", Route="Oral", Strength="10", Dosage_Form="capsule"),
        MedispanDrug(id="2", NameDescription="Lisinopril 5mg Tablet", GenericName="Lisinopril", Route="Oral", Strength="5", Dosage_Form="tablet"),
        MedispanDrug(id="3", NameDescription="Lisinopril 10mg Tablet", GenericName="Lisinopril", Route="Oral", Strength="10", Dosage_Form="tablet"),
    ]
    
    reranked = service.rerank_medications(medispan_results, "test", extracted_medication)
    
    # Tablets should be moved to top, but strength order should remain unchanged
    assert reranked[0].Dosage_Form == "tablet"
    assert reranked[1].Dosage_Form == "tablet"
    assert reranked[2].Dosage_Form == "capsule"
    # Original order within tablets should be preserved (5mg then 10mg)
    assert reranked[0].Strength == "5"
    assert reranked[1].Strength == "10"

def test_rerank_medications_strength_only_enabled():
    """Test when only strength reranking is enabled"""
    config = MedispanMatchConfig(
        v2_enabled_globally=True,
        v2_settings=MedispanMatchConfig.MedispanMatchV2Settings(
            rerank_settings=MedispanMatchConfig.RerankSettings(
                enabled=True,
                rerank_strength_enabled=True,
                rerank_form_enabled=False,
                strength_ranking_eligible_forms=["tablet", "capsule"]
            )
        )
    )
    service = MedispanMatchService("test_tenant", config)
    
    extracted_medication = MedicationValue(
        name="Lisinopril",
        strength="10 mg",
        form="tablet",
        route="oral"
    )
    
    medispan_results = [
        MedispanDrug(id="1", NameDescription="Lisinopril 5mg", GenericName="Lisinopril", Route="Oral", Strength="5", Dosage_Form="tablet"),
        MedispanDrug(id="2", NameDescription="Lisinopril 10mg", GenericName="Lisinopril", Route="Oral", Strength="10", Dosage_Form="tablet"),
    ]
    
    reranked = service.rerank_medications(medispan_results, "test", extracted_medication)
    
    # 10mg should be moved to top
    assert reranked[0].Strength == "10"
    assert reranked[1].Strength == "5"

def test_rerank_medications_case_insensitive_form(service_with_rerank_config):
    """Test that form matching is case insensitive"""
    extracted_medication = MedicationValue(
        name="Lisinopril",
        strength="10 mg",
        form="TABLET",  # Uppercase form
        route="oral"
    )
    
    medispan_results = [
        MedispanDrug(id="1", NameDescription="Lisinopril 5mg", GenericName="Lisinopril", Route="Oral", Strength="5", Dosage_Form="capsule"),
        MedispanDrug(id="2", NameDescription="Lisinopril 10mg", GenericName="Lisinopril", Route="Oral", Strength="10", Dosage_Form="tablet"),
    ]
    
    reranked = service_with_rerank_config.rerank_medications(medispan_results, "test", extracted_medication)
    
    # Should perform reranking despite case difference
    assert reranked[0].Dosage_Form == "tablet"

def test_rerank_medications_no_form_specified(service_with_rerank_config):
    """Test behavior when no form is specified in extracted medication"""
    extracted_medication = MedicationValue(
        name="Lisinopril",
        strength="10 mg",
        form=None,
        route="oral"
    )
    
    medispan_results = [
        MedispanDrug(id="1", NameDescription="Lisinopril 5mg", GenericName="Lisinopril", Route="Oral", Strength="5", Dosage_Form="tablet"),
        MedispanDrug(id="2", NameDescription="Lisinopril 10mg", GenericName="Lisinopril", Route="Oral", Strength="10", Dosage_Form="tablet"),
    ]
    
    reranked = service_with_rerank_config.rerank_medications(medispan_results, "test", extracted_medication)
    
    # Should return original order when no form specified
    assert reranked == medispan_results

def test_rerank_medications_empty_results(service_with_rerank_config):
    """Test reranking with empty medispan results"""
    extracted_medication = MedicationValue(
        name="Lisinopril",
        strength="10 mg",
        form="tablet",
        route="oral"
    )
    
    medispan_results = []
    
    reranked = service_with_rerank_config.rerank_medications(medispan_results, "test", extracted_medication)
    
    # Should return empty list
    assert reranked == []

def test_rerank_medications_with_total_results_limit():
    """Test that reranking respects the total_results configuration limit"""
    config = MedispanMatchConfig(
        v2_enabled_globally=True,
        v2_settings=MedispanMatchConfig.MedispanMatchV2Settings(
            total_results=2,  # Limit to 2 results
            rerank_settings=MedispanMatchConfig.RerankSettings(
                enabled=True,
                rerank_strength_enabled=True,
                rerank_form_enabled=True,
                strength_ranking_eligible_forms=["tablet", "capsule"]
            )
        )
    )
    service = MedispanMatchService("test_tenant", config)
    
    extracted_medication = MedicationValue(
        name="Lisinopril",
        strength="10 mg",
        form="tablet",
        route="oral"
    )
    
    medispan_results = [
        MedispanDrug(
            id="1",
            NameDescription="Lisinopril 5mg Capsule",
            GenericName="Lisinopril",
            Route="Oral",
            Strength="5",
            Dosage_Form="capsule"
        ),
        MedispanDrug(
            id="2",
            NameDescription="Lisinopril 20mg Tablet",
            GenericName="Lisinopril",
            Route="Oral",
            Strength="20",
            Dosage_Form="tablet"
        ),
        MedispanDrug(
            id="3",
            NameDescription="Lisinopril 10mg Tablet",
            GenericName="Lisinopril",
            Route="Oral",
            Strength="10",
            Dosage_Form="tablet"
        ),
        MedispanDrug(
            id="4",
            NameDescription="Lisinopril 10mg Capsule",
            GenericName="Lisinopril",
            Route="Oral",
            Strength="10",
            Dosage_Form="capsule"
        )
    ]
    
    reranked = service.rerank_medications(medispan_results, "Lisinopril 10 mg tablet", extracted_medication)
    
    # Should be limited to 2 results as configured
    assert len(reranked) == 2
    
    # Should still follow priority order within the limit
    # First should be both form AND strength match (highest priority)
    assert reranked[0].Dosage_Form == "tablet"
    assert reranked[0].Strength == "10"
    assert reranked[0].id == "3"
    
    # Second should be strength only match
    assert reranked[1].Dosage_Form == "capsule"
    assert reranked[1].Strength == "10"
    assert reranked[1].id == "4"

def test_limit_results_when_reranking_disabled():
    """Test that result limiting still works when reranking is disabled"""
    config = MedispanMatchConfig(
        v2_enabled_globally=True,
        v2_settings=MedispanMatchConfig.MedispanMatchV2Settings(
            total_results=2,  # Limit to 2 results
            rerank_settings=MedispanMatchConfig.RerankSettings(
                enabled=False,  # Reranking disabled
                rerank_strength_enabled=False,
                rerank_form_enabled=False
            )
        )
    )
    service = MedispanMatchService("test_tenant", config)
    
    extracted_medication = MedicationValue(
        name="Lisinopril",
        strength="10 mg",
        form="tablet",
        route="oral"
    )
    
    medispan_results = [
        MedispanDrug(id="1", NameDescription="Lisinopril 5mg", GenericName="Lisinopril", Route="Oral", Strength="5", Dosage_Form="tablet"),
        MedispanDrug(id="2", NameDescription="Lisinopril 10mg", GenericName="Lisinopril", Route="Oral", Strength="10", Dosage_Form="tablet"),
        MedispanDrug(id="3", NameDescription="Lisinopril 20mg", GenericName="Lisinopril", Route="Oral", Strength="20", Dosage_Form="tablet"),
    ]
    
    reranked = service.rerank_medications(medispan_results, "test", extracted_medication)
    
    # Should be limited to 2 results even when reranking is disabled
    assert len(reranked) == 2
    # Should maintain original order (first 2 items)
    assert reranked[0].id == "1"
    assert reranked[1].id == "2"
