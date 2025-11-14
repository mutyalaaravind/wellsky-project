import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from src.adapters.firestore_vector_adapter import MedispanFirestoreVectorAdapter
from src.models import MedispanDrug
from google.cloud.firestore_v1.base_query import FieldFilter
import settings

def test_medispan_drug_creation():
    # Direct instantiation test
    drug = MedispanDrug(
        id='123',
        NameDescription='Test Drug 10mg',
        GenericName='Test Generic',
        Route='ORAL',
        Strength='10',
        StrengthUnitOfMeasure='mg',
        Dosage_Form='TABLET'
    )
    assert isinstance(drug, MedispanDrug)
    
    # Dict conversion test
    data = {
        'id': '123',
        'NameDescription': 'Test Drug 10mg',
        'GenericName': 'Test Generic',
        'Route': 'ORAL',
        'Strength': '10',
        'StrengthUnitOfMeasure': 'mg',
        'Dosage_Form': 'TABLET'
    }
    drug_from_dict = MedispanDrug.model_validate(data)
    assert isinstance(drug_from_dict, MedispanDrug)

@pytest.fixture
def mock_firestore_client():
    with patch('google.cloud.firestore.Client') as mock:
        mock.return_value = MagicMock()
        yield mock

@pytest.fixture
def sample_drug_data():
    return {
        'id': '123',
        'NameDescription': 'Test Drug 10mg',
        'GenericName': 'Test Generic',
        'Strength': '10',
        'StrengthUnitOfMeasure': 'mg',
        'Route': 'ORAL',
        'Dosage_Form': 'TABLET',
        'namedescription_lower': 'test drug 10mg'
    }

@pytest.mark.asyncio
async def test_init(mock_firestore_client):
    adapter = MedispanFirestoreVectorAdapter(app_id="test", catalog="medispan")
    assert adapter.app_id == "test"
    assert adapter.catalog == "medispan"
    mock_firestore_client.assert_called_once_with(
        project=settings.GCP_PROJECT_ID,
        database=settings.GCP_FIRESTORE_DB
    )

@pytest.mark.asyncio
async def test_convert_firestore_to_medispan_drug(sample_drug_data):
    drug = MedispanDrug(
        id=str(sample_drug_data['id']),
        NameDescription=sample_drug_data['NameDescription'],
        GenericName=sample_drug_data['GenericName'],
        Route=sample_drug_data['Route'],
        Strength=sample_drug_data['Strength'],
        StrengthUnitOfMeasure=sample_drug_data['StrengthUnitOfMeasure'],
        Dosage_Form=sample_drug_data['Dosage_Form']
    )
    assert isinstance(drug, MedispanDrug)
    assert drug.id == sample_drug_data['id']
    assert drug.NameDescription == sample_drug_data['NameDescription']

@pytest.mark.asyncio
async def test_keyword_search(mock_firestore_client, sample_drug_data):
    adapter = MedispanFirestoreVectorAdapter(app_id="test", catalog="medispan")
    
    # Create mock document
    mock_doc = MagicMock()
    mock_doc.id = sample_drug_data['id']
    mock_doc.to_dict.return_value = {k: v for k, v in sample_drug_data.items() if k != 'id'}

    # Set up collection query chain
    collection_mock = MagicMock()
    mock_firestore_client.return_value.collection.return_value = collection_mock
    
    query_mock = MagicMock()
    collection_mock.where.return_value = query_mock
    query_mock.where.return_value = query_mock
    query_mock.limit.return_value = query_mock
    query_mock.stream.return_value = [mock_doc]

    result = await adapter.keyword_search(
        description="test drug",
        dosage_form="tablet",
        route="oral"
    )

    assert len(result) == 1
    assert result[0]['id'] == sample_drug_data['id']
    assert result[0]['NameDescription'] == sample_drug_data['NameDescription']
    
@pytest.mark.asyncio
async def test_search_by_vector(mock_firestore_client, sample_drug_data):
    adapter = MedispanFirestoreVectorAdapter(app_id="test", catalog="medispan")
    
    # Create mock document
    mock_doc = MagicMock()
    mock_doc.id = sample_drug_data['id']
    sample_data_with_embedding = {**sample_drug_data, 'med_embedding': [0.1, 0.2, 0.3]}
    mock_doc.to_dict.return_value = {k: v for k, v in sample_data_with_embedding.items() if k != 'id'}

    # Set up collection query chain
    collection_mock = MagicMock()
    mock_firestore_client.return_value.collection.return_value = collection_mock
    
    query_mock = MagicMock()
    collection_mock.find_nearest.return_value = query_mock
    query_mock.stream.return_value = [mock_doc]

    result = await adapter.search_by_vector(
        embedding=[0.1, 0.2, 0.3],
        similarity_threshold=0.7,
        max_results=5
    )

    assert len(result) == 1
    assert result[0]['id'] == sample_drug_data['id']
    assert result[0]['NameDescription'] == sample_drug_data['NameDescription']
