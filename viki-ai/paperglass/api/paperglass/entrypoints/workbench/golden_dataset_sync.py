import asyncio
import os
import re
import pandas as pd
import io
from datetime import datetime
from typing import Dict, Any, List
from office365.runtime.auth.client_credential import ClientCredential
from office365.sharepoint.client_context import ClientContext

from google.cloud import firestore
from paperglass.domain.time import now_utc
from paperglass.settings import (
    GCP_FIRESTORE_DB,
    SHAREPOINT_CLIENT_ID,
    SHAREPOINT_CLIENT_SECRET
)

from paperglass.log import getLogger
LOGGER = getLogger(__name__)

DOCUMENT_ID_MAPPING = {
    'test data1': '5f88a17aab8c11efaa3a00155d9cb27a',
    'test data2': '60420d7dab8c11efaa3a00155d9cb27a',
    'test data3': '619820b3ab8c11efaa3a00155d9cb27a',
    'test data4': '63e5f5d8ab8c11efaa3a00155d9cb27a',
    'test data5': '6521ed80ab8c11efaa3a00155d9cb27a',
    'test data6': 'b87cdcd8ab8c11efaa3a00155d9cb27a',
    'test data7': 'ba2041e2ab8c11efaa3a00155d9cb27a',
    'test data8': 'bb859f5aab8c11efaa3a00155d9cb27a',
    'test data9': 'bccbf206ab8c11efaa3a00155d9cb27a',
    'test data10': 'be0aa22aab8c11efaa3a00155d9cb27a',
    'test data11': '1698a090ab8d11efaa3a00155d9cb27a',
    'test data12': '1745ee1dab8d11efaa3a00155d9cb27a',
    'test data13': '1878154fab8d11efaa3a00155d9cb27a',
    'test data14': '19c26fe5ab8d11efaa3a00155d9cb27a',
    'test data15': '1c617baaab8d11efaa3a00155d9cb27a',
    'test data16': '6aafa278ab8d11efaa3a00155d9cb27a',
    'test data17': '6c514d7aab8d11efaa3a00155d9cb27a',
    'test data18': '6d9e894aab8d11efaa3a00155d9cb27a',
    'test data19': '6ec2ac16ab8d11efaa3a00155d9cb27a',
    'test data20': '700dece8ab8d11efaa3a00155d9cb27a',
    'test data21': '7b1b548ab07011ef933f42004e494300',
    'test data22': '80c1fd62b07011ef933f42004e494300',
    'test data23': '89414aa6b07011ef933f42004e494300',
    'test data24': '93fcf1acb07011ef933f42004e494300',
    'test data25': 'b5faf984b07011ef933f42004e494300',
    'test data26': '0577ea96b07411ef933f42004e494300',
    'test data27': '08c9db14b07411ef933f42004e494300',
    'test data28': '0c49e770b07411ef933f42004e494300',
    'test data29': '10ad2a52b07411ef933f42004e494300',
    'test data30': '2a84aa4ab07411ef933f42004e494300',
    'test data31': '95385dfab07411ef933f42004e494300',
    'test data32': '9921922eb07411ef933f42004e494300',
    'test data33': '9d96faa6b07411ef933f42004e494300',
    'test data34': 'abdc72a8b07411ef933f42004e494300',
    'test data35': 'b42ec83eb07411ef933f42004e494300',
    'test data36': 'e860663ab07411ef933f42004e494300',
    'test data37': 'f129871ab07411ef933f42004e494300',
    'test data38': 'f8b66a2ab07411ef933f42004e494300',
    'test data39': '138ce248b07511ef933f42004e494300',
    'test data40': '4c02a842b07511ef933f42004e494300',
    'test data41': '50772d80b07511ef933f42004e494300',
    'test data42': '5889f8c2b07511ef933f42004e494300',
    'test data43': '9a6e54c2b07511ef933f42004e494300',
    'test data44': 'b8dcf6cab07511ef933f42004e494300',
    'test data45': 'c7e9e902b07511ef933f42004e494300'
}

class GoldenDatasetSync:

    def __init__(self):
        self.db = firestore.AsyncClient(database=GCP_FIRESTORE_DB)
        self.collection_name = "paperglass_test_cases_golden_dataset"
        self.archive_collection_name = f"{self.collection_name}_archive"
        
        # SharePoint configuration
        self.sharepoint_site = "https://mediwareinformationsystems.sharepoint.com/sites/EAI-SPace"
        self.file_url = "/sites/EAI-SPace/Shared Documents/AI/Medical Extraction/Golden Dataset/Master_sheet_v2.xlsx"
        
        # Initialize SharePoint client
        credentials = ClientCredential(SHAREPOINT_CLIENT_ID, SHAREPOINT_CLIENT_SECRET)
        self.ctx = ClientContext(self.sharepoint_site).with_credentials(credentials)

    def normalize_document_name(self, test_document: str) -> str:
        clean_name = test_document.lower().replace('.pdf', '').strip()
        match = re.search(r'test\s*data\s*(\d+)', clean_name)
        if match:
            return f"test data{match.group(1)}"
        return clean_name

    def get_document_id(self, test_document: str) -> str:
        normalized_name = self.normalize_document_name(test_document)
        doc_id = DOCUMENT_ID_MAPPING.get(normalized_name)
        
        if not doc_id:
            LOGGER.warning(f"No document_id mapping found for {test_document} (normalized: {normalized_name})")
        else:
            LOGGER.debug(f"Mapped {test_document} to document_id {doc_id}")
            
        return doc_id

    def normalize_value(self, value: Any) -> Any:
        if pd.isna(value):
            return None
        if isinstance(value, (int, float)):
            return str(value)
        if isinstance(value, pd.Timestamp):
            return value.strftime('%m/%d/%Y')
        return value

    def read_excel_file(self) -> List[Dict[str, Any]]:
        try:
            # Get file from SharePoint
            file = self.ctx.web.get_file_by_server_relative_url(self.file_url)
            file_content = io.BytesIO()
            file.download_session(file_content).execute_query()
            file_content.seek(0)
            
            # Read Excel file from bytes
            file_bytes = file_content
            df = pd.read_excel(file_bytes)
            records = []
            current_doc = None
            current_medications = []
            
            for _, row in df.iterrows():
                if pd.notna(row['test_document']):
                    if current_doc is not None:
                        current_doc['test_expected']['medication'] = current_medications
                        current_doc['test_expected']['list_of_medispan_ids'] = [
                            med['medispan_id'] for med in current_medications 
                            if med['medispan_id'] is not None
                        ]
                        records.append(current_doc)
                    
                    doc_id = self.get_document_id(row['test_document'])
                    if not doc_id:
                        continue
                    
                    current_doc = {
                        'document_id': row['document_id'],
                        'execution_id': doc_id,
                        'test_document': row['test_document'],
                        'app_id': '007',
                        'patient_id': '7c03ff786c904cf5a128704d5a1081f7',
                        'tenant_id': '54321',
                        'active': True,
                        'modified_by': None,
                        'created_by': None,
                        'document_operation_instance_id': None,
                        'category': 'golden-medication-extraction',
                        'test_expected': {
                            'total_count': int(row['total_count']) if pd.notna(row['total_count']) else 0,
                            'medispan_matched_count': int(row['medispan_matched_count']) if pd.notna(row['medispan_matched_count']) else 0,
                            'unlisted_count': int(row['unlisted_count']) if pd.notna(row['unlisted_count']) else 0,
                            'medication': []
                        }
                    }
                    current_medications = []
                
                if pd.notna(row['name']):
                    medication = {
                        'name': self.normalize_value(row['name']),
                        'brand_name': self.normalize_value(row['brand_name']),
                        'route': self.normalize_value(row['route']),
                        'page_number': self.normalize_value(row['page_number']),
                        'frequency': self.normalize_value(row['frequency']),
                        'strength': self.normalize_value(row['strength']),
                        'instructions': self.normalize_value(row['instructions']),
                        'medispan_id': str(int(row['medispan_id'])) if pd.notna(row['medispan_id']) else None,
                        'dosage': self.normalize_value(row['dosage']),
                        'start_date': self.normalize_value(row['start_date']),
                        'form': self.normalize_value(row['form'])
                    }
                    current_medications.append(medication)
            
            if current_doc is not None:
                current_doc['test_expected']['medication'] = current_medications
                current_doc['test_expected']['list_of_medispan_ids'] = [
                    med['medispan_id'] for med in current_medications 
                    if med['medispan_id'] is not None
                ]
                records.append(current_doc)
            
            return records
        except Exception as e:
            LOGGER.error(f"Error reading Excel file: {str(e)}")
            raise

    def has_changes(self, new_data: Dict[str, Any], existing_data: Dict[str, Any]) -> bool:
        new_test_expected = new_data['test_expected']
        existing_test_expected = existing_data['test_expected']
        
        if (new_test_expected['total_count'] != existing_test_expected['total_count'] or
            new_test_expected['medispan_matched_count'] != existing_test_expected['medispan_matched_count'] or
            new_test_expected['unlisted_count'] != existing_test_expected['unlisted_count']):
            return True
            
        new_meds = sorted(new_test_expected['medication'], key=lambda x: (x['name'], x.get('medispan_id', '')))
        existing_meds = sorted(existing_test_expected['medication'], key=lambda x: (x['name'], x.get('medispan_id', '')))
        
        if len(new_meds) != len(existing_meds):
            return True
            
        for new_med, existing_med in zip(new_meds, existing_meds):
            # Check if there are any differences in keys
            if set(new_med.keys()) != set(existing_med.keys()):
                return True
            # Compare all values, using get() for safe access
            if any(new_med.get(key) != existing_med.get(key) for key in new_med.keys()):
                return True
                
        return False

    async def create_testcase(self, doc_id: str, data: Dict[str, Any]):
        """Create a new testcase in Firestore"""
        try:
            data['created_at'] = now_utc().isoformat()
            data['modified_at'] = now_utc().isoformat()
            
            doc_ref = self.db.collection(self.collection_name).document(doc_id)
            await doc_ref.set(data)
            LOGGER.debug(f"Created testcase {doc_id}")
        except Exception as e:
            LOGGER.error(f"Error creating testcase {doc_id}: {str(e)}")
            raise

    async def update_testcase(self, doc_id: str, new_data: Dict[str, Any], existing_doc: Dict[str, Any]):
        try:
            if not self.has_changes(new_data, existing_doc):
                LOGGER.debug(f"No changes detected for testcase {doc_id}, skipping update")
                return False
                
            new_data['modified_at'] =now_utc().isoformat()
            new_data['created_at'] = existing_doc['created_at']
            
            doc_ref = self.db.collection(self.collection_name).document(doc_id)
            await doc_ref.set(new_data)
            LOGGER.debug(f"Updated testcase {doc_id}")
            return True
        except Exception as e:
            LOGGER.error(f"Error updating testcase {doc_id}: {str(e)}")
            raise

    async def sync_golden_dataset(self):
        try:
            golden_dataset = self.read_excel_file()
            processed_docs = set()
            updated = 0
            created = 0
            for item in golden_dataset:
                doc_id = item.get("document_id")
                if not doc_id:
                    LOGGER.warning(f"Skipping item without document_id")
                    continue
                
                if doc_id in processed_docs:
                    continue
                processed_docs.add(doc_id)
                
                doc_ref = self.db.collection(self.collection_name).document(doc_id)
                doc = await doc_ref.get()
                
                if doc.exists:
                    result = await self.update_testcase(doc_id, item, doc.to_dict())
                    if result:
                        updated += 1
                else:
                    await self.create_testcase(doc_id, item)
                    created += 1
            
            LOGGER.debug("Golden Dataset sync completed successfully")
            return updated, created, len(golden_dataset)
        except Exception as e:
            LOGGER.error(f"Error in golden Dataset sync: {str(e)}")
            raise

async def run():
    try:
        syncer = GoldenDatasetSync()
        await syncer.sync_golden_dataset()
    except Exception as e:
        LOGGER.error(f"Workbench error for sync of golden Data set: {str(e)}")
        raise

def main():
    asyncio.run(run())

if __name__ == "__main__":
    main()
