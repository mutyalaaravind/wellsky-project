import requests
import json
import google.auth

from paperglass.domain.values import get_class

from paperglass.infrastructure.ports import IFhirStoreAdapter
import uuid as uuid

from paperglass.log import getLogger

logger = getLogger(__name__)


class HTTPException(Exception):
    def __init__(self, reason, message, status_code, error_type="HttpError"):
        self.reason = reason
        self.message = message
        self.status_code = status_code
        self.error_type = error_type
        super(HTTPException, self).__init__(self.reason)


class GCPAuth(object):
    _credentials = None

    def auth_token(self, force_refresh=False):

        if GCPAuth._credentials and GCPAuth._credentials.token and not force_refresh:
            return GCPAuth._credentials.token

        if GCPAuth._credentials:
            logger.info(f"Current token {GCPAuth._credentials.token}")
        # getting the credentials and project details for gcp project
        GCPAuth._credentials, project_id = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )

        # getting request object
        auth_req = google.auth.transport.requests.Request()

        GCPAuth._credentials.refresh(auth_req)  # refresh token

        logger.info(GCPAuth._credentials.token)

        if GCPAuth._credentials.valid:
            return GCPAuth._credentials.token
        else:
            raise Exception("GCP Auth failed")  # prints token


class FhirStoreAdapter(IFhirStoreAdapter):

    def __init__(self, fhir_server_url, fhir_datastore):
        self.fhir_server_url = fhir_server_url
        self.fhir_datastore = fhir_datastore

    def _construct_object(self, resourceType_cls, arguments):
        if resourceType_cls:
            data_object = resourceType_cls.parse_obj(arguments)
        return data_object

    def _get_tokens(self, results):
        def _extract_token(url):
            token_comps = [c.split('=')[1] for c in url.split('&') if '_page_token=' in c]
            return token_comps[0] if token_comps else None

        tokens = [(l.get('relation'), _extract_token(l.get('url'))) for l in results.get('link')]
        return dict(tokens)

    def _get_gcp_auth_token(self, force_refresh=False):
        return GCPAuth().auth_token(force_refresh)

    def _get_headers(self, for_patch=False):
        return {
            'Content-Type': 'application/json-patch+json' if for_patch else 'application/fhir+json; charset=utf-8',
            'Authorization': f'Bearer {self._get_gcp_auth_token()}',
        }

    def post(self, type, payload, type_cls=None):

        payload['resourceType'] = type

        url = f'{self.fhir_server_url}/{self.fhir_datastore}/fhir/{type}'

        payload = json.loads(json.dumps(payload, indent=4, sort_keys=True, default=str))

        retry_count = 0
        while retry_count < 3:
            response = requests.post(url, json=payload, headers=self._get_headers())

            if response.status_code >= 200 and response.status_code <= 300:
                return self._construct_object(type_cls, response.json())

            logger.debug(f"Error : {response.reason} {response.text}")

            if response.status_code == 401:
                logger.debug("Token expired, refresing it now")
                self._get_gcp_auth_token(force_refresh=True)

                retry_count += 1
            else:
                raise HTTPException(reason=response.reason, message=response.text, status_code=response.status_code)

        raise HTTPException(reason=response.reason, message=response.text, status_code=response.status_code)

    def get(self, type, id):
        url = f'{self.fhir_server_url}/{self.fhir_datastore}/fhir/{type}/{id}'

        retry_count = 0
        while retry_count < 3:
            response = requests.get(url, headers=self._get_headers())
            if response.status_code >= 200 and response.status_code <= 300:
                return self._construct_object(type, response.json())

            logger.debug(f"Error : {response.reason} {response.text}")

            if response.status_code == 401:
                self._get_gcp_auth_token(force_refresh=True)

                retry_count += 1
            else:
                raise HTTPException(reason=response.reason, message=response.text, status_code=response.status_code)

        raise HTTPException(reason=response.reason, message=response.text, status_code=response.status_code)

    def put(self, type, id, payload, type_cls=None):
        payload['resourceType'] = type

        url = f'{self.fhir_server_url}/{self.fhir_datastore}/fhir/{type}/{id}'

        payload = json.loads(json.dumps(payload, indent=4, sort_keys=True, default=str))

        retry_count = 0
        while retry_count < 3:
            response = requests.put(url, json=payload, headers=self._get_headers())
            if response.status_code >= 200 and response.status_code <= 300:
                return self._construct_object(type_cls, response.json())

            logger.debug(f"Error : {response.reason} {response.text}")

            if response.status_code == 401:
                self._get_gcp_auth_token(force_refresh=True)

                retry_count += 1
            else:
                raise HTTPException(reason=response.reason, message=response.text, status_code=response.status_code)

        raise HTTPException(reason=response.reason, message=response.text, status_code=response.status_code)

    def patch(self, type, id, payload):
        payload = json.loads(json.dumps(payload, indent=4, sort_keys=True, default=str))
        patch_body = []
        for key, val in payload.items():
            patch_body.append({"op": "replace", "path": f"/{key}", "value": val})

        logger.debug(f"\nPATCH: {patch_body}\n")

        url = f'{self.fhir_server_url}/{self.fhir_datastore}/fhir/{type}/{id}'

        retry_count = 0
        while retry_count < 3:
            response = requests.patch(url, json=patch_body, headers=self._get_headers(for_patch=True))

            if response.status_code >= 200 and response.status_code <= 300:
                return self._construct_object(type, response.json())

            logger.debug(f"ERROR: {response.reason}\n{response.text}")
            if response.status_code == 401:
                self._get_gcp_auth_token(force_refresh=True)

                retry_count += 1
            else:
                raise HTTPException(reason=response.reason, message=response.text, status_code=response.status_code)

        raise HTTPException(reason=response.reason, message=response.text, status_code=response.status_code)

    def search(self, type, arguments, cls, count=10, page_token=None):
        # assert len(arguments)
        def _construct_search_term(args):
            terms = ''
            if 'paramType' in args:
                terms = f"{args.get('key')}:{args.get('paramType')}={args.get('value')}"
            else:
                terms = f"{args.get('key')}={args.get('value')}"

            logger.debug(f"Search terms : {terms}")
            return terms

        base_url = f"{self.fhir_server_url}/{self.fhir_datastore}/fhir/{type}"

        if arguments:
            search_params = '&'.join([_construct_search_term(a) for a in arguments])
            logger.debug(f"Searching with search terms : {search_params}")
            url = f'{base_url}/?{search_params}&_count={count or 10}'
        else:
            url = f'{base_url}/?_count={count or 10}'

        if page_token:
            url += f'&_page_token={page_token}'

        logger.info(url)

        retry_count = 0
        while retry_count < 3:
            response = requests.get(url, headers=self._get_headers())
            if response.status_code >= 200 and response.status_code <= 300:
                results = response.json()
                result_items = (
                    [self._construct_object(cls, r.get('resource')) for r in results.get('entry')]
                    if results.get('total') > 0
                    else []
                )
                tokens = self._get_tokens(results)
                logger.debug(f'Tokens: {tokens}')
                return {'items': result_items, 'nextToken': tokens.get('next'), 'currentToken': tokens.get('self')}

            logger.debug(f"Error: {response.reason} {response.text}")

            if response.status_code == 401:
                self._get_gcp_auth_token(force_refresh=True)

                retry_count += 1
            else:
                raise HTTPException(reason=response.reason, message=response.text, status_code=response.status_code)

        raise HTTPException(reason=response.reason, message=response.text, status_code=response.status_code)

    def delete(self, type, id):
        url = f'{self.fhir_server_url}/{self.fhir_datastore}/fhir/{type}/{id}'
        retry_count = 0
        while retry_count < 3:
            response = requests.delete(url, headers=self._get_headers())
            if response.status_code >= 200 and response.status_code <= 300:
                return self._construct_object(type, response.json())

            logger.debug(f"Error : {response.reason} {response.text}")

            if response.status_code == 401:
                self._get_gcp_auth_token(force_refresh=True)

                retry_count += 1
            else:
                raise HTTPException(reason=response.reason, message=response.text, status_code=response.status_code)

        raise HTTPException(reason=response.reason, message=response.text, status_code=response.status_code)

    def execute_bundle(self, type, entry):

        payload = {'resourceType': 'Bundle', 'type': type, 'entry': entry}
        url = f'{self.fhir_server_url}/{self.fhir_datastore}/fhir'

        payload = json.loads(json.dumps(payload, indent=4, sort_keys=True, default=str))

        retry_count = 0
        while retry_count < 3:
            response = requests.post(url, json=payload, headers=self._get_headers())

            if response.status_code >= 200 and response.status_code <= 300:
                return json.loads(response.text)

            logger.debug(f"Error : {response.reason} {response.text}")

            if response.status_code == 401:
                logger.debug("Token expired, refresing it now")
                self._get_gcp_auth_token(force_refresh=True)

                retry_count += 1
            else:
                raise HTTPException(reason=response.reason, message=response.text, status_code=response.status_code)

        raise HTTPException(reason=response.reason, message=response.text, status_code=response.status_code)

    def build_bundle_entry(self, resource_type, method, payload, condition=None, conditional_url=None, id=None):
        """
        builds entry for FHIR Transactions and Batches

        :param resource_type: Resource type
        :param method: POST, PUT, PATCH, DELETE
        :param payload: resource payload
        :param condition: conditional update condition name - e.g ifNoneExist, ifModifiedSince, ifMatch, ifNoneMatch
        :param conditional_url: resource conditional create url - e.g Patient?identifier=WSCC|46252
        """

        assert all([resource_type, method, payload])

        url = f'{resource_type}/{id}' if id else f'{resource_type}/{uuid.uuid4().hex}'

        entry = {}

        if not method == 'PATCH':
            entry['fullUrl'] = url

        payload['resourceType'] = resource_type
        entry['resource'] = payload

        request = {'method': method, 'url': conditional_url or url}

        # condition ifNoneExist
        if condition and conditional_url:
            request['url'] = resource_type
            request[condition] = conditional_url

        entry['request'] = request

        return entry
