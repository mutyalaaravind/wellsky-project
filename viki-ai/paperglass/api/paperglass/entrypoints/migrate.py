"""
use this script to migrate existing data to new medication profile based schema
pre-requisites:
makefile: - change stage and SELF_API to appropriate value
gcloud auth application-default login --impersonate-service-account=viki-ai-{env}-sa@viki-{env}-app-wsky.iam.gserviceaccount.com
gcloud auth login
gcloud config set project viki-{env}-app-wsky
$(PIPENV) run python paperglass/entrypoints/app_integration_launcher.py
"""
import sys,os



sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from paperglass.interface.ports import ICommandHandlingPort
from paperglass.usecases.commands import Orchestrate
from paperglass.settings import OKTA_CLIENT_SECRET
import json,asyncio,jwt
from google.cloud import firestore
from kink import inject

async def get_all_documents():
     
    async def get_docs():
        # Connect to Firestore
        db = firestore.Client(project=os.environ.get("GCP_PROJECT_ID"))

        # Define the collection and document
        collection_name = "paperglass_documents"

        # Create a new document with a generated ID
        doc_ref = db.collection(collection_name).get()
        docs = [doc.to_dict() for doc in doc_ref]
        return docs 
    
    docs = await get_docs()
    with open(f'./.logs/migration/{os.environ["STAGE"]}-documents.txt',"w+") as f:
        for doc in docs:
            f.write(doc.get("id")+"\n")

@inject()
async def run_migrations(command_handler:ICommandHandlingPort):
    def get_doc(id):
        # Connect to Firestore
        db = firestore.Client(project=os.environ.get("GCP_PROJECT_ID"))

        # Define the collection and document
        collection_name = "paperglass_documents"

        # Create a new document with a generated ID
        doc_ref = db.collection(collection_name).document(id).get()
        return doc_ref.to_dict()
    
    docs = open(f'./.logs/migration/{os.environ["STAGE"]}-documents.txt',"r").readlines()
    os.environ["CLOUD_PROVIDER"] = "GCP"
    with open(f'./.logs/migration/{os.environ["STAGE"]}-done.txt',"a+") as logger:
        for document_id in docs:
            print(document_id)
            doc = get_doc(document_id.strip())
            patient_id=doc.get("patient_id")
            user_id="vipindas.koova@wellsky.com"
            tenant_id=doc.get("tenant_id")
            app_id=doc.get("app_id")
            document_id = doc.get("id")
            logger.seek(0)
            logs = logger.read()
            logs_json = None
            if logs:
                if f"{document_id}-success" in logs:
                    continue
            if app_id and tenant_id and patient_id and user_id:
                # call orchestration event if in cloud. if local call orchestrator directly
                encoded_token = jwt.encode({'appId': app_id, 'tenantId':tenant_id,'patientId':patient_id,'amuserkey':user_id}, OKTA_CLIENT_SECRET,algorithm='HS256')
                result = await command_handler.handle_command(Orchestrate(patient_id=patient_id,
                                                            app_id=app_id,
                                                            tenant_id=tenant_id,
                                                            document_id=document_id,
                                                            token=encoded_token))
                if result == {}:
                    logger.write(f"{document_id}-success\n")
                else:
                    logger.write(f"{document_id}-failed-{result}\n")
                                                            


if __name__ == '__main__':
    #asyncio.run(get_all_documents())
    asyncio.run(run_migrations())