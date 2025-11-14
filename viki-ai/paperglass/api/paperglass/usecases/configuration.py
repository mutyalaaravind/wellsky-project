from paperglass.domain.models import AppConfig,AppTenantConfig, Configuration
from paperglass.infrastructure.ports import IQueryPort
from ..domain.values import Configuration, ConfigurationTest
from kink import inject
from typing import List
from aiocache import cached, Cache

from paperglass.settings import CONFIG_CACHE_ENABLE, CONFIG_CACHE_TTL
from paperglass.log import CustomLogger
LOGGER = CustomLogger(__name__)

def conditional_cache(ttl, cache):
    def decorator(func):
        if CONFIG_CACHE_ENABLE:
            return cached(ttl=ttl, cache=cache)(func)
        return func
    return decorator

@inject
@cached(ttl=CONFIG_CACHE_TTL, cache=Cache.MEMORY)
async def get_config(app_id:str, tenant_id:str, query:IQueryPort) -> 'Configuration':
    config: Configuration = None
    tenant_config:AppTenantConfig = await query.get_app_tenant_config(app_id, tenant_id)    
    if not tenant_config:
        LOGGER.debug("No tenant config found for app_id: %s, tenant_id: %s", app_id, tenant_id)
        app_config:AppConfig = await query.get_app_config(app_id)        
        if app_config:
            config = app_config.config
        # Temporary fix for missing tenant config in local dev
        else:
            config = Configuration(
                extract_allergies = False,
                extract_conditions = True,
                extract_immunizations = False,
                extraction_persisted_to_medication_profile = False,
                use_extract_and_classify_strategy=True,
                use_ordered_events=False,
                use_v3_orchestration_engine=True
            )
    else:
        config = tenant_config.config

    return config

@inject
async def get_testsetup(test_id:str, query:IQueryPort) -> 'ConfigurationTest':
    config_test: ConfigurationTest = None
    config_test = await query.get_test_config(test_id)
    return config_test

@inject
async def get_golden_data(num_of_doc,query:IQueryPort):
    config_gd_test = await query.get_test_case_golden_dataset(num_of_doc)
    return config_gd_test

    
