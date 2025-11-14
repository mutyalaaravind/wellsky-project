from typing import Dict, List
import json
import uuid

import aiohttp
import aiocache

from ..ports import IMedispanPort

from google.cloud import firestore

from ...settings import MEDISPAN_API_URL, MEDISPAN_AUTH_URL, MEDISPAN_PAGE_SIZE

from ...log import getLogger
LOGGER = getLogger(__name__)


class MedispanAdapter(IMedispanPort):
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret

    @aiocache.cached(ttl=900)
    async def get_access_token(self) -> str:
        LOGGER.info('Fetching access token from Medispan')        
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
        }
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
            async with session.post(MEDISPAN_AUTH_URL, data=payload) as response:
                text = await response.text()
                return json.loads(text)["access_token"]

    async def search_medications(self, search_term: str) -> List[dict]:
        payload = {
            "searchText": search_term,
            "pageSize": MEDISPAN_PAGE_SIZE,
        }
        LOGGER.debug("Searching medispan for medications with search term: %s", payload)
        try:
            token = await self.get_access_token()
        except Exception as exc:
            LOGGER.error('Error fetching access token from Medispan: %s', exc)
            raise self.Error('Error fetching access token from Medispan') from exc
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }

        try:
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
                LOGGER.debug("Fetching data from Medispan")
                async with session.post(MEDISPAN_API_URL, headers=headers, data=json.dumps(payload)) as response:
                    response_data = json.loads(await response.text())
        except Exception as exc:
            LOGGER.error('Error fetching data from Medispan: %s', exc)
            raise self.Error('Error fetching data from Medispan') from exc

        #LOGGER.debug("Medispan response for search term '%s': %s", search_term, json.dumps(response_data, indent=2))
        LOGGER.info("Medispan responseCount: %s and totalCount: %s for search term", len(response_data['result']['data']), response_data['result']['totalCount'])
        # total_count = response_data['result']
        return [
            self.Drug(
                id = drug['externalDrugId'],
                brand_name=drug['brandName'],
                generic_name=drug['genericName'],
                full_name=drug['nameDescription'],
                route=drug['route'],
                form=drug['dosage_Form'],
                strength=self.Drug.Strength(
                    value=drug['strength'],
                    unit=drug['strengthUnitOfMeasure'],
                ),
                package=self.Drug.Package(
                    size=drug['packageSize'],
                    unit=drug['packageSizeUnitOfMeasure'],
                    quantity=drug['packageQuantity'],
                ),
                # TODO: Add more fields?
            )
            for drug in response_data['result']['data']
        ]


class MedispanCachedAdapter(MedispanAdapter):
    
    def __init__(self, client_id: str, client_secret: str):
        super().__init__(client_id, client_secret)
        self.db_client = firestore.AsyncClient()

    async def search_medications(self, search_term: str) -> List[dict]:
        medications,cache_exists = await self._get_cache_item(search_term)
        if not cache_exists:
            LOGGER.info('Results not cached.  Fetching medications from Medispan...')
            medications = await super().search_medications(search_term)
            await self._save_cache_item(search_term, medications)
        else:
            LOGGER.info("Medispan results found in cache: %s", medications)
        return medications
    
    async def _get_cache_item(self, search_term):
        cache_exists = False
        docs = await self.db_client.collection("medispan_cache").where("search_term", "==", search_term).get()
        if docs:
            cache_exists = True
        results = [await self.to_drug_model(doc.to_dict().get("medication_suggestions")) for doc in docs if doc and doc.to_dict().get("medication_suggestions")] if docs else None
        if results:
            return results[0],cache_exists
        return None,cache_exists

    async def _save_cache_item(self, search_term, medications):
        id = uuid.uuid4().hex
        await self.db_client.collection("medispan_cache").document(id).set({"search_term":search_term,
                                                                            "medication_suggestions":[x.dict() for x in medications]})
        return id
    
    async def to_drug_model(self, medications:List[Dict]):
        
        if not  medications:
            return None
        
        return [self.Drug(**drug) for drug in medications if drug]