from typing import Optional
from google.cloud.firestore import AsyncClient

from autoscribe.infrastructure.ports import IPersistencePort
from autoscribe.domain.models import Transaction


class FirestoreAdapter(IPersistencePort):
    def __init__(self):
        self.client = AsyncClient()
        self.transactions_ref = self.client.collection('autoscribe_transactions')

    async def put_transaction(self, transaction: Transaction):
        await self.transactions_ref.document(transaction.id).set(transaction.dict())

    async def get_transaction(self, transaction_id: str) -> Optional[Transaction]:
        doc = await self.transactions_ref.document(transaction_id).get()
        if doc.exists:
            return Transaction.parse_obj(doc.to_dict())
        return None
