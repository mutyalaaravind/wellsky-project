import asyncio
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import paperglass.usecases.documents as documents

from paperglass.infrastructure.adapters.external_medications import HHHAdapter
from paperglass.domain.values import HostFreeformMedicationAddModel

from paperglass.domain.utils.opentelemetry_utils import bootstrap_opentelemetry
bootstrap_opentelemetry(__name__)

from paperglass.log import getLogger
LOGGER = getLogger(__name__)

# Run once or in a loop based on mode provided
async def run():
    from paperglass.interface.utils import verify_okta_token
    dev_okta_token="eyJraWQiOiJMMWtJd2F5QnBvcl9ZUTZ3b2JxNHEtUk10YU93VW9obS1UU2I3eWo3a1pBIiwiYWxnIjoiUlMyNTYifQ.eyJ2ZXIiOjEsImp0aSI6IkFULndJTG5FS1VBdWFHQjFNZWtuMHBoLVhqMjljd2FGY0NGNzBUbmwxY0ZNWkUiLCJpc3MiOiJodHRwczovL3dlbGxza3ktY2lhbS5va3RhcHJldmlldy5jb20vb2F1dGgyL2F1c2FqdDhodjFCOFM3aGtoMWQ3IiwiYXVkIjoidmlraS5wcm9kLndlbGxza3kuaW8iLCJpYXQiOjE3MjQ2OTMxNDYsImV4cCI6MTcyNDY5Njc0NiwiY2lkIjoiYXBpLndlbGxza3kudmlraS5wYXBlcmdsYXNzIiwic2NwIjpbImFwaS53ZWxsc2t5LnZpa2kuYWkucGFwZXJnbGFzcyJdLCJzdWIiOiJhcGkud2VsbHNreS52aWtpLnBhcGVyZ2xhc3MifQ.GibtrJaFp_HPqHbxy_CVbw0xsRrBVgfMsjduBeKTPP-JVSGetfpcAwGGIGgqHFarjxXhdxVvhFLj0-zhSRLt2tQRBsis8XJ6XF4rCSUrdc_VsZqbmkHvNGPjAEv-s1s6jB_jVQI2WIOKTFAj8TS-Cp3Jpt5-XfwJF3CsewgfKNF1-8mQGTNIPmSR8RGNfIQC4Lqk3pmdPwZbsiiSJ_YwLm-PE0DKgCjgtNlbdhH2YenSQtidkh-lRVWQtm6nvOWK1eOtxUT3LVo1fHE-zrnmRYj8kVJnuOUfn_0kqxUg3E3czZ1Nnke2aFtUowGDBLYR0VNNiIq8q2vifi0lFkx44g"
    dev_client_id="api.wellsky.viki.paperglass"
    dev_issuer_url="https://wellsky-ciam.oktapreview.com/oauth2/ausajt8hv1B8S7hkh1d7/v1/token"
    dev_audience="viki.prod.wellsky.io"

    qa_okta_token="eyJraWQiOiJMMWtJd2F5QnBvcl9ZUTZ3b2JxNHEtUk10YU93VW9obS1UU2I3eWo3a1pBIiwiYWxnIjoiUlMyNTYifQ.eyJ2ZXIiOjEsImp0aSI6IkFULlk4dlUtTzBHOTBidExIMWRUeFFKbW0xejhwdnFtUmdoWXEzY2Rpa2Jpc1kiLCJpc3MiOiJodHRwczovL3dlbGxza3ktY2lhbS5va3RhcHJldmlldy5jb20vb2F1dGgyL2F1c2FqdDhodjFCOFM3aGtoMWQ3IiwiYXVkIjoidmlraS5wcm9kLndlbGxza3kuaW8iLCJpYXQiOjE3MjQ2NTkzNDIsImV4cCI6MTcyNDY2Mjk0MiwiY2lkIjoiYXBpLndlbGxza3kudmlraS5wYXBlcmdsYXNzIiwic2NwIjpbImFwaS53ZWxsc2t5LnZpa2kuYWkucGFwZXJnbGFzcyJdLCJzdWIiOiJhcGkud2VsbHNreS52aWtpLnBhcGVyZ2xhc3MifQ.SiUYVPcyqAN_hQKWwlnt4pjzWhihyV3U3-MJ2ZhUL0VbtNOzQW7zK2T-t3iYdc0BsvufqoJDR_Gsf-_UU1Y7HP5JF_UQkLPEd9sVYfYbHHx4ZHnY8Nu10rjdZFIISo-ngSlQSOMzWge8ocFOAqh4Zhyi2bdGoa9ajWzUEA6vn0xjuWctXB6SHfkq8477TZHzXRBo3WWRCY5LZW2B40KKS08dYa63ZgAWwKH8QDVzRw495vvAZ6P8YwiyGPIk-hPX7pBq8JZvSiss1vbD1KgWNKPWWRYmPtvfU6Rk-kz5zCYKrLc_eDr9QArZgVk4enfyMhTQHVX3-aULgTemtB34GQ"
    qa_client_id="api.wellsky.viki.paperglass"
    qa_issuer_url="https://wellsky-ciam.oktapreview.com/oauth2/ausajt8hv1B8S7hkh1d7/v1/token"
    qa_audience="api.wellsky.viki.paperglass"

    stage_okta_token=""
    stage_client_id="api.wellsky.viki.paperglass"
    stage_issuer_url="https://wellsky-ciam.okta.com/oauth2/aushirk9h5LbqrTwi5d7/v1/token"
    stage_audience="api.wellsky.viki.paperglass"

    prod_okta_token="eyJraWQiOiJFRF9zYXR5T01kWTJYV3QxSUJlSFZoaDJBejRycldtaThGckhyRlpPTXhVIiwiYWxnIjoiUlMyNTYifQ.eyJ2ZXIiOjEsImp0aSI6IkFULi1KemlqUFhGN2xCWkRPS3VzdDk3TWloYnlxUWJfSkdkbl9NZkxXNTBlWEkiLCJpc3MiOiJodHRwczovL3dlbGxza3ktY2lhbS5va3RhLmNvbS9vYXV0aDIvYXVzZjc5bzRqZG5Da0psT3k1ZDciLCJhdWQiOiJ2aWtpLmRldi53ZWxsc2t5LmlvIiwiaWF0IjoxNzI0Njk0MTQxLCJleHAiOjE3MjQ2OTc3NDEsImNpZCI6ImFwaS53ZWxsc2t5LnZpa2kucGFwZXJnbGFzcy5wcm9kIiwic2NwIjpbImFwaS53ZWxsc2t5LnZpa2kuYWkucGFwZXJnbGFzcyJdLCJzdWIiOiJhcGkud2VsbHNreS52aWtpLnBhcGVyZ2xhc3MucHJvZCJ9.TVrDNGV2A_wIHPjmHjQA12yQLqe79a4Fpb5Mxy_iN0CoWwkoJ9iSCtZ6yvdynnd9w2U83q5SB66kyRbTZQ7CmgzKgvrjW4QGnsKLOx1og-u9ILzZX23EONpw7ytAJFxsQBfjaySf0CufcOyHzYE05vvc7fM1ZXF2Zk5LSgDjFZJrFdRPl2LPNAWisYKTnC1EwlWZp7nZdD2AFVUopYndd24PB9r8Ggoqcw5mYRHjwz5PKO7aJJEyC9V_Cd-dhMreKsg0w_vzDsCtqcHwnYezTw1fJVwzs8nqPTWoeKeLLwGtRcKC0d4tbfZr0pWjiFuQhklSokEMP98foiDRhBAOVw"
    prod_client_id="api.wellsky.viki.paperglass.prod"
    prod_issuer_url="https://wellsky-ciam.okta.com/oauth2/ausf79o4jdnCkJlOy5d7/v1/token"
    prod_audience="viki.dev.wellsky.io"

    await verify_okta_token(dev_okta_token,dev_issuer_url,dev_client_id,dev_audience)
    # await verify_okta_token(qa_okta_token,qa_issuer_url,qa_client_id,qa_audience)
    # await verify_okta_token(stage_okta_token,stage_issuer_url,stage_client_id,stage_audience)
    #await verify_okta_token(prod_okta_token, prod_issuer_url, prod_client_id, prod_audience)



def main():
    
    asyncio.run(run())

if __name__ == "__main__":   
    main()






