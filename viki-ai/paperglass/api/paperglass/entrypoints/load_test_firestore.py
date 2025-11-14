import asyncio
import time,sys,os
import statistics
from typing import List, Dict, Optional
from google.cloud import firestore
from concurrent.futures import ThreadPoolExecutor
import argparse
import json
from datetime import datetime
import google.auth
import google.auth.transport.requests

from kink import inject

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from paperglass.infrastructure.ports import IQueryPort
from paperglass.usecases.documents import get_document_status_logs_summarized, get_documents

from paperglass.domain.utils.opentelemetry_utils import bootstrap_opentelemetry
import aiohttp
import random

bootstrap_opentelemetry(__name__)

class FirestoreLoadTester:
    def __init__(self, collection_name: str, num_requests: int, batch_size: int):
        self.db = None #firestore.Client()
        self.collection_name = collection_name
        self.num_requests = num_requests
        self.batch_size = batch_size
        self.response_times = []
        self.errors = []
        self.executor = ThreadPoolExecutor(max_workers=batch_size)
        self._token = None
        self._token_expiry = None
        
    async def _get_auth_token(self) -> str:
        """Get a valid authentication token, refreshing if necessary"""
        current_time = datetime.now()
        
        # If token exists and is not expired, return it
        if self._token and self._token_expiry and current_time < self._token_expiry:
            return self._token
            
        # Otherwise, get new token
        credentials, project = google.auth.default(
            scopes=['https://www.googleapis.com/auth/datastore']
        )
        
        auth_req = google.auth.transport.requests.Request()
        credentials.refresh(auth_req)
        
        self._token = credentials.token
        # Set token expiry to slightly before the actual expiry to ensure we refresh in time
        #self._token_expiry = datetime.now() + credentials.expiry.replace(microsecond=0) - datetime.now() - datetime.timedelta(minutes=5)
        
        return self._token
        
    async def query_firestore_rest(self, where_conditions: Optional[List[Dict]] = None) -> float:
        """Execute a single query to Firestore using REST API and measure response time
        
        Args:
            query: The query port interface
            where_conditions: Optional list of where conditions, each condition being a dict with:
                - field: Field name to filter on
                - op: Operator ('==', '>', '<', '>=', '<=', '!=')
                - value: Value to compare against
        """
        start_time = time.time()
        try:
            # Get fresh token
            token = await self._get_auth_token()
            
            url = f"https://firestore.googleapis.com/v1/projects/{self.db.project}/databases/viki-stage/documents/{self.collection_name}"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }
            # Construct structured query if where conditions are provided
            if where_conditions:
                body = {
                    "structuredQuery": {
                        "from": [{"collectionId": self.collection_name}],
                        "where": {
                            "compositeFilter": {
                                "op": "AND",
                                "filters": [
                                    {
                                        "fieldFilter": {
                                            "field": {"fieldPath": cond["field"]},
                                            "op": self._convert_operator(cond["op"]),
                                            "value": self._convert_value(cond["value"])
                                        }
                                    }
                                    for cond in where_conditions
                                ]
                            }
                        },
                        "limit": 10
                    }
                }
                
                async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
                    async with session.post(
                        f"https://firestore.googleapis.com/v1/projects/{self.db.project}/databases/viki-stage/documents:runQuery",
                        headers=headers,
                        json=body
                    ) as response:
                        #import pdb;pdb.set_trace()
                        if response.status != 200:
                            raise Exception(f"Failed to query Firestore: {response.status} {await response.json()}")
                        data = await response.json()
                        #print(json.dumps(data, indent=2))  # Pretty print the response
            else:
                # Simple GET request if no where conditions
                async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
                    async with session.get(url, headers=headers) as response:
                        if response.status != 200:
                            raise Exception(f"Failed to query Firestore: {response.status}")
                        data = await response.json()
                        #print(json.dumps(data, indent=2))  # Pretty print the response
            
            duration = time.time() - start_time
            return duration
        except Exception as e:
            print(str(e))
            self.errors.append(str(e))
            return -1

    def _convert_operator(self, op: str) -> str:
        """Convert Python-style operators to Firestore REST API operators"""
        operators = {
            "==": "EQUAL",
            ">": "GREATER_THAN",
            "<": "LESS_THAN",
            ">=": "GREATER_THAN_OR_EQUAL",
            "<=": "LESS_THAN_OR_EQUAL",
            "!=": "NOT_EQUAL"
        }
        return operators.get(op, "EQUAL")

    def _convert_value(self, value: any) -> Dict:
        """Convert Python value to Firestore REST API value format"""
        if isinstance(value, str):
            return {"stringValue": value}
        elif isinstance(value, bool):
            return {"booleanValue": value}
        elif isinstance(value, int):
            return {"integerValue": str(value)}
        elif isinstance(value, float):
            return {"doubleValue": value}
        elif value is None:
            return {"nullValue": None}
        elif isinstance(value, datetime):
            return {"timestampValue": value.isoformat()}
        else:
            raise ValueError(f"Unsupported value type: {type(value)}")
    
    async def get_okta_token(self):
        return "eyJraWQiOiJ2WVh4VzE5MW01Z3BPUkVKVUFjbkZHelM2UHpsRk5TNEZ2WHZUWUVoeldNIiwiYWxnIjoiUlMyNTYifQ.eyJ2ZXIiOjEsImp0aSI6IkFULm9hU1g5MDh1enFyS1hWbURrU092TEthaUVrOVZEaXlfQ1dXSFZJalp3S1kiLCJpc3MiOiJodHRwczovL3dlbGxza3ktY2lhbS5va3RhLmNvbS9vYXV0aDIvYXVzZjc5bzRqZG5Da0psT3k1ZDciLCJhdWQiOiJ2aWtpLmRldi53ZWxsc2t5LmlvIiwiaWF0IjoxNzM1MzIxMTk3LCJleHAiOjE3MzUzMjQ3OTcsImNpZCI6ImFwaS53ZWxsc2t5LnZpa2kucGFwZXJnbGFzcy5wcm9kIiwic2NwIjpbImFwaS53ZWxsc2t5LnZpa2kuYWkucGFwZXJnbGFzcyJdLCJzdWIiOiJhcGkud2VsbHNreS52aWtpLnBhcGVyZ2xhc3MucHJvZCJ9.CSl48od5cN5ce-HAGYXPywOpDdk3Tlgbs6HZ-bElJJb6KoJg9mnsShpu1rjScvNliPs5h8PVWQNRPE0cul6EqAkD49NcIazgvZn0O8T617PZsQ2l3CAn5CljK3hjTW85Ub7AtTUpFRmDlPUfARVftiOov4H_iFy8gU1m-t7G8_OEuoPt8i1UMHewXNt7vg1JWHiFmxNi3ETTi8sU7KDFGexVQ1_K_lKEfM-cmskU9wBYKiewwDnQcJQL5VQDLr4wg0XR4ns3zZe0IGSRGpI-NbmT2C8IjC8Xjan-5Sp8aAAtyrrsMJjze2IV4PeMThZ_19zQGiMwUBPHa-LWM6v5FQ"
    
    async def query_firestore(self,query:IQueryPort) -> float:
        """Execute a single query to Firestore and measure response time"""
        start_time = time.time()
        try:
            #print("Querying Firestore")
            # Perform a simple query - modify this based on your needs
            patient_id="5ad3d2c003c24c47ae14af17fda071e6"
            
            # latency is constant with load
            # docs = await query.get_document_operation_instances_by_document_id(document_id="d0e468a6955511efb03c3e3297f4bd07",operation_definition_id="f576881047e511efb01242004e494300")
            
            # latency increases with load
            #docs = await get_document_status_logs_summarized(app_id=None, tenant_id=None, patient_id=None,document_id="d0e468a6955511efb03c3e3297f4bd07",doc_operation_instance_id="d20df602955511ef920c42004e494300",query=query)
            
            # latency increases with load
            #docs = await get_documents(patient_id=patient_id, start_at=datetime.utcnow().isoformat(), end_at=None, limit=10, query=query)
            
            #docs = await query.get_app_config(app_id="hhh")
            
            # lateny
            #docs = await query.get_document_operation_instance_by_id("000199d2b38e11ef9a5e42004e494300")
            patient_id = "16282186"
            patient_ids = ["16282186","15028651","16229544","14603843"]
            #patient_id = random.choice(patient_ids)
            docs = await get_documents(app_id="hhh",tenant_id="",patient_id=patient_id, start_at="2024-12-27T19:40:25.929Z", end_at=None, limit=10, query=query)
            
            list(docs)  # Force query execution
            #print(docs)
            #time.sleep(0.5)
            
            
            
            duration = time.time() - start_time
            print(f"patient_id:{patient_id} duration:{duration}")
            return duration
        except Exception as e:
            print(str(e))
            self.errors.append(str(e))
            return -1

    async def run_batch(self, batch_id: int, query:IQueryPort) -> List[float]:
        """Run a batch of concurrent queries"""
        print("\nRunning batch:", batch_id)
        tasks = []
        for i in range(self.batch_size):
            task = asyncio.create_task(self.query_firestore(query))
            # task = asyncio.create_task(self.query_firestore_rest(where_conditions=[{"field": "document_id", "op": "==", "value": "d0e468a6955511efb03c3e3297f4bd07"},
            #                                                                               {"field": "document_operation_instance_id", "op": "==", "value": "d20df602955511ef920c42004e494300"}
            #                                                                               ]))
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        return [r for r in results if r > 0]

    @inject()
    async def run_load_test(self, query:IQueryPort):
        """Execute the full load test"""
        print(f"\nStarting load test with {self.num_requests} total requests "
              f"in batches of {self.batch_size}")
        
        num_batches = (self.num_requests + self.batch_size - 1) // self.batch_size
        all_tasks = []
        
        for batch_id in range(num_batches):
            task = asyncio.create_task(self.run_batch(batch_id,query))
            all_tasks.append(task)
            
        batch_results = await asyncio.gather(*all_tasks)
        
        self.response_times = [time for batch in batch_results for time in batch]

    def generate_report(self) -> Dict:
        """Generate a summary report of the load test"""
        if not self.response_times:
            return {"error": "No successful requests recorded","errors":self.errors}

        return {
            "total_requests": self.num_requests,
            "successful_requests": len(self.response_times),
            "failed_requests": len(self.errors),
            "average_response_time": statistics.mean(self.response_times),
            "median_response_time": statistics.median(self.response_times),
            "min_response_time": min(self.response_times),
            "max_response_time": max(self.response_times),
            "p95_response_time": statistics.quantiles(self.response_times, n=20)[-1],
            "total_errors": len(self.errors),
            "error_messages": self.errors[:5] if self.errors else []
        }
        
@inject()
async def load_docs(query:IQueryPort):
    patient_id="6b40380207e04c1b95c896310faa0670"
    
    docs = await get_document_status_logs_summarized(app_id=None, tenant_id=None, patient_id=None,document_id="d0e468a6955511efb03c3e3297f4bd07",doc_operation_instance_id="d20df602955511ef920c42004e494300",query=query)
    #docs = await query.get_document_operation_instances_by_document_id(document_id="d0e468a6955511efb03c3e3297f4bd07",operation_definition_id="f576881047e511efb01242004e494300")
    #docs = await get_documents(patient_id=patient_id, start_at=datetime.utcnow().isoformat(), end_at=None, limit=10, query=query)
    print(list(docs))  # Force query execution

def main():
    parser = argparse.ArgumentParser(description='Firestore Load Testing Tool')
    parser.add_argument('--collection', type=str, default="paperglass_document_operation_instance_log",
                      help='Firestore collection to query')
    parser.add_argument('--requests', type=int, default=1000,
                      help='Total number of requests to make')
    parser.add_argument('--batch-size', type=int, default=10,
                      help='Number of concurrent requests per batch')
    parser.add_argument('--output', type=str,
                      help='Output file for detailed results (optional)')
    
    args = parser.parse_args()
    
    # Initialize and run load test
    tester = FirestoreLoadTester(
        collection_name=args.collection,
        num_requests=args.requests,
        batch_size=args.batch_size
    )
    
    #asyncio.run(load_docs())
    
    print(f"Starting load test on collection: {args.collection}")
    print(f"Total requests: {args.requests}")
    print(f"Batch size: {args.batch_size}")
    
    # asyncio.run(tester.query_firestore_rest(where_conditions=[{"field": "document_id", "op": "==", "value": "d0e468a6955511efb03c3e3297f4bd07"},
    #                                                                                       {"field": "document_operation_instance_id", "op": "==", "value": "d20df602955511ef920c42004e494300"}
    #                                                                                       ]))
    # return
    
    asyncio.run(tester.run_load_test())
    
    # Generate and display report
    report = tester.generate_report()
    print("\nLoad Test Results:")
    print("=" * 50)
    for key, value in report.items():
        if key != "error_messages":
            if isinstance(value, float):
                print(f"{key}: {value:.3f}")
            else:
                print(f"{key}: {value}")
    
    if report.get("error_messages"):
        print("\nSample Errors:")
        for error in report["error_messages"]:
            print(f"- {error}")
    
    # Save detailed results if output file specified
    if args.output:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        detailed_results = {
            "test_parameters": {
                "collection": args.collection,
                "total_requests": args.requests,
                "batch_size": args.batch_size,
                "timestamp": timestamp
            },
            "summary": report,
            "response_times": tester.response_times
        }
        
        with open(args.output, 'w') as f:
            json.dump(detailed_results, f, indent=2)
        print(f"\nDetailed results saved to: {args.output}")
   

@inject()    
async def get_documents_by_patient_id(query:IQueryPort):
    patient_id = "16282186"
    
    start_time = time.time()
    docs = await get_documents(app_id="hhh", tenant_id="",patient_id=patient_id, start_at="2024-12-27T19:40:25.929Z", end_at=None, limit=10, query=query)
    print(len(docs))
    end_time = time.time()
    
    elapsed_time = end_time - start_time
    print(elapsed_time)

if __name__ == "__main__":
    # asyncio.run(get_documents_by_patient_id())
    main()
